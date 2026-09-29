# Ask: Is LIFO allowed under IFRS?

- **Mode:** ask (standalone, no chat history) · **Execution:** local
- **Model:** `mlx-community/gemma-4-e2b-it-4bit` @ `2387675` (4-bit affine, group size 64 (MLX); mlx 0.32.2 + mlx-vlm 0.7.2)
- **Network at run time:** online (network reachable; harness still pinned to local files)
- **Retrieval:** hybrid BM25 + bge-small-en-v1.5, top 6

## Retrieved passages

### [S1] `raw/Wikipedia - FIFO and LIFO accounting.md` § LIFO (lines 34–36)
<sub>rrf 0.0328 · bm25 3.52 · cosine 0.726</sub>

```text
"LIFO" stands for last-in, first-out, meaning that the most recently purchased items are recorded as sold first. From the 1970s, some U.S. companies shifted towards the use of LIFO, which reduces their income taxes in times of inflation, but since International Financial Reporting Standards (IFRS) banned LIFO, more companies returned to FIFO. One third of American companies are thought to use LIFO, according to the "Save LIFO Coalition", which argues in favor of the retention of the LIFO method.

LIFO is used only in the United States, which is governed by the generally accepted accounting principles (GAAP). Section 472 of the Internal Revenue Code directs how LIFO may be used if necessary. The code directs that LIFO may be used "only if the taxpayer establishes" that they have no other way of valuing their inventory.
```

### [S2] `raw/Wikipedia - FIFO and LIFO accounting.md` § LIFO (lines 46–46)
<sub>rrf 0.0320 · bm25 2.15 · cosine 0.679</sub>

```text
In the United States, publicly traded entities which use LIFO for taxation purposes must also use LIFO for financial reporting purposes, but such companies are also likely to report a LIFO reserve to their shareholders. A number of tax reform proposals have argued for the repeal of LIFO tax provision.
```

### [S3] `raw/Wikipedia - FIFO and LIFO accounting.md` § FIFO and LIFO accounting (lines 12–12)
<sub>rrf 0.0310 · bm25 1.79 · cosine 0.654</sub>

```text
FIFO and LIFO accounting are methods used in managing inventory and financial matters involving the amount of money a company has to have tied up within inventory of produced goods, raw materials, parts, components, or feedstocks. They are used to manage assumptions of costs related to inventory, stock repurchases (if purchased at different prices), and various other accounting purposes.
```

### [S4] `raw/Wikipedia - Goodwill (accounting).md` § Goodwill (accounting) (lines 14–14)
<sub>rrf 0.0290 · bm25 1.46 · cosine 0.546</sub>

```text
Under U.S. GAAP and IFRS, goodwill is never amortized for public companies, because it is considered to have an indefinite useful life. On the other hand, private companies in the United States may elect to amortize goodwill over a period of ten years or less under an accounting alternative from the Private Company Council of the FASB. Instead, management is responsible for valuing goodwill every year and determining if an impairment is required. If the fair market value falls below the historical cost (the amount for which goodwill was purchased), an impairment must be recorded to adjust it down to fair market value. However, an increase in fair market value would not be recognized in this way, and may instead be attributed to other assets.
```

### [S5] `raw/Wikipedia - Goodwill (accounting).md` § History and purchase vs. pooling-of-interests (lines 60–60)
<sub>rrf 0.0289 · bm25 2.62 · cosine 0.488</sub>

```text
Previously, companies could structure many acquisition transactions to choose between two accounting methods for recording a business combination: purchase accounting or pooling-of-interests accounting. The pooling-of-interests method combined the book values of the assets and liabilities of the two companies to create the new combined balance sheet. It therefore did not distinguish between who is buying whom. It also did not record the price the acquiring company paid for the acquisition. Since 2001, U.S. Generally Accepted Accounting Principles (FAS 141) no longer allows the pooling-of-interests method.
```

### [S6] `raw/Wikipedia - Goodwill (accounting).md` § Amortization and adjustments to carrying value (lines 64–64)
<sub>rrf 0.0143 · bm25 0.00 · cosine 0.543</sub>

```text
Goodwill is no longer amortized under U.S. GAAP (FAS 142). FAS 142 was issued in June 2001. Companies objected to the removal of the option to use pooling-of-interests, so the Financial Accounting Standards Board removed amortization as a concession. As of 2005-01-01, it is also forbidden under International Financial Reporting Standards. Goodwill can now only be impaired under these GAAP standards.
```

## Gemma's answer (verbatim)

```text
EVIDENCE:
- [S1] "From the 1970s, some U.S. companies shifted towards the use of LIFO, which reduces their income taxes in times of inflation, but since International Financial Reporting Standards (IFRS) banned LIFO, more companies returned to FIFO."
ANSWER: LIFO is banned under International Financial Reporting Standards (IFRS) [S1].
```

## Citation check (automatic)

- **Status:** ok
- **Labels cited in answer:** S1
- [S1] “From the 1970s, some U.S. companies shifted towards the use of LIFO, which reduces their income taxes in times of inflation, but since International Financial Reporting Standards (IFRS) banned LIFO, more companies returned to FIFO.” — found in passage
- claim “LIFO is banned under International Financial Reporting Standards (IFRS).” — supported by S1 (S1: 100% word overlap)

## Timing and memory

- 1183 prompt tok · 84 new tok · 65 tok/s · 2.5s · peak 4.27 GB
- retrieval 1.22s · model load 3.55s · total 7.3s
