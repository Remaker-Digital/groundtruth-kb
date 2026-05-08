REVISED

# Implementation Proposal — GTKB-ISOLATION-018 Sub-sub-slice 18.E.3: Platform-Test Disposition Decision (REVISED-1)

**Author:** Prime Builder (Claude Code)
**Drafted:** 2026-05-07 (S334)
**Type:** Revision addressing Codex NO-GO at `bridge/gtkb-isolation-018-slice-e3-platform-test-disposition-002.md` (F1 platform-test inventory undercount; F2 coverage-test scope; F3 Option A/B count recalculation).
**Predecessors:** `-001` (initial proposal), `-002` (Codex NO-GO).
**Owner-decision status:** Option A is durably recorded as `DELIB-S334-OQ-E3-OPTION-A` in MemBase (per parallel-agent capture of the S334 owner prose answer). This revision incorporates the corrected inventory; the operative AUQ resolution is preserved.

---

## Codex Findings Addressed (from -002)

| Finding | Disposition |
|---|---|
| **F1** — `tests/scripts/` platform-test inventory undercounted (-001 claimed 19 of 69; live review shows essentially all 69 are platform tests) | **Fixed.** This `-003` includes a complete file-by-file disposition table for ALL 69 `tests/scripts/*.py` files plus `tests/scripts/__init__.py` and `tests/scripts/conftest.py`. Result: **all 69 are PLATFORM**; tests/scripts/ stays at root in its entirety under Option A. |
| **F2** — T-list-coverage-1 only detected `.claude/`-referencing tests; missed root `scripts/`, `.github/workflows/`, `harness-state/`, `bridge/`, `groundtruth_kb` references | **Fixed.** Replaced T-list-coverage-1 with broader detection covering: `parents[N] / "scripts"`, `from scripts.* import`, `.github/workflows/`, `harness-state/`, `bridge/`, `groundtruth_kb` modules, dashboard artifacts (`gtkb-dashboard`, `gtkb_dashboard`, `gtkb_overlay`), wrap-scan tooling, and platform governance scripts (`adr_dcl_clause`, `bridge_applicability`, `harness_identity`, `release_candidate`, etc.). |
| **F3** — Option A/B count estimates unreliable | **Fixed.** Recalculated counts: Option A = **83 files stay at root** (13 tests/hooks + 69 tests/scripts + 1 tests/__init__.py). Option B = **0 files stay; ~83 platform-test files require `parents[N]` rewrites**. |

---

## Specification Links

Carried forward from `-001`. Re-cited here for preflight matching:

Cross-cutting required:
- `GOV-FILE-BRIDGE-AUTHORITY-001` (verified)
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (specified)
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (specified)

Cross-cutting advisory:
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (verified)
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (verified)
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (verified)

