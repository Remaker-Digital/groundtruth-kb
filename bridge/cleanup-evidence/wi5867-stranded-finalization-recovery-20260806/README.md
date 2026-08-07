# WI-5867 stranded file-only VERIFIED finalization — recovery evidence

Date: 2026-08-06 UTC
Actor: loyal-opposition/goose/G
Session: G-2026-08-06T20-01-18Z
Recovery route: WI-5825-class poisoned-row / finalization-recovery procedure (owner decision B'')

## Summary

The `--finalize-verified` atomic finalization for
`gtkb-wi5867-protected-commit-gate-contention-attribution` was interrupted
mid-commit (300s shell timeout killed the helper process after the verdict was
written and published but before the git commit landed). This left a
**file-only VERIFIED** — the exact stranding class tracked by WI-5825 / WI-5939 /
WI-5941 / WI-5688 / WI-5783.

## Stranded state (verified 2026-08-06)

- **Bridge state:** thread latest status = **VERIFIED** at
  `bridge/gtkb-wi5867-protected-commit-gate-contention-attribution-004.md`
  (published), because the `-004` verdict file was written via the governed
  writer.
- **Git state:** `-004` verdict file is **untracked** (`??`); the two
  implementation files remain **modified/uncommitted** (`M`):
  `scripts/check_protected_commit_authorization.py`,
  `platform_tests/scripts/test_protected_commit_evaluation_bound.py`.
  No finalization commit landed (HEAD = `b330fb85f`, the predecessor-chain
  commit only).
- **Publication capability:** pending sidecar
  `.gtkb-state/bridge-publication-pending/gtkb-wi5867-protected-commit-gate-contention-attribution-004-c4fefeace5500fbb.json`
  - capability_hash: `sha256:419d5aedb3b58d1ae5f7fbbf6e3de4edb0e639b7381ae12fda1b34ac800b5186`
  - content_digest: `sha256:cda7284d08045f7f1ed6f8033b189e3b2e31be3780c2ad2c806a7a8b8deec21b`
  - document_name: `gtkb-wi5867-protected-commit-gate-contention-attribution`
  - version: 4, status: VERIFIED, session_id: `G-2026-08-06T20-01-18Z`
  - Capability row state: **`recovery_required`** (the poisoned-row class).
    `recover_bridge_publication(mode="rollback")` refuses this transition
    (`RegistryAuthorizationError: bridge publication cannot be rolled back from
    recovery_required`).
- **Work-intent claim:** draft claim for the thread **expired**
  (TTL 21:40:35Z, `claim_kind: draft`, `expired: true`).

## Implementation substance (verified)

The implementation itself verified clean before finalization: all code anchors
present, focused suite reproduced exactly (39 passed / 1 disclosed pre-existing
WI-5946 stale-ceiling failure), spec-to-test mapping complete, fail-closed
bound semantics preserved, both mandatory preflights passed in finalization
phase (git_commit + protected_mutation allowed). **VERIFIED-eligible**; blocked
only by the interrupted atomic commit and the resulting `recovery_required`
capability row.

## Required recovery (WI-5825-class)

Reconcile the stranded `-004` file-only VERIFIED through the designated
poisoned-row / finalization-recovery procedure (WI-5825 authority), then commit
the verified implementation paths + verdict in one atomic transaction. A manual
delete-and-rerun was explicitly declined by the owner in favor of the
WI-5825-class procedure.

No dispatcher, TAFE, source, test, Git index, commit, push, release,
deployment, credential, or external-system mutation was performed by this
evidence capture. The stranded `-004` file and its capability row were left
intact for the recovery procedure.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
