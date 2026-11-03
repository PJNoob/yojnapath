# YojnaPath architecture

YojnaPath uses the Companio live voice infrastructure with a scheme-guidance prompt and a browser-first website. The active product path is the web call; old Telegram web routes and the earlier Twilio prototype are not part of this repository's running site.

## Browser to agent flow

```mermaid
sequenceDiagram
    participant Browser
    participant Next as Next.js token API
    participant LiveKit
    participant Worker as Python agent worker
    participant Providers as STT / LLM / TTS providers
    Browser->>Next: POST /api/web-call/session with beta code
    Next->>Next: Validate code and throttle attempts
    Next->>LiveKit: Dispatch yojnapath-web-agent to a new room
    Next-->>Browser: Short-lived, microphone-only room token
    Browser->>LiveKit: Join room and publish microphone
    LiveKit->>Worker: Agent job and audio
    Worker->>Providers: Transcribe, respond, synthesize
    Providers-->>Worker: Spoken response
    Worker->>LiveKit: Publish response audio
    LiveKit-->>Browser: Play response
```

`src/app/web/app/api/web-call/session/route.ts` handles code validation, room creation, dispatch, and token issuance. `src/app/web/features/call/use-web-call.ts` joins LiveKit, publishes the microphone, plays the agent audio, and handles mute and hang-up. The page is `src/app/web/app/call/page.tsx` with the light call UI in `features/call/call-screen.tsx`.

`src/voice_agent/main.py` registers the Python worker under `AGENT_NAME`. `session.py`, `stt_providers.py`, and `providers.py` construct the LiveKit audio pipeline. `promptmanger.py` directs the Hindi/Hinglish scheme conversation. `call_context.py` validates dispatch metadata and enforces a maximum session duration. Optional Langfuse tracing is in `telemetry.py`.

For local development, `compose.yaml` runs LiveKit on localhost. Production runs a single LiveKit pod in GKE. The worker and Next.js server call its internal `livekit-signal` Service; browsers use `wss://livekit.yojnapath.asymptotiq.com` for signaling and a dedicated public UDP address for WebRTC media. The worker uses local Silero VAD and provider plugins, with no LiveKit Cloud inference dependency.

## Conversation behavior

The agent follows a flexible call path: greet, understand whether the caller has a specific scheme or broad need, ask one clarifying question, explain general next steps, and close when the caller is done. This is **prompt guidance**, not a persisted stage graph. The worker has no scheme retrieval tool or current government data. The prompt prohibits fabricated scheme facts and asks callers to verify eligibility, deadlines, documents, and application steps with official sources.

## Trust boundaries

- The browser never receives LiveKit API secrets, provider keys, or the stored beta access code. It receives only a room-scoped participant token.
- Next.js holds the LiveKit API credentials and checks the beta code. The current rate limiter is in memory per server process and is only appropriate for a small private beta.
- The worker holds STT, LLM, TTS, and optional telemetry credentials. It connects outbound to LiveKit and providers; no browser-to-worker ingress is needed.
- The worker enforces duration from server-created dispatch metadata. Client-side timers are only a user-interface convenience.

## Deployment boundary

Deploy all three images to Artifact Registry and three Helm releases to the one-node GKE cluster. A Google Cloud Ingress with a managed certificate routes the website and LiveKit signaling by hostname through one global IP. A regional UDP load balancer exposes LiveKit media. The Python worker has no public endpoint. All three components share one LiveKit API key pair through separate Kubernetes Secrets. Match `LIVEKIT_AGENT_NAME` to worker `AGENT_NAME`. The single node is a beta footprint: its failure interrupts calls, and some networks that block UDP cannot establish media until TURN/TCP fallback is added. [infra/README.md](infra/README.md) has commands and [DEPLOYMENT_GKE.md](DEPLOYMENT_GKE.md) has rollout checks.

## Before public use

Add a maintained and cited scheme data source, an identity/entitlement flow, a shared rate limit, durable per-call records, a verified LiveKit completion webhook, reviewed privacy terms, and production observability. The old optional SIP/telephony module can be removed after the browser-only path is stable.
