"""Shared grounding checks: is a generated claim actually stated in a source passage?

Used by ingestion (facts drafted by Gemma) and by ask's citation check (answer
sentences). Deliberately simple and explainable: every number in the claim must appear
in the passage, and at least half of the claim's content words must too.
"""
from __future__ import annotations

import re

from .retrieval import tokenize

NUMBER = re.compile(r"\d+(?:[.,]\d+)*")
CITED_CLAIM = re.compile(r"(.+?)((?:\s*\[S\d+\])+)([.!?]?)", re.S)


def _num(n: str) -> str:
    n = n.replace(",", "")                     # 60,743 -> 60743
    if "." in n:
        n = n.rstrip("0").rstrip(".")          # 492.0 -> 492, 0.10 -> 0.1
    return n or "0"


def numbers_in(text: str) -> set[str]:
    return {_num(n) for n in NUMBER.findall(text)}


def normalize_labels(text: str) -> str:
    """'[S1, S2]' -> '[S1][S2]' so every label is matched the same way."""
    return re.sub(r"\[(S\d+(?:\s*,\s*S\d+)+)\]",
                  lambda m: "".join(f"[{x.strip()}]" for x in m.group(1).split(",")), text)


def support(claim: str, passage_text: str, min_overlap: float = 0.5) -> tuple[bool, str]:
    missing = numbers_in(claim) - numbers_in(passage_text)
    if missing:
        return False, f"number(s) {', '.join(sorted(missing))} not in the passage"
    words = set(tokenize(claim))
    if not words:
        return False, "empty claim"
    overlap = len(words & set(tokenize(passage_text))) / len(words)
    if overlap < min_overlap:
        return False, f"only {overlap:.0%} of its words appear in the passage"
    return True, f"{overlap:.0%} word overlap"


def cited_claims(text: str) -> list[tuple[str, list[str]]]:
    """Split an answer into (claim, [labels]) pieces; a claim ends at its labels."""
    return [((m.group(1).strip() + m.group(3)).strip(), re.findall(r"S\d+", m.group(2)))
            for m in CITED_CLAIM.finditer(normalize_labels(text))]
