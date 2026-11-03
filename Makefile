.PHONY: install build dev run check frontend backend \
	install-frontend install-backend build-frontend build-backend \
	dev-frontend dev-backend run-frontend run-backend run-both \
	livekit-up livekit-down livekit-logs

.PHONY: tf-bootstrap tf-init tf-validate tf-plan tf-deploy \
	image-build image-push image-build-frontend image-build-backend image-build-livekit \
	image-push-frontend image-push-backend image-push-livekit \
	kube-context k8s-secret k8s-secret-frontend k8s-secret-backend k8s-secret-livekit \
	deploy-backend helm-deploy-frontend helm-deploy-backend helm-deploy-livekit \
	prepare-production-env

GCP_PROJECT_ID ?=
GCP_REGION ?= asia-south1
GCP_ZONE ?= asia-south1-a
ENVIRONMENT ?= dev
TF_STATE_BUCKET ?= $(GCP_PROJECT_ID)-yojnapath-terraform-state
TF_PREFIX ?= yojnapath/$(ENVIRONMENT)/gke
TF_BOOTSTRAP_DIR := infra/terraform/bootstrap
TF_GKE_DIR := infra/terraform/gke
IMAGE_TAG ?= dev
VOICE_REPOSITORY := $(GCP_REGION)-docker.pkg.dev/$(GCP_PROJECT_ID)/yojnapath-$(ENVIRONMENT)-voice-agent/voice-agent
WEB_REPOSITORY := $(GCP_REGION)-docker.pkg.dev/$(GCP_PROJECT_ID)/yojnapath-$(ENVIRONMENT)-web/web
LIVEKIT_REPOSITORY := $(GCP_REGION)-docker.pkg.dev/$(GCP_PROJECT_ID)/yojnapath-$(ENVIRONMENT)-livekit/livekit
WEB_HOST ?= yojnapath.asymptotiq.com
LIVEKIT_HOST ?= livekit.yojnapath.asymptotiq.com
HTTPS_IP_NAME ?= yojnapath-$(ENVIRONMENT)-https
MEDIA_IP ?= $(shell terraform -chdir=$(TF_GKE_DIR) output -raw livekit_media_ip 2>/dev/null)
WORKER_ENV_FILE ?= .env.production
WEB_ENV_FILE ?= src/app/web/.env.production
LIVEKIT_KEYS_FILE ?= .env.livekit
K8S_NAMESPACE ?= yojnapath
K8S_SECRET ?= yojnapath-worker-env

prepare-production-env:
	python3 infra/scripts/prepare-production-env.py

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

dev-backend: run-backend

dev-frontend:
	npm run dev --prefix $(WEB_DIR)

run:
	@case "$(SERVICE)" in \
		frontend) $(MAKE) run-frontend ;; \
		backend) $(MAKE) run-backend ;; \
		"") $(MAKE) run-both ;; \
		*) echo "Choose one service: frontend or backend" >&2; exit 2 ;; \
	esac

run-both: livekit-up
	@uv run voice-agent start & \
	agent_pid=$$!; \
	trap 'kill $$agent_pid 2>/dev/null || true; wait $$agent_pid 2>/dev/null || true' EXIT INT TERM; \
	npm run dev --prefix $(WEB_DIR)

run-backend: livekit-up
	uv run voice-agent start

run-frontend: dev-frontend

livekit-up:
	docker compose up -d livekit

livekit-down:
	docker compose down

livekit-logs:
	docker compose logs -f livekit

check:
	uv run pytest
	uv run ruff check .
	npm run lint --prefix $(WEB_DIR)
	npm run typecheck --prefix $(WEB_DIR)

# Create the versioned GCS backend once. Bootstrap retains local state: back it up securely.
tf-bootstrap:
	@test -n "$(GCP_PROJECT_ID)" || { echo "Set GCP_PROJECT_ID" >&2; exit 2; }
	terraform -chdir=$(TF_BOOTSTRAP_DIR) init -input=false
	terraform -chdir=$(TF_BOOTSTRAP_DIR) apply -var="project_id=$(GCP_PROJECT_ID)" -var="region=$(GCP_REGION)" -var="state_bucket=$(TF_STATE_BUCKET)"

tf-init:
	@test -n "$(GCP_PROJECT_ID)" || { echo "Set GCP_PROJECT_ID" >&2; exit 2; }
	terraform -chdir=$(TF_GKE_DIR) init -input=false -reconfigure -backend-config="bucket=$(TF_STATE_BUCKET)" -backend-config="prefix=$(TF_PREFIX)"

tf-validate:
	terraform -chdir=$(TF_GKE_DIR) init -backend=false -input=false
	terraform -chdir=$(TF_GKE_DIR) validate

tf-plan: tf-init
	terraform -chdir=$(TF_GKE_DIR) plan -var="project_id=$(GCP_PROJECT_ID)" -var="region=$(GCP_REGION)" -var="zone=$(GCP_ZONE)" -var="environment=$(ENVIRONMENT)"

tf-deploy: tf-init
	terraform -chdir=$(TF_GKE_DIR) apply -var="project_id=$(GCP_PROJECT_ID)" -var="region=$(GCP_REGION)" -var="zone=$(GCP_ZONE)" -var="environment=$(ENVIRONMENT)"

image-build:
	@test -n "$(GCP_PROJECT_ID)" || { echo "Set GCP_PROJECT_ID" >&2; exit 2; }
	docker buildx build --platform linux/amd64 --load -f infra/docker/voice-agent/Dockerfile -t $(VOICE_REPOSITORY):$(IMAGE_TAG) .

image-build-backend: image-build

