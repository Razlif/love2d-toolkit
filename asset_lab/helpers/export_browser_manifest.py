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
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(description="Export Asset Lab manifest for the frontend viewer.")
    parser.add_argument("--asset-lab", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    destination = export_manifest(args.asset_lab.resolve())
    print(f"[asset-lab] wrote {destination}")


if __name__ == "__main__":
    main()
