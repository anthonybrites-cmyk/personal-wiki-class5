"""Plain-text originals -> Markdown, without changing a word.

Old Mac/Word text exports arrive in MacRoman with CR line endings and "*"/"o" bullet
glyphs, which neither Python's UTF-8 reader nor Obsidian handle. `wiki convert` writes a
Markdown copy next to each .txt and leaves the .txt byte-for-byte unchanged. It changes
only encoding, line endings, bullet glyphs, and heading markers, and it proves the words
are unchanged: the Markdown's word sequence must equal the original's (bullet glyphs
aside), or nothing is written. No model is involved.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

import yaml

WORDS = re.compile(r"[^\W_]+")
OUTLINE_L1 = re.compile(r"^\*\s?(.*)$")   # Word outline export: "*" = levels 1, 3, 4
OUTLINE_L2 = re.compile(r"^o\s(.*)$")     # "o" = levels 2, 5
WIKI_HEADING = re.compile(r"^(={2,6})\s*(.+?)\s*\1$")


@dataclass
class Conversion:
    source: Path
    target: Path
    encoding: str
    line_endings: str
    words: int
    headings: int
    status: str          # written | unchanged | skipped
    note: str = ""


def decode(data: bytes) -> tuple[str, str]:
    """UTF-8 if valid; otherwise MacRoman for classic-Mac CR files, else Windows-1252."""
    try:
        return data.decode("utf-8-sig"), "utf-8"
    except UnicodeDecodeError:
        pass
    mac = data.count(b"\r") > 2 * data.count(b"\r\n")
    enc = "mac_roman" if mac else "cp1252"
    return data.decode(enc), enc


def line_endings(data: bytes) -> str:
    crlf, cr = data.count(b"\r\n"), data.count(b"\r")
    lf = data.count(b"\n") - crlf
    return "CR (classic Mac)" if cr - crlf > max(crlf, lf) else "CRLF" if crlf > lf else "LF"


def _is_o(line: str) -> bool:
    return line == "o" or bool(OUTLINE_L2.match(line))


def _title_case(body: str) -> bool:
    words = re.findall(r"[A-Za-z][A-Za-z'&-]*", body)
    return bool(words) and all(w[0].isupper() for w in words if len(w) >= 4)


def _is_outline_heading(body: str, prev_line: str, next_line: str) -> bool:
    """A top-level outline item that introduces sub-bullets. The export loses indentation,
    so "*" can be level 1 or a deep sub-bullet; this is a heuristic that only decides
    where headings go, never what the words are. A heading is a short label (no sentence
    punctuation) followed by an "o" item, and either written in Title Case or following
    an "o" item itself (a new top-level topic after the previous topic's sub-items)."""
    words = body.split()
    return (_is_o(next_line) and 1 <= len(words) <= 7
            and ":" not in body.rstrip(":") and " – " not in body and " - " not in body
            and (_title_case(body) or _is_o(prev_line)))


def to_markdown(text: str) -> tuple[str, int]:
    lines = [l.rstrip() for l in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    nonblank = [i for i, l in enumerate(lines) if l.strip()]
    nxt = {a: lines[b].strip() for a, b in zip(nonblank, nonblank[1:])}
    prv = {b: lines[a].strip() for a, b in zip(nonblank, nonblank[1:])}
    out: list[str] = []
    headings, seen_title, under_item = 0, False, False
    in_pre = False
    for i, raw in enumerate(lines):
        line = raw.strip()
        # Lines indented by 2+ spaces (plain-text tables such as a journal entry) keep
        # their layout inside a fenced block.
        if raw.startswith("  ") and line and seen_title:
            if not in_pre:
                out += ["", "```"]
                in_pre = True
            out.append(raw)
            continue
        if in_pre:
            out += ["```", ""]
            in_pre = False
        if not line:
            out.append("")
            continue
        wiki_heading = WIKI_HEADING.match(line)
        if wiki_heading and seen_title:          # MediaWiki "== Heading ==" (Wikipedia exports)
            level = min(len(wiki_heading.group(1)), 6)
            out += ["", f"{'#' * level} {wiki_heading.group(2)}", ""]
            headings += 1
            continue
        if line in ("*", "o"):
            continue                             # empty bullet: no words to keep
        if not seen_title:                       # first line is the document title
            out += [f"# {line}", ""]
            seen_title = True
            continue
        m1, m2 = OUTLINE_L1.match(line), OUTLINE_L2.match(line)
        if m1 and m1.group(1).strip():
            body = m1.group(1).strip()
            if _is_outline_heading(body, prv.get(i, ""), nxt.get(i, "")):
                out += ["", f"## {body.rstrip(':')}{':' if body.endswith(':') else ''}", ""]
                headings += 1
                under_item = False
            else:
                out.append(("  - " if under_item else "- ") + body)
        elif m2 and m2.group(1).strip():
            out.append("- " + m2.group(1).strip())
            under_item = True
        elif m1 or m2:
            continue                             # empty bullet: no words to keep
        elif re.fullmatch(r"[A-Z][\w ]{0,30}:", line) and nxt.get(i, "").startswith("["):
            out += ["", f"## {line}", ""]        # e.g. "References:" before "[1] ..."
            headings += 1
        elif re.match(r"^\[\d+\]", line):
            out.append(f"- {line}")              # numbered reference
        else:
            out += [line, ""]                    # prose: one paragraph per line
    if in_pre:
        out.append("```")
    md = re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip() + "\n"
    # Lists need a blank line before a following paragraph/heading and vice versa.
    md = re.sub(r"(\n- [^\n]*)\n(?=[^\s-])", r"\1\n\n", md)
    return md, headings


def words_of_original(text: str) -> list[str]:
    body = [re.sub(r"^\s*(\*|o)\s", "", l) for l in text.replace("\r", "\n").split("\n")]
    body = [l for l in body if l.strip() not in ("*", "o")]
    return WORDS.findall("\n".join(body))


def convert_file(src: Path, force: bool = False) -> Conversion:
    data = src.read_bytes()
    text, enc = decode(data)
    digest = hashlib.sha256(data).hexdigest()
    target = src.with_suffix(".md")
    ends = line_endings(data)

    if target.exists():
        head = target.read_text(encoding="utf-8")
        meta = yaml.safe_load(head[4:head.find("\n---", 4)]) if head.startswith("---\n") else {}
        if not isinstance(meta, dict) or meta.get("converted_from") != src.name:
            return Conversion(src, target, enc, ends, 0, 0, "skipped",
                              f"{target.name} exists and was not made by `wiki convert`; not overwritten")
        if meta.get("original_sha256") == digest and not force:
            return Conversion(src, target, enc, ends, int(meta.get("words", 0)), 0, "unchanged")

    body, headings = to_markdown(text)
    before, after = words_of_original(text), WORDS.findall(body)
    if before != after:
        first = next((i for i, (a, b) in enumerate(zip(before, after)) if a != b), min(len(before), len(after)))
        raise ValueError(f"conversion of {src.name} would change the text near word {first} "
                         f"({before[first:first + 5]} vs {after[first:first + 5]}); nothing written")

    meta = {"converted_from": src.name, "original_sha256": digest, "original_encoding": enc,
            "original_line_endings": ends, "words": len(after),
            "converted_by": "wiki convert (harness/convert.py): encoding, line endings, "
                            "bullets and headings only; word sequence verified identical"}
    front = yaml.safe_dump(meta, sort_keys=False, allow_unicode=True, width=1000).strip()
    target.write_text(f"---\n{front}\n---\n\n{body}", encoding="utf-8")
    return Conversion(src, target, enc, ends, len(after), headings, "written")


def convert_all(paths: list[Path], force: bool = False) -> list[Conversion]:
    files = []
    for p in paths:
        files += [p] if p.is_file() else sorted(p.rglob("*.txt"))
    return [convert_file(f, force) for f in files if f.suffix.lower() == ".txt"]
