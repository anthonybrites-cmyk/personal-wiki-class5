"""`wiki` command line: parses the command, picks the mode, and reports errors plainly."""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from . import config, records, ui

EPILOG = f"""\
modes:
  chat    personal assistant with a voice and conversation memory; searches the
          notes only when a message needs them (the router's reason is printed)
  ask     one standalone factual question → retrieved passages → Gemma → cited
          answer or "insufficient evidence"; never sees chat history or persona
  search  original passages + file locations only; no answer, Gemma never loads

examples:
  wiki convert vault/raw
  wiki ingest vault/raw
  wiki search "LIFO reserve"
  wiki ask "When is goodwill recognized?" --mode local
  wiki chat
  wiki status

configuration (harness/config.py):
  model        {config.GEMMA_ID} (local MLX, offline-pinned)
  embeddings   {config.EMBED_ID}
  vault        vault/  (raw/ originals, wiki/ notes, index.md) — open it in Obsidian
  instructions instructions/persona.md (chat), wiki-instructions.md (ask),
               ingest-instructions.md (ingest)
  outputs      runs/ (or $WIKI_RUNS_DIR); machine index in store/

required inputs: Markdown or .txt files in vault/raw/ (.txt is converted to a Markdown
copy first; the original is never modified) and the model weights in the
local Hugging Face cache (see README → Setup). Nothing is fetched at run time.
"""


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="wiki", formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Personal wiki CLI: local Gemma 4 E2B + retrieval over your own notes.",
        epilog=EPILOG)
    sub = p.add_subparsers(dest="command", metavar="<command>")

    s = sub.add_parser("convert", help="make Markdown copies of .txt originals (no model)",
                       description="Decode each .txt (UTF-8, MacRoman or Windows-1252), fix line "
                                   "endings and bullets, add headings, and write NAME.md next to "
                                   "it. The .txt is never modified, and the Markdown is only "
                                   "written if its word sequence equals the original's.")
    s.add_argument("paths", nargs="*", type=Path, default=[config.RAW])
    s.add_argument("--force", action="store_true", help="rewrite even if already converted")

    s = sub.add_parser("ingest", help="turn sources in vault/raw into linked wiki notes (uses Gemma)",
                       description="Read sources, draft notes with local Gemma, check facts "
                                   "against the source, write notes, rebuild index.md and the "
                                   "retrieval index. Unchanged sources are skipped.")
    s.add_argument("paths", nargs="*", type=Path, default=[config.RAW],
                   help="files or folders under vault/raw (default: vault/raw)")
    s.add_argument("--force", action="store_true",
                   help="re-run Gemma even for unchanged sources (reviewed prose is kept)")
    s.add_argument("--overwrite-reviewed", action="store_true",
                   help="allow replacing notes marked reviewed: true")

    sub.add_parser("index", help="rebuild the retrieval index only (no Gemma)")

    s = sub.add_parser("search", help="show original matching passages (no Gemma, no answer)")
    s.add_argument("query")
    s.add_argument("-k", type=int, default=config.SEARCH_TOP_K, help="passages to show")
    s.add_argument("--scope", choices=["sources", "wiki", "all"], default="sources",
                   help="original sources (default), generated wiki notes, or both")

    s = sub.add_parser("ask", help="standalone factual answer with citations (RAG)")
    s.add_argument("question")
    s.add_argument("--mode", choices=["local"], default="local",
                   help="where the model runs; only local is implemented (default)")
    s.add_argument("-k", type=int, default=config.ASK_TOP_K, help="passages given to Gemma")
    s.add_argument("--quiet", action="store_true", help="hide the retrieved-passage list")

    s = sub.add_parser("chat", help="personal assistant with conversation memory")
    s.add_argument("--mode", choices=["local"], default="local",
                   help="where the model runs; only local is implemented (default)")

    sub.add_parser("status", help="show model, vault, index and instruction files")
    return p


