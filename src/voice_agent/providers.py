"""Factories for speech, language, and voice providers."""

from __future__ import annotations

from typing import Any

from livekit.plugins import groq, openai, sarvam

from voice_agent.config import LLMProvider, Settings
from voice_agent.stt_providers import build_stt

__all__ = ["build_llm", "build_stt", "build_tts"]


def build_llm(settings: Settings) -> Any:
    match settings.llm_provider:
        case LLMProvider.GROQ:
            return groq.LLM(
                model=settings.llm_model,
                api_key=settings.groq_key,
                base_url=settings.groq_base_url,
                reasoning_effort=settings.llm_reasoning_effort,
                max_completion_tokens=settings.llm_max_completion_tokens,
            )
        case LLMProvider.OPENAI:
            return openai.LLM(
                model=settings.llm_model,
                api_key=settings.openai_key,
                base_url=settings.openai_url,
                max_completion_tokens=settings.llm_max_completion_tokens,
            )
        case LLMProvider.SARVAM:
            return openai.LLM(
                model=settings.llm_model,
                api_key=settings.sarvam_key,
                base_url=settings.sarvam_url,
                reasoning_effort=None,
                max_completion_tokens=settings.llm_max_completion_tokens,
            )


def build_tts(settings: Settings) -> Any:
    return sarvam.TTS(
        model=settings.tts_model,
        target_language_code=settings.tts_language,
        speaker=settings.tts_speaker,
        api_key=settings.sarvam_key,
    )
