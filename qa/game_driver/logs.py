"""Inspect completed Love2D QA runs without rereading the whole event log."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from qa.game_driver.session import list_run_dirs, read_latest


LOG_ROOT = ROOT / "qa" / "runtime_logs"


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"Expected an object in {path}")
    return value


def resolve_run(run_id: str) -> Path:
    run_dir = LOG_ROOT / run_id
    if not run_dir.is_dir():
        raise FileNotFoundError(f"QA run not found: {run_id}")
    return run_dir


def inspect_run(run_id: str) -> dict[str, Any]:
    run_dir = resolve_run(run_id)
    result: dict[str, Any] = {"run_id": run_id}
    for filename in ("session.json", "final_report.json"):
        path = run_dir / filename
        if path.exists():
            result[filename[:-5]] = read_json(path)
    result["event_count"] = sum(1 for _ in read_jsonl(run_dir / "events.jsonl"))
    result["result_count"] = sum(1 for _ in read_jsonl(run_dir / "results.jsonl"))
    result["screenshots"] = len(list((run_dir / "screenshots").glob("*.png")))
    result["snapshots"] = len(list((run_dir / "snapshots").glob("*.json")))
    return result


def read_jsonl(path: Path):
    if not path.exists():
        return
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("latest").add_argument("--json", action="store_true")
    subparsers.add_parser("list").add_argument("--json", action="store_true")
    inspect = subparsers.add_parser("inspect")
    inspect.add_argument("run_id")
    inspect.add_argument("--json", action="store_true")
    events = subparsers.add_parser("events")
    events.add_argument("run_id")
    events.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "latest":
            value = read_latest(LOG_ROOT)
            if value is None:
                raise FileNotFoundError("No completed QA run found")
        elif args.command == "list":
            value = [path.name for path in list_run_dirs(LOG_ROOT)]
        elif args.command == "inspect":
            value = inspect_run(args.run_id)
        else:
            value = list(read_jsonl(resolve_run(args.run_id) / "events.jsonl"))
        if args.json:
            print(json.dumps(value, indent=2, ensure_ascii=False))
        elif isinstance(value, list):
            for item in value:
                print(json.dumps(item, ensure_ascii=False))
        else:
            print(json.dumps(value, indent=2, ensure_ascii=False))
        return 0
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
