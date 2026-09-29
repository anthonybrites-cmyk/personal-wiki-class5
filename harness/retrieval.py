"""The retrieval tool: a local hybrid index over vault passages.

Two rankers run over the same passages and are fused with reciprocal-rank fusion:
  * BM25 keyword search (pure Python, below) — exact names, numbers, acronyms.
  * bge-small vector search (local MLX embeddings) — reworded questions.
Search returns original passages with their source locations. It never calls Gemma.
"""
from __future__ import annotations

import json
import math
import re
from collections import Counter
from dataclasses import dataclass, field

import numpy as np

from . import config
from .sources import Passage, chunk_markdown, list_text_files

STOPWORDS = set("""
a an and are as at be been but by can could did do does for from had has have how i
if in into is it its me my of on or our so than that the their them then there these
they this to was we were what when where which who why will with you your about after
also any both each more most other some such only over under up out no not just very
""".split())


def tokenize(text: str) -> list[str]:
    """Lowercase words, stopwords removed, light suffix stripping so that
    'policies'/'policy' and 'trained'/'training'/'train' meet."""
    out = []
    for tok in re.findall(r"[a-z0-9]+", text.lower()):
        if tok in STOPWORDS or (len(tok) == 1 and not tok.isdigit()):
            continue
        for suffix, repl in (("ies", "y"), ("ing", ""), ("ed", ""), ("es", ""), ("s", "")):
            if len(tok) > len(suffix) + 3 and tok.endswith(suffix):
                tok = tok[: -len(suffix)] + repl
                break
        out.append(tok)
    return out


class BM25:
    def __init__(self, docs: list[list[str]], k1: float = 1.5, b: float = 0.75):
        self.k1, self.b = k1, b
        self.tf = [Counter(d) for d in docs]
        self.len = [len(d) for d in docs]
        self.avg = sum(self.len) / max(len(docs), 1)
        df = Counter(t for d in docs for t in set(d))
        n = len(docs)
        self.idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}

    def scores(self, query: list[str]) -> np.ndarray:
        out = np.zeros(len(self.tf))
        for i, tf in enumerate(self.tf):
            s = 0.0
            for t in set(query):
                f = tf.get(t)
                if f:
                    s += self.idf[t] * f * (self.k1 + 1) / (
                        f + self.k1 * (1 - self.b + self.b * self.len[i] / self.avg))
            out[i] = s
        return out


class Embedder:
    """Lazy wrapper around the local bge-small model (loads in well under a second)."""
    _model = _tok = None

    @classmethod
    def encode(cls, texts: list[str], batch: int = 16) -> np.ndarray:
        import mlx.core as mx
        from huggingface_hub import snapshot_download
        from mlx_embeddings import load
        if cls._model is None:
            path = snapshot_download(config.EMBED_ID, revision=config.EMBED_REVISION,
                                     local_files_only=True)
            cls._model, cls._tok = load(path)
        vecs = []
        for i in range(0, len(texts), batch):
            enc = cls._tok._tokenizer(texts[i:i + batch], return_tensors="np", padding=True,
                                      truncation=True, max_length=512)
            out = cls._model(mx.array(enc["input_ids"]),
                             attention_mask=mx.array(enc["attention_mask"]))
            vecs.append(np.array(out.text_embeds, dtype=np.float32))
        return np.concatenate(vecs) if vecs else np.zeros((0, 384), dtype=np.float32)


@dataclass
class Hit:
    passage: Passage
    score: float          # fused RRF score (higher is better)
    bm25: float
    vector: float         # cosine similarity
    rank: int = 0
    label: str = ""       # "S1", "S2", ... assigned when shown to the model or the user

    def to_dict(self) -> dict:
        return {"label": self.label, "rank": self.rank, "score": round(self.score, 5),
                "bm25": round(self.bm25, 3), "vector": round(self.vector, 4),
                **self.passage.to_dict()}


@dataclass
class Index:
    passages: list[Passage]
    embeddings: np.ndarray | None
    bm25: BM25 = field(init=False)

    def __post_init__(self):
        self.bm25 = BM25([tokenize(p.search_text()) for p in self.passages])

    # --- build / load ---------------------------------------------------------------
    @classmethod
    def build(cls, with_embeddings: bool = True) -> "Index":
        passages = [p for f in list_text_files(config.RAW) for p in chunk_markdown(f, "source")]
        if config.WIKI.exists():
            passages += [p for f in list_text_files(config.WIKI) for p in chunk_markdown(f, "wiki")]
        emb = Embedder.encode([p.search_text() for p in passages]) if with_embeddings else None
        index = cls(passages, emb)
        index.save()
        return index

    def save(self) -> None:
        config.STORE.mkdir(exist_ok=True)
        with config.CHUNKS_FILE.open("w", encoding="utf-8") as fh:
            for p in self.passages:
                fh.write(json.dumps(p.to_dict(), ensure_ascii=False) + "\n")
        if self.embeddings is not None:
            np.save(config.EMBEDDINGS_FILE, self.embeddings)
        elif config.EMBEDDINGS_FILE.exists():
            config.EMBEDDINGS_FILE.unlink()

    @classmethod
    def load(cls) -> "Index":
        if not config.CHUNKS_FILE.exists():
            raise FileNotFoundError(
                f"No retrieval index at {config.CHUNKS_FILE.relative_to(config.ROOT)}. "
                "Run `wiki index` (or `wiki ingest vault/raw`) first.")
        passages = [Passage(**json.loads(line))
                    for line in config.CHUNKS_FILE.read_text(encoding="utf-8").splitlines() if line]
        emb = np.load(config.EMBEDDINGS_FILE) if config.EMBEDDINGS_FILE.exists() else None
        if emb is not None and len(emb) != len(passages):
            emb = None  # stale vectors: fall back to keywords rather than mis-align
        return cls(passages, emb)

    # --- search ---------------------------------------------------------------------
    def search(self, query: str, k: int, kinds: tuple[str, ...] = ("source",),
               paths: set[str] | None = None, max_per_source: int | None = None) -> list[Hit]:
        keep = [i for i, p in enumerate(self.passages)
                if p.kind in kinds and (paths is None or p.path in paths)]
        if not keep:
            return []
        bm = self.bm25.scores(tokenize(query))[keep]
        if self.embeddings is not None:
            q = Embedder.encode([config.EMBED_QUERY_PREFIX + query])[0]
            vec = self.embeddings[keep] @ q
        else:
            vec = np.zeros(len(keep))

        # Reciprocal-rank fusion: robust to the two scores living on different scales.
        fused = np.zeros(len(keep))
        for scores, active in ((bm, bm.max() > 0), (vec, self.embeddings is not None)):
            if not active:
                continue
            order = np.argsort(-scores)
            for rank, j in enumerate(order):
                if scores[j] > 0:
                    fused[j] += 1.0 / (config.RRF_K + rank + 1)

        hits, per_source = [], Counter()
        cap = max_per_source or config.MAX_PER_SOURCE
        for j in np.argsort(-fused):
            if fused[j] <= 0:
                break
            # A passage with no keyword overlap must at least be semantically close.
            if bm[j] == 0 and vec[j] < config.MIN_VECTOR_SCORE:
                continue
            p = self.passages[keep[j]]
            if per_source[p.path] >= cap:
                continue
            per_source[p.path] += 1
            hits.append(Hit(p, float(fused[j]), float(bm[j]), float(vec[j]), rank=len(hits) + 1))
            if len(hits) == k:
                break
        for h in hits:
            h.label = f"S{h.rank}"
        return hits
