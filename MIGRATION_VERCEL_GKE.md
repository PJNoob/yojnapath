# Vercel and GKE rollout plan

The first release uses Vercel for the Next.js website, GKE for one persistent LiveKit agent worker, and LiveKit Cloud for browser audio. The website does not use a telephone number, Telegram, or a database for the private beta call path.

1. **Provision LiveKit and providers.** Create or use one LiveKit project. Configure Groq Qwen 3.8 for the LLM and Sarvam Saaras/Bulbul for STT/TTS. Keep `GROQ_API_KEY` and `SARVAM_API_KEY` only on the worker, and LiveKit credentials in the required server-side stores.
2. **Build and deploy the worker.** Package the Python project into a pinned container image, create a GKE Autopilot Deployment, and start `voice-agent start` with `AGENT_NAME=yojnapath-web-agent`. Start with one replica; measure per-call CPU/memory before scaling. Give active sessions a graceful drain window during rollouts. No public ingress is required for the worker's media path.
3. **Deploy the web app.** In Vercel set the project root to `src/app/web`. Set `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`, `LIVEKIT_AGENT_NAME`, `WEB_CALL_ACCESS_ENABLED=true`, a long random `WEB_CALL_ACCESS_CODE`, and the duration/TTL values as server-side variables. Set `NEXT_PUBLIC_SITE_URL` to the production HTTPS origin. Do not expose secrets through `NEXT_PUBLIC_` variables.
4. **Verify the end-to-end call.** Test invalid and valid beta codes, microphone denial, microphone publish, two-way audio, mute, hang-up, duration enforcement, worker restart/drain, and an unavailable provider. Correlate the room/session ID in Vercel, LiveKit, and GKE logs.
5. **Set budgets and rollback.** Configure Google Cloud billing alerts and track LiveKit/STT/LLM/TTS costs separately. Keep the previous Vercel deployment and worker image. Disable `WEB_CALL_ACCESS_ENABLED` if call issuance must be stopped.
6. **Public launch gate.** Replace the shared beta code with user identity and entitlements, add durable rate limiting and call records, verify completion with a LiveKit webhook, connect a maintained scheme catalog, and publish reviewed privacy/terms information.

The $300 Google Cloud credit, if eligible for this project, does not pay Vercel or external voice-provider bills. Vercel's Hobby plan is for non-commercial personal use; a commercial launch needs an eligible paid plan. Hosting both services in GKE is possible but requires a second container, public HTTPS ingress, and more operations. The split setup is simpler for the first beta.

References: [GKE pricing](https://cloud.google.com/kubernetes-engine/pricing), [GKE Autopilot](https://docs.cloud.google.com/kubernetes-engine/docs/concepts/autopilot-overview), [Vercel Hobby](https://vercel.com/docs/plans/hobby), [LiveKit worker lifecycle](https://docs.livekit.io/agents/server/lifecycle/).
