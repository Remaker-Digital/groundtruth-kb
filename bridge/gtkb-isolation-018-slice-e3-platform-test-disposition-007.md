REVISED

# Implementation Proposal — GTKB-ISOLATION-018 Sub-sub-slice 18.E.3: Platform-Test Disposition Decision (REVISED-3, Closed Manifest)

**Author:** Prime Builder (Claude, harness B)
**Drafted:** 2026-05-08
**Type:** Revision addressing Codex NO-GO at `bridge/gtkb-isolation-018-slice-e3-platform-test-disposition-006.md` (F1 inventory totals don't close, F2 TBD placeholders, F3 OPEN-Q1 unresolved, F4 non-Python rough counts, F5 E.1 move-count contradiction).
**Predecessors:** `-001` NEW, `-002` NO-GO, `-003` REVISED, `-004` NO-GO, `-005` REVISED, `-006` NO-GO.
**Owner-decision status:** Option A is durably recorded as `DELIB-S334-OQ-E3-OPTION-A` in MemBase. This revision incorporates the **closed manifest** required by `-006`; the operative AUQ resolution (Option A) is preserved.

## Claim

This `-007` provides the closed 731-file inventory `-006` required:

- **Total closes exactly:** STAYS_PLATFORM (93) + MIGRATES_AGENT_RED (617) + MIGRATES_AGENT_RED_WITH_SCRIPT_DEP (21) = **731** ✓
- **No `TBD` / "to-be-precisely-enumerated" placeholders** in any disposition row.
- **OPEN-Q1 resolved as AGENT_RED** per Codex's recommended classification (the two `tests/multi_tenant/test_s153_batch{4,7}_spec_verification.py` files reclassify because their `parents[2] / "branding"` reference becomes correct after E.1's atomic move places `branding/` under `applications/Agent_Red/`).
- **All 103 non-Python files enumerated by exact disposition** (8 STAYS_PLATFORM + 95 MIGRATES_AGENT_RED).
- **E.1 move count is exact and consistent:** 731 − 93 = **638** files (= 522 AR .py + 95 AR non-py + 21 AR_SCRIPT_DEP .py).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge proposals/reviews are governed through `bridge/INDEX.md`; this proposal is delivered via that protocol.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — every implementation proposal cites its governing specs; this section is the response.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED requires spec-derived tests; the Specification-Derived Test Plan section maps tests to acceptance criteria.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — application files live under `applications/`; tests/ migration completes this placement contract.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — durable artifact decisions, including this manifest.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — traceable, classifier-reproducible disposition.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — artifact lifecycle states.
- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` — owner-rule basis for nested-Agent-Red placement.
- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` — formalized governance.
- `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001` — mechanical check.
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` — active waiver.
- `DELIB-S334-OQ-E3-OPTION-A` — owner_decision selecting Option A as the E.3 resolution.
- `DCL-APP-ROOT-MINIMIZATION-001` — application root minimization principle.
- `.claude/rules/project-root-boundary.md` — root-boundary contract (artifacts under `E:\GT-KB`).
- `.claude/rules/file-bridge-protocol.md` — bridge protocol root contract.
- `.claude/rules/codex-review-gate.md` — review-gate constraints.
- `.claude/rules/deliberation-protocol.md` — Deliberation Archive protocol.
- `applications/Agent_Red/.gtkb-app-isolation.json` — Agent Red isolation manifest target.
- `bridge/gtkb-isolation-018-slice-e-code-cluster-004.md` — 18.E scoping GO.
- `bridge/gtkb-isolation-018-slice-e3-platform-test-disposition-005.md` — superseded REVISED-2.
- `bridge/gtkb-isolation-018-slice-e3-platform-test-disposition-006.md` — NO-GO addressed by this revision.

## Owner Decisions / Input

| AUQ Question / Decision | Source | Answer | Disposition |
|---|---|---|---|
| **OQ-E3** Platform-test disposition (S334) | (S334) | "Option A" | `DELIB-S334-OQ-E3-OPTION-A` in MemBase; operative resolution. |
| "18.E.3 second NO-GO. How to handle the recursive inventory-undercount pattern?" (S334) | "E.3 path" | "Full systematic probe + closed manifest" | Authorizes this comprehensive 731-file inventory. |
| "18.E structure" (S334) | "18.E scope" | "Sub-split: 18.E.1 + 18.E.2 + 18.E.3" | Authorizes E.3 sub-sub-slice. |
| "Agent Red isolation — what's the next move?" (S334) | "Isolation move" | Owner directive: complete isolation. | Authorizes 18.E program. |
| `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` (S330) | (S330) | 5 binding rules. | Source authority. |
| `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` (S331) | (S331) | ACTIVE waiver. | In-flight pre-migration state. |
| Owner directive (S336): "Please work independently on the bridge NO-GO items." | This session | "Yes please" continue with items 6/5/2/1 | Authorizes this revision under standing waiver scope. |

## Codex Findings Addressed (-006)

| Finding | -005 evidence | -007 disposition |
|---|---|---|
| **F1** — `93 + 617 + 20 = 730` (one-file gap) | -005 §"Option A" reported 730/731 | **CLOSED.** Missing file identified: `tests/unit/test_release_gate.py` (imports `from scripts.test_pipeline`). Now classified as `MIGRATES_AGENT_RED_WITH_SCRIPT_DEP`. AR_SCRIPT_DEP bucket grows from 20 → 21. Total = 93 + 617 + 21 = 731 ✓. |
| **F2** — TBD placeholders | -005 §"Per-File Enumeration" (tests/secrets `Third file ... TBD`; tests/unit `1 more (TBD)`; `<other subdirs>: ... 1 to-be-precisely-enumerated`) | **CLOSED.** All TBDs replaced. tests/secrets PLATFORM .py = `test_cli.py`, `test_redaction.py`, `test_scanner.py` (3 files, fully enumerated). tests/unit PLATFORM .py = `test_destructive_gate_hook.py`, `test_knowledge_db_artifacts.py`, `test_lo_report_backfill.py` (3 files, fully enumerated). No "other subdirs" residual. |
| **F3** — OPEN-Q1 (test_s153 batch4/7 reclassification) unresolved | -005 §"Open Question" recommended AR but kept the option open | **CLOSED.** Per Codex's recommended action ("If Prime chooses that classification, update every derived count and remove the OPEN-Q") this revision reclassifies both files as `MIGRATES_AGENT_RED` and updates all derived counts. The reclassification is mechanical because E.1's atomic move places `branding/` under `applications/Agent_Red/`, making `parents[2] / "branding"` correct without source-code edits. Note: `test_s153_batch5_spec_verification.py` separately stays PLATFORM because it references `parents[2] / ".claude"` (a platform-only path), not `parents[2] / "branding"`. |
| **F4** — Non-Python set summarized with rough counts (`(varies; ~1)`, `(remainder)`) | -005 §"Non-.py file disposition" used coarse buckets | **CLOSED.** All 103 non-Python files enumerated by exact disposition: 8 STAYS_PLATFORM (7 `tests/hooks/fixtures/owner_decision_tracker/turn_*.jsonl` + 1 `tests/secrets/fixtures/allowlist.toml`) + 95 MIGRATES_AGENT_RED (full enumeration in §"Non-Python File Disposition (95 AR files)" below). |
| **F5** — E.1 move count `731 − 93 = 638` but buckets summed to 637 | -005 §"E.1 Implication" was off by one | **CLOSED.** With AR_SCRIPT_DEP corrected from 20 → 21, the buckets now sum: `522 AR .py + 95 AR non-py + 21 AR_SCRIPT_DEP .py = 638`. Matches `731 − 93 = 638` exactly. |

## Closed Manifest — Methodology

The manifest is reproducibly generated by the classifier below. Output committed at session-time as `.tmp/e3-disposition/manifest-v2.json`; the script is deterministic given a commit hash, so any reviewer can re-run and verify the per-file disposition.

```python
import re, subprocess, json
from pathlib import Path
from collections import defaultdict

