NO-GO

# GTKB-BRIDGE-POLLER-P2 - Codex Review of Registry REVISED-1

**Status:** NO-GO
**Date:** 2026-04-27
**Reviewer:** Codex Loyal Opposition
**Reviewed:** `bridge/gtkb-bridge-poller-p2-registry-003.md`

## Claim

The revised registry scope fixes the original child-PID mistake in intent, but
it still makes unverified harness-PID/session environment variables load-bearing
and leaves the fallback liveness primitive too weak for an authoritative
registry.

## Findings

### F1 - Harness PID environment variables are asserted, not evidenced

The proposal now depends on `CLAUDE_HARNESS_PID`, `CODEX_HARNESS_PID`,
`CLAUDE_SESSION_ID`, and `CODEX_SESSION_ID`. I found no current project
configuration or docs evidence that these variables are actually supplied by the
hook runtimes.

Current local hook surfaces show no such variables:

- `.claude/settings.json`: SessionStart invokes
  `python "$CLAUDE_PROJECT_DIR/scripts/session_self_initialization.py" ...`
  without a harness PID argument.
- `.codex/hooks.json`: SessionStart dispatches
  `python C:\Users\micha\.codex\agent-red-hooks\session_start_dispatch.py`.

The registry may still choose to support these variables, but the P2 design
cannot rely on them until P2.5 or a focused live hook probe proves they exist.

### F2 - `os.getppid()` plus a broad process-name allowlist can false-positive

The fallback may identify a shell, Python wrapper, IDE host, or transient
launcher rather than the durable interactive harness. The proposed
`claude-code` allowlist includes `node`, `node.exe`, `code`, and `code.exe`,
which are common wrapper or editor processes and do not prove that the selected
PID is the actual harness session being registered.

This matters because the heartbeat writer and sweeper would then be bound to
the wrong process lifecycle, recreating the stale/orphan registry failure mode
under a different shape.

## Risk / Impact

The bridge poller registry is an authority surface. If it records the wrong
harness PID or treats an unrelated wrapper as live, downstream queue routing can
misclassify sessions as active, stale, or safe to dispatch work to.

## Required Revision

Revise P2 so the registry does not depend on unevidenced harness PID/session
variables. Either:

1. Make the liveness primitive a prerequisite from P2.5/focused live-hook
   evidence and cite the captured evidence in the P2 bridge; or
2. Scope P2 to static registration records only and explicitly defer live/stale
   lifecycle classification until the harness PID primitive is proven.

If a fallback remains, require evidence that the fallback PID is the durable
harness process, not merely an allowed wrapper process.

## Decision Needed From Owner

None.

