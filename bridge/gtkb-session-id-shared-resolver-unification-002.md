NO-GO

bridge_kind: lo_verdict
Document: gtkb-session-id-shared-resolver-unification
Version: 002
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-03 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-session-id-shared-resolver-unification-001.md

# Loyal Opposition Review - Shared Session-ID Resolver Unification Proposal

## Verdict

NO-GO.

The proposal is directionally sound and the predecessor minimal fix is already VERIFIED, but the proposed target scope is incomplete. It includes `scripts/workstream_focus.py` and proposes replacing its marker-session fallback tuple with the new shared helper order, yet existing marker/doctor parity tests and the doctor marker resolver are outside `target_paths`. As filed, implementation either breaks existing marker precedence/parity tests or fails the proposal's own acceptance criterion that the marker writer delegates to the shared helper.

## Applicability Preflight

- packet_hash: `sha256:6bc26958bab1615ea60539e3c728d2d9606dec90be4b8ba90631228a6ef33f41`
- bridge_document_name: `gtkb-session-id-shared-resolver-unification`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-session-id-shared-resolver-unification-001.md`
- operative_file: `bridge/gtkb-session-id-shared-resolver-unification-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-session-id-shared-resolver-unification`
- Operative file: `bridge\gtkb-session-id-shared-resolver-unification-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

## Prior Deliberations

- `DELIB-20260625` - owner authorization to implement WI-4270 through the shared-helper follow-on.
- `DECISION-0899` - owner selected the shared-helper design over minimal-additive and hybrid approaches.
- `DECISION-0900` - owner selected `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`.
- `DECISION-0901` - owner sequenced this shared-helper work after the minimal fix.
- `bridge/gtkb-claude-code-session-id-env-var-gap-012.md` - predecessor minimal fix VERIFIED.

## Findings

### F1 - Proposal changes marker precedence without including marker/doctor parity scope

**Observation:** The proposal's `target_paths` include `scripts/workstream_focus.py` but do not include `groundtruth-kb/src/groundtruth_kb/project/doctor.py`, `platform_tests/hooks/test_workstream_focus_session_role_marker.py`, or `platform_tests/scripts/test_doctor_session_role_marker.py`. The proposal says the new canonical helper order is `CLAUDE_SESSION_ID`, `CLAUDE_CODE_SESSION_ID`, `GTKB_INHERITED_SESSION_ID`, `CODEX_SESSION_ID`, `CODEX_THREAD_ID`, `ANTIGRAVITY_SESSION_ID`, `GTKB_SESSION_ID`; it also says `scripts/workstream_focus.py` will replace its divergent tuple with the shared helper. Current `scripts/workstream_focus.py` and the doctor marker resolver put `GTKB_SESSION_ID` first, and existing tests assert that precedence and parity.

**Deficiency rationale:** This is not only a test-list omission. The marker writer and doctor currently share a contract: explicit GT-KB marker continuity wins over live harness env vars. If `workstream_focus.py` adopts the proposal's helper order while the doctor and existing tests remain out of scope, the implementation either breaks current marker/doctor tests or leaves the marker writer outside the shared helper, contradicting proposal acceptance criterion 2. The proposal must decide whether marker continuity should keep `GTKB_SESSION_ID` first or whether both marker writer and doctor should move to the new shared order.

**Evidence source:** `bridge/gtkb-session-id-shared-resolver-unification-001.md` line 14 target paths; lines 192-210 shared helper order and `workstream_focus.py` migration; `scripts/workstream_focus.py` lines 1085-1089 current marker resolver order; `groundtruth-kb/src/groundtruth_kb/project/doctor.py` lines 2818-2822 current doctor resolver order; `platform_tests/hooks/test_workstream_focus_session_role_marker.py` lines 187-192 precedence assertion; `platform_tests/scripts/test_doctor_session_role_marker.py` lines 145-146 precedence fixture.

**Impact:** Prime could receive GO for a scope that is internally inconsistent. The implementation would either fail existing marker/doctor tests, silently weaken session-role continuity, or omit a named consumer from the shared resolver migration.

**Recommended action:** Revise the proposal to include the affected doctor and parity-test surfaces in `target_paths`, or explicitly exclude marker/doctor precedence from this slice and remove `workstream_focus.py` from the shared-helper migration. The revised verification plan should include the existing marker and doctor session-role marker tests, plus new assertions for whichever precedence policy is chosen.

**Option rationale:** Expanding/reconciling scope is lower risk than approving a refactor whose acceptance criteria conflict with existing marker semantics. It preserves the owner-selected shared-helper direction while forcing the proposal to settle the marker-continuity edge case before implementation.

## Positive Evidence

- `show_thread_bridge.py` reports live latest `NEW` with no drift.
- Applicability preflight passes with no missing required or advisory specs.
- ADR/DCL clause preflight passes with zero blocking gaps.
- `WI-4270` exists, is open, and is associated with `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`.
- The predecessor minimal `CLAUDE_CODE_SESSION_ID` fix is VERIFIED at `bridge/gtkb-claude-code-session-id-env-var-gap-012.md`.

## Required Revisions

1. Decide and state the intended precedence for marker continuity: should `GTKB_SESSION_ID` remain first for marker writer/doctor surfaces, or should all consumers adopt one global order?
2. If all consumers adopt one global order, add `groundtruth-kb/src/groundtruth_kb/project/doctor.py`, `platform_tests/hooks/test_workstream_focus_session_role_marker.py`, and `platform_tests/scripts/test_doctor_session_role_marker.py` to `target_paths`.
3. Update the verification plan to run the marker writer and doctor marker tests, not only the new shared-helper and bridge-work-intent tests.
4. If marker/doctor precedence is intentionally different, remove `scripts/workstream_focus.py` from the shared-helper migration acceptance criterion or define a helper API that supports explicit precedence variants without reintroducing drift.
5. File a REVISED proposal with the target paths and tests aligned to the chosen behavior.

## Commands Executed

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-session-id-shared-resolver-unification
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-session-id-shared-resolver-unification
python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-session-id-shared-resolver-unification --format json --preview-lines 40
python scripts\implementation_authorization.py begin --bridge-id gtkb-session-id-shared-resolver-unification --no-write
rg -n "SESSION_ID_ENV_VARS|SESSION_ENV_VARS|GTKB_SESSION_ID|CLAUDE_CODE_SESSION_ID|GTKB_INHERITED_SESSION_ID|ANTIGRAVITY_SESSION_ID" scripts\workstream_focus.py groundtruth-kb\src\groundtruth_kb\project\doctor.py platform_tests\hooks\test_workstream_focus_session_role_marker.py platform_tests\scripts\test_doctor_session_role_marker.py
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb backlog show WI-4270 --json
Select-String -Path bridge\gtkb-session-id-shared-resolver-unification-001.md -Pattern "workstream_focus|marker writer|doctor|target_paths|precedence|GTKB_SESSION_ID|Spec-Derived" -Context 1,2
```

Note: `implementation_authorization.py begin --no-write` correctly returned unauthorized because the latest status is still `NEW`; that command was diagnostic only and is not used as a GO precondition here.

## Owner Action Required

None.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
