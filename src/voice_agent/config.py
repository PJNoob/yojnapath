"""Typed runtime configuration loaded from the development environment file."""

from __future__ import annotations

import os
from enum import StrEnum
from functools import lru_cache
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pydantic import Field, HttpUrl, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(os.getenv("VOICE_AGENT_ENV_FILE", ".env.dev"))


class LLMProvider(StrEnum):
    """Supported language-model API implementations."""

    GROQ = "groq"
    OPENAI = "openai"
    SARVAM = "sarvam"


class STTProvider(StrEnum):
    """Supported speech-to-text implementations."""

    GROQ = "groq"
    PULSE = "pulse"


class SipTransport(StrEnum):
    """Transport used between Plivo and the LiveKit SIP edge."""

    TCP = "tcp"
    TLS = "tls"


class Settings(BaseSettings):
    """All provider, model, and conversation configuration for the agent."""

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    environment: str = "development"
    log_level: str = "INFO"
    agent_name: str = Field(min_length=1)
    dev_server_host: str = Field(min_length=1)
    dev_server_port: int = Field(ge=0, le=65535)

    groq_api_key: SecretStr | None = None
    smallest_ai_api_key: SecretStr | None = None
    openai_api_key: SecretStr | None = None
    sarvam_api_key: SecretStr | None = None
    rumik_api_key: SecretStr
    livekit_url: str | None = None
    livekit_api_key: SecretStr | None = None
    livekit_api_secret: SecretStr | None = None

    livekit_sip_subdomain: str | None = None
    plivo_phone_number: str | None = None
    sip_room_prefix: str = Field(min_length=1)
    sip_transport: SipTransport

    langfuse_enabled: bool = False
    langfuse_secret_key: SecretStr | None = None
    langfuse_public_key: SecretStr | None = None
    langfuse_base_url: HttpUrl | None = None

    groq_base_url: str
    openai_base_url: str | None = None
    sarvam_base_url: str | None = None
    rumik_base_url: str
    smallest_base_url: str
    stt_provider: STTProvider
    stt_groq_model: str = Field(min_length=1)
    stt_pulse_model: Literal["pulse"]
    stt_language: str = Field(min_length=2, max_length=32)
    stt_detect_language: bool
    stt_sample_rate: int
    stt_encoding: Literal["linear16", "linear32", "alaw", "mulaw", "opus", "ogg_opus"]
    stt_word_timestamps: bool
    stt_diarize: bool
    stt_eou_timeout_ms: int = Field(ge=100, le=10000)
    stt_endpointing: bool
    stt_keywords: list[tuple[str, float]] = Field(default_factory=list)
    stt_format: bool
    stt_sentence_timestamps: bool
    stt_redact_pii: bool
    stt_redact_pci: bool
    stt_emotion_detection: bool
    llm_provider: LLMProvider
    llm_model: str = Field(min_length=1)
    llm_reasoning_effort: Literal["none", "low", "medium", "high"]
    llm_max_completion_tokens: int = Field(gt=0, le=4096)
    tts_model: Literal["muga"]
    tts_tone: Literal["neutral", "happy", "excited", "sad", "angry", "whisper"]
    tts_full_response_aggregation: bool

    vad_min_speech_duration: float = Field(gt=0, le=2)
    vad_min_silence_duration: float = Field(gt=0, le=3)
    vad_prefix_padding_duration: float = Field(ge=0, le=2)
    vad_activation_threshold: float = Field(gt=0, lt=1)
    endpointing_min_delay: float = Field(ge=0, le=5)
    endpointing_max_delay: float = Field(gt=0, le=10)
    false_interruption_timeout: float = Field(gt=0, le=5)
    aec_warmup_duration: float = Field(ge=0, le=10)
    preemptive_generation: bool

    @field_validator("rumik_api_key")
    @classmethod
    def api_key_must_not_be_blank(cls, value: SecretStr) -> SecretStr:
        if not value.get_secret_value().strip():
            raise ValueError("API key must be set in the selected environment file")
        return value

    @field_validator("endpointing_max_delay")
    @classmethod
    def endpointing_window_must_be_valid(cls, value: float, info: object) -> float:
        data = getattr(info, "data", {})
        min_delay = data.get("endpointing_min_delay", 0.0)
        if value < min_delay:
            raise ValueError("ENDPOINTING_MAX_DELAY must be >= ENDPOINTING_MIN_DELAY")
        return value

    @field_validator("stt_sample_rate")
    @classmethod
    def stt_sample_rate_must_be_supported(cls, value: int) -> int:
        supported_rates = {8000, 16000, 22050, 24000, 44100, 48000}
        if value not in supported_rates:
            raise ValueError(f"STT_SAMPLE_RATE must be one of {sorted(supported_rates)}")
        return value

    @model_validator(mode="after")
    def langfuse_credentials_must_be_complete(self) -> Settings:
        if self.langfuse_enabled and not all(
            (self.langfuse_secret_key, self.langfuse_public_key, self.langfuse_base_url)
        ):
            raise ValueError(
                "LANGFUSE_SECRET_KEY, LANGFUSE_PUBLIC_KEY, and LANGFUSE_BASE_URL are required "
                "when LANGFUSE_ENABLED=true"
            )
        return self

    @model_validator(mode="after")
    def selected_llm_provider_must_be_configured(self) -> Settings:
        if self.llm_provider is LLMProvider.GROQ and (
            self.groq_api_key is None or not self.groq_api_key.get_secret_value().strip()
        ):
            raise ValueError("GROQ_API_KEY is required when LLM_PROVIDER=groq")
        if self.llm_provider is LLMProvider.OPENAI:
            if not self.openai_base_url or not self.openai_base_url.strip():
                raise ValueError("OPENAI_BASE_URL is required when LLM_PROVIDER=openai")
            if not self.openai_api_key or not self.openai_api_key.get_secret_value().strip():
                raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")
        if self.llm_provider is LLMProvider.SARVAM:
            if not self.sarvam_base_url or not self.sarvam_base_url.strip():
                raise ValueError("SARVAM_BASE_URL is required when LLM_PROVIDER=sarvam")
            if not self.sarvam_api_key or not self.sarvam_api_key.get_secret_value().strip():
                raise ValueError("SARVAM_API_KEY is required when LLM_PROVIDER=sarvam")
        return self

    @model_validator(mode="after")
    def selected_stt_provider_must_be_configured(self) -> Settings:
        if self.stt_provider is STTProvider.GROQ and (
            self.groq_api_key is None or not self.groq_api_key.get_secret_value().strip()
        ):
            raise ValueError("GROQ_API_KEY is required when STT_PROVIDER=groq")
        if self.stt_provider is STTProvider.PULSE and (
            self.smallest_ai_api_key is None
            or not self.smallest_ai_api_key.get_secret_value().strip()
        ):
            raise ValueError("SMALLEST_AI_API_KEY is required when STT_PROVIDER=pulse")
        if self.stt_emotion_detection:
            raise ValueError(
                "STT_EMOTION_DETECTION is unavailable in realtime LiveKit STT; "
                "Smallest Pulse currently exposes it only through prerecorded transcription"
            )
        return self

    @property
    def groq_key(self) -> str:
        if self.groq_api_key is None:
            raise RuntimeError("Groq API key is not configured")
        return self.groq_api_key.get_secret_value()

    @property
    def rumik_key(self) -> str:
        return self.rumik_api_key.get_secret_value()

    @property
    def smallest_key(self) -> str:
        if self.smallest_ai_api_key is None:
            raise RuntimeError("Smallest AI API key is not configured")
        return self.smallest_ai_api_key.get_secret_value()

    @property
    def smallest_url(self) -> str:
        return self.smallest_base_url.rstrip("/")

    @property
    def openai_key(self) -> str:
        if self.openai_api_key is None:
            raise RuntimeError("OpenAI-compatible API key is not configured")
        return self.openai_api_key.get_secret_value()

    @property
    def openai_url(self) -> str:
        if self.openai_base_url is None:
            raise RuntimeError("OpenAI-compatible base URL is not configured")
        return self.openai_base_url.rstrip("/")

    @property
    def sarvam_key(self) -> str:
        if self.sarvam_api_key is None:
            raise RuntimeError("Sarvam API key is not configured")
        return self.sarvam_api_key.get_secret_value()

    @property
    def sarvam_url(self) -> str:
        if self.sarvam_base_url is None:
            raise RuntimeError("Sarvam base URL is not configured")
        return self.sarvam_base_url.rstrip("/")

    @property
    def langfuse_secret(self) -> str | None:
        return self.langfuse_secret_key.get_secret_value() if self.langfuse_secret_key else None

    @property
    def langfuse_public(self) -> str | None:
        return self.langfuse_public_key.get_secret_value() if self.langfuse_public_key else None

    @property
    def langfuse_url(self) -> str | None:
        return str(self.langfuse_base_url).rstrip("/") if self.langfuse_base_url else None


def load_environment() -> None:
    """Expose `.env.dev` values to LiveKit internals without overwriting shell values."""

    load_dotenv(ENV_FILE, override=False)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
