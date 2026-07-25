"""Search Freesound or register curated audio candidates for Asset Lab."""

from __future__ import annotations

import argparse
import json
import os
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from audio_manifest import CATALOG_PATH, PREVIEWS_DIR, load_catalog, normalize_license, save_catalog, license_allowed
from common import load_dotenv, relative_to_asset_lab, slugify


def api_search(query: str, api_key: str, limit: int) -> list[dict[str, Any]]:
    params = urllib.parse.urlencode({
        "query": query,
        "page_size": min(limit, 150),
        "fields": "id,name,username,license,url,duration,tags,description,previews",
    })
    request = urllib.request.Request(
        f"https://freesound.org/apiv2/search/?{params}",
        headers={"Authorization": f"Token {api_key}"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8")).get("results", [])


def download(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "love2d-toolkit-audio-lab/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        destination.write_bytes(response.read())


def freesound_candidates(query: str, kind: str, api_key: str, limit: int, licenses: set[str], min_duration: float | None, max_duration: float | None) -> list[dict[str, Any]]:
    output = []
    for item in api_search(query, api_key, limit):
        license_key = normalize_license(item.get("license"))
        if not license_allowed(item.get("license")) or (licenses and license_key not in {normalize_license(value) for value in licenses}):
            continue
        duration = float(item.get("duration") or 0)
        if min_duration is not None and duration < min_duration:
            continue
        if max_duration is not None and duration > max_duration:
            continue
        previews = item.get("previews") or {}
        preview_url = previews.get("preview-hq-ogg") or previews.get("preview-hq-mp3")
        if not preview_url:
            continue
        candidate_id = f"freesound_{item['id']}"
        extension = ".ogg" if "ogg" in preview_url else ".mp3"
        path = PREVIEWS_DIR / f"{candidate_id}{extension}"
        output.append({
            "candidate_id": candidate_id,
            "kind": kind,
            "source": "freesound",
            "source_id": str(item["id"]),
            "title": item.get("name") or candidate_id,
            "author": item.get("username"),
            "license": item.get("license"),
            "duration": item.get("duration"),
            "tags": item.get("tags") or [],
            "source_url": item.get("url") or f"https://freesound.org/s/{item['id']}/",
            "preview_url": preview_url,
            "local_preview": relative_to_asset_lab(path),
            "status": "candidate",
        })
    return output


def curated_candidates(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    entries = data if isinstance(data, list) else [data]
    result = []
    for entry in entries:
        if not license_allowed(entry.get("license")):
            raise ValueError(f"Curated entry has disallowed license: {entry.get('license')}")
        result.append({
            "candidate_id": entry.get("candidate_id") or f"{entry['source']}_{slugify(entry['title'])}",
            "kind": entry["kind"], "source": entry["source"], "source_id": entry.get("source_id"),
            "title": entry["title"], "author": entry.get("author"), "license": entry["license"],
            "duration": entry.get("duration"), "tags": entry.get("tags", []),
            "source_url": entry["source_url"], "preview_url": entry.get("preview_url"),
            "local_preview": entry.get("local_preview"), "status": "candidate",
        })
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Search and stage audio candidates for Asset Lab.")
    parser.add_argument("--source", choices=("freesound", "curated"), required=True)
    parser.add_argument("--kind", choices=("sound", "music"), required=True)
    parser.add_argument("--query", default="")
    parser.add_argument("--license", action="append", dest="licenses", default=[])
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--min-duration", type=float)
    parser.add_argument("--max-duration", type=float)
    parser.add_argument("--curated-json", type=Path)
    parser.add_argument("--download-previews", action="store_true", help="Also download every returned preview; otherwise download on import.")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args(argv)
    load_dotenv()
    if args.source == "freesound":
        api_key = os.getenv("FREESOUND_API_KEY")
        if not api_key:
            raise SystemExit("FREESOUND_API_KEY is required for Freesound search.")
        candidates = freesound_candidates(args.query, args.kind, api_key, args.limit, {value.lower() for value in args.licenses}, args.min_duration, args.max_duration)
    else:
        if not args.curated_json:
            raise SystemExit("--curated-json is required for curated sources.")
        candidates = curated_candidates(args.curated_json)
    print(f"Found {len(candidates)} allowed audio candidate(s).")
    for candidate in candidates:
        print(f"  {candidate['candidate_id']} | {candidate['title']} | {candidate.get('license')} | {candidate.get('duration', 0):.2f}s")
    if not args.execute:
        print("Dry run only. No catalog or preview files changed.")
        return 0
    catalog = load_catalog()
    existing = {item.get("candidate_id"): item for item in catalog["candidates"]}
    for candidate in candidates:
        if args.download_previews and candidate.get("preview_url") and not candidate.get("local_preview"):
            extension = Path(urllib.parse.urlparse(candidate["preview_url"]).path).suffix or ".ogg"
            preview_path = PREVIEWS_DIR / f"{candidate['candidate_id']}{extension}"
            download(candidate["preview_url"], preview_path)
            candidate["local_preview"] = relative_to_asset_lab(preview_path)
        existing[candidate["candidate_id"]] = candidate
    catalog["candidates"] = list(existing.values())
    save_catalog(catalog)
    print(f"Wrote {CATALOG_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
