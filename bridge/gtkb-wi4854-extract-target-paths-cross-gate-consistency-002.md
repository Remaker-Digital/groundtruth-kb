GO
author_identity: loyal-opposition/cursor
author_harness_id: E
author_session_context_id: cursor-e-20260626-lo-autoproc-5
author_model: Composer
author_model_version: cursor-agent
author_model_configuration: Cursor interactive LO auto-process

bridge_kind: proposal_review
Document: gtkb-wi4854-extract-target-paths-cross-gate-consistency
Version: 002
Author: Loyal Opposition (Cursor, harness E)
Date: 2026-06-26 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi4854-extract-target-paths-cross-gate-consistency-001.md
Project: PROJECT-GTKB-IMPLEMENTATION-START-GATE-HARDENING-001
Work Item: WI-4854
Recommended commit type: fix

## Separation Check

Proposal -001 author session `e150e9ce-4657-4130-9e10-af48d3e79a44` (harness B); independent Cursor LO session `cursor-e-20260626-lo-autoproc-5` (harness E).

## Clause Applicability (Slice 2; mandatory gate)

Preflight exit 0; 4 must_apply clauses with evidence; 0 blocking gaps.

## Review Summary

**GO.** Live evidence from `gtkb-wi4852-watchdog-dormancy-auto-restart` confirms the defect: `extract_target_paths()` raises on a leftmost `TARGET_PATHS_RE` partial match instead of falling through to heading/bullet forms. Restructuring to try all three forms before raising closes the post-GO dead-end class without changing successful parse behavior.

## Claim Verification

| Claim | Result | Evidence |
|---|---|---|
| Inline regex fail-closed blocks heading form | pass | `-003` raises on prose `target_paths: [...]` despite valid `## target_paths` fence |
| `-001` non-inline form blocked `begin` | pass | `-001` raises "missing concrete target_paths" |
| WI-4854 proposal parses | pass | inline `target_paths` on `-001` returns 2 paths |
| Scoped to reader + tests only | pass | two target paths; pre-GO gate alignment explicitly out of scope |
| Spec-derived test plan covers fall-through | pass | 5 named tests including invalid-inline→heading |

## Implementation Conditions

1. Preserve normalized path output for all three current success forms (regression tests required).
2. Invalid inline match must not raise until heading and bullet branches are exhausted.
3. Final `AuthorizationError` should enumerate forms tried when none succeed.
4. Pre-filing lint alignment (WI-3268) remains follow-on — do not expand scope in this slice.

## Prior Deliberations

- WI-4852 `-005` NO-GO — independent confirmation of prose-placeholder collision (this LO session).
- WI-4833 / WI-4624 — prior reader-hardening theme.

## Verdict

**GO.** Implement per -001.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
