"""Ingestion: original sources -> local Gemma -> checked, linked wiki notes.

For each source file under vault/raw/:
  1. hash it; skip if unchanged since the last ingest (unless --force);
  2. send its outline and excerpts to Gemma with instructions/ingest-instructions.md;
  3. parse the line-format reply and CHECK it against the source:
       - every FACT must be found in a passage of this source (numbers must match),
         and links to the section where the harness found it, not where Gemma said;
       - summary sentences with numbers that are not in the source are dropped;
       - titles must be short and readable, never hashes, dates or sentences;
  4. write/update the source note, found by `source:` in its frontmatter (so it is
     never duplicated, even if renamed), and create/update topic notes;
  5. rebuild vault/index.md, the Source Catalog, and the retrieval index.

Notes marked `reviewed: true` keep their reviewed prose: re-ingesting an unchanged
source only refreshes metadata and link sections, and saves Gemma's fresh draft to
runs/ingest/ for comparison instead of overwriting the reviewed text.
"""
from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from . import config, prompts, records, ui, wikipages
from .grounding import CITED_CLAIM, normalize_labels, numbers_in, support
from .llm import LocalGemma
from .retrieval import Embedder, Index, tokenize
from .sources import (Passage, chunk_markdown, list_text_files, section_outline, sha256_file,
                      vault_relative, word_count)

IMAGE_LINE = re.compile(r"^\s*!\[.*\]\(.*\)\s*$")


# --- parsing Gemma's line format ------------------------------------------------------
@dataclass
class Draft:
    title: str = ""
    aliases: list[str] = field(default_factory=list)
    description: str = ""
    summary: str = ""
    facts: list[tuple[str, str]] = field(default_factory=list)          # (fact, section)
    topics: list[tuple[str, str, str]] = field(default_factory=list)    # (name, kind, why)


def parse_draft(raw: str) -> Draft:
    """Parse the line format. Small models sometimes put `|| SECTION:` / `|| WHY:` parts
    on their own lines, so a bare SECTION/KIND/WHY line attaches to the item above it."""
    d = Draft()
    last = None  # ("fact", i) or ("topic", i)
    for line in raw.splitlines():
        key, _, value = line.strip().lstrip("-* ").partition(":")
        key, value = key.strip().upper(), value.strip()
        parts = [p.strip() for p in value.split("||")]
        fields = {p.split(":", 1)[0].strip().upper(): p.split(":", 1)[1].strip()
                  for p in parts[1:] if ":" in p}
        if key == "TITLE":
            d.title = value
        elif key == "ALIASES":
            d.aliases = [a.strip() for a in value.split(",")
                         if a.strip() and a.strip().lower() != "none"]
        elif key == "DESCRIPTION":
            d.description = value
        elif key == "SUMMARY":
            d.summary = value
        elif key == "FACT" and parts[0]:
            d.facts.append((parts[0], fields.get("SECTION", "")))
            last = ("fact", len(d.facts) - 1)
        elif key in ("ORG", "ORGANIZATION", "TOOL", "CONCEPT", "TOPIC") and parts[0]:
            kind = "organization" if key in ("ORG", "ORGANIZATION", "TOOL") or \
                fields.get("KIND", "").lower().startswith(("org", "tool")) else "concept"
            d.topics.append((parts[0], kind, fields.get("WHY", "")))
            last = ("topic", len(d.topics) - 1)
        elif key == "SECTION" and last and last[0] == "fact":
            fact, _ = d.facts[last[1]]
            d.facts[last[1]] = (fact, value)
        elif key in ("WHY", "KIND") and last and last[0] == "topic":
            name, kind, why = d.topics[last[1]]
            if key == "WHY":
                why = value
            else:
                kind = "organization" if value.lower().startswith(("org", "tool")) else "concept"
            d.topics[last[1]] = (name, kind, why)
    return d


