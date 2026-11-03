"""Create ignored production env files with one shared self-hosted LiveKit key pair."""

from __future__ import annotations

import re
import secrets
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def replace_values(source: str, values: dict[str, str]) -> str:
    for key, value in values.items():
        pattern = rf"(?m)^{re.escape(key)}=.*$"
        if re.search(pattern, source):
            source = re.sub(pattern, f"{key}={value}", source)
        else:
            source += f"\n{key}={value}"
    return source.rstrip() + "\n"


def write_private(path: Path, content: str) -> None:
    with path.open("x", encoding="utf-8") as file:
        file.write(content)
    path.chmod(0o600)


def main() -> int:
    worker_source = ROOT / ".env.dev"
    web_source = ROOT / "src/app/web/.env.local.example"
    targets = [ROOT / ".env.production", ROOT / ".env.livekit", ROOT / "src/app/web/.env.production"]
    if not worker_source.is_file():
        print("Create .env.dev with Groq and Sarvam keys first", file=sys.stderr)
        return 2
    if any(path.exists() for path in targets):
        print("Production env file already exists; edit it directly to preserve deployed keys", file=sys.stderr)
        return 2

    worker_text = worker_source.read_text(encoding="utf-8")
    for name in ("GROQ_API_KEY", "SARVAM_API_KEY"):
        match = re.search(rf"(?m)^{name}=(.+)$", worker_text)
        if not match or not match.group(1).strip():
            print(f"{name} must be set in .env.dev", file=sys.stderr)
            return 2

    key = "yojnapath_" + secrets.token_hex(12)
    secret = secrets.token_hex(32)
    access_code = secrets.token_urlsafe(32)
    worker_text = replace_values(worker_text, {
        "ENVIRONMENT": "production",
        "DEV_SERVER_HOST": "0.0.0.0",
        "LIVEKIT_URL": "ws://livekit-signal.yojnapath.svc.cluster.local:7880",
        "LIVEKIT_API_KEY": key,
        "LIVEKIT_API_SECRET": secret,
        "AGENT_NAME": "yojnapath-web-agent",
    })
    web_text = replace_values(web_source.read_text(encoding="utf-8"), {
        "WEB_CALL_ACCESS_ENABLED": "true",
        "WEB_CALL_ACCESS_CODE": access_code,
        "LIVEKIT_URL": "wss://livekit.yojnapath.asymptotiq.com",
        "LIVEKIT_API_KEY": key,
        "LIVEKIT_API_SECRET": secret,
        "LIVEKIT_AGENT_NAME": "yojnapath-web-agent",
        "NEXT_PUBLIC_SITE_URL": "https://yojnapath.asymptotiq.com",
    })
    write_private(targets[0], worker_text)
    write_private(targets[1], f"LIVEKIT_KEYS={key}: {secret}\n")
    write_private(targets[2], web_text)
    print("Created three ignored production env files; values were not printed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
