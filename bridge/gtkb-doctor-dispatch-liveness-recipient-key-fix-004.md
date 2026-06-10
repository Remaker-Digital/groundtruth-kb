VERIFIED

# Loyal Opposition Verification - Doctor `_check_bridge_dispatch_liveness` recipient-key fix

bridge_kind: lo_verdict
Document: gtkb-doctor-dispatch-liveness-recipient-key-fix
Version: 004
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-04 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-doctor-dispatch-liveness-recipient-key-fix-003.md
Recommended commit type: fix

## Verdict

VERIFIED.

The implementation report satisfies the mandatory specification-derived verification gate. The source/test changes are already committed in the current checkout (`ed5696c2`, `e584f9ca`, `10329f78`), the live thread has no INDEX/file drift, and the reported behavior reproduces against the current tree when pytest uses an existing in-root temp directory available to this Codex environment.

## Applicability Preflight

- packet_hash: `sha256:f84d1eed9bad68f6643ca28b3df35bf58e971a4d3a27e89a6caac1629a457503`
- bridge_document_name: `gtkb-doctor-dispatch-liveness-recipient-key-fix`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-doctor-dispatch-liveness-recipient-key-fix-003.md`
- operative_file: `bridge/gtkb-doctor-dispatch-liveness-recipient-key-fix-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/**, content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:work item |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-doctor-dispatch-liveness-recipient-key-fix`
- Operative file: `bridge\gtkb-doctor-dispatch-liveness-recipient-key-fix-003.md`
- Clauses evaluated: 5
- must_apply: 2, may_apply: 3, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | - | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | - | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

## Prior Deliberations

- `DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09` - carried forward from the proposal/GO; records the smart-poller retirement and canonical dispatch substrate.
- `DELIB-1796` - carried forward from the GO; Smart-Poller Doctor-Path Fix context.
- `DELIB-0719` - carried forward from the GO; doctor severity/startup-term owner-decision context.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - carried forward from the report; false-alarm output is a deterministic-service token tax.
- Local deliberation search for `WI-4307 doctor dispatch liveness recipient key` found no newer contrary owner decision or prior rejection that changes this verification.

## Specifications Carried Forward

- `GOV-RELIABILITY-FAST-LANE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001`

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
|---|---|---|---|
| `GOV-RELIABILITY-FAST-LANE-001` | `python -m pytest tests\test_doctor_bridge_dispatch_liveness.py -v --tb=short -p no:cacheprovider` with `TEMP/TMP=E:\GT-KB\.pytest_tmp_lo` | yes | 12 passed |
| `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` | `test_run_doctor_distinguishes_claude_from_codex_recipients_in_report`; `test_run_doctor_recipient_keys_match_cross_harness_trigger_canonical_labels`; `rg` inspection of `_BRIDGE_AGENT_TO_RECIPIENT` and `ROLE_STATE_KEYS` | yes | pass; doctor mapping values are `prime-builder` and `loyal-opposition`, matching trigger keys |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | `test_run_doctor_recipient_keys_match_cross_harness_trigger_canonical_labels`; live `_check_bridge_dispatch_liveness(Path("."), agent)` spot-check against `.gtkb-state/bridge-poller/dispatch-state.json` | yes | pass; live messages now report stale canonical recipient entries, not missing legacy keys |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Path inspection of changed files and `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-doctor-dispatch-liveness-recipient-key-fix` | yes | in-root `groundtruth-kb/` only; zero blocking gaps |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Bridge thread plus committed source/test/report artifacts | yes | durable proposal, GO, implementation report, and verification verdict exist |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-doctor-dispatch-liveness-recipient-key-fix --format json --preview-lines 0` | yes | `drift=[]`; latest before verdict was post-implementation `NEW -003` |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Review of project/work item/owner-decision evidence in `-003` | yes | report carries WI-4307, project, PAUTH, project membership, and owner AUQ evidence |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-doctor-dispatch-liveness-recipient-key-fix` | yes | preflight passed with no missing required/advisory specs |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This table plus reproduced lint/format/pytest/live-state evidence | yes | every carried-forward spec has executed verification evidence |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Bridge lifecycle inspection: `NEW -001`, `GO -002`, `NEW -003`, `VERIFIED -004` | yes | defect work item followed proposal, implementation report, and verification chain |

## Positive Confirmations

- `_BRIDGE_AGENT_TO_RECIPIENT` now maps `claude` to `prime-builder` and `codex` to `loyal-opposition`.
- The regression test `test_run_doctor_recipient_keys_match_cross_harness_trigger_canonical_labels` compares doctor mapping values to `scripts.cross_harness_bridge_trigger.ROLE_STATE_KEYS` and rejects legacy `prime`/`codex` keys.
- The widened `groundtruth-kb/tests/test_doctor.py` touchpoint is a paired test-fixture correction under the same canonical-key defect class and remains inside the standing PAUTH source/test scope.
- Ruff lint and format gates passed for all three changed files.
- The live-state spot-check reports true staleness ALARMs for canonical recipient keys rather than missing `recipients.prime` or `recipients.codex` false-key ALARMs.

## Findings

None.

## Commands Executed

```text
python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-doctor-dispatch-liveness-recipient-key-fix --format json --preview-lines 0
# drift=[]

python scripts\bridge_applicability_preflight.py --bridge-id gtkb-doctor-dispatch-liveness-recipient-key-fix
# preflight_passed: true; missing_required_specs: []; missing_advisory_specs: []

python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-doctor-dispatch-liveness-recipient-key-fix
# exit 0; blocking gaps: 0

groundtruth-kb\.venv\Scripts\gt.exe deliberations search "WI-4307 doctor dispatch liveness recipient key" --limit 10
# no newer contrary owner decision or prior rejection found

git diff --name-only HEAD --
# no tracked source/test/report diff at verification time

git log --oneline -5 -- bridge\gtkb-doctor-dispatch-liveness-recipient-key-fix-003.md groundtruth-kb\src\groundtruth_kb\project\doctor.py groundtruth-kb\tests\test_doctor_bridge_dispatch_liveness.py groundtruth-kb\tests\test_doctor.py bridge\INDEX.md
# a4ef4b8a docs(bridge): revise init keyword packet blocker
# 10329f78 docs(bridge): file post-impl report -003 for doctor dispatch-liveness key fix (WI-4307)
# e584f9ca test(doctor): align test_doctor.py recipient keys with canonical role labels
# ed5696c2 fix(gtkb): align doctor dispatch recipient keys
# cab949a2 doc(bridge): file GO verdict for doctor dispatch liveness recipient-key fix

groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb\src\groundtruth_kb\project\doctor.py groundtruth-kb\tests\test_doctor_bridge_dispatch_liveness.py groundtruth-kb\tests\test_doctor.py
# All checks passed!

groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check groundtruth-kb\src\groundtruth_kb\project\doctor.py groundtruth-kb\tests\test_doctor_bridge_dispatch_liveness.py groundtruth-kb\tests\test_doctor.py
# 3 files already formatted

groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests\test_doctor_bridge_dispatch_liveness.py -v --tb=short
# initial reproduction failed at fixture setup because this Codex environment cannot access C:\Users\micha\AppData\Local\Temp\pytest-of-micha; two tests that did not use tmp_path passed

cd groundtruth-kb
$env:TEMP = 'E:\GT-KB\.pytest_tmp_lo'
$env:TMP = 'E:\GT-KB\.pytest_tmp_lo'
.\.venv\Scripts\python.exe -m pytest tests\test_doctor_bridge_dispatch_liveness.py -v --tb=short -p no:cacheprovider
# 12 passed in 4.76s

cd groundtruth-kb
$env:TEMP = 'E:\GT-KB\.pytest_tmp_lo'
$env:TMP = 'E:\GT-KB\.pytest_tmp_lo'
.\.venv\Scripts\python.exe -m pytest tests\test_doctor.py -v --tb=short -k "bridge or dispatch or poller" -p no:cacheprovider
# 6 passed, 31 deselected in 0.19s

python - <<spot-check equivalent via stdin>>
from pathlib import Path
from groundtruth_kb.project.doctor import _check_bridge_dispatch_liveness
for agent in ('claude', 'codex'):
    r = _check_bridge_dispatch_liveness(Path('.'), agent)
    print(f'{agent}: status={r.status} | {r.message[:180]}')
# claude: status=fail | claude bridge dispatch: ALARM (last update 4118m 47s ago, state: unchanged, pending: 52) ...
# codex: status=fail | codex bridge dispatch: ALARM (last update 4118m 47s ago, state: no_pending, pending: 0) ...
```

## Owner Action Required

None.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
