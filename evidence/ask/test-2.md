# Test 2: reworded, one source

> **Can a company count the customer loyalty it built up by itself as something it owns on its books?**

| | |
|---|---|
| Mode | `wiki ask` (standalone: no chat history, no persona) |
| Execution | **local** · network at run time: **offline (no DNS)** |
| Model | `mlx-community/gemma-4-e2b-it-4bit` @ `2387675` — 4-bit affine, group size 64 (MLX) |
| Runtime | mlx 0.32.2 + mlx-vlm 0.7.2 |
| Retrieval | hybrid BM25 + bge-small-en-v1.5 (RRF), top 6 |
| Run | 2026-09-28T22:40:48 · record [`20260928-224048-can-a-company-count-the-customer-loyalty-it-buil.json`](../offline/runs/ask/20260928-224048-can-a-company-count-the-customer-loyalty-it-buil.json) |
| Measured | 7.03 s wall for the whole command (includes model load) · max RSS 3.01 GB · peak memory footprint 4.91 GB |
| Generation | 1431 prompt tokens → 65 new tokens in 2.239 s (64 tok/s) · MLX peak 4.394 GB |

## Expected (written before the run: [tests/ask-tests.md](../../tests/ask-tests.md))

- **Sources:** `raw/Wikipedia - Goodwill (accounting).md`
- **Passages containing:** “it cannot be self-created”; “such expenses cannot be capitalized and added to goodwill”
- **Answer:** No: goodwill is recognized only through an acquisition and cannot be self-created; reputation-building spending cannot be capitalized as goodwill

## Retrieval check

- Expected passages retrieved: **S3 (lines 12–12)**
- Expected sources present: 1 of 1 (raw/Wikipedia - Goodwill (accounting).md)

## Gemma's answer (verbatim)

```text
EVIDENCE:
- [S3] "Goodwill is often understood to represent the firm's intrinsic ability to acquire and retain customer business, where that is not attributed more specifically to a brand name, contractual arrangements, or otherwise."
ANSWER: No, goodwill is recognized only through an acquisition [S3].
```

## Citation check (automatic, by the harness)

- **Status:** `ok`
- quote [S3] “Goodwill is often understood to represent the firm's intrinsic ability to acquire and retain customer business, where that is not attributed more specifically to a brand name, contractual arrangements, or otherwise.” — found in that passage
- claim “No, goodwill is recognized only through an acquisition.” — supported by S3 (S3: 100% word overlap)

## Retrieved passages (original text, as given to Gemma)

#### [S1] `raw/Wikipedia - Goodwill (accounting).md` § History and purchase vs. pooling-of-interests (lines 60–60)
<sub>rank 1 · rrf 0.03252 · bm25 3.275 · cosine 0.5641</sub>

```text
Previously, companies could structure many acquisition transactions to choose between two accounting methods for recording a business combination: purchase accounting or pooling-of-interests accounting. The pooling-of-interests method combined the book values of the assets and liabilities of the two companies to create the new combined balance sheet. It therefore did not distinguish between who is buying whom. It also did not record the price the acquiring company paid for the acquisition. Since 2001, U.S. Generally Accepted Accounting Principles (FAS 141) no longer allows the pooling-of-interests method.
```

#### [S2] `raw/Wikipedia - Goodwill (accounting).md` § Calculating goodwill (lines 22–42)
<sub>rank 2 · rrf 0.0315 · bm25 3.124 · cosine 0.5482</sub>

```text
To calculate goodwill, the fair market value of the acquired company's identifiable assets and liabilities is deducted from the purchase price. For instance, if company A acquired 100% of company B but paid more than company B's net market value, goodwill arises. To calculate goodwill, it is necessary to have a list of all of company B's assets and liabilities at fair market value.

```
                        Fair market value
  Accounts Receivable   $10
  Inventory              $5
  Accounts payable       $6
  -------------------------
  Total Net assets    = $10 + $5 - $6
                      =  $9
```

To acquire company B, company A paid $20. Hence, goodwill would be $11 ($20 − $9). The journal entry in the books of company A to record the acquisition of company B would be:

```
  DR Goodwill             $11
  DR Accounts Receivable  $10
  DR Inventory             $5
  CR Accounts Payable      $6
  CR Cash                 $20
