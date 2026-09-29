# Test 3: connects two sources

> **What does goodwill represent in an acquisition, and which kind of contingent value right protects the buyer against overpaying?**

| | |
|---|---|
| Mode | `wiki ask` (standalone: no chat history, no persona) |
| Execution | **local** · network at run time: **offline (no DNS)** |
| Model | `mlx-community/gemma-4-e2b-it-4bit` @ `2387675` — 4-bit affine, group size 64 (MLX) |
| Runtime | mlx 0.32.2 + mlx-vlm 0.7.2 |
| Retrieval | hybrid BM25 + bge-small-en-v1.5 (RRF), top 6 |
| Run | 2026-09-28T22:40:56 · record [`20260928-224056-what-does-goodwill-represent-in-an-acquisition-a.json`](../offline/runs/ask/20260928-224056-what-does-goodwill-represent-in-an-acquisition-a.json) |
| Measured | 8.32 s wall for the whole command (includes model load) · max RSS 2.55 GB · peak memory footprint 4.88 GB |
| Generation | 1263 prompt tokens → 138 new tokens in 3.402 s (62 tok/s) · MLX peak 4.317 GB |

## Expected (written before the run: [tests/ask-tests.md](../../tests/ask-tests.md))

- **Sources:** `raw/Wikipedia - Goodwill (accounting).md`, `raw/Wikipedia - Contingent value rights.md`
- **Passages containing:** “It reflects the premium the buyer pays over the net value of its other assets”; “is deducted from the purchase price”; “protecting the acquirer against the valuation risk inherent in overpaying”
- **Answer:** Goodwill: the premium paid over the net (fair) value of the target's identifiable assets and liabilities; event-driven CVRs protect the acquirer against overpaying

## Retrieval check

- Expected passages retrieved: **S1 (lines 12–12), S2 (lines 16–20)**
- Expected sources present: 2 of 2 (raw/Wikipedia - Contingent value rights.md, raw/Wikipedia - Goodwill (accounting).md)

## Gemma's answer (verbatim)

```text
EVIDENCE:
- [S1] "Goodwill is often understood to represent the firm's intrinsic ability to acquire and retain customer business, where that is not attributed more specifically to a brand name, contractual arrangements, or otherwise."
- [S2] "Event-driven CVRs compensate the owners for yet to eventuate positive developments in their business - hence protecting the acquirer against the valuation risk inherent in overpaying."
ANSWER: Goodwill represents the firm's intrinsic ability to acquire and retain customer business [S1]. Event-driven Contingent Value Rights (CVRs) protect the acquirer against the valuation risk inherent in overpaying [S2].
```

## Citation check (automatic, by the harness)

- **Status:** `ok`
- quote [S1] “Goodwill is often understood to represent the firm's intrinsic ability to acquire and retain customer business, where that is not attributed more specifically to a brand name, contractual arrangements, or otherwise.” — found in that passage
- quote [S2] “Event-driven CVRs compensate the owners for yet to eventuate positive developments in their business - hence protecting the acquirer against the valuation risk inherent in overpaying.” — found in that passage
- claim “Goodwill represents the firm's intrinsic ability to acquire and retain customer business.” — supported by S1 (S1: 100% word overlap)
- claim “Event-driven Contingent Value Rights (CVRs) protect the acquirer against the valuation risk inherent in overpaying.” — supported by S2 (S2: 85% word overlap)

## Retrieved passages (original text, as given to Gemma)

#### [S1] `raw/Wikipedia - Goodwill (accounting).md` § Goodwill (accounting) (lines 12–12) ← expected evidence
<sub>rank 1 · rrf 0.03226 · bm25 7.67 · cosine 0.7315</sub>

```text
In accounting, goodwill is an intangible asset recognized when a firm is purchased as a going concern. It reflects the premium the buyer pays over the net value of its other assets. Goodwill is often understood to represent the firm's intrinsic ability to acquire and retain customer business, where that is not attributed more specifically to a brand name, contractual arrangements, or otherwise. It is recognized only through an acquisition; it cannot be self-created. It is classified as an intangible asset on the balance sheet because it cannot be seen or touched.
```

#### [S2] `raw/Wikipedia - Contingent value rights.md` § Forms (lines 16–20) ← expected evidence
<sub>rank 2 · rrf 0.03202 · bm25 13.435 · cosine 0.7225</sub>

