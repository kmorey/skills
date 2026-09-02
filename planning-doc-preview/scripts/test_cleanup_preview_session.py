from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
from cleanup_preview_session import cleanup_preview_session
from preview_session import (
    PreviewSession,
    preview_root_dir,
    read_session,
    session_metadata_path,
    write_session,
)
from start_preview_server import start_preview_server
from test_start_preview_server import _stop_server


@pytest.fixture(autouse=True)
def isolate_preview_temp_root(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(tempfile, "gettempdir", lambda: str(tmp_path))


def test_cleanup_removes_artifacts_and_session_metadata_without_touching_source(
    tmp_path: Path,
) -> None:
    source_markdown_path = tmp_path / "plan.md"
    source_markdown_path.write_text("# Source of truth\n", encoding="utf-8")

    preview_dir = preview_root_dir() / "preview"
    html_path = preview_dir / "index.html"
    preview_dir.mkdir(parents=True)
    html_path.write_text("<h1>Preview</h1>", encoding="utf-8")

    session = start_preview_server(preview_dir, html_path)
    session.source_markdown_path = str(source_markdown_path)

    try:
        cleanup_preview_session()

        assert source_markdown_path.read_text(encoding="utf-8") == "# Source of truth\n"
        assert not html_path.exists()
        assert not preview_dir.exists()
        assert not session_metadata_path().exists()
        assert read_session() is None
    finally:
        _stop_server(session.server_pid)


def test_cleanup_is_idempotent_when_session_is_already_gone(tmp_path: Path) -> None:
    source_markdown_path = tmp_path / "plan.md"
    source_markdown_path.write_text("# Source of truth\n", encoding="utf-8")

    cleanup_preview_session()
    cleanup_preview_session()

    assert source_markdown_path.read_text(encoding="utf-8") == "# Source of truth\n"
    assert not session_metadata_path().exists()
    assert read_session() is None


def test_cleanup_refuses_to_signal_unverifiable_process(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    preview_dir = preview_root_dir() / "preview"
    html_path = preview_dir / "index.html"
    preview_dir.mkdir(parents=True)
    html_path.write_text("<h1>Preview</h1>", encoding="utf-8")
    write_session(
        PreviewSession(
            source_markdown_path=str(tmp_path / "plan.md"),
            html_output_path=str(html_path),
            preview_dir=str(preview_dir),
            url="http://127.0.0.1:9999/index.html",
            port=9999,
            server_pid=424242,
        )
    )

    kill_calls: list[tuple[int, int]] = []

    monkeypatch.setattr(
        "cleanup_preview_session._pid_looks_like_preview_server", lambda *_args: False
    )
    monkeypatch.setattr(
        "cleanup_preview_session.os.kill",
        lambda pid, sig: kill_calls.append((pid, sig)),
    )

    cleanup_preview_session()

    assert kill_calls == []
    assert not html_path.exists()
    assert not preview_dir.exists()
    assert read_session() is None


def test_cleanup_refuses_to_delete_paths_outside_managed_preview_root(
    tmp_path: Path,
) -> None:
    outside_dir = tmp_path / "outside-preview"
    outside_html_path = outside_dir / "index.html"
    outside_dir.mkdir()
    outside_html_path.write_text("<h1>Preview</h1>", encoding="utf-8")
    write_session(
        PreviewSession(
            source_markdown_path=str(tmp_path / "plan.md"),
            html_output_path=str(outside_html_path),
            preview_dir=str(outside_dir),
            url="http://127.0.0.1:9999/index.html",
            port=9999,
            server_pid=None,
        )
    )

    cleanup_preview_session()

    assert outside_html_path.exists()
    assert outside_dir.exists()
    assert not session_metadata_path().exists()
    assert read_session() is None


def test_cleanup_keeps_metadata_when_verified_server_survives_signals(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    preview_dir = preview_root_dir() / "preview"
    html_path = preview_dir / "index.html"
    preview_dir.mkdir(parents=True)
    html_path.write_text("<h1>Preview</h1>", encoding="utf-8")
    session = PreviewSession(
        source_markdown_path=str(tmp_path / "plan.md"),
        html_output_path=str(html_path),
        preview_dir=str(preview_dir),
        url="http://127.0.0.1:9999/index.html",
        port=9999,
        server_pid=515151,
    )
    write_session(session)

    kill_calls: list[tuple[int, int]] = []

    monkeypatch.setattr(
        "cleanup_preview_session._pid_looks_like_preview_server", lambda *_args: True
    )

    def fake_kill(pid: int, sig: int) -> None:
        kill_calls.append((pid, sig))

    monkeypatch.setattr("cleanup_preview_session.os.kill", fake_kill)
    monkeypatch.setattr("cleanup_preview_session.time.sleep", lambda *_args: None)

    with pytest.raises(RuntimeError, match="could not be stopped"):
        cleanup_preview_session()

    assert (515151, 15) in kill_calls
    assert (515151, 9) in kill_calls
    assert html_path.exists()
    assert preview_dir.exists()
    assert read_session() == session


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
