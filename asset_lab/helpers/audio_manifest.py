"""Shared paths and metadata helpers for the Asset Lab audio workflow."""

from __future__ import annotations

import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any

from common import ASSET_LAB_DIR, PROJECT_ROOT, read_json, slugify, write_json


AUDIO_LIBRARY_DIR = ASSET_LAB_DIR / "audio_library"
CATALOG_PATH = AUDIO_LIBRARY_DIR / "catalog.json"
PREVIEWS_DIR = AUDIO_LIBRARY_DIR / "previews"
IMPORTED_DIR = AUDIO_LIBRARY_DIR / "imported"
PROMOTED_STATE_PATH = PROJECT_ROOT / "game_data" / "promoted_assets.json"
ATTRIBUTIONS_PATH = PROJECT_ROOT / "media_assets" / "audio" / "ATTRIBUTIONS.json"

ALLOWED_LICENSES = {"cc0", "cc by", "cc-by", "creative commons 0", "creative commons attribution"}


def load_catalog() -> dict[str, Any]:
    data = read_json(CATALOG_PATH, {"version": 1, "candidates": []})
    if not isinstance(data, dict) or not isinstance(data.get("candidates"), list):
        raise ValueError(f"Invalid audio catalog: {CATALOG_PATH}")
    data.setdefault("version", 1)
    return data


def save_catalog(data: dict[str, Any]) -> None:
    data["updated_at"] = datetime.now().isoformat(timespec="seconds")
    write_json(CATALOG_PATH, data)


def normalize_license(value: str | None) -> str:
    normalized = " ".join((value or "").lower().replace("_", " ").split())
    if "publicdomain/zero" in normalized or "creative commons 0" in normalized or normalized == "cc0":
        return "cc0"
    if "creativecommons.org/licenses/by" in normalized or normalized in {"cc by", "cc-by", "creative commons attribution"}:
        return "cc by"
    return normalized


def license_allowed(value: str | None) -> bool:
    return normalize_license(value) in {"cc0", "cc by"}


def require_allowed_license(value: str | None) -> None:
    if not license_allowed(value):
        raise ValueError(f"License is not allowed automatically: {value or 'unknown'}")


def candidate_by_id(catalog: dict[str, Any], candidate_id: str) -> dict[str, Any]:
    for candidate in catalog["candidates"]:
        if candidate.get("candidate_id") == candidate_id:
            return candidate
    raise ValueError(f"Audio candidate not found: {candidate_id}")


def stable_id(value: str) -> str:
    return slugify(value)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def local_path(candidate: dict[str, Any], field: str = "local_preview") -> Path:
    value = candidate.get(field)
    if not value:
        raise ValueError(f"Audio candidate has no {field}: {candidate.get('candidate_id')}")
    path = (ASSET_LAB_DIR / value).resolve()
    if ASSET_LAB_DIR.resolve() not in path.parents:
        raise ValueError("Audio path escapes Asset Lab")
    return path
