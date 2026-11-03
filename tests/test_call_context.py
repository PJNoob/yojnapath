import pytest

from voice_agent.call_context import parse_call_session_context


def test_parse_call_session_context() -> None:
    context = parse_call_session_context(
        '{"call_session_id":"call-1","access_mode":"pilot","max_duration_seconds":600}'
    )

    assert context is not None
    assert context.max_duration_seconds == 600


def test_blank_metadata_is_supported_for_console_sessions() -> None:
    assert parse_call_session_context("") is None


def test_web_call_metadata_keeps_worker_duration_limit() -> None:
    context = parse_call_session_context(
        '{"call_session_id":"web-1","access_mode":"web","max_duration_seconds":300}'
    )

    assert context is not None
    assert context.access_mode == "web"
    assert context.max_duration_seconds == 300


def test_invalid_metadata_is_rejected() -> None:
    with pytest.raises(ValueError, match="Invalid dispatched"):
        parse_call_session_context('{"access_mode":"paid"}')
