"""The scheme guide must not retain the old wellness companion persona."""

from voice_agent.promptmanger import PROMPTS


def test_scheme_prompt_has_no_old_companion_positioning() -> None:
    instructions = PROMPTS.agent_instructions.lower()

    assert "companio" not in instructions
    assert "savita" not in instructions
    assert "wellness call" not in instructions