```text
These rights typically take either of two forms:  (1) Event-driven CVRs compensate the owners for yet to eventuate positive developments in their business - hence protecting the acquirer against the valuation risk inherent in overpaying.  (2) Price-protection CVRs are granted when payment is share based - protecting the acquired company, by providing  a hedge against downside price risk in the acquirer's equity.

In the first case, CVRs are granted

in scenarios in which the acquiring company does not wish to pay for a product that might not work, has a limited market, or might need significant investment;
```

#### [S3] `raw/Wikipedia - Goodwill (accounting).md` § Modern meaning (lines 46–48)
<sub>rank 3 · rrf 0.0311 · bm25 4.733 · cosine 0.7524</sub>

```text
Goodwill is a special type of intangible asset that represents the portion of a business's value not attributable to other income-producing assets, tangible or intangible.

For example, a privately held software company may have net assets (consisting primarily of miscellaneous equipment and/or property, and assuming no debt) valued at $1 million. Still, the company's overall value (including customers and intellectual capital) is valued at $10 million. Anybody buying that company would book $10 million in total assets acquired, comprising $1 million in physical assets and $9 million in other intangible assets. And any consideration paid in excess of $10 million shall be considered as goodwill. In a private company, goodwill has no predetermined value before the acquisition; its magnitude depends on the other two variables by definition. A publicly traded company, by contrast, is subject to a constant process of market valuation, so goodwill will always be apparent.
```

#### [S4] `raw/Wikipedia - Contingent value rights.md` § Forms (lines 22–24)
<sub>rank 4 · rrf 0.03031 · bm25 5.656 · cosine 0.6987</sub>

```text
whereas on the other side, the acquired company “wants to get full value for its assets”.  The CVR then “helps bridge this negotiation”.  Under these rights, shareholders will receive additional cash, securities, or benefits if a specific and named event occurs - one where the value of the firm significantly increases - within a specified timeframe.  CVRs are common in the biotech and pharmaceutical industries (see Valuation (finance) § Valuation of intangible assets); they are also often granted to shareholders in companies facing significant,  value accretive restructuring.  For an example see Media General / Nexstar Media Group.

In the second case, protection against price risk is facilitated by specifying that payment will be made at an averaged, as opposed to final, share price; a floor may also be set.
```

#### [S5] `raw/Wikipedia - Contingent value rights.md` § Contingent value rights (lines 12–12)
<sub>rank 5 · rrf 0.03016 · bm25 5.821 · cosine 0.69</sub>

```text
In corporate finance, Contingent Value Rights (CVR) are rights granted by an acquirer to a company’s shareholders, facilitating the transaction where some uncertainty is inherent.  CVRs may be separately tradeable securities; they are occasionally acquired (or shorted) by specialized hedge funds.
```

#### [S6] `raw/Wikipedia - Goodwill (accounting).md` § Controversy (lines 70–72)
<sub>rank 6 · rrf 0.03016 · bm25 3.468 · cosine 0.7281</sub>

```text
When the business is threatened with insolvency, investors will deduct the goodwill from any calculation of residual equity because it has no resale value.

The accounting treatment for goodwill remains controversial within both the accounting and financial industries because it is fundamentally a workaround employed by accountants to compensate for the fact that businesses, when purchased, are valued based on estimates of future cash flows and prices negotiated by the buyer and seller, and not on the fair value of assets and liabilities to be transferred by the seller. This creates a mismatch between the reported assets and net incomes of companies that have grown without purchasing other companies and those that have.
```

## Assessment

**Pass, with a different emphasis than expected.** The question connects two sources.

- **Retrieval:** both expected passages came back: the goodwill lead (S1) and the CVR
  "Forms" section (S2).
- **CVR half:** exactly as expected. "Event-driven Contingent Value Rights … protect the
  acquirer against the valuation risk inherent in overpaying [S2]".
- **Goodwill half:** Gemma answered with the article's sentence "Goodwill is often
  understood to represent the firm's intrinsic ability to acquire and retain customer
  business". That is a true quote from S1, and it uses the question's own word
  ("represent"). I had expected the accounting definition from the same passage, "the
  premium the buyer pays over the net value of its other assets". Both are in S1, and
  both are correct readings of the source. The answer just leaves out the more precise
  one.
