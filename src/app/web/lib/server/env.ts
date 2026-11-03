import { z } from "zod";

const booleanFromEnvironment = z.enum(["true", "false"]).transform((value) => value === "true");

const webCallEnvironmentSchema = z.object({
  WEB_CALL_ACCESS_ENABLED: booleanFromEnvironment.default(false),
  WEB_CALL_ACCESS_CODE: z.string().min(12),
  WEB_CALL_MAX_DURATION_SECONDS: z.coerce.number().int().min(60).max(900).default(300),
  WEB_CALL_TOKEN_TTL_SECONDS: z.coerce.number().int().min(30).max(300).default(120),
  LIVEKIT_URL: z.string().url().refine((url) => url.startsWith("wss://") || url.startsWith("ws://")),
  LIVEKIT_INTERNAL_URL: z.string().url().refine((url) => url.startsWith("wss://") || url.startsWith("ws://")).optional(),
  LIVEKIT_API_KEY: z.string().min(1),
  LIVEKIT_API_SECRET: z.string().min(1),
  LIVEKIT_AGENT_NAME: z.string().min(1).default("yojnapath-web-agent"),
});

let cachedEnvironment: z.infer<typeof webCallEnvironmentSchema> | undefined;

export function getWebCallEnvironment(): z.infer<typeof webCallEnvironmentSchema> {
  if (cachedEnvironment) return cachedEnvironment;
  const parsed = webCallEnvironmentSchema.parse(process.env);
  if (!parsed.WEB_CALL_ACCESS_ENABLED) throw new Error("Web calls are disabled.");
  cachedEnvironment = parsed;
  return parsed;
}
