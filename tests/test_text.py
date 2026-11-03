"""Muga text normalization tests."""

import asyncio
from collections.abc import AsyncIterable

from voice_agent.text import normalize_muga_stream, normalize_muga_text


def test_preserves_dynamic_tone_instead_of_forcing_fallback() -> None:
    result = normalize_muga_text("[happy] Tum bahut pyaare ho.", fallback_tone="neutral")
    assert result == "[happy] Tum bahut pyaare ho."


def test_transliterates_devanagari_before_muga() -> None:
    result = normalize_muga_text("[whisper] नमस्ते, कैसे हो?", fallback_tone="neutral")
    assert result.startswith("[whisper] ")
    assert not any("\u0900" <= character <= "\u097f" for character in result)


def test_adds_fallback_tone_to_untagged_text() -> None:
    result = normalize_muga_text("Main tumhare saath hoon.", fallback_tone="neutral")
    assert result == "[neutral] Main tumhare saath hoon."


def test_stream_is_normalized_as_one_utterance() -> None:
    async def chunks() -> AsyncIterable[str]:
        yield "[happy] Tum "
        yield "bahut pyaare ho."

    async def collect() -> list[str]:
        return [part async for part in normalize_muga_stream(chunks(), fallback_tone="neutral")]

    assert asyncio.run(collect()) == ["[happy] Tum bahut pyaare ho."]
