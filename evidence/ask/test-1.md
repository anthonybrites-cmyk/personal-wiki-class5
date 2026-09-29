# Test 1: direct, one source

> **In the Foo Co. example, what was the total cost of sales for November under FIFO?**

| | |
|---|---|
| Mode | `wiki ask` (standalone: no chat history, no persona) |
| Execution | **local** · network at run time: **offline (no DNS)** |
| Model | `mlx-community/gemma-4-e2b-it-4bit` @ `2387675` — 4-bit affine, group size 64 (MLX) |
| Runtime | mlx 0.32.2 + mlx-vlm 0.7.2 |
| Retrieval | hybrid BM25 + bge-small-en-v1.5 (RRF), top 6 |
| Run | 2026-09-28T22:40:41 · record [`20260928-224041-in-the-foo-co-example-what-was-the-total-cost-of.json`](../offline/runs/ask/20260928-224041-in-the-foo-co-example-what-was-the-total-cost-of.json) |
| Measured | 6.76 s wall for the whole command (includes model load) · max RSS 2.76 GB · peak memory footprint 4.84 GB |
| Generation | 1621 prompt tokens → 57 new tokens in 2.271 s (66 tok/s) · MLX peak 4.313 GB |

## Expected (written before the run: [tests/ask-tests.md](../../tests/ask-tests.md))

- **Sources:** `raw/Wikipedia - FIFO and LIFO accounting.md`
- **Passages containing:** “Under FIFO, the total cost of sales for November would be $11,050”
- **Answer:** $11,050

## Retrieval check

- Expected passages retrieved: **S1 (lines 20–26)**
- Expected sources present: 1 of 1 (raw/Wikipedia - FIFO and LIFO accounting.md)

## Gemma's answer (verbatim)

```text
EVIDENCE:
- [S1] "Under FIFO, the total cost of sales for November would be $11,050."
ANSWER: Under FIFO, the total cost of sales for November would be $11,050 [S1].
```

## Citation check (automatic, by the harness)

- **Status:** `ok`
- quote [S1] “Under FIFO, the total cost of sales for November would be $11,050.” — found in that passage
- claim “Under FIFO, the total cost of sales for November would be $11,050.” — supported by S1 (S1: 100% word overlap)

## Retrieved passages (original text, as given to Gemma)

#### [S1] `raw/Wikipedia - FIFO and LIFO accounting.md` § FIFO (lines 20–26) ← expected evidence
<sub>rank 1 · rrf 0.03279 · bm25 18.876 · cosine 0.766</sub>

```text
With FIFO, the cost of inventory reported on the balance sheet represents the cost of the inventory purchased earliest. FIFO most closely mimics the flow of inventory, as businesses are far more likely to sell the oldest inventory first.

Consider this example: Foo Co. had the following inventory at hand, in order of acquisition in November:

If Foo Co. sells 210 units during November, the company would expense the cost associated with the first 100 units at $50 and the remaining 110 units at $55. Under FIFO, the total cost of sales for November would be $11,050. The ending inventory would be calculated the following way:

Thus, the balance sheet would now show the inventory valued at $5250.
```

#### [S2] `raw/Wikipedia - FIFO and LIFO accounting.md` § LIFO (lines 38–44)
<sub>rank 2 · rrf 0.03226 · bm25 14.523 · cosine 0.7655</sub>

```text
In the FIFO example above, the company (Foo Co.), using LIFO accounting, would expense the cost associated with the first 75 units at $59, 125 more units at $55, and the remaining 10 units at $50. Under LIFO, the total cost of sales for November would be $11,800. The ending inventory would be calculated the following way:

The balance sheet would show $4500 in inventory under LIFO.

The difference between the cost of an inventory calculated under the FIFO and LIFO methods is called the LIFO reserve (in the example above, it is $750, i.e. $5250 - $4500). This reserve, a form of contra account, is essentially the amount by which an entity's taxable income has been deferred by using the LIFO method.

In most sets of accounting standards, such as the International Financial Reporting Standards, FIFO (or LIFO) valuation principles are "in-fine" subordinated to the higher principle of lower of cost or market valuation.
```

#### [S3] `raw/Wikipedia - FIFO and LIFO accounting.md` § FIFO (lines 16–18)
<sub>rank 3 · rrf 0.03175 · bm25 6.689 · cosine 0.682</sub>

```text
"FIFO" stands for first-in, first-out, meaning that the oldest inventory items are recorded as sold first (but this does not necessarily mean that the exact oldest physical object has been tracked and sold). In other words, the cost associated with the inventory that was purchased first is the cost expensed first.

A company might use the LIFO method for accounting purposes, even if it uses FIFO for inventory management purposes (i.e., for the actual storage, shelving, and sale of its merchandise). For example, a company that sells many perishable goods, such as a supermarket chain, is likely to follow the FIFO method when managing inventory, to ensure that goods with earlier expiration dates are sold before goods with later expiration dates. However, this does not preclude that same company from accounting for its merchandise with the LIFO method.
```

#### [S4] `raw/Wikipedia - Goodwill (accounting).md` § Calculating goodwill (lines 22–42)
<sub>rank 4 · rrf 0.02878 · bm25 1.728 · cosine 0.5193</sub>

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

#### [S5] `raw/Wikipedia - Goodwill (accounting).md` § Modern meaning (lines 46–48)
<sub>rank 5 · rrf 0.02765 · bm25 3.071 · cosine 0.4716</sub>

```text
Goodwill is a special type of intangible asset that represents the portion of a business's value not attributable to other income-producing assets, tangible or intangible.

For example, a privately held software company may have net assets (consisting primarily of miscellaneous equipment and/or property, and assuming no debt) valued at $1 million. Still, the company's overall value (including customers and intellectual capital) is valued at $10 million. Anybody buying that company would book $10 million in total assets acquired, comprising $1 million in physical assets and $9 million in other intangible assets. And any consideration paid in excess of $10 million shall be considered as goodwill. In a private company, goodwill has no predetermined value before the acquisition; its magnitude depends on the other two variables by definition. A publicly traded company, by contrast, is subject to a constant process of market valuation, so goodwill will always be apparent.
```

#### [S6] `raw/Wikipedia - Goodwill (accounting).md` § Goodwill (accounting) (lines 14–14)
<sub>rank 6 · rrf 0.0276 · bm25 1.203 · cosine 0.5146</sub>

```text
Under U.S. GAAP and IFRS, goodwill is never amortized for public companies, because it is considered to have an indefinite useful life. On the other hand, private companies in the United States may elect to amortize goodwill over a period of ten years or less under an accounting alternative from the Private Company Council of the FASB. Instead, management is responsible for valuing goodwill every year and determining if an impairment is required. If the fair market value falls below the historical cost (the amount for which goodwill was purchased), an impairment must be recorded to adjust it down to fair market value. However, an increase in fair market value would not be recognized in this way, and may instead be attributed to other assets.
```

## Assessment

**Pass.**

- **Retrieval:** the expected passage came back at S1: the FIFO section with "Under FIFO,
  the total cost of sales for November would be $11,050". The distractor (the LIFO
  section with $11,800) came back at S2, and Gemma did not mix them up.
- **Answer:** "$11,050 [S1]" is copied from the source and verified by both the quote and
  the claim check.
