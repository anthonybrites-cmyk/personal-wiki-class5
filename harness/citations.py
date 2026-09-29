"""Citation checks. A citation is a claim about evidence, so the harness verifies it:

  * every [S#] label must name a passage that was actually retrieved;
  * every quoted evidence phrase must really appear in the passage it cites;
  * every answer sentence must be supported by a passage it cites (its numbers appear
    there and most of its words do: see grounding.support);
  * an answer with no valid citation is flagged as unsupported (unless it is an
    explicit insufficient-evidence reply).
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field

from .grounding import cited_claims, normalize_labels, support
from .retrieval import Hit

LABEL = re.compile(r"\[(S\d+)\]")
EVIDENCE_LINE = re.compile(r"^\s*[-*]?\s*\[(S\d+)\]\s*[:\-–]?\s*[\"“”']?(.+?)[\"“”']?\s*$")
INSUFFICIENT = re.compile(r"insufficient[\s_-]*evidence", re.I)
# Refusals in the model's own words ("the notes do not cover…"), which count as
# insufficient evidence when the answer cites nothing inline.
REFUSAL = re.compile(
    r"\b(not (mentioned|covered|stated|specified|provided|given|included|found)|"
    r"do(es)? not (mention|cover|state|specify|say|include|contain|provide|give)|"
    r"no (information|mention|data) (about|on|regarding))\b", re.I)


def _norm(text: str) -> str:
    """Compare text the way a reader would: ignore Markdown emphasis, code ticks,
    table pipes, punctuation spacing, and case."""
    text = re.sub(r"[*_`|>#]", " ", text.lower())
    text = text.replace("“", '"').replace("”", '"').replace("’", "'").replace("—", "-")
    return re.sub(r"\s+", " ", re.sub(r"[^\w%+.\-/'() ]", " ", text)).strip()


def quote_found(quote: str, passage_text: str) -> bool:
    q, p = _norm(quote), _norm(passage_text)
    if not q:
        return False
    if q in p:
        return True
    # Tolerate small copying slips: 85% of the quote's words, in the passage.
    words = q.split()
    have = set(p.split())
    return len(words) >= 3 and sum(w in have for w in words) / len(words) >= 0.85


@dataclass
class CitationReport:
    insufficient: bool
    answer: str
    cited: list[str] = field(default_factory=list)          # labels used inline in the answer
    unknown: list[str] = field(default_factory=list)        # labels that match no passage
    quotes: list[dict] = field(default_factory=list)        # {label, quote, found, found_in}
    claims: list[dict] = field(default_factory=list)        # {claim, labels, supported_by, why}
    status: str = ""                                        # ok | insufficient | warning
    notes: list[str] = field(default_factory=list)          # problems (make status "warning")
    info: list[str] = field(default_factory=list)           # observations that are not failures

    def to_dict(self) -> dict:
        return asdict(self)


def parse_answer(raw: str) -> tuple[str, list[tuple[str, str]]]:
    """Split the model's reply into (answer text, [(label, quote), ...])."""
    if raw.lstrip().upper().startswith("EVIDENCE:"):  # evidence-first layout
        evidence_part, _, answer_part = raw.partition("ANSWER:")
        evidence_part = evidence_part.split("EVIDENCE:", 1)[1]
    else:
        answer_part, _, evidence_part = raw.partition("EVIDENCE:")
    answer = re.sub(r"^\s*ANSWER:\s*", "", answer_part.strip(), flags=re.I).strip()
    quotes = []
    for line in evidence_part.splitlines():
        m = EVIDENCE_LINE.match(line)
        if m:
            quotes.append((m.group(1), m.group(2).strip().strip('"“”')))
    return answer, quotes


def identifiers(question: str) -> list[str]:
    """ALL-CAPS names and codes in a question (IFRS, FASB, CVR, FAS-142), not ordinary words."""
    return list(dict.fromkeys(t for t in re.findall(r"\b[A-Z][A-Z0-9]{2,}(?:-[A-Z0-9]+)*\b", question)))


def check(raw: str, hits: list[Hit], question: str = "") -> CitationReport:
    raw = normalize_labels(raw)  # "[S1, S2]" -> "[S1][S2]"
    answer, quotes = parse_answer(raw)
    by_label = {h.label: h for h in hits}
    cited = list(dict.fromkeys(LABEL.findall(answer)))
    insufficient = bool(INSUFFICIENT.search(answer[:80])) or (not cited and bool(REFUSAL.search(answer)))
    report = CitationReport(insufficient=insufficient, answer=answer, cited=cited)
    report.unknown = [c for c in cited if c not in by_label]
    for label, quote in quotes:
        hit = by_label.get(label)
        found = bool(hit and quote_found(quote, hit.passage.text))
        # If the phrase is real but sits in a different retrieved passage, say which.
        found_in = label if found else next(
            (h.label for h in hits if quote_found(quote, h.passage.text)), None)
        report.quotes.append({"label": label, "quote": quote, "found": found,
                              "found_in": found_in})

    if insufficient:
        report.status = "insufficient"
        if cited:
            report.notes.append("says insufficient evidence but also cites passages")
        if not INSUFFICIENT.search(answer[:80]):
            report.info.append("refusal phrased in the model's own words, not the required "
                               "INSUFFICIENT EVIDENCE format")
        return report

    # Specific identifiers in the question (standard names, codes, acronyms such as
    # FASB or IFRS) must appear in a cited passage; otherwise the answer may be a
    # true statement about a *different* trial or product.
    cited_text = " ".join(by_label[l].passage.text for l in
                          set(cited) | {q["label"] for q in report.quotes} if l in by_label)
    for term in identifiers(question):
        if term.lower() not in cited_text.lower():
            report.notes.append(f"the question names {term}, but no cited passage mentions it: "
                                "the answer may be about something else")

    # A citation is either an inline [S#] in the answer or a labelled evidence quote.
    labels = list(dict.fromkeys(cited + [q["label"] for q in report.quotes]))
    report.unknown = [c for c in labels if c not in by_label]
    valid = [c for c in labels if c in by_label]
    verified = {q["label"] for q in report.quotes if q["found"]}

    # Claim-level check: each cited sentence must be stated in one of its passages.
    for claim, claim_labels in cited_claims(answer):
        known = [l for l in claim_labels if l in by_label]
        results = {l: support(claim, by_label[l].passage.text) for l in known}
        ok = [l for l, (good, _) in results.items() if good]
        why = "; ".join(f"{l}: {r[1]}" for l, r in results.items()) or "no retrieved passage cited"
        report.claims.append({"claim": claim, "labels": claim_labels, "supported_by": ok, "why": why})
        verified.update(ok)
        if not ok:
            report.notes.append(f"claim not supported by its cited passage(s): “{claim[:80]}” ({why})")
    if not valid:
        report.notes.append("answer cites no retrieved passage: treat it as unsupported")
    if report.unknown:
        report.notes.append(f"unknown labels {', '.join(report.unknown)}: no such passage")
    for q in report.quotes:
        if q["found"]:
            continue
        if q["found_in"]:
            report.notes.append(f"quote labelled {q['label']} is really from {q['found_in']}")
        else:
            report.notes.append(f"quote labelled {q['label']} not found in any retrieved passage")
    unverified = [c for c in valid if c not in verified]
    if unverified:
        report.notes.append(f"no verified quote for {', '.join(unverified)}")
    if valid and not cited:
        report.info.append("labels appear only in the EVIDENCE list, not inline in the answer")
    report.status = "ok" if valid and not report.notes else "warning"
    return report
