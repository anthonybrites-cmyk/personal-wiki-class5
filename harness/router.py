"""Chat's retrieval decision. Deliberately rule-based and printed every turn, so you
can see (and test) why a message did or did not trigger a notes search.

Order matters: follow-ups and small talk are recognised first, then signals that the
user wants their own notes (explicit phrases, or a wiki topic name / alias).
"""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class Route:
    retrieve: bool
    reason: str
    query: str = ""
    topics: tuple[str, ...] = ()   # wiki notes the message names (narrows the search)


FOLLOW_UP = re.compile(
    r"^(please\s+)?(make|keep|cut|trim|shorten|expand|rewrite|rephrase|reword|simplify|"
    r"summari[sz]e|condense|polish|tweak|turn|format|translate|redo|try)\b.*\b(it|that|this|"
    r"them|those|shorter|longer|bullets?|again|version|draft|plan|list)\b|"
    r"^(shorter|longer|more (formal|casual|detail)|less \w+|again|another one|one more)\b",
    re.I)

SMALL_TALK = re.compile(
    r"^(hi|hey|hello|yo|thanks|thank you|thx|cool|nice|great|ok(ay)?|bye|good (morning|night))\b|"
    r"\bwhat (can|could|should) (we|you|i) do\b|"
    r"\bwhat can you (help|do)\b|\bhelp me with\b\??$|\bwho are you\b|\bwhat are you\b|"
    r"\bhow do(es)? (you|this|the tool) work\b|\bwhat commands\b",
    re.I)

NOTES_INTENT = re.compile(
    r"\b(my|our) (notes?|wiki|projects?|assignments?|repos?|readmes?|class(es)?|coursework|"
    r"write-?ups?|cases?|study guides?|finals?|exams?|courses?)\b|"
    r"\baccording to\b|\bin my (notes|wiki)\b|\bwhat did i\b|\bdid i\b|\bremind me\b|"
    r"\bhow did (i|my)\b|\bwhich of my\b|\bdo my notes\b",
    re.I)


REFERS_BACK = re.compile(r"\b(it|that|this|these|those|them|above|previous|again)\b", re.I)


def decide(message: str, topics: dict[str, str], have_history: bool) -> Route:
    """topics maps lower-cased names/aliases -> wiki note title."""
    text = message.strip()
    low = f" {text.lower()} "
    named = sorted({title for alias, title in topics.items()
                    if re.search(rf"(?<![a-z0-9]){re.escape(alias)}(?![a-z0-9])", low)})
    # "make that shorter" is a follow-up; "Summarize goodwill impairment in 3 bullets" is a
    # new request that names a wiki topic and does not point back at the last reply.
    if have_history and FOLLOW_UP.search(text) and (not named or REFERS_BACK.search(text)):
        return Route(False, "follow-up on the previous reply — uses the conversation")
    if SMALL_TALK.search(text) and not NOTES_INTENT.search(text):
        return Route(False, "conversational / capabilities question")

    if named:
        return Route(True, "mentions wiki topic: " + ", ".join(named[:3]), text, tuple(named))
    if NOTES_INTENT.search(text):
        return Route(True, "asks about your own notes/projects", text)
    return Route(False, "general brainstorming/drafting — no notes needed")
