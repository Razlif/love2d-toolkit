"""Explicitly refresh the pinned Love2D API reference."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from qa.game_checks.love_runtime import find_love_executable
from love_docs import load_reference, validate_reference


HERE = Path(__file__).resolve().parent
SOURCE_REF = "447486c14b7af6ffb610c47d9b800703b4e628f4"
SOURCE_URL = "https://github.com/love2d-community/love-api"


def download_source(destination: Path) -> Path:
    archive_path = destination / "love-api.tar.gz"
    url = f"{SOURCE_URL}/archive/{SOURCE_REF}.tar.gz"
    urllib.request.urlretrieve(url, archive_path)
    extract_path = destination / "source"
    extract_path.mkdir()
    with tarfile.open(archive_path, "r:gz") as archive:
        try:
            archive.extractall(extract_path, filter="data")
        except TypeError:
            archive.extractall(extract_path)
    roots = list(extract_path.iterdir())
    if len(roots) != 1 or not roots[0].is_dir():
        raise RuntimeError("Unexpected love-api archive layout")
    return roots[0]


def run_converter(source: Path, output: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="love-api-converter-") as directory:
        work = Path(directory)
        shutil.copy2(HERE / "convert_api.lua", work / "main.lua")
        love = find_love_executable()
        staged_source = work / "api"
        shutil.copytree(source, staged_source)
        command = [love, str(work), str(staged_source), str(output)]
        completed = subprocess.run(command, capture_output=True, text=True, check=False)
        if completed.returncode != 0:
            raise RuntimeError(completed.stderr.strip() or completed.stdout.strip() or "Love2D converter failed")


def validate_generated(path: Path) -> None:
    from love_docs import load_reference, validate_reference

    if path != Path(__file__).with_name("love_api.json"):
        with path.open(encoding="utf-8") as handle:
            reference = json.load(handle)
        errors = validate_reference(reference)
    else:
        errors = validate_reference(load_reference())
    if errors:
        raise RuntimeError("Generated reference is invalid: " + "; ".join(errors))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="check the pinned source without changing files")
    parser.add_argument("--execute", action="store_true", help="download and replace the generated reference")
    args = parser.parse_args()
    if args.check == args.execute:
        parser.error("choose exactly one of --check or --execute")
    print(f"Pinned Love2D API source: {SOURCE_REF}")
    if args.check:
        reference = load_reference()
        errors = validate_reference(reference)
        if reference["metadata"].get("source_ref") != SOURCE_REF:
            errors.append("metadata source_ref does not match the pinned source")
        if errors:
            raise RuntimeError("Local reference check failed: " + "; ".join(errors))
        print("Local reference is valid; use --execute to regenerate it.")
        return 0
    with tempfile.TemporaryDirectory(prefix="love-api-update-") as directory:
        source = download_source(Path(directory))
        output = Path(directory) / "love_api.json"
        run_converter(source, output)
        with output.open(encoding="utf-8") as handle:
            reference = json.load(handle)
        errors = validate_reference(reference)
        if errors:
            raise RuntimeError("Generated reference is invalid: " + "; ".join(errors))
        metadata = {
            "love_version": reference["love_version"],
            "source": SOURCE_URL,
            "source_ref": SOURCE_REF,
            "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "generator": "convert_api.lua",
        }
        reference_path = HERE / "love_api.json"
        metadata_path = HERE / "reference_metadata.json"
        reference_path.with_suffix(".json.tmp").write_text(
            json.dumps(reference, ensure_ascii=False, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )
        metadata_path.with_suffix(".json.tmp").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
        reference_path.with_suffix(".json.tmp").replace(reference_path)
        metadata_path.with_suffix(".json.tmp").replace(metadata_path)
    print(f"Updated Love2D {metadata['love_version']} reference.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
