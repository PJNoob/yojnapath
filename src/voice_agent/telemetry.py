"""Langfuse tracing integration for LiveKit's OpenTelemetry spans."""

from __future__ import annotations

from langfuse import Langfuse
from livekit.agents.telemetry import set_tracer_provider
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.util.types import AttributeValue

from voice_agent.config import Settings


def setup_langfuse(
    settings: Settings,
    *,
    metadata: dict[str, AttributeValue] | None = None,
) -> TracerProvider | None:
    """Configure one shared provider for LiveKit and Langfuse, when enabled."""

    if not settings.langfuse_enabled:
        return None

    public_key = settings.langfuse_public
    secret_key = settings.langfuse_secret
    base_url = settings.langfuse_url
    if not public_key or not secret_key or not base_url:
        raise ValueError("Langfuse tracing is enabled but its credentials are incomplete")

    tracer_provider = TracerProvider()
    set_tracer_provider(tracer_provider, metadata=metadata)
    Langfuse(
        public_key=public_key,
        secret_key=secret_key,
        base_url=base_url,
        tracer_provider=tracer_provider,
        should_export_span=lambda _span: True,
    )
    return tracer_provider
