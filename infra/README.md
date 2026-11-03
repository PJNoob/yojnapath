# GCP infrastructure

This folder contains Docker, Terraform, and Helm for three GKE workloads: the Next.js website, self-hosted LiveKit, and the Python voice worker. Terraform creates a one-node zonal GKE Standard cluster, three private Artifact Registry repositories, a global HTTPS address, and a regional LiveKit UDP address.

The website and LiveKit signaling share one GKE HTTPS Ingress with a Google managed certificate. Browser media uses LiveKit's UDP load balancer on port 7882. The worker has a private ClusterIP Service on port 8081 for health checks; it has no public endpoint and connects to the internal LiveKit Service, Groq, and Sarvam. This is a private beta footprint; a single-node interruption stops calls.

## Prerequisites

- A billing-enabled Google Cloud project, billing budget/alerts, permissions to enable APIs and create GKE, IAM, Artifact Registry, and GCS resources.
- `terraform >= 1.12`, Google Cloud CLI, `gke-gcloud-auth-plugin`, `kubectl`, Helm 3, Docker, and Python 3.
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

## Cloudflare DNS and TLS

In the `asymptotiq.com` zone, add A records `yojnapath` and `livekit.yojnapath`, both pointing to `136.81.224.173` (Terraform `https_ip`). Set TTL Auto and **DNS only** (gray cloud). The LiveKit media IP `34.47.174.15` is used directly by WebRTC and needs no DNS record. The Python worker is internal and needs no DNS record. Certificate issuance starts after both names resolve to the Ingress IP.

The web Helm chart's GKE `FrontendConfig` redirects HTTP to HTTPS for both hostnames. Browser microphone access requires a secure page, so use `https://yojnapath.asymptotiq.com/call`. Check the redirect with `curl -I http://yojnapath.asymptotiq.com/call`; it should return `301` with an HTTPS `Location` header.

## Build and release all three services

`.env.dev` must contain working Groq and Sarvam keys. `make prepare-production-env` generates one shared LiveKit API key pair and a private beta access code in three ignored, mode-0600 files. It sets the web server's `LIVEKIT_INTERNAL_URL` to the in-cluster Service and its browser-facing `LIVEKIT_URL` to the public `wss://` hostname. It does not overwrite existing files. Keep production env files out of Git.

```sh
make prepare-production-env
export IMAGE_TAG=$(git rev-parse --short HEAD)
make image-build-livekit image-push-livekit
make image-build-backend image-push-backend
make image-build-frontend image-push-frontend
make k8s-secret-livekit k8s-secret-backend k8s-secret-frontend
make helm-deploy-livekit helm-deploy-backend helm-deploy-frontend
```

Image push requires Artifact Registry Writer permission. Each chart's `values.yaml` contains its Artifact Registry image URL; update the image tag for each release. The worker chart defaults to the already-pushed `683ba9b` tag. Helm uses existing Kubernetes Secrets and starts one replica of each service. The images never copy `.env` files. Rotate the shared LiveKit key in all three Secrets together and restart their Deployments. Restrict Kubernetes Secret access.

Check `kubectl -n yojnapath get pods,svc,ingress,managedcertificate`. Test `https://yojnapath.asymptotiq.com/call` after the certificate becomes Active.

## Cost and operations

The trial credit is finite. GKE node, disk, two load balancers, network egress, and Artifact Registry are billed by Google; Groq and Sarvam are separate. Set a billing budget alert. Scale after measuring active-call CPU and memory. The UDP-only LiveKit media path may fail on networks that block UDP; add TURN/TCP fallback before a broad launch.
