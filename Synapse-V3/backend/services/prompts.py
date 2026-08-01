"""Prompt loading. Prompts live in backend/prompts/*.md, never inline in Python."""

import re
from functools import lru_cache
from pathlib import Path

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"

_VERSION_RE = re.compile(r"<!--\s*version:\s*(\S+)")


@lru_cache
def load_prompt(name: str) -> str:
    """Return the prompt body for prompts/<name>.md (header comment included)."""
    path = PROMPTS_DIR / f"{name}.md"
    return path.read_text(encoding="utf-8")


@lru_cache
def prompt_version(name: str) -> str:
    """Parse the version out of the prompt's header comment, for trace rows."""
    match = _VERSION_RE.search(load_prompt(name))
    return f"{name}-v{match.group(1)}" if match else f"{name}-v?"
