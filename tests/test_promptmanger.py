"""Prompt manager invariants for the scheme voice guide."""

from voice_agent.promptmanger import PROMPTS


def test_scheme_prompt_keeps_voice_format_and_factual_limits() -> None:
    instructions = PROMPTS.agent_instructions

    assert "YojnaPath Sahayak" in instructions
    assert "Hinglish" in instructions
    assert "Roman letters" in instructions
    assert "Never use Devanagari" in instructions
    assert "exactly one Muga tone tag" in instructions
    assert "no live scheme database" in instructions
    assert "Never invent current scheme names" in instructions
    assert "Do not ask for Aadhaar numbers" in instructions
    assert "Muga tone tag" in PROMPTS.greeting_instructions
