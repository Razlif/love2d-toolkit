"""Drive a Love2D QA session through the file-based command bridge."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from qa.game_checks.love_runtime import find_love_executable
from qa.game_driver.process_manager import build_launch
from qa.game_driver.protocol import ProtocolError, validate_commands
from qa.game_driver.session import JsonlCursor, SCHEMA_VERSION, append_jsonl, finalize_run, new_run_dir, write_json


def load_commands(path: Path | None) -> list[dict]:
    if path is None:
        return []
    commands = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            commands.append(json.loads(line))
        except (json.JSONDecodeError, ProtocolError) as error:
            raise SystemExit(f"Invalid command at {path}:{line_number}: {error}") from error
    try:
        return validate_commands(commands)
    except ProtocolError as error:
        raise SystemExit(f"Invalid command file {path}: {error}") from error


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("playground",), default="playground")
    parser.add_argument("--cutscene")
    parser.add_argument("--commands", type=Path)
    parser.add_argument("--run-id")
    parser.add_argument("--timeout", type=float, default=30)
    args = parser.parse_args()

    run_dir = new_run_dir(ROOT / "qa" / "runtime_logs", args.run_id)
    executable = find_love_executable()
    version_result = subprocess.run([executable, "--version"], capture_output=True, text=True, check=False)
    git_result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=False)
    session = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_dir.name,
        "status": "running",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "mode": args.mode,
        "cutscene": args.cutscene,
        "commands_file": str(args.commands.resolve()) if args.commands else None,
        "project_path": str(ROOT),
        "love_executable": executable,
        "love_version": (version_result.stdout or version_result.stderr).strip(),
        "git_commit": git_result.stdout.strip() or None,
    }
    write_json(run_dir / "session.json", session)
    commands = load_commands(args.commands)
    for command in commands:
        append_jsonl(run_dir / "commands.jsonl", command)

    launch = build_launch(executable, ROOT, run_dir, args.cutscene)
    process = subprocess.Popen(launch, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    events = JsonlCursor(run_dir / "results.jsonl")
    completed_actions = set()
    deadline = time.monotonic() + args.timeout
    report = {"status": "timeout", "error_count": 1, "error": None}
    try:
        while time.monotonic() < deadline:
            records = events.read_new()
            for record in records:
                print(json.dumps(record, indent=2))
                action_id = record.get("action_id")
                if action_id:
                    completed_actions.add(action_id)
                all_commands_done = bool(commands) and all(
                    command["id"] in completed_actions for command in commands
                )
                if record.get("command") == "run_finished" or all_commands_done:
                    report = {"status": "passed" if record.get("ok", True) else "failed", "error_count": 0 if record.get("ok", True) else 1}
                    return 0 if record.get("ok", True) else 1
                if record.get("final") and not commands:
                    report = {"status": "passed" if record.get("ok", True) else "failed", "error_count": 0 if record.get("ok", True) else 1}
                    return 0 if record.get("ok", True) else 1
            if process.poll() is not None:
                output = process.stdout.read() if process.stdout else ""
                if output:
                    print(output, end="")
                report = {"status": "passed" if process.returncode == 0 else "crashed", "error_count": 0 if process.returncode == 0 else 1}
                return process.returncode or 0
            time.sleep(0.02)
        print(f"QA session timed out after {args.timeout:g} seconds", file=sys.stderr)
        report = {"status": "timeout", "error_count": 1, "error": f"session exceeded {args.timeout:g} seconds"}
        return 1
    finally:
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=5)
        session["status"] = report["status"]
        session["finished_at"] = datetime.now(timezone.utc).isoformat()
        existing_report = {}
        existing_report_path = run_dir / "final_report.json"
        if existing_report_path.exists():
            try:
                existing_report = json.loads(existing_report_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                existing_report = {}
        report = {**existing_report, **report}
        if existing_report.get("snapshot"):
            report["final_snapshot"] = existing_report["snapshot"]
        if existing_report.get("screenshot"):
            report["final_screenshot"] = existing_report["screenshot"]
        write_json(run_dir / "session.json", session)
        finalize_run(run_dir, report)


if __name__ == "__main__":
    raise SystemExit(main())
