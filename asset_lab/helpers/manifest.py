from __future__ import annotations

from typing import Any

from common import MANIFEST_PATH, now_stamp, read_json, write_json


def load_manifest() -> dict[str, Any]:
    data = read_json(MANIFEST_PATH, {"version": 1, "assets": []})
    if not isinstance(data, dict):
        data = {"version": 1, "assets": []}
    data.setdefault("version", 1)
    data.setdefault("assets", [])
    return data


def save_manifest(data: dict[str, Any]) -> None:
    data["updated_at"] = now_stamp()
    write_json(MANIFEST_PATH, data)


def find_asset(asset_id: str, asset_type: str | None = None) -> dict[str, Any] | None:
    for asset in load_manifest().get("assets", []):
        if asset.get("id") == asset_id and (asset_type is None or asset.get("type") == asset_type):
            return asset
    return None


def require_asset(asset_id: str, asset_type: str) -> dict[str, Any]:
    asset = find_asset(asset_id, asset_type)
    if asset is None:
        raise ValueError(f"Asset '{asset_id}' is not registered in manifest as type '{asset_type}'.")
    return asset


def find_image_version(asset_id: str, asset_type: str, version: int) -> dict[str, Any] | None:
    asset = find_asset(asset_id, asset_type)
    if asset is None:
        return None
    for image in asset.get("images", []):
        if int(image.get("version", -1)) == version:
            return image
    return None


def available_image_versions(asset_id: str, asset_type: str) -> list[int]:
    asset = find_asset(asset_id, asset_type)
    if asset is None:
        return []
    return sorted(int(image["version"]) for image in asset.get("images", []) if "version" in image)


def set_provider_state(asset_id: str, asset_type: str, provider: str, state: dict[str, Any]) -> dict[str, Any]:
    manifest = load_manifest()
    for asset in manifest.get("assets", []):
        if asset.get("id") == asset_id and asset.get("type") == asset_type:
            provider_state = asset.setdefault("provider_state", {})
            existing = dict(provider_state.get(provider, {}))
            existing.update(state)
            existing["updated_at"] = now_stamp()
            provider_state[provider] = existing
            asset["updated_at"] = now_stamp()
            save_manifest(manifest)
            return asset
    raise ValueError(f"Asset '{asset_id}' is not registered in manifest as type '{asset_type}'.")


def get_provider_state(asset_id: str, asset_type: str, provider: str) -> dict[str, Any]:
    asset = require_asset(asset_id, asset_type)
    return dict(asset.get("provider_state", {}).get(provider, {}))


def upsert_asset_record(record: dict[str, Any]) -> dict[str, Any]:
    manifest = load_manifest()
    assets = manifest.setdefault("assets", [])
    for index, existing in enumerate(assets):
        if existing.get("id") == record["id"]:
            merged = dict(existing)
            merged.update(record)
            merged["updated_at"] = now_stamp()
            assets[index] = merged
            save_manifest(manifest)
            return merged

    record = dict(record)
    record.setdefault("created_at", now_stamp())
    record.setdefault("updated_at", now_stamp())
    assets.append(record)
    save_manifest(manifest)
    return record


def add_image(asset_id: str, entry: dict[str, Any], base_record: dict[str, Any]) -> dict[str, Any]:
    manifest = load_manifest()
    assets = manifest.setdefault("assets", [])
    record = None
    for asset in assets:
        if asset.get("id") == asset_id:
            record = asset
            break
    if record is None:
        record = dict(base_record)
        record.setdefault("images", [])
        record.setdefault("animations", [])
        record.setdefault("created_at", now_stamp())
        assets.append(record)

    images = record.setdefault("images", [])
    images.append(entry)
    record["updated_at"] = now_stamp()
    save_manifest(manifest)
    return record


def add_animation(asset_id: str, entry: dict[str, Any], base_record: dict[str, Any]) -> dict[str, Any]:
    manifest = load_manifest()
    assets = manifest.setdefault("assets", [])
    record = None
    for asset in assets:
        if asset.get("id") == asset_id:
            record = asset
            break
    if record is None:
        record = dict(base_record)
        record.setdefault("images", [])
        record.setdefault("animations", [])
        record.setdefault("created_at", now_stamp())
        assets.append(record)

    animations = record.setdefault("animations", [])
    animations.append(entry)
    record["updated_at"] = now_stamp()
    save_manifest(manifest)
    return record
