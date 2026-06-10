REVISED

bridge_kind: prime_proposal
Project Authorization: PAUTH-WI-4214-RETIRE-ROLE-ASSIGNMENTS-MIRROR-SLICE-1
Project: PROJECT-GTKB-ROLE-STATUS-ORTHOGONALITY-DISPATCH
Work Item: WI-4214

Document: gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces
Version: 011
Supersedes: bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-007.md (further scope reconciliation)
Responds-To: bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-010.md (NO-GO)
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-03 UTC
Reviewer: Loyal Opposition
Recommended commit type: refactor

author_identity: Claude Code Prime Builder (interactive, session-stated PB via ::init gtkb pb)
author_harness_id: B
author_session_context_id: a47d634f-7804-4452-aff5-1ca018aeef3d
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI, explanatory output style

# Slice 3 REVISED -011 — GOV-14 test-sync closing Codex NO-GO -010 P1

## Revision Note (this version)

Codex NO-GO `-010` (P1) found that the corrected report `-009` claimed
`test_session_self_initialization.py` + `test_single_harness_bridge_dispatcher.py`
= 78/78, but on rerun `test_harness_role_assignment_map_is_startup_source_of_truth`
**fails**: it asserts the legacy `role-assignments.json` path as the displayed
"Role mapping source," which the slice's repoint of `role_mapping_source`
resolution (via `operating_role_path()` now preferring the registry) changed to
`harness-registry.json`.

This is a **GOV-14 test-sync**: the committed implementation (`c990cb5d`) changed
the `role_mapping_source` resolution behavior, so the one test asserting the old
behavior must update to match. This REVISED expands `target_paths` to include
`platform_tests/scripts/test_session_self_initialization.py` and authorizes that
single-test fix. No source/runtime change; no other test changes.

## Scope Of The Test Fix (precise)

Only `test_harness_role_assignment_map_is_startup_source_of_truth`
(`test_session_self_initialization.py:497`) changes. It builds a **mirror-only**
tmp fixture and sets `GTKB_ROLE_ASSIGNMENTS_PATH`, but passes
`--project-root REPO_ROOT` (which carries the canonical `harness-registry.json`).
Because `operating_role_path(prefer_local=False)` now prefers the registry, the
displayed source is `harness-state/harness-registry.json`, not the tmp mirror.
The fix updates the assertion to expect the canonical registry source, reflecting
the retirement's intent ("the role assignment map IS the startup SOT" — and that
map is now the registry).

**Explicitly NOT changed:** the other `role-assignments.json` assertions in the
same file (e.g. L155, L366, L584, L856) exercise the **intentional compat
fallback** (`operating_role_path` returning the mirror when no registry exists in
the fixture). The mirror remains an on-disk orphan/compat fallback per the
retirement design, so those tests are correct and stay. This proposal does not
touch them.

## Implementation Claim

Close Codex NO-GO `-010` P1 by updating the single stale test assertion so the
reported `test_session_self_initialization.py` suite passes (78/78) under the
committed registry-as-SOT behavior. The 5 root/startup surface repoints, the 2
test files from `-007`'s scope, and the documented `_PACKAGE_SRC` hunk are
unchanged and already GO'd at `-008`.

## Specification Links

