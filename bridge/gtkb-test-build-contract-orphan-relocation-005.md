NEW

# Implementation Report — Relocate orphaned test_build_contract.py out of the platform test tree (WI-3371)

bridge_kind: implementation_report
Document: gtkb-test-build-contract-orphan-relocation
Version: 005
Author: Prime Builder (Claude, harness B)
Date: 2026-05-18 UTC
Session: S359
Implements: bridge/gtkb-test-build-contract-orphan-relocation-003.md (Codex GO at bridge/gtkb-test-build-contract-orphan-relocation-004.md)

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3371

target_paths: ["platform_tests/test_host/test_build_contract.py", "applications/Agent_Red/tests/test_host/test_build_contract.py"]

This is the post-implementation report for the GO'd proposal at
`bridge/gtkb-test-build-contract-orphan-relocation-003.md` (Codex GO at
`-004`). IP-1 — the tracked `git mv` relocating the orphaned Agent Red test out
of the GT-KB platform test tree — is complete and verified.

## Implementation Summary

IP-1 executed exactly as approved: a single content-preserving tracked rename.

- Command: `git mv platform_tests/test_host/test_build_contract.py applications/Agent_Red/tests/test_host/test_build_contract.py`, run in canonical `E:\GT-KB`.
- `git status --short` reports `R  platform_tests/test_host/test_build_contract.py -> applications/Agent_Red/tests/test_host/test_build_contract.py` — a tracked rename with 0 content lines changed.
- The implementation-start authorization packet was created from the `-004` GO via `python scripts/implementation_authorization.py begin --bridge-id gtkb-test-build-contract-orphan-relocation`; its `target_path_globs` are exactly the two relocation paths.
- No other path was touched. Per Codex's GO implementation constraints, `platform_tests/test_host/__pycache__/` and the now-empty `platform_tests/test_host/` directory were NOT deleted — they are explicitly out of scope under this GO.

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001` — governs the reliability fast-lane this fix is routed through; defect-origin, no new behavior, small single-concern change.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` — owner-decision record establishing the fast-lane (PROJECT-GTKB-RELIABILITY-FIXES plus the standing authorization plus the GOV spec).
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol; this report follows the NEW/REVISED/GO/NO-GO/VERIFIED workflow with `bridge/INDEX.md` as canonical state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — the linked specifications are carried forward from the GO'd proposal.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — this report carries the spec-to-verification mapping forward with the exact commands run and the observed results.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — the relocation enforces the in-root placement contract: the Agent Red test now resides under `applications/Agent_Red/`, not in the GT-KB platform test tree; both paths are in-root under `E:\GT-KB`.
- `GOV-STANDING-BACKLOG-001` — WI-3371 is the tracked backlog work item.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — the fix is delivered as a durable, governed bridge-tracked change.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the work is governed through the bridge artifact chain and the linked work item.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — artifact-lifecycle triggers; this fix is a pure file relocation with no new or modified code artifact, so it triggers no test-artifact creation.

## Prior Deliberations

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` (outcome `owner_decision`, S351) — established the reliability fast-lane under which this fix is routed.
- A Deliberation Archive search (`search_deliberations` for `test_build_contract platform_tests collection orphan`, `isolation 18.E.1 test_host atomic move`, and `Agent Red test relocation platform tests`) returned no prior decision on this orphaned file. Codex independently re-ran the same three searches across both the `-002` and `-004` reviews and likewise found no matches. WI-3371 is a newly-discovered defect.

## Owner Decisions / Input

- 2026-05-18, owner decision via AskUserQuestion: presented with the diagnosis and three fix options, the owner selected **relocate to Agent Red**. This implementation executes the selected option.
- Standing pre-approval: `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (owner decision `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`) covers WI-3371 by active project membership. Per `GOV-RELIABILITY-FAST-LANE-001`, no per-fix deliberation, per-fix project authorization, or formal-artifact-approval packet is required.
- No blocking owner decision is pending. This report needs only a Loyal Opposition VERIFIED.

## Specification-Derived Verification Evidence

Spec-to-verification mapping (per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`), carried forward from the GO'd proposal with observed results:

| Linked requirement / specification | Required evidence | Command | Observed result |
|---|---|---|---|
| WI-3371 — `pytest platform_tests/` must collect without the orphan abort | full-tree collection completes with 0 errors | `python -m pytest platform_tests/ -q --collect-only` | `2464 tests collected in 1.05s`; 0 collection errors; no `ModuleNotFoundError`; no `Interrupted` line. PASS |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — Agent Red test resides under `applications/Agent_Red/` | source path absent, destination path present after the tracked rename | `git status --short` + filesystem existence check | `R platform_tests/test_host/test_build_contract.py -> applications/Agent_Red/tests/test_host/test_build_contract.py`; source absent; destination present. PASS |

Before/after contrast:

- Before (pre-implementation reproduction, from `E:\GT-KB`): `python -m pytest platform_tests/ -q --collect-only` -> `ModuleNotFoundError: No module named 'test_host'`, `Interrupted: 1 error during collection`, `no tests collected`.
- After (this implementation): `python -m pytest platform_tests/ -q --collect-only` -> `======================== 2464 tests collected in 1.05s ========================`, no ERROR section, no `Interrupted` line.

The GO'd proposal estimated "~2454 tests collected"; the observed 2464 reflects the live `platform_tests/` tree at implementation time (the count is not pinned and drifts with concurrent test additions). The acceptance criterion is 0 collection errors, which is met.

## Acceptance Criteria Check

- MET — IP-1 landed; `platform_tests/test_host/test_build_contract.py` no longer exists at that path and `applications/Agent_Red/tests/test_host/test_build_contract.py` exists, as a tracked `git mv` rename.
- MET — `python -m pytest platform_tests/ -q --collect-only` completes with 0 collection errors (2464 tests collected).
- MET — mandatory applicability and clause preflights PASS for this bridge id: applicability preflight on the `-003` operative file reported `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`; clause preflight reported 0 blocking gaps (exit 0). Codex's `-004` GO independently reproduced both.

## Codex GO Implementation Constraints — Compliance

Per `bridge/gtkb-test-build-contract-orphan-relocation-004.md` "Implementation Constraints For Prime Builder":

- MET — proceeded only after creating an implementation-start authorization packet from the `-004` GO.
- MET — implementation kept to the approved tracked rename between the two `target_paths`.
- MET — `platform_tests/test_host/__pycache__/` and the empty directory were NOT deleted under this GO.
- MET — this post-implementation report includes the executed `pytest --collect-only` result and the source/destination path evidence.

## Files Changed

- Renamed (tracked `git mv`, content-preserving, 0 content lines changed): `platform_tests/test_host/test_build_contract.py` -> `applications/Agent_Red/tests/test_host/test_build_contract.py`.

## Recommended Commit Type

`fix:` — a defect repair restoring `pytest platform_tests/` collection, which the stranded orphan broke. The diff is a pure file relocation; no new capability surface is added. Suggested commit subject: `fix(platform-tests): relocate orphaned test_build_contract.py to Agent Red test tree (WI-3371)`.

## Risks / Rollback

Rollback: `git mv applications/Agent_Red/tests/test_host/test_build_contract.py platform_tests/test_host/test_build_contract.py`. Fully reversible; one tracked rename, no content change.

## Commit Status

Not yet committed. Per the bridge protocol, the commit follows Codex `VERIFIED`. The rename is currently staged in canonical `E:\GT-KB` and has not been bundled with any unrelated change.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
