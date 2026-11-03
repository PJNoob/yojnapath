# GCP infrastructure

This folder follows the AWS `infra-code` project's separation of Docker, Terraform, and Helm, adapted to YojnaPath's Vercel website and outbound LiveKit worker. Terraform creates a single-zone GKE Standard cluster with one `e2-standard-2` node, a custom VPC/subnet, a dedicated node service account, and two private Artifact Registry Docker repositories (`voice-agent` and `web`). The web repository is available if hosting changes later; the current site stays on Vercel. No public load balancer, NAT gateway, database, or extra VM is created.

The worker connects outbound to LiveKit Cloud, Groq, and Sarvam. Browser audio goes directly to LiveKit Cloud; no telephony or GKE ingress is needed. The GKE node has an external IP for outbound traffic. This is a low-resource private beta footprint, not a high-availability setup. A single-zone/node interruption can stop calls.

## Prerequisites

- A billing-enabled Google Cloud project, billing budget/alerts, permissions to enable APIs and create GKE, IAM, Artifact Registry, and GCS resources.
- `terraform >= 1.12`, Google Cloud CLI, `kubectl`, Helm 3, Docker, and a LiveKit Cloud project.
- Authenticate with `gcloud auth login` and `gcloud auth application-default login`; set `GCP_PROJECT_ID` to the real project ID. Use the same Google identity for Terraform and `gcloud`.
- Bootstrap needs `serviceusage.googleapis.com` enabled in the project. Enable it once in the Cloud console or with `gcloud services enable serviceusage.googleapis.com --project "$GCP_PROJECT_ID"`.

## Provision

Run from the repository root. The default location is `asia-south1` / `asia-south1-a`; change `GCP_REGION` and `GCP_ZONE` together if needed. GCS bucket names are globally unique, so override `TF_STATE_BUCKET` if the default is taken.

```sh
export GCP_PROJECT_ID=your-real-project-id
make tf-bootstrap
make tf-plan
make tf-deploy
```

`tf-bootstrap` creates a versioned, private GCS Terraform state bucket using local bootstrap state. Keep `infra/terraform/bootstrap/terraform.tfstate` in secure backup; it is Git-ignored. `tf-plan` initializes the GCS backend and previews resources. `tf-deploy` asks Terraform for interactive approval before creating billable resources. `make tf-validate` runs static Terraform validation. The main state is under `yojnapath/dev/gke` in the bucket. GCS state locking is handled by Terraform's GCS backend.

## Build and release the worker

Create a production worker environment file from `.env.dev.example` and replace at least `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`, `GROQ_API_KEY`, and `SARVAM_API_KEY`. Set `LIVEKIT_URL` to the hosted `wss://` URL, `ENVIRONMENT=production`, `DEV_SERVER_HOST=0.0.0.0`, and keep `AGENT_NAME=yojnapath-web-agent` aligned with Vercel's `LIVEKIT_AGENT_NAME`. Use `WORKER_ENV_FILE` to point to the file. Do not put the local `devkey`/`secret`, localhost URL, or live secrets into Git. `.env.production` is ignored.

```sh
export IMAGE_TAG=$(git rev-parse --short HEAD)
make image-build image-push
make k8s-secret WORKER_ENV_FILE=.env.production
make deploy-backend
```

`image-push` requires Artifact Registry Writer permission for your Google identity. `k8s-secret` creates a Kubernetes Secret in the `yojnapath` namespace from the production file. Helm uses the existing Secret and starts one worker replica. The container image never copies `.env` files. The worker has no Kubernetes Service or Ingress. Rotate provider and LiveKit keys in both the worker Secret and Vercel as applicable, then restart the Deployment. Kubernetes Secrets are stored in cluster state; limit cluster access and enable GKE secret encryption policies if required for your deployment.

For the website, deploy `src/app/web` on Vercel and set its server-side LiveKit credentials, access code, and site origin as described in [the rollout plan](../MIGRATION_VERCEL_GKE.md).

## Cost and operations

The zonal cluster may qualify for Google's monthly GKE management-fee credit, but the node VM, disk, network egress, Artifact Registry storage, and external voice providers are billed separately. The $300 trial credit is finite. Review the region-specific estimate in the Google Cloud Pricing Calculator before applying and use a billing budget alert. The node is on demand so a conversation is less likely to be interrupted than on a Spot VM. Scale only after measuring active-call CPU and memory. Use `kubectl -n yojnapath logs deploy/voice-agent` and `kubectl -n yojnapath rollout status deploy/voice-agent` for health checks.