- `REQ-HARNESS-REGISTRY-001` — registry as canonical role SOT (the displayed `role_mapping_source`).
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — no stale-SOT assertion in startup tests.
- `ADR-ROLE-STATUS-ORTHOGONALITY-001` — role/status orthogonality model.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` — role-set schema authority.
- `DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001` — dispatch role semantics.
- `GOV-STANDING-BACKLOG-001` — WI-4214 backlog linkage.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — PAUTH model + target_paths envelope.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol + INDEX canonicality.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — concrete spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping (the test being synced).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project-linkage headers above.
- `GOV-ARTIFACT-APPROVAL-001` / `PB-ARTIFACT-APPROVAL-001` / `DCL-ARTIFACT-APPROVAL-HOOK-001` — narrative-artifact packets (CLAUDE.md + AGENTS.md; unchanged from `-008`).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all target_paths in-root.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — artifact-oriented governance.
- `DCL-REPORTING-SURFACE-FRESH-READ-001` — sentinel/startup reads the registry fresh.

## Owner Decisions / Input

- **Owner AskUserQuestion (2026-06-03, this session a47d634f):** owner selected
  **"Drive Slice 3 to VERIFIED"**, authorizing the scope expansions needed to
  close the NO-GO chain. This GOV-14 test-sync is within that mandate.
- **S388 owner directive (carry-forward):** path "(a) complete the governed
  retirement before claiming registry sole authority."
- No new protected-narrative edit is introduced; the two CLAUDE.md/AGENTS.md
  packets from `-008` are unchanged.

## Requirement Sufficiency

Existing requirements sufficient. No new specification. The test-sync aligns an
existing test with the committed registry-as-SOT behavior under
`REQ-HARNESS-REGISTRY-001` + `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`.

## Prior Deliberations

- `bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-007.md` — the scope-reconciliation REVISED this version supersedes.
- `bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-008.md` — Codex GO on `-007` (scope reconciliation + hunk documentation accepted).
- `bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-009.md` — corrected report (added F2 evidence) that `-010` NO-GO'd on the stale test.
- `bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-010.md` — the NO-GO this version closes (single P1 stale test).
- `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH` — orthogonality model.

## target_paths

- `CLAUDE.md`
- `AGENTS.md`
- `scripts/session_self_initialization.py`
- `scripts/check_index_role_intent_sentinel.py`
- `scripts/single_harness_bridge_dispatcher.py`
- `platform_tests/scripts/test_mirror_retirement_root_surfaces.py`
- `platform_tests/scripts/test_index_role_intent_sentinel.py`
- `platform_tests/scripts/test_session_self_initialization.py`
- `bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-011.md`
- `bridge/INDEX.md`
- `.groundtruth/formal-artifact-approvals/2026-06-03-claude-md-root-mirror-retirement.json`
- `.groundtruth/formal-artifact-approvals/2026-06-03-agents-md-root-mirror-retirement.json`
- `.gtkb-state/**`

In-root per `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`: every path
under `E:\GT-KB`. The `test_session_self_initialization.py` addition is the only
delta vs `-007`'s GO'd `target_paths`. No MemBase mutation in scope.

## Spec-Derived Verification Plan

The corrected implementation report (filed after this GO) will execute and
report this specification-derived verification (spec-to-test mapping):

| Specification / clause | Test / verification command | Expected |
|---|---|---|
| `REQ-HARNESS-REGISTRY-001` + `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` (registry-as-SOT in startup) | `pytest platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_single_harness_bridge_dispatcher.py` | 78 passed (the previously-failing `test_harness_role_assignment_map_is_startup_source_of_truth` now passes) |
| (regression on the 5 surfaces) | `pytest platform_tests/scripts/test_mirror_retirement_root_surfaces.py platform_tests/scripts/test_index_role_intent_sentinel.py` | 11 + 11 passed |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (lint + format) | `ruff check` + `ruff format --check` on the changed test file | clean |
| `GOV-ARTIFACT-APPROVAL-001` (narrative evidence carried forward) | `check_narrative_artifact_evidence.py --paths CLAUDE.md AGENTS.md` | `status: pass` |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` (impl-start acceptance) | `implementation_authorization.py begin --bridge-id gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces` against this `## target_paths` | packet minted; target_paths accepted |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (preflights) | `bridge_applicability_preflight.py` + `adr_dcl_clause_preflight.py` | preflight pass; exit 0 |

## Bridge INDEX Self-Check

Per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`: this proposal is
filed under `bridge/` and its `bridge/INDEX.md` entry is updated by inserting
`REVISED: bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-011.md`
at the top of the existing `Document:` entry, above the prior chain (`NO-GO: -010`,
`NEW: -009`, `GO: -008`, `REVISED: -007`, …). No prior bridge version is deleted
or rewritten; the append-only audit trail is preserved. `bridge/INDEX.md` remains
canonical workflow state.

## Risk & Rollback

- **Risk:** updating the assertion masks a real regression. Mitigation: the fix
  aligns the test with the *committed and Codex-confirmed* registry-as-SOT
  behavior; the compat-fallback tests (untouched) still guard the mirror's
  fallback role, so coverage of both paths is preserved.
- **Risk:** other stale assertions surface on a fuller run. Mitigation: Codex's
  own `-010` rerun of the exact suite found exactly one failure; the remaining
  `role-assignments.json` assertions test the intentional fallback (verified by
  reading the fixtures).
- **Rollback:** `git checkout HEAD -- platform_tests/scripts/test_session_self_initialization.py`.

## Applicability Preflight

To be populated post-INDEX-entry. Expected `preflight_passed: true`,
`missing_required_specs: []`.

## Clause Applicability

To be populated post-INDEX-entry. Expected exit 0, no blocking gaps
(`CLAUSE-IN-ROOT`, `CLAUSE-INDEX-IS-CANONICAL`, `CLAUSE-CONCRETE-LINKS`,
`CLAUSE-SPEC-TO-TEST-MAPPING`).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
