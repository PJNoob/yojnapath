"""Voice assistant behavior and Muga-safe text delivery."""

from collections.abc import AsyncIterable
from typing import Any

from livekit.agents import Agent, ModelSettings

from voice_agent.text import normalize_muga_stream


class VoiceAssistant(Agent):
    """Small conversational agent whose behavior comes entirely from settings."""

    def __init__(
        self,
        *,
        instructions: str,
        greeting_instructions: str,
        fallback_tone: str,
    ) -> None:
        super().__init__(instructions=instructions)
        self._greeting_instructions = greeting_instructions
        self._fallback_tone = fallback_tone

    async def on_enter(self) -> None:
        self.session.generate_reply(instructions=self._greeting_instructions)

    def tts_node(self, text: AsyncIterable[str], model_settings: ModelSettings) -> Any:
        """Normalize the complete reply before Muga validates and synthesizes it."""

        normalized_text = normalize_muga_stream(text, fallback_tone=self._fallback_tone)
        return Agent.default.tts_node(self, normalized_text, model_settings)