Topic-specific:
- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` (S330 owner_decision)
- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` v1
- `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001` v1
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` v1 (ACTIVE)
- **`DELIB-S334-OQ-E3-OPTION-A`** (S334 owner_decision; Option A as the OQ-E3 resolution)
- `bridge/gtkb-isolation-018-slice-e-code-cluster-004.md` (18.E scoping GO)
- `bridge/gtkb-isolation-018-slice-e-code-cluster-003.md` (18.E scoping REVISED-1 with F4 testpaths consequence)
- `bridge/gtkb-isolation-018-slice-e3-platform-test-disposition-002.md` (Codex NO-GO triggering this revision)
- `bridge/gtkb-isolation-018-slice-c-docs-cluster-011.md` (18.C VERIFIED; pattern precedent)
- `bridge/gtkb-isolation-018-slice-d-non-functional-content-006.md` (18.D VERIFIED; pattern precedent)
- `applications/Agent_Red/.gtkb-app-isolation.json`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (verified)
- `DCL-APP-ROOT-MINIMIZATION-001`
- `.claude/rules/project-root-boundary.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/deliberation-protocol.md`

## Owner Decisions / Input

| AUQ Question / Decision | Header / Source | Answer | Disposition |
|---|---|---|---|
| **OQ-E3** Platform-test disposition (S334, 2026-05-07) | (S334 prose answer to recommended default) | "**Option A**" | **Recorded in MemBase as `DELIB-S334-OQ-E3-OPTION-A`** (parallel-agent capture). This revision uses Option A as the operative resolution; corrected inventory below confirms Option A is the right choice (83 files stay at root vs ~83 source-edits under Option B). |
| "18.E structure — sub-split or atomic?" (S334) | "18.E scope" | "Sub-split: 18.E.1 + 18.E.2 + 18.E.3" | Authorizes this E.3 sub-sub-slice. |
| "Agent Red isolation — what's the next move?" (S334) | "Isolation move" | Owner directive: complete isolation as release-gating. | Authorizes 18.E program. |
| `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` (S330) | (S330) | 5 binding rules. | Source authority. |
| `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` (S331) | (S331) | ACTIVE waiver. | Authorizes in-flight pre-migration state. |

## F1 Fix — Complete tests/scripts/ Disposition Table (All 69 Files)

Live probe (2026-05-07) using broader detection: `parents[N] / "scripts"` + `from scripts.*` + `.github/workflows/` + `harness-state/` + `bridge/` + `groundtruth_kb` + dashboard/wrap-scan/governance markers.

**All 69 `tests/scripts/*.py` files plus 2 supporting files = 69+2 = 71 platform files.**

| File | Disposition | Rationale |
|---|---|---|
| `tests/scripts/__init__.py` | STAYS_PLATFORM | Package marker for tests/scripts/ subdir |
| `tests/scripts/conftest.py` | STAYS_PLATFORM | pytest conftest shielding scripts/ tests from heavy root conftest |
| `tests/scripts/test_adr_dcl_clause_preflight.py` | STAYS_PLATFORM | Tests `scripts/adr_dcl_clause_preflight.py` (platform) |
| `tests/scripts/test_archive_claude_design_handoff.py` | STAYS_PLATFORM | Tests `.claude/` archive handoff |
| `tests/scripts/test_audit_adr_dcl_metadata.py` | STAYS_PLATFORM | Tests ADR/DCL metadata audit (platform governance) |
| `tests/scripts/test_audit_gtkb_triad_completeness.py` | STAYS_PLATFORM | Tests GT-KB triad audit |
| `tests/scripts/test_bridge_applicability_preflight.py` | STAYS_PLATFORM | Tests `scripts/bridge_applicability_preflight.py` |
| `tests/scripts/test_bridge_automation_role_authority.py` | STAYS_PLATFORM | Tests bridge-automation role authority |
| `tests/scripts/test_bridge_notify_reader.py` | STAYS_PLATFORM | Tests bridge notify reader |
| `tests/scripts/test_check_dev_environment_inventory_drift.py` | STAYS_PLATFORM | Tests `scripts/check_dev_environment_inventory_drift.py` |
| `tests/scripts/test_check_environment_isolation.py` | STAYS_PLATFORM | Tests environment isolation |
| `tests/scripts/test_check_harness_parity.py` | STAYS_PLATFORM | Tests harness parity check |
| `tests/scripts/test_claude_session_start_dispatcher.py` | STAYS_PLATFORM | Tests Claude session-start dispatcher |
| `tests/scripts/test_codex_backlog_cleanup_inventory.py` | STAYS_PLATFORM | Tests Codex backlog cleanup inventory |
| `tests/scripts/test_codex_hook_parity.py` | STAYS_PLATFORM | Tests Codex hook parity |
| `tests/scripts/test_collect_dev_environment_inventory.py` | STAYS_PLATFORM | Tests `scripts/collect_dev_environment_inventory.py` |
| `tests/scripts/test_command_registry_tracking.py` | STAYS_PLATFORM | Tests `.claude/commands/registry.json` |
| `tests/scripts/test_dashboard_subject_selector.py` | STAYS_PLATFORM | Tests dashboard subject selector |
| `tests/scripts/test_dora_001b_track1_writer.py` | STAYS_PLATFORM | Tests DORA-001b track 1 writer |
| `tests/scripts/test_dora_001b_track2_ingest.py` | STAYS_PLATFORM | Tests DORA-001b track 2 ingest |
| `tests/scripts/test_generate_bridge_swimlane.py` | STAYS_PLATFORM | Tests `scripts/generate_bridge_swimlane.py` |
| `tests/scripts/test_generate_codex_skill_adapters.py` | STAYS_PLATFORM | Tests `scripts/generate_codex_skill_adapters.py` |
| `tests/scripts/test_gitignore_session_snapshots.py` | STAYS_PLATFORM | Tests platform `.gitignore` session snapshots |
| `tests/scripts/test_governance_hygiene_bundle.py` | STAYS_PLATFORM | Tests governance hygiene bundle |
| `tests/scripts/test_groundtruth_governance_adoption.py` | STAYS_PLATFORM | Tests groundtruth governance adoption |
| `tests/scripts/test_groundtruth_kb_tests_workflow.py` | STAYS_PLATFORM | Tests `.github/workflows/groundtruth-kb-tests.yml` |
| `tests/scripts/test_gtkb_bridge_writer.py` | STAYS_PLATFORM | Tests `scripts/gtkb_bridge_writer.py` |
| `tests/scripts/test_gtkb_dashboard_alerting.py` | STAYS_PLATFORM | Tests GT-KB dashboard alerting |
| `tests/scripts/test_gtkb_dashboard_control_plane.py` | STAYS_PLATFORM | Tests GT-KB dashboard control plane |
| `tests/scripts/test_gtkb_dashboard_grafana.py` | STAYS_PLATFORM | Tests GT-KB Grafana dashboard |
| `tests/scripts/test_gtkb_overlay.py` | STAYS_PLATFORM | Tests `scripts/gtkb_overlay.py` |
| `tests/scripts/test_gtkb_scoped_client.py` | STAYS_PLATFORM | Tests GT-KB scoped client |
| `tests/scripts/test_harness_identity.py` | STAYS_PLATFORM | Tests `scripts/harness_identity.py` |
| `tests/scripts/test_harness_roles.py` | STAYS_PLATFORM | Tests harness role assignments + `harness-state/` |
| `tests/scripts/test_harvest_loud_wrap.py` | STAYS_PLATFORM | Tests harvest loud wrap (platform) |
| `tests/scripts/test_harvest_session_thread_level.py` | STAYS_PLATFORM | Tests session-thread harvest |
| `tests/scripts/test_isolation_017_citation_backfill_audit.py` | STAYS_PLATFORM | Tests ISOLATION-017 citation backfill audit |
| `tests/scripts/test_kb_attribution.py` | STAYS_PLATFORM | Tests KB attribution |
| `tests/scripts/test_memory_md_ceiling.py` | STAYS_PLATFORM | Tests MEMORY.md ceiling (platform governance) |
| `tests/scripts/test_project_resource_aliases.py` | STAYS_PLATFORM | Tests project resource aliases |
| `tests/scripts/test_rehearse_backlog_split.py` | STAYS_PLATFORM | Tests rehearse backlog split |
| `tests/scripts/test_rehearse_bridge_split.py` | STAYS_PLATFORM | Tests rehearse bridge split |
| `tests/scripts/test_rehearse_chromadb_regen.py` | STAYS_PLATFORM | Tests rehearse ChromaDB regen |
| `tests/scripts/test_rehearse_ci_inventory.py` | STAYS_PLATFORM | Tests rehearse CI inventory |
| `tests/scripts/test_rehearse_common_validation.py` | STAYS_PLATFORM | Tests rehearse common validation |
| `tests/scripts/test_rehearse_dashboard_regen.py` | STAYS_PLATFORM | Tests rehearse dashboard regen |
| `tests/scripts/test_rehearse_db_filter_dryrun.py` | STAYS_PLATFORM | Tests rehearse DB filter dry-run |
| `tests/scripts/test_rehearse_driver_wave_banner.py` | STAYS_PLATFORM | Tests rehearse driver wave banner |
| `tests/scripts/test_rehearse_inventory.py` | STAYS_PLATFORM | Tests rehearse inventory |
| `tests/scripts/test_rehearse_isolation.py` | STAYS_PLATFORM | Tests rehearse isolation |
| `tests/scripts/test_rehearse_lint_clean.py` | STAYS_PLATFORM | Tests rehearse lint clean |
| `tests/scripts/test_rehearse_membase_export.py` | STAYS_PLATFORM | Tests rehearse MemBase export |
| `tests/scripts/test_rehearse_path_rewrite.py` | STAYS_PLATFORM | Tests rehearse path rewrite |
| `tests/scripts/test_rehearse_production_effects.py` | STAYS_PLATFORM | Tests rehearse production effects |
| `tests/scripts/test_rehearse_release_readiness_split.py` | STAYS_PLATFORM | Tests rehearse release-readiness split |
| `tests/scripts/test_rehearse_split_helper.py` | STAYS_PLATFORM | Tests rehearse split helper |
| `tests/scripts/test_release_candidate_gate.py` | STAYS_PLATFORM | Tests release-candidate gate |
| `tests/scripts/test_retroactive_harvest_bridge_threads.py` | STAYS_PLATFORM | Tests retroactive bridge-thread harvest |
| `tests/scripts/test_run_spec_derived_tests.py` | STAYS_PLATFORM | Tests `scripts/run_spec_derived_tests.py` |
| `tests/scripts/test_session_self_initialization.py` | STAYS_PLATFORM | Tests session self-initialization |
| `tests/scripts/test_session_self_initialization_imports.py` | STAYS_PLATFORM | Tests session self-init imports |
| `tests/scripts/test_standing_backlog_harvest.py` | STAYS_PLATFORM | Tests standing-backlog harvest |
| `tests/scripts/test_system_interface_map.py` | STAYS_PLATFORM | Tests system interface map |
| `tests/scripts/test_verify_slice8_5_ci_green.py` | STAYS_PLATFORM | Tests slice 8.5 CI green |
| `tests/scripts/test_wrap_capture_transcript.py` | STAYS_PLATFORM | Tests wrap capture transcript |
| `tests/scripts/test_wrap_scan_consistency.py` | STAYS_PLATFORM | Tests wrap-scan consistency |
| `tests/scripts/test_wrap_scan_consistency_allowlist.py` | STAYS_PLATFORM | Tests wrap-scan consistency allowlist |
| `tests/scripts/test_wrap_scan_hygiene.py` | STAYS_PLATFORM | Tests wrap-scan hygiene |
| `tests/scripts/test_wrap_scan_hygiene_skip_dirs.py` | STAYS_PLATFORM | Tests wrap-scan hygiene skip-dirs |

**Result: ALL 69 `tests/scripts/*.py` files + `__init__.py` + `conftest.py` = 71 files STAY at root** under Option A. Zero migrate to applications/Agent_Red/tests/scripts/.

This is consistent with the operating-model: tests/scripts/ exists specifically to test platform tooling under `scripts/`, `.claude/`, `.github/workflows/`, `harness-state/`, `bridge/`, etc. All those targets are platform; therefore all tests of those targets are platform tests.

## F1 Fix — tests/hooks/ Disposition (Carried Forward, Confirmed Complete)

| File | Disposition | Rationale |
|---|---|---|
| `tests/hooks/__init__.py` | STAYS_PLATFORM | Package marker |
| `tests/hooks/fixtures/owner_decision_tracker/turn_*.jsonl` (7 files) | STAYS_PLATFORM | Fixtures for testing `.claude/hooks/owner-decision-tracker.py` |
| `tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py` | STAYS_PLATFORM | Tests `.claude/hooks/bridge-compliance-gate.py` |
| `tests/hooks/test_credential_scan.py` | STAYS_PLATFORM | Tests `.claude/hooks/credential-scan.py` |
| `tests/hooks/test_formal_artifact_approval_gate.py` | STAYS_PLATFORM | Tests `.claude/hooks/formal-artifact-approval-gate.py` |
| `tests/hooks/test_owner_decision_tracker.py` | STAYS_PLATFORM | Tests `.claude/hooks/owner-decision-tracker.py` |
| `tests/hooks/test_workstream_focus.py` | STAYS_PLATFORM | Tests `.claude/hooks/workstream-focus.py` |

**Result: ALL 13 `tests/hooks/` files STAY at root.**

## F1 Fix — Other tests/ Subdirs Disposition

Probed for platform-test markers across all other `tests/*` subdirs. None reference platform code. All migrate with E.1 to `applications/Agent_Red/tests/`:

| Subdir | File count | Disposition |
|---|--:|---|
| `tests/multi_tenant/` | ~major bulk | MIGRATE (Agent Red multi-tenant tests) |
| `tests/integrations/` | (subset) | MIGRATE (Agent Red integration tests, including stripe_catalog test) |
| `tests/agents/` | (subset) | MIGRATE (Agent Red agent-pattern tests) |
| `tests/chat/` | (subset) | MIGRATE (Agent Red chat tests) |
| `tests/admin/`, `tests/widget/` | (subset) | MIGRATE (Agent Red frontend tests) |
| `tests/accessibility/`, `tests/e2e_mock/` | (subset) | MIGRATE (Agent Red product tests) |
| `tests/__init__.py` | 1 | STAYS_PLATFORM (shared at root level since some tests stay) |
| Other Agent Red subdirs | (remaining) | MIGRATE |

**Note:** `tests/__init__.py` is the only file in `tests/` itself (not a subdir). Under Option A, both `tests/__init__.py` (root) and `applications/Agent_Red/tests/__init__.py` (new) need to exist as package markers for pytest to discover tests in both locations.

## F2 Fix — Replaced T-list-coverage-1

Removed: T-list-coverage-1 with narrow `.claude/`-only detector.

Added: **T-list-coverage-broad** — comprehensive platform-test detection covering ALL platform-target patterns:

```text
python -c "import sys; from pathlib import Path; import re;
  patterns = [
    r'parents\[\d+\]\s*/\s*[\"\']scripts[\"\']',
    r'from\s+scripts\.',
    r'import\s+scripts\.',
    r'\.github/workflows',
    r'harness-state/',
    r'bridge/INDEX',
    r'groundtruth_kb',
    r'gtkb-dashboard|gtkb_dashboard|gtkb_overlay',
    r'wrap_scan|wrap_capture',
    r'adr_dcl_clause|bridge_applicability|bridge_compliance|bridge_notify',
    r'harness_identity|harness_roles|harness_parity',
    r'release_candidate|release_blocker',
    r'check_dev_environment|check_environment',
    r'claude_session_start|codex_hook',
    r'command_registry|generate_bridge_swimlane|generate_codex_skill',
    r'groundtruth_governance|gtkb_bridge|kb_attribution',
    r'owner_decision|rehearse|retroactive_harvest',
    r'run_spec_derived|session_self|session_wrap|wrap_capture',
    r'protected_artifact|isolation|spec_event',
    r'workstream_focus|formal_artifact_approval|credential_scan',
    r'\.claude/',
  ]
  combined = re.compile('|'.join(patterns));
  for f in Path('tests').rglob('*.py'):
    if combined.search(f.read_text(errors='ignore')):
      print('PLATFORM:', f)
