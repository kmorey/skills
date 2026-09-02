from __future__ import annotations

import html
import re
import sys
from pathlib import Path


def render_markdown(markdown_text: str, title: str, source_path: Path) -> str:
    lines = markdown_text.splitlines()
    output: list[str] = []
    paragraph: list[str] = []
    in_code_block = False
    in_list = False

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            output.append(f"<p>{html.escape(' '.join(paragraph))}</p>")
            paragraph = []

    def close_list() -> None:
        nonlocal in_list
        if in_list:
            output.append("</ul>")
            in_list = False

    for line in lines:
        if line.startswith("```"):
            flush_paragraph()
            close_list()
            if in_code_block:
                output.append("</code></pre>")
                in_code_block = False
            else:
                output.append("<pre><code>")
                in_code_block = True
            continue

        if in_code_block:
            output.append(html.escape(line))
            continue

        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            close_list()
            continue

        if stripped.startswith("### "):
            flush_paragraph()
            close_list()
            output.append(f"<h3>{html.escape(stripped[4:])}</h3>")
            continue

        if stripped.startswith("## "):
            flush_paragraph()
            close_list()
            output.append(f"<h2>{html.escape(stripped[3:])}</h2>")
            continue

        if stripped.startswith("# "):
            flush_paragraph()
            close_list()
            output.append(f"<h1>{html.escape(stripped[2:])}</h1>")
            continue

        if stripped.startswith("- "):
            flush_paragraph()
            if not in_list:
                output.append("<ul>")
                in_list = True
            output.append(f"<li>{html.escape(stripped[2:])}</li>")
            continue

        ordered_list_match = re.match(r"\d+\.\s+(.*)", stripped)
        if ordered_list_match:
            flush_paragraph()
            if not in_list:
                output.append("<ul>")
                in_list = True
            output.append(f"<li>{html.escape(ordered_list_match.group(1))}</li>")
            continue

        paragraph.append(stripped)

    flush_paragraph()
    close_list()
    body = "\n".join(output)

    return f"""<!doctype html>
<html lang=\"en\">
<head>
<meta charset=\"utf-8\">
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
<title>{html.escape(title)}</title>
<style>
body {{ font-family: Georgia, serif; margin: 40px auto; max-width: 860px; padding: 0 20px; line-height: 1.6; color: #222; background: #faf8f2; }}
h1, h2, h3 {{ line-height: 1.25; }}
h1 {{ font-size: 2.2rem; }}
h2 {{ margin-top: 2rem; font-size: 1.5rem; border-top: 1px solid #ddd; padding-top: 1rem; }}
h3 {{ margin-top: 1.3rem; font-size: 1.15rem; }}
p, li {{ font-size: 1.05rem; }}
pre {{ background: #1f2430; color: #e6e6e6; padding: 16px; overflow-x: auto; border-radius: 8px; }}
code {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
ul {{ padding-left: 1.4rem; }}
.source {{ color: #666; font-size: 0.95rem; margin-bottom: 2rem; }}
</style>
</head>
<body>
<div class=\"source\">Rendered from <code>{html.escape(str(source_path))}</code></div>
{body}
</body>
</html>
"""


def render_markdown_file(
    source_markdown_path: Path, output_html_path: Path, title: str
) -> Path:
    markdown_text = source_markdown_path.read_text(encoding="utf-8")

    try:
        html_output = render_markdown(markdown_text, title, source_markdown_path)
    except Exception as exc:  # pragma: no cover - exercised via tests
        raise RuntimeError(f"render failed for {source_markdown_path}") from exc

    try:
        output_html_path.parent.mkdir(parents=True, exist_ok=True)
        output_html_path.write_text(html_output, encoding="utf-8")
    except OSError as exc:
        raise RuntimeError(
            f"output write failed for {output_html_path}: {exc}"
        ) from exc

    return output_html_path


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit(
            "Usage: render_markdown_preview.py <source_markdown_path> <output_html_path> <title>"
        )

    source_markdown_path = Path(sys.argv[1])
    output_html_path = Path(sys.argv[2])
    title = sys.argv[3]

    try:
        rendered_path = render_markdown_file(
            source_markdown_path, output_html_path, title
        )
    except FileNotFoundError as exc:
        raise SystemExit(f"Source markdown not found: {exc.filename}") from exc
    except PermissionError as exc:
        raise SystemExit(f"Source markdown is unreadable: {exc}") from exc
    except RuntimeError as exc:
        raise SystemExit(str(exc)) from exc

    print(rendered_path)


if __name__ == "__main__":
    main()
