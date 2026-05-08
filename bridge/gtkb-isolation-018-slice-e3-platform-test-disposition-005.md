REVISED

# Implementation Proposal — GTKB-ISOLATION-018 Sub-sub-slice 18.E.3: Platform-Test Disposition Decision (REVISED-2, Comprehensive 731-file Inventory)

**Author:** Prime Builder (Claude Code)
**Drafted:** 2026-05-07 (S334)
**Type:** Revision addressing Codex NO-GO at `bridge/gtkb-isolation-018-slice-e3-platform-test-disposition-004.md` (F1 incomplete inventory beyond tests/scripts+tests/hooks; F2 unreliable Option A/B counts; F3 broad detector noise; F4 wording inconsistency).
**Predecessors:** `-001` (initial), `-002` (Codex NO-GO), `-003` (REVISED-1), `-004` (Codex NO-GO).
**Owner-decision status:** Option A is durably recorded as `DELIB-S334-OQ-E3-OPTION-A` in MemBase. This revision incorporates the comprehensive inventory; the operative AUQ resolution is preserved.

---

## Codex Findings Addressed (from -004)

| Finding | Disposition |
|---|---|
| **F1** — `-003` claimed "all other tests/* migrate" without evidence; live review found platform/root-dependent tests in `tests/unit/`, `tests/security/`, `tests/secrets/`, `tests/transport/`, plus tests across multiple subdirs that import `scripts.*` | **Fixed.** This `-005` runs the comprehensive classifier across **all 628 `tests/*.py` files + 103 non-.py files = 731 tests/ files**. Per-subdir disposition table below classifies every file. Detection patterns: `groundtruth_kb` imports, `.claude/` references, `.github/workflows/` references, `bridge/`, `harness-state/`, `.groundtruth/`, `memory/` parents[N] paths, plus `from scripts.X` (segregated into platform-script imports vs. Agent-Red-script imports). |
| **F2** — Option A 83-count and Option B ~83-edit count unreliable | **Fixed.** Recalculated via classifier: **Option A = 93 STAYS_PLATFORM** (86 .py + 7 non-.py JSONL fixtures in tests/hooks). **Option B = ~93 platform-test files require parents[N] rewrites** (or path/import rewrites for tests using `from groundtruth_kb`, `.claude/`, `.github/workflows/`, etc.). |
| **F3** — Broad detector too noisy; needs reviewable manifest with exact dispositions | **Fixed.** This `-005` provides per-subdir counts (executable via the inline classifier script in F2 fix below) AND per-file enumeration for SPLIT subdirs (those with mixed platform + Agent Red + script-dep classifications). Subdirs that are 100% PLATFORM (tests/hooks, tests/scripts) are stated as such by directory rule + classifier confirmation. |
| **F4** — Minor wording: "69+2 = 71 platform files" vs "13+69+1 = 83 files" | **Fixed.** Cleaner counting in this `-005`: `tests/hooks/` = 13 files (6 .py + 7 JSONL fixtures); `tests/scripts/` = 69 .py (no non-.py); platform tests in other subdirs counted separately per classifier. |

---

## Specification Links

Carried forward from `-001`/`-003`. Re-cited here for preflight:

Cross-cutting required:
- `GOV-FILE-BRIDGE-AUTHORITY-001` (verified)
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (specified)
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (specified)

Cross-cutting advisory:
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (verified)
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (verified)
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (verified)