"
```

**Expected result:** All 71 files in the F1 disposition table flagged PLATFORM. Any unflagged platform-tests indicates the detector needs further patterns added; any false positives (Agent Red tests flagged as platform) need per-file review.

## F3 Fix — Recalculated Option A vs Option B Counts

### Option A (resolved per DELIB-S334-OQ-E3-OPTION-A)

- **83 files stay at root** (corrected from -001's 32):
  - `tests/hooks/` — 13 (all)
  - `tests/scripts/` — 69 (all)
  - `tests/__init__.py` — 1 (shared)
- **0 source-code edits** to test files
- **`pyproject.toml` `testpaths`** = `["tests", "applications/Agent_Red/tests"]` (dual discovery)

### Option B (alternative; not chosen)

- **0 files stay at root** (all migrate)
- **~83 source-code edits** to platform-test files (each `Path(__file__).resolve().parents[2]` → `parents[3]`)
- Also requires updating `tests/scripts/conftest.py` if it uses `parents[N]`
- **`pyproject.toml` `testpaths`** = `["applications/Agent_Red/tests"]` (single)

The corrected counts strengthen Option A's case: Option B's 83 source-code edits would add substantial complexity to E.1 (already a 1,500+ file move) and would create coupling between platform-test files and their location depth. Option A's persistent dual-discovery is a 1-line config change.

## E.1 Implication (Updated per Corrected Counts)

Under Option A:
- **Files moved by E.1:** ~1,517 - 83 = **~1,434 files** (was estimated ~1,491-1,503; corrected lower because more files stay at root)
- **Files staying at root:** 83 (was 32)
- **Source-code edits to test files:** 0
- **`pyproject.toml` updates:** 4 fields including `testpaths = ["tests", "applications/Agent_Red/tests"]`

## Migration Strategy (E.3-specific, Updated)

Same as `-001`: E.3 is a decision-making sub-sub-slice. Now that:
1. Codex F1+F2+F3 fixes are addressed in this `-003`
2. Owner has chosen Option A (DELIB-S334-OQ-E3-OPTION-A in MemBase)

Remaining steps:
1. **Codex GO on this `-003`** (approves the corrected platform-test inventory + recalculated counts)
2. **File `-005` REPORT** capturing:
   - DELIB-S334-OQ-E3-OPTION-A reference as the operative resolution
   - The 83-file platform-test list (concretized for E.1)
   - Test execution evidence (T-decision-1 + T-test-list-1 + T-list-coverage-broad)
3. **Codex VERIFIED on `-005`** (E.1 can now draft against resolved scope)

## Specification-Derived Test Plan (Updated)

| Test ID | Spec Coverage | Procedure | Expected Result |
|---|---|---|---|
| **T-bridge-1** | `GOV-FILE-BRIDGE-AUTHORITY-001` | `grep "Document: gtkb-isolation-018-slice-e3-platform-test-disposition" bridge/INDEX.md` | Match present |
| **T-spec-1** | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-018-slice-e3-platform-test-disposition` | `preflight_passed: true` |
| **T-spec-2** | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This proposal contains Specification Links + spec-to-test mapping + executed evidence | Section present |
| **T-decision-1** | E.3 deliverable (decision capture) | `python -c "from groundtruth_kb.db import KnowledgeDB; db=KnowledgeDB(); d=db.get_deliberation('DELIB-S334-OQ-E3-OPTION-A'); print('exists:', d is not None)"` | `exists: True` (decision durably recorded) |
| **T-test-list-1** | E.3 deliverable (platform-test list enumerated) | `-005` REPORT contains the 83-file STAYS_PLATFORM list per the F1 disposition table above | List enumerated and matches live tree |
| **T-list-coverage-broad** | F2 fix — comprehensive platform-test detector | The detector in F2 Fix above run against `tests/` returns the 83 STAYS_PLATFORM files (or that set + a few false positives needing per-file review) | Detector flags all 83; any additions/exclusions justified per file |

