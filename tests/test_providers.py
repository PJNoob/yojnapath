"""Provider routing tests without external network calls."""

from types import SimpleNamespace
from typing import cast
from unittest.mock import patch

from voice_agent.config import LLMProvider, Settings, STTProvider
from voice_agent.promptmanger import PROMPTS
from voice_agent.providers import build_llm, build_stt, build_tts


def provider_settings(provider: LLMProvider) -> Settings:
    values = SimpleNamespace(
        llm_provider=provider,
        llm_model="test-model",
        groq_key="groq-test",
        groq_base_url="https://groq.invalid/v1",
        openai_key="sk-no-key-required",
        openai_url="http://127.0.0.1:8080/v1",
        sarvam_key="sarvam-test",
        sarvam_url="https://api.sarvam.ai/v1",
        llm_reasoning_effort="none",
        llm_max_completion_tokens=128,
    )
    return cast(Settings, values)


def stt_settings(provider: STTProvider) -> Settings:
    values = SimpleNamespace(
        stt_provider=provider,
        stt_sarvam_model="saaras:v4",
        stt_sarvam_language="hi-IN",
        stt_sarvam_mode="codemix",
        sarvam_key="sarvam-test",
        stt_groq_model="whisper-large-v3-turbo",
        stt_pulse_model="pulse",
        groq_key="groq-test",
        groq_base_url="https://groq.invalid/v1",
        smallest_key="smallest-test",
        smallest_url="https://smallest.invalid/v1",
        stt_language="hi",
        stt_detect_language=False,
        stt_sample_rate=16000,
        stt_encoding="linear16",
        stt_word_timestamps=True,
        stt_diarize=False,
        stt_eou_timeout_ms=300,
        stt_endpointing=True,
        stt_keywords=[],
        stt_format=True,
        stt_sentence_timestamps=True,
        stt_redact_pii=False,
        stt_redact_pci=False,
    )
    return cast(Settings, values)


def test_build_stt_routes_to_sarvam() -> None:
    settings = stt_settings(STTProvider.SARVAM)

    with patch("voice_agent.stt_providers.sarvam.STT") as constructor:
        build_stt(settings)

    constructor.assert_called_once_with(
        model="saaras:v4",
        language="hi-IN",
        mode="codemix",
        sample_rate=16000,
        api_key="sarvam-test",
    )


def test_build_tts_routes_to_sarvam() -> None:
    settings = cast(
        Settings,
        SimpleNamespace(
            tts_model="bulbul:v3",
            tts_language="hi-IN",
            tts_speaker="shubh",
            sarvam_key="sarvam-test",
        ),
    )

    with patch("voice_agent.providers.sarvam.TTS") as constructor:
        build_tts(settings)

    constructor.assert_called_once_with(
        model="bulbul:v3",
        target_language_code="hi-IN",
        speaker="shubh",
        api_key="sarvam-test",
    )


def test_build_stt_routes_to_groq() -> None:
    settings = stt_settings(STTProvider.GROQ)

    with patch("voice_agent.stt_providers.groq.STT") as constructor:
        build_stt(settings)

    constructor.assert_called_once_with(
        model="whisper-large-v3-turbo",
        api_key="groq-test",
        base_url="https://groq.invalid/v1",
        language="hi",
        prompt=PROMPTS.transcription_context,
        detect_language=False,
    )


def test_build_stt_routes_to_smallest_pulse() -> None:
    settings = stt_settings(STTProvider.PULSE)

    with patch("voice_agent.stt_providers.smallestai.STT") as constructor:
        build_stt(settings)

    constructor.assert_called_once_with(
        model="pulse",
        api_key="smallest-test",
        base_url="https://smallest.invalid/v1",
        language="hi",
        sample_rate=16000,
        encoding="linear16",
        word_timestamps=True,
        diarize=False,
        eou_timeout_ms=300,
        endpointing=True,
        keywords=[],
        format=True,
        sentence_timestamps=True,
        redact_pii=False,
        redact_pci=False,
    )


def test_build_llm_routes_to_groq() -> None:
    settings = provider_settings(LLMProvider.GROQ)

    with patch("voice_agent.providers.groq.LLM") as constructor:
        build_llm(settings)

    constructor.assert_called_once_with(
        model="test-model",
        api_key="groq-test",
        base_url="https://groq.invalid/v1",
        reasoning_effort="none",
        max_completion_tokens=128,
    )


def test_build_llm_routes_to_openai_compatible_api() -> None:
    settings = provider_settings(LLMProvider.OPENAI)

    with patch("voice_agent.providers.openai.LLM") as constructor:
        build_llm(settings)

    constructor.assert_called_once_with(
        model="test-model",
        api_key="sk-no-key-required",
        base_url="http://127.0.0.1:8080/v1",
        max_completion_tokens=128,
    )


def test_build_llm_routes_to_sarvam_with_reasoning_disabled() -> None:
    settings = provider_settings(LLMProvider.SARVAM)

    with patch("voice_agent.providers.openai.LLM") as constructor:
        build_llm(settings)

    constructor.assert_called_once_with(
        model="test-model",
        api_key="sarvam-test",
        base_url="https://api.sarvam.ai/v1",
        reasoning_effort=None,
        max_completion_tokens=128,
    )
