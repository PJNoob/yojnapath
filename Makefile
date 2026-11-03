.PHONY: install build dev run check frontend backend \
	install-frontend install-backend build-frontend build-backend \
	dev-frontend dev-backend run-frontend run-backend run-both

WEB_DIR := src/app/web
SERVICE := $(filter frontend backend,$(MAKECMDGOALS))

# Allow `make install frontend` and `make run backend` as short forms.
frontend backend:
	@:

install:
	@case "$(SERVICE)" in \
		frontend) $(MAKE) install-frontend ;; \
		backend) $(MAKE) install-backend ;; \
		"") $(MAKE) install-backend install-frontend ;; \
		*) echo "Choose one service: frontend or backend" >&2; exit 2 ;; \
	esac

install-backend:
	uv sync --locked --extra dev

install-frontend:
	npm ci --prefix $(WEB_DIR)

build:
	@case "$(SERVICE)" in \
		frontend) $(MAKE) build-frontend ;; \
		backend) $(MAKE) build-backend ;; \
		"") $(MAKE) build-backend build-frontend ;; \
		*) echo "Choose one service: frontend or backend" >&2; exit 2 ;; \
	esac

build-backend:
	uv build

build-frontend:
	npm run build --prefix $(WEB_DIR)

# Start the LiveKit worker and Next.js together for local development.
dev:
	@case "$(SERVICE)" in \
		frontend) $(MAKE) dev-frontend ;; \
		backend) $(MAKE) dev-backend ;; \
		"") $(MAKE) run-both ;; \
		*) echo "Choose one service: frontend or backend" >&2; exit 2 ;; \
	esac

dev-backend:
	uv run voice-agent dev

dev-frontend:
	npm run dev --prefix $(WEB_DIR)

run:
	@case "$(SERVICE)" in \
		frontend) $(MAKE) run-frontend ;; \
		backend) $(MAKE) run-backend ;; \
		"") $(MAKE) run-both ;; \
		*) echo "Choose one service: frontend or backend" >&2; exit 2 ;; \
	esac

run-both:
	@uv run voice-agent dev & \
	agent_pid=$$!; \
	trap 'kill $$agent_pid 2>/dev/null || true; wait $$agent_pid 2>/dev/null || true' EXIT INT TERM; \
	npm run dev --prefix $(WEB_DIR)

run-backend: dev-backend

run-frontend: dev-frontend

check:
	uv run pytest
	uv run ruff check .
	npm run lint --prefix $(WEB_DIR)
	npm run typecheck --prefix $(WEB_DIR)
