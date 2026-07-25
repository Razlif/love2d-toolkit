from __future__ import annotations

import base64
from pathlib import Path
from typing import Any

from common import append_trace


def api_key_from_env() -> str:
    return "mock"


def _image_to_base64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("ascii")


def generate_static(
    *,
    prompt: str,
    trace_path: Path,
    mock_image: Path | None = None,
    source_image_path: Path | None = None,
    init_image_strength: int | None = None,
    **_: Any,
) -> dict[str, Any]:
    if mock_image is None:
        raise ValueError("--mock-image is required when --provider mock creates an image.")
    if not mock_image.exists():
        raise FileNotFoundError(f"Mock image not found: {mock_image}")

    append_trace(
        trace_path,
        "mock_provider",
        {
            "kind": "image",
            "source": str(mock_image),
            "prompt": prompt,
            "source_image_path": str(source_image_path) if source_image_path else None,
            "init_image_strength": init_image_strength,
        },
    )
    return {
        "kind": "image",
        "image_base64": _image_to_base64(mock_image),
        "response": {"mock": True, "source": str(mock_image)},
    }


def generate_animation(
    *,
    action: str,
    trace_path: Path,
    mock_frames_dir: Path | None = None,
    **_: Any,
) -> dict[str, Any]:
    if mock_frames_dir is None:
        raise ValueError("--mock-frames-dir is required when --provider mock creates an animation.")
    if not mock_frames_dir.exists():
        raise FileNotFoundError(f"Mock frames dir not found: {mock_frames_dir}")

    frame_paths = sorted(mock_frames_dir.glob("frame_*.png"))
    if not frame_paths:
        raise ValueError(f"No frame_*.png files found in mock frames dir: {mock_frames_dir}")

    append_trace(
        trace_path,
        "mock_provider",
        {"kind": "animation", "source": str(mock_frames_dir), "frame_count": len(frame_paths), "action": action},
    )
    return {
        "kind": "animation",
        "frame_images_base64": [_image_to_base64(path) for path in frame_paths],
        "response": {"mock": True, "source": str(mock_frames_dir), "frames": [str(path) for path in frame_paths]},
    }
