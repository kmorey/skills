from __future__ import annotations

import shutil
import sys
from pathlib import Path

from cleanup_preview_session import cleanup_preview_session
from preview_session import (
    PreviewSessionResult,
    cleanup_instruction,
    preview_html_path,
    preview_site_dir,
    read_session,
    session_is_alive,
    write_session,
)
from render_markdown_preview import render_markdown_file
from start_preview_server import start_preview_server


def _validated_markdown_path(markdown_path: Path) -> Path:
    if not markdown_path.exists():
        raise RuntimeError(f"Markdown source not found: {markdown_path}")
    if not markdown_path.is_file():
        raise RuntimeError(f"Markdown source is missing or invalid: {markdown_path}")
    return markdown_path


def _preview_title(markdown_path: Path) -> str:
    return f"Planning Preview - {markdown_path.stem}"


def _result(url: str, html_path: Path) -> PreviewSessionResult:
    return PreviewSessionResult(
        url=url,
        html_output_path=str(html_path),
        cleanup_instruction=cleanup_instruction(),
    )


def _cleanup_render_artifacts() -> None:
    site_dir = preview_site_dir()
    if site_dir.exists():
        shutil.rmtree(site_dir)


def preview_planning_doc(markdown_path: Path) -> PreviewSessionResult:
    markdown_path = _validated_markdown_path(markdown_path)
    existing_session = read_session()
    if existing_session is not None and not session_is_alive(existing_session):
        cleanup_preview_session()

    html_path = preview_html_path()
    site_dir = preview_site_dir()

    try:
        render_markdown_file(markdown_path, html_path, _preview_title(markdown_path))
    except Exception as exc:
        _cleanup_render_artifacts()
        raise RuntimeError(f"preview render failed: {exc}") from exc

    try:
        session = start_preview_server(site_dir, html_path)
    except Exception as exc:
        _cleanup_render_artifacts()
        raise RuntimeError(f"preview server failed: {exc}") from exc

    session.source_markdown_path = str(markdown_path)
    write_session(session)
    return _result(session.url, html_path)


def refresh_planning_doc_preview(markdown_path: Path) -> PreviewSessionResult:
    markdown_path = _validated_markdown_path(markdown_path)
    session = read_session()
    if session is None or not session_is_alive(session):
        return preview_planning_doc(markdown_path)

    if session.source_markdown_path != str(markdown_path):
        raise RuntimeError(
            "active preview session belongs to a different markdown path"
        )

    html_path = Path(session.html_output_path)
    try:
        render_markdown_file(markdown_path, html_path, _preview_title(markdown_path))
    except Exception as exc:
        cleanup_preview_session()
        raise RuntimeError(f"preview render failed: {exc}") from exc

    return _result(session.url, html_path)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: preview_planning_doc.py <source_markdown_path>")

    markdown_path = Path(sys.argv[1])
    session = read_session()
    if (
        session is not None
        and session.source_markdown_path == str(markdown_path)
        and session_is_alive(session)
    ):
        result = refresh_planning_doc_preview(markdown_path)
    else:
        result = preview_planning_doc(markdown_path)

    print(f"Preview URL: {result.url}")
    print(f"HTML Path: {result.html_output_path}")
    print(f"Cleanup: {result.cleanup_instruction}")


if __name__ == "__main__":
    main()
