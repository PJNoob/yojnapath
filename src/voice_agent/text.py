"""Text normalization for Rumik Muga's strict input contract."""

from __future__ import annotations

import re
from collections.abc import AsyncIterable, AsyncIterator

from indic_transliteration import sanscript  # type: ignore[import-untyped]
from indic_transliteration.sanscript import transliterate  # type: ignore[import-untyped]

_TONE_PREFIX = re.compile(
    r"^\s*\[(neutral|happy|excited|sad|angry|whisper)\]\s*",
    flags=re.IGNORECASE,
)
_ANY_SQUARE_TAG = re.compile(r"\[[^\]]*\]")
_DEVANAGARI = re.compile(r"[\u0900-\u097f]")
_WHITESPACE = re.compile(r"\s+")


def normalize_muga_text(text: str, *, fallback_tone: str) -> str:
    """Return one Roman-script utterance with exactly one leading Muga tone tag."""

    match = _TONE_PREFIX.match(text)
    tone = match.group(1).lower() if match else fallback_tone
    body = text[match.end() :] if match else text
    body = _ANY_SQUARE_TAG.sub("", body)

    if _DEVANAGARI.search(body):
        body = transliterate(body, sanscript.DEVANAGARI, sanscript.ITRANS)

    body = _WHITESPACE.sub(" ", body).strip()
    if not body:
        body = "Main yahin hoon."

    return f"[{tone}] {body}"


async def normalize_muga_stream(
    chunks: AsyncIterable[str], *, fallback_tone: str
) -> AsyncIterator[str]:
    """Aggregate streamed LLM deltas so tone and script can be normalized atomically."""

    text = "".join([chunk async for chunk in chunks])
    yield normalize_muga_text(text, fallback_tone=fallback_tone)
