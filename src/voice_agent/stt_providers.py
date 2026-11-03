"""Speech-to-text provider strategies and their shared factory registry."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from types import MappingProxyType
from typing import Any

from livekit.plugins import groq, sarvam, smallestai

from voice_agent.config import Settings, STTProvider
from voice_agent.promptmanger import PROMPTS


class STTFactory(ABC):
    """Contract implemented by every speech-to-text provider."""

    @abstractmethod
    def create(self, settings: Settings) -> Any:
        """Build one LiveKit-compatible STT implementation."""


class GroqSTTFactory(STTFactory):
    """Create Groq's utterance-based Whisper implementation."""

    def create(self, settings: Settings) -> Any:
        return groq.STT(
            model=settings.stt_groq_model,
            api_key=settings.groq_key,
            base_url=settings.groq_base_url,
            language=settings.stt_language,
            prompt=PROMPTS.transcription_context,
            detect_language=settings.stt_detect_language,
        )


class PulseSTTFactory(STTFactory):
    """Create Smallest AI's realtime Pulse WebSocket implementation."""

    def create(self, settings: Settings) -> Any:
        return smallestai.STT(
            model=settings.stt_pulse_model,
            api_key=settings.smallest_key,
            base_url=settings.smallest_url,
            language=settings.stt_language,
            sample_rate=settings.stt_sample_rate,
            encoding=settings.stt_encoding,
            word_timestamps=settings.stt_word_timestamps,
            diarize=settings.stt_diarize,
            eou_timeout_ms=settings.stt_eou_timeout_ms,
            endpointing=settings.stt_endpointing,
            keywords=settings.stt_keywords,
            format=settings.stt_format,
            sentence_timestamps=settings.stt_sentence_timestamps,
            redact_pii=settings.stt_redact_pii,
            redact_pci=settings.stt_redact_pci,
        )


class SarvamSTTFactory(STTFactory):
    """Create Sarvam's streaming Saaras STT for Hindi and Hinglish."""

    def create(self, settings: Settings) -> Any:
        return sarvam.STT(
            model=settings.stt_sarvam_model,
            language=settings.stt_sarvam_language,
            mode=settings.stt_sarvam_mode,
            sample_rate=settings.stt_sample_rate,
            api_key=settings.sarvam_key,
        )


STT_FACTORIES: Mapping[STTProvider, STTFactory] = MappingProxyType(
    {
        STTProvider.GROQ: GroqSTTFactory(),
        STTProvider.PULSE: PulseSTTFactory(),
        STTProvider.SARVAM: SarvamSTTFactory(),
    }
)


def build_stt(settings: Settings) -> Any:
    """Resolve and execute the selected provider strategy."""

    return STT_FACTORIES[settings.stt_provider].create(settings)
