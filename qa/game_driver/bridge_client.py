"""Small dependency-free client for the local Love2D QA bridge."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib.request import Request, urlopen


def load_config(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def call(config: dict, endpoint: str, method: str = "GET", payload=None):
    url = f"http://{config['host']}:{config['port']}{endpoint}"
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = Request(url, data=data, method=method)
    request.add_header("Authorization", f"Bearer {config['token']}")
    if data:
        request.add_header("Content-Type", "application/json")
    with urlopen(request, timeout=5) as response:
        content_type = response.headers.get("Content-Type", "")
        body = response.read()
        if content_type.startswith("image/"):
            return body
        return json.loads(body)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path, help="run-folder bridge.json")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("status")
    subparsers.add_parser("snapshot")
    events = subparsers.add_parser("events")
    events.add_argument("--after", type=int, default=0)
    results = subparsers.add_parser("results")
    results.add_argument("--after", type=int, default=0)
    screenshot = subparsers.add_parser("screenshot")
    screenshot.add_argument("--output", type=Path)
    send = subparsers.add_parser("send")
    send.add_argument("command_json", help="JSON command object or array")
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
        if args.command == "status":
            value = call(config, "/v1/status")
        elif args.command == "snapshot":
            value = call(config, "/v1/snapshot")
        elif args.command == "events":
            value = call(config, f"/v1/events?after={args.after}")
        elif args.command == "results":
            value = call(config, f"/v1/results?after={args.after}")
        elif args.command == "screenshot":
            output = args.output or (args.config.parent / "screenshots" / "bridge_latest.png")
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(call(config, "/v1/screenshots/latest"))
            value = {"saved": str(output)}
        else:
            value = call(config, "/v1/commands", "POST", json.loads(args.command_json))
        print(json.dumps(value, indent=2, ensure_ascii=False) if not isinstance(value, bytes) else "screenshot saved")
        return 0
    except Exception as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
