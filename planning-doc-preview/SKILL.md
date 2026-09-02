---
name: planning-doc-preview
description: Use when a user wants a planning or spec Markdown document made easier to read in a browser, refreshed after edits, or cleaned up after review
---

# Planning Doc Preview

## Overview

Use this skill when a planning or spec Markdown file should be rendered as readable local HTML and opened through a temporary browser preview.

The workflow is intentionally lightweight: render a limited Markdown subset into simple local HTML, serve one local preview session, keep the URL stable during refreshes, and clean everything up when the review is done.

The renderer is not a full Markdown engine. It is intentionally scoped to common planning-doc structure: headings (`#` through `###`), paragraphs, fenced code blocks, and simple bulleted or numbered lists. It does not aim to support full GitHub-flavored Markdown features such as tables, task-list checkboxes, nested list semantics, blockquotes, or rich inline formatting.

## When to Use

- User asks to make a plan or spec easier to read in a browser
- User wants a local preview URL for a Markdown planning document
- User updates the Markdown and wants the same preview refreshed
- User approves the doc and wants preview cleanup

Do not use this for multi-file docs sites, remote sharing, general publishing, or documents that require full-fidelity Markdown rendering.

## Baseline Gap

Before this skill existed, a search across `~/.config/opencode/skills/**/SKILL.md` found no reusable preview/browser workflow for prompts like `make this plan easier to read in a browser`, so the workflow was not discoverable through skill search.

## Workflow

1. Confirm the source input is the Markdown file path to preview.
2. Launch preview generation and local serving:

```bash
python ~/.config/opencode/skills/planning-doc-preview/scripts/preview_planning_doc.py "/absolute/path/to/doc.md"
```

3. Return all three of these to the user:
   - preview URL
   - generated HTML path
   - cleanup command/step
4. Treat the original Markdown file as the source of truth.

## Return Format

Always give the user:

- `Preview URL:` the local browser URL for the active session
- `HTML Path:` the generated temporary HTML artifact path
- `Cleanup:` the cleanup command or explicit cleanup step for the active session

Do not replace the cleanup line with a generic note like "clean up later". Return the actual cleanup command.

## Refresh Behavior

- This skill supports one active preview session at a time
- Re-running the preview command for the same Markdown file in the same live session refreshes the generated HTML in place
- Refresh keeps the same preview URL and the same generated HTML path
- If the active session is missing or dead, start a fresh preview session instead

Use the same command to refresh after edits:

```bash
python ~/.config/opencode/skills/planning-doc-preview/scripts/preview_planning_doc.py "/absolute/path/to/doc.md"
```

## Cleanup Behavior

Default cleanup point: after the user says the plan/spec/doc is approved.

Also clean up immediately if the user asks to stop or remove the preview before approval.

Cleanup command:

```bash
python ~/.config/opencode/skills/planning-doc-preview/scripts/cleanup_preview_session.py
```

Cleanup stops the temporary server, removes generated preview artifacts, removes session metadata, and leaves the source Markdown file untouched.

Repeated cleanup is safe and should succeed as a no-op when the session is already gone.

## Stale-Session Recovery

- If a prior preview session crashed or was interrupted, starting a new preview first attempts automatic cleanup of the stale session
- Only fail the workflow if that cleanup cannot succeed
- If auto-cleanup fails, return the manual cleanup command and explain that the stale session must be cleared before retrying

## Expected Failure Modes

- Missing or invalid Markdown path: fail clearly and do not start the server
- Unreadable Markdown file: fail clearly and do not start the server
- Render failure: fail clearly and do not leave an active preview session behind
- Server startup failure or port-binding failure: fail clearly and do not leave a half-active session record behind
- Stale-session cleanup failure: stop and return the manual cleanup command

## Operator Notes

- Preview a file: run `python ~/.config/opencode/skills/planning-doc-preview/scripts/preview_planning_doc.py "/absolute/path/to/doc.md"`
- Refresh after edits: run the same command again for the same file; the URL stays stable within the active session
- Clean up after approval or on request: run `python ~/.config/opencode/skills/planning-doc-preview/scripts/cleanup_preview_session.py`
- Expect local-only output: a localhost preview URL plus a temporary HTML artifact outside the repo source file
