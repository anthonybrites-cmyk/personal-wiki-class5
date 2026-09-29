"""Wiki notes on disk: frontmatter, readable filenames, and Obsidian links.

Machine identity (source path, content hash, model, timestamps) lives in YAML
frontmatter; the filename and the first heading are the human-readable title.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

from . import config

BAD_FILENAME_CHARS = re.compile(r'[\\/:*?"<>|#^\[\]]')
MACHINE_LOOKING = re.compile(
    r"(\d{8}|\d{4}-\d{2}-\d{2}|[0-9a-f]{8,}|\bchunk\b|\btask[-_ ]?\d|\.[a-z]{1,4}$|_|--)", re.I)


@dataclass
class Note:
    path: Path
    meta: dict
    body: str

    @property
    def title(self) -> str:
        return self.path.stem

    @property
    def folder(self) -> str:
        return self.path.parent.name


def split_frontmatter(text: str) -> tuple[dict, str]:
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end != -1:
            meta = yaml.safe_load(text[4:end]) or {}
            return (meta if isinstance(meta, dict) else {}), text[end + 4:].lstrip("\n")
    return {}, text


def render(meta: dict, body: str) -> str:
    front = yaml.safe_dump(meta, sort_keys=False, allow_unicode=True, width=1000).strip()
    return f"---\n{front}\n---\n\n{body.rstrip()}\n"


def read(path: Path) -> Note:
    meta, body = split_frontmatter(path.read_text(encoding="utf-8"))
    return Note(path, meta, body)


def all_notes() -> list[Note]:
    if not config.WIKI.exists():
        return []
    return [read(p) for p in sorted(config.WIKI.rglob("*.md"))]


def find_by_source(source: str) -> Note | None:
    """Re-ingestion looks notes up by the source path in their metadata, not by
    filename, so a note renamed in Obsidian is still found and updated in place."""
    for note in all_notes():
        if note.meta.get("source") == source:
            return note
    return None


def topic_map() -> dict[str, str]:
    """lower-cased title/alias -> note title; chat's router uses this to notice
    when a message is about something in the wiki."""
    out: dict[str, str] = {}
    for note in all_notes():
        for name in [note.title, *(note.meta.get("aliases") or [])]:
            key = str(name).lower().strip()
            if len(key) >= 3:
                out[key] = note.title
    return out


def sources_for(titles: list[str]) -> set[str]:
    """Source files behind wiki notes: a source note's own file, or for a topic, the
    files of every source note that links to it. Lets chat search only the files a
    named topic actually comes from."""
    wanted = {t.lower() for t in titles}
    out: set[str] = set()
    for note in all_notes():
        if note.meta.get("type") != config.SOURCE_KIND or not note.meta.get("source"):
            continue
        linked = {str(t).lower() for key in config.TOPIC_KINDS.values()
                  for t in (note.meta.get(key) or [])}
        if note.title.lower() in wanted or linked & wanted:
            out.add(note.meta["source"])
    return out


def clean_title(raw: str) -> str:
    """Turn a proposed title into a safe, readable filename stem."""
    t = BAD_FILENAME_CHARS.sub(" ", raw or "")
    t = re.sub(r"\(.*?\)", " ", t)                      # drop parentheticals
    t = re.sub(r"\s+[—–-]\s+.*$", "", t)                 # drop " — Class 3 Submission"
    t = re.sub(r"(?<=\w)\.(?=\s|$)", "", t)             # "Ms." -> "Ms"
    t = re.sub(r"\s+", " ", t).strip(" .,-")
    return t


def title_problems(title: str) -> list[str]:
    words = title.split()
    problems = []
    if not 1 <= len(words) <= 6:
        problems.append(f"{len(words)} words (want 1-6)")
    if MACHINE_LOOKING.search(title):
        problems.append("looks machine-generated (date, hash, underscore, or chunk/task id)")
    if re.search(r"(^|\s)-{1,2}\w", title):
        problems.append("looks like a shell command")
    if title.endswith("?") or (len(words) > 4 and words[0].lower() in {"how", "what", "why", "the"}):
        problems.append("reads like a sentence, not a subject")
    return problems


def link(title: str, label: str | None = None) -> str:
    return f"[[{title}|{label}]]" if label else f"[[{title}]]"


def heading_anchor(heading: str) -> str:
    """Obsidian heading links can't contain these characters; it matches the rest."""
    return re.sub(r"\s+", " ", re.sub(r"[#|^:\[\]]", " ", heading)).strip()


def passage_link(passage) -> str:
    """Link a retrieval passage to its place in the source. A passage under a real
    section links to that heading; one in a document with no sub-headings (a prose
    write-up) links to the file and names its line range instead."""
    if passage.section == passage.title:
        lines = (f"line {passage.start_line}" if passage.start_line == passage.end_line
                 else f"lines {passage.start_line}–{passage.end_line}")
        return source_link(passage.path, label=lines)
    return source_link(passage.path, passage.section, "§ " + passage.section)


def source_link(source_path: str, heading: str | None = None, label: str | None = None) -> str:
    """Link from a wiki note to the original file (and section) under vault/raw/."""
    target = source_path[:-3] if source_path.endswith(".md") else source_path
    if heading:
        target += "#" + heading_anchor(heading)
    return f"[[{target}|{label}]]" if label else f"[[{target}]]"