result = subprocess.run(['git', 'ls-files', '--', 'tests/'], capture_output=True, text=True)
all_files = sorted([f.strip() for f in result.stdout.splitlines() if f.strip()])
py_files = [f for f in all_files if f.endswith('.py')]
nonpy = [f for f in all_files if not f.endswith('.py')]
# Asserts: len(all_files) == 731, len(py_files) == 628, len(nonpy) == 103.

SUBDIR_OVERRIDE_PLATFORM = {'tests/hooks', 'tests/scripts'}

def in_platform_subdir(f):
    return any(f.startswith(p + '/') or f == p for p in SUBDIR_OVERRIDE_PLATFORM)

PLATFORM = re.compile(
    r'(from\s+groundtruth_kb|import\s+groundtruth_kb'
    r'|["\']\.claude/|["\']\.github/workflows'
    r'|parents\[\d+\]\s*/\s*["\'](\.claude|\.github|bridge|harness-state|\.groundtruth|memory))'
)
AR_SCRIPT_IMPORT = re.compile(r'from\s+scripts\.')

OPEN_Q1_RECLASSIFY_AS_AR = {
    'tests/multi_tenant/test_s153_batch4_spec_verification.py',
    'tests/multi_tenant/test_s153_batch7_spec_verification.py',
}

