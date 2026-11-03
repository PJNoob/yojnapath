import { createHash, randomUUID, timingSafeEqual } from "node:crypto";
import { NextRequest, NextResponse } from "next/server";
import { AccessToken, LiveKitAPI, TrackSource } from "livekit-server-sdk";
import { z } from "zod";
import { getWebCallEnvironment } from "@/lib/server/env";
import { isRateLimited } from "@/lib/server/rate-limit";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const requestSchema = z.object({ accessCode: z.string().min(1).max(256) });

function reply(error: string, status: number) {
  return NextResponse.json({ error }, { status, headers: { "Cache-Control": "no-store" } });
}

function matchesAccessCode(provided: string, expected: string): boolean {
  const providedHash = createHash("sha256").update(provided).digest();
  const expectedHash = createHash("sha256").update(expected).digest();
  return timingSafeEqual(providedHash, expectedHash);
}

export async function POST(request: NextRequest) {
  const clientAddress = request.headers.get("x-forwarded-for")?.split(",")[0]?.trim() ?? "unknown";
  const addressHash = createHash("sha256").update(clientAddress).digest("hex");
  if (isRateLimited(`web-call:${addressHash}`, 5, 60_000)) return reply("Too many call attempts. Please wait a minute.", 429);

  const parsed = requestSchema.safeParse(await request.json().catch(() => null));
  if (!parsed.success) return reply("Enter your access code to start a call.", 400);

  try {
    const environment = getWebCallEnvironment();
    if (!matchesAccessCode(parsed.data.accessCode, environment.WEB_CALL_ACCESS_CODE)) {
      return reply("That access code is not valid.", 403);
    }

    const sessionId = randomUUID();
    const roomName = `web-${sessionId}`;
    const metadata = JSON.stringify({
      call_session_id: sessionId,
      access_mode: "web",
      max_duration_seconds: environment.WEB_CALL_MAX_DURATION_SECONDS,
    });
    const livekit = new LiveKitAPI({
      host: environment.LIVEKIT_INTERNAL_URL ?? environment.LIVEKIT_URL,
      apiKey: environment.LIVEKIT_API_KEY,
      secret: environment.LIVEKIT_API_SECRET,
    });
    await livekit.agentDispatch.createDispatch(roomName, environment.LIVEKIT_AGENT_NAME, { metadata });

    const token = new AccessToken(environment.LIVEKIT_API_KEY, environment.LIVEKIT_API_SECRET, {
      identity: `web-visitor-${sessionId}`,
      ttl: environment.WEB_CALL_TOKEN_TTL_SECONDS,
      metadata,
    });
    token.addGrant({
      roomJoin: true,
      room: roomName,
      canPublish: true,
      canSubscribe: true,
      canPublishData: false,
      canPublishSources: [TrackSource.MICROPHONE],
    });

    return NextResponse.json({
      livekitUrl: environment.LIVEKIT_URL,
      participantToken: await token.toJwt(),
      maxDurationSeconds: environment.WEB_CALL_MAX_DURATION_SECONDS,
    }, { headers: { "Cache-Control": "no-store" } });
  } catch (error) {
    console.error("Unable to issue web call token", error);
    return reply("The call service is temporarily unavailable.", 503);
  }
}
