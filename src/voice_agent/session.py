"""LiveKit session assembly, turn handling, and input processing."""

from __future__ import annotations

from typing import Any

from livekit.agents import AgentSession, TurnHandlingOptions, inference, room_io
from livekit.plugins import noise_cancellation, silero

from voice_agent.config import Settings
from voice_agent.providers import build_llm, build_stt, build_tts


def build_vad(settings: Settings) -> Any:
    return silero.VAD.load(
        min_speech_duration=settings.vad_min_speech_duration,
        min_silence_duration=settings.vad_min_silence_duration,
        prefix_padding_duration=settings.vad_prefix_padding_duration,
        activation_threshold=settings.vad_activation_threshold,
    )


def build_session(settings: Settings, *, vad: Any) -> AgentSession[Any]:
    return AgentSession(
        stt=build_stt(settings),
        llm=build_llm(settings),
        tts=build_tts(settings),
        vad=vad,
        turn_handling=TurnHandlingOptions(
            turn_detection=inference.TurnDetector(),
            endpointing={
                "min_delay": settings.endpointing_min_delay,
                "max_delay": settings.endpointing_max_delay,
            },
            interruption={
                "resume_false_interruption": True,
                "false_interruption_timeout": settings.false_interruption_timeout,
            },
            preemptive_generation={"enabled": settings.preemptive_generation},
        ),
        aec_warmup_duration=settings.aec_warmup_duration,
    )


def build_room_options() -> room_io.RoomOptions:
    """Use LiveKit BVC for real room input; console mode supplies its own AEC path."""

    return room_io.RoomOptions(
        audio_input=room_io.AudioInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )
