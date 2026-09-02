from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from preview_session import (
    PreviewSession,
    preview_root_dir,
    read_session,
    session_metadata_path,
    write_session,
)


REAL_TEMP_ROOT = Path(tempfile.gettempdir()) / "planning-doc-preview"


@pytest.fixture(autouse=True)
def isolate_preview_temp_root(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(tempfile, "gettempdir", lambda: str(tmp_path))


def test_preview_session_serializes_metadata_round_trip(tmp_path: Path) -> None:
    session = PreviewSession(
        source_markdown_path=str(tmp_path / "source.md"),
        html_output_path=str(tmp_path / "preview" / "index.html"),
        preview_dir=str(tmp_path / "preview"),
        url="http://127.0.0.1:8123/index.html",
        port=8123,
        server_pid=4321,
    )

    write_session(session)

    assert read_session() == session


def test_preview_session_uses_test_specific_temp_root(tmp_path: Path) -> None:
    assert preview_root_dir() == tmp_path / "planning-doc-preview"
    assert session_metadata_path() == tmp_path / "planning-doc-preview" / "session.json"
    assert preview_root_dir() != REAL_TEMP_ROOT


def test_preview_session_uses_single_well_known_metadata_path(tmp_path: Path) -> None:
    expected = Path(tempfile.gettempdir()) / "planning-doc-preview" / "session.json"

    assert session_metadata_path() == expected


def test_preview_session_uses_single_well_known_preview_root_dir(
    tmp_path: Path,
) -> None:
    expected = Path(tempfile.gettempdir()) / "planning-doc-preview"

    assert preview_root_dir() == expected


def test_read_session_treats_corrupt_metadata_as_missing(tmp_path: Path) -> None:
    session_metadata_path().parent.mkdir(parents=True, exist_ok=True)
    session_metadata_path().write_text("{not json", encoding="utf-8")

    assert read_session() is None


def test_read_session_treats_unreadable_metadata_as_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    session_metadata_path().parent.mkdir(parents=True, exist_ok=True)
    session_metadata_path().write_text("{}", encoding="utf-8")

    original_read_text = Path.read_text

    def fake_read_text(self: Path, *args: str, **kwargs: str) -> str:
        if self == session_metadata_path():
            raise PermissionError("cannot read session metadata")
        return original_read_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", fake_read_text)

    assert read_session() is None


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
