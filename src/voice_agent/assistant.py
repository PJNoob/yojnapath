"""YojnaPath voice assistant behavior."""

from livekit.agents import Agent


class VoiceAssistant(Agent):
    """Small conversational agent whose behavior comes entirely from settings."""

    def __init__(
        self,
        *,
        instructions: str,
        greeting_text: str,
    ) -> None:
        super().__init__(instructions=instructions)
        self._greeting_text = greeting_text

    async def on_enter(self) -> None:
        self.session.say(self._greeting_text)
