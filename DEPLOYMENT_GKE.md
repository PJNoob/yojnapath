# Single-cluster GKE rollout plan

YojnaPath hosts the Next.js site, self-hosted LiveKit, and the Python worker in GKE. The browser call needs no telephone provider. The site uses `https://yojnapath.asymptotiq.com`; LiveKit signaling uses `wss://livekit.yojnapath.asymptotiq.com`.

1. Reserve the HTTPS and LiveKit UDP addresses with Terraform. Add the two DNS-only Cloudflare A records in [infra/README.md](infra/README.md).
2. Generate ignored production environment files, build and push all three images to Artifact Registry, apply the three Kubernetes Secrets, and install the LiveKit, worker, and web Helm releases in that order.
3. Wait for the GKE Ingress and UDP LoadBalancer to become healthy and the Google managed certificate to become Active. Confirm the browser receives no API or provider secrets.
4. Test invalid and valid beta codes, microphone permission, two-way audio, mute, hang-up, duration enforcement, worker restart, and provider failure. Test from outside GKE on a network that permits UDP.
5. Configure a Google Cloud billing budget. Monitor node, disk, load balancer, egress, and Artifact Registry charges. Groq and Sarvam are separate from Google Cloud credits. Keep previous image tags for rollback.
6. Before open public use, replace the shared beta code with identity, shared rate limiting, durable call records, verified webhook completion, reviewed privacy terms, and a maintained scheme data source. Add TURN/TCP fallback for UDP-blocked networks and more than one node for availability.

This initial cluster has one `e2-standard-2` node and one pod per service. A node failure interrupts calls, and the setup has limited concurrent-call capacity.
