# Ask: How is a price-protection CVR valued?

- **Mode:** ask (standalone, no chat history) · **Execution:** local
- **Model:** `mlx-community/gemma-4-e2b-it-4bit` @ `2387675` (4-bit affine, group size 64 (MLX); mlx 0.32.2 + mlx-vlm 0.7.2)
- **Network at run time:** online (network reachable; harness still pinned to local files)
- **Retrieval:** hybrid BM25 + bge-small-en-v1.5, top 6

## Retrieved passages

### [S1] `raw/Wikipedia - Contingent value rights.md` § Forms (lines 22–24)
<sub>rrf 0.0325 · bm25 5.88 · cosine 0.744</sub>

```text
whereas on the other side, the acquired company “wants to get full value for its assets”.  The CVR then “helps bridge this negotiation”.  Under these rights, shareholders will receive additional cash, securities, or benefits if a specific and named event occurs - one where the value of the firm significantly increases - within a specified timeframe.  CVRs are common in the biotech and pharmaceutical industries (see Valuation (finance) § Valuation of intangible assets); they are also often granted to shareholders in companies facing significant,  value accretive restructuring.  For an example see Media General / Nexstar Media Group.

In the second case, protection against price risk is facilitated by specifying that payment will be made at an averaged, as opposed to final, share price; a floor may also be set.
```

### [S2] `raw/Wikipedia - Contingent value rights.md` § Forms (lines 16–20)
<sub>rrf 0.0320 · bm25 4.62 · cosine 0.718</sub>

```text
These rights typically take either of two forms:  (1) Event-driven CVRs compensate the owners for yet to eventuate positive developments in their business - hence protecting the acquirer against the valuation risk inherent in overpaying.  (2) Price-protection CVRs are granted when payment is share based - protecting the acquired company, by providing  a hedge against downside price risk in the acquirer's equity.

In the first case, CVRs are granted

in scenarios in which the acquiring company does not wish to pay for a product that might not work, has a limited market, or might need significant investment;
```

### [S3] `raw/Wikipedia - Contingent value rights.md` § Contingent value rights (lines 12–12)
<sub>rrf 0.0315 · bm25 2.46 · cosine 0.756</sub>

```text
In corporate finance, Contingent Value Rights (CVR) are rights granted by an acquirer to a company’s shareholders, facilitating the transaction where some uncertainty is inherent.  CVRs may be separately tradeable securities; they are occasionally acquired (or shorted) by specialized hedge funds.
```

### [S4] `raw/Wikipedia - Goodwill (accounting).md` § History and purchase vs. pooling-of-interests (lines 60–60)
<sub>rrf 0.0299 · bm25 3.33 · cosine 0.533</sub>

```text
Previously, companies could structure many acquisition transactions to choose between two accounting methods for recording a business combination: purchase accounting or pooling-of-interests accounting. The pooling-of-interests method combined the book values of the assets and liabilities of the two companies to create the new combined balance sheet. It therefore did not distinguish between who is buying whom. It also did not record the price the acquiring company paid for the acquisition. Since 2001, U.S. Generally Accepted Accounting Principles (FAS 141) no longer allows the pooling-of-interests method.
```

### [S5] `raw/Wikipedia - Goodwill (accounting).md` § Controversy (lines 70–72)
<sub>rrf 0.0294 · bm25 1.66 · cosine 0.538</sub>

```text
When the business is threatened with insolvency, investors will deduct the goodwill from any calculation of residual equity because it has no resale value.

The accounting treatment for goodwill remains controversial within both the accounting and financial industries because it is fundamentally a workaround employed by accountants to compensate for the fact that businesses, when purchased, are valued based on estimates of future cash flows and prices negotiated by the buyer and seller, and not on the fair value of assets and liabilities to be transferred by the seller. This creates a mismatch between the reported assets and net incomes of companies that have grown without purchasing other companies and those that have.
```

### [S6] `raw/Wikipedia - Goodwill (accounting).md` § Modern meaning (lines 46–48)
<sub>rrf 0.0284 · bm25 2.03 · cosine 0.505</sub>

```text
Goodwill is a special type of intangible asset that represents the portion of a business's value not attributable to other income-producing assets, tangible or intangible.

For example, a privately held software company may have net assets (consisting primarily of miscellaneous equipment and/or property, and assuming no debt) valued at $1 million. Still, the company's overall value (including customers and intellectual capital) is valued at $10 million. Anybody buying that company would book $10 million in total assets acquired, comprising $1 million in physical assets and $9 million in other intangible assets. And any consideration paid in excess of $10 million shall be considered as goodwill. In a private company, goodwill has no predetermined value before the acquisition; its magnitude depends on the other two variables by definition. A publicly traded company, by contrast, is subject to a constant process of market valuation, so goodwill will always be apparent.
```

## Gemma's answer (verbatim)

```text
EVIDENCE:
- [S2] "Price-protection CVRs are granted when payment is share based - protecting the acquired company, by providing a hedge against downside price risk in the acquirer's equity."
ANSWER: Price-protection CVRs are granted when payment is share based to provide a hedge against downside price risk in the acquirer's equity [S2].
```

## Citation check (automatic)

- **Status:** insufficient
- **Labels cited in answer:** S2
- [S2] “Price-protection CVRs are granted when payment is share based - protecting the acquired company, by providing a hedge against downside price risk in the acquirer's equity.” — found in passage
- claim “Price-protection CVRs are granted when payment is share based to provide a hedge against downside price risk in the acquirer's equity.” — supported by S2 (S2: 93% word overlap)
- ⚠ relevance check: the answer does not give what the question asks for, so the harness reports insufficient evidence (answer kept above)

## Timing and memory

- 1269 prompt tok · 81 new tok · 57 tok/s · 2.8s · peak 4.32 GB
- retrieval 1.199s · model load 3.45s · total 7.51s
