from __future__ import annotations

from pathlib import Path

import pytest
from render_markdown_preview import render_markdown_file


def test_render_markdown_file_includes_heading_list_and_code_block(
    tmp_path: Path,
) -> None:
    source_path = tmp_path / "plan.md"
    output_path = tmp_path / "preview" / "plan.html"
    source_path.write_text(
        "# Plan\n\n- first\n- second\n\n```python\nprint('hi')\n```\n",
        encoding="utf-8",
    )

    render_markdown_file(source_path, output_path, "Planning Preview")

    html = output_path.read_text(encoding="utf-8")
    assert "<h1>Plan</h1>" in html
    assert "<ul>" in html
    assert "<li>first</li>" in html
    assert "<pre><code>" in html
    assert 'print"' not in html
    assert "print(&#x27;hi&#x27;)" in html


def test_render_markdown_file_includes_simple_ordered_list_items(
    tmp_path: Path,
) -> None:
    source_path = tmp_path / "ordered.md"
    output_path = tmp_path / "preview.html"
    source_path.write_text("1. first\n2. second\n", encoding="utf-8")

    render_markdown_file(source_path, output_path, "Ordered")

    html = output_path.read_text(encoding="utf-8")
    assert "<ul>" in html
    assert "<li>first</li>" in html
    assert "<li>second</li>" in html


def test_render_markdown_file_writes_html_to_requested_output_path(
    tmp_path: Path,
) -> None:
    source_path = tmp_path / "source.md"
    output_path = tmp_path / "nested" / "preview.html"
    source_path.write_text("# Title\n", encoding="utf-8")

    result = render_markdown_file(source_path, output_path, "Custom Title")

    assert result == output_path
    assert output_path.exists()
    html = output_path.read_text(encoding="utf-8")
    assert "<title>Custom Title</title>" in html
    assert str(source_path) in html


def test_render_markdown_file_fails_on_missing_source_path(tmp_path: Path) -> None:
    source_path = tmp_path / "missing.md"
    output_path = tmp_path / "preview.html"

    with pytest.raises(FileNotFoundError):
        render_markdown_file(source_path, output_path, "Missing")


def test_render_markdown_file_fails_on_unreadable_source_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source_path = tmp_path / "source.md"
    output_path = tmp_path / "preview.html"
    source_path.write_text("# Secret\n", encoding="utf-8")

    original_read_text = Path.read_text

    def fake_read_text(self: Path, *args: str, **kwargs: str) -> str:
        if self == source_path:
            raise PermissionError(f"cannot read {self}")
        return original_read_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", fake_read_text)

    with pytest.raises(PermissionError):
        render_markdown_file(source_path, output_path, "Unreadable")


def test_render_markdown_file_fails_cleanly_when_rendering_cannot_complete(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source_path = tmp_path / "source.md"
    output_path = tmp_path / "preview.html"
    source_path.write_text("# Title\n", encoding="utf-8")

    def fake_render(*_args: object, **_kwargs: object) -> str:
        raise ValueError("boom")

    monkeypatch.setattr("render_markdown_preview.render_markdown", fake_render)

    with pytest.raises(RuntimeError, match="render"):
        render_markdown_file(source_path, output_path, "Broken")


def test_render_markdown_file_fails_cleanly_when_output_write_cannot_complete(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source_path = tmp_path / "source.md"
    output_path = tmp_path / "preview" / "preview.html"
    source_path.write_text("# Title\n", encoding="utf-8")

    def fake_write_text(self: Path, data: str, encoding: str | None = None) -> int:
        if self == output_path:
            raise OSError("disk full")
        return len(data)

    monkeypatch.setattr(Path, "write_text", fake_write_text)

    with pytest.raises(RuntimeError, match="output.*disk full"):
        render_markdown_file(source_path, output_path, "Broken output")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
