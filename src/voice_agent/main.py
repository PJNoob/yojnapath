"""LiveKit agent server entrypoint."""

from __future__ import annotations

import asyncio
import logging

from livekit.agents import AgentServer, JobContext, JobProcess, cli

from voice_agent.assistant import VoiceAssistant
from voice_agent.call_context import parse_call_session_context
from voice_agent.config import get_settings, load_environment
from voice_agent.promptmanger import PROMPTS
from voice_agent.session import build_room_options, build_session, build_vad
from voice_agent.telemetry import setup_langfuse

load_environment()
settings = get_settings()
logging.basicConfig(level=settings.log_level.upper())
logger = logging.getLogger(__name__)

server = AgentServer(host=settings.dev_server_host, port=settings.dev_server_port)


def prewarm(process: JobProcess) -> None:
    process.userdata["vad"] = build_vad(settings)


server.setup_fnc = prewarm


@server.rtc_session(agent_name=settings.agent_name)
async def voice_agent(ctx: JobContext) -> None:
    call_context = parse_call_session_context(ctx.job.metadata)
    session_id = call_context.call_session_id if call_context else ctx.room.name
    ctx.log_context_fields = {"room": ctx.room.name, "call_session_id": session_id}
    tracer_provider = setup_langfuse(
        settings,
        metadata={
            "langfuse.session.id": session_id,
            "langfuse.trace.name": "yojnapath-scheme-voice-session",
            "langfuse.environment": settings.environment,
        },
    )
    if tracer_provider is not None:

        async def flush_traces() -> None:
            tracer_provider.force_flush()

        ctx.add_shutdown_callback(flush_traces)

    session = build_session(settings, vad=ctx.proc.userdata["vad"])

    await session.start(
        room=ctx.room,
        agent=VoiceAssistant(
            instructions=PROMPTS.agent_instructions,
            greeting_instructions=PROMPTS.greeting_instructions,
            fallback_tone=settings.tts_tone,
        ),
        room_options=build_room_options(),
    )
    logger.info("Voice session started")

    if call_context is not None:

        async def close_on_limit() -> None:
            await asyncio.sleep(call_context.max_duration_seconds)
            logger.info("Voice call reached configured duration limit")
            ctx.shutdown(reason="call_duration_limit")

        limit_task = asyncio.create_task(close_on_limit())

        async def cancel_duration_limit() -> None:
            limit_task.cancel()

        ctx.add_shutdown_callback(cancel_duration_limit)


def run() -> None:
    cli.run_app(server)


if __name__ == "__main__":
    run()