# --- checking the draft against the source --------------------------------------------
def named_in_source(name: str, text: str) -> bool:
    """A topic must be something the source actually names: every word of it (or its
    acronym) appears in the source text."""
    low = text.lower()
    words = [w for w in re.findall(r"[a-z0-9]+", name.lower()) if w not in {"and", "of", "the"}]
    if words and all(re.search(rf"\b{re.escape(w)}", low) for w in words):
        return True
    return len(words) > 1 and re.search(rf"\b{initials(name)}\b", low) is not None


def excerpt_for_prompt(passages: list[Passage], budget: int) -> str:
    """Give Gemma a representative slice of a long source: passages in order, but at
    most an even share of the word budget per section so late sections still appear."""
    sections: dict[str, list[Passage]] = {}
    for p in passages:
        sections.setdefault(p.section, []).append(p)
    share = max(60, budget // max(len(sections), 1))
    out, used = [], 0
    for section, ps in sections.items():
        text = "\n".join(l for p in ps for l in p.text.splitlines() if not IMAGE_LINE.match(l))
        words = text.split()
        if len(words) > share:
            text = " ".join(words[:share]) + " …"
        out.append(f"## {section}\n{text}")
        used += min(len(words), share)
        if used >= budget:
            break
    return "\n\n".join(out)


# --- topic names ------------------------------------------------------------------------
def norm_name(name: str) -> str:
    n = re.sub(r"[^a-z0-9 ]", " ", name.lower())
    return re.sub(r"\s+", " ", " ".join(w[:-1] if len(w) > 3 and w.endswith("s") else w
                                        for w in n.split())).strip()


def initials(name: str) -> str:
    return "".join(w[0] for w in re.split(r"[\s\-]+", name) if w).lower()


def match_topic(name: str, existing: dict[str, dict]) -> str | None:
    """Return the title of an existing topic this name refers to, if any."""
    n = norm_name(name)
    for title, info in existing.items():
        names = [title, *info.get("aliases", [])]
        for cand in names:
            c = norm_name(cand)
            if n == c:
                return title
            # "Postgres Row Level Security" ~ "Row Level Security"
            if len(c.split()) >= 2 and len(n.split()) >= 2 and (f" {c} " in f" {n} " or f" {n} " in f" {c} "):
                return title
        if name.isupper() and 2 <= len(name) <= 5 and name.lower() == initials(title):
            return title
        if title.isupper() and 2 <= len(title) <= 5 and title.lower() == initials(name):
            return title
    return None


def reviewed_topics(note: wikipages.Note) -> list[dict]:
    """For a reviewed note the human-edited note is the truth: its `concepts:` /
    `organizations:` frontmatter lists, with each reason taken from its '- [[X]] — why' line."""
    whys = {m.group(1): m.group(2).strip() for m in re.finditer(
        r"^- \[\[([^\]|]+)(?:\|[^\]]*)?\]\]\s*(?:—|-)?\s*(.*)$", note.body, re.M)}
    out = []
    for kind, key in config.TOPIC_KINDS.items():
        for title in note.meta.get(key) or []:
            out.append({"title": str(title), "kind": kind, "why": whys.get(str(title), "")})
    return out


# --- the pipeline -------------------------------------------------------------------------
@dataclass
class SourceResult:
    source: str
    status: str                          # new | updated | unchanged | kept-reviewed
    note: str = ""
    kept_facts: list[dict] = field(default_factory=list)
    dropped: list[dict] = field(default_factory=list)
    topics: list[dict] = field(default_factory=list)
    stats: dict = field(default_factory=dict)
    raw_output: str = ""


class Ingestor:
    def __init__(self, gemma: LocalGemma, force: bool = False, overwrite_reviewed: bool = False):
        self.gemma, self.force, self.overwrite_reviewed = gemma, force, overwrite_reviewed
        self.catalog = self._load_catalog()
        self.model_tag = f"{config.GEMMA_ID}@{config.GEMMA_REVISION[:7]}"
        self.now = datetime.now().isoformat(timespec="seconds")
        self.raw_index: Index | None = None
        self.touched: set[str] = set()  # topics referenced by sources processed this run

    # catalog.json: machine map of source -> note, hash, and extracted topics
    def _load_catalog(self) -> dict:
        if config.CATALOG_JSON.exists():
            return json.loads(config.CATALOG_JSON.read_text(encoding="utf-8"))
        return {"sources": {}, "topics": {}}

    def _save_catalog(self) -> None:
        config.STORE.mkdir(exist_ok=True)
        config.CATALOG_JSON.write_text(json.dumps(self.catalog, indent=2, ensure_ascii=False) + "\n",
                                       encoding="utf-8")

    def _index(self) -> Index:
        if self.raw_index is None:
            passages = [p for f in list_text_files(config.RAW) for p in chunk_markdown(f)]
            self.raw_index = Index(passages, Embedder.encode([p.search_text() for p in passages]))
        return self.raw_index

    # --- one source -------------------------------------------------------------------
    def ingest_file(self, path: Path) -> SourceResult:
        source = vault_relative(path)
        digest = sha256_file(path)
        existing = wikipages.find_by_source(source)
        entry = self.catalog["sources"].get(source, {})
        unchanged = existing is not None and existing.meta.get("source_sha256") == digest
        if unchanged and not self.force:
            return SourceResult(source, "unchanged", str(existing.path.relative_to(config.VAULT)))

        passages = chunk_markdown(path)
        outline = "\n".join(f"{'  ' * (lvl - 1)}- {h}" for lvl, h in section_outline(path))
        excerpts = excerpt_for_prompt(passages, config.INGEST_SOURCE_WORDS)
        messages = prompts.ingest_messages(source, outline, excerpts, sorted(self.catalog["topics"]))
        raw, stats = self.gemma.generate(messages, config.INGEST_MAX_TOKENS, config.INGEST_TEMPERATURE)
        draft = parse_draft(raw)
        result = SourceResult(source, "new" if existing is None else "updated",
                              stats=stats.to_dict(), raw_output=raw)

        # Facts: keep only what the harness can find in this source.
        local = Index(passages, Embedder.encode([p.search_text() for p in passages]))
        facts = []
        for fact, claimed in draft.facts:
            # Look for the fact in every passage of this source (a README has at most a
            # few dozen) and link the one that supports it best; if none does, report
            # the retrieval's top match and why it failed.
            checks = [(p, *support(fact, p.search_text())) for p in passages]
            passing = [c for c in checks if c[1]]
            if passing:
                best = max(passing, key=lambda c: float(c[2].split("%")[0]))
            else:
                top = local.search(fact, k=1, max_per_source=1)
                best = next((c for c in checks if top and c[0].id == top[0].passage.id),
                            (None, False, "no matching passage"))
            hit_passage, ok, why = best
            record = {"fact": fact, "claimed_section": claimed,
                      "found_section": hit_passage.section if hit_passage else None,
                      "lines": [hit_passage.start_line, hit_passage.end_line] if hit_passage else None,
                      "check": why}
            (result.kept_facts if ok else result.dropped).append(record)
            if ok:
                facts.append((fact, hit_passage))

        # A note summarises; it does not copy the source. Keep at most INGEST_MAX_FACTS,
        # one per section first so a long study guide isn't all "Topics I Know the Least".
        if len(facts) > config.INGEST_MAX_FACTS:
            order = list(dict.fromkeys(
                [i for i, (_, p) in enumerate(facts)
                 if p.section not in {q.section for _, q in facts[:i]}] + list(range(len(facts)))))
            keep = sorted(order[:config.INGEST_MAX_FACTS])
            for i, (fact, _) in enumerate(facts):
                if i not in keep:
                    result.dropped.append({"fact": fact, "check": f"over the {config.INGEST_MAX_FACTS}-fact limit"})
            result.kept_facts = [k for k in result.kept_facts if any(k["fact"] == facts[i][0] for i in keep)]
            facts = [facts[i] for i in keep]
        if stats.finish_reason == "length":
            result.dropped.append({"output": "truncated",
                                   "check": f"Gemma hit the {config.INGEST_MAX_TOKENS}-token limit; later lines are missing"})

        full_text = path.read_text(encoding="utf-8")
        summary_sentences = []
        for s in re.split(r"(?<=[.!?])\s+", draft.summary.strip()):
            missing = numbers_in(s) - numbers_in(full_text)
            if s and missing:
                result.dropped.append({"summary_sentence": s,
                                       "check": f"number(s) {', '.join(sorted(missing))} not in source"})
            elif s:
                summary_sentences.append(s)

        # Title: an existing note keeps its (possibly human-edited) name forever.
        h1 = next((h for lvl, h in section_outline(path) if lvl == 1), path.stem)
        if existing is not None:
            title = existing.title
        else:
            title = self._pick_title(draft.title, h1, path.stem, result)

        org_names = {norm_name(n) for n, kind, _ in draft.topics if kind == "organization"}
        aliases = [a for a in dict.fromkeys(draft.aliases)
                   if a.lower() in full_text.lower() and a.lower() != title.lower()
                   and norm_name(a) not in org_names and a.lower() not in {"n/a", "na"}]
        if re.search(r"\b(assignment|final|write-?up|individual|study guide)\b", title, re.I):
            result.dropped.append({"title": title, "check": "kept, but it names the document type "
                                   "rather than the subject: consider renaming in review"})

        # Topics: merge with existing topics, never link a source note to itself.
        topics = []
        for name, kind, why in draft.topics[:6]:
            clean = wikipages.clean_title(name)
            if not clean or wikipages.title_problems(clean) or norm_name(clean) == norm_name(title):
                result.dropped.append({"topic": name, "check": "not a usable note name"})
                continue
            reused = match_topic(clean, self.catalog["topics"]) is not None
            if not named_in_source(clean, full_text) and not (
                    reused and any(w in full_text.lower() for w in norm_name(clean).split() if len(w) > 2)):
                result.dropped.append({"topic": name, "check": "the source never names it"})
                continue
            matched = match_topic(clean, self.catalog["topics"])
            final = matched or clean
            if any(t["title"] == final for t in topics):
                continue
            kind = kind if kind in config.TOPIC_KINDS else "concept"
            topics.append({"title": final, "kind": self.catalog["topics"].get(final, {}).get("kind", kind),
                           "why": why.rstrip(".")})
        result.topics = topics
        self.touched.update(t["title"] for t in topics)

        # Write (or protect) the source note.
        reviewed = bool(existing and existing.meta.get("reviewed"))
        protect = reviewed and unchanged and not self.overwrite_reviewed
        folder = config.WIKI / config.WIKI_FOLDERS[config.SOURCE_KIND]
        note_path = existing.path if existing else folder / f"{title}.md"
        original = self._original_of(path)
        if protect:
            result.status = "kept-reviewed"
            meta = dict(existing.meta)
            meta.update({"last_checked": self.now, "checked_by": self.model_tag})
            body = self._replace_section(existing.body, "Source",
                                         self._source_section(source, digest, original))
            topics = reviewed_topics(existing)  # reviewed links stay as reviewed
            self._write(note_path, meta, body)
            draft_md = self._source_body(title, summary_sentences, facts, topics, source, digest,
                                         original)
            records.save("ingest-drafts", title, {"source": source, "raw_output": raw}, draft_md)
        else:
            if reviewed:  # source changed: back up the reviewed text before regenerating
                records.save("ingest-backups", title, {"source": source},
                             existing.path.read_text(encoding="utf-8"))
            meta = {
                "type": config.SOURCE_KIND,
                "source": source,
                "source_sha256": digest,
                **({"original": original["path"], "original_sha256": original["sha256"]}
                   if original else {}),
                "aliases": aliases if not existing else (existing.meta.get("aliases") or aliases),
                "description": draft.description.rstrip(".") or h1,
                **{key: [t["title"] for t in topics if t["kind"] == kind]
                   for kind, key in config.TOPIC_KINDS.items()},
                "generated_by": self.model_tag,
                "ingested_at": self.now,
                "reviewed": False,
            }
            self._write(note_path, meta, self._source_body(title, summary_sentences, facts, topics,
                                                           source, digest, original))
        result.note = str(note_path.relative_to(config.VAULT))

        self.catalog["sources"][source] = {
            "note": result.note, "title": note_path.stem, "sha256": digest,
            "ingested_at": self.now, "model": self.model_tag,
            "topics": topics, "reviewed": reviewed,
        }
        for t in topics:
            info = self.catalog["topics"].setdefault(t["title"], {"kind": t["kind"], "aliases": []})
            info.setdefault("kind", t["kind"])
        return result

    def _pick_title(self, proposed: str, h1: str, folder: str, result: SourceResult) -> str:
        taken = {n.title.lower() for n in wikipages.all_notes()}
        for cand in (proposed, h1, folder.replace("-", " ").title()):
            t = wikipages.clean_title(cand)
            problems = wikipages.title_problems(t) if t else ["empty"]
            if not problems and t.lower() not in taken:
                return t
            result.dropped.append({"title": cand, "check": "; ".join(problems) or "name already used"})
        return wikipages.clean_title(folder.replace("-", " ").title()) + " - Notes"

    # --- note bodies -------------------------------------------------------------------------
    @staticmethod
    def _original_of(path: Path) -> dict | None:
        """If this Markdown file was converted from a .txt, the untouched original."""
        meta, _ = wikipages.split_frontmatter(path.read_text(encoding="utf-8"))
        if meta.get("converted_from"):
            return {"path": vault_relative(path.parent / meta["converted_from"]),
                    "sha256": meta.get("original_sha256", "")}
        return None

    def _source_body(self, title, summary, facts, topics, source, digest, original) -> str:
        lines = [f"# {title}", "", " ".join(summary) or "_Summary pending review._", "",
                 "## Key facts", ""]
        for fact, p in facts:
            lines.append(f"- {fact.rstrip('.')}. ({wikipages.passage_link(p)})")
        if not facts:
            lines.append("- _No fact passed the source check; see the ingest report._")
        lines += ["", "## Related notes", ""]
        for t in topics:
            why = f" — {t['why']}" if t["why"] else ""
            lines.append(f"- {wikipages.link(t['title'])}{why}")
        lines += ["", self._source_section(source, digest, original)]
        return "\n".join(lines)

    def _source_section(self, source: str, digest: str, original: dict | None) -> str:
        if original:
            return "\n".join([
                "## Source", "",
                f"- Text: {wikipages.source_link(source, label=source)} (Markdown conversion, words unchanged)",
                f"- Original file (unchanged): `{original['path']}` · SHA-256 `{original['sha256'][:12]}…`",
                "- Drafted by local Gemma 4 E2B · see [[Source Catalog]]",
            ])
        return "\n".join([
            "## Source", "",
            f"- Original (unchanged): {wikipages.source_link(source, label=source)}",
            f"- SHA-256 `{digest[:12]}…` · drafted by local Gemma 4 E2B · see [[Source Catalog]]",
        ])

    @staticmethod
    def _replace_section(body: str, heading: str, new: str) -> str:
        """Swap one '## heading' section (up to the next '## ') for new text."""
        pattern = re.compile(rf"^## {re.escape(heading)}\n.*?(?=^## |\Z)", re.S | re.M)
        if pattern.search(body):
            return pattern.sub(lambda _: new.rstrip() + "\n\n", body, count=1).rstrip() + "\n"
        return body.rstrip() + "\n\n" + new + "\n"

    @staticmethod
    def _write(path: Path, meta: dict, body: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(wikipages.render(meta, body), encoding="utf-8")

    # --- topic notes ---------------------------------------------------------------------
    def update_topics(self, report: list[dict]) -> None:
        """Create missing topic notes (Gemma summary grounded in retrieved passages) and
        refresh every topic's 'Appears in' links from the catalog."""
        users: dict[str, list[tuple[str, str]]] = {}
        used_in: dict[str, set[str]] = {}
        for source, src in self.catalog["sources"].items():
            for t in src.get("topics", []):
                users.setdefault(t["title"], []).append((src["title"], t.get("why", "")))
                used_in.setdefault(t["title"], set()).add(source)
        for title, info in sorted(list(self.catalog["topics"].items())):
            if title not in users:
                if any(n.title.lower() == title.lower() for n in wikipages.all_notes()):
                    print(ui.yellow(f"  ! topic '{title}' is no longer linked from any source note "
                                    "(note left in place; delete it by hand if unwanted)"))
                else:
                    del self.catalog["topics"][title]
                    print(ui.dim(f"  - topic '{title}' removed (no links and no note)"))
                continue
            folder = config.WIKI_FOLDERS[info.get("kind", "concept")]
            # Case-insensitive: macOS and Windows filesystems treat "Server-side" and
            # "Server-Side" as the same file, so an exact match would miss the note.
            note = next((n for n in wikipages.all_notes() if n.title.lower() == title.lower()), None)
            appears = self._appears_section(users[title])
            regenerate = self.force and title in self.touched and not note.meta.get("reviewed") \
                if note else True
            if regenerate:
                body, meta, entry = self._new_topic(title, info, appears, used_in[title])
                path = note.path if note else config.WIKI / folder / f"{title}.md"
                self._write(path, meta, body)
                report.append(entry)
            else:
                body = self._replace_section(note.body, "Appears in", appears)
                self._write(note.path, note.meta, body)

    def _appears_section(self, users: list[tuple[str, str]]) -> str:
        lines = ["## Appears in", ""]
        for note_title, why in sorted(users):
            lines.append(f"- {wikipages.link(note_title)}" + (f" — {why}" if why else ""))
        return "\n".join(lines)

    def _new_topic(self, title: str, info: dict, appears: str,
                   sources: set[str]) -> tuple[str, dict, dict]:
        # Only search the sources whose notes link to this topic: the summary should
        # describe how *these* sources use it, not whatever else scores well.
        k, cap = (3, 3) if len(sources) == 1 else (min(4, 2 * len(sources)), 2)
        hits = self._index().search(title, k=k, paths=sources, max_per_source=cap)
        raw, stats = ("", None)
        sentences = []
        if hits:
            raw, stats = self.gemma.generate(prompts.concept_messages(title, hits), 200,
                                             config.INGEST_TEMPERATURE)
            by_label = {h.label: h for h in hits}
            # A claim ends where its citation labels end; text with no label is dropped.
            for m in CITED_CLAIM.finditer(normalize_labels(raw.strip())):
                text = (m.group(1).strip() + m.group(3)).strip()
                labels = re.findall(r"S\d+", m.group(2))
                valid = [by_label[l] for l in dict.fromkeys(labels) if l in by_label]
                if not text or not valid:
                    continue
                cites = ", ".join(wikipages.passage_link(h.passage) for h in valid)
                sentences.append(f"{text.rstrip('.')}. ({cites})")
                if len(sentences) == 3:
                    break
        summary = " ".join(sentences) or "_No grounded summary yet: the sources mention this only in passing._"
        body = "\n".join([f"# {title}", "", summary, "", appears])
        desc = sentences[0].split(" ([[")[0].strip() if sentences else title
        meta = {"type": info.get("kind", "concept"), "aliases": info.get("aliases", []),
                "description": (desc[:140].rsplit(" ", 1)[0] + "…") if len(desc) > 140 else desc,
                "generated_by": self.model_tag, "ingested_at": self.now, "reviewed": False}
        entry = {"topic": title, "status": "written", "raw_output": raw,
                 "cited_passages": [h.passage.id for h in hits],
                 "stats": stats.to_dict() if stats else None}
        return body, meta, entry

    # --- navigation pages ------------------------------------------------------------------
    def write_index(self) -> None:
        notes = wikipages.all_notes()
        lines = [f"# {config.WIKI_TITLE}", "", config.WIKI_INTRO, ""]
        for heading, kind, blurb in config.WIKI_GROUPS:
            members = sorted((n for n in notes if n.meta.get("type") == kind), key=lambda n: n.title.lower())
            if not members:
                continue
            lines += [f"## {heading}", "", f"*{blurb}*", ""]
            for n in members:
                desc = str(n.meta.get("description", "")).strip()
                lines.append(f"- {wikipages.link(n.title)}" + (f" — {desc}" if desc else ""))
            lines.append("")
        lines += ["## Sources", "",
                  "- [[Source Catalog]] — every original file in `raw/`, its conversion, its hash, and the note made from it",
                  ""]
        config.INDEX_MD.write_text("\n".join(lines), encoding="utf-8")

    def write_catalog_page(self) -> None:
        rows = ["# Source Catalog", "",
                "Original files live unchanged in `raw/`. Plain-text originals are converted to "
                "Markdown next to them (`wiki convert`: encoding, line endings and bullets only; "
                "every word is checked to be unchanged). Each source is ingested into exactly one "
                "article note; the note's frontmatter `source:` field is the machine key that "
                "re-ingestion uses, so renaming a note never creates a duplicate.", "",
                "| Original file (unchanged) | SHA-256 of original | Text the harness reads | Wiki note | Ingested | Reviewed |",
                "|---|---|---|---|---|---|"]
        for source, e in sorted(self.catalog["sources"].items()):
            note = wikipages.find_by_source(source)
            reviewed = "yes" if note and note.meta.get("reviewed") else "no"
            title = note.title if note else e["title"]
            # Inside a Markdown table the link's "|" must be escaped or it splits the cell.
            src_link = wikipages.source_link(source, label=source).replace("|", "\\|")
            orig = (note.meta.get("original") if note else None) or source
            orig_sha = (note.meta.get("original_sha256") if note else None) or e["sha256"]
            rows.append(f"| `{orig}` | `{orig_sha[:12]}` | {src_link} | {wikipages.link(title)} | "
                        f"{e['ingested_at'][:16].replace('T', ' ')} | {reviewed} |")
        config.CATALOG_MD.write_text("\n".join(rows) + "\n", encoding="utf-8")

    def sync_reviewed(self) -> None:
        """Pick up review edits (links added or removed in Obsidian) without calling Gemma."""
        for note in wikipages.all_notes():
            source = note.meta.get("source")
            if note.meta.get("type") != config.SOURCE_KIND or not note.meta.get("reviewed") or not source:
                continue
            topics = reviewed_topics(note)
            entry = self.catalog["sources"].setdefault(source, {
                "note": str(note.path.relative_to(config.VAULT)), "title": note.title,
                "sha256": note.meta.get("source_sha256", ""), "ingested_at": self.now,
                "model": self.model_tag})
            entry.update({"topics": topics, "reviewed": True, "title": note.title,
                          "note": str(note.path.relative_to(config.VAULT))})
            for t in topics:
                # A reviewer's choice of concept vs organization wins over Gemma's.
                self.catalog["topics"].setdefault(t["title"], {"aliases": []})["kind"] = t["kind"]

    # --- run --------------------------------------------------------------------------------
    def run(self, targets: list[Path]) -> dict:
        files = [f for t in targets for f in list_text_files(t)]
        files = [f for f in files if config.RAW.resolve() in f.resolve().parents]
        if not files:
            raise FileNotFoundError("No .md/.txt sources found under vault/raw/ in "
                                    + ", ".join(str(t) for t in targets))
        t0 = time.perf_counter()
        self.sync_reviewed()
        results, topic_report = [], []
        for f in files:
            print(ui.dim(f"  · {vault_relative(f)} ..."), end="", flush=True)
            r = self.ingest_file(f)
            results.append(r)
            extra = (f" · kept {len(r.kept_facts)} facts, dropped {len(r.dropped)}"
                     if r.status != "unchanged" else "")
            secs = f" · {r.stats.get('seconds', 0):.1f}s" if r.stats else ""
            print(f"\r  {ui.green('✓') if r.status != 'unchanged' else ui.dim('=')} "
                  f"{vault_relative(f)} → {r.note} [{r.status}]{extra}{secs}")
        self.update_topics(topic_report)
        for t in topic_report:
            print(f"  {ui.green('+')} topic note: {t['topic']}")
        self.write_index()
        self.write_catalog_page()
        self._save_catalog()
        index = Index.build()
        elapsed = time.perf_counter() - t0
        return {"results": results, "topics": topic_report, "seconds": elapsed,
                "passages": len(index.passages)}
