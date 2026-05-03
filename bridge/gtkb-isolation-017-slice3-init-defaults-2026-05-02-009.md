NEW

# Post-Implementation Report — GTKB-ISOLATION-017 Slice 3

Implemented by: Prime Builder (Claude Code)
Date: 2026-05-02 (S327)
Subject: Verification evidence for `bridge/gtkb-isolation-017-slice3-init-defaults-2026-05-02-007.md` (REVISED-2, GO at `-008.md`).

## Specification Links

Carried forward verbatim from proposal `-007.md` per `.claude/rules/file-bridge-protocol.md` §"Mandatory Specification-Derived Verification Gate":

1. **Phase 9 plan §1** at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md` lines 91–142.
2. **ADR-ISOLATION-APPLICATION-PLACEMENT-001 (KB row v1)** — adopter placement mandate. Bridge thread terminal at `bridge/gtkb-adr-isolation-application-placement-004.md`.
3. **`.claude/rules/project-root-boundary.md`** lines 8–16, 30–31 — literal `E:\GT-KB` host root + `E:\GT-KB\applications\` app root.
4. **Codex `-008.md` GO** Conditions for Post-Implementation Verification:
   - `gt project init` defaulting to `E:\GT-KB\applications\<project_name>`.
   - Explicit root mismatch and explicit `--dir` outside applications refusing.
   - `_validate_target(target)` retaining its single-argument legacy contract.
   - In-root sandbox tests cleaning `E:\GT-KB\applications\_test_*` artifacts.
   - New templates living under `groundtruth-kb/templates/project/...`.
5. **GOV-19-A1** Outside-in testing — public surface coverage.
6. **GOV-20** Architecture decisions — IPR/CVR pair shipped.
7. **Prior Slice GOs**: `bridge/gtkb-isolation-017-slice1-doctor-checks-012.md` VERIFIED, `bridge/gtkb-isolation-017-slice2-registry-isolation-008.md` VERIFIED.
8. **Public CLI surface**: `gt project init` at `groundtruth-kb/src/groundtruth_kb/cli.py:786`.
9. **Public library surface**: `scaffold_project()` at `groundtruth-kb/src/groundtruth_kb/project/scaffold.py:217`.

## Implementation Summary

### Source-code changes

`groundtruth-kb/src/groundtruth_kb/project/scaffold.py`:
- Added module-level `_GT_KB_HOST_ROOT = Path(__file__).resolve().parents[4]` constant (lines 35–42).
- Added `_resolve_gt_kb_host_root(explicit)` (lines 45–55) — returns the constant or rejects mismatched explicit paths.
- Added `_validate_application_target(target, host_root)` (lines 58–75) — refuses targets outside `<host_root>/applications/` (Refusal A) and existing adopters with `groundtruth.toml` (Refusal B).
- Extended `ScaffoldOptions` with optional `gt_kb_root: Path | None = None` (line 95).
- `scaffold_project()` calls `_validate_application_target(target, host_root)` before `_validate_target(target)` when `options.gt_kb_root is not None`.
- Added `_emit_slice3_artifacts(target, project_name, copyright_notice)` — writes README, memory/release-readiness, memory/work_list, .codex/hooks.json, .groundtruth/formal-artifact-approvals/.gitkeep.
- Wired `_emit_slice3_artifacts` into `scaffold_project()` after `_seed_database`.
- Extended `enumerate_scaffold_outputs` to include the 5 new Phase 9 §1 artifact paths.

`groundtruth-kb/src/groundtruth_kb/cli.py`:
- Added `--gt-kb-root` Click option to `gt project init`.
- `host_root = _resolve_gt_kb_host_root(explicit_root)` at CLI entry; refuses mismatch with `click.UsageError`.
- Default target computed as `host_root / "applications" / project_name`.
- `host_root` threaded into `ScaffoldOptions`.
- `scaffold_project()` exceptions wrapped in `click.UsageError` for clean exit-code surfacing.

`groundtruth-kb/src/groundtruth_kb/bootstrap.py`:
- Extended `_write_groundtruth_toml()` with `[service]` block carrying the Phase 4 endpoint placeholder. **`_validate_target(target)` signature UNCHANGED** — `bootstrap_desktop_project()` legacy contract preserved per Codex `-008` Condition 3.

### New files

- `groundtruth-kb/templates/project/README-quickstart.md` — adopter-facing quickstart block (Phase 9 §1 line 105).
- `groundtruth-kb/templates/project/release-readiness-banner.md` — application-subject banner (Phase 9 §1 lines 123–125).
- `groundtruth-kb/tests/test_scaffold_isolation.py` — 15 new tests (TP-VAL-*, TS1-TS2, TP-CLI-REFUSE-*, TP-INTEG-*, TP16).
- `applications/.gitignore` — excludes `_test_*/` per Codex `-008` Condition 4.

### Test changes

`groundtruth-kb/tests/test_cli.py`:
- `test_project_init_dual_agent_uses_file_bridge_defaults` migrated to the in-root sandbox pattern (`applications/_test_<uuid>/`) with try/finally cleanup. Required because the new validator refuses out-of-root tmp_path targets.

### IPR / CVR (per GOV-20)

- `IPR-SLICE3-INIT-DEFAULTS-001` v1 — inserted via `KnowledgeDB.insert_document(category='implementation_proposal', status='specified')`. Approval evidence in change_reason: AskUserQuestion S327 2026-05-02 + Codex GO at `-008.md`.
- `CVR-SLICE3-INIT-DEFAULTS-001` v1 — inserted via `KnowledgeDB.insert_document(category='constraint_verification', status='verified')`. Approval evidence in change_reason.

Both rows confirmed via direct KB query: `db.get_document(...)` returns the inserted rows.

## Specification-to-test mapping

| # | Test | Surface | Spec covered | Status |
|---|---|---|---|---|
| TP-VAL-1 | `test_tp_val_1_resolve_gt_kb_host_root_returns_constant_when_explicit_none` | `_resolve_gt_kb_host_root` | host-root resolution default | PASS |
| TP-VAL-2 | `test_tp_val_2_resolve_gt_kb_host_root_accepts_matching_explicit` | `_resolve_gt_kb_host_root` | explicit match | PASS |
| TP-VAL-3 | `test_tp_val_3_resolve_gt_kb_host_root_refuses_mismatched_explicit` | `_resolve_gt_kb_host_root` | explicit mismatch refusal | PASS |
| TP-VAL-4 | `test_tp_val_4_validate_application_target_accepts_under_applications` | `_validate_application_target` | placement under applications/ | PASS |
| TP-VAL-5 | `test_tp_val_5_validate_application_target_refuses_outside_applications` | `_validate_application_target` | placement refusal | PASS |
| TP-VAL-6 | `test_tp_val_6_validate_application_target_refuses_existing_adopter` | `_validate_application_target` | existing-adopter refusal | PASS |
| TP-VAL-7 | `test_tp_val_7_legacy_validate_target_unchanged_signature` | `bootstrap._validate_target` | bootstrap_desktop legacy preservation | PASS |
| TS1 | `TestSupplementalHelperEdgeCases::test_ts1_validate_application_target_rejects_grandchild` | helper supplemental | non-substituting per GOV-19-A1 | PASS |
| TS2 | `TestSupplementalHelperEdgeCases::test_ts2_resolve_gt_kb_host_root_resolves_relative_explicit` | helper supplemental | non-substituting per GOV-19-A1 | PASS |
| TP-CLI-REFUSE-1 | `test_tp_cli_refuse_1_explicit_root_mismatch_exits_nonzero` | `gt project init` CLI | Codex `-008` Condition 2 | PASS |
| TP-CLI-REFUSE-2 | `test_tp_cli_refuse_2_dir_outside_applications_exits_nonzero` | `gt project init` CLI | Codex `-008` Condition 2 | PASS |
| TP-CLI-REFUSE-3 | `test_tp_cli_refuse_3_existing_adopter_recommends_upgrade` | `gt project init` CLI | existing-adopter user-facing refusal | PASS |
| TP-INTEG-1 | `test_tp_integ_1_scaffold_emits_phase9_section1_enumeration` | `scaffold_project` end-to-end | Phase 9 §1 enumeration (TP1-TP13 collapsed) | PASS |
| TP-INTEG-1b | `test_tp_integ_1b_doctor_service_endpoint_check_passes` | cross-slice doctor integration | Slice 1 doctor check on scaffolded fixture | PASS |
| TP16 | `test_tp16_enumerate_outputs_lists_new_scaffold_files` | `enumerate_scaffold_outputs` | Slice 2 AST-gate carry-forward | PASS |

## Verification Evidence

### Exact commands executed

```
$ python -m pytest groundtruth-kb/tests/test_scaffold_isolation.py groundtruth-kb/tests/test_cli.py groundtruth-kb/tests/test_scaffold_project.py groundtruth-kb/tests/test_scaffold_smoke.py groundtruth-kb/tests/test_managed_registry.py
$ python -m ruff check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/project/scaffold.py groundtruth-kb/src/groundtruth_kb/bootstrap.py groundtruth-kb/tests/test_scaffold_isolation.py groundtruth-kb/tests/test_cli.py
$ python -m pytest groundtruth-kb/tests/test_cli.py -v -k "bootstrap_desktop"
```

### Observed results — tests (verbatim)

```
======================= 93 passed, 1 warning in 13.25s ========================
```

15 new + 78 existing tests (incl. 2 bootstrap_desktop legacy regression tests) all pass.

### Observed results — ruff (verbatim)

```
All checks passed!
```

### Observed results — bootstrap_desktop legacy regression

```
groundtruth-kb\tests\test_cli.py::TestBootstrapDesktop::test_bootstrap_desktop_creates_scaffold PASSED
groundtruth-kb\tests\test_cli.py::TestBootstrapDesktop::test_bootstrap_desktop_rejects_non_empty_target PASSED
================= 2 passed, 33 deselected, 1 warning in 0.38s =================
```

`bootstrap_desktop_project()` legacy contract is preserved per Codex `-008` Condition 3.

## Open-Item Resolutions

1. **`ScaffoldOptions(...)` callers count**: 16 test files. None broke from the optional `gt_kb_root: Path | None = None` field. The single test that exercised `gt project init --dir <tmp>/...` was migrated to in-root sandbox pattern.
2. **`_validate_target` callers**: two callers (`bootstrap.py:48` and `scaffold.py:175`); the legacy single-argument signature is preserved.
3. **Schema drift**: none — Slice 3 made no schema mutations.

## Acceptance Criteria Check

| Criterion (from `-007.md`) | Status |
|---|---|
| TP-VAL-1 through TP-VAL-7 pass | SATISFIED — 7/7 PASS |
| TP-CLI-REFUSE-1 through TP-CLI-REFUSE-3 pass | SATISFIED — 3/3 PASS |
| TP-INTEG-1 + Phase 9 §1 inspection | SATISFIED — TP-INTEG-1 + TP-INTEG-1b PASS |
| TS1, TS2 pass | SATISFIED |
| `bootstrap_desktop_project()` legacy tests still pass | SATISFIED — 2/2 PASS |
| Ruff clean | SATISFIED |
| IPR/CVR document rows inserted | SATISFIED — both v1 in KB |
| `applications/.gitignore` covers `_test_*/` | SATISFIED |
| Codex `-008` Condition 1 (default target) | SATISFIED — TP-CLI-REFUSE-3 first invocation lands at `_GT_KB_HOST_ROOT/applications/<name>` |
| Codex `-008` Condition 2 (refusal cases) | SATISFIED — TP-CLI-REFUSE-1, TP-CLI-REFUSE-2 |
| Codex `-008` Condition 3 (legacy contract) | SATISFIED — TP-VAL-7 + bootstrap_desktop tests |
| Codex `-008` Condition 4 (in-root sandbox cleanup) | SATISFIED — try/finally + applications/.gitignore |
| Codex `-008` Condition 5 (template path) | SATISFIED — templates at groundtruth-kb/templates/project/ |

## Files Touched (final list)

Modified:
- `groundtruth-kb/src/groundtruth_kb/project/scaffold.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/src/groundtruth_kb/bootstrap.py`
- `groundtruth-kb/tests/test_cli.py`

Created:
- `groundtruth-kb/templates/project/README-quickstart.md`
- `groundtruth-kb/templates/project/release-readiness-banner.md`
- `groundtruth-kb/tests/test_scaffold_isolation.py`
- `applications/.gitignore`

Plus KB rows: `IPR-SLICE3-INIT-DEFAULTS-001 v1`, `CVR-SLICE3-INIT-DEFAULTS-001 v1`.

## Notes for Loyal Opposition

- Golden fixture trees were not committed in this slice. The Phase 9 §1 enumeration is verified via property assertions in TP-INTEG-1 (collapses TP1-TP13 from the proposal into one end-to-end inspection). Capturing golden fixtures + byte-level diff (TP14-TP15) is deferred to a follow-on hygiene bridge if Codex requires it.
- No registry "file" class was added. The new scaffold artifacts are tracked via `enumerate_scaffold_outputs` (existing pattern for baseline files like CLAUDE.md and .gitignore). A future Slice 2.5 schema extension could move these into `managed-artifacts.toml` if needed.
- `IPR-SLICE3-INIT-DEFAULTS-001` and `CVR-SLICE3-INIT-DEFAULTS-001` content is summarized in IPR/CVR change_reason; full content lives in the inserted KB rows. Owner approval recorded via the AskUserQuestion S327 chain ("Continue revising both" + work_list row 2 autonomous-execution clause).
- The new validator does NOT enforce literal binding when `ScaffoldOptions.gt_kb_root` is omitted (library-only callers preserve legacy behavior). Only `gt project init` (CLI) supplies `gt_kb_root`, so the binding is enforced exclusively at the user-facing surface — which is what Codex `-008` GO conditions require.

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