```
```

#### [S3] `raw/Wikipedia - Goodwill (accounting).md` § Goodwill (accounting) (lines 12–12) ← expected evidence
<sub>rank 3 · rrf 0.03126 · bm25 2.688 · cosine 0.5507</sub>

```text
In accounting, goodwill is an intangible asset recognized when a firm is purchased as a going concern. It reflects the premium the buyer pays over the net value of its other assets. Goodwill is often understood to represent the firm's intrinsic ability to acquire and retain customer business, where that is not attributed more specifically to a brand name, contractual arrangements, or otherwise. It is recognized only through an acquisition; it cannot be self-created. It is classified as an intangible asset on the balance sheet because it cannot be seen or touched.
```

#### [S4] `raw/Wikipedia - Contingent value rights.md` § Forms (lines 16–20)
<sub>rank 4 · rrf 0.03021 · bm25 0.753 · cosine 0.5553</sub>

```text
These rights typically take either of two forms:  (1) Event-driven CVRs compensate the owners for yet to eventuate positive developments in their business - hence protecting the acquirer against the valuation risk inherent in overpaying.  (2) Price-protection CVRs are granted when payment is share based - protecting the acquired company, by providing  a hedge against downside price risk in the acquirer's equity.

In the first case, CVRs are granted

in scenarios in which the acquiring company does not wish to pay for a product that might not work, has a limited market, or might need significant investment;
```

#### [S5] `raw/Wikipedia - FIFO and LIFO accounting.md` § LIFO (lines 34–36)
<sub>rank 5 · rrf 0.02899 · bm25 0.829 · cosine 0.5402</sub>

```text
"LIFO" stands for last-in, first-out, meaning that the most recently purchased items are recorded as sold first. From the 1970s, some U.S. companies shifted towards the use of LIFO, which reduces their income taxes in times of inflation, but since International Financial Reporting Standards (IFRS) banned LIFO, more companies returned to FIFO. One third of American companies are thought to use LIFO, according to the "Save LIFO Coalition", which argues in favor of the retention of the LIFO method.

LIFO is used only in the United States, which is governed by the generally accepted accounting principles (GAAP). Section 472 of the Internal Revenue Code directs how LIFO may be used if necessary. The code directs that LIFO may be used "only if the taxpayer establishes" that they have no other way of valuing their inventory.
```

#### [S6] `raw/Wikipedia - Contingent value rights.md` § Forms (lines 22–24)
<sub>rank 6 · rrf 0.02817 · bm25 0.697 · cosine 0.5361</sub>

```text
whereas on the other side, the acquired company “wants to get full value for its assets”.  The CVR then “helps bridge this negotiation”.  Under these rights, shareholders will receive additional cash, securities, or benefits if a specific and named event occurs - one where the value of the firm significantly increases - within a specified timeframe.  CVRs are common in the biotech and pharmaceutical industries (see Valuation (finance) § Valuation of intangible assets); they are also often granted to shareholders in companies facing significant,  value accretive restructuring.  For an example see Media General / Nexstar Media Group.

In the second case, protection against price risk is facilitated by specifying that payment will be made at an averaged, as opposed to final, share price; a floor may also be set.
```

## Assessment

**Pass.** This is the reworded question.

- **Retrieval:** "customer loyalty it built up by itself … on its books" shares almost no
  words with the source. The goodwill article's lead, with "It is recognized only through
  an acquisition; it cannot be self-created", still came back at S3. The second expected
  passage, "such expenses cannot be capitalized and added to goodwill", was not retrieved.
- **Answer:** "No, goodwill is recognized only through an acquisition [S3]" answers the
  yes/no question correctly, with a verified citation. It doesn't add the "cannot be
  self-created" wording, but the meaning is the same.
- **Why this test matters for the checks:** an LLM relevance judge I tried during
  development wrongly *rejected* this correct answer. That's why the harness uses a
  deterministic value-question rule instead ([prompt history](../prompt-history/README.md)).
