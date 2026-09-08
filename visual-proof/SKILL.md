---
name: visual-proof
description: Capture and deliver current visual evidence for user-visible interface changes. Use before reporting UI work complete, while preparing a pull request with UI changes, or when the user asks for screenshots or visual QA evidence. Do not use for changes with no visible interface effect.
---

# Visual Proof

Produce the smallest set of current images that lets the user inspect the
implemented interface. Proof is complete only when every image is from the
validated revision, shows the relevant state clearly, and remains reachable
after the response settles.

## Establish the proof surface

Read the repository's agent and development instructions. Prefer its prescribed
browser test, screenshot, or review workflow. If the application uses Fleet
review apps, use the `fleet-review-apps` skill to obtain and verify the private
HTTPS URL. Otherwise start the application through its documented local or
remote development workflow.

Exercise the actual state changed by the implementation. Capture only the
viewports and states needed to prove the outcome; include narrow and wide
layouts when responsive behavior changed. A startup page that does not expose
the changed behavior is not proof.

## Store proof through the available adapter

Use the first available destination:

1. The runtime-designated result or attachment directory, when developer
   instructions provide one.
2. A repository-prescribed untracked screenshot or test-artifact directory.
3. A private temporary directory outside the repository created for this handoff.

Keep proof out of tracked source unless the user explicitly requests committed
fixtures or documentation. Use a broadly viewable image format such as PNG,
JPEG, or WebP. Avoid secrets, personal data, authentication tokens, and
unrelated application records in the captured frame.

Before responding, verify that each proof path is a regular file, record the
viewport or device represented, and confirm that no code or configuration
changed after capture. If the revision changed, recapture.

## Preview proofs in Herdr

When `HERDR_ENV=1`, `HERDR_PANE_ID` is set, and `herdr` is available, check
`herdr plugin list --plugin kmorey.file-preview --json`. If File Preview is
installed and enabled, choose the relevant PNG proofs, JSON-encode their
absolute paths in display order, and open one gallery beside the current pane
without stealing focus:

```sh
herdr plugin pane open \
  --plugin kmorey.file-preview \
  --entrypoint viewer \
  --placement split \
  --target-pane "$HERDR_PANE_ID" \
  --direction right \
  --env 'FILE_PREVIEW_PATHS=["/absolute/path/to/first.png","/absolute/path/to/second.png"]' \
  --no-focus
```

File Preview accepts at most 24 paths and supports PNG alongside document
formats. This skill still delivers visual evidence as images. Prefer PNG for
Herdr proof galleries; retain original formats and links for additional proof.
A single PNG can use `FILE_PREVIEW_PATH` instead. The user can navigate with
Left/Right Arrow or `h`/`l`.

If the plugin is missing or disabled, continue with attachment and absolute-link
delivery and mention the preview limitation. Existing Visual Proof installations
must be relinked/reinstalled as `kmorey.file-preview`; the old plugin ID is not an
alias. For a local Herdr plugins checkout, install the File Preview dependencies
with `npm --prefix file-preview ci`, then link its directory using
`herdr plugin link "$PWD/file-preview"` from that checkout. For a released
installation, use the pinned File Preview release:

```sh
herdr plugin install kmorey/herdr-plugins/file-preview --ref v0.5.0 --yes
```

Paths are read on the plugin host beside the originating agent. Copying a path
or opening externally does not download the file or open a remote file on the
client machine. Outside the guarded Herdr environment, use attachment and
absolute-link delivery directly.

If sandboxing denies access to the Herdr socket, request the normal command
approval and retry. Do not open more than one proof pane for a handoff. A pane
failure does not replace or block the attachment and absolute-link delivery
below; mention the preview limitation briefly and continue.

## Deliver proof

Attach or embed images when the conversation supports it. Always include an
absolute Markdown link to each proof file so direct Codex and terminal clients
have an inspectable handoff even without inline image rendering. Include the
verified review URL when one exists and briefly identify the state and viewport
shown by each image.

If the current environment cannot retain or expose a generated file, report
that limitation as a blocker to visual completion. A live URL or a statement
that the UI was checked does not replace requested visual proof.

Put visual proof before the completion summary for the UI change.
