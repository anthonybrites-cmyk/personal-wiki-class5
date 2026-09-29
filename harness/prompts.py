"""Prompt assembly. Each mode loads its own instruction file; nothing is implicit.

  ask    -> instructions/wiki-instructions.md + retrieved passages + the question (no history)
  chat   -> instructions/persona.md + wiki topic list + optional passages + recent history
  ingest -> instructions/ingest-instructions.md + one source's outline and excerpts
"""
from __future__ import annotations

from pathlib import Path

from . import config
from .retrieval import Hit


def load_instructions(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8").strip()
    except OSError as e:
        raise FileNotFoundError(f"Missing instruction file {path.relative_to(config.ROOT)}: {e}")
    if not text:
        raise ValueError(f"Instruction file {path.relative_to(config.ROOT)} is empty")
    return text


def format_passages(hits: list[Hit]) -> str:
    blocks = []
    for h in hits:
        p = h.passage
        blocks.append(f"[{h.label}] {p.title} — {p.path} § {p.section}\n{p.text.strip()}")
    return "\n\n".join(blocks)


def ask_messages(question: str, hits: list[Hit]) -> list[dict]:
    """Standalone: system rules + passages + question. Chat history never enters."""
    user = (
        "SOURCE PASSAGES (original text from my notes):\n\n"
        f"{format_passages(hits)}\n\n"
        "----\n"
        f"QUESTION: {question}\n\n"
        "Check whether the passages answer this exact question. Follow the research rules "
        "and reply in the ANSWER / EVIDENCE format."
    )
    return [{"role": "system", "content": load_instructions(config.RESEARCH_MD)},
            {"role": "user", "content": user}]


def chat_system(topics: dict[str, list[str]], hits: list[Hit]) -> str:
    """Persona + what the wiki covers + the passages currently in play (if any)."""
    parts = [load_instructions(config.PERSONA_MD)]
    if topics:
        lines = [f"- {config.WIKI_FOLDERS.get(kind, kind.title())}: {', '.join(sorted(titles))}"
                 for kind, titles in sorted(topics.items())]
        parts.append("## What Anthony's wiki covers (note titles only, not evidence)\n" +
                     "\n".join(lines))
    if hits:
        parts.append(
            "## Note passages for this conversation\n"
            "The harness retrieved these from the wiki's original sources. Cite them as [S#] "
            "when you use them. Use only what they say; if they do not cover something, "
            "say so.\n\n" + format_passages(hits))
    else:
        parts.append("## Note passages for this conversation\nNone were retrieved for this "
                     "turn. Do not state facts from Anthony's notes; answer from the "
                     "conversation, or suggest `/notes <question>` to search the wiki.")
    return "\n\n".join(parts)


CITE_REMINDER = ("\n\n(Harness note: note passages are available above. Put the [S#] label "
                 "after each fact you take from them, and label your own ideas as suggestions.)")


def chat_messages(system: str, history: list[dict], remind_citations: bool = False) -> list[dict]:
    trimmed = [dict(m) for m in history[-config.CHAT_HISTORY_MESSAGES:]]
    while trimmed and trimmed[0]["role"] != "user":  # start on a whole turn
        trimmed = trimmed[1:]
    if remind_citations and trimmed:
        # Added to the outgoing copy only; the stored history keeps the user's own words.
        trimmed[-1]["content"] += CITE_REMINDER
    return [{"role": "system", "content": system}] + trimmed


def ingest_messages(source_path: str, outline: str, excerpts: str,
                    existing_topics: list[str]) -> list[dict]:
    known = ", ".join(existing_topics) if existing_topics else "(none yet)"
    user = (
        f"SOURCE FILE: {source_path}\n\n"
        f"SECTION OUTLINE:\n{outline}\n\n"
        f"EXISTING TOPIC NOTES (reuse these exact names when they fit): {known}\n\n"
        f"SOURCE TEXT (excerpts, in order):\n{excerpts}\n\n"
        "Write the note fields now, in the exact line format from the instructions."
    )
    return [{"role": "system", "content": load_instructions(config.INGEST_MD)},
            {"role": "user", "content": user}]


def concept_messages(concept: str, hits: list[Hit]) -> list[dict]:
    user = (
        f"TOPIC: {concept}\n\nSOURCE PASSAGES:\n\n{format_passages(hits)}\n\n"
        f"In 2 sentences, explain what {concept} is and how it shows up in these notes. "
        "Use only the passages. Put a label like [S1] after each claim. "
        "If the passages say little about it, write one sentence and cite it."
    )
    return [{"role": "system", "content": "You write short, accurate wiki summaries from "
             "the passages you are given. No outside knowledge, no speculation."},
            {"role": "user", "content": user}]