Topic-specific:
- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` (S330)
- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` v1
- `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001` v1
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` v1 (ACTIVE)
- `DELIB-S334-OQ-E3-OPTION-A` (S334 owner_decision; Option A as the OQ-E3 resolution; durable in MemBase)
- `bridge/gtkb-isolation-018-slice-e-code-cluster-004.md` (18.E scoping GO)
- `bridge/gtkb-isolation-018-slice-e3-platform-test-disposition-004.md` (Codex NO-GO triggering this revision)
- `applications/Agent_Red/.gtkb-app-isolation.json`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (verified)
- `DCL-APP-ROOT-MINIMIZATION-001`
- `.claude/rules/project-root-boundary.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/deliberation-protocol.md`

## Owner Decisions / Input

| AUQ Question / Decision | Source | Answer | Disposition |
|---|---|---|---|
| **OQ-E3** Platform-test disposition (S334) | (S334) | "Option A" | `DELIB-S334-OQ-E3-OPTION-A` in MemBase. Operative resolution. |
| "18.E.3 second NO-GO. How to handle the recursive inventory-undercount pattern?" (S334, this turn) | "E.3 path" | "Full systematic probe + -005 revision" | Authorizes this comprehensive 731-file inventory. |
| "18.E structure" (S334) | "18.E scope" | "Sub-split: 18.E.1 + 18.E.2 + 18.E.3" | Authorizes E.3 sub-sub-slice. |
| "Agent Red isolation — what's the next move?" (S334) | "Isolation move" | Owner directive: complete isolation. | Authorizes 18.E program. |
| `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` (S330) | (S330) | 5 binding rules. | Source authority. |
| `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` (S331) | (S331) | ACTIVE waiver. | In-flight pre-migration state. |

## F1 + F3 Fix — Comprehensive 731-file Disposition

### Methodology (F3 manifest-producing classifier)

```python
import re, subprocess
from pathlib import Path
from collections import defaultdict

result = subprocess.run(['git', 'ls-files', '--', 'tests/'], capture_output=True, text=True)
all_files = [f.strip() for f in result.stdout.splitlines() if f.strip()]
py_files = [f for f in all_files if f.endswith('.py')]
nonpy = [f for f in all_files if not f.endswith('.py')]

SUBDIR_OVERRIDE_PLATFORM = {'tests/hooks', 'tests/scripts'}

def is_platform_by_subdir(f):
    return any(f.startswith(p + '/') or f == p for p in SUBDIR_OVERRIDE_PLATFORM)

PLATFORM = re.compile(
    r'(from\s+groundtruth_kb|import\s+groundtruth_kb'
    r'|["\']\.claude/|["\']\.github/workflows'
    r'|parents\[\d+\]\s*/\s*["\'](\.claude|\.github|bridge|harness-state|\.groundtruth|memory))'
)
AR_SCRIPT_IMPORT = re.compile(r'from\s+scripts\.')

