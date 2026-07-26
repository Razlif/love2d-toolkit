"""Start, inspect, and stop one managed Love2D QA session."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from qa.game_driver.logs import inspect_run
from qa.game_driver.process_manager import ProcessManagerError, is_process_alive, start_session, status, stop_session

LOG_ROOT = ROOT / "qa" / "runtime_logs"


def bridge_start(port: int = 0) -> dict:
    current = status()
    run_id = current.get("run_id")
    if not run_id or current.get("status") != "running":
        raise ProcessManagerError("Start a managed Love2D session before starting its bridge")
    run_dir = LOG_ROOT / run_id
    bridge_path = run_dir / "bridge.json"
    config = json.loads(bridge_path.read_text(encoding="utf-8")) if bridge_path.exists() else {}
    bridge_pid = config.get("pid")
    if config.get("status") == "running" and is_process_alive(bridge_pid):
        return config
    command = [sys.executable, str(ROOT / "qa" / "bridge_server.py"), "--run-id", run_id, "--port", str(port)]
    log = (run_dir / "bridge.log").open("a", encoding="utf-8")
    try:
        process = subprocess.Popen(command, cwd=ROOT, stdout=log, stderr=log, start_new_session=True)
    finally:
        log.close()
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        time.sleep(0.05)
        if bridge_path.exists():
            config = json.loads(bridge_path.read_text(encoding="utf-8"))
            if config.get("pid") == process.pid and config.get("port"):
                return config
        if process.poll() is not None:
            break
    raise ProcessManagerError(f"Bridge failed to start; see {run_dir / 'bridge.log'}")


def bridge_status() -> dict:
    active = status()
    run_id = active.get("run_id")
    if not run_id:
        return {"status": "stopped"}
    config_path = LOG_ROOT / run_id / "bridge.json"
    config = json.loads(config_path.read_text(encoding="utf-8")) if config_path.exists() else {}
    config["status"] = "running" if is_process_alive(config.get("pid")) else "stopped"
    return config


def bridge_stop() -> dict:
    value = bridge_status()
    pid = value.get("pid")
    if is_process_alive(pid):
        if os.name == "nt":
            subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True, text=True, check=False)
        else:
            os.kill(pid, 15)
    value["status"] = "stopped"
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    start = subparsers.add_parser("start")
    start.add_argument("--mode", choices=("playground",), default="playground")
    start.add_argument("--cutscene")
    start.add_argument("--run-id")
    start.add_argument("--json", action="store_true")
    status_parser = subparsers.add_parser("status")
    status_parser.add_argument("--json", action="store_true")
    latest = subparsers.add_parser("latest")
    latest.add_argument("--json", action="store_true")
    stop = subparsers.add_parser("stop")
    stop.add_argument("--timeout", type=float, default=5)
    stop.add_argument("--json", action="store_true")
    inspect = subparsers.add_parser("inspect")
    inspect.add_argument("run_id")
    inspect.add_argument("--json", action="store_true")
    bridge = subparsers.add_parser("bridge")
    bridge_subparsers = bridge.add_subparsers(dest="bridge_command", required=True)
    bridge_start_parser = bridge_subparsers.add_parser("start")
    bridge_start_parser.add_argument("--port", type=int, default=0)
    bridge_start_parser.add_argument("--json", action="store_true")
    bridge_subparsers.add_parser("status").add_argument("--json", action="store_true")
    bridge_subparsers.add_parser("stop").add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "start":
            result = start_session(mode=args.mode, cutscene=args.cutscene, run_id=args.run_id)
        elif args.command == "status":
            result = status()
        elif args.command == "latest":
            current = status().get("latest") or {}
            result = inspect_run(current["run_id"]) if current.get("run_id") else current
        elif args.command == "inspect":
            result = inspect_run(args.run_id)
        elif args.command == "bridge":
            if args.bridge_command == "start":
                result = bridge_start(args.port)
            elif args.bridge_command == "status":
                result = bridge_status()
            else:
                result = bridge_stop()
        else:
            result = stop_session(timeout=args.timeout)
    except (ProcessManagerError, FileNotFoundError, KeyError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
