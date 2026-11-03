"""Prompt manager invariants for the scheme voice guide."""

from voice_agent.promptmanger import PROMPTS


def test_scheme_prompt_keeps_voice_format_and_factual_limits() -> None:
    instructions = PROMPTS.agent_instructions

    assert "YojnaPath Sahayak" in instructions
    assert "Hinglish" in instructions
    assert "Devanagari" in instructions
    assert "Sarvam Bulbul" in instructions
    assert "no live scheme database" in instructions
    assert "Never invent current scheme names" in instructions
    assert "Do not ask for Aadhaar numbers" in instructions
    assert "योजना-पथ सहायक" in PROMPTS.greeting_text
