"""Promote imported audio from Asset Lab into the Love2D runtime."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import uuid
from datetime import datetime
from pathlib import Path

HELPERS = Path(__file__).resolve().parent
sys.path.insert(0, str(HELPERS))

from audio_manifest import ATTRIBUTIONS_PATH, candidate_by_id, load_catalog, license_allowed, local_path, sha256, stable_id
from common import PROJECT_ROOT, read_json, write_json
from promote_lab_asset import load_promoted_state, runtime_manifest_data, write_runtime_manifest


def stamp() -> str:
    return datetime.now().isoformat(timespec="seconds")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Promote imported audio into media_assets.")
    parser.add_argument("--operation", choices=("promote-new", "promote-update"), required=True)
    parser.add_argument("--kind", choices=("sound", "music"), required=True)
    parser.add_argument("--asset-id", required=True)
    parser.add_argument("--candidate-id", required=True)
    parser.add_argument("--volume", type=float, default=1)
    parser.add_argument("--loop", action="store_true")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args(argv)
    asset_id = stable_id(args.asset_id)
    candidate = candidate_by_id(load_catalog(), args.candidate_id)
    if candidate.get("kind") != args.kind:
        raise SystemExit(f"Candidate kind is {candidate.get('kind')}, not {args.kind}.")
    if not license_allowed(candidate.get("license")):
        raise SystemExit(f"Candidate license is not allowed: {candidate.get('license')}")
    source = local_path(candidate, "imported_path")
    if not source.is_file():
        raise SystemExit(f"Imported audio is missing: {source}")
    state = load_promoted_state(PROJECT_ROOT)
    audio = state.setdefault("audio", {"sounds": {}, "music": {}})
    group_name = "music" if args.kind == "music" else "sounds"
    group = audio.setdefault(group_name, {})
    if args.operation == "promote-new" and asset_id in group:
        raise SystemExit(f"Audio asset already promoted: {asset_id}; use promote-update.")
    if args.operation == "promote-update" and asset_id not in group:
        raise SystemExit(f"Audio asset is not promoted: {asset_id}; use promote-new.")
    relative = Path("media_assets") / "audio" / group_name / f"{asset_id}{source.suffix.lower()}"
    destination = PROJECT_ROOT / relative
    record = {
        "id": asset_id, "path": relative.as_posix(), "source": candidate.get("source"),
        "source_id": candidate.get("source_id"), "title": candidate.get("title"),
        "author": candidate.get("author"), "license": candidate.get("license"),
        "source_url": candidate.get("source_url"), "preview_url": candidate.get("preview_url"),
        "volume": max(0, min(1, args.volume)), "loop": bool(args.loop), "sha256": sha256(source),
        "updated_at": stamp(),
    }
    print(f"Promote: {source} -> {destination}")
    if not args.execute:
        print("Dry run only. No runtime files or manifests changed.")
        return 0
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(f".{destination.name}.{uuid.uuid4().hex}.tmp")
    shutil.copy2(source, temporary)
    if sha256(temporary) != record["sha256"]:
        temporary.unlink(missing_ok=True)
        raise SystemExit("Audio checksum verification failed.")
    temporary.replace(destination)
    group[asset_id] = record
    state["updated_at"] = stamp()
    state_path = PROJECT_ROOT / "game_data" / "promoted_assets.json"
    write_json(state_path, state)
    write_runtime_manifest(PROJECT_ROOT / "game_data" / "asset_manifest.lua", state)
    credits = read_json(ATTRIBUTIONS_PATH, {"version": 1, "audio": {}})
    credits.setdefault("audio", {})[asset_id] = {key: record.get(key) for key in ("title", "author", "license", "source", "source_id", "source_url")}
    write_json(ATTRIBUTIONS_PATH, credits)
    print("Audio promotion complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
