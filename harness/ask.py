"""Ask mode: the RAG workflow for one standalone factual question.

question -> retrieve passages -> assemble research prompt -> local Gemma
         -> check citations -> print answer + sources -> save the record
No chat history and no persona are ever loaded here.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

from . import citations, config, prompts, records, ui
from .llm import GenStats, LocalGemma
from .retrieval import Hit, Index

NO_PASSAGES = ("INSUFFICIENT EVIDENCE — no passage in the wiki's sources is relevant to "
               "this question, so the model was not called.")


@dataclass
class AskResult:
    question: str
    hits: list[Hit]
    raw: str
    report: citations.CitationReport
    stats: GenStats | None
    timings: dict = field(default_factory=dict)
    model: dict = field(default_factory=dict)


def run(question: str, index: Index, gemma: LocalGemma, k: int = config.ASK_TOP_K,
        stream: bool = False) -> AskResult:
    t0 = time.perf_counter()
    hits = index.search(question, k=k)
    t_retrieve = time.perf_counter() - t0

    if not hits:
        # Harness-level guard: nothing cleared the relevance floor, so there is no
        # evidence to give the model. Saying so is cheaper and more honest than asking.
        report = citations.check(f"ANSWER: {NO_PASSAGES}", [])
        return AskResult(question, [], f"ANSWER: {NO_PASSAGES}", report, None,
                         {"retrieve_s": round(t_retrieve, 3)}, LocalGemma.identity())

    messages = prompts.ask_messages(question, hits)
    t1 = time.perf_counter()
    gemma.load()
    t_load = time.perf_counter() - t1
    raw, stats = gemma.generate(messages, config.ASK_MAX_TOKENS, config.ASK_TEMPERATURE,
                                on_text=(lambda s: print(ui.dim(s), end="", flush=True))
                                if stream else None)
    if stream:
        print()
    report = citations.check(raw, hits, question)
    timings = {"retrieve_s": round(t_retrieve, 3), "model_load_s": round(t_load, 2),
               "generate_s": round(stats.seconds, 2),
               "total_s": round(time.perf_counter() - t0, 2)}
    return AskResult(question, hits, raw, report, stats, timings, LocalGemma.identity())


def render(res: AskResult, show_passages: bool = True) -> str:
    out = [ui.rule("ask · local · " + config.GEMMA_LABEL)]
    out.append(ui.bold("Q: ") + res.question)
    if show_passages:
        out.append("")
        out.append(ui.bold(f"Retrieved passages ({len(res.hits)})") +
                   ui.dim("  — hybrid BM25 + bge-small, original text"))
        for h in res.hits:
            out.append(f"  {ui.cyan('[' + h.label + ']')} {h.passage.location} "
                       + ui.dim(f"rrf={h.score:.4f} bm25={h.bm25:.1f} cos={h.vector:.2f}"))
    out.append("")
    r = res.report
    if r.status == "insufficient":
        out.append(ui.yellow(ui.bold("Answer: ")) + r.answer)
    else:
        out.append(ui.bold("Answer: ") + r.answer)
    used = {c for c in r.cited} | {q["label"] for q in r.quotes}
    cited_hits = [h for h in res.hits if h.label in used]
    if cited_hits:
        out.append("")
        out.append(ui.bold("Passages quoted while deciding (no answer found)" if r.insufficient
                           else "Citations"))
        for h in cited_hits:
            out.append(f"  {ui.cyan('[' + h.label + ']')} {h.passage.location}")
            for q in r.quotes:
                if q["label"] == h.label:
                    mark = (ui.green("✓ found in passage") if q["found"] else
                            ui.red(f"✗ actually in [{q['found_in']}]") if q["found_in"] else
                            ui.red("✗ not in any retrieved passage"))
                    out.append(f"       “{q['quote']}”  {mark}")
    if r.claims:
        out.append("")
        out.append(ui.bold("Claim check"))
        for c in r.claims:
            mark = (ui.green(f"✓ supported by {', '.join(c['supported_by'])}") if c["supported_by"]
                    else ui.red("✗ not supported by its cited passage"))
            out.append(f"  {mark}  {c['claim'][:90]}")
    out.append("")
    badge = {"ok": ui.green("citations verified"), "insufficient":
             ui.yellow("insufficient evidence reported"), "warning": ui.red("check failed")}[r.status]
    out.append(ui.bold("Citation check: ") + badge +
               (": " + "; ".join(r.notes) if r.notes else ""))
    for note in r.info:
        out.append(ui.dim(f"  note: {note}"))
    if res.stats:
        out.append(ui.dim(f"[{res.stats.short()} · retrieval {res.timings['retrieve_s']:.2f}s · "
                          f"model load {res.timings['model_load_s']:.1f}s]"))
    return "\n".join(out)


def to_record(res: AskResult) -> dict:
    return {
        "mode": "ask",
        "execution": "local",
        "network": records.network_state(),
        "question": res.question,
        "model": res.model,
        "retrieval": {"method": "hybrid BM25 + bge-small-en-v1.5 (RRF)", "k": len(res.hits),
                      "hits": [h.to_dict() for h in res.hits]},
        "prompt_files": ["instructions/wiki-instructions.md"],
        "raw_model_output": res.raw,
        "answer": res.report.answer,
        "citation_check": res.report.to_dict(),
        "stats": res.stats.to_dict() if res.stats else None,
        "timings": res.timings,
    }


def to_markdown(res: AskResult) -> str:
    r = res.report
    lines = [f"# Ask: {res.question}", "",
             f"- **Mode:** ask (standalone, no chat history) · **Execution:** local",
             f"- **Model:** `{res.model.get('model')}` @ `{res.model.get('revision', '')[:7]}` "
             f"({res.model.get('quantization')}; {res.model.get('runtime')})",
             f"- **Network at run time:** {records.network_state()}",
             f"- **Retrieval:** hybrid BM25 + bge-small-en-v1.5, top {len(res.hits)}", ""]
    lines += ["## Retrieved passages", ""]
    for h in res.hits:
        p = h.passage
        lines += [f"### [{h.label}] `{p.path}` § {p.section} (lines {p.start_line}–{p.end_line})",
                  f"<sub>rrf {h.score:.4f} · bm25 {h.bm25:.2f} · cosine {h.vector:.3f}</sub>", "",
                  "```text", p.text.strip(), "```", ""]
    lines += ["## Gemma's answer (verbatim)", "", "```text", res.raw.strip(), "```", "",
              "## Citation check (automatic)", "",
              f"- **Status:** {r.status}", f"- **Labels cited in answer:** {', '.join(r.cited) or 'none'}"]
    for q in r.quotes:
        where = ("found in passage" if q["found"] else
                 f"NOT in {q['label']}; the phrase is in {q['found_in']}" if q["found_in"] else
                 "NOT found in any retrieved passage")
        lines.append(f"- [{q['label']}] “{q['quote']}” — {where}")
    for c in r.claims:
        verdict = f"supported by {', '.join(c['supported_by'])}" if c["supported_by"] else "NOT supported"
        lines.append(f"- claim “{c['claim']}” — {verdict} ({c['why']})")
    for n in r.notes:
        lines.append(f"- ⚠ {n}")
    for n in r.info:
        lines.append(f"- note: {n}")
    if res.stats:
        lines += ["", "## Timing and memory", "",
                  f"- {res.stats.short()}",
                  f"- retrieval {res.timings['retrieve_s']}s · model load {res.timings['model_load_s']}s · "
                  f"total {res.timings['total_s']}s"]
    return "\n".join(lines) + "\n"
