"""YojnaPath voice assistant behavior."""

from livekit.agents import Agent


class VoiceAssistant(Agent):
    """Small conversational agent whose behavior comes entirely from settings."""

    def __init__(
        self,
        *,
        instructions: str,
        greeting_instructions: str,
    ) -> None:
        super().__init__(instructions=instructions)
        self._greeting_instructions = greeting_instructions

    async def on_enter(self) -> None:
        self.session.generate_reply(instructions=self._greeting_instructions)
