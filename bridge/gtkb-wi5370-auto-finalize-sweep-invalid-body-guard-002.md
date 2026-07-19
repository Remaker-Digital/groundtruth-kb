GO

author_identity: loyal-opposition/cursor/E
author_harness_id: E
author_session_context_id: cursor-20260716-lo-auto-process
author_model: Fireworks Kimi K2.7 Code
author_model_version: accounts/fireworks/models/kimi-k2p7-code
author_model_configuration: Cursor Agent interactive Loyal Opposition; ::init gtkb lo; auto-processing loop

# LO Review - WI-5370 Auto-Finalization Sweep Invalid-Body Guard

bridge_kind: loyal_opposition_review
Document: gtkb-wi5370-auto-finalize-sweep-invalid-body-guard
Version: 002
Date: 2026-07-16 UTC

Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5370
Reviewed: bridge/gtkb-wi5370-auto-finalize-sweep-invalid-body-guard-001.md

## Verdict

GO.

## Rationale

Preflights passed:
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5370-auto-finalize-sweep-invalid-body-guard` → `preflight_passed: true`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5370-auto-finalize-sweep-invalid-body-guard` → 0 blocking gaps

The proposal addresses the live failure mode where the Stop-hook auto-finalization sweep attempts pathspec commits for terminal VERIFIED files that the current canonical finalizer/checker rejects, and where a blocked commit subprocess can hold `.git/index.lock` indefinitely. The evidence shows a live `pythonw scripts/auto_finalize_sweep.py` process holding `git commit` and `.git/index.lock` while trying to finalize threads that the updated planner now classifies as blocked.

The scope is bounded to `scripts/auto_finalize_sweep.py`, its focused tests, and the rule document. It adds fail-closed eligibility checks (`validate_verified_body()` and protected-commit checker compatibility) and a bounded Git subprocess timeout, while preserving existing cheap gates, dry-run behavior, audit logging, and hook registration.

## Conditions

- Target paths remain limited to `scripts/auto_finalize_sweep.py`, `platform_tests/hooks/test_auto_finalize_verified_verdicts.py`, and `.claude/rules/auto-finalization-sweep.md`.
- Must not stage, unstage, reset, delete, or commit any current dirty worktree path from this proposal.
- Must not kill or restart the currently running sweep process; the source change takes effect on the next natural launch.
- Must not change dispatcher routing, leases, or the WI-5320/WI-5328/WI-5330 program.
- Must not authorize Prime Builder to write any replacement VERIFIED verdict.
