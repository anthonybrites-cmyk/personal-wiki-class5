# Setup check: following the README from a fresh clone

Checklist item 2 says to follow the documented setup once more. On 2026-09-28, after the
repo was published, I cloned it anonymously into an empty folder and ran the README's
Setup steps exactly (online, since setup needs the network):

| Step | Command | Result |
|---|---|---|
| Clone | `git clone https://github.com/anthonybrites-cmyk/personal-wiki-class5.git` | only `main` present, head `08eda47` |
| Virtualenv | `python3.11 -m venv .venv` | Python 3.11.2 |
| Packages | `.venv/bin/pip install --no-cache-dir -r requirements.txt` | exit 0 |
| Gemma weights | `.venv/bin/hf download mlx-community/gemma-4-e2b-it-4bit --revision 2387675…` | resolved to the pinned snapshot (already cached, so nothing re-downloaded) |
| Embeddings | `.venv/bin/hf download mlx-community/bge-small-en-v1.5-4bit --revision 6d66cdf…` | resolved to the pinned snapshot |
| Status | `./wiki status` | both models `cached ✓`; 3 source texts; 14 wiki notes (Articles 3, Concepts 9, Organizations 2); 61 passages; all 3 instruction files ✓ |
| Search | `./wiki search "LIFO reserve" -k 2` | 2 passages from `raw/Wikipedia - FIFO and LIFO accounting.md § LIFO`, no answer generated |
| Ask | `./wiki ask "In the Foo Co. example, what was the total cost of sales for November under FIFO?" --mode local --quiet` | "Under FIFO, the total cost of sales for November would be $11,050 [S1]" · citations verified · 64 tok/s · model load 3.7 s |

Because the weights were already in this Mac's cache, the two download commands only
verified the pinned revisions. On a new machine they download about 3.4 GB. What happens
when they have *not* been run is shown in [`error-handling.md`](error-handling.md).
