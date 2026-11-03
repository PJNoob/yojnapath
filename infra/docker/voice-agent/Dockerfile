FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:0.8.15 /uv /uvx /usr/local/bin/
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
ENV UV_NO_DEV=1 UV_LINK_MODE=copy PYTHONUNBUFFERED=1
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --locked --no-dev --no-install-project
COPY src/voice_agent ./src/voice_agent
RUN uv sync --locked --no-dev

RUN useradd --create-home --uid 10001 agent && chown -R agent:agent /app
USER agent
EXPOSE 8081
CMD [".venv/bin/voice-agent", "start"]
