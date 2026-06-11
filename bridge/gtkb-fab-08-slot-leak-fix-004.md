NO-GO

bridge_kind: verification_verdict
Document: gtkb-fab-08-slot-leak-fix
Version: 004
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-11 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-fab-08-slot-leak-fix-003.md

# FAB-08 Slot-Leak Fix - Verification Verdict

## Applicability Preflight

- packet_hash: `sha256:a0060189e603d3dd8638c807239efa69c07959ee9bcf3062e72b4885bd5bfc87`
- bridge_document_name: `gtkb-fab-08-slot-leak-fix`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-fab-08-slot-leak-fix-003.md`
- operative_file: `bridge/gtkb-fab-08-slot-leak-fix-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: `["applications/_test_*/**"]`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`

| Spec | Severity | Cited | Matched By |
|---|---|---|---|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | advisory | yes | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | blocking | yes | path:applications/**, path:groundtruth-kb/src/groundtruth_kb/project/**, content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | advisory | yes | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | blocking | yes | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | blocking | yes | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | advisory | yes | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | blocking | yes | doc:*, path:bridge/** |

The missing-parent warning is expected after purge: no `applications/_test_*` slots remain.

## Clause Applicability

- Bridge id: `gtkb-fab-08-slot-leak-fix`
- Operative file: `bridge\gtkb-fab-08-slot-leak-fix-003.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory. Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

## Prior Deliberations

- `DELIB-FAB08-REMEDIATION-20260610` - owner chose fix + purge + doctor auto-clean for HYG-053 and deferred Agent_Red `application.toml` backfill to a separate Agent-Red-scoped bridge.
- `bridge/gtkb-fab-08-slot-leak-fix-001.md` - proposal.
- `bridge/gtkb-fab-08-slot-leak-fix-002.md` - GO with constraints.

## Specifications Carried Forward

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
|---|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-fab-08-slot-leak-fix --format json --preview-lines 40` after writing verdict | yes | PASS; latest `NO-GO`, `drift=[]` |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-fab-08-slot-leak-fix` | yes | PASS; no missing required/advisory specs |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest platform_tests\scripts\test_fab08_slot_leak_fix.py -q`; `python -m pytest groundtruth-kb\tests\test_scaffold_isolation.py -q`; ruff check/format | yes | FAB08 tests pass; ruff pass; scaffold suite has two known HYG-023 fixture failures |
| `GOV-STANDING-BACKLOG-001` | Review report Backlog Visibility plus no `groundtruth.db`/work_items diff in target set | yes | PASS for no bulk backlog/MemBase mutation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `Get-ChildItem applications -Directory -Filter _test_*` and implementation diff scope inspection | yes | PASS for purge scope: no `_test_*` dirs remain, `Agent_Red` remains |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Prior-deliberation citation and report artifact review | yes | PASS |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Report/deletion inventory review in `-003` plus live applications count | yes | PASS |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Review generated implementation report lifecycle evidence | yes | PASS |

## Positive Confirmations

- Mandatory bridge applicability preflight passed with no missing required or advisory specs.
- Mandatory ADR/DCL clause preflight passed with zero blocking gaps.
- `platform_tests/scripts/test_fab08_slot_leak_fix.py` passed locally: 5 passed.
- Targeted `ruff check` and `ruff format --check` passed for all five changed Python files.
- `applications/` currently contains no `_test_*` directories; `Agent_Red` remains present.
- The FAB08-specific doctor check reports `no stale _test_* slots (>24h)`.

## Findings

### P1 - The implementation breaks the advertised Python 3.11 runtime

Observation: `groundtruth-kb/pyproject.toml` still advertises `requires-python = ">=3.11"` and Ruff target `py311`, but the new removal helpers call `shutil.rmtree(path, onexc=_on_rm_error)` in `groundtruth-kb/src/groundtruth_kb/project/doctor.py`, `groundtruth-kb/tests/adopter/conftest.py`, `groundtruth-kb/tests/test_cli.py`, and `groundtruth-kb/tests/test_scaffold_isolation.py`.

Deficiency rationale: `onexc` is a Python 3.12+ `shutil.rmtree` keyword. On Python 3.11, these helpers raise `TypeError: rmtree() got an unexpected keyword argument 'onexc'` instead of pruning stale slots or cleaning test sandboxes. That violates the package's declared runtime contract and makes the recurrence-prevention path fail on a supported interpreter.

Proposed solution: either replace the helper with a Python 3.11-compatible implementation using `onerror` (or a version-adaptive `onexc`/`onerror` wrapper), or intentionally raise the package runtime floor and adjust all supporting metadata/tests. The least-disruptive fix is a compatibility wrapper, because FAB08 does not otherwise need a runtime-floor change.

Prime Builder implementation context: the owner deliberation asked for an `onexc` helper, but the implementation must reconcile that with the live project metadata. A version-adaptive helper preserves the owner intent while keeping `>=3.11` support intact.

## Required Revisions

1. Make `_force_remove_tree` and each `_force_rmtree` helper compatible with the declared Python 3.11 floor, or explicitly route and justify a runtime-floor change in scope.
2. Add or adjust a test that would fail if the helper passes an unsupported keyword on the project runtime floor. If direct Python 3.11 execution is unavailable in the verifier environment, use an inspect/signature-based compatibility test or a monkeypatch around `shutil.rmtree`.
3. Re-run the FAB08 focused pytest, targeted ruff check/format, and the doctor stale-slot confirmation.

## Commands Executed

```powershell
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-fab-08-slot-leak-fix
```

Result: PASS; `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.

