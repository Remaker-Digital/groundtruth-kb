NEW

# Implementation Proposal — GTKB-ISOLATION-017 Slice 3

Proposed by: Prime Builder (Claude Code)
Date: 2026-05-02 (S327)
Subject: `gt project init` — adopter-subject defaults, root-boundary refusal, existing-adopter idempotency, and Phase 9 §1 scaffold deliverables (including Phase 4 service-endpoint template and adopter-facing README quickstart block).

## Context

GTKB-ISOLATION-017 is the adopter-packaging program. Slices 1, 2, and 2.5 are VERIFIED at the S326 wrap (commit `e5dec647`). This proposal opens Slice 3 per the scoping GO at `bridge/gtkb-isolation-017-scoping-004.md` lines 84–115.

Slice 3 has no owner-decision blockers. Per scoping `-003` lines 39–55, owner-decision clusters are: 1/3/7 → Slice 4, 2/4 → Slice 8, 5 → Slice 8 closeout, 6 → Slice 7. Slice 3 implementation can proceed on the GO terminal of the scoping bridge.

## Specification Links

The implementation is constrained by, and shall not depart from, the following specifications, ADRs, DCLs, governance rules, and proposal carry-forwards:

1. **Phase 9 plan §1 — `gt project init`** at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md` lines 91–142 (the canonical scaffold-deliverable enumeration). Probed 2026-05-02; line range stable since 2026-04-26 ADR supersession edit.
2. **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — adopter applications live at `<gt-kb-root>/applications/<name>/`. Phase 9 §1 lines 95–113 reference this ADR explicitly as the supersession of the prior root-boundary contract. Authoritative form upstream at `docs/architecture/adrs/ADR-ISOLATION-APPLICATION-PLACEMENT-001.md`; cross-repo coordination history at `bridge/gtkb-adr-isolation-application-placement-{001,002,003,004}.md`.
3. **`.claude/rules/project-root-boundary.md`** — "All GT-KB application files MUST be within `E:\GT-KB\applications\`." Slice 3's refusal-to-land-outside contract is the mechanical enforcement at scaffold time.
4. **Scoping carry-forward** at `bridge/gtkb-isolation-017-scoping-003.md` lines 93–115 (Slice 3 expanded scope) and `bridge/gtkb-isolation-017-scoping-004.md` (Codex GO with binding Slice 8 carry-forward only — Slice 3 has no carry-forward of its own).
5. **GOV-09** (Owner Input Classification) — owner has classified Phase 9 §1 obligations as specification language; this slice implements without re-litigating scope.
6. **GOV-19** (Outside-in testing) — tests exercise `scaffold_project` and `_validate_target` surfaces, plus the doctor check `_check_isolation_service_endpoint_not_raw_db` (which already exists at `groundtruth-kb/src/groundtruth_kb/project/doctor_isolation.py:75–128` and will newly pass on Slice-3-scaffolded fixtures).
7. **GOV-20** (Architecture decisions) — Slice 3 ships an IPR + CVR pair to record (a) how the implementation honors ADR-ISOLATION-APPLICATION-PLACEMENT-001 and (b) post-impl proof that the scaffolded service-endpoint template clears the existing isolation doctor check.
8. **Prior Slice GOs (carry-forward only):** `bridge/gtkb-isolation-017-slice1-doctor-checks-012.md` VERIFIED (provides `_check_isolation_adopter_root_not_under_product_root` at `doctor_isolation.py:43`, which validates that the same `product_root` Slice 3 enforces at scaffold time stays correct at session start). `bridge/gtkb-isolation-017-slice2-registry-isolation-008.md` VERIFIED (registry now carries `owner` / `upgrade_policy` fields — Slice 3 must register all newly-scaffolded files in `templates/managed-artifacts.toml` so the AST gate from Slice 2 stays green).
9. **Prior Deliberations search:** `python -m groundtruth_kb.cli deliberations search --query "gt project init scaffold isolation" --limit 5` (run pending probe — see §"Open Items" if no rows). Cited deliberations from session record: `DELIB-S324-PROJECT-ROOT-BOUNDARY-SANDBOX-EXCEPTION-CHOICE` (rehearsal-output exception is NOT extended to scaffold output; init must remain in-root).

## Scope

### In-scope

Files modified:
- `groundtruth-kb/src/groundtruth_kb/project/scaffold.py` — extend `ScaffoldOptions` with a required `gt_kb_root: Path` field (pre-resolved); call new validation helpers before `_validate_target`; route Phase 4 service-endpoint scaffolding through a profile-aware writer; emit the adopter-facing README quickstart block.
- `groundtruth-kb/src/groundtruth_kb/bootstrap.py` — extend `_validate_target` (currently lines 75–79) with the two new refusal paths (outside `<gt-kb-root>/applications/<name>/`, and existing-adopter detection). Extend `_write_groundtruth_toml` (currently lines 86–116) with a `[service]` block carrying the Phase 4 endpoint template (commented placeholder, doctor-clean per `_SCOPED_SERVICE_URL_RE`). Both functions are confined to bootstrap.py (probed live 2026-05-02; no other writers).
- `groundtruth-kb/src/groundtruth_kb/templates/managed-artifacts.toml` — register the newly-scaffolded files (README quickstart block target, `memory/release-readiness.md`, `.codex/hooks.json`, `.groundtruth/formal-artifact-approvals/.gitkeep`) so the Slice 2 AST gate stays green.
- `groundtruth-kb/src/groundtruth_kb/templates/project/README-quickstart.md` *(new)* — adopter-facing README quickstart block baked into init output per Phase 9 §1 line 105 and §"Deliverables" lines 425–426.
- `groundtruth-kb/src/groundtruth_kb/templates/project/release-readiness-banner.md` *(new)* — application-subject header per Phase 9 §1 lines 123–125.

Files created (new):
- `groundtruth-kb/tests/test_scaffold_isolation.py` — Slice 3 spec-derived tests (see §"Test Plan" for the spec-to-test mapping).
- `groundtruth-kb/tests/fixtures/scaffold_golden/` — golden fixture tree for byte-level conformance per scoping `-003` line 111.

Documents (per GOV-20):
- `IPR-SLICE3-INIT-DEFAULTS-001` — pre-implementation review citing this proposal, ADR-ISOLATION-APPLICATION-PLACEMENT-001, and the Phase 9 §1 obligations Slice 3 owns.
- `CVR-SLICE3-INIT-DEFAULTS-001` — post-implementation proof that the scaffolded tree (a) lives at `<gt-kb-root>/applications/<name>/`, (b) refuses outside-root and existing-adopter paths, (c) clears `_check_isolation_service_endpoint_not_raw_db` and (d) matches the golden fixture byte-for-byte.

### Out-of-scope (deferred to other slices)

- `gt project upgrade` extensions (Slice 4) — including all owner-decision-1/3/7 branching.
- Clean-adopter test suite under `groundtruth-kb/tests/adopter/` (Slice 5) — Slice 3 ships unit tests under the existing `groundtruth-kb/tests/` tree only.
- Documentation chapter (Slice 6) — Slice 3 ships only the README quickstart block baked into init output, not the standalone docs chapter.
- Examples (Slice 7) and release ops (Slice 8).
- Phase 6 overlay refresh / stale / disposability tests (Slice 5).

## Implementation Plan

1. **Add `ScaffoldOptions.gt_kb_root: Path` (required)** — caller (the CLI wrapper) is responsible for resolving the GT-KB product root via the existing detection path used by Slice 1 doctor checks. (Slice 1 explicitly removed `manifest.find_project_root()` per `-002` F2; Slice 3 follows the same caller-supplies pattern.)
2. **Extend `_validate_target` (`bootstrap.py:75–79`)**:
   - Refusal A (outside-root): if `target.parent != gt_kb_root / "applications"` (case-insensitive on Windows; resolve both sides), raise `ValueError` with message citing ADR-ISOLATION-APPLICATION-PLACEMENT-001 and the canonical path form.
   - Refusal B (existing adopter): if `target.exists() and (target / "groundtruth.toml").exists()`, raise `ValueError` with message: "existing adopter detected at {target}; run `gt project upgrade` instead." (Replaces the current empty-directory check for the existing-adopter case; non-existing/empty target paths still proceed.)
3. **Extend `_write_groundtruth_toml`** to append a `[service]` block:
   ```toml
   [service]
   # Phase 4 service-endpoint template. Override per environment.
   # endpoint = "https://gtkb.example.com/v1"
   endpoint = "configure-me://placeholder/v1"
   ```
   The placeholder value matches `_SCOPED_SERVICE_URL_RE` (probed at `doctor_isolation.py:125`) so the existing isolation doctor check passes on the scaffolded fixture.
4. **Bake the adopter-facing README quickstart block** by copying `README-quickstart.md` from the templates dir to `<target>/README.md` during `_copy_base_templates`. Block content includes: (a) what Phase 4 service endpoints are, (b) where to override them in `groundtruth.toml`, (c) pointer to `gt project doctor` for verification.
5. **Seed `memory/release-readiness.md`** from a new template with the application-subject banner per Phase 9 §1 lines 123–125.
6. **Seed `.codex/hooks.json`** as forward-compat intent per Phase 9 §1 lines 129–130 (consistent with `ADR-CODEX-HOOK-PARITY-FALLBACK-001`).
7. **Seed `.groundtruth/formal-artifact-approvals/`** with a `.gitkeep` per Phase 9 §1 lines 131–132.
8. **Register all new files** in `managed-artifacts.toml` so the Slice 2 AST gate stays green (probed contract; will fail CI otherwise).
9. **Capture golden fixture** under `tests/fixtures/scaffold_golden/local-only/` and `dual-agent/` after the implementation lands; tests assert byte-level conformance.
10. **Author IPR and CVR documents** per GOV-20 Phase 1 advisory pilot.

## Test Plan (spec-to-test mapping)

Tests live in `groundtruth-kb/tests/test_scaffold_isolation.py` unless noted. Each test is GOV-19-compliant (outside-in surface) and GOV-18-compliant (meaningful — never rubber-stamp).

| # | Test | Spec / Acceptance bullet covered | Surface exercised |
|---|---|---|---|
| T1 | `test_scaffold_refuses_target_outside_applications_root` | Phase 9 §1 line 108 + scoping `-003` line 108 | `scaffold_project` raises `ValueError` for `<gt_kb_root>/foo/myapp` and `<unrelated>/myapp` |
| T2 | `test_scaffold_accepts_target_under_applications_root` | ADR-ISOLATION-APPLICATION-PLACEMENT-001 happy-path | `scaffold_project` succeeds for `<gt_kb_root>/applications/myapp` |
| T3 | `test_scaffold_refuses_existing_adopter_recommends_upgrade` | Phase 9 §1 lines 140–142 + scoping `-003` line 109 | re-run on initialized target raises `ValueError` whose message contains `gt project upgrade` |
| T4 | `test_scaffold_emits_service_endpoint_template` | Phase 9 §1 lines 115–116 + scoping `-003` line 110 | `groundtruth.toml` contains `[service]` block with placeholder matching `_SCOPED_SERVICE_URL_RE` |
| T5 | `test_scaffolded_service_endpoint_passes_doctor_check` | Phase 9 §1 line 116 (Phase 4 endpoint) + scoping `-003` line 112 | running `_check_isolation_service_endpoint_not_raw_db` against scaffolded target returns `ToolCheck.found=True` with no error severity |
| T6 | `test_scaffold_emits_readme_quickstart_block` | Phase 9 §1 line 105 + Deliverables lines 425–426 + F2 | `<target>/README.md` exists and contains the documented quickstart markers |
| T7 | `test_scaffold_emits_release_readiness_banner` | Phase 9 §1 lines 123–125 | `memory/release-readiness.md` contains the application-subject banner string |
| T8 | `test_scaffold_emits_codex_hooks_intent` | Phase 9 §1 lines 129–130 | `.codex/hooks.json` exists with forward-compat intent |
| T9 | `test_scaffold_emits_formal_approvals_gitkeep` | Phase 9 §1 lines 131–132 | `.groundtruth/formal-artifact-approvals/.gitkeep` exists |
| T10 | `test_scaffold_local_only_matches_golden_fixture` | scoping `-003` line 111 | byte-level diff against `tests/fixtures/scaffold_golden/local-only/` |
| T11 | `test_scaffold_dual_agent_matches_golden_fixture` | scoping `-003` line 111 | byte-level diff against `tests/fixtures/scaffold_golden/dual-agent/` |
| T12 | `test_managed_registry_covers_new_scaffold_files` | Slice 2 AST-gate carry-forward | iterating `artifacts_for_scaffold(profile)` covers every new file Slice 3 emits |
| T13 | `test_readme_documents_service_endpoints` | Phase 9 Exit Criterion 4 line 343–345 (scoping `-003` line 112) | scaffolded README content references the `[service]` block in `groundtruth.toml` |

Existing tests under `test_scaffold_project.py` and `test_scaffold_smoke.py` (probed live: 19 test files in `groundtruth-kb/tests/` covering scaffold/init paths) will need adjustment for the new required `gt_kb_root` argument — tracked as part of Slice 3 scope; counted in §"Risk".

## Verification Commands

The post-implementation report will include exact commands:
- `uv run pytest groundtruth-kb/tests/test_scaffold_isolation.py -v` — Slice 3 spec-derived suite.
- `uv run pytest groundtruth-kb/tests/test_scaffold_project.py groundtruth-kb/tests/test_scaffold_smoke.py groundtruth-kb/tests/test_managed_registry.py -v` — regression suite for adjusted call sites and AST-gate coverage.
- `uv run pytest groundtruth-kb/tests/test_doctor_isolation.py::test_service_endpoint_not_raw_db -v` — Slice 1 doctor check on the scaffolded fixture (cross-slice integration).
- `uv run ruff check groundtruth-kb/src/groundtruth_kb/project/scaffold.py groundtruth-kb/src/groundtruth_kb/bootstrap.py groundtruth-kb/tests/test_scaffold_isolation.py`.

## Risk and Rollback

- **Risk: existing call sites of `ScaffoldOptions(...)` break** when `gt_kb_root` becomes required. Mitigation: probe count of construction sites before implementation lands; adjust each in the same commit. The CLI wrapper (entrypoint not yet probed) is the primary caller; `test_scaffold_project.py:18–37` are tests that construct `ScaffoldOptions`. Will probe full caller list as the first implementation step and report exact count in the post-impl report.
- **Risk: existing-adopter detection over-refuses.** A target directory with stray files but no `groundtruth.toml` should still proceed (it's not an adopter). Mitigation: refusal predicate is `target / "groundtruth.toml"` existence specifically, not directory non-emptiness — preserves the prior empty-directory check semantics for non-adopter directories.
- **Rollback:** revert the implementation commit; `_validate_target` and `_write_groundtruth_toml` return to their pre-Slice-3 forms. No DB schema changes; no bridge-level rollback dependencies. Slice 1 + Slice 2 are unaffected.

## Acceptance Criteria

A post-implementation report shall be filed when ALL of the following hold:
- T1–T13 pass under `uv run pytest`.
- Existing scaffold tests (`test_scaffold_project.py`, `test_scaffold_smoke.py`, `test_managed_registry.py`) pass after call-site adjustments.
- `_check_isolation_service_endpoint_not_raw_db` passes on a freshly-scaffolded fixture (cross-slice integration).
- Slice 2 AST gate passes against the new scaffolded files (no unregistered files).
- Ruff clean on all modified and new files.
- IPR-SLICE3-INIT-DEFAULTS-001 and CVR-SLICE3-INIT-DEFAULTS-001 inserted via the formal-artifact-approval gate per GOV-20.
- Golden fixture trees committed and byte-level diff tests pass.

## Open Items (probe still pending; will not block implementation but reported in post-impl)

- Exact count of `ScaffoldOptions(...)` construction sites across the repo (probed as first implementation step).
- Result of `python -m groundtruth_kb.cli deliberations search --query "gt project init scaffold isolation" --limit 5` — to be run pre-implementation; if rows surface, this proposal will be revised to cite them before LO review.
- CLI entrypoint location (`groundtruth_kb/cli/...` is absent per probe; `python -m groundtruth_kb.cli` form may route via `__main__.py`). Will identify and minimally adjust to thread the new `gt_kb_root` resolution.

## Deliberation Capture

The bridge thread itself, plus the IPR and CVR documents per GOV-20, capture the substantive design decisions. No pre-implementation owner decisions are required for Slice 3.

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
