"""Manage one persistent Love2D QA session."""

from __future__ import annotations

import json
import os
import secrets
import signal
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from qa.game_checks.love_runtime import find_love_executable
from qa.game_driver.session import SCHEMA_VERSION, finalize_run, new_run_dir, read_latest, write_json, write_json_atomic


ROOT = Path(__file__).resolve().parents[2]
LOG_ROOT = ROOT / "qa" / "runtime_logs"
ACTIVE_PATH = LOG_ROOT / "active.json"


class ProcessManagerError(RuntimeError):
    pass


def is_process_alive(pid: int | None) -> bool:
    if not isinstance(pid, int) or pid <= 0:
        return False
    if os.name == "nt":
        import ctypes

        process_query_limited_information = 0x1000
        handle = ctypes.windll.kernel32.OpenProcess(process_query_limited_information, False, pid)
        if handle:
            ctypes.windll.kernel32.CloseHandle(handle)
            return True
        return False
    try:
        os.kill(pid, 0)
    except (OSError, ProcessLookupError):
        return False
    return True


def _git_commit(root: Path) -> str | None:
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=False)
    return result.stdout.strip() or None


def _love_version(executable: str) -> str:
    result = subprocess.run([executable, "--version"], capture_output=True, text=True, check=False)
    return (result.stdout or result.stderr).strip()


def build_launch(executable: str, root: Path, run_dir: Path, cutscene: str | None = None) -> list[str]:
    command = [executable, ".", "--qa", "--qa-run-dir", str(run_dir)]
    if cutscene:
        command.extend(["--cutscene", cutscene])
    return command


def _read_active() -> dict[str, Any] | None:
    if not ACTIVE_PATH.exists():
        return None
    try:
        with ACTIVE_PATH.open(encoding="utf-8") as handle:
            value = json.load(handle)
        return value if isinstance(value, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def _reserve_active(record: dict[str, Any]) -> None:
    LOG_ROOT.mkdir(parents=True, exist_ok=True)
    existing = _read_active()
    if existing and (existing.get("status") == "starting" or is_process_alive(existing.get("pid"))):
        raise ProcessManagerError(f"A managed Love2D session is already active: {existing.get('run_id')}")
    if ACTIVE_PATH.exists():
        ACTIVE_PATH.unlink()
    try:
        with ACTIVE_PATH.open("x", encoding="utf-8") as handle:
            json.dump(record, handle, indent=2, sort_keys=True)
            handle.write("\n")
    except FileExistsError as error:
        raise ProcessManagerError("Another process manager start is already in progress") from error


def _clear_active() -> None:
    try:
        ACTIVE_PATH.unlink()
    except FileNotFoundError:
        pass


def start_session(
    *,
    mode: str = "playground",
    cutscene: str | None = None,
    run_id: str | None = None,
    root: Path = ROOT,
    log_root: Path = LOG_ROOT,
    popen: Callable[..., subprocess.Popen] = subprocess.Popen,
    startup_grace: float = 0.15,
) -> dict[str, Any]:
    global ACTIVE_PATH, LOG_ROOT
    old_active, old_root = ACTIVE_PATH, LOG_ROOT
    ACTIVE_PATH, LOG_ROOT = log_root / "active.json", log_root
    try:
        executable = find_love_executable()
        run_dir = new_run_dir(log_root, run_id)
        started_at = datetime.now(timezone.utc).isoformat()
        reservation = {"schema_version": SCHEMA_VERSION, "run_id": run_dir.name, "status": "starting", "started_at": started_at}
        _reserve_active(reservation)
        stdout_handle = (run_dir / "stdout.log").open("w", encoding="utf-8")
        stderr_handle = (run_dir / "stderr.log").open("w", encoding="utf-8")
        command = build_launch(executable, root, run_dir, cutscene)
        try:
            process = popen(command, cwd=root, stdout=stdout_handle, stderr=stderr_handle, text=True)
        except Exception:
            stdout_handle.close()
            stderr_handle.close()
            _clear_active()
            raise
        stdout_handle.close()
        stderr_handle.close()
        poll = getattr(process, "poll", None)
        if callable(poll):
            time.sleep(startup_grace)
            if poll() is not None:
                stderr_text = (run_dir / "stderr.log").read_text(encoding="utf-8", errors="replace")[-2000:]
                _clear_active()
                raise ProcessManagerError(
                    f"Love2D exited during startup (code {process.returncode}); "
                    f"see {run_dir / 'stdout.log'} and {run_dir / 'stderr.log'}. {stderr_text.strip()}"
                )
        session = {
            "schema_version": SCHEMA_VERSION,
            "run_id": run_dir.name,
            "status": "running",
            "started_at": started_at,
            "mode": mode,
            "cutscene": cutscene,
            "project_path": str(root),
            "love_executable": executable,
            "love_version": _love_version(executable),
            "git_commit": _git_commit(root),
        }
        write_json(run_dir / "session.json", session)
        process_record = {
            **reservation,
            "status": "running",
            "pid": process.pid,
            "command": command,
            "project_path": str(root),
            "stdout_log": str(run_dir / "stdout.log"),
            "stderr_log": str(run_dir / "stderr.log"),
        }
        write_json_atomic(run_dir / "process.json", process_record)
        write_json_atomic(run_dir / "bridge.json", {
            "schema_version": SCHEMA_VERSION,
            "run_id": run_dir.name,
            "host": "127.0.0.1",
            "token": secrets.token_urlsafe(32),
            "status": "stopped",
        })
        write_json_atomic(ACTIVE_PATH, process_record)
        return process_record
    finally:
        ACTIVE_PATH, LOG_ROOT = old_active, old_root


def status(*, log_root: Path = LOG_ROOT) -> dict[str, Any]:
    active_path = log_root / "active.json"
    try:
        active = json.loads(active_path.read_text(encoding="utf-8")) if active_path.exists() else None
    except json.JSONDecodeError:
        active = None
    if not active:
        return {"status": "stopped", "latest": read_latest(log_root)}
    alive = active.get("status") == "starting" or is_process_alive(active.get("pid"))
    active["status"] = "running" if alive else "stale"
    return active


def stop_session(*, timeout: float = 5, log_root: Path = LOG_ROOT) -> dict[str, Any]:
    active_path = log_root / "active.json"
    active = json.loads(active_path.read_text(encoding="utf-8")) if active_path.exists() else None
    if not active:
        raise ProcessManagerError("No managed Love2D session is active")
    pid = active.get("pid")
    if is_process_alive(pid):
        if os.name == "nt":
            subprocess.run(["taskkill", "/PID", str(pid), "/T"], capture_output=True, text=True, check=False)
        else:
            os.kill(pid, signal.SIGTERM)
        deadline = time.monotonic() + timeout
        while is_process_alive(pid) and time.monotonic() < deadline:
            time.sleep(0.05)
        if is_process_alive(pid):
            if os.name == "nt":
                subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True, text=True, check=False)
            else:
                os.kill(pid, signal.SIGKILL)
    run_dir = log_root / str(active["run_id"])
    report = {"status": "stopped", "error_count": 0, "stopped_at": datetime.now(timezone.utc).isoformat()}
    if run_dir.is_dir():
        finalize_run(run_dir, report)
    try:
        active_path.unlink()
    except FileNotFoundError:
        pass
    return {**active, **report}
