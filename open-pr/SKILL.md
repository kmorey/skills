---
name: open-pr
description: "Finish a completed feature branch for review: synchronize it with its target, run the repository delivery gate, collect required visual proof, create or update a pull request, and notify explicitly linked work items. Use when a change is ready to submit, not to merge or merely review a pull request."
---

# Open Pull Request

Deliver one completed feature as a reviewable pull request. The delivery is
complete only when the current head is based on its intended target, the
repository's delivery gate has passed at that head, the pull request points at
it, and every explicitly linked work item has the same delivery record.

## Establish the delivery record

Read the repository instructions and current work context first. Resolve:

- the feature branch and intended target branch;
- any existing open pull request for the branch, preserving its target unless
  the user directs a change;
- the repository-defined delivery gate; and
- issue, ticket, or project-record URLs explicitly associated with the work.

Prefer an explicit target, then the existing pull request base, then the
repository's configured default branch. Do not infer linked work items from a
similar title, commit message, or search result.

Ensure the intended feature work is committed and the worktree is clean before
rebasing. Stop for user direction if the branch has no reviewable change, the
target is ambiguous, or a rebase would alter a pull request's agreed target.

## Synchronize before validation

Fetch the target from its canonical remote and rebase the feature branch onto
that remote-tracking ref. Resolve every conflict deliberately, then verify that
the target is an ancestor of `HEAD`.

Run validation after this rebase. Immediately before the delivery push, fetch
the target again and repeat the ancestry check. If it advanced, rebase again and
rerun the delivery gate; a prior green result describes the wrong commit.

Push only after the gate passes. For an already-published rebased branch, use
`--force-with-lease`, never an unguarded force-push.

## Validate and collect visual proof

Run every delivery check required by the repository instructions from the exact
rebased head. A nonzero result stops delivery. Repair the failure, commit the
repair, synchronize again if the target advanced, and rerun the gate. Record the
exact successful command and validated commit.

Determine whether the change affects a user-visible interface. For UI changes,
use the `visual-proof` skill when it is installed. The proof must come from the
rebased, validated head and remain inspectable after this turn. For a non-UI
change, record that visual proof is not applicable.

If code or configuration changes after the successful gate, the gate and any UI
proof are stale. Repeat the affected validation and proof collection.

## Create or update the pull request

Use the forge client authenticated for the repository remote, such as `gh`,
`tea`, or `glab`. Inspect the remote and existing pull requests before choosing
the client; update an existing pull request instead of creating a duplicate.
Always supply the base and head explicitly when the client supports it.

Give reviewers a compact body containing:

- the implemented outcome and why it resolves the work;
- the exact successful delivery-gate command and validated commit;
- visual-proof status, with an accessible proof link or attachment when the
  forge supports one; and
- every explicitly linked work-item URL.

After the forge returns, verify the pull request URL, base branch, head branch,
and that its remote head contains the validated commit. A pushed branch is not
a substitute for an open pull request.

## Update linked work items

After the pull request is verified, post the same delivery record to every
explicitly linked work item. Use an installed tracker skill or the authenticated
tracker client for that exact URL. The update states the feature outcome,
pull-request URL, validated commit, successful gate command, and visual-proof
status. Do not transition or close a work item unless the user asks.

If authentication requires interactive user action, use the current runtime's
supported handoff. In a Fleet conversation whose developer instructions define
operator terminal cards, emit that card. In direct Codex or a plain terminal,
state the exact authentication command or browser action and resume only after
the authenticated update can be verified.

If a linked work item cannot be updated, report the exact blocker. The pull
request may exist, but the full delivery remains incomplete.

## Completion record

For UI changes, put the current visual proof first. Then make the record stand
alone: summarize the issue and implemented outcome, include the pull-request URL
and target, the validated commit and successful gate command, and the result for
every linked work item. State that no deployment occurred unless it was
separately verified.
