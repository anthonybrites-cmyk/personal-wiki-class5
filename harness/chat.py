"""Chat mode: the personal assistant.

Per turn the harness (1) handles slash commands, (2) asks the router whether this
message needs the notes, (3) retrieves only if so, (4) builds persona + topics +
passages + recent history, (5) streams Gemma's reply, (6) checks any [S#] labels
against the passages actually supplied, and (7) appends the turn to a transcript.
"""
from __future__ import annotations

import re
import sys
import time
from datetime import datetime

from . import config, prompts, records, router, ui, wikipages
from .citations import LABEL
from .llm import LocalGemma
from .retrieval import Hit, Index

MAX_ACTIVE_PASSAGES = 8  # passages kept in context across follow-ups

HELP = """\
  /notes <question>  search the wiki now and answer from the passages
  /sources           show the passages behind the last reply
  /save              save the last reply to drafts/ (a generated draft, not evidence)
  /reset             forget the conversation and retrieved passages
  /help              this list
  /exit              quit (Ctrl-D also works)"""


class ChatSession:
    def __init__(self, index: Index, gemma: LocalGemma):
        self.index, self.gemma = index, gemma
        self.topics = wikipages.topic_map()
        self.topic_groups: dict[str, list[str]] = {}
        for note in wikipages.all_notes():
            self.topic_groups.setdefault(str(note.meta.get("type", "note")), []).append(note.title)
        self.history: list[dict] = []
        self.passages: dict[str, Hit] = {}   # label -> hit, labels stable for the session
        self.turns: list[dict] = []
        self.last_reply = ""
        self.last_cited: list[str] = []
        self.started = datetime.now()

    # --- retrieval with session-stable labels ----------------------------------------
    def _retrieve(self, query: str, topics: tuple[str, ...] = ()) -> list[Hit]:
        # A named wiki topic narrows the search to the files that topic comes from, so
        # "my Pac-Man agent" can't pull in the Custom LLM's similarly titled sections.
        paths = wikipages.sources_for(list(topics)) if topics else None
        hits = self.index.search(query, k=config.CHAT_TOP_K, paths=paths or None,
                                 max_per_source=config.CHAT_TOP_K if paths else None)
        by_id = {h.passage.id: lbl for lbl, h in self.passages.items()}
        for h in hits:
            if h.passage.id in by_id:
                h.label = by_id[h.passage.id]
            else:
                h.label = f"S{len(self.passages) + 1}"
                self.passages[h.label] = h
        # Keep only the most recent passages in context; older labels stay valid in
        # the transcript but are no longer shown to the model.
        if len(self.passages) > MAX_ACTIVE_PASSAGES:
            keep = sorted(self.passages, key=lambda l: int(l[1:]))[-MAX_ACTIVE_PASSAGES:]
            self.passages = {l: self.passages[l] for l in keep}
        return hits

    def _context_hits(self) -> list[Hit]:
        return [self.passages[l] for l in sorted(self.passages, key=lambda l: int(l[1:]))]

    # --- one turn -----------------------------------------------------------------------
    def turn(self, message: str, force_query: str | None = None) -> str:
        if force_query is not None:
            route = router.Route(True, "forced with /notes", force_query)
        else:
            route = router.decide(message, self.topics, bool(self.history))

        new_hits: list[Hit] = []
        if route.retrieve:
            new_hits = self._retrieve(route.query, route.topics)
            if new_hits:
                labels = ", ".join(h.label for h in new_hits)
                print(ui.dim(f"  · notes: searched ({route.reason}) → {labels}"))
            else:
                print(ui.dim(f"  · notes: searched ({route.reason}) → nothing relevant found"))
        else:
            print(ui.dim(f"  · notes: not searched ({route.reason})"))

        context = self._context_hits()
        system = prompts.chat_system(self.topic_groups, context)
        self.history.append({"role": "user", "content": message})
        messages = prompts.chat_messages(system, self.history, remind_citations=bool(new_hits))

        print(ui.bold(ui.magenta("marginalia> ")), end="", flush=True)
        reply, stats = self.gemma.generate(messages, config.CHAT_MAX_TOKENS,
                                           config.CHAT_TEMPERATURE,
                                           on_text=lambda s: print(s, end="", flush=True))
        print()

        # Citation check: every [S#] must be a passage the model was actually given.
        given = {h.label for h in context}
        cited = list(dict.fromkeys(LABEL.findall(reply)))
        bogus = [c for c in cited if c not in given]
        if cited:
            print(ui.dim("  sources:"))
            for c in cited:
                if c in given:
                    print(ui.dim(f"    [{c}] {self.passages[c].passage.location}"))
        if new_hits and not cited:
            print(ui.yellow("  note: notes were retrieved but the reply cites none of them — "
                            "treat any facts from the notes in it as unverified"))
        if bogus:
            print(ui.red(f"  ⚠ cites {', '.join(bogus)} but no such passage was retrieved — "
                         "treat those claims as unsupported"))
        print(ui.dim(f"  [{stats.short()}]"))
        print()

        if reply:
            self.history.append({"role": "assistant", "content": reply})
        else:
            self.history.pop()
        self.last_reply, self.last_cited = reply, [c for c in cited if c in given]
        self.turns.append({
            "user": message, "route": {"retrieve": route.retrieve, "reason": route.reason,
                                       "query": route.query},
            "retrieved": [h.to_dict() for h in new_hits],
            "passages_in_context": [h.label for h in context],
            "reply": reply, "cited": cited, "unknown_citations": bogus,
            "stats": stats.to_dict(),
        })
        return reply

    # --- slash commands -----------------------------------------------------------------
    def command(self, line: str) -> bool:
        """Handle a /command. Returns False when the session should end."""
        cmd, _, arg = line.partition(" ")
        cmd = cmd.lower()
        if cmd in ("/exit", "/quit"):
            return False
        if cmd == "/help":
            print(HELP + "\n")
        elif cmd == "/reset":
            self.history.clear()
            self.passages.clear()
            print(ui.dim("  conversation and retrieved passages cleared\n"))
        elif cmd == "/sources":
            if not self.last_cited:
                print(ui.dim("  the last reply cited no passages\n"))
            for c in self.last_cited:
                h = self.passages.get(c)
                if h:
                    print(ui.cyan(f"  [{c}] ") + h.passage.location)
                    print(ui.indent(h.passage.text.strip(), "      ") + "\n")
        elif cmd == "/save":
            self.save_draft()
        elif cmd == "/notes":
            if not arg.strip():
                print(ui.dim("  usage: /notes <question>\n"))
            else:
                self.turn(arg.strip(), force_query=arg.strip())
        else:
            print(ui.dim(f"  unknown command {cmd} — /help lists them\n"))
        return True

    def save_draft(self) -> None:
        if not self.last_reply:
            print(ui.dim("  nothing to save yet\n"))
            return
        config.DRAFTS.mkdir(exist_ok=True)
        first = re.sub(r"[^A-Za-z0-9 ]", "", self.last_reply.split("\n")[0])[:40].strip()
        path = config.DRAFTS / f"{records.stamp()}-{records.slug(first or 'draft')}.md"
        cited = "\n".join(f"- [{c}] {self.passages[c].passage.location}"
                          for c in self.last_cited if c in self.passages) or "- none"
        path.write_text(
            "> Generated by chat (Gemma 4 E2B). This is a draft, **not source evidence**; "
            "ask mode never reads drafts/.\n\n"
            f"{self.last_reply}\n\n## Passages cited\n\n{cited}\n", encoding="utf-8")
        print(ui.dim(f"  saved {path.relative_to(config.ROOT)}\n"))

    def save_transcript(self) -> None:
        if not self.turns:
            return
        md = [f"# Chat session {self.started:%Y-%m-%d %H:%M}", "",
              f"- **Mode:** chat · **Execution:** local · **Model:** `{config.GEMMA_ID}`",
              f"- **Network:** {records.network_state()}", ""]
        for i, t in enumerate(self.turns, 1):
            r = t["route"]
            md += [f"## Turn {i}", "", f"**you>** {t['user']}", "",
                   f"*router: {'searched notes' if r['retrieve'] else 'no notes search'} — "
                   f"{r['reason']}*", ""]
            for h in t["retrieved"]:
                md.append(f"- retrieved [{h['label']}] `{h['path']}` § {h['section']} "
                          f"(lines {h['start_line']}–{h['end_line']})")
            if t["retrieved"]:
                md.append("")
            md += [f"**marginalia>** {t['reply']}", ""]
            if t["unknown_citations"]:
                md += [f"⚠ cited {', '.join(t['unknown_citations'])} with no such passage", ""]
            md += [f"<sub>{t['stats']['prompt_tokens']} prompt tok · "
                   f"{t['stats']['generated_tokens']} new tok · {t['stats']['seconds']}s</sub>", ""]
        path = records.save("chat", "session", {
            "mode": "chat", "execution": "local", "model": LocalGemma.identity(),
            "prompt_files": ["instructions/persona.md"], "turns": self.turns},
            "\n".join(md))
        print(ui.dim(f"transcript saved to {path.relative_to(config.ROOT) if path.is_relative_to(config.ROOT) else path}"))


def run(index: Index, gemma: LocalGemma) -> int:
    prompts.load_instructions(config.PERSONA_MD)  # fail fast, before loading the model
    interactive = sys.stdin.isatty()
    print(ui.dim(f"loading {config.GEMMA_ID} ..."), end="", flush=True)
    t0 = time.perf_counter()
    gemma.load()
    print("\r" + ui.dim(f"loaded {config.GEMMA_LABEL} in {time.perf_counter() - t0:.1f}s "
                        "· local · offline-pinned") + " " * 10)
    session = ChatSession(index, gemma)
    print(ui.bold("Marginalia") + ui.dim(" — your personal wiki assistant. /help for commands, "
                                         "/exit to quit.\n"))
    try:
        while True:
            try:
                line = input(ui.cyan("you> ") if interactive else "")
            except EOFError:
                print()
                break
            if not interactive:
                print(ui.cyan("you> ") + line)  # echo scripted input into the transcript
            line = line.strip()
            if not line:
                continue
            if line.startswith("/"):
                if not session.command(line):
                    break
                continue
            session.turn(line)
    except KeyboardInterrupt:
        print()
    finally:
        session.save_transcript()
    return 0
