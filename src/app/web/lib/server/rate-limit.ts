type RateLimit = { count: number; resetAt: number };
const limits = new Map<string, RateLimit>();

export function isRateLimited(key: string, limit = 10, windowMilliseconds = 60_000): boolean {
  const now = Date.now();
  const current = limits.get(key);
  if (!current || current.resetAt <= now) {
    limits.set(key, { count: 1, resetAt: now + windowMilliseconds });
    return false;
  }
  current.count += 1;
  return current.count > limit;
}
