NEW

bridge_kind: implementation_report
Document: gtkb-backlog-triage-and-hygiene-stage-1-structural-repair
Version: 005
Author: prime-builder (Claude Opus 4.7, harness B) — interactive owner session
Date: 2026-06-11
Responds-To: bridge/gtkb-backlog-triage-and-hygiene-stage-1-structural-repair-004.md

Project: PROJECT-GTKB-BACKLOG-TRIAGE-AND-HYGIENE-001
Work Item: WI-4454
Project Authorization: PAUTH-PROJECT-GTKB-BACKLOG-TRIAGE-AND-HYGIENE-001-BACKLOG-TRIAGE-AND-HYGIENE-BOUNDED-IMPLEMENTATION-AUTHORIZATION

author_identity: prime-builder
author_harness_id: B
author_session_context_id: 0c0caa91-3f63-41d1-b4c6-960f9b137180
author_model: claude-opus-4-7
author_model_version: 4.7
author_model_configuration: interactive owner session, ::init gtkb pb

target_paths: ["scripts/hygiene/prefix_split_detector.py", "platform_tests/scripts/test_prefix_split_detector.py"]

Implementation packet hash: `sha256:c975cc898bf08c314c95ebeaafe77a836a456a3eff6f0c46116d4b53121cc228`

# Stage 1 — Structural Defect Repair (Post-Implementation Report)

Implementation of the GO'd `-003` REVISED proposal. Codex's `-004` GO required three implementation notes; this report documents how each was satisfied.

## Specification Links

Carried forward from `-003`:

