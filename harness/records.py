"""Saved outputs: every ask, search, chat session and ingest leaves a record on disk.

Records go to runs/ by default (git-ignored scratch). The offline demo points
WIKI_RUNS_DIR at evidence/ so the exact outputs of that run are what gets committed.
"""
from __future__ import annotations

import json
import re
import socket
from datetime import datetime
from pathlib import Path

from . import config


def stamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def slug(text: str, n: int = 48) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:n].rstrip("-") or "untitled"


def network_state() -> str:
    """Best-effort label for the record: can this machine resolve a public hostname?"""
    try:
        socket.setdefaulttimeout(1.5)
        socket.gethostbyname("huggingface.co")
        return "online (network reachable; harness still pinned to local files)"
    except OSError:
        return "offline (no DNS)"
    finally:
        socket.setdefaulttimeout(None)


def save(kind: str, name: str, record: dict, markdown: str | None = None) -> Path:
    folder = config.RUNS / kind
    folder.mkdir(parents=True, exist_ok=True)
    base = folder / f"{stamp()}-{slug(name)}"
    record = {"saved_at": datetime.now().isoformat(timespec="seconds"), **record}
    base.with_suffix(".json").write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n",
                                         encoding="utf-8")
    if markdown is not None:
        base.with_suffix(".md").write_text(markdown, encoding="utf-8")
    return base.with_suffix(".md" if markdown is not None else ".json")
