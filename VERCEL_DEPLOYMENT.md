# YojnaPath web deployment

Deploy the Next.js project from `src/app/web` to Vercel. The Python voice worker runs separately on GKE and connects to the same LiveKit project. Follow [MIGRATION_VERCEL_GKE.md](MIGRATION_VERCEL_GKE.md) for the full release order and required checks.

The workflow in `.github/workflows/vercel.yml` can verify and deploy the web app manually after Vercel project secrets are configured. A successful web deployment alone does not make calls work; the LiveKit worker and provider credentials must also be running.
