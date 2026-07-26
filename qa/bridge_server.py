"""Local HTTP adapter for a running Love2D QA session.

The server is intentionally localhost-only. It exposes the existing file bridge
without adding a second runtime or a new gameplay protocol.
"""

from __future__ import annotations

import argparse
import json
import os
import secrets
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
LOG_ROOT = ROOT / "qa" / "runtime_logs"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from qa.game_driver.protocol import ProtocolError, validate_commands
from qa.game_driver.session import SCHEMA_VERSION, append_jsonl, read_latest, write_json_atomic


class BridgeError(RuntimeError):
    pass


def read_object(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def resolve_run(run_id: str | None, log_root: Path = LOG_ROOT) -> Path:
    if run_id:
        run_dir = log_root / run_id
    else:
        active = read_object(log_root / "active.json") or {}
        run_dir = log_root / str(active.get("run_id", ""))
    if run_dir.resolve().parent != log_root.resolve() or not run_dir.is_dir():
        raise BridgeError("No active QA run was found")
    return run_dir


def ensure_bridge_config(run_dir: Path) -> dict[str, Any]:
    path = run_dir / "bridge.json"
    config = read_object(path) or {}
    if not config.get("token"):
        config = {
            "schema_version": SCHEMA_VERSION,
            "run_id": run_dir.name,
            "host": "127.0.0.1",
            "token": secrets.token_urlsafe(32),
        }
        write_json_atomic(path, config)
    return config


def read_jsonl_after(path: Path, after: int = 0) -> tuple[list[dict[str, Any]], int, list[str]]:
    records: list[dict[str, Any]] = []
    errors: list[str] = []
    offset = max(0, int(after))
    if not path.exists():
        return records, offset, errors
    with path.open("r", encoding="utf-8") as handle:
        handle.seek(offset)
        while True:
            line = handle.readline()
            if not line:
                break
            offset = handle.tell()
            if line.strip():
                try:
                    value = json.loads(line)
                except json.JSONDecodeError:
                    errors.append(f"invalid JSON at byte offset {offset}")
                    continue
                if isinstance(value, dict):
                    records.append(value)
    return records, offset, errors


def latest_file(directory: Path, pattern: str) -> Path | None:
    files = sorted(directory.glob(pattern), key=lambda path: path.stat().st_mtime_ns if path.exists() else 0)
    return files[-1] if files else None


class BridgeHandler(BaseHTTPRequestHandler):
    server_version = "Love2D-QA-Bridge/1"

    @property
    def bridge(self) -> "BridgeHTTPServer":
        return self.server  # type: ignore[return-value]

    def log_message(self, _format: str, *_args: Any) -> None:
        return

    def authorized(self) -> bool:
        token = self.headers.get("Authorization", "")
        if token.startswith("Bearer "):
            token = token[7:]
        token = token or self.headers.get("X-QA-Token", "")
        return secrets.compare_digest(token, self.bridge.token)

    def send_json(self, status: int, value: Any) -> None:
        data = json.dumps(value, ensure_ascii=False, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        if not self.authorized():
            self.send_json(401, {"error": "missing or invalid QA bridge token"})
            return
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        try:
            if parsed.path == "/v1/status":
                self.send_json(200, self.bridge.status())
            elif parsed.path in {"/v1/snapshot", "/v1/snapshots/latest"}:
                path = latest_file(self.bridge.run_dir / "snapshots", "*.json")
                if not path:
                    self.send_json(404, {"error": "no snapshot available"})
                else:
                    self.send_json(200, {"path": str(path), "snapshot": read_object(path)})
            elif parsed.path in {"/v1/events", "/v1/results"}:
                filename = parsed.path.rsplit("/", 1)[-1] + ".jsonl"
                records, next_cursor, errors = read_jsonl_after(self.bridge.run_dir / filename, int(query.get("after", [0])[0]))
                self.send_json(200, {"run_id": self.bridge.run_dir.name, "records": records, "next": next_cursor, "errors": errors})
            elif parsed.path in {"/v1/screenshots/latest", "/v1/screenshot"}:
                path = latest_file(self.bridge.run_dir / "screenshots", "*.png")
                if not path:
                    self.send_json(404, {"error": "no screenshot available"})
                else:
                    data = path.read_bytes()
                    self.send_response(200)
                    self.send_header("Content-Type", "image/png")
                    self.send_header("Content-Length", str(len(data)))
                    self.send_header("X-QA-Path", str(path))
                    self.end_headers()
                    self.wfile.write(data)
            else:
                self.send_json(404, {"error": "unknown endpoint"})
        except (ValueError, OSError) as error:
            self.send_json(400, {"error": str(error)})

    def do_POST(self) -> None:
        if not self.authorized():
            self.send_json(401, {"error": "missing or invalid QA bridge token"})
            return
        if urlparse(self.path).path != "/v1/commands":
            self.send_json(404, {"error": "unknown endpoint"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length) or b"null")
            commands = payload if isinstance(payload, list) else [payload]
            commands = validate_commands(commands)
            existing, _, _ = read_jsonl_after(self.bridge.run_dir / "commands.jsonl")
            existing_ids = {item.get("id") for item in existing}
            duplicate = next((item["id"] for item in commands if item["id"] in existing_ids), None)
            if duplicate:
                raise ProtocolError(f"command id already submitted: {duplicate}")
            for command in commands:
                command = {**command, "source": command.get("source", "agent")}
                append_jsonl(self.bridge.run_dir / "commands.jsonl", command)
            self.send_json(202, {"accepted": [command["id"] for command in commands], "run_id": self.bridge.run_dir.name})
        except (ValueError, json.JSONDecodeError, ProtocolError) as error:
            self.send_json(400, {"error": str(error)})


class BridgeHTTPServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address: tuple[str, int], run_dir: Path):
        super().__init__(address, BridgeHandler)
        self.run_dir = run_dir
        self.config = ensure_bridge_config(run_dir)
        self.token = str(self.config["token"])
        self.bridge_address = {"host": self.server_address[0], "port": self.server_address[1]}
        self.config.update(self.bridge_address, pid=os.getpid(), status="running")
        write_json_atomic(run_dir / "bridge.json", self.config)

    def status(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "run_id": self.run_dir.name,
            "session": read_object(self.run_dir / "session.json"),
            "process": read_object(self.run_dir / "process.json"),
            "bridge": {"host": self.server_address[0], "port": self.server_address[1], "pid": os.getpid()},
            "latest": read_latest(self.run_dir.parent),
        }


def serve(run_id: str | None, host: str, port: int) -> int:
    if host != "127.0.0.1":
        raise BridgeError("The first bridge version only binds to 127.0.0.1")
    run_dir = resolve_run(run_id)
    server = BridgeHTTPServer((host, port), run_dir)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        config = read_object(run_dir / "bridge.json") or {}
        config.update(status="stopped", stopped_pid=os.getpid())
        write_json_atomic(run_dir / "bridge.json", config)
        server.server_close()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=0)
    args = parser.parse_args(argv)
    try:
        return serve(args.run_id, args.host, args.port)
    except BridgeError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