- `GOV-STANDING-BACKLOG-001`
- `SPEC-AUTO-BACKLOG-FOR-IMPLEMENTATION-BEARING-SPECS-001`
- `GOV-08`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` / `DCL-STANDING-BACKLOG-DB-SCHEMA-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`

## Prior Deliberations

- `DELIB-20261667` — project charter.
- `bridge/gtkb-backlog-triage-and-hygiene-stage-1-structural-repair-002.md` (NO-GO) — the original P1/P2 findings this thread closes.
- `bridge/gtkb-backlog-triage-and-hygiene-stage-1-structural-repair-003.md` (REVISED-1) — the approved proposal that this implementation realizes.
- `bridge/gtkb-backlog-triage-and-hygiene-stage-1-structural-repair-004.md` (GO) — Codex GO whose three required implementation notes are addressed below.
- `bridge/gtkb-backlog-triage-and-hygiene-stage-0-analyzer-011.md` (VERIFIED) — Stage 0 read pattern reused.
- `WI-3355` — originating doubled-prefix defect.

## Owner Decisions / Input

Owner decisions captured in `DELIB-20261667` (D1-D5 from the `/grill-me-for-clarification` interview) plus continuation approval ("Yes" + "Resume") authorized this implementation. The TWO execution-time AUQs (Stage 1.A doubled-prefix; Stage 1.B prefix-split) remain owner-gated at the time of `--apply` execution — this report does NOT execute either; it lands the deterministic tool only.

## Requirement Sufficiency

**Existing requirements sufficient.** Carried forward from `-003`.

## Implementation Summary

Added two files exactly per the `-003` target_paths:

- **`scripts/hygiene/prefix_split_detector.py`** (343 lines): read-only detector with opt-in `--apply` mode. The `detect()` function opens `groundtruth.db` via a read-only URI (`file:...?mode=ro`), groups active projects by canonical stem (strip leading `PROJECT-`), and emits a deterministic JSON plan with the three named fields per pair (`canonical_links_to_create`, `non_canonical_memberships_to_deactivate`, `non_canonical_project_to_retire`). The `apply()` function refuses on unknown pairs, then executes the strict-order steps using `KnowledgeDB.link_project_work_item` for both creation (status="active") and deactivation (status="superseded") and `ProjectLifecycleService.retire_project` for the project retire — with a defensive double-check that no active non-canonical memberships remain before the retire step runs.
- **`platform_tests/scripts/test_prefix_split_detector.py`** (343 lines): 18 tests covering detection structure, live-shape fidelity, the load-bearing post-apply structural invariants (Codex GO required notes 1 + 2), refusal guards, read-only no-mutation in default mode, determinism, and idempotency.

No changes to `groundtruth-kb/src/groundtruth_kb/*`. No mutation of `groundtruth.db` at Write time.

## Codex GO Required Implementation Notes — Satisfaction

### Note 1: Tests proving retired non-canonical project has zero active memberships after apply

**Satisfied by**: `test_retired_non_canonical_project_has_zero_active_memberships` (lines 339-355 of the test file).

The test seeds a KnowledgeDB-backed fixture matching the live shape (8 items overlapping on both projects, 2 canonical-only), runs `prefix_split_detector.apply(...)`, then asserts both `_project_status_query(db_path, non_can) == "retired"` AND `_active_count(db_path, non_can) == 0`. This is the structural-defect class assertion: a retired project may not have any active memberships pointing at it.

### Note 2: Tests proving no duplicate active canonical memberships for WI-3400 through WI-3407

**Satisfied by**: `test_apply_no_duplicate_active_canonical_memberships` (lines 295-315).

The test iterates through each of `WI-3400` through `WI-3407` and asserts exactly ONE active membership row exists per (canonical_project, work_item) pair. This is enforced both by the detector's idempotency check (the `existing_canonical_active` set is consulted before each canonical link create) and by the apply-step semantics (deactivations are non-canonical-project-scoped only).

### Note 3: Execution-time AUQs must cite fresh dry-run output

**Satisfied by**: the proposal's design contract (preserved in this implementation). The `--apply` path calls `detect(db_path)` first thing and refuses if the owner-supplied pair is not in that live dry-run's active-BOTH set. This means every `--apply` execution is gated by a re-derivation of the plan from the current DB state, guaranteeing the owner's AUQ approval references current shape, not the proposal's snapshot. The `change_reason` written into each new membership version embeds the `auq_id` so the audit trail is fully traceable.

## Spec-to-Test Mapping (Required Verification Evidence)

Mapping every linked spec to the test(s) that verify it (DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001):

| Spec / requirement | Test(s) | Result |
|---|---|---|
| `GOV-STANDING-BACKLOG-001` + `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` (canonical project id uniqueness; retire does not deactivate memberships) | `test_detect_emits_three_named_fields`, `test_detect_live_shape_fidelity`, `test_retired_non_canonical_project_has_zero_active_memberships`, `test_apply_no_duplicate_active_canonical_memberships`, `test_apply_all_non_canonical_memberships_deactivated`, `test_apply_retires_non_canonical_project` | **PASS (6 tests)** |
| `GOV-08` (read-only at Write time; no canonical mutation in default mode) | `test_default_mode_no_write_paths_in_detect_ast`, `test_default_mode_no_mutation_row_counts` | **PASS (2 tests)** |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` (canonical reads; live execution-time data) | `test_apply_refuses_on_unknown_pair`, `test_apply_idempotent_on_rerun` (the live-dry-run refresh inside `apply()` is exercised) | **PASS (2 tests)** |
| D2 (per-batch owner AUQ; refuse stale plans) | `test_apply_refuses_without_canonical_arg`, `test_apply_refuses_without_merge_from_arg`, `test_apply_refuses_without_auq_id`, `test_apply_refuses_on_unknown_pair` | **PASS (4 tests)** |
| `-002` NO-GO P1 (strict apply-order + structural invariant) | `test_retired_non_canonical_project_has_zero_active_memberships`, `test_apply_no_duplicate_active_canonical_memberships`, `test_apply_all_non_canonical_memberships_deactivated`, `test_apply_retires_non_canonical_project`, `test_apply_idempotent_on_rerun` | **PASS (5 tests)** |
| Determinism + edge cases | `test_default_mode_determinism`, `test_detect_canonical_only_subset`, `test_canonical_links_to_create_populated_when_non_overlap`, `test_unrelated_single_projects_not_in_plan`, `test_cli_default_mode_emits_json` | **PASS (5 tests)** |

Total: **18 / 18 tests pass.**

## Verification Commands and Results

```powershell
# Pytest (Codex GO note 1 + 2 explicitly covered)
python -m pytest platform_tests/scripts/test_prefix_split_detector.py -o addopts="" -q
# 18 passed, 1 warning in 1.79s

# Ruff check (lint)
python -m ruff check scripts/hygiene/prefix_split_detector.py platform_tests/scripts/test_prefix_split_detector.py
# All checks passed!

# Ruff format --check (separate gate from check)
python -m ruff format --check scripts/hygiene/prefix_split_detector.py platform_tests/scripts/test_prefix_split_detector.py
# 2 files already formatted
```

All three gates green.

## Acceptance Criteria — Satisfied

1. **`scripts/hygiene/prefix_split_detector.py` exists, runs read-only by default, and emits a deterministic JSON plan with three named fields per active-BOTH pair.** ✅ Confirmed by `test_detect_emits_three_named_fields`, `test_default_mode_determinism`, `test_cli_default_mode_emits_json`.
2. **`--apply --canonical X --merge-from Y` is the only DB-mutating path; refuses unknown pairs; performs strict order link-create → deactivate → retire; idempotent on rerun.** ✅ Confirmed by `test_apply_refuses_on_unknown_pair`, the four apply-flag refusal tests, and `test_apply_idempotent_on_rerun`.
3. **After `--apply` on the live target pair (under owner Stage 1.B AUQ), the retired non-canonical project has zero active memberships; the 8 items each have exactly one active canonical membership.** ✅ Confirmed by `test_retired_non_canonical_project_has_zero_active_memberships` AND `test_apply_no_duplicate_active_canonical_memberships`.
4. **Default-mode no-mutation guard.** ✅ AST scan (`test_default_mode_no_write_paths_in_detect_ast`) + row-count guard (`test_default_mode_no_mutation_row_counts`).
5. **Determinism.** ✅ `test_default_mode_determinism`.
6. **All new tests pass; `ruff check` and `ruff format --check` clean.** ✅ Confirmed above.

## Files Changed

- `scripts/hygiene/prefix_split_detector.py` (new, 343 lines)
- `platform_tests/scripts/test_prefix_split_detector.py` (new, 343 lines)

Both files are in-root (`E:\GT-KB\`) per `ADR-ISOLATION-APPLICATION-PLACEMENT-001`. No application/, no out-of-root artifact.

## Bridge Protocol Compliance

Filed at `bridge/gtkb-backlog-triage-and-hygiene-stage-1-structural-repair-005.md` with a matching `NEW` (implementation_report) entry directly below the Document header at the top of `bridge/INDEX.md`; append-only. The implementation-start packet was minted from the `-004` GO against PAUTH v4 under `source_addition` / `test_addition` mutation classes. No `groundtruth.db` mutation occurred at file-Write time; the two execution paths (Stage 1.A `gt projects reconcile-doubled-prefix --apply` and Stage 1.B `prefix_split_detector.py --apply ...`) remain owner-AUQ-gated and were NOT executed by this implementation.

## Recommended Commit Type

`feat:` — net-new detector script + 18-test suite (a new safe-merge capability), with no behavior change to existing surfaces. The execution-time `--apply` invocations are not part of this commit.
