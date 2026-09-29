#!/usr/bin/env python
"""Check every [[wikilink]] in the vault: the target note must exist (and be
unambiguous), and a #heading must exist in the target. Mirrors Obsidian's rules:
a bare name matches a unique file stem anywhere; a path matches from the vault root.

    .venv/bin/python scripts/check_links.py [report.md]
"""
from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VAULT = ROOT / "vault"
LINK = re.compile(r"(?<!!)\[\[([^\]|#\\]+)(?:#([^\]|]+))?(?:\\?\|[^\]]*)?\]\]")
HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*$", re.M)


def norm_heading(h: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[#|^:\[\]]", " ", h)).strip().lower()


def main() -> int:
    files = sorted(p for p in VAULT.rglob("*.md") if ".obsidian" not in p.parts)
    by_stem, by_path = defaultdict(list), {}
    for p in files:
        rel = p.relative_to(VAULT).with_suffix("").as_posix()
        by_stem[p.stem.lower()].append(p)
        by_path[rel.lower()] = p
    headings = {p: {norm_heading(h) for h in HEADING.findall(p.read_text(encoding="utf-8"))}
                for p in files}

    total, problems, per_file = 0, [], defaultdict(int)
    for p in files:
        if p.is_relative_to(VAULT / "raw"):
            continue  # originals are unchanged copies; their links are not ours to fix
        for target, heading in LINK.findall(p.read_text(encoding="utf-8")):
            total += 1
            per_file[p] += 1
            key = target.strip().lower()
            hits = [by_path[key]] if key in by_path else by_stem.get(key, [])
            where = p.relative_to(VAULT).as_posix()
            if not hits:
                problems.append(f"{where}: [[{target}]] → no such note")
            elif len(hits) > 1:
                problems.append(f"{where}: [[{target}]] → ambiguous ({len(hits)} files)")
            elif heading and norm_heading(heading) not in headings[hits[0]]:
                problems.append(f"{where}: [[{target}#{heading}]] → heading not found")

    lines = [f"# Link check", "", f"- notes checked: {sum(1 for p in files if not p.is_relative_to(VAULT / 'raw'))}",
             f"- wikilinks checked: {total}", f"- broken or ambiguous: {len(problems)}", ""]
    lines += [f"- ✗ {x}" for x in problems] or ["All links resolve to an existing note, and every #heading exists."]
    report = "\n".join(lines) + "\n"
    print(report)
    if len(sys.argv) > 1:
        Path(sys.argv[1]).write_text(report, encoding="utf-8")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
