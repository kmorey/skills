from __future__ import annotations

import json
import os
import socket
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class PreviewSession:
    source_markdown_path: str
    html_output_path: str
    preview_dir: str
    url: str
    port: int
    server_pid: int | None


@dataclass
class PreviewSessionResult:
    url: str
    html_output_path: str
    cleanup_instruction: str


def preview_root_dir() -> Path:
    return Path(tempfile.gettempdir()) / "planning-doc-preview"


def session_metadata_path() -> Path:
    return preview_root_dir() / "session.json"


def preview_site_dir() -> Path:
    return preview_root_dir() / "site"


def preview_html_path() -> Path:
    return preview_site_dir() / "index.html"


def cleanup_instruction() -> str:
    return f"Run `python {Path(__file__).with_name('cleanup_preview_session.py')}` to cleanup the active preview session."


def session_is_alive(session: PreviewSession | None) -> bool:
    if session is None or session.server_pid is None:
        return False

    try:
        os.kill(session.server_pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        pass

    try:
        with socket.create_connection(("127.0.0.1", session.port), timeout=0.1):
            return True
    except OSError:
        return False


def write_session(session: PreviewSession) -> None:
    metadata_path = session_metadata_path()
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(json.dumps(asdict(session), indent=2), encoding="utf-8")


def read_session() -> PreviewSession | None:
    metadata_path = session_metadata_path()
    if not metadata_path.exists():
        return None

    try:
        data = json.loads(metadata_path.read_text(encoding="utf-8"))
        return PreviewSession(**data)
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return None


def clear_session() -> None:
    metadata_path = session_metadata_path()
    if metadata_path.exists():
        metadata_path.unlink()
