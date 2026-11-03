.PHONY: install run-dev check

install:
	uv sync --extra dev
	npm ci --prefix src/app/web

run-dev:
	uv run voice-agent dev & \
	agent_pid=$$!; \
	trap 'kill $$agent_pid 2>/dev/null || true; wait $$agent_pid 2>/dev/null || true' EXIT INT TERM; \
	npm run dev --prefix src/app/web

check:
	uv run pytest
	uv run ruff check .
	npm run lint --prefix src/app/web
	npm run typecheck --prefix src/app/web
