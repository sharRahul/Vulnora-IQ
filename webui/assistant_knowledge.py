"""Lightweight, dependency-free knowledge retrieval for the assistant.

Grounds assistant answers in VulnoraIQ's bundled AI-security documentation
(the OWASP LLM Top-10 notes and the assurance boundary) so a small local model
stays factual without any embedding model or external service. Retrieval is a
simple bag-of-words overlap score over Markdown sections — cheap, deterministic,
and good enough to surface the right paragraph for a finding or question.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
# docs/owasp = OWASP LLM Top-10 notes; model/knowledge = text extracted from the
# OWASP source PDFs (agentic, MCP, red-teaming, data-security, IR, ASVS, SAMM).
# Together these form the hybrid-RAG corpus the Nora assistant grounds on.
_DOC_DIRS = [_ROOT / "docs" / "owasp", _ROOT / "model" / "knowledge"]
_DOC_FILES = [_ROOT / "docs" / "ASSESSMENT_ASSURANCE.md"]
_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
_MAX_CHUNK = 1000
_TOKEN_RE = re.compile(r"[a-z0-9]{3,}")
_STOP = frozenset(
    "the and for are with that this from has have was were will not you your they them "
    "a an of to in on or by is it as be at can may use using review when which what how".split()
)


@dataclass(frozen=True)
class Snippet:
    source: str
    heading: str
    text: str


def _tokenise(text: str) -> list[str]:
    return [t for t in _TOKEN_RE.findall(text.lower()) if t not in _STOP]


def _split_sections(markdown: str) -> list[tuple[str, str]]:
    sections: list[tuple[str, str]] = []
    heading = "Overview"
    buffer: list[str] = []
    for line in markdown.splitlines():
        if line.startswith("#"):
            if buffer:
                sections.append((heading, "\n".join(buffer).strip()))
                buffer = []
            heading = line.lstrip("# ").strip() or heading
        else:
            buffer.append(line)
    if buffer:
        sections.append((heading, "\n".join(buffer).strip()))
    return [(h, t) for h, t in sections if len(t) >= 40]


def _chunk(text: str, size: int = _MAX_CHUNK) -> list[str]:
    """Split a long section into <=``size`` char chunks on paragraph boundaries.

    Extracted PDF sections can be many thousands of characters; chunking keeps
    retrieval granular and avoids losing content to a blunt truncation.
    """
    if len(text) <= size:
        return [text]
    chunks: list[str] = []
    current = ""
    for para in re.split(r"\n\s*\n", text):
        para = para.strip()
        if not para:
            continue
        if current and len(current) + len(para) + 2 > size:
            chunks.append(current)
            current = para
        elif len(para) > size:
            # a single oversized paragraph: hard-split it
            if current:
                chunks.append(current)
                current = ""
            for i in range(0, len(para), size):
                chunks.append(para[i : i + size])
        else:
            current = f"{current}\n\n{para}" if current else para
    if current:
        chunks.append(current)
    return chunks


@lru_cache(maxsize=1)
def _corpus() -> tuple[Snippet, ...]:
    snippets: list[Snippet] = []
    files: list[Path] = list(_DOC_FILES)
    for directory in _DOC_DIRS:
        if directory.is_dir():
            files.extend(sorted(directory.glob("*.md")))
    for path in files:
        if not path.is_file():
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        content = _HTML_COMMENT_RE.sub("", content)  # drop <!-- page N --> markers
        for heading, text in _split_sections(content):
            for chunk in _chunk(text):
                snippets.append(Snippet(source=path.name, heading=heading, text=chunk))
    return tuple(snippets)


def search(query: str, *, limit: int = 3) -> list[Snippet]:
    """Return the most relevant documentation snippets for ``query``."""
    wanted = _tokenise(query)
    if not wanted:
        return []
    wanted_set = set(wanted)
    scored: list[tuple[float, Snippet]] = []
    for snippet in _corpus():
        tokens = _tokenise(snippet.heading + " " + snippet.text)
        if not tokens:
            continue
        overlap = sum(1 for t in tokens if t in wanted_set)
        if not overlap:
            continue
        # Normalise by length so long sections do not always win.
        score = overlap / (len(tokens) ** 0.5)
        scored.append((score, snippet))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [snippet for _, snippet in scored[:limit]]


def context_block(query: str, *, limit: int = 3) -> str:
    """Format the top snippets as a compact context block for the prompt."""
    hits = search(query, limit=limit)
    if not hits:
        return ""
    parts = [f"[{hit.source} · {hit.heading}]\n{hit.text}" for hit in hits]
    return "\n\n".join(parts)
