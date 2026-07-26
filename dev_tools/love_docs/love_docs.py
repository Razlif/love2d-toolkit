"""Search the pinned offline Love2D API reference."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
REFERENCE_PATH = Path(__file__).with_name("love_api.json")
METADATA_PATH = Path(__file__).with_name("reference_metadata.json")
EXPECTED_LOVE_VERSION = "11.5"


class ReferenceError(RuntimeError):
    """Raised when the local reference is missing or invalid."""


def _load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as handle:
            value = json.load(handle)
    except FileNotFoundError as exc:
        raise ReferenceError(f"Missing Love2D reference file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ReferenceError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ReferenceError(f"Reference file must contain a JSON object: {path}")
    return value


def load_reference() -> dict[str, Any]:
    reference = _load_json(REFERENCE_PATH)
    metadata = _load_json(METADATA_PATH)
    if reference.get("love_version") != metadata.get("love_version"):
        raise ReferenceError("Reference and metadata Love2D versions do not match")
    if not isinstance(reference.get("entries"), list):
        raise ReferenceError("Reference is missing its entries list")
    if not isinstance(reference.get("by_fullname"), dict):
        raise ReferenceError("Reference is missing its by_fullname index")
    reference["metadata"] = metadata
    return reference


def _entry_text(entry: dict[str, Any]) -> str:
    parts = [
        str(entry.get("fullname") or entry.get("name") or ""),
        str(entry.get("what") or ""),
        str(entry.get("description") or ""),
        str(entry.get("module") or ""),
        str(entry.get("type") or ""),
    ]
    return " ".join(parts).casefold()


def search(reference: dict[str, Any], query: str, limit: int) -> list[dict[str, Any]]:
    needle = query.casefold().strip()
    if not needle:
        return []
    entries = reference["entries"]
    ranked: list[tuple[int, str, dict[str, Any]]] = []
    for entry in entries:
        text = _entry_text(entry)
        fullname = str(entry.get("fullname") or entry.get("name") or "")
        name = str(entry.get("name") or "")
        if needle not in text:
            continue
        score = 2
        if fullname.casefold() == needle:
            score = 0
        elif name.casefold() == needle:
            score = 1
        elif fullname.casefold().startswith(needle):
            score = 1
        ranked.append((score, fullname.casefold(), entry))
    ranked.sort(key=lambda item: (item[0], item[1]))
    return [entry for _, _, entry in ranked[: max(0, limit)]]


def lookup(reference: dict[str, Any], fullname: str) -> dict[str, Any] | None:
    index = reference["by_fullname"]
    position = index.get(fullname)
    if position is None:
        position = index.get(fullname.casefold())
    if position is None:
        folded = fullname.casefold()
        for entry in reference["entries"]:
            candidate = str(entry.get("fullname") or entry.get("name") or "")
            if candidate.casefold() == folded:
                return entry
        return None
    try:
        return reference["entries"][int(position)]
    except (IndexError, TypeError, ValueError):
        raise ReferenceError(f"Invalid index entry for {fullname}")


def validate_reference(reference: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if reference.get("love_version") != EXPECTED_LOVE_VERSION:
        errors.append(
            f"expected Love2D {EXPECTED_LOVE_VERSION}, got {reference.get('love_version')}"
        )
    entries = reference.get("entries")
    index = reference.get("by_fullname")
    if not isinstance(entries, list):
        return ["entries must be a list"]
    if not isinstance(index, dict):
        return ["by_fullname must be an object"]
    seen: set[str] = set()
    for number, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"entry {number} is not an object")
            continue
        fullname = entry.get("fullname")
        if not isinstance(fullname, str) or not fullname:
            errors.append(f"entry {number} has no fullname")
            continue
        if fullname in seen:
            errors.append(f"duplicate fullname: {fullname}")
        seen.add(fullname)
        if str(index.get(fullname)) != str(number):
            errors.append(f"index mismatch: {fullname}")
    return errors


def _print_entry(entry: dict[str, Any]) -> None:
    fullname = entry.get("fullname") or entry.get("name")
    print(f"{fullname} [{entry.get('what', 'entry')}]")
    if entry.get("module"):
        print(f"module: {entry['module']}")
    if entry.get("type"):
        print(f"type: {entry['type']}")
    description = str(entry.get("description") or entry.get("minidescription") or "")
    if description:
        print(description.strip())
    for variant in entry.get("variants", []):
        arguments = ", ".join(
            f"{item.get('name', '?')}: {item.get('type', '?')}"
            for item in variant.get("arguments", [])
        )
        returns = ", ".join(item.get("type", "?") for item in variant.get("returns", []))
        print(f"signature: ({arguments}) -> {returns or 'none'}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    version = subparsers.add_parser("version", help="show the pinned reference version")
    version.add_argument("--json", action="store_true")

    search_parser = subparsers.add_parser("search", help="search names and descriptions")
    search_parser.add_argument("query")
    search_parser.add_argument("--limit", type=int, default=20)
    search_parser.add_argument("--json", action="store_true")

    lookup_parser = subparsers.add_parser("lookup", help="look up an exact fullname")
    lookup_parser.add_argument("fullname")
    lookup_parser.add_argument("--json", action="store_true")

    subparsers.add_parser("check", help="validate the local reference")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        reference = load_reference()
        errors = validate_reference(reference)
        if args.command == "check":
            if errors:
                for error in errors:
                    print(f"ERROR: {error}", file=sys.stderr)
                return 1
            print(f"Love2D {reference['love_version']} reference is valid ({len(reference['entries'])} entries)")
            return 0
        if errors:
            raise ReferenceError("; ".join(errors))
        if args.command == "version":
            result = {"love_version": reference["love_version"], **reference["metadata"]}
            print(json.dumps(result, indent=2) if args.json else f"Love2D {reference['love_version']}")
            return 0
        if args.command == "search":
            results = search(reference, args.query, args.limit)
            if args.json:
                print(json.dumps(results, ensure_ascii=False, indent=2))
            else:
                for entry in results:
                    print(f"{entry.get('fullname') or entry.get('name')} [{entry.get('what')}]")
                if not results:
                    print(f"No Love2D API entries matched: {args.query}", file=sys.stderr)
                    return 1
            return 0
        entry = lookup(reference, args.fullname)
        if entry is None:
            suggestions = search(reference, args.fullname, 5)
            print(f"No exact Love2D API entry: {args.fullname}", file=sys.stderr)
            if suggestions:
                print("Suggestions:", file=sys.stderr)
                for suggestion in suggestions:
                    print(f"  {suggestion.get('fullname') or suggestion.get('name')}", file=sys.stderr)
            return 1
        if args.json:
            print(json.dumps(entry, ensure_ascii=False, indent=2))
        else:
            _print_entry(entry)
        return 0
    except ReferenceError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
