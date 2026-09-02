from __future__ import annotations

import socket
import tempfile
import subprocess
import sys
import time
from pathlib import Path

from cleanup_preview_session import ensure_clean_single_preview_session
from preview_session import PreviewSession, clear_session, write_session


SERVER_STARTUP_SNIPPET = """
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys

port_file = Path(sys.argv[1])
server = ThreadingHTTPServer(("127.0.0.1", 0), SimpleHTTPRequestHandler)
port_file.write_text(str(server.server_address[1]), encoding="utf-8")
try:
    server.serve_forever()
finally:
    if port_file.exists():
        port_file.unlink()
"""


def _preview_url(preview_dir: Path, html_path: Path, port: int) -> str:
    relative_path = html_path.relative_to(preview_dir).as_posix()
    return f"http://127.0.0.1:{port}/{relative_path}"


def _wait_for_server_start(process: subprocess.Popen[str], port_file: Path) -> int:
    deadline = time.monotonic() + 2
    while time.monotonic() < deadline:
        if port_file.exists():
            try:
                port = int(port_file.read_text(encoding="utf-8").strip())
            except (OSError, ValueError):
                time.sleep(0.05)
                continue

            try:
                with socket.create_connection(("127.0.0.1", port), timeout=0.1):
                    return port
            except OSError:
                time.sleep(0.05)
                continue

        if process.poll() is not None:
            stderr_output = _read_startup_stderr(process)
            detail = f": {stderr_output}" if stderr_output else ""
            raise RuntimeError(f"preview server failed to stay running{detail}")

        time.sleep(0.05)

    stderr_output = _read_startup_stderr(process)
    detail = f": {stderr_output}" if stderr_output else ""
    raise RuntimeError(f"preview server failed to accept connections{detail}")


def _read_startup_stderr(process: subprocess.Popen[str]) -> str:
    if process.stderr is None:
        return ""

    try:
        _stdout, stderr_output = process.communicate(timeout=0.1)
    except subprocess.TimeoutExpired:
        return ""

    return stderr_output.strip()


def start_preview_server(preview_dir: Path, html_path: Path) -> PreviewSession:
    ensure_clean_single_preview_session()

    process: subprocess.Popen[str] | None = None
    port_file = Path(tempfile.mkstemp(prefix="preview-port-", suffix=".txt")[1])

    try:
        process = subprocess.Popen(
            [
                sys.executable,
                "-u",
                "-c",
                SERVER_STARTUP_SNIPPET,
                str(port_file),
            ],
            cwd=str(preview_dir),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        port = _wait_for_server_start(process, port_file)

        session = PreviewSession(
            source_markdown_path="",
            html_output_path=str(html_path),
            preview_dir=str(preview_dir),
            url=_preview_url(preview_dir, html_path, port),
            port=port,
            server_pid=process.pid,
        )
        write_session(session)
        return session
    except Exception as exc:
        clear_session()
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=2)

        if isinstance(exc, RuntimeError) and "server" in str(exc):
            raise

        raise RuntimeError(f"preview server failed to start: {exc}") from exc
    finally:
        if port_file.exists():
            port_file.unlink()
