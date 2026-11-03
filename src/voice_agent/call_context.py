"""Validated metadata supplied by the server's explicit LiveKit dispatch."""

from __future__ import annotations

import json

from pydantic import BaseModel, Field, ValidationError


class CallSessionContext(BaseModel):
    """Trusted server-created limits for a dispatched call."""

    call_session_id: str = Field(min_length=1, max_length=128)
    access_mode: str = Field(pattern="^(pilot|web)$")
    max_duration_seconds: int = Field(ge=60, le=3600)


def parse_call_session_context(metadata: str | None) -> CallSessionContext | None:
    """Return no context for local console sessions; reject malformed dispatched metadata."""
    if not metadata:
        return None
    try:
        return CallSessionContext.model_validate(json.loads(metadata))
    except (json.JSONDecodeError, ValidationError) as error:
        raise ValueError("Invalid dispatched call-session metadata") from error