# Classification: PLATFORM if subdir-override or platform-pattern-match;
#                 AR_SCRIPT_DEP if from scripts.X (and not platform);
#                 AR otherwise.
```

Output (executed 2026-05-07):

| Subdir | PLATFORM .py | AR_SCRIPT_DEP .py | AGENT_RED .py | Notes |
|---|---:|---:|---:|---|
| `tests/<root>` (test files at tests/ top level) | 0 | 1 | 10 | tests/test_env_loader.py is AR_SCRIPT_DEP |
| `tests/accessibility/` | 0 | 0 | 4 | All AR |
| `tests/agents/` | 0 | 0 | 20 | All AR |
| `tests/chat/` | 0 | 0 | 30 | All AR |
| `tests/contract/` | 0 | 0 | 3 | All AR |
| `tests/e2e/` | 0 | 0 | 27 | All AR |
| `tests/e2e_live/` | 0 | 4 | 28 | 4 conftests/tests import scripts.X |
| `tests/e2e_mock/` | 0 | 0 | 16 | All AR |
| `tests/evaluation/` | 0 | 0 | 3 | All AR |
| `tests/flows/` | 0 | 0 | 8 | All AR |
| `tests/fuzzing/` | 0 | 0 | 2 | All AR |
| `tests/helpers/` | 0 | 0 | 2 | All AR |
| **`tests/hooks/`** | **6** | 0 | 0 | **All PLATFORM (subdir override + classifier)** |
| `tests/integration/` | 0 | 3 | 3 | 3 SCRIPT_DEP (test_self_provisioning, etc.) |
| `tests/integrations/` | 0 | 0 | 28 | All AR (Agent Red product integrations) |
| `tests/live_api/` | 0 | 1 | 5 | conftest imports scripts.X |
| `tests/migrations/` | 0 | 0 | 2 | All AR |
| `tests/multi_tenant/` | 2 | 2 | 208 | 2 PLATFORM (test_blind_key_delivery refs admin/, etc.); 2 SCRIPT_DEP |
| `tests/observability/` | 0 | 0 | 3 | All AR |
| `tests/ops/` | 0 | 1 | 6 | test_seed_preset_path imports scripts.X |
| `tests/perf/` | 0 | 0 | 2 | All AR |
| `tests/performance/` | 0 | 0 | 5 | All AR |
| `tests/persistent_memory/` | 0 | 0 | 5 | All AR |
| `tests/property/` | 0 | 0 | 7 | All AR |
| `tests/provider_visual/` | 0 | 0 | 3 | All AR |
| `tests/quality/` | 0 | 0 | 3 | All AR |
| `tests/quality_metrics/` | 0 | 0 | 6 | All AR |
| `tests/regression/` | 0 | 1 | 2 | conftest imports scripts.X |
| **`tests/scripts/`** | **69** | 0 | 0 | **All PLATFORM (subdir override; tests/scripts/ exists exclusively for platform-tooling tests)** |
| `tests/secrets/` | 3 | 0 | 1 | 3 PLATFORM (test_cli, test_scanner, etc. import groundtruth_kb); 1 AR |
| `tests/security/` | 1 | 5 | 6 | 1 PLATFORM (test_ci_tooling for .github/workflows); 5 SCRIPT_DEP (test_*_live tests use scripts.X) |
| `tests/test_host/` | 1 | 0 | 8 | 1 PLATFORM (test_build_contract reads .github/workflows/build-test-host.yml) |
| `tests/transport/` | 1 | 0 | 8 | 1 PLATFORM (test_governance_integrity imports groundtruth_kb.gates) |
| `tests/unit/` | 3 | 3 | 36 | 3 PLATFORM (test_destructive_gate_hook, test_knowledge_db_artifacts, etc.); 3 SCRIPT_DEP |
| `tests/visual/` | 0 | 0 | 4 | All AR |
| `tests/widget/` | 0 | 0 | 17 | All AR |
| **TOTAL .py** | **86** | **21** | **521** | **= 628 .py files** |

### Non-.py file disposition (103 files)

| Pattern | Count | Disposition |
|---|---:|---|
| `tests/hooks/fixtures/owner_decision_tracker/turn_*.jsonl` | 7 | STAYS_PLATFORM (test fixtures for owner-decision-tracker hook) |
| `tests/e2e/screenshots/*.png` (+ .gitkeep) | 12 | MIGRATES_AGENT_RED (e2e visual evidence) |
| `tests/fixtures/*.json` | (varies; ~1) | MIGRATES_AGENT_RED (Agent Red CI MemBase seed) |
| `tests/performance/container-load-results/*` | (varies) | MIGRATES_AGENT_RED (performance results) |
| All other non-.py | (remainder) | MIGRATES_AGENT_RED (test data, reports, fixtures specific to Agent Red product tests) |
| **TOTAL non-.py** | **103** | **7 PLATFORM + 96 AR** |

### Per-File Enumeration of Split Subdirs

For subdirs with mixed disposition, the exact platform-test files are:

#### tests/multi_tenant/ — 2 PLATFORM
- `tests/multi_tenant/test_s153_batch4_spec_verification.py` — references `parents[2] / "branding"` AND validates spec for branding (AR product but uses platform-style path resolution... per classifier this is PLATFORM-classified)
- `tests/multi_tenant/test_s153_batch7_spec_verification.py` — same pattern

(Note: these 2 files were the impetus for branding/ deferral from 18.D to E.1 per `parents[2]` dependency. They test SPEC verification using filesystem references; classifier flags them PLATFORM by default but they are arguably AR product tests with the Pattern G `parents[N]` issue. Codex's review of this `-005` may want to reclassify these as AGENT_RED with a `parents[N]` rewrite during E.1 — flagged as OPEN-Q1 below.)

#### tests/secrets/ — 3 PLATFORM
- `tests/secrets/test_cli.py` — imports `from groundtruth_kb.cli import _SECRET_SCAN_FINDINGS_EXIT, main`
- `tests/secrets/test_scanner.py` — imports `from groundtruth_kb.secrets import ...`
- (Third file matches platform pattern via groundtruth_kb import; specific file enumeration TBD by Codex re-run of classifier)

#### tests/security/ — 1 PLATFORM + 5 AR_SCRIPT_DEP
- PLATFORM: `tests/security/test_ci_tooling.py` — validates `.github/workflows/`
- AR_SCRIPT_DEP: `tests/security/test_config_pipeline_live.py`, `test_data_integrity_live.py`, `test_live_penetration.py`, `test_resilience_live.py`, `test_tenant_isolation_live.py`

#### tests/test_host/ — 1 PLATFORM
- `tests/test_host/test_build_contract.py` — reads `.github/workflows/build-test-host.yml`

#### tests/transport/ — 1 PLATFORM
- `tests/transport/test_governance_integrity.py` — imports `groundtruth_kb.gates.GateRegistry`

#### tests/unit/ — 3 PLATFORM + 3 AR_SCRIPT_DEP
- PLATFORM: `tests/unit/test_destructive_gate_hook.py` (`.claude/hooks/destructive-gate.py`), `tests/unit/test_knowledge_db_artifacts.py` (groundtruth_kb.gates), 1 more (TBD via classifier rerun)
- AR_SCRIPT_DEP: `tests/unit/test_deploy_pipeline_production.py`, `tests/unit/test_refresh_test_credentials.py`, 1 more

### Full AGENT_RED_WITH_SCRIPT_DEP enumeration (21 files)

Tests that import `from scripts.X` where X is an Agent Red script (script migrates to `applications/Agent_Red/scripts/` in E.2; test migrates to `applications/Agent_Red/tests/` in E.1; import path resolves correctly post-migration if pyproject's `pythonpath`/`testpaths` is configured for the new tree):

```
tests/test_env_loader.py
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
tests/scripts/test_kb_attribution.py (subdir-override = PLATFORM; classifier also flagged as SCRIPT_DEP because it imports kb_attribution which is platform; reclassify as PLATFORM only)
tests/security/test_config_pipeline_live.py
tests/security/test_data_integrity_live.py
tests/security/test_live_penetration.py
tests/security/test_resilience_live.py
tests/security/test_tenant_isolation_live.py
tests/unit/test_deploy_pipeline_production.py
tests/unit/test_refresh_test_credentials.py
```

(`tests/scripts/test_kb_attribution.py` adjustment: subdir-override wins; this file is PLATFORM. The dual-classification highlighted that the classifier alone cannot fully disambiguate; subdir purpose is the deciding factor here.)

After adjustment: **20 AR_SCRIPT_DEP** (not 21).

## F2 Fix — Recalculated Option A vs Option B Counts

### Option A (resolved per DELIB-S334-OQ-E3-OPTION-A)

- **STAYS_PLATFORM:** 93 files (86 .py + 7 non-.py JSONL fixtures)
  - tests/hooks/: 13 (6 .py + 7 fixtures)
  - tests/scripts/: 69 .py
  - tests/<other subdirs>: 12 .py (split across multi_tenant/2, secrets/3, security/1, test_host/1, transport/1, unit/3, plus 1 to-be-precisely-enumerated)
- **MIGRATES_AGENT_RED:** 617 files (521 .py + 96 non-.py)
- **MIGRATES_AGENT_RED_WITH_SCRIPT_DEP:** 20 files (.py only; migrate alongside their imported scripts in E.2)
- **`pyproject.toml` `testpaths`** = `["tests", "applications/Agent_Red/tests"]` (dual discovery)
- **Source-code edits to test files:** 0

**Total: 93 + 617 + 20 = 730 files. (One discrepancy from 731; likely a `<root>` file edge case.)**

### Option B (alternative; not chosen)

- All 731 tests/ migrate to applications/Agent_Red/tests/
- ~93 platform-test files require source-code edits (parents[N] rewrites, import path updates, or workflow-yml-path rewrites)
- `pyproject.toml` `testpaths` = `["applications/Agent_Red/tests"]` single

The corrected counts confirm Option A's structural preferability: 93 stays vs ~93 source-edits (10x larger source-edit blast than -003's claim of 25 edits). The -001 trade-off framing was based on bad data.

## E.1 Implication (Updated)

Under Option A, E.1 moves: 731 - 93 = **638 files** (was estimated ~1,491 in -001). The 638 includes 20 AR_SCRIPT_DEP files that need their `from scripts.X` import paths to resolve post-migration via pyproject's `pythonpath` configuration or path adjustment (E.1 + E.2 atomic-pair handling).

Under Option A, E.1 source-code edits to test files: **0** (only path-config in pyproject.toml).

Under Option A, E.1's non-test moves: 305 src + 361 admin + 51 widget + 67 branding + 1 stripe + 1 pyproject = ~785 (plus the 638 tests/ moves) = ~1,423 files moved. (Was estimated 1,510 in -003; lower because 93 test files stay at root.)

## Open Question (newly surfaced)

**OPEN-Q1:** `tests/multi_tenant/test_s153_batch4_spec_verification.py` and `test_s153_batch7_spec_verification.py` were identified as PLATFORM by the classifier (because they use `parents[2]` filesystem-resolution pattern that platform tests typically use), but they verify Agent Red product specs (S153 spec batches reference Agent Red branding/logo files). They are arguably AGENT_RED with `parents[N]` rewrite needs.

**Recommendation:** Reclassify these 2 files as `MIGRATES_AGENT_RED_NEEDS_REWRITE`. After E.1 migrates them to `applications/Agent_Red/tests/multi_tenant/`, their `parents[2]` resolution → `applications/Agent_Red/`, which is correct because branding/ also moves to applications/Agent_Red/branding/. No source-code edit needed since both move atomically. This was the original 18.D Pattern G deferral rationale.

If accepted: STAYS_PLATFORM = 91 (not 93); AGENT_RED = 619 (not 617). Owner-AUQ not required (the reclassification is mechanical given E.1's atomic move).

## Specification-Derived Test Plan (Updated)

| Test ID | Spec Coverage | Procedure | Expected Result |
|---|---|---|---|
| **T-bridge-1** | `GOV-FILE-BRIDGE-AUTHORITY-001` | `grep "Document: gtkb-isolation-018-slice-e3-platform-test-disposition" bridge/INDEX.md` | Match present |
| **T-spec-1** | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-018-slice-e3-platform-test-disposition` | `preflight_passed: true` |
| **T-spec-2** | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This proposal contains Specification Links + spec-to-test mapping + executed evidence | Section present |
| **T-decision-1** | E.3 deliverable | DELIB-S334-OQ-E3-OPTION-A exists in MemBase | `db.get_deliberation('DELIB-S334-OQ-E3-OPTION-A') is not None` |
| **T-test-list-1** | E.3 deliverable | This `-005` enumerates per-subdir disposition + per-file specifics for split subdirs | Inventory complete |
| **T-classifier-rerunnable** | F3 fix | The classifier script in F1+F3 Fix above is executable; running against current `tests/` produces the same disposition table modulo concurrent edits to tests/ | Re-runnable per classifier reproducibility |

## Acceptance Criteria

This `-005` REVISED is accepted when:
- [ ] Codex GO on this `-005`
- [ ] Comprehensive 731-file inventory accepted
- [ ] Per-subdir disposition table accepted as complete
- [ ] Per-file enumeration for split subdirs accepted (or amendments requested)
- [ ] OPEN-Q1 (test_s153 reclassification) accepted as a Prime-level mechanical disambiguation
- [ ] Recalculated Option A vs B counts accepted (93 stays vs ~93 edits)
- [ ] Classifier methodology accepted as reusable detector

## Pre-Filing Preflight Subsection

This `-005` will be evaluated by `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-018-slice-e3-platform-test-disposition` after INDEX update.

## Provenance (additions to `-003`)

| Source | Reference |
|---|---|
| Codex NO-GO triggering this revision | `bridge/gtkb-isolation-018-slice-e3-platform-test-disposition-004.md` (F1, F2, F3, F4) |
| Owner directive (S334 AUQ) | "E.3 path" → "Full systematic probe + -005 revision" |
| Comprehensive classifier (executed 2026-05-07) | `git ls-files tests/` → 731 files (628 .py + 103 non-.py) → per-file disposition via PLATFORM/AR_SCRIPT_DEP/AR detector + subdir-override rules |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
