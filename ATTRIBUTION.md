# Attribution and license for the wiki content

The source texts in `vault/raw/` are plain-text extracts of three English Wikipedia
articles, retrieved on 2026-09-28 through the MediaWiki API (`prop=extracts`,
`explaintext=1`). Each file is the article title on the first line, then the API's text,
unchanged. The plain-text export drops tables and images: the FIFO article's inventory
table and the Goodwill article's formatting are not in the extract.

| Article | Revision used | Authors | File |
|---|---|---|---|
| [Contingent value rights](https://en.wikipedia.org/wiki/Contingent_value_rights) | [1369971399](https://en.wikipedia.org/w/index.php?oldid=1369971399) (2026-08-18) | [page history (authors)](https://en.wikipedia.org/w/index.php?title=Contingent_value_rights&action=history) | `raw/Wikipedia - Contingent value rights.txt` |
| [FIFO and LIFO accounting](https://en.wikipedia.org/wiki/FIFO_and_LIFO_accounting) | [1324617022](https://en.wikipedia.org/w/index.php?oldid=1324617022) (2025-11-28) | [page history (authors)](https://en.wikipedia.org/w/index.php?title=FIFO_and_LIFO_accounting&action=history) | `raw/Wikipedia - FIFO and LIFO accounting.txt` |
| [Goodwill (accounting)](https://en.wikipedia.org/wiki/Goodwill_(accounting)) | [1367469269](https://en.wikipedia.org/w/index.php?oldid=1367469269) (2026-08-03) | [page history (authors)](https://en.wikipedia.org/w/index.php?title=Goodwill_(accounting)&action=history) | `raw/Wikipedia - Goodwill (accounting).txt` |

Wikipedia text is licensed under the
[Creative Commons Attribution-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-sa/4.0/)
(CC BY-SA 4.0). The authors are the Wikipedia contributors listed in each page history.

**Changes made.** `wiki convert` turned each `.txt` into a Markdown copy (`.md`, same words;
headings and preformatted blocks only). The notes in `vault/wiki/` are adapted from these
articles: summaries drafted by a local Gemma model and edited by hand. **The source texts,
their Markdown copies, and the wiki notes are shared under the same CC BY-SA 4.0 license.**

The harness code (`harness/`, `scripts/`, `wiki`) is my own work and is not part of the
licensed content.
