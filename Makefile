.PHONY: install build dev run check

WEB_DIR := src/app/web

install:
	uv sync --locked --extra dev
	npm ci --prefix $(WEB_DIR)

build:
	uv build
	npm run build --prefix $(WEB_DIR)

# Start the LiveKit worker and Next.js together for local development.
dev:
	@uv run voice-agent dev & \
	agent_pid=$$!; \
	trap 'kill $$agent_pid 2>/dev/null || true; wait $$agent_pid 2>/dev/null || true' EXIT INT TERM; \
	npm run dev --prefix $(WEB_DIR)

# Run the built website and worker locally with production commands.
run:
	@uv run voice-agent start & \
	agent_pid=$$!; \
	trap 'kill $$agent_pid 2>/dev/null || true; wait $$agent_pid 2>/dev/null || true' EXIT INT TERM; \
	npm run start --prefix $(WEB_DIR)

check:
	uv run pytest
	uv run ruff check .
	npm run lint --prefix $(WEB_DIR)
	npm run typecheck --prefix $(WEB_DIR)
