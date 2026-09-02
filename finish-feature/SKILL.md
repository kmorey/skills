---
name: finish-feature
description: "Deliver and safely retire a completed feature workspace from direct Codex, Herdr, or another external agent: verify the exact commit is retained remotely, stop its review app and worktree-owned Docker resources, then remove a clean linked worktree and local branch. Use when the user asks to finish, close, archive, or clean up completed feature work; do not use merely to open a pull request, merge, deploy, or discard unfinished work."
---

# Finish Feature

Provide the external-agent equivalent of Fleet's guarded `!finish` lifecycle.
Finish is complete only when the exact feature commit is retained remotely,
runtime resources owned by the workspace are gone, and a removable linked
worktree and its local branch are gone. Preserve primary and adopted checkouts.

Read the repository instructions before inspecting or changing anything. Use
the repository's own delivery and cleanup rules when they are stricter.

## Deliver the exact head

Resolve the canonical worktree root, local branch, intended target, remote, and
`HEAD`. Identify whether this is the primary checkout, a linked worktree, or a
Fleet-managed workspace. Keep these identities explicit throughout the run.

The workspace must be clean before retirement. Commit intended feature changes
through the repository's normal workflow. Preserve unrelated changes and stop
for direction when ownership is ambiguous. This skill never treats invocation
as permission to discard changes.

Fetch the canonical remote. The exact `HEAD` is retained when either:

- it is reachable from the fetched remote target branch; or
- an authenticated forge query verifies that an open, closed, or merged pull
  request contains that commit.

A local commit, stale remote-tracking ref, or pushed branch without a verified
pull request is insufficient. When reviewable feature work is not yet retained,
invoke the `open-pr` skill if installed. Otherwise perform its host-neutral
equivalent: synchronize, run the repository delivery gate at the final head,
push, open or update the pull request, and verify its remote head. This skill
does not authorize merging or deployment.

## Preview retirement

Build a read-only retirement preview containing:

- canonical worktree path, ownership, branch, target, and full `HEAD` SHA;
- clean/dirty status and every changed or untracked path;
- the fetched remote ref or verified pull-request URL retaining `HEAD`;
- Fleet review-app status for this exact worktree; and
- every Docker Compose project, container, and non-default network whose
  `com.docker.compose.project.working_dir` resolves within the worktree.

Inspect Docker and Fleet with host permissions when the runtime requires them.
Use the `fleet-review-apps` skill when installed. Resolve `fleet` from `PATH`,
then fall back to
`~/.local/share/hermes-fleet/current/scripts/fleet`. An unavailable Docker
daemon is an unknown cleanup state, not proof that no resources exist.

Classify the preview:

- **cleanup**: a clean, identity-verified linked worktree whose `HEAD` is
  retained remotely;
- **preserve**: the primary checkout, an adopted workspace, or a workspace
  whose owning lifecycle must detach it; stop owned runtime resources but keep
  its directory and branch; or
- **blocked**: dirty, unretained, unverifiable, or ambiguously owned work.

Show the preview and exact proposed deletions before cleanup. Require explicit
confirmation for those targets unless the user's current request already
approved removal of that exact linked worktree and branch.

## Re-verify and clean up

Immediately before mutation, regenerate the preview. Restart review if the
path, ownership, branch, `HEAD`, worktree status, remote retention evidence, or
Docker inventory changed.

For an approved `cleanup` or `preserve` plan:

1. Run `fleet review down` from the exact worktree when a Fleet review runtime
   exists. A failure preserves the worktree for a safe retry.
2. Re-inspect Docker labels. Remove only the unchanged Compose containers and
   matching non-default Compose networks proven to belong below this worktree.
   Retain all volumes. A new or relabelled resource invalidates the preview.
3. Recheck that the worktree is clean and `HEAD` still has the same remote
   retention evidence.
4. For `cleanup`, run `git worktree remove --force` from another registered
   checkout, targeting the exact canonical path. Then delete only the verified
   local feature branch. Keep every remote branch.
5. For `preserve`, leave the directory and local branch in place.

If the path is Fleet-managed and its coordinator record is still active, use
Fleet's owning finish lifecycle when it is callable. When it is not callable,
classify the workspace as `preserve`; removing it behind Fleet would corrupt
the lifecycle record.

## Completion record

Verify and report the remote retention evidence, stopped review runtime,
removed Compose resources, retained volumes, and the disposition of the
worktree and local branch. State every preserved item and blocker explicitly.
