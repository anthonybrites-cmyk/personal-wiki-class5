# Ask: What discount rate must companies use when testing goodwill for impairment?

- **Mode:** ask (standalone, no chat history) · **Execution:** local
- **Model:** `mlx-community/gemma-4-e2b-it-4bit` @ `2387675` (4-bit affine, group size 64 (MLX); mlx 0.32.2 + mlx-vlm 0.7.2)
- **Network at run time:** online (network reachable; harness still pinned to local files)
- **Retrieval:** hybrid BM25 + bge-small-en-v1.5, top 6

## Retrieved passages

### [S1] `raw/Wikipedia - Goodwill (accounting).md` § Goodwill (accounting) (lines 14–14)
<sub>rrf 0.0328 · bm25 7.27 · cosine 0.703</sub>

```text
Under U.S. GAAP and IFRS, goodwill is never amortized for public companies, because it is considered to have an indefinite useful life. On the other hand, private companies in the United States may elect to amortize goodwill over a period of ten years or less under an accounting alternative from the Private Company Council of the FASB. Instead, management is responsible for valuing goodwill every year and determining if an impairment is required. If the fair market value falls below the historical cost (the amount for which goodwill was purchased), an impairment must be recorded to adjust it down to fair market value. However, an increase in fair market value would not be recognized in this way, and may instead be attributed to other assets.
```

### [S2] `raw/Wikipedia - Goodwill (accounting).md` § Amortization and adjustments to carrying value (lines 66–66)
<sub>rrf 0.0318 · bm25 3.66 · cosine 0.702</sub>

```text
Instead of deducting the value of goodwill annually over a period of a maximum of 40 years, companies are now required to determine the fair value of the reporting units, using the present value of future cash flow, and compare it to their carrying value (book value of assets plus goodwill minus liabilities) If the fair value is less than carrying value (impaired), the goodwill value needs to be reduced. Hence, the carrying value equals the fair value. The impairment loss is reported as a separate line item on the income statement, and the new adjusted value of goodwill is reported in the balance sheet.
```

### [S3] `raw/Wikipedia - Goodwill (accounting).md` § Amortization and adjustments to carrying value (lines 64–64)
<sub>rrf 0.0317 · bm25 3.87 · cosine 0.673</sub>

```text
Goodwill is no longer amortized under U.S. GAAP (FAS 142). FAS 142 was issued in June 2001. Companies objected to the removal of the option to use pooling-of-interests, so the Financial Accounting Standards Board removed amortization as a concession. As of 2005-01-01, it is also forbidden under International Financial Reporting Standards. Goodwill can now only be impaired under these GAAP standards.
```

### [S4] `raw/Wikipedia - FIFO and LIFO accounting.md` § LIFO (lines 34–36)
<sub>rrf 0.0282 · bm25 3.29 · cosine 0.542</sub>

```text
"LIFO" stands for last-in, first-out, meaning that the most recently purchased items are recorded as sold first. From the 1970s, some U.S. companies shifted towards the use of LIFO, which reduces their income taxes in times of inflation, but since International Financial Reporting Standards (IFRS) banned LIFO, more companies returned to FIFO. One third of American companies are thought to use LIFO, according to the "Save LIFO Coalition", which argues in favor of the retention of the LIFO method.

LIFO is used only in the United States, which is governed by the generally accepted accounting principles (GAAP). Section 472 of the Internal Revenue Code directs how LIFO may be used if necessary. The code directs that LIFO may be used "only if the taxpayer establishes" that they have no other way of valuing their inventory.
```

### [S5] `raw/Wikipedia - FIFO and LIFO accounting.md` § LIFO (lines 46–46)
<sub>rrf 0.0279 · bm25 7.11 · cosine 0.499</sub>

```text
In the United States, publicly traded entities which use LIFO for taxation purposes must also use LIFO for financial reporting purposes, but such companies are also likely to report a LIFO reserve to their shareholders. A number of tax reform proposals have argued for the repeal of LIFO tax provision.
```

### [S6] `raw/Wikipedia - FIFO and LIFO accounting.md` § FIFO (lines 16–18)
<sub>rrf 0.0275 · bm25 2.46 · cosine 0.516</sub>

```text
"FIFO" stands for first-in, first-out, meaning that the oldest inventory items are recorded as sold first (but this does not necessarily mean that the exact oldest physical object has been tracked and sold). In other words, the cost associated with the inventory that was purchased first is the cost expensed first.

A company might use the LIFO method for accounting purposes, even if it uses FIFO for inventory management purposes (i.e., for the actual storage, shelving, and sale of its merchandise). For example, a company that sells many perishable goods, such as a supermarket chain, is likely to follow the FIFO method when managing inventory, to ensure that goods with earlier expiration dates are sold before goods with later expiration dates. However, this does not preclude that same company from accounting for its merchandise with the LIFO method.
```

## Gemma's answer (verbatim)

```text
EVIDENCE:
- [S1] "management is responsible for valuing goodwill every year and determining if an impairment is required."
- [S2] "determine the fair value of the reporting units, using the present value of future cash flow, and compare it to their carrying value (book value of assets plus goodwill minus liabilities)"
ANSWER: Companies determine the fair value of reporting units using the present value of future cash flow to compare it to their carrying value [S2].
```

## Citation check (automatic)

- **Status:** ok
- **Labels cited in answer:** S2
- [S1] “management is responsible for valuing goodwill every year and determining if an impairment is required.” — found in passage
- [S2] “determine the fair value of the reporting units, using the present value of future cash flow, and compare it to their carrying value (book value of assets plus goodwill minus liabilities)” — found in passage
- claim “Companies determine the fair value of reporting units using the present value of future cash flow to compare it to their carrying value.” — supported by S2 (S2: 100% word overlap)

## Timing and memory

- 1280 prompt tok · 99 new tok · 54 tok/s · 3.1s · peak 4.33 GB
- retrieval 1.215s · model load 3.15s · total 7.52s