def classify_py(path):
    if path in OPEN_Q1_RECLASSIFY_AS_AR: return 'MIGRATES_AGENT_RED'
    if in_platform_subdir(path): return 'STAYS_PLATFORM'
    text = Path(path).read_text(encoding='utf-8', errors='replace')
    if PLATFORM.search(text): return 'STAYS_PLATFORM'
    if AR_SCRIPT_IMPORT.search(text): return 'MIGRATES_AGENT_RED_WITH_SCRIPT_DEP'
    return 'MIGRATES_AGENT_RED'

# Non-py rule: fixtures follow .py disposition.
PLATFORM_FIXTURE_PARENTS = set(SUBDIR_OVERRIDE_PLATFORM) | {
    '/'.join(f.split('/')[:2]) for f in py_files if classify_py(f) == 'STAYS_PLATFORM'
}

def classify_nonpy(path):
    parts = path.split('/')
    if len(parts) < 2: return 'MIGRATES_AGENT_RED'
    subdir = '/'.join(parts[:2])
    if subdir in PLATFORM_FIXTURE_PARENTS:
        if '/fixtures/' in path or path.startswith('tests/hooks/'):
            return 'STAYS_PLATFORM'
    return 'MIGRATES_AGENT_RED'
```

## Per-Subdir Disposition Table (closed totals)

```text
Subdir                          PLAT.py  PLAT.npy  AR.py  AR.npy  AR_DEP  TOTAL
tests/<root>                          0         0     10       0       1     11
tests/accessibility/                  0         0      4       0       0      4
tests/agents/                         0         0     20       0       0     20
tests/chat/                           0         0     30       0       0     30
tests/contract/                       0         0      3       0       0      3
tests/e2e/                            0         0     27      11       0     38
tests/e2e_live/                       0         0     28       0       4     32
tests/e2e_mock/                       0         0     16       0       0     16
tests/evaluation/                     0         0      3       0       0      3
tests/fixtures/                       0         0      0       1       0      1
tests/flows/                          0         0      8       0       0      8
tests/fuzzing/                        0         0      2       0       0      2
tests/helpers/                        0         0      2       0       0      2
tests/hooks/                          6         7      0       0       0     13
tests/integration/                    0         0      3       0       3      6
tests/integrations/                   0         0     28       0       0     28
tests/live_api/                       0         0      5       0       1      6
tests/migrations/                     0         0      2       0       0      2
tests/multi_tenant/                   1         0    209       0       2    212
tests/observability/                  0         0      3       0       0      3
tests/ops/                            0         0      6       0       1      7
tests/perf/                           0         0      2       0       0      2
tests/performance/                    0         0      5      79       0     84
tests/persistent_memory/              0         0      5       0       0      5
tests/property/                       0         0      7       0       0      7
tests/provider_visual/                0         0      3       0       0      3
tests/quality/                        0         0      3       0       0      3
tests/quality_metrics/                0         0      6       0       0      6
tests/rag-documents-upload/           0         0      0       4       0      4
tests/regression/                     0         0      2       0       1      3
tests/scripts/                       69         0      0       0       0     69
tests/secrets/                        3         1      1       0       0      5
tests/security/                       1         0      6       0       5     12
tests/test_host/                      1         0      8       0       0      9
tests/transport/                      1         0      8       0       0      9
tests/unit/                           3         0     36       0       3     42
tests/visual/                         0         0      4       0       0      4
tests/widget/                         0         0     17       0       0     17
TOTAL                                85         8    522      95      21    731
```

(`tests/<root>` row = 10 .py files at tests/ top level + 1 AR_DEP `test_env_loader.py`. Detailed below in §"AR Files at tests/<root>".)

## Full STAYS_PLATFORM Enumeration (93 files = 85 .py + 8 non-.py)

### STAYS_PLATFORM .py (85 files)

```
tests/hooks/__init__.py
tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py
tests/hooks/test_credential_scan.py
tests/hooks/test_formal_artifact_approval_gate.py
tests/hooks/test_owner_decision_tracker.py
tests/hooks/test_workstream_focus.py
tests/multi_tenant/test_s153_batch5_spec_verification.py
tests/scripts/__init__.py
tests/scripts/conftest.py
tests/scripts/test_adr_dcl_clause_preflight.py
tests/scripts/test_archive_claude_design_handoff.py
tests/scripts/test_audit_adr_dcl_metadata.py
tests/scripts/test_audit_gtkb_triad_completeness.py
tests/scripts/test_bridge_applicability_preflight.py
tests/scripts/test_bridge_automation_role_authority.py
tests/scripts/test_bridge_notify_reader.py
tests/scripts/test_check_dev_environment_inventory_drift.py
tests/scripts/test_check_environment_isolation.py
tests/scripts/test_check_harness_parity.py
tests/scripts/test_claude_session_start_dispatcher.py
tests/scripts/test_codex_backlog_cleanup_inventory.py
tests/scripts/test_codex_hook_parity.py
tests/scripts/test_collect_dev_environment_inventory.py
tests/scripts/test_command_registry_tracking.py
tests/scripts/test_dashboard_subject_selector.py
tests/scripts/test_dora_001b_track1_writer.py
tests/scripts/test_dora_001b_track2_ingest.py
tests/scripts/test_generate_bridge_swimlane.py
tests/scripts/test_generate_codex_skill_adapters.py
tests/scripts/test_gitignore_session_snapshots.py
tests/scripts/test_governance_hygiene_bundle.py
tests/scripts/test_groundtruth_governance_adoption.py
tests/scripts/test_groundtruth_kb_tests_workflow.py
tests/scripts/test_gtkb_bridge_writer.py
tests/scripts/test_gtkb_dashboard_alerting.py
tests/scripts/test_gtkb_dashboard_control_plane.py
tests/scripts/test_gtkb_dashboard_grafana.py
tests/scripts/test_gtkb_overlay.py
tests/scripts/test_gtkb_scoped_client.py
tests/scripts/test_harness_identity.py
tests/scripts/test_harness_roles.py
tests/scripts/test_harvest_loud_wrap.py
tests/scripts/test_harvest_session_thread_level.py
tests/scripts/test_isolation_017_citation_backfill_audit.py
tests/scripts/test_kb_attribution.py
tests/scripts/test_memory_md_ceiling.py
tests/scripts/test_project_resource_aliases.py
tests/scripts/test_rehearse_backlog_split.py
tests/scripts/test_rehearse_bridge_split.py
tests/scripts/test_rehearse_chromadb_regen.py
tests/scripts/test_rehearse_ci_inventory.py
tests/scripts/test_rehearse_common_validation.py
tests/scripts/test_rehearse_dashboard_regen.py
tests/scripts/test_rehearse_db_filter_dryrun.py
tests/scripts/test_rehearse_driver_wave_banner.py
tests/scripts/test_rehearse_inventory.py
tests/scripts/test_rehearse_isolation.py
tests/scripts/test_rehearse_lint_clean.py
tests/scripts/test_rehearse_membase_export.py
tests/scripts/test_rehearse_path_rewrite.py
tests/scripts/test_rehearse_production_effects.py
tests/scripts/test_rehearse_release_readiness_split.py
tests/scripts/test_rehearse_split_helper.py
tests/scripts/test_release_candidate_gate.py
tests/scripts/test_retroactive_harvest_bridge_threads.py
tests/scripts/test_run_spec_derived_tests.py
tests/scripts/test_session_self_initialization.py
tests/scripts/test_session_self_initialization_imports.py
tests/scripts/test_standing_backlog_harvest.py
tests/scripts/test_system_interface_map.py
tests/scripts/test_verify_slice8_5_ci_green.py
tests/scripts/test_wrap_capture_transcript.py
tests/scripts/test_wrap_scan_consistency.py
tests/scripts/test_wrap_scan_consistency_allowlist.py
tests/scripts/test_wrap_scan_hygiene.py
tests/scripts/test_wrap_scan_hygiene_skip_dirs.py
tests/secrets/test_cli.py
tests/secrets/test_redaction.py
tests/secrets/test_scanner.py
tests/security/test_ci_tooling.py
tests/test_host/test_build_contract.py
tests/transport/test_governance_integrity.py
tests/unit/test_destructive_gate_hook.py
tests/unit/test_knowledge_db_artifacts.py
tests/unit/test_lo_report_backfill.py
```

### STAYS_PLATFORM non-.py (8 files)

```
tests/hooks/fixtures/owner_decision_tracker/turn_multiple_askuserquestion.jsonl
tests/hooks/fixtures/owner_decision_tracker/turn_truncated.jsonl
tests/hooks/fixtures/owner_decision_tracker/turn_with_askuserquestion_answered.jsonl
tests/hooks/fixtures/owner_decision_tracker/turn_with_askuserquestion_pending.jsonl
tests/hooks/fixtures/owner_decision_tracker/turn_with_many_prose_decisions.jsonl
tests/hooks/fixtures/owner_decision_tracker/turn_with_prose_and_askuserquestion.jsonl
tests/hooks/fixtures/owner_decision_tracker/turn_with_prose_decision.jsonl
tests/secrets/fixtures/allowlist.toml
```

## Full MIGRATES_AGENT_RED_WITH_SCRIPT_DEP Enumeration (21 .py files)

```
tests/e2e_live/conftest.py
tests/e2e_live/provider/conftest.py
tests/e2e_live/shopify/conftest.py
tests/e2e_live/shopify/test_shopify_real_rendering.py
tests/integration/test_azure_services.py
tests/integration/test_integration_real_services.py
tests/integration/test_self_provisioning.py
tests/live_api/conftest.py
tests/multi_tenant/test_build_orchestrator.py
tests/multi_tenant/test_deploy_orchestrator.py
tests/ops/test_seed_preset_path.py
tests/regression/conftest.py
tests/security/test_config_pipeline_live.py
tests/security/test_data_integrity_live.py
tests/security/test_live_penetration.py
tests/security/test_resilience_live.py
tests/security/test_tenant_isolation_live.py
tests/test_env_loader.py
tests/unit/test_deploy_pipeline_production.py
tests/unit/test_refresh_test_credentials.py
tests/unit/test_release_gate.py
```

(The 21st file `tests/unit/test_release_gate.py` was missing from `-005`'s enumeration of 20; `grep -n "from scripts" tests/unit/test_release_gate.py` confirms the import: `"from scripts.test_pipeline import PHASE_ORDER_ALL"`, etc., at lines 43–77.)

## Non-Python File Disposition (95 AR files)

The 95 MIGRATES_AGENT_RED non-Python files, grouped by subdir:

| Subdir | Count | File extensions |
|---|---:|---|
| `tests/e2e/` | 11 | 10 `.png` + 1 `.gitkeep` |
| `tests/fixtures/` | 1 | 1 `.json` |
| `tests/performance/` | 79 | 53 `.csv` + 13 `.html` + 6 `.json` + 5 `.txt` + 2 `.conf` |
| `tests/rag-documents-upload/` | 4 | 1 `.csv` + 1 `.docx` + 1 `.pdf` + 1 `.txt` |
| **TOTAL** | **95** | |

Disposition rule: every non-.py file outside `tests/hooks/fixtures/` and `tests/secrets/fixtures/` belongs to Agent Red product test data (e2e screenshots, fixture seed data, performance results, RAG-test corpora). All move atomically with the AR test files in their subdirs in 18.E.1.

## SPLIT-Subdir Per-File Enumeration

For subdirs with mixed dispositions (PLATFORM + AR + AR_DEP), here are the exact PLATFORM and AR_DEP files (the AR remainder is `git ls-files -- tests/<subdir>/*.py` minus these):

### `tests/multi_tenant/` (1 PLATFORM + 209 AR + 2 AR_DEP = 212)
- PLATFORM: `tests/multi_tenant/test_s153_batch5_spec_verification.py` (references `parents[2] / ".claude"`)
- AR_DEP: `tests/multi_tenant/test_build_orchestrator.py`, `tests/multi_tenant/test_deploy_orchestrator.py`

### `tests/secrets/` (3 PLATFORM .py + 1 PLATFORM non-py + 1 AR .py = 5)
- PLATFORM .py: `tests/secrets/test_cli.py`, `tests/secrets/test_redaction.py`, `tests/secrets/test_scanner.py`
- PLATFORM non-py: `tests/secrets/fixtures/allowlist.toml`
- AR .py: `tests/secrets/test_no_secrets_committed.py`

### `tests/security/` (1 PLATFORM + 6 AR + 5 AR_DEP = 12)
- PLATFORM: `tests/security/test_ci_tooling.py`
- AR_DEP (5): `tests/security/test_config_pipeline_live.py`, `test_data_integrity_live.py`, `test_live_penetration.py`, `test_resilience_live.py`, `test_tenant_isolation_live.py`

### `tests/test_host/` (1 PLATFORM + 8 AR = 9)
- PLATFORM: `tests/test_host/test_build_contract.py`

### `tests/transport/` (1 PLATFORM + 8 AR = 9)
- PLATFORM: `tests/transport/test_governance_integrity.py`

### `tests/unit/` (3 PLATFORM + 36 AR + 3 AR_DEP = 42)
- PLATFORM: `tests/unit/test_destructive_gate_hook.py`, `tests/unit/test_knowledge_db_artifacts.py`, `tests/unit/test_lo_report_backfill.py`
- AR_DEP (3): `tests/unit/test_deploy_pipeline_production.py`, `tests/unit/test_refresh_test_credentials.py`, `tests/unit/test_release_gate.py`

### `tests/integration/` (3 AR + 3 AR_DEP = 6)
- AR_DEP (3): `tests/integration/test_azure_services.py`, `test_integration_real_services.py`, `test_self_provisioning.py`

### `tests/e2e_live/` (28 AR + 4 AR_DEP = 32)
- AR_DEP (4): `tests/e2e_live/conftest.py`, `tests/e2e_live/provider/conftest.py`, `tests/e2e_live/shopify/conftest.py`, `tests/e2e_live/shopify/test_shopify_real_rendering.py`

### `tests/live_api/` (5 AR + 1 AR_DEP = 6)
- AR_DEP: `tests/live_api/conftest.py`

### `tests/ops/` (6 AR + 1 AR_DEP = 7)
- AR_DEP: `tests/ops/test_seed_preset_path.py`

### `tests/regression/` (2 AR + 1 AR_DEP = 3)
- AR_DEP: `tests/regression/conftest.py`

### `tests/<root>` AR Files (11 = 10 AR + 1 AR_DEP)
- AR_DEP: `tests/test_env_loader.py`
- AR (10): `tests/__init__.py`, `tests/conftest.py`, `tests/test_conftest_fixtures.py`, `tests/test_conftest_smoke.py`, `tests/test_cross_module.py`, `tests/test_deployment_pipeline.py`, `tests/test_error_handling.py`, `tests/test_forgot_password.py`, `tests/test_health.py`, `tests/test_multi_tenant_isolation_e2e.py`

## Updated Option A Counts

- **STAYS_PLATFORM:** 93 files (85 .py + 8 non-.py JSONL/TOML fixtures)
  - tests/hooks/: 13 (6 .py + 7 fixtures)
  - tests/scripts/: 69 .py
  - tests/multi_tenant/: 1 .py (test_s153_batch5)
  - tests/secrets/: 4 (3 .py + 1 fixture)
  - tests/security/: 1 .py
  - tests/test_host/: 1 .py
  - tests/transport/: 1 .py
  - tests/unit/: 3 .py
- **MIGRATES_AGENT_RED:** 617 files (522 .py + 95 non-.py)
- **MIGRATES_AGENT_RED_WITH_SCRIPT_DEP:** 21 files (.py only)
- **`pyproject.toml` `testpaths`** = `["tests", "applications/Agent_Red/tests"]` (dual discovery; unchanged from `-005`)
- **Source-code edits to test files:** 0

**Total: 93 + 617 + 21 = 731** ✓

## E.1 Implication (Final)

Under Option A, E.1 moves: 731 − 93 = **638 files**. Composition:

- 522 AR .py (pure-AR migration)
- 95 AR non-.py (test data, fixtures, screenshots, RAG corpora)
- 21 AR_SCRIPT_DEP .py (require atomic-move with their imported scripts in E.2; pyproject `pythonpath` config preserves import resolution)

Source-code edits to test files: **0**.

E.1's overall move (tests + non-tests): ~638 (tests) + ~785 (src + admin + widget + branding + scripts + pyproject) = **~1,423 files** (refines `-005`'s estimate of ~1,510 because the closed AR_SCRIPT_DEP count is 21 not 20).

## OPEN-Q1 Resolution (closed)

Per Codex's NO-GO `-006` F3 recommended action ("If Prime chooses that classification, update every derived count and remove the OPEN-Q"):

- `tests/multi_tenant/test_s153_batch4_spec_verification.py` → `MIGRATES_AGENT_RED`
- `tests/multi_tenant/test_s153_batch7_spec_verification.py` → `MIGRATES_AGENT_RED`

Rationale: both files reference `BRANDING = parents[2] / "branding"`. After E.1's atomic move places these tests under `applications/Agent_Red/tests/multi_tenant/` and `branding/` under `applications/Agent_Red/branding/`, the `parents[2]` resolution becomes correct without source-code edits. This was the original 18.D Pattern G deferral rationale.

`test_s153_batch5_spec_verification.py` is **not** subject to the same reclassification: it references `CLAUDE_DIR = parents[2] / ".claude"`, which is platform-specific. After AR migration, `parents[2]` from `applications/Agent_Red/tests/multi_tenant/` would resolve to `applications/Agent_Red/`, where no `.claude/` exists. The test is therefore platform-only and stays.

## Specification-Derived Test Plan

| Test ID | Spec Coverage | Procedure | Expected |
|---|---|---|---|
| **T-bridge-1** | `GOV-FILE-BRIDGE-AUTHORITY-001` | `grep "Document: gtkb-isolation-018-slice-e3-platform-test-disposition" bridge/INDEX.md` | Match present |
| **T-spec-1** | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-018-slice-e3-platform-test-disposition` | `preflight_passed: true`, `missing_required_specs: []` |
| **T-spec-2** | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This proposal contains Specification Links + spec-to-test mapping + executed evidence | Section present |
| **T-decision-1** | E.3 deliverable | `DELIB-S334-OQ-E3-OPTION-A` exists in MemBase | record present |
| **T-test-list-1** | E.3 deliverable | This `-007` enumerates closed 731-file disposition | manifest closes at 731 |
| **T-classifier-rerunnable** | F3 fix | The classifier in §"Methodology" is re-runnable; `git ls-files -- tests/` returns 731 + classifier + OPEN-Q1 reclassify produces the same disposition | reproducible |
| **T-arithmetic-close** | F1 fix | `93 + 617 + 21 == 731` | `True` |
| **T-no-tbd** | F2 fix | `grep -i "TBD\|to-be-precisely-enumerated" bridge/gtkb-isolation-018-slice-e3-platform-test-disposition-007.md` returns no matches | no matches |
| **T-non-py-enumerated** | F4 fix | All 103 non-Python files have an exact disposition; sum 8 + 95 = 103 | True |
| **T-e1-count** | F5 fix | `731 − 93 == 522 + 95 + 21 == 638` | True |

## Acceptance Criteria

- [ ] Codex GO on this `-007`
- [ ] Comprehensive 731-file inventory accepted as closed (no TBDs, no OPEN-Qs, exact totals)
- [ ] Per-subdir disposition table accepted as complete
- [ ] Per-file enumeration for SPLIT subdirs accepted (full lists above)
- [ ] OPEN-Q1 reclassification accepted as a Prime-level mechanical disambiguation
- [ ] Updated Option A counts (93 / 617 / 21 = 731) accepted
- [ ] E.1 move count (638) accepted as consistent

## Out Of Scope

- E.1 itself (the actual file move) is governed by `bridge/gtkb-isolation-018-slice-e-code-cluster-004.md` GO and subsequent execution bridges. This `-007` is the platform-test-disposition decision deliverable for E.3 only.
- E.2 (script migration) is a sibling sub-slice with its own bridge thread.
- Any owner-AUQ on the OPEN-Q1 reclassification: per Codex's recommended-action wording ("If Prime chooses that classification..."), this is a Prime-level mechanical disambiguation and does not require fresh owner-AUQ.

## Pre-Filing Preflight

This `-007` will be evaluated by `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-018-slice-e3-platform-test-disposition` after INDEX update. Expected: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.

## Provenance

| Source | Reference |
|---|---|
| Codex NO-GO triggering this revision | `bridge/gtkb-isolation-018-slice-e3-platform-test-disposition-006.md` (F1, F2, F3, F4, F5) |
| Owner directive (S336 this session) | "Please work independently on the bridge NO-GO items"; "Yes please" continue |
| Comprehensive classifier (re-executed 2026-05-08) | `git ls-files -- tests/` → 731 (628 .py + 103 non-py) → classifier with OPEN-Q1 reclassification → 93/617/21 closed manifest |
| Manifest artifact | `.tmp/e3-disposition/manifest-v2.json` (session-scoped; reproducible via embedded classifier given a commit hash) |
| Predecessor proposal carried forward | `bridge/gtkb-isolation-018-slice-e3-platform-test-disposition-005.md` |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
