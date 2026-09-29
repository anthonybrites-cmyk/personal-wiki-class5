# Wiki review log

Gemma 4 E2B drafted every note in `vault/wiki/`. I checked each note against the source
article and corrected it **in the wiki**. The source texts were never edited. Their
SHA-256 hashes, recorded when they were downloaded, still match
([`tests/original-txt-sha256.txt`](../tests/original-txt-sha256.txt)). Commit `878f39c`
("First ingest: Gemma drafts of the wiki notes (unreviewed)") holds exactly what Gemma
wrote before any of the changes below. Gemma's raw ingest output is in
[`ingest-history/v1-report.md`](ingest-history/v1-report.md).

Every fact and topic-note sentence I wrote or reworded goes through the harness's own
source check before it is saved: its numbers must appear in the cited passage, and at
least half its words. The review script refused two of my own sentences because each
combined facts from two different passages (FIFO + LIFO totals; FAS 141 + FAS 142). I
split them.

## Article notes

| Note | Problem in Gemma's draft | Fix |
|---|---|---|
| Goodwill Accounting | **Misleading:** "*Companies* may elect to amortize goodwill over ten years or less". The source says only **private companies in the United States** may. **Framing:** "the conclusion is that goodwill is subject to impairment testing". The article states no conclusion. | Rewritten with the private-company qualifier. Added "cannot be self-created", the $20 − $9 = $11 example, and FAS 141. The summary is now descriptive. |
| FIFO and LIFO Accounting | **Framing:** "the conclusion notes …" again. **Missing:** IFRS's ban and the rising-price effect on COGS, profit, and tax, which are the article's key points. | Summary rewritten. Added the IFRS ban, the US-only/GAAP fact, and the rising-price comparison. The Foo Co. figures were correct and kept. |
| Contingent Value Rights | **Out of context:** "The CVR then helps bridge this negotiation." **Missing:** *whom* each CVR type protects (event-driven → acquirer against overpaying; price-protection → target's shareholders), which is the article's core distinction. | Rewritten with both forms, the payout condition, and the call-option / Asian-option valuation. |

## Topics

Gemma proposed 15 topics. **Removed as noise:**

- **Categories, not organizations:** "hedge funds", "biotech and pharmaceutical industries".
- **A one-off example:** "Media General Nexstar Media Group".
- **Lowercase generics:** "option", "call option", now covered by *Option Pricing*.
- **A law filed as an organization:** "Internal Revenue Code".
- **A duplicate:** "Private Company Council of the FASB", folded into *FASB*.

"International Financial Reporting Standards" was filed as an **organization**. It is a
set of standards, so I moved it to Concepts. This exposed a harness bug: the old catalog
entry's type overrode my review. Fixed in `harness/ingest.py`; a reviewer's choice now
wins.

**Added in review:**

- *US GAAP* and *IFRS*: both articles' rules differ under each.
- *Business Valuation*: why price ≠ asset value (goodwill), and how CVRs are priced.
- *Option Pricing*.
- Direct links between the Goodwill and CVR notes.

| Topic note | Problem in Gemma's draft | Fix |
|---|---|---|
| Business Valuation | **Filler:** "a topic covered in the notes, which includes concepts such as goodwill …, contingent value rights …". It cited the *See also* lists. | Four cited sentences: price vs asset value, the $1M vs $10M example, why CVRs bridge the valuation gap, and how analysts price them. |
| Intangible Asset | **Tautology:** "Intangible assets are assets that are not tangible." | Replaced with the article's own reason (cannot be seen or touched), and the biotech/pharma link to CVRs. |
| Cost of Goods Sold | Mixed in the FIFO *balance-sheet inventory* value, which isn't COGS. | FIFO vs LIFO cost of sales, and the rising-price effect. |
| US GAAP | **Uncited generic opener:** "US GAAP is a set of accounting principles that governs certain practices." | Four cited facts across both articles. |
| FASB | **Stated beyond the source:** "the body that issues accounting standards". It also placed the article's criticism that goodwill rules are "highly subjective" in the FASB note. The article says that of rules from "the Accounting Standards Board" and never names FASB there. | Two cited facts: FASB removed amortization as a concession; the Private Company Council alternative. |
| Acquisition Premium, IFRS, Save LIFO Coalition | Accurate but thin or awkward. | Tightened, each sentence cited. |
| Impairment Testing, LIFO Reserve, Option Pricing | Accurate. | Kept Gemma's text. Wrote index descriptions. |

## A naming collision (found by the link checker)

I first saved the downloaded articles under their Wikipedia titles. Two of them ("Contingent
value rights", "FIFO and LIFO accounting") then had the same name as their wiki notes apart
from capitalization. Obsidian treats those as the same name, so 13 links were ambiguous. I
renamed the source files `Wikipedia - <title>.txt`: same bytes and same hashes. I also
pointed the reviewed notes' `source:` at the new paths, so re-ingestion found them in place
instead of drafting duplicates.

## What the errors had in common

As with the two earlier source sets I tried for this project, Gemma never invented a number.
Its errors were:

- **Dropped qualifiers:** "companies" instead of "private companies in the United States".
- **Framing a study text as having a "conclusion".**
- **Putting a statement under the wrong actor:** the "subjective rules" criticism in the FASB note.
- **Filler written from a "See also" list.**

The numeric and word-overlap checks pass all of these. Reading the cited passage catches
them.

## Re-ingest check

[`reingest-check.md`](reingest-check.md): `wiki ingest vault/raw --force` re-ran Gemma on
all three sources after the review. 17 → 17 notes, no duplicates, reviewed text kept.
