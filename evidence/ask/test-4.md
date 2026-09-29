# Test 4: not answerable

> **What discount rate must companies use when testing goodwill for impairment?**

| | |
|---|---|
| Mode | `wiki ask` (standalone: no chat history, no persona) |
| Execution | **local** · network at run time: **offline (no DNS)** |
| Model | `mlx-community/gemma-4-e2b-it-4bit` @ `2387675` — 4-bit affine, group size 64 (MLX) |
| Runtime | mlx 0.32.2 + mlx-vlm 0.7.2 |
| Retrieval | hybrid BM25 + bge-small-en-v1.5 (RRF), top 6 |
| Run | 2026-09-28T22:41:04 · record [`20260928-224104-what-discount-rate-must-companies-use-when-testi.json`](../offline/runs/ask/20260928-224104-what-discount-rate-must-companies-use-when-testi.json) |
| Measured | 7.65 s wall for the whole command (includes model load) · max RSS 2.66 GB · peak memory footprint 4.89 GB |
| Generation | 1280 prompt tokens → 99 new tokens in 2.646 s (66 tok/s) · MLX peak 4.329 GB |

## Expected (written before the run: [tests/ask-tests.md](../../tests/ask-tests.md))

- **Sources:** none — not answerable
- **Passages containing:** —
- **Answer:** insufficient evidence (only 'present value of future cash flow' is mentioned, no rate)

## Retrieval check

- Nothing in the sources answers this; the retrieved passages below are the closest matches the index could find.

## Gemma's answer (verbatim)

```text
EVIDENCE:
- [S1] "management is responsible for valuing goodwill every year and determining if an impairment is required."
- [S2] "determine the fair value of the reporting units, using the present value of future cash flow, and compare it to their carrying value (book value of assets plus goodwill minus liabilities)"
ANSWER: Companies determine the fair value of reporting units using the present value of future cash flow to compare it to their carrying value [S2].
```

## Citation check (automatic, by the harness)

- **Status:** `insufficient`
- quote [S1] “management is responsible for valuing goodwill every year and determining if an impairment is required.” — found in that passage
- quote [S2] “determine the fair value of the reporting units, using the present value of future cash flow, and compare it to their carrying value (book value of assets plus goodwill minus liabilities)” — found in that passage
- ⚠ the question asks for a specific value, but the answer gives none: reporting insufficient evidence (Gemma's reply kept)

## Retrieved passages (original text, as given to Gemma)

#### [S1] `raw/Wikipedia - Goodwill (accounting).md` § Goodwill (accounting) (lines 14–14)
<sub>rank 1 · rrf 0.03279 · bm25 7.267 · cosine 0.7026</sub>

```text
Under U.S. GAAP and IFRS, goodwill is never amortized for public companies, because it is considered to have an indefinite useful life. On the other hand, private companies in the United States may elect to amortize goodwill over a period of ten years or less under an accounting alternative from the Private Company Council of the FASB. Instead, management is responsible for valuing goodwill every year and determining if an impairment is required. If the fair market value falls below the historical cost (the amount for which goodwill was purchased), an impairment must be recorded to adjust it down to fair market value. However, an increase in fair market value would not be recognized in this way, and may instead be attributed to other assets.
```

#### [S2] `raw/Wikipedia - Goodwill (accounting).md` § Amortization and adjustments to carrying value (lines 66–66)
<sub>rank 2 · rrf 0.03175 · bm25 3.655 · cosine 0.7025</sub>

```text
Instead of deducting the value of goodwill annually over a period of a maximum of 40 years, companies are now required to determine the fair value of the reporting units, using the present value of future cash flow, and compare it to their carrying value (book value of assets plus goodwill minus liabilities) If the fair value is less than carrying value (impaired), the goodwill value needs to be reduced. Hence, the carrying value equals the fair value. The impairment loss is reported as a separate line item on the income statement, and the new adjusted value of goodwill is reported in the balance sheet.
```

#### [S3] `raw/Wikipedia - Goodwill (accounting).md` § Amortization and adjustments to carrying value (lines 64–64)
<sub>rank 3 · rrf 0.03175 · bm25 3.865 · cosine 0.6728</sub>

```text
Goodwill is no longer amortized under U.S. GAAP (FAS 142). FAS 142 was issued in June 2001. Companies objected to the removal of the option to use pooling-of-interests, so the Financial Accounting Standards Board removed amortization as a concession. As of 2005-01-01, it is also forbidden under International Financial Reporting Standards. Goodwill can now only be impaired under these GAAP standards.
```

#### [S4] `raw/Wikipedia - FIFO and LIFO accounting.md` § LIFO (lines 34–36)
<sub>rank 4 · rrf 0.02821 · bm25 3.288 · cosine 0.5422</sub>

```text
"LIFO" stands for last-in, first-out, meaning that the most recently purchased items are recorded as sold first. From the 1970s, some U.S. companies shifted towards the use of LIFO, which reduces their income taxes in times of inflation, but since International Financial Reporting Standards (IFRS) banned LIFO, more companies returned to FIFO. One third of American companies are thought to use LIFO, according to the "Save LIFO Coalition", which argues in favor of the retention of the LIFO method.

LIFO is used only in the United States, which is governed by the generally accepted accounting principles (GAAP). Section 472 of the Internal Revenue Code directs how LIFO may be used if necessary. The code directs that LIFO may be used "only if the taxpayer establishes" that they have no other way of valuing their inventory.
```

#### [S5] `raw/Wikipedia - FIFO and LIFO accounting.md` § LIFO (lines 46–46)
<sub>rank 5 · rrf 0.02789 · bm25 7.113 · cosine 0.4987</sub>

```text
In the United States, publicly traded entities which use LIFO for taxation purposes must also use LIFO for financial reporting purposes, but such companies are also likely to report a LIFO reserve to their shareholders. A number of tax reform proposals have argued for the repeal of LIFO tax provision.
```

#### [S6] `raw/Wikipedia - FIFO and LIFO accounting.md` § FIFO (lines 16–18)
<sub>rank 6 · rrf 0.0275 · bm25 2.463 · cosine 0.5164</sub>

```text
"FIFO" stands for first-in, first-out, meaning that the oldest inventory items are recorded as sold first (but this does not necessarily mean that the exact oldest physical object has been tracked and sold). In other words, the cost associated with the inventory that was purchased first is the cost expensed first.

A company might use the LIFO method for accounting purposes, even if it uses FIFO for inventory management purposes (i.e., for the actual storage, shelving, and sale of its merchandise). For example, a company that sells many perishable goods, such as a supermarket chain, is likely to follow the FIFO method when managing inventory, to ensure that goods with earlier expiration dates are sold before goods with later expiration dates. However, this does not preclude that same company from accounting for its merchandise with the LIFO method.
```

## Assessment

**Pass: insufficient evidence reported, by the harness.**

- **The sources:** no source gives a discount rate. The goodwill article only says
  impairment tests use "the present value of future cash flow".
- **Gemma's reply** (kept in the card): "Companies determine the fair value of reporting
  units using the present value of future cash flow … [S2]". That is a true, cited
  sentence that does not answer the question.
- **What caught it:** the harness's value-question rule. A question asking for a specific
  value ("what discount rate") got an answer containing no number, so the harness reports
  **insufficient evidence** and says why. Gemma itself did not refuse; this is the same
  failure seen in the online rehearsal
  ([records](../prompt-history/rehearsal-before-relevance-check/)).
- **Distractors:** none were borrowed ("ten years", "40 years", "2001").
