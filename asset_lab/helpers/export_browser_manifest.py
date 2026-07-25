"""Export manifest.json as a browser-loadable JavaScript global."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def export_manifest(asset_lab: Path) -> Path:
    source = asset_lab / "manifest.json"
    destination = asset_lab / "manifest.js"
    data = json.loads(source.read_text(encoding="utf-8"))
    output = "// Generated from manifest.json. Do not edit by hand.\n"
    output += "window.ASSET_LAB_MANIFEST = "
    output += json.dumps(data, ensure_ascii=False, indent=2)
    output += ";\n"
    destination.write_text(output, encoding="utf-8")
    catalog_path = asset_lab / "audio_library" / "catalog.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8")) if catalog_path.exists() else {"version": 1, "candidates": []}
    audio_destination = asset_lab / "audio_catalog.js"
    audio_output = "// Generated from audio_library/catalog.json. Do not edit by hand.\n"
    audio_output += "window.ASSET_LAB_AUDIO_CATALOG = "
    audio_output += json.dumps(catalog, ensure_ascii=False, indent=2)
    audio_output += ";\n"
    audio_destination.write_text(audio_output, encoding="utf-8")
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(description="Export Asset Lab manifest for the frontend viewer.")
    parser.add_argument("--asset-lab", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    destination = export_manifest(args.asset_lab.resolve())
    print(f"[asset-lab] wrote {destination}")


if __name__ == "__main__":
    main()
