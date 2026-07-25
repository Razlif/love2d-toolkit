"""Import a selected audio candidate into Asset Lab staging."""

from __future__ import annotations

import argparse
import shutil
import urllib.parse
import urllib.request
from pathlib import Path

from audio_manifest import ASSET_LAB_DIR, IMPORTED_DIR, PREVIEWS_DIR, candidate_by_id, license_allowed, load_catalog, local_path, save_catalog, sha256, stable_id


def download_preview(candidate: dict, catalog: dict) -> Path:
    preview_url = candidate.get("preview_url")
    if not preview_url:
        raise SystemExit(f"Audio candidate has no preview URL: {candidate.get('candidate_id')}")
    extension = Path(urllib.parse.urlparse(preview_url).path).suffix.lower() or ".ogg"
    destination = PREVIEWS_DIR / f"{candidate['candidate_id']}{extension}"
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(preview_url, headers={"User-Agent": "love2d-toolkit-audio-lab/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            destination.write_bytes(response.read())
    except Exception as exc:
        raise SystemExit(f"Could not download audio preview: {exc}") from exc
    candidate["local_preview"] = destination.relative_to(ASSET_LAB_DIR).as_posix()
    save_catalog(catalog)
    return destination


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Import an Asset Lab audio candidate.")
    parser.add_argument("--candidate-id", required=True)
    parser.add_argument("--asset-id", required=True)
    parser.add_argument("--operation", choices=("import-new", "import-update"), default="import-new")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args(argv)
    catalog = load_catalog()
    candidate = candidate_by_id(catalog, args.candidate_id)
    if not license_allowed(candidate.get("license")):
        raise SystemExit(f"Candidate license is not allowed: {candidate.get('license')}")
    asset_id = stable_id(args.asset_id)
    if candidate.get("asset_id") and candidate["asset_id"] != asset_id and args.operation == "import-new":
        raise SystemExit(f"Candidate already imported as {candidate['asset_id']}; use import-update.")
    if not candidate.get("local_preview"):
        source = download_preview(candidate, catalog)
    else:
        source = local_path(candidate)
    if not source.is_file():
        raise SystemExit(f"Local preview is missing: {source}")
    destination = IMPORTED_DIR / candidate["kind"] / f"{asset_id}{source.suffix.lower()}"
    print(f"Import: {source} -> {destination}")
    if not args.execute:
        print("Dry run only. No imported file or catalog entry changed.")
        return 0
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    candidate.update({"asset_id": asset_id, "imported_path": destination.relative_to(IMPORTED_DIR.parent.parent).as_posix(), "sha256": sha256(destination), "status": "imported"})
    save_catalog(catalog)
    print("Audio candidate imported.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
