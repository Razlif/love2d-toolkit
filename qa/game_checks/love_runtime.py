"""Locate a Love2D executable across supported host platforms."""

from __future__ import annotations

import os
import shutil
from pathlib import Path


WINDOWS_CANDIDATES = (
    Path(r"C:\Program Files\LOVE\lovec.exe"),
    Path(r"C:\Program Files\LOVE\love.exe"),
    Path(r"C:\Program Files (x86)\LOVE\lovec.exe"),
    Path(r"C:\Program Files (x86)\LOVE\love.exe"),
)


class LoveRuntimeError(RuntimeError):
    """Raised when no usable Love2D executable can be found."""


def _resolve_override(value: str) -> str | None:
    path = Path(value).expanduser()
    if path.is_file():
        return str(path)
    return shutil.which(value)


def find_love_executable() -> str:
    """Return a Love2D executable path or raise an actionable error."""

    override = os.environ.get("LOVE_EXECUTABLE")
    if override:
        resolved = _resolve_override(override)
        if resolved:
            return resolved
        raise LoveRuntimeError(
            "LOVE_EXECUTABLE is set but does not point to a usable Love2D "
            f"executable: {override}"
        )

    for name in ("lovec", "love"):
        resolved = shutil.which(name)
        if resolved:
            return resolved

    for candidate in WINDOWS_CANDIDATES:
        if candidate.is_file():
            return str(candidate)

    raise LoveRuntimeError(
        "Could not find Love2D. Install 'love' or 'lovec', or set "
        "LOVE_EXECUTABLE to the executable path."
    )
