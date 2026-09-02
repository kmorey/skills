from __future__ import annotations

import os
import signal
import tempfile
from pathlib import Path

import pytest

from preview_session import (
    PreviewSession,
    preview_root_dir,
    read_session,
    session_metadata_path,
)
from preview_session import write_session
from start_preview_server import start_preview_server


@pytest.fixture(autouse=True)
def isolate_preview_temp_root(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(tempfile, "gettempdir", lambda: str(tmp_path))


def _stop_server(server_pid: int | None) -> None:
    if server_pid is None:
        return

    try:
        os.kill(server_pid, signal.SIGTERM)
    except ProcessLookupError:
        return

    try:
        os.waitpid(server_pid, 0)
    except ChildProcessError:
        pass


def test_start_preview_server_returns_local_url_and_session_metadata(
    tmp_path: Path,
) -> None:
    preview_dir = tmp_path / "preview"
    html_path = preview_dir / "index.html"
    preview_dir.mkdir()
    html_path.write_text("<h1>Preview</h1>", encoding="utf-8")

    session = start_preview_server(preview_dir, html_path)

    try:
        assert session.preview_dir == str(preview_dir)
        assert session.html_output_path == str(html_path)
        assert session.url == f"http://127.0.0.1:{session.port}/index.html"
        assert session.port > 0
        assert session.server_pid is not None
    finally:
        _stop_server(session.server_pid)


def test_start_preview_server_writes_session_metadata(tmp_path: Path) -> None:
    preview_dir = tmp_path / "preview"
    html_path = preview_dir / "index.html"
    preview_dir.mkdir()
    html_path.write_text("<p>hello</p>", encoding="utf-8")

    session = start_preview_server(preview_dir, html_path)

    try:
        assert session_metadata_path().exists()
        assert read_session() == session
    finally:
        _stop_server(session.server_pid)


def test_start_preview_server_failure_leaves_no_session_metadata(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    preview_dir = tmp_path / "preview"
    html_path = preview_dir / "index.html"
    preview_dir.mkdir()
    html_path.write_text("<p>hello</p>", encoding="utf-8")

    def fake_popen(*_args: object, **_kwargs: object) -> object:
        raise OSError("boom")

    monkeypatch.setattr("start_preview_server.subprocess.Popen", fake_popen)

    with pytest.raises(RuntimeError, match="server"):
        start_preview_server(preview_dir, html_path)

    assert not session_metadata_path().exists()
    assert read_session() is None


def test_start_preview_server_failure_reports_early_stderr_context(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    preview_dir = tmp_path / "preview"
    html_path = preview_dir / "index.html"
    preview_dir.mkdir()
    html_path.write_text("<p>hello</p>", encoding="utf-8")

    class FakeProcess:
        pid = 4321

        def __init__(self) -> None:
            self.stderr = True

        def poll(self) -> int:
            return 1

        def terminate(self) -> None:
            return None

        def wait(self, timeout: float | None = None) -> int:
            return 1

        def kill(self) -> None:
            return None

        def communicate(
            self, input: bytes | None = None, timeout: float | None = None
        ) -> tuple[bytes, bytes]:
            return (b"", b"address already in use")

    monkeypatch.setattr(
        "start_preview_server.subprocess.Popen", lambda *_args, **_kwargs: FakeProcess()
    )

    with pytest.raises(RuntimeError, match="address already in use"):
        start_preview_server(preview_dir, html_path)


def test_start_preview_server_attempts_stale_cleanup_before_starting(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    stale_preview_dir = preview_root_dir() / "stale-preview"
    stale_html_path = stale_preview_dir / "index.html"
    stale_preview_dir.mkdir(parents=True)
    stale_html_path.write_text("<p>stale</p>", encoding="utf-8")
    write_session(
        PreviewSession(
            source_markdown_path=str(tmp_path / "old.md"),
            html_output_path=str(stale_html_path),
            preview_dir=str(stale_preview_dir),
            url="http://127.0.0.1:9999/index.html",
            port=9999,
            server_pid=None,
        )
    )

    preview_dir = preview_root_dir() / "preview"
    html_path = preview_dir / "index.html"
    preview_dir.mkdir(parents=True)
    html_path.write_text("<p>hello</p>", encoding="utf-8")

    call_order: list[str] = []

    original_ensure = getattr(
        __import__("start_preview_server"), "ensure_clean_single_preview_session", None
    )

    def fake_ensure() -> None:
        call_order.append("cleanup")
        if original_ensure is not None:
            original_ensure()

    original_popen = getattr(__import__("start_preview_server").subprocess, "Popen")

    def fake_popen(*args: object, **kwargs: object):
        assert call_order == ["cleanup"]
        return original_popen(*args, **kwargs)

    monkeypatch.setattr(
        "start_preview_server.ensure_clean_single_preview_session", fake_ensure
    )
    monkeypatch.setattr("start_preview_server.subprocess.Popen", fake_popen)

    session = start_preview_server(preview_dir, html_path)

    try:
        assert not stale_html_path.exists()
        assert session.html_output_path == str(html_path)
        assert read_session() == session
    finally:
        _stop_server(session.server_pid)


def test_start_preview_server_fails_with_clear_instruction_when_stale_cleanup_cannot_succeed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    stale_preview_dir = preview_root_dir() / "stale-preview"
    stale_html_path = stale_preview_dir / "index.html"
    stale_preview_dir.mkdir(parents=True)
    stale_html_path.write_text("<p>stale</p>", encoding="utf-8")
    stale_session = PreviewSession(
        source_markdown_path=str(tmp_path / "old.md"),
        html_output_path=str(stale_html_path),
        preview_dir=str(stale_preview_dir),
        url="http://127.0.0.1:9999/index.html",
        port=9999,
        server_pid=None,
    )
    write_session(stale_session)

    preview_dir = tmp_path / "preview"
    html_path = preview_dir / "index.html"
    preview_dir.mkdir()
    html_path.write_text("<p>hello</p>", encoding="utf-8")

    monkeypatch.setattr(
        "start_preview_server.ensure_clean_single_preview_session",
        lambda: (_ for _ in ()).throw(
            RuntimeError(
                "stale preview session could not be cleaned up; run cleanup_preview_session.py"
            )
        ),
    )

    with pytest.raises(RuntimeError, match="cleanup_preview_session.py"):
        start_preview_server(preview_dir, html_path)

    assert read_session() == stale_session
    assert stale_html_path.exists()
    assert html_path.exists()


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