image-build-frontend:
	@test -n "$(GCP_PROJECT_ID)" || { echo "Set GCP_PROJECT_ID" >&2; exit 2; }
	docker buildx build --platform linux/amd64 --load -f infra/docker/web/Dockerfile \
		--build-arg NEXT_PUBLIC_SITE_URL=https://$(WEB_HOST) -t $(WEB_REPOSITORY):$(IMAGE_TAG) .

image-build-livekit:
	@test -n "$(GCP_PROJECT_ID)" || { echo "Set GCP_PROJECT_ID" >&2; exit 2; }
	docker buildx build --platform linux/amd64 --load -f infra/docker/livekit/Dockerfile \
		-t $(LIVEKIT_REPOSITORY):$(IMAGE_TAG) .

image-push:
	@test -n "$(GCP_PROJECT_ID)" || { echo "Set GCP_PROJECT_ID" >&2; exit 2; }
	gcloud auth configure-docker $(GCP_REGION)-docker.pkg.dev --quiet
	docker push $(VOICE_REPOSITORY):$(IMAGE_TAG)

image-push-backend: image-push

image-push-frontend:
	@test -n "$(GCP_PROJECT_ID)" || { echo "Set GCP_PROJECT_ID" >&2; exit 2; }
	gcloud auth configure-docker $(GCP_REGION)-docker.pkg.dev --quiet
	docker push $(WEB_REPOSITORY):$(IMAGE_TAG)

image-push-livekit:
	@test -n "$(GCP_PROJECT_ID)" || { echo "Set GCP_PROJECT_ID" >&2; exit 2; }
	gcloud auth configure-docker $(GCP_REGION)-docker.pkg.dev --quiet
	docker push $(LIVEKIT_REPOSITORY):$(IMAGE_TAG)

kube-context:
	@test -n "$(GCP_PROJECT_ID)" || { echo "Set GCP_PROJECT_ID" >&2; exit 2; }
	gcloud container clusters get-credentials yojnapath-$(ENVIRONMENT)-gke --zone $(GCP_ZONE) --project $(GCP_PROJECT_ID)

k8s-secret: kube-context
	@test -f "$(WORKER_ENV_FILE)" || { echo "Create $(WORKER_ENV_FILE) from .env.dev.example with production values" >&2; exit 2; }
	kubectl create namespace $(K8S_NAMESPACE) --dry-run=client -o yaml | kubectl apply -f -
	kubectl -n $(K8S_NAMESPACE) create secret generic $(K8S_SECRET) --from-env-file=$(WORKER_ENV_FILE) --dry-run=client -o yaml | kubectl apply -f -

k8s-secret-backend: k8s-secret

k8s-secret-frontend: kube-context
	@test -f "$(WEB_ENV_FILE)" || { echo "Create $(WEB_ENV_FILE) with production web values" >&2; exit 2; }
	kubectl create namespace $(K8S_NAMESPACE) --dry-run=client -o yaml | kubectl apply -f -
	kubectl -n $(K8S_NAMESPACE) create secret generic yojnapath-web-env --from-env-file=$(WEB_ENV_FILE) --dry-run=client -o yaml | kubectl apply -f -

k8s-secret-livekit: kube-context
	@test -f "$(LIVEKIT_KEYS_FILE)" || { echo "Create $(LIVEKIT_KEYS_FILE) with LIVEKIT_KEYS=key: secret" >&2; exit 2; }
	kubectl create namespace $(K8S_NAMESPACE) --dry-run=client -o yaml | kubectl apply -f -
	kubectl -n $(K8S_NAMESPACE) create secret generic yojnapath-livekit-keys --from-env-file=$(LIVEKIT_KEYS_FILE) --dry-run=client -o yaml | kubectl apply -f -

deploy-backend: kube-context
	@kubectl -n $(K8S_NAMESPACE) get secret $(K8S_SECRET) >/dev/null || { echo "Run make k8s-secret first" >&2; exit 2; }
	helm upgrade --install voice-agent infra/helm/voice-agent --namespace $(K8S_NAMESPACE) --wait --timeout 10m \
		--set-string image.repository=$(VOICE_REPOSITORY) --set-string image.tag=$(IMAGE_TAG) \
		--set-string existingSecret=$(K8S_SECRET)

helm-deploy-backend: deploy-backend

helm-deploy-livekit: kube-context
	@test -n "$(MEDIA_IP)" || { echo "Run make tf-deploy first to reserve the media IP" >&2; exit 2; }
	@kubectl -n $(K8S_NAMESPACE) get secret yojnapath-livekit-keys >/dev/null || { echo "Run make k8s-secret-livekit first" >&2; exit 2; }
	helm upgrade --install livekit infra/helm/livekit --namespace $(K8S_NAMESPACE) --wait --timeout 10m \
		--set-string image.repository=$(LIVEKIT_REPOSITORY) --set-string image.tag=$(IMAGE_TAG) \
		--set-string mediaIP=$(MEDIA_IP)

helm-deploy-frontend: kube-context
	@kubectl -n $(K8S_NAMESPACE) get secret yojnapath-web-env >/dev/null || { echo "Run make k8s-secret-frontend first" >&2; exit 2; }
	helm upgrade --install web infra/helm/web --namespace $(K8S_NAMESPACE) --wait --timeout 10m \
		--set-string image.repository=$(WEB_REPOSITORY) --set-string image.tag=$(IMAGE_TAG) \
		--set-string webHost=$(WEB_HOST) --set-string livekitHost=$(LIVEKIT_HOST) \
		--set-string httpsIPName=$(HTTPS_IP_NAME)
