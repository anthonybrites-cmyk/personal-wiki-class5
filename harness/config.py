"""Paths, model identity, and the knobs that shape retrieval and prompts.

Everything a reader might want to tune lives here, in one place.
"""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# --- Data layout -----------------------------------------------------------------
VAULT = ROOT / "vault"                # open THIS folder in Obsidian
RAW = VAULT / "raw"                   # original sources, never modified
WIKI = VAULT / "wiki"                 # reviewed, linked notes (Projects/, Concepts/, Tools/)
INDEX_MD = VAULT / "index.md"         # human landing page, rebuilt by ingest
CATALOG_MD = VAULT / "Source Catalog.md"

STORE = ROOT / "store"                # machine files: chunks, embeddings, catalog (outside the vault)
CHUNKS_FILE = STORE / "chunks.jsonl"
EMBEDDINGS_FILE = STORE / "embeddings.npy"
CATALOG_JSON = STORE / "catalog.json"

INSTRUCTIONS = ROOT / "instructions"  # prompts the harness loads per mode
PERSONA_MD = INSTRUCTIONS / "persona.md"
RESEARCH_MD = INSTRUCTIONS / "wiki-instructions.md"
INGEST_MD = INSTRUCTIONS / "ingest-instructions.md"

# Saved outputs (ask records, chat transcripts, ingest reports). Overridable so the
# offline demo can write straight into evidence/.
RUNS = Path(os.environ.get("WIKI_RUNS_DIR", ROOT / "runs"))
DRAFTS = ROOT / "drafts"              # chat replies saved with /save — generated, never evidence

# One "source" note per file in raw/, plus topic notes for what several sources share.
# Each kind's folder, and the frontmatter key a source note uses to list its topics.
SOURCE_KIND = "source"
TOPIC_KINDS = {"concept": "concepts", "organization": "organizations"}
WIKI_FOLDERS = {"source": "Articles", "concept": "Concepts", "organization": "Organizations"}
WIKI_GROUPS = [  # index.md sections: (heading, kind, one-line description)
    ("Articles", "source", "One note per source article: what it explains."),
    ("Concepts", "concept", "Ideas and methods that show up across the articles."),
    ("Organizations", "organization", "Standard setters, agencies, and companies in the material."),
]
WIKI_TITLE = "Accounting and Deals Wiki"
WIKI_INTRO = ("A study wiki on accounting for inventory and acquisitions, built from three "
              "Wikipedia articles (CC BY-SA 4.0, see ATTRIBUTION.md) by a local Gemma model and "
              "reviewed by hand. Start with an article note, follow its **Related notes** to shared "
              "concepts and organizations, and use each note's **Source** link to open the "
              "original text in `raw/`.")

# --- Models ------------------------------------------------------------------------
# Generator: Gemma 4 E2B, instruction-tuned, 4-bit affine quantization (group size 64),
# converted to MLX by mlx-community. Pinned to the snapshot this project was tested on.
GEMMA_ID = "mlx-community/gemma-4-e2b-it-4bit"
GEMMA_REVISION = "238767527555cb75a05732a84dff5d6ba0dd6809"
GEMMA_LABEL = "Gemma 4 E2B-it · 4-bit MLX"

# Embeddings for the vector half of hybrid retrieval (384-dim, ~20 MB, local).
EMBED_ID = "mlx-community/bge-small-en-v1.5-4bit"
EMBED_REVISION = "6d66cdf333ff5d4cdad084f2fc2a619575d064ab"
EMBED_QUERY_PREFIX = "Represent this sentence for searching relevant passages: "

# --- Chunking ----------------------------------------------------------------------
CHUNK_TARGET_WORDS = 170   # pack Markdown blocks up to about this many words
CHUNK_MAX_WORDS = 240      # hard ceiling; bigger blocks are split by line
CHUNK_MIN_WORDS = 8        # drop fragments like a lone image link

# --- Retrieval ---------------------------------------------------------------------
RRF_K = 60                 # reciprocal-rank-fusion constant for BM25 + vector ranks
ASK_TOP_K = 6              # passages sent to Gemma in ask mode
CHAT_TOP_K = 4             # passages sent to Gemma when chat decides to retrieve
SEARCH_TOP_K = 5           # passages printed by search
MAX_PER_SOURCE = 3         # keeps one long source from crowding out the others
MIN_VECTOR_SCORE = 0.45    # below this and with no keyword hit, a passage is "not relevant"

# --- Generation --------------------------------------------------------------------
ASK_MAX_TOKENS = 350
ASK_TEMPERATURE = 0.0      # greedy: the same evidence gives the same answer
CHAT_MAX_TOKENS = 450
CHAT_TEMPERATURE = 0.7
CHAT_HISTORY_MESSAGES = 12 # trailing user+assistant messages sent back each turn
INGEST_MAX_TOKENS = 900
INGEST_TEMPERATURE = 0.0
INGEST_SOURCE_WORDS = 2200 # how much of one source goes into the page-writing prompt
INGEST_MAX_FACTS = 7       # facts kept per source note (the rest are reported, not written)
