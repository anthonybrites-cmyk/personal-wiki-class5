# Re-ingest check — 2026-09-28 22:27

**Result: PASS** — `./wiki ingest vault/raw --force` exited 0.

| Check | Result |
|---|---|
| Notes before → after | 17 → 17 |
| New files (duplicates) | none |
| Removed / renamed files | none |
| Machine-style filenames | none |
| Content changed (ignoring last_checked) | Source Catalog.md |
| Originals in raw/ unchanged | yes |
| Measured (`/usr/bin/time -l`) | 26.2 s wall · max RSS 2.78 GB · peak memory footprint 6.28 GB |

## Notes in the vault after re-ingest

- `Source Catalog.md`
- `attachments/README.md`
- `index.md`
- `wiki/Articles/Contingent Value Rights.md`
- `wiki/Articles/FIFO and LIFO Accounting.md`
- `wiki/Articles/Goodwill Accounting.md`
- `wiki/Concepts/Acquisition Premium.md`
- `wiki/Concepts/Business Valuation.md`
- `wiki/Concepts/Cost of Goods Sold.md`
- `wiki/Concepts/Impairment Testing.md`
- `wiki/Concepts/Intangible Asset.md`
- `wiki/Concepts/International Financial Reporting Standards.md`
- `wiki/Concepts/LIFO Reserve.md`
- `wiki/Concepts/Option Pricing.md`
- `wiki/Concepts/US GAAP.md`
- `wiki/Organizations/FASB.md`
- `wiki/Organizations/Save LIFO Coalition.md`

## Harness output

```text
── ingest · local · Gemma 4 E2B-it · 4-bit MLX ───────────────────────────────
  · raw/Wikipedia - Contingent value rights.md ...
  ✓ raw/Wikipedia - Contingent value rights.md → wiki/Articles/Contingent Value Rights.md [kept-reviewed] · kept 5 facts, dropped 1 · 6.4s
  · raw/Wikipedia - FIFO and LIFO accounting.md ...
  ✓ raw/Wikipedia - FIFO and LIFO accounting.md → wiki/Articles/FIFO and LIFO Accounting.md [kept-reviewed] · kept 6 facts, dropped 0 · 7.1s
  · raw/Wikipedia - Goodwill (accounting).md ...
  ✓ raw/Wikipedia - Goodwill (accounting).md → wiki/Articles/Goodwill Accounting.md [kept-reviewed] · kept 5 facts, dropped 0 · 7.1s

3 source(s): 3 processed, 0 unchanged · 0 topic note(s) written · index 61 passages · 26.0s · model load 3.4s
  dropped from wiki/Articles/Contingent Value Rights.md: 'FASB' — the source never names it
saved evidence/reingest-run/ingest/20260928-222733-report.md
```
