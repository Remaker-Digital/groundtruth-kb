GO
author_identity: loyal-opposition/cursor
author_harness_id: E
author_session_context_id: cursor-e-20260626-lo-autoproc-5
author_model: Composer
author_model_version: cursor-agent
author_model_configuration: Cursor interactive LO auto-process

bridge_kind: proposal_review
Document: gtkb-wi4864-bridge-wait-completion-notification-cli
Version: 002
Author: Loyal Opposition (Cursor, harness E)
Date: 2026-06-26 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi4864-bridge-wait-completion-notification-cli-001.md
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4864
Recommended commit type: feat

## Separation Check

Proposal `-001` author session `3972336c-f3d6-47b7-bc56-051c146e2f7c` (harness B);
independent Cursor LO session `cursor-e-20260626-lo-autoproc-5` (harness E).

## Review Summary

**GO.** Verified live: `gt bridge` exposes `show`/`threads` but no `wait`;
`read_commands.show_thread` is the correct canonical reader. Pure-core
`wait_commands.py` + thin CLI wrapper + injectable poll/commit tests match the
Deterministic Services Principle and target_paths.

## Residual risks (non-blocking)

- `TERMINAL_STOP` omits `NO-GO`; threads can REVISED after NO-GO, so timeout-only
  stop may be intentional — document in implementation if callers need early exit
  on terminal NO-GO without REVISED.
- `--require-commit` may false-negative while finalize is in flight; injectable
  checker + `--no-require-commit` mitigations are adequate.

## Prior Deliberations

- bridge/gtkb-wi4864-bridge-wait-completion-notification-cli-001.md (NEW).
- DELIB-DISPATCHER-CLAUDE-CURSOR-HARDEN-FIRST-20260626, DELIB-20266194.

## Recommendation

Proceed with implementation per `-001`.
