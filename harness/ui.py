"""Tiny terminal helpers (colour only when writing to a real terminal)."""
from __future__ import annotations

import os
import sys
import textwrap

_COLOR = sys.stdout.isatty() and not os.environ.get("NO_COLOR")


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _COLOR else text


def dim(t: str) -> str: return _c("2", t)
def bold(t: str) -> str: return _c("1", t)
def cyan(t: str) -> str: return _c("36", t)
def green(t: str) -> str: return _c("32", t)
def yellow(t: str) -> str: return _c("33", t)
def red(t: str) -> str: return _c("31", t)
def magenta(t: str) -> str: return _c("35", t)


def rule(title: str = "") -> str:
    width = 78
    if not title:
        return dim("─" * width)
    return dim("── ") + bold(title) + dim(" " + "─" * max(3, width - len(title) - 4))


def indent(text: str, prefix: str = "    ", width: int = 96) -> str:
    out = []
    for line in text.splitlines() or [""]:
        if len(line) > width and not line.lstrip().startswith("|"):
            out.extend(textwrap.wrap(line, width, initial_indent=prefix, subsequent_indent=prefix))
        else:
            out.append(prefix + line)
    return "\n".join(out)


def err(msg: str) -> None:
    print(red("error: ") + msg, file=sys.stderr)
