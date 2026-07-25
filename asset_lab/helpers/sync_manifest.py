from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

HELPERS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(HELPERS_DIR))

import manifest
from common import ASSET_LAB_DIR, now_stamp
from validate_lab_assets import collect_manifest_paths, lab_path, scan_asset_files


MISSING_STATUS = "missing_on_disk"
PENDING_SELF_STATUS = "pending_self_creation"
CREATED_STATUS = "created_on_disk"
ORPHAN_STATUS = "orphan_on_disk"
ORPHAN_MISSING_STATUS = "orphan_missing_on_disk"


def referenced_file_entries(data: dict[str, Any]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for asset in data.get("assets", []):
        asset_id = asset.get("id", "<missing_id>")
        for image in asset.get("images", []):
            if image.get("path"):
                entries.append({"asset_id": asset_id, "kind": "image", "entry": image, "path_key": "path"})
        for animation in asset.get("animations", []):
            name = animation.get("name", "<unnamed>")
            for key in ("sheet_path", "gif_path"):
                if animation.get(key):
                    entries.append({"asset_id": asset_id, "kind": f"animation:{name}:{key}", "entry": animation, "path_key": key})
    return entries


def find_missing_references(data: dict[str, Any]) -> list[dict[str, Any]]:
    missing: list[dict[str, Any]] = []
    for item in referenced_file_entries(data):
        path = item["entry"][item["path_key"]]
        if not lab_path(path).exists():
            missing.append({"asset_id": item["asset_id"], "kind": item["kind"], "path": path})
    return missing


def find_orphan_files(data: dict[str, Any]) -> list[str]:
    manifest_paths = collect_manifest_paths(data)
    asset_files = scan_asset_files()
    orphan_paths = asset_files - manifest_paths
    return sorted(orphan_paths)


def mark_missing_references(data: dict[str, Any]) -> int:
    changed = 0
    for item in referenced_file_entries(data):
        entry = item["entry"]
        path = entry[item["path_key"]]
        if lab_path(path).exists():
            if entry.get("status") == PENDING_SELF_STATUS:
                entry["previous_status"] = PENDING_SELF_STATUS
                entry["status"] = CREATED_STATUS
                entry["created_on_disk_at"] = now_stamp()
                changed += 1
                continue
            if entry.get("status") == MISSING_STATUS:
                entry["previous_status"] = MISSING_STATUS
                entry["status"] = "recovered_on_disk"
                entry["recovered_at"] = now_stamp()
                changed += 1
            continue
        if entry.get("status") != MISSING_STATUS:
            entry["previous_status"] = entry.get("status")
            entry["status"] = MISSING_STATUS
            entry["missing_detected_at"] = now_stamp()
            changed += 1
    return changed


def sync_orphans(data: dict[str, Any], orphan_paths: list[str]) -> int:
    changed = 0
    now = now_stamp()
    existing = {item.get("path"): item for item in data.setdefault("orphans", []) if item.get("path")}

    for path in orphan_paths:
        if path in existing:
            item = existing[path]
            if item.get("status") != ORPHAN_STATUS:
                item["status"] = ORPHAN_STATUS
                item["detected_at"] = now
                changed += 1
            continue
        data["orphans"].append(
            {
                "path": path,
                "status": ORPHAN_STATUS,
                "detected_at": now,
                "reason": "file_not_referenced_by_manifest",
            }
        )
        changed += 1

    current_orphans = set(orphan_paths)
    for path, item in existing.items():
        if path not in current_orphans and item.get("status") != ORPHAN_MISSING_STATUS:
            item["status"] = ORPHAN_MISSING_STATUS
            item["missing_detected_at"] = now
            changed += 1

    return changed


def source_prompt(asset: dict[str, Any], source_image_version: int | None) -> str | None:
    if not isinstance(source_image_version, int):
        return None
    for image in asset.get("images", []):
        if image.get("version") == source_image_version:
            return image.get("prompt")
    return None


def backfill_prompt_metadata(data: dict[str, Any]) -> int:
    changed = 0
    for asset in data.get("assets", []):
        asset_id = asset.get("id")
        asset_type = asset.get("type")
        for image in asset.get("images", []):
            if image.get("prompt_metadata"):
                continue
            group_id = image.get("variation_group_id") or f"{image.get('id', asset_id)}__legacy"
            image["variation_group_id"] = group_id
            metadata = {
                "prompt": image.get("prompt"),
                "asset_id": asset_id,
                "asset_type": asset_type,
                "provider": image.get("provider"),
                "action": "legacy_image",
                "variation_group_id": group_id,
            }
            if image.get("mode"):
                metadata["mode"] = image["mode"]
            if image.get("source_image_version"):
                metadata["source_image_version"] = image["source_image_version"]
                metadata["source_prompt_snapshot"] = source_prompt(asset, image["source_image_version"])
            if image.get("source_image_path"):
                metadata["source_image_path"] = image["source_image_path"]
            image["prompt_metadata"] = metadata
            changed += 1

        for animation in asset.get("animations", []):
            if animation.get("prompt_metadata"):
                continue
            group_id = animation.get("variation_group_id") or f"{animation.get('id', asset_id)}__legacy"
            animation["variation_group_id"] = group_id
            metadata = {
                "prompt": animation.get("prompt"),
                "asset_id": asset_id,
                "asset_type": asset_type,
                "provider": animation.get("provider"),
                "action": "legacy_animation",
                "variation_group_id": group_id,
                "animation": animation.get("name"),
                "source_image_version": animation.get("source_image_version"),
                "source_prompt_snapshot": source_prompt(asset, animation.get("source_image_version")),
            }
            if animation.get("source_image_path"):
                metadata["source_image_path"] = animation["source_image_path"]
            animation["prompt_metadata"] = metadata
            changed += 1
    return changed


def print_report(missing: list[dict[str, Any]], orphans: list[str]) -> None:
    if not missing and not orphans:
        print("Manifest sync report: no drift found.")
        return

    print(f"Manifest sync report: {len(missing)} missing reference(s), {len(orphans)} orphan file(s).")
    for item in missing:
        print(f"- missing {item['asset_id']} {item['kind']}: {item['path']}")
    for path in orphans:
        print(f"- orphan file: {path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Report or mark Asset Lab manifest drift.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--report", action="store_true", help="Print drift report only. Default.")
    mode.add_argument("--apply", action="store_true", help="Mark missing references and register orphan files.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data = manifest.load_manifest()
    missing = find_missing_references(data)
    orphans = find_orphan_files(data)
    print_report(missing, orphans)

    if not args.apply:
        return 1 if missing or orphans else 0

    changed = mark_missing_references(data)
    changed += sync_orphans(data, orphans)
    changed += backfill_prompt_metadata(data)
    if changed:
        manifest.save_manifest(data)
    print(f"Manifest sync apply complete. Changed {changed} record(s).")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
