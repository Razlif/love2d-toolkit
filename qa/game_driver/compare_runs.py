"""Compare the meaningful state of two completed QA runs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from qa.game_driver.logs import LOG_ROOT, read_json, resolve_run


def _final_snapshot(run_dir: Path) -> dict[str, Any] | None:
    report_path = run_dir / "final_report.json"
    if report_path.exists():
        report = read_json(report_path)
        snapshot_path = report.get("snapshot") or report.get("final_snapshot")
        if snapshot_path:
            path = Path(snapshot_path)
            if path.exists():
                return read_json(path)
    snapshots = sorted((run_dir / "snapshots").glob("*.json"))
    return read_json(snapshots[-1]) if snapshots else None


def compare_runs(old_id: str, new_id: str) -> dict[str, Any]:
    old_dir = resolve_run(old_id)
    new_dir = resolve_run(new_id)
    old_report = read_json(old_dir / "final_report.json") if (old_dir / "final_report.json").exists() else {}
    new_report = read_json(new_dir / "final_report.json") if (new_dir / "final_report.json").exists() else {}
    old_snapshot = _final_snapshot(old_dir) or {}
    new_snapshot = _final_snapshot(new_dir) or {}
    differences = []
    for field in ("status", "state", "error_count"):
        if old_report.get(field) != new_report.get(field):
            differences.append({"field": field, "old": old_report.get(field), "new": new_report.get(field)})
    for field in ("state", "camera", "visible_entities", "collisions", "audio"):
        if old_snapshot.get(field) != new_snapshot.get(field):
            differences.append({"field": field, "old": old_snapshot.get(field), "new": new_snapshot.get(field)})
    return {
        "schema_version": 1,
        "old_run_id": old_id,
        "new_run_id": new_id,
        "status": "pass" if not differences else "fail",
        "differences": differences,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("old_run_id")
    parser.add_argument("new_run_id")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = compare_runs(args.old_run_id, args.new_run_id)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif result["status"] == "pass":
        print("PASS: no meaningful state differences")
    else:
        print(f"FAIL: {len(result['differences'])} meaningful difference(s)")
        for difference in result["differences"]:
            print(f"- {difference['field']}")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