def cmd_search(args) -> int:
    from .retrieval import Index
    index = Index.load()
    kinds = {"sources": ("source",), "wiki": ("wiki",), "all": ("source", "wiki")}[args.scope]
    t0 = time.perf_counter()
    hits = index.search(args.query, k=args.k, kinds=kinds)
    secs = time.perf_counter() - t0
    print(ui.rule(f"search · {args.scope} · no model"))
    print(ui.bold("query: ") + args.query)
    mode = "BM25 + bge-small vectors (RRF)" if index.embeddings is not None else "BM25 only"
    print(ui.dim(f"{len(hits)} passage(s) · {mode} · {secs:.2f}s · no answer is generated\n"))
    if not hits:
        print("No passage matched. Try other words, or `wiki search --scope all`.")
    for h in hits:
        print(ui.cyan(f"[{h.label}] ") + ui.bold(h.passage.location))
        print(ui.dim(f"     rrf {h.score:.4f} · bm25 {h.bm25:.2f} · cosine {h.vector:.3f}"))
        print(ui.indent(h.passage.text.strip(), "     ") + "\n")
    md = [f"# Search: {args.query}", "", f"- scope: {args.scope} · {mode} · no model call", ""]
    for h in hits:
        md += [f"## [{h.label}] `{h.passage.path}` § {h.passage.section} "
               f"(lines {h.passage.start_line}–{h.passage.end_line})", "",
               "```text", h.passage.text.strip(), "```", ""]
    path = records.save("search", args.query, {"mode": "search", "query": args.query,
                                               "scope": args.scope, "retrieval": mode,
                                               "hits": [h.to_dict() for h in hits]}, "\n".join(md))
    print(ui.dim(f"saved {path}"))
    return 0


def cmd_ask(args) -> int:
    from . import ask
    from .llm import LocalGemma
    from .retrieval import Index
    index = Index.load()
    res = ask.run(args.question, index, LocalGemma(), k=args.k)
    print(ask.render(res, show_passages=not args.quiet))
    path = records.save("ask", args.question, ask.to_record(res), ask.to_markdown(res))
    print(ui.dim(f"saved {path}"))
    return 0


def cmd_chat(args) -> int:
    from . import chat
    from .llm import LocalGemma
    from .retrieval import Index
    return chat.run(Index.load(), LocalGemma())


def cmd_convert(args) -> int:
    from .convert import convert_all
    results = convert_all([p.resolve() for p in args.paths], force=args.force)
    if not results:
        print("no .txt files to convert")
    for c in results:
        mark = {"written": ui.green("✓"), "unchanged": ui.dim("="), "skipped": ui.yellow("!")}[c.status]
        detail = (f"{c.encoding}, {c.line_endings} line endings → UTF-8 · {c.words} words, "
                  f"word sequence identical · {c.headings} headings" if c.status == "written"
                  else c.note or "already converted from this exact file")
        print(f"  {mark} {c.source.name} → {c.target.name} [{c.status}] {ui.dim(detail)}")
    return 0


def cmd_ingest(args) -> int:
    from .convert import convert_all
    from .ingest import Ingestor
    from .llm import LocalGemma
    gemma = LocalGemma()
    print(ui.rule("ingest · local · " + config.GEMMA_LABEL))
    for c in convert_all([p.resolve() for p in args.paths]):
        if c.status == "written":
            print(f"  {ui.green('✓')} converted {c.source.name} → {c.target.name} "
                  + ui.dim(f"({c.encoding}, {c.words} words verified unchanged)"))
    ing = Ingestor(gemma, force=args.force, overwrite_reviewed=args.overwrite_reviewed)
    out = ing.run([p.resolve() for p in args.paths])
    results = out["results"]
    changed = [r for r in results if r.status != "unchanged"]
    print(ui.dim(f"\n{len(results)} source(s): {len(changed)} processed, "
                 f"{len(results) - len(changed)} unchanged · {len(out['topics'])} topic note(s) "
                 f"written · index {out['passages']} passages · {out['seconds']:.1f}s"
                 + (f" · model load {gemma.load_seconds:.1f}s" if gemma.model else "")))
    for r in changed:
        for d in r.dropped:
            what = d.get("fact") or d.get("summary_sentence") or d.get("topic") or d.get("title")
            print(ui.yellow(f"  dropped from {r.note}: ") + f"{what!r} — {d['check']}")
    md = ["# Ingest report", ""]
    for r in results:
        md += [f"## {r.source} → {r.note} [{r.status}]", ""]
        if r.status == "unchanged":
            md += ["Source hash unchanged; Gemma not called.", ""]
            continue
        md += [f"- stats: {r.stats}", "", "### Gemma output (verbatim)", "", "```text",
               r.raw_output, "```", "", "### Facts kept"]
        md += [f"- {k['fact']} — § {k['found_section']} ({k['check']})" for k in r.kept_facts] or ["- none"]
        md += ["", "### Dropped by the source check"]
        md += [f"- {d} " for d in r.dropped] or ["- none"]
        md += ["", "### Topics", *[f"- {t['title']} ({t['kind']}) — {t['why']}" for t in r.topics], ""]
    for t in out["topics"]:
        md += [f"## Topic note: {t['topic']}", "", "```text", t["raw_output"], "```", ""]
    path = records.save("ingest", "report", {
        "mode": "ingest", "execution": "local", "seconds": round(out["seconds"], 2),
        "model_load_s": round(gemma.load_seconds, 2),
        "results": [r.__dict__ for r in results], "topics": out["topics"]}, "\n".join(md))
    print(ui.dim(f"saved {path}"))
    return 0


