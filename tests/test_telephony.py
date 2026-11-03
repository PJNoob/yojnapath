"""Tests for deterministic, offline telephony provisioning config."""

from tests.test_config import settings_values
from voice_agent.config import Settings
from voice_agent.telephony import build_plivo_india_plan


def test_plivo_plan_uses_india_endpoint_and_explicit_agent_dispatch() -> None:
    values = settings_values()
    values["livekit_sip_subdomain"] = "project-sip"
    values["plivo_phone_number"] = "+919876543210"
    settings = Settings(**values)  # type: ignore[arg-type]

    plan = build_plivo_india_plan(settings)
    dispatch = plan.dispatch_rule.model_dump(by_alias=True)

    assert plan.livekit_sip_endpoint == (
        "project-sip.india.sip.livekit.cloud;transport=tcp"
    )
    assert dispatch["roomConfig"]["agents"][0]["agentName"] == "test-agent"
    assert dispatch["rule"]["dispatchRuleIndividual"]["roomPrefix"] == "call-"


def test_plivo_plan_rejects_non_e164_number() -> None:
    values = settings_values()
    values["livekit_sip_subdomain"] = "project-sip"
    values["plivo_phone_number"] = "9876543210"
    settings = Settings(**values)  # type: ignore[arg-type]

    try:
        build_plivo_india_plan(settings)
    except ValueError as error:
        assert "E.164" in str(error)
    else:
        raise AssertionError("A non-E.164 Plivo number was accepted")
