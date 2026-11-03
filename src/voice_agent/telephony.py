"""Generate Plivo-to-LiveKit India SIP configuration from validated settings."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, field_validator

from voice_agent.config import Settings, get_settings, load_environment


class InboundTrunk(BaseModel):
    """LiveKit inbound SIP trunk payload."""

    model_config = ConfigDict(frozen=True)

    name: str
    numbers: list[str]


class InboundTrunkDocument(BaseModel):
    """Document accepted by `lk sip inbound create`."""

    model_config = ConfigDict(frozen=True)

    trunk: InboundTrunk


class IndividualDispatch(BaseModel):
    """Create one isolated room per telephone call."""

    model_config = ConfigDict(frozen=True, populate_by_name=True)

    room_prefix: str = Field(serialization_alias="roomPrefix")


class DispatchRule(BaseModel):
    """LiveKit individual dispatch rule."""

    model_config = ConfigDict(frozen=True, populate_by_name=True)

    individual: IndividualDispatch = Field(serialization_alias="dispatchRuleIndividual")


class AgentDispatch(BaseModel):
    """Agent assigned when LiveKit creates the call room."""

    model_config = ConfigDict(frozen=True, populate_by_name=True)

    agent_name: str = Field(serialization_alias="agentName")


class RoomConfig(BaseModel):
    """Room-level agent dispatch configuration."""

    model_config = ConfigDict(frozen=True)

    agents: list[AgentDispatch]


class DispatchRuleDocument(BaseModel):
    """Document accepted by `lk sip dispatch create`."""

    model_config = ConfigDict(frozen=True, populate_by_name=True)

    rule: DispatchRule
    name: str
    room_config: RoomConfig = Field(serialization_alias="roomConfig")


class PlivoIndiaPlan(BaseModel):
    """Validated provisioning values for a Plivo India inbound trunk."""

    model_config = ConfigDict(frozen=True)

    phone_number: str
    livekit_sip_endpoint: str
    inbound_trunk: InboundTrunkDocument
    dispatch_rule: DispatchRuleDocument

    @field_validator("phone_number")
    @classmethod
    def phone_number_must_be_e164(cls, value: str) -> str:
        if not re.fullmatch(r"\+[1-9]\d{7,14}", value):
            raise ValueError("PLIVO_PHONE_NUMBER must use E.164 format, for example +919876543210")
        return value


def build_plivo_india_plan(settings: Settings) -> PlivoIndiaPlan:
    """Build configs without making changes to either provider account."""

    subdomain = (settings.livekit_sip_subdomain or "").strip()
    phone_number = (settings.plivo_phone_number or "").strip()
    if not subdomain:
        raise ValueError("LIVEKIT_SIP_SUBDOMAIN is required to generate telephony config")
    if not re.fullmatch(r"[a-zA-Z0-9-]+", subdomain):
        raise ValueError("LIVEKIT_SIP_SUBDOMAIN must contain only the project SIP subdomain")
    if not phone_number:
        raise ValueError("PLIVO_PHONE_NUMBER is required to generate telephony config")

    endpoint = (
        f"{subdomain}.india.sip.livekit.cloud;transport={settings.sip_transport.value}"
    )
    return PlivoIndiaPlan(
        phone_number=phone_number,
        livekit_sip_endpoint=endpoint,
        inbound_trunk=InboundTrunkDocument(
            trunk=InboundTrunk(
                name=f"{settings.agent_name}-plivo-india",
                numbers=[phone_number],
            )
        ),
        dispatch_rule=DispatchRuleDocument(
            rule=DispatchRule(
                individual=IndividualDispatch(room_prefix=settings.sip_room_prefix)
            ),
            name=f"{settings.agent_name}-dispatch",
            room_config=RoomConfig(agents=[AgentDispatch(agent_name=settings.agent_name)]),
        ),
    )


def write_plan(plan: PlivoIndiaPlan, output_dir: Path) -> None:
    """Write CLI-ready LiveKit JSON plus the Plivo origination URI."""

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "livekit-inbound-trunk.json").write_text(
        plan.inbound_trunk.model_dump_json(by_alias=True, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_dir / "livekit-dispatch-rule.json").write_text(
        plan.dispatch_rule.model_dump_json(by_alias=True, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_dir / "plivo-origination-uri.txt").write_text(
        plan.livekit_sip_endpoint + "\n",
        encoding="utf-8",
    )


def run() -> None:
    """Generate provider configuration files; never calls provider APIs."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path(".telephony"))
    args = parser.parse_args()
    load_environment()
    plan = build_plivo_india_plan(get_settings())
    write_plan(plan, args.output_dir)
    print(f"Wrote Plivo/LiveKit India configuration to {args.output_dir}")
    print(f"Plivo origination URI: {plan.livekit_sip_endpoint}")


if __name__ == "__main__":
    run()
