#!/usr/bin/env python
"""Re-ingest sources with --force and prove it neither duplicates nor renames notes.

Snapshots every note under vault/ (path + content hash, ignoring the harness's
last_checked/checked_by timestamps), runs `./wiki ingest <paths> --force`, snapshots
again, and writes a Markdown report.

    .venv/bin/python scripts/reingest_check.py evidence/reingest-check.md vault/raw
"""
from __future__ import annotations

import hashlib
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VAULT = ROOT / "vault"
VOLATILE = re.compile(r"^(last_checked|checked_by):.*$\n", re.M)


def measure(time_output: str) -> str:
    """Summarise macOS `/usr/bin/time -l` output: wall time and memory."""
    def grab(pattern):
        m = re.search(pattern, time_output)
        return float(m.group(1)) if m else 0.0
    wall = grab(r"([\d.]+) real")
    rss = grab(r"(\d+)\s+maximum resident set size") / 1e9
    peak = grab(r"(\d+)\s+peak memory footprint") / 1e9
    return f"{wall:.1f} s wall · max RSS {rss:.2f} GB · peak memory footprint {peak:.2f} GB"


def snapshot() -> dict[str, str]:
    out = {}
    for p in sorted(VAULT.rglob("*.md")):
        rel = p.relative_to(VAULT).as_posix()
        if rel.startswith("raw/"):
            continue
        text = VOLATILE.sub("", p.read_text(encoding="utf-8"))
        out[rel] = hashlib.sha256(text.encode()).hexdigest()[:12]
    return out


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    report, targets = Path(sys.argv[1]), sys.argv[2:]
    raw_before = {p.relative_to(VAULT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()[:12]
                  for p in sorted((VAULT / "raw").rglob("*.md"))}
    before = snapshot()
    cmd = ["./wiki", "ingest", *targets, "--force"]
    print("$ " + " ".join(cmd), flush=True)
    timing = ROOT / "store" / ".ingest-time.txt"
    proc = subprocess.run(["/usr/bin/time", "-l", "-o", str(timing), *cmd], cwd=ROOT,
                          capture_output=True, text=True,
                          env={**__import__("os").environ, "NO_COLOR": "1"})
    output = "\n".join(l for l in (proc.stdout + proc.stderr).splitlines() if "mel filter" not in l)
    print(output)
    measured = measure(timing.read_text() if timing.exists() else "")
    timing.unlink(missing_ok=True)
    print(f"measured: {measured}")
    meas_file = __import__("os").environ.get("MEAS_FILE")
    if meas_file:  # the offline demo collects every measurement in one table
        nums = re.findall(r"[\d.]+", measured)
        with open(meas_file, "a") as fh:
            fh.write(f"ingest ({len(targets)} path(s), --force)\t" + "\t".join(nums[:3]) + "\n")
    after = snapshot()
    raw_after = {p.relative_to(VAULT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()[:12]
                 for p in sorted((VAULT / "raw").rglob("*.md"))}

    added = sorted(set(after) - set(before))
    removed = sorted(set(before) - set(after))
    changed = sorted(k for k in set(before) & set(after) if before[k] != after[k])
    machine = [k for k in after if re.search(r"\d{8}|[0-9a-f]{8,}|_|--|\bchunk\b", Path(k).stem)]
    ok = proc.returncode == 0 and not added and not removed and not machine and raw_before == raw_after

    lines = [f"# Re-ingest check — {datetime.now():%Y-%m-%d %H:%M}", "",
             f"**Result: {'PASS' if ok else 'FAIL'}** — `{' '.join(cmd)}` exited {proc.returncode}.", "",
             "| Check | Result |", "|---|---|",
             f"| Notes before → after | {len(before)} → {len(after)} |",
             f"| New files (duplicates) | {', '.join(added) or 'none'} |",
             f"| Removed / renamed files | {', '.join(removed) or 'none'} |",
             f"| Machine-style filenames | {', '.join(machine) or 'none'} |",
             f"| Content changed (ignoring last_checked) | {', '.join(changed) or 'none'} |",
             f"| Originals in raw/ unchanged | {'yes' if raw_before == raw_after else 'NO'} |",
             f"| Measured (`/usr/bin/time -l`) | {measured} |", "",
             "## Notes in the vault after re-ingest", "",
             *[f"- `{k}`" for k in after], "", "## Harness output", "", "```text", output, "```", ""]
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n{'PASS' if ok else 'FAIL'}: {len(before)} → {len(after)} notes, "
          f"{len(added)} added, {len(removed)} removed, {len(changed)} changed · report {report}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