## Acceptance Criteria

This `-003` REVISED is accepted when:
- [ ] Codex GO on this `-003`
- [ ] Complete 71-file `tests/scripts/` disposition table accepted
- [ ] tests/hooks/ 13-file disposition confirmed
- [ ] Other tests/ subdirs migration confirmed
- [ ] Option A vs Option B recalculated counts (83 vs ~83) accepted
- [ ] `DELIB-S334-OQ-E3-OPTION-A` accepted as operative resolution

E.3 sub-sub-slice is VERIFIED when:
- [ ] Codex GO on this `-003`
- [ ] `-005` REPORT filed with platform-test list + decision-capture evidence
- [ ] Codex VERIFIED on `-005`

## Pre-Filing Preflight Subsection

This `-003` will be evaluated by `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-018-slice-e3-platform-test-disposition` after INDEX update. Expected: `preflight_passed: true`.

## Provenance (additions to `-001`)

| Source | Reference |
|---|---|
| Codex NO-GO triggering this revision | `bridge/gtkb-isolation-018-slice-e3-platform-test-disposition-002.md` (F1, F2, F3) |
| Owner decision (durable) | `DELIB-S334-OQ-E3-OPTION-A` in MemBase (parallel-agent capture of S334 prose answer "Option A") |
| F1 evidence | Comprehensive grep across all 69 tests/scripts/*.py + 2 supporting files + 13 tests/hooks/ files (executed 2026-05-07) |
| F2 evidence | Broader detector pattern set in F2 Fix above |
| F3 evidence | 83 platform files identified vs ~83 source-code edits required under Option B |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
