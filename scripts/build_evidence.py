#!/usr/bin/env python
"""Turn the saved records of an offline run into evidence cards.

    .venv/bin/python scripts/build_evidence.py [run_dir]     (default: evidence/offline)

Writes evidence/ask/test-1.md … test-4.md and evidence/mode-checks.md. Each card has
the pre-registered expectation (tests/ask_tests.json), the retrieved passages, Gemma's
verbatim answer, the automatic citation check, and timing/memory. A hand-written
"## Assessment" section already in a card is kept when the card is rebuilt.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EVIDENCE = ROOT / "evidence"
KEEP = re.compile(r"^## Assessment\b.*", re.S | re.M)


def keep_assessment(path: Path) -> str:
    if path.exists():
        m = KEEP.search(path.read_text(encoding="utf-8"))
        if m:
            return m.group(0).rstrip() + "\n"
    return "## Assessment\n\n_To be written after checking the cited passages by hand._\n"


def rel(p: Path, frm: Path) -> str:
    import os
    return os.path.relpath(p, frm).replace(" ", "%20")


def load_measurements(run: Path) -> list[dict]:
    f = run / "measurements.tsv"
    return list(csv.DictReader(f.open(), delimiter="\t")) if f.exists() else []


def passage_block(h: dict, expected: bool) -> list[str]:
    tag = " ← expected evidence" if expected else ""
    return [f"#### [{h['label']}] `{h['path']}` § {h['section']} (lines {h['start_line']}–{h['end_line']}){tag}",
            f"<sub>rank {h['rank']} · rrf {h['score']} · bm25 {h['bm25']} · cosine {h['vector']}</sub>", "",
            "```text", h["text"].strip(), "```", ""]


def is_expected(h: dict, test: dict) -> bool:
    """A retrieved passage is 'expected evidence' if it comes from an expected source and
    contains one of the phrases written down before the run (tests/ask_tests.json)."""
    text = " ".join(h["text"].split()).lower()
    return h["path"] in test["expected_sources"] and \
        any(" ".join(t.split()).lower() in text for t in test.get("expected_text", []))


def ask_card(test: dict, rec: dict, rec_path: Path, meas: dict | None, run: Path) -> str:
    out = EVIDENCE / "ask"
    hits = rec["retrieval"]["hits"]
    exp_hits = [h for h in hits if is_expected(h, test)]
    exp_sources_found = sorted({h["path"] for h in hits} & set(test["expected_sources"]))
    cc = rec["citation_check"]
    m = rec["model"]
    lines = [f"# {test['id'].replace('-', ' ').title()}: {test['kind']}", "",
             f"> **{rec['question']}**", "",
             "| | |", "|---|---|",
             f"| Mode | `wiki ask` (standalone: no chat history, no persona) |",
             f"| Execution | **{rec['execution']}** · network at run time: **{rec['network']}** |",
             f"| Model | `{m['model']}` @ `{m['revision'][:7]}` — {m['quantization']} |",
             f"| Runtime | {m['runtime']} |",
             f"| Retrieval | {rec['retrieval']['method']}, top {rec['retrieval']['k']} |",
             f"| Run | {rec['saved_at']} · record [`{rec_path.name}`]({rel(rec_path, out)}) |"]
    if meas:
        lines.append(f"| Measured | {meas['wall_s']} s wall for the whole command (includes model load) · "
                     f"max RSS {meas['max_rss_gb']} GB · peak memory footprint {meas['peak_footprint_gb']} GB |")
    if rec.get("stats"):
        s = rec["stats"]
        lines.append(f"| Generation | {s['prompt_tokens']} prompt tokens → {s['generated_tokens']} new tokens "
                     f"in {s['seconds']} s ({s['generation_tps']:.0f} tok/s) · MLX peak {s['peak_memory_gb']} GB |")
    lines += ["", "## Expected (written before the run: [tests/ask-tests.md](../../tests/ask-tests.md))", "",
              f"- **Sources:** {', '.join('`' + s + '`' for s in test['expected_sources']) or 'none — not answerable'}",
              f"- **Passages containing:** {'; '.join('“' + t + '”' for t in test.get('expected_text', [])) or '—'}",
              f"- **Answer:** {test['expected_answer']}", "",
              "## Retrieval check", ""]
    if test["answerable"]:
        ranks = ", ".join(f"{h['label']} (lines {h['start_line']}–{h['end_line']})" for h in exp_hits) or "none"
        lines += [f"- Expected passages retrieved: **{ranks}**",
                  f"- Expected sources present: {len(exp_sources_found)} of {len(test['expected_sources'])} "
                  f"({', '.join(exp_sources_found) or 'none'})"]
    else:
        lines += ["- Nothing in the sources answers this; the retrieved passages below are the closest "
                  "matches the index could find."]
    lines += ["", "## Gemma's answer (verbatim)", "", "```text", rec["raw_model_output"].strip(), "```", "",
              "## Citation check (automatic, by the harness)", "",
              f"- **Status:** `{cc['status']}`"]
    for q in cc["quotes"]:
        where = "found in that passage" if q["found"] else (
            f"NOT in {q['label']} (the phrase is in {q['found_in']})" if q["found_in"] else "NOT found")
        lines.append(f"- quote [{q['label']}] “{q['quote']}” — {where}")
    for c in cc.get("claims", []):
        verdict = f"supported by {', '.join(c['supported_by'])}" if c["supported_by"] else "NOT supported"
        lines.append(f"- claim “{c['claim']}” — {verdict} ({c['why']})")
    lines += [f"- ⚠ {n}" for n in cc["notes"]] + [f"- note: {n}" for n in cc.get("info", [])]
    lines += ["", "## Retrieved passages (original text, as given to Gemma)", ""]
    for h in hits:
        lines += passage_block(h, is_expected(h, test))
    lines.append(keep_assessment(out / f"{test['id']}.md"))
    return "\n".join(lines)


def main() -> int:
    run = Path(sys.argv[1]) if len(sys.argv) > 1 else EVIDENCE / "offline"
    tests = json.loads((ROOT / "tests/ask_tests.json").read_text())["tests"]
    records = sorted((run / "runs/ask").glob("*.json"))
    meas = load_measurements(run)
    ask_meas = [m for m in meas if m["step"].startswith("ask")]
    (EVIDENCE / "ask").mkdir(parents=True, exist_ok=True)

    used = set()
    for test in tests:
        match = next((r for r in records if r not in used and
                      json.loads(r.read_text())["question"] == test["question"]), None)
        if match is None:
            print(f"no record for {test['id']}")
            continue
        used.add(match)
        rec = json.loads(match.read_text())
        m = next((x for x in ask_meas if x["step"] == f"ask {test['id']}"), None)
        card = ask_card(test, rec, match, m, run)
        (EVIDENCE / "ask" / f"{test['id']}.md").write_text(card, encoding="utf-8")
        print(f"wrote evidence/ask/{test['id']}.md ({rec['citation_check']['status']})")

    # Mode checks: chat transcript, search, and ask after the chat claim.
    chat = sorted((run / "runs/chat").glob("*.json"))
    search = sorted((run / "runs/search").glob("*.json"))
    after = [r for r in records if r not in used]
    out = EVIDENCE / "mode-checks.md"
    lines = ["# Mode-boundary checks (offline run)", "",
             "Chat, search, and ask run as separate CLI processes in the offline demo. This card "
             "collects what each one actually did. The full terminal output is in "
             f"[{rel(run / 'transcript.txt', EVIDENCE)}]({rel(run / 'transcript.txt', EVIDENCE)}).", ""]
    if chat:
        c = json.loads(chat[-1].read_text())
        lines += ["## Chat (`wiki chat`, persona from `instructions/persona.md`)", "",
                  f"Transcript record: [`{chat[-1].name}`]({rel(chat[-1], EVIDENCE)}) · "
                  f"[readable]({rel(chat[-1].with_suffix('.md'), EVIDENCE)})", "",
                  "| # | You | Router decision | Passages | Cited |", "|---|---|---|---|---|"]
        for i, t in enumerate(c["turns"], 1):
            r = t["route"]
            got = ", ".join(f"{h['label']} {h['path'].split('/')[1]} § {h['section']}" for h in t["retrieved"]) or "—"
            lines.append(f"| {i} | {t['user']} | {'search' if r['retrieve'] else 'no search'}: {r['reason']} "
                         f"| {got} | {', '.join(t['cited']) or '—'} |")
        lines.append("")
        for i, t in enumerate(c["turns"], 1):
            lines += [f"### Turn {i}: “{t['user']}”", "", "```text", t["reply"].strip(), "```", ""]
    if search:
        s = json.loads(search[0].read_text())
        lines += ["## Search (`wiki search`, no model)", "",
                  f"Query `{s['query']}` · {s['retrieval']} · record [`{search[0].name}`]({rel(search[0], EVIDENCE)})", ""]
        for h in s["hits"]:
            lines.append(f"- [{h['label']}] `{h['path']}` § {h['section']} (lines {h['start_line']}–{h['end_line']})")
        lines += ["", "The output is original passages and locations only: no answer is generated and "
                  "Gemma is never loaded (see the measured memory for `search` in "
                  f"[measurements.tsv]({rel(run / 'measurements.tsv', EVIDENCE)})).", ""]
    if after:
        a = json.loads(after[-1].read_text())
        lines += ["## Ask after the chat claim", "",
                  f"After telling chat “my networking tracker got an A+”, a new `wiki ask` process was asked "
                  f"the same question as test 4. Record [`{after[-1].name}`]({rel(after[-1], EVIDENCE)}).", "",
                  "```text", a["raw_model_output"].strip(), "```", "",
                  f"Citation check: `{a['citation_check']['status']}`.", ""]
    lines.append(keep_assessment(out))
    out.write_text("\n".join(lines), encoding="utf-8")
    print("wrote evidence/mode-checks.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
