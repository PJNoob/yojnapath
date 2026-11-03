"""Fast tests for configuration invariants without provider network calls."""

from pydantic import SecretStr, ValidationError

from voice_agent.config import LLMProvider, Settings, STTProvider


def settings_values() -> dict[str, object]:
    return {
        "agent_name": "test-agent",
        "dev_server_host": "127.0.0.1",
        "dev_server_port": 8081,
        "groq_api_key": SecretStr("groq-test"),
        "smallest_ai_api_key": None,
        "openai_api_key": None,
        "sarvam_api_key": None,
        "rumik_api_key": SecretStr("rumik-test"),
        "livekit_sip_subdomain": None,
        "plivo_phone_number": None,
        "sip_room_prefix": "call-",
        "sip_transport": "tcp",
        "groq_base_url": "https://groq.invalid/v1",
        "openai_base_url": None,
        "sarvam_base_url": None,
        "rumik_base_url": "https://rumik.invalid",
        "smallest_base_url": "https://smallest.invalid/v1/",
        "stt_provider": "groq",
        "stt_groq_model": "whisper-test",
        "stt_pulse_model": "pulse",
        "stt_language": "en",
        "stt_detect_language": False,
        "stt_sample_rate": 16000,
        "stt_encoding": "linear16",
        "stt_word_timestamps": True,
        "stt_diarize": False,
        "stt_eou_timeout_ms": 300,
        "stt_endpointing": True,
        "stt_keywords": [],
        "stt_format": True,
        "stt_sentence_timestamps": True,
        "stt_redact_pii": False,
        "stt_redact_pci": False,
        "stt_emotion_detection": False,
        "llm_provider": "groq",
        "llm_model": "llm-test",
        "llm_reasoning_effort": "none",
        "llm_max_completion_tokens": 128,
        "tts_model": "muga",
        "tts_tone": "neutral",
        "tts_full_response_aggregation": True,
        "vad_min_speech_duration": 0.05,
        "vad_min_silence_duration": 0.55,
        "vad_prefix_padding_duration": 0.5,
        "vad_activation_threshold": 0.5,
        "endpointing_min_delay": 0.35,
        "endpointing_max_delay": 2.0,
        "false_interruption_timeout": 1.0,
        "aec_warmup_duration": 3.0,
        "preemptive_generation": True,
    }


def test_settings_accept_supported_pipeline() -> None:
    settings = Settings(**settings_values())  # type: ignore[arg-type]
    assert settings.tts_model == "muga"
    assert settings.llm_provider is LLMProvider.GROQ
    assert settings.stt_provider is STTProvider.GROQ
    assert settings.groq_key == "groq-test"


def test_settings_accept_pulse_stt_provider() -> None:
    values = settings_values()
    values["stt_provider"] = "pulse"
    values["smallest_ai_api_key"] = SecretStr("smallest-test")

    settings = Settings(**values)  # type: ignore[arg-type]

    assert settings.stt_provider is STTProvider.PULSE
    assert settings.smallest_key == "smallest-test"
    assert settings.smallest_url == "https://smallest.invalid/v1"


def test_pulse_and_sarvam_pipeline_does_not_require_groq_key() -> None:
    values = settings_values()
    values["stt_provider"] = "pulse"
    values["smallest_ai_api_key"] = SecretStr("smallest-test")
    values["llm_provider"] = "sarvam"
    values["sarvam_api_key"] = SecretStr("sarvam-test")
    values["sarvam_base_url"] = "https://api.sarvam.ai/v1"
    values["groq_api_key"] = None

    settings = Settings(**values)  # type: ignore[arg-type]

    assert settings.stt_provider is STTProvider.PULSE
    assert settings.llm_provider is LLMProvider.SARVAM


def test_pulse_stt_provider_requires_api_key() -> None:
    values = settings_values()
    values["stt_provider"] = "pulse"

    try:
        Settings(**values)  # type: ignore[arg-type]
    except ValidationError as error:
        assert "SMALLEST_AI_API_KEY" in str(error)
    else:
        raise AssertionError("Pulse STT provider without an API key was accepted")


def test_realtime_stt_rejects_unsupported_emotion_detection() -> None:
    values = settings_values()
    values["stt_emotion_detection"] = True

    try:
        Settings(**values)  # type: ignore[arg-type]
    except ValidationError as error:
        assert "prerecorded transcription" in str(error)
    else:
        raise AssertionError("Realtime STT accepted unsupported emotion detection")


def test_settings_accept_openai_compatible_provider() -> None:
    values = settings_values()
    values["llm_provider"] = "openai"
    values["openai_api_key"] = SecretStr("sk-no-key-required")
    values["openai_base_url"] = "http://127.0.0.1:8080/v1/"

    settings = Settings(**values)  # type: ignore[arg-type]

    assert settings.llm_provider is LLMProvider.OPENAI
    assert settings.openai_url == "http://127.0.0.1:8080/v1"


def test_openai_compatible_provider_requires_endpoint_settings() -> None:
    values = settings_values()
    values["llm_provider"] = "openai"

    try:
        Settings(**values)  # type: ignore[arg-type]
    except ValidationError as error:
        assert "OPENAI_BASE_URL" in str(error)
    else:
        raise AssertionError("OpenAI-compatible provider without an endpoint was accepted")


def test_settings_accept_sarvam_provider() -> None:
    values = settings_values()
    values["llm_provider"] = "sarvam"
    values["llm_model"] = "sarvam-105b-conversations"
    values["sarvam_api_key"] = SecretStr("sarvam-test")
    values["sarvam_base_url"] = "https://api.sarvam.ai/v1/"

    settings = Settings(**values)  # type: ignore[arg-type]

    assert settings.llm_provider is LLMProvider.SARVAM
    assert settings.sarvam_url == "https://api.sarvam.ai/v1"


def test_sarvam_provider_requires_endpoint_settings() -> None:
    values = settings_values()
    values["llm_provider"] = "sarvam"

    try:
        Settings(**values)  # type: ignore[arg-type]
    except ValidationError as error:
        assert "SARVAM_BASE_URL" in str(error)
    else:
        raise AssertionError("Sarvam provider without an endpoint was accepted")


def test_endpointing_max_cannot_precede_min() -> None:
    values = settings_values()
    values["endpointing_min_delay"] = 2.0
    values["endpointing_max_delay"] = 1.0

    try:
        Settings(**values)  # type: ignore[arg-type]
    except ValidationError as error:
        assert "ENDPOINTING_MAX_DELAY" in str(error)
    else:
        raise AssertionError("Invalid endpointing window was accepted")


def test_enabled_langfuse_requires_complete_credentials() -> None:
    values = settings_values()
    values["langfuse_enabled"] = True
    values["langfuse_secret_key"] = None
    values["langfuse_public_key"] = None
    values["langfuse_base_url"] = None

    try:
        Settings(**values)  # type: ignore[arg-type]
    except ValidationError as error:
        assert "LANGFUSE_SECRET_KEY" in str(error)
    else:
        raise AssertionError("Incomplete Langfuse configuration was accepted")