def cmd_index(args) -> int:
    from .retrieval import Index
    t0 = time.perf_counter()
    index = Index.build()
    kinds = {k: sum(p.kind == k for p in index.passages) for k in ("source", "wiki")}
    print(f"indexed {kinds['source']} source passages + {kinds['wiki']} wiki passages "
          f"in {time.perf_counter() - t0:.1f}s → {config.STORE.relative_to(config.ROOT)}/")
    return 0


def cmd_status(args) -> int:
    from huggingface_hub import snapshot_download
    from . import wikipages
    from .sources import list_text_files
    def cached(repo, rev=None):
        try:
            return "cached ✓  " + snapshot_download(repo, revision=rev, local_files_only=True)
        except Exception:
            return ui.red("NOT cached — see README → Setup")
    print(ui.rule("wiki status"))
    print(f"model       {config.GEMMA_ID} @ {config.GEMMA_REVISION[:7]}  ({config.GEMMA_LABEL})")
    print(f"            {cached(config.GEMMA_ID, config.GEMMA_REVISION)}")
    print(f"embeddings  {config.EMBED_ID} @ {config.EMBED_REVISION[:7]}\n            {cached(config.EMBED_ID, config.EMBED_REVISION)}")
    print(f"execution   local (HF_HUB_OFFLINE=1) · network now: {records.network_state()}")
    raws = list_text_files(config.RAW) if config.RAW.exists() else []
    originals = sorted(config.RAW.rglob("*.txt")) if config.RAW.exists() else []
    notes = wikipages.all_notes()
    by = {}
    for n in notes:
        by[n.folder] = by.get(n.folder, 0) + 1
    print(f"vault       {config.VAULT.relative_to(config.ROOT)}/ · {len(raws)} source text(s)"
          f" ({len(originals)} .txt original(s) kept unchanged) · "
          f"{len(notes)} wiki note(s) {by or ''} · index.md {'✓' if config.INDEX_MD.exists() else '✗'}")
    if config.CHUNKS_FILE.exists():
        n = sum(1 for _ in config.CHUNKS_FILE.open())
        vec = "with vectors" if config.EMBEDDINGS_FILE.exists() else "keywords only"
        print(f"index       {n} passages ({vec}) in {config.STORE.relative_to(config.ROOT)}/")
    else:
        print("index       " + ui.red("missing — run `wiki index`"))
    for f in (config.PERSONA_MD, config.RESEARCH_MD, config.INGEST_MD):
        print(f"instruction {f.relative_to(config.ROOT)} {'✓' if f.exists() else ui.red('missing')}")
    print(f"outputs     {config.RUNS}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 0
    from .llm import ModelUnavailable
    handler = {"search": cmd_search, "ask": cmd_ask, "chat": cmd_chat, "ingest": cmd_ingest,
               "convert": cmd_convert,
               "index": cmd_index, "status": cmd_status}[args.command]
    try:
        return handler(args)
    except ModelUnavailable as e:
        ui.err(str(e))
        return 2
    except (FileNotFoundError, ValueError) as e:
        ui.err(str(e))
        return 1
    except KeyboardInterrupt:
        print()
        return 130


if __name__ == "__main__":
    sys.exit(main())
