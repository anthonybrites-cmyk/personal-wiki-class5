"""Read Markdown/text files and split them into citable passages.

A passage keeps its source path, the heading it sits under, and its line range, so
every search hit and every citation can point back to the exact place in the file.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from . import config

TEXT_SUFFIXES = {".md", ".markdown", ".txt"}
HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
FENCE = re.compile(r"^\s*(```|~~~)")
WORD = re.compile(r"[A-Za-z0-9]+")


@dataclass
class Passage:
    id: str            # "raw/pacman-dqn-class3/README.md#L42-L50"
    kind: str          # "source" (original evidence) or "wiki" (generated note)
    path: str          # path relative to vault/, e.g. "raw/pacman-dqn-class3/README.md"
    title: str         # document title (first H1, else file stem)
    section: str       # nearest heading above the passage
    heading_path: str  # "Results > Before / after evaluation"
    start_line: int    # 1-based, inclusive
    end_line: int
    text: str          # the original lines, unchanged

    @property
    def location(self) -> str:
        return f"{self.path} § {self.section} (lines {self.start_line}-{self.end_line})"

    def search_text(self) -> str:
        """What the indexes see: headings add context the passage body may lack."""
        return f"{self.title}. {self.heading_path}.\n{self.text}"

    def to_dict(self) -> dict:
        return asdict(self)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def list_text_files(root: Path) -> list[Path]:
    if root.is_file():
        return [root] if root.suffix.lower() in TEXT_SUFFIXES else []
    files = [p for p in root.rglob("*")
             if p.is_file() and p.suffix.lower() in TEXT_SUFFIXES and not p.name.startswith(".")]
    # A .txt converted by `wiki convert` is represented by its Markdown twin; the .txt
    # stays in raw/ untouched as the original, but is not indexed twice.
    return sorted(p for p in files
                  if not (p.suffix.lower() == ".txt" and p.with_suffix(".md").exists()))


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raise ValueError(f"{path.name} is not UTF-8 text. Run `wiki convert` to make a "
                         "Markdown copy (the original is left unchanged).") from None


def vault_relative(path: Path) -> str:
    return path.resolve().relative_to(config.VAULT.resolve()).as_posix()


def word_count(text: str) -> int:
    return len(WORD.findall(text))


def strip_frontmatter(lines: list[str]) -> int:
    """Return the index of the first body line (skips a leading --- YAML block)."""
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                return i + 1
    return 0


def _blocks(lines: list[str], start: int, end: int) -> list[tuple[int, int]]:
    """Split lines[start:end] into blank-line separated blocks, keeping code fences
    and tables whole. Returns (first, last) 0-based inclusive line indices."""
    blocks, i = [], start
    while i < end:
        if not lines[i].strip():
            i += 1
            continue
        j = i
        if FENCE.match(lines[i]):
            j += 1
            while j < end and not FENCE.match(lines[j]):
                j += 1
            j = min(j, end - 1)
        else:
            while j + 1 < end and lines[j + 1].strip() and not FENCE.match(lines[j + 1]):
                j += 1
        blocks.append((i, j))
        i = j + 1
    return blocks


def _split_oversized(lines: list[str], first: int, last: int) -> list[tuple[int, int, str]]:
    """Split one long block by lines. Table continuations repeat the header row so
    each piece can still be read on its own."""
    is_table = lines[first].lstrip().startswith("|") and first + 1 <= last and \
        set(lines[first + 1].strip()) <= set("|-: ")
    header = "\n".join(lines[first:first + 2]) + "\n" if is_table else ""
    if first == last:  # one very long line (a prose paragraph): split between sentences
        sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z\[])", lines[first].strip())
        out, cur = [], []
        for sent in sentences:
            if cur and word_count(" ".join(cur + [sent])) > config.CHUNK_TARGET_WORDS:
                out.append((first, first, " ".join(cur)))
                cur = []
            cur.append(sent)
        if cur:
            out.append((first, first, " ".join(cur)))
        return out
    pieces, cur_start, count = [], first, 0
    for k in range(first, last + 1):
        n = word_count(lines[k])
        if count and count + n > config.CHUNK_TARGET_WORDS:
            pieces.append((cur_start, k - 1))
            cur_start, count = k, 0
        count += n
    pieces.append((cur_start, last))
    out = []
    for a, b in pieces:
        text = "\n".join(lines[a:b + 1])
        if is_table and a > first + 1:
            text = header + text
        out.append((a, b, text))
    return out


def chunk_markdown(path: Path, kind: str = "source") -> list[Passage]:
    """Heading-aware chunking: a passage never spans two sections."""
    rel = vault_relative(path)
    lines = read_text(path).splitlines()
    body_start = strip_frontmatter(lines)

    # Find headings (outside code fences) to get section boundaries.
    heads: list[tuple[int, int, str]] = []  # (line index, level, text)
    in_fence = False
    for i in range(body_start, len(lines)):
        if FENCE.match(lines[i]):
            in_fence = not in_fence
            continue
        m = None if in_fence else HEADING.match(lines[i])
        if m:
            heads.append((i, len(m.group(1)), m.group(2).strip()))

    title = next((t for _, lvl, t in heads if lvl == 1), path.stem)
    bounds = [(body_start, None, [])]  # (start, heading text, heading stack)
    stack: list[tuple[int, str]] = []
    for i, lvl, text in heads:
        stack = [(l, t) for l, t in stack if l < lvl] + [(lvl, text)]
        bounds.append((i, text, [t for _, t in stack]))

    passages: list[Passage] = []
    for n, (start, head, stack_texts) in enumerate(bounds):
        end = bounds[n + 1][0] if n + 1 < len(bounds) else len(lines)
        body_first = start + 1 if head is not None else start
        section = head or title
        heading_path = " > ".join(t for t in stack_texts if t != title) or section

        # Pack blocks into passages of about CHUNK_TARGET_WORDS.
        pending: list[tuple[int, int, str]] = []
        for a, b in _blocks(lines, body_first, end):
            text = "\n".join(lines[a:b + 1])
            if word_count(text) > config.CHUNK_MAX_WORDS:
                pending.extend(_split_oversized(lines, a, b))
            else:
                pending.append((a, b, text))

        group: list[tuple[int, int, str]] = []
        def flush():
            if not group:
                return
            text = "\n\n".join(t for _, _, t in group)
            if word_count(text) >= config.CHUNK_MIN_WORDS:
                a, b = group[0][0] + 1, group[-1][1] + 1
                passages.append(Passage(
                    id=f"{rel}#L{a}-L{b}", kind=kind, path=rel, title=title,
                    section=section, heading_path=heading_path,
                    start_line=a, end_line=b, text=text,
                ))
            group.clear()

        for piece in pending:
            size = sum(word_count(t) for _, _, t in group)
            if group and size + word_count(piece[2]) > config.CHUNK_TARGET_WORDS:
                flush()
            group.append(piece)
        flush()
    return passages


def section_outline(path: Path) -> list[tuple[int, str]]:
    """(level, heading) pairs, used by ingestion to show Gemma the source's shape."""
    lines = read_text(path).splitlines()
    out, in_fence = [], False
    for line in lines[strip_frontmatter(lines):]:
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        m = None if in_fence else HEADING.match(line)
        if m:
            out.append((len(m.group(1)), m.group(2).strip()))
    return out
