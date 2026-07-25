from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from common import append_trace, redact, request_json


ACCOUNT_URL = "https://www.autosprite.io/api/v1/account"
CHARACTERS_URL = "https://www.autosprite.io/api/v1/characters"


def api_key_from_env() -> str:
    key = os.environ.get("AUTOSPRITE_API_KEY")
    if not key:
        raise RuntimeError("Missing AUTOSPRITE_API_KEY in .env or environment.")
    return key


def check_account(*, api_key: str, trace_path: Path) -> dict[str, Any]:
    append_trace(
        trace_path,
        "provider_request",
        {"provider": "autosprite", "method": "GET", "url": ACCOUNT_URL, "api_key": redact(api_key)},
    )
    status, data = request_json("GET", ACCOUNT_URL, headers={"x-api-key": api_key}, timeout=30)
    append_trace(trace_path, "provider_response", {"provider": "autosprite", "status": status, "body_keys": sorted(data.keys())})
    if status >= 400:
        raise RuntimeError(f"AutoSprite account check failed with HTTP {status}.")
    return data


def create_character_from_image(
    *,
    api_key: str,
    name: str,
    image_path: Path,
    character_description: str,
    is_humanoid: bool,
    trace_path: Path,
) -> dict[str, Any]:
    import mimetypes
    import uuid

    if not image_path.exists():
        raise FileNotFoundError(f"AutoSprite source image missing: {image_path}")

    boundary = f"----assetlab{uuid.uuid4().hex}"
    mime_type = mimetypes.guess_type(image_path.name)[0] or "image/png"
    fields = {
        "name": name,
        "characterDescription": character_description,
        "isHumanoid": "true" if is_humanoid else "false",
    }

    parts: list[bytes] = []
    for key, value in fields.items():
        parts.append(f"--{boundary}\r\n".encode("utf-8"))
        parts.append(f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode("utf-8"))
        parts.append(str(value).encode("utf-8"))
        parts.append(b"\r\n")
    parts.append(f"--{boundary}\r\n".encode("utf-8"))
    parts.append(
        f'Content-Disposition: form-data; name="image"; filename="{image_path.name}"\r\n'
        f"Content-Type: {mime_type}\r\n\r\n".encode("utf-8")
    )
    parts.append(image_path.read_bytes())
    parts.append(b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode("utf-8"))
    body = b"".join(parts)

    headers = {
        "x-api-key": api_key,
        "Content-Type": f"multipart/form-data; boundary={boundary}",
    }
    append_trace(
        trace_path,
        "provider_request",
        {
            "provider": "autosprite",
            "method": "POST",
            "url": CHARACTERS_URL,
            "api_key": redact(api_key),
            "fields": {**fields, "image": str(image_path)},
        },
    )

    import json
    import urllib.error
    import urllib.request

    req = urllib.request.Request(CHARACTERS_URL, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            raw = response.read().decode("utf-8")
            data = json.loads(raw) if raw else {}
            status = response.status
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            data = {"raw": raw}
        status = exc.code

    append_trace(trace_path, "provider_response", {"provider": "autosprite", "status": status, "body_keys": sorted(data.keys())})
    if status >= 400:
        raise RuntimeError(f"AutoSprite character upload failed with HTTP {status}.")
    if not data.get("id"):
        raise RuntimeError("AutoSprite character upload response did not include id.")
    return data


def generate_static(**_: Any) -> dict[str, Any]:
    raise NotImplementedError("AutoSprite generation is not implemented in the Asset Lab creator yet.")


def generate_animation(**_: Any) -> dict[str, Any]:
    raise NotImplementedError("AutoSprite animation is not implemented in the Asset Lab creator yet.")
