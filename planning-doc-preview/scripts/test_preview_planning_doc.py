from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from cleanup_preview_session import cleanup_preview_session
from preview_session import (
    PreviewSession,
    preview_html_path,
    read_session,
    write_session,
)
from preview_planning_doc import preview_planning_doc, refresh_planning_doc_preview


@pytest.fixture(autouse=True)
def isolate_preview_temp_root(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    monkeypatch.setattr(tempfile, "gettempdir", lambda: str(tmp_path))
    cleanup_preview_session()
    yield
    cleanup_preview_session()


def test_preview_planning_doc_returns_preview_url_html_path_and_cleanup_instruction(
    tmp_path: Path,
) -> None:
    markdown_path = tmp_path / "plan.md"
    markdown_path.write_text("# Planning Doc\n", encoding="utf-8")

    result = preview_planning_doc(markdown_path)

    assert result.url.startswith("http://127.0.0.1:")
    assert result.html_output_path.endswith(".html")
    assert "cleanup" in result.cleanup_instruction.lower()
    assert Path(result.html_output_path).exists()
    session = read_session()
    assert session is not None
    assert session.source_markdown_path == str(markdown_path)


def test_preview_planning_doc_overwrites_html_in_place_and_keeps_same_url_on_refresh(
    tmp_path: Path,
) -> None:
    markdown_path = tmp_path / "plan.md"
    markdown_path.write_text("# First Version\n", encoding="utf-8")

    initial = preview_planning_doc(markdown_path)
    initial_html = Path(initial.html_output_path).read_text(encoding="utf-8")

    markdown_path.write_text("# Updated Version\n", encoding="utf-8")
    refreshed = refresh_planning_doc_preview(markdown_path)
    refreshed_html = Path(refreshed.html_output_path).read_text(encoding="utf-8")

    assert refreshed.url == initial.url
    assert refreshed.html_output_path == initial.html_output_path
    assert "First Version" in initial_html
    assert "Updated Version" in refreshed_html
    assert "First Version" not in refreshed_html


def test_preview_planning_doc_fails_cleanly_when_render_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    markdown_path = tmp_path / "plan.md"
    markdown_path.write_text("# Planning Doc\n", encoding="utf-8")

    def fake_render(*_args: object, **_kwargs: object) -> Path:
        raise RuntimeError("render exploded")

    monkeypatch.setattr("preview_planning_doc.render_markdown_file", fake_render)

    with pytest.raises(RuntimeError, match="render"):
        preview_planning_doc(markdown_path)


def test_preview_planning_doc_fails_cleanly_when_server_start_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    markdown_path = tmp_path / "plan.md"
    markdown_path.write_text("# Planning Doc\n", encoding="utf-8")

    def fake_start_server(*_args: object, **_kwargs: object) -> object:
        raise RuntimeError("server exploded")

    monkeypatch.setattr("preview_planning_doc.start_preview_server", fake_start_server)

    with pytest.raises(RuntimeError, match="server"):
        preview_planning_doc(markdown_path)


def test_preview_planning_doc_fails_cleanly_when_markdown_path_is_missing(
    tmp_path: Path,
) -> None:
    markdown_path = tmp_path / "missing.md"

    with pytest.raises(RuntimeError, match="missing|not found"):
        preview_planning_doc(markdown_path)


def test_refresh_planning_doc_preview_restarts_when_session_metadata_points_to_dead_server(
    tmp_path: Path,
) -> None:
    markdown_path = tmp_path / "plan.md"
    markdown_path.write_text("# Updated Version\n", encoding="utf-8")
    dead_html_path = preview_html_path()
    dead_html_path.parent.mkdir(parents=True, exist_ok=True)
    dead_html_path.write_text("<h1>stale</h1>", encoding="utf-8")
    write_session(
        PreviewSession(
            source_markdown_path=str(markdown_path),
            html_output_path=str(dead_html_path),
            preview_dir=str(dead_html_path.parent),
            url="http://127.0.0.1:65534/index.html",
            port=65534,
            server_pid=999999,
        )
    )

    refreshed = refresh_planning_doc_preview(markdown_path)

    assert refreshed.url.startswith("http://127.0.0.1:")
    assert refreshed.url != "http://127.0.0.1:65534/index.html"
    assert refreshed.html_output_path == str(dead_html_path)
    assert "Updated Version" in Path(refreshed.html_output_path).read_text(
        encoding="utf-8"
    )


def test_refresh_planning_doc_preview_cleans_up_active_session_when_render_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    markdown_path = tmp_path / "plan.md"
    markdown_path.write_text("# First Version\n", encoding="utf-8")

    initial = preview_planning_doc(markdown_path)

    markdown_path.write_text("# Broken Refresh\n", encoding="utf-8")

    def fake_render(*_args: object, **_kwargs: object) -> Path:
        raise RuntimeError("render exploded")

    monkeypatch.setattr("preview_planning_doc.render_markdown_file", fake_render)

    with pytest.raises(RuntimeError, match="render"):
        refresh_planning_doc_preview(markdown_path)

    assert read_session() is None
    assert not Path(initial.html_output_path).exists()


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