```powershell
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-fab-08-slot-leak-fix
```

Result: PASS; clauses evaluated 5, evidence gaps 0, blocking gaps 0.

```powershell
groundtruth-kb\.venv\Scripts\gt.exe deliberations get DELIB-FAB08-REMEDIATION-20260610
```

Result: PASS; owner decision confirms fix + purge + doctor auto-clean, with HYG-022 deferred.

```powershell
rg -n "requires-python|target-version|onexc|shutil\.rmtree" groundtruth-kb\pyproject.toml groundtruth-kb\src\groundtruth_kb\project\doctor.py groundtruth-kb\tests\adopter\conftest.py groundtruth-kb\tests\test_cli.py groundtruth-kb\tests\test_scaffold_isolation.py
```

Result: `requires-python = ">=3.11"` and `target-version = "py311"` found; new `onexc` calls found in all new removal helpers.

```powershell
python -m pytest platform_tests\scripts\test_fab08_slot_leak_fix.py -q
```

Result: PASS; 5 passed.

```powershell
python -m pytest groundtruth-kb\tests\test_scaffold_isolation.py -q
```

Result: 19 passed, 2 failed. The two failures are the reported HYG-023 golden fixture mismatches in `.claude\hooks\bridge-compliance-gate.py`, not the FAB08 cleanup path.

```powershell
python -m ruff check groundtruth-kb\tests\adopter\conftest.py groundtruth-kb\tests\test_scaffold_isolation.py groundtruth-kb\tests\test_cli.py groundtruth-kb\src\groundtruth_kb\project\doctor.py platform_tests\scripts\test_fab08_slot_leak_fix.py
python -m ruff format --check groundtruth-kb\tests\adopter\conftest.py groundtruth-kb\tests\test_scaffold_isolation.py groundtruth-kb\tests\test_cli.py groundtruth-kb\src\groundtruth_kb\project\doctor.py platform_tests\scripts\test_fab08_slot_leak_fix.py
```

Result: PASS; all checks passed, 5 files already formatted.

```powershell
python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-fab-08-slot-leak-fix --format json --preview-lines 40
```

Result: PASS; latest `NO-GO` at `bridge/gtkb-fab-08-slot-leak-fix-004.md`, `drift=[]`.

```powershell
groundtruth-kb\.venv\Scripts\gt.exe project doctor --dir E:\GT-KB --json
```

Result: overall FAIL on unrelated platform hygiene findings, but FAB08-specific check PASS: `Stale test-sandbox auto-prune (applications/_test_*)` reported `no stale _test_* slots (>24h)`.

## Owner Action Required

None. This is an implementation revision issue, not an owner decision.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
