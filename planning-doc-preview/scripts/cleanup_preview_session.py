from __future__ import annotations

import os
import shutil
import signal
import time
from pathlib import Path

from preview_session import (
    clear_session,
    preview_root_dir,
    read_session,
    session_metadata_path,
)


MANUAL_CLEANUP_INSTRUCTION = (
    f"stale preview session could not be cleaned up; run `python {Path(__file__)}`"
)


def _is_managed_preview_path(path: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(preview_root_dir().resolve(strict=False))
    except ValueError:
        return False

    return True


def _pid_looks_like_preview_server(server_pid: int, preview_dir: Path) -> bool:
    proc_dir = Path("/proc") / str(server_pid)
    cmdline_path = proc_dir / "cmdline"

    try:
        cmdline = cmdline_path.read_text(encoding="utf-8").replace("\x00", " ")
        cwd = Path(os.readlink(proc_dir / "cwd")).resolve(strict=False)
    except OSError:
        return False

    if (
        "ThreadingHTTPServer" not in cmdline
        or "SimpleHTTPRequestHandler" not in cmdline
    ):
        return False

    if not _is_managed_preview_path(cwd):
        return False

    return cwd == preview_dir.resolve(strict=False)


def _is_process_alive(server_pid: int) -> bool:
    try:
        waited_pid, _status = os.waitpid(server_pid, os.WNOHANG)
    except ChildProcessError:
        waited_pid = 0

    if waited_pid == server_pid:
        return False

    try:
        os.kill(server_pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True

    return True


def _wait_for_process_exit(server_pid: int, timeout_seconds: float) -> bool:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if not _is_process_alive(server_pid):
            return True
        time.sleep(0.05)

    return not _is_process_alive(server_pid)


def _terminate_server(server_pid: int | None, preview_dir: Path) -> None:
    if server_pid is None:
        return

    if not _pid_looks_like_preview_server(server_pid, preview_dir):
        return

    if not _is_process_alive(server_pid):
        return

    try:
        os.kill(server_pid, signal.SIGTERM)
    except ProcessLookupError:
        return

    if _wait_for_process_exit(server_pid, timeout_seconds=2):
        return

    try:
        os.kill(server_pid, signal.SIGKILL)
    except ProcessLookupError:
        return

    if not _wait_for_process_exit(server_pid, timeout_seconds=2):
        raise RuntimeError("verified preview server could not be stopped")


def cleanup_preview_session() -> None:
    session = read_session()
    metadata_path = session_metadata_path()

    if session is None:
        if metadata_path.exists():
            clear_session()
        return

    preview_dir = Path(session.preview_dir)
    _terminate_server(session.server_pid, preview_dir)

    html_output_path = Path(session.html_output_path)
    if _is_managed_preview_path(html_output_path) and html_output_path.exists():
        html_output_path.unlink()

    if _is_managed_preview_path(preview_dir) and preview_dir.exists():
        shutil.rmtree(preview_dir)

    clear_session()


def ensure_clean_single_preview_session() -> None:
    if not session_metadata_path().exists():
        return

    try:
        cleanup_preview_session()
    except Exception as exc:
        raise RuntimeError(MANUAL_CLEANUP_INSTRUCTION) from exc

    if session_metadata_path().exists() or read_session() is not None:
        raise RuntimeError(MANUAL_CLEANUP_INSTRUCTION)


def main() -> None:
    cleanup_preview_session()
    print("preview session cleaned up")


if __name__ == "__main__":
    main()
