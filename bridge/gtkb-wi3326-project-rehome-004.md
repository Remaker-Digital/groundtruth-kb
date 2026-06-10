GO
bridge_kind: lo_verdict
Document: gtkb-wi3326-project-rehome
Version: 004
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-06 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi3326-project-rehome-003.md

# Loyal Opposition Review - WI-3326 Project Re-Home

## Verdict

GO.

The revised proposal is narrow, owner-authorized, and mechanically reviewable:
it limits implementation to append-only MemBase project-membership state for
WI-3326, cites the active project authorization
`PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-WI-3326-REHOME`, and provides
pre/post relation-state verification instead of source-code tests for the
MemBase-only operation.

## Applicability Preflight

```text
## Applicability Preflight

- packet_hash: `sha256:10d4635053ee2ccf3ec3a9963669292bb4bb0784a4727a6d01b3af83327c9e7d`
- bridge_document_name: `gtkb-wi3326-project-rehome`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-wi3326-project-rehome-003.md`
- operative_file: `bridge/gtkb-wi3326-project-rehome-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi3326-project-rehome`
- Operative file: `bridge\gtkb-wi3326-project-rehome-003.md`
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

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Prior Deliberations

- `DELIB-20260624` - owner selected "Re-home WI-3326 + continue"; it directs
  keeping WI-3326 alive under `PROJECT-GTKB-DETERMINISTIC-SERVICES-001` and
  continuing WI-4266.
- `DELIB-20260741` - LO verification of `gt projects remove-item` Slice 1;
  verified the operator command and explicitly preserved the live WI-3326
  membership move as separate follow-up work.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - deterministic operator
  services should replace repetitive manual database mutation.

## Evidence Reviewed

- Full bridge thread read: `bridge/gtkb-wi3326-project-rehome-001.md` through
  `bridge/gtkb-wi3326-project-rehome-003.md`.
- Live `bridge/INDEX.md` listed latest state as
  `REVISED: bridge/gtkb-wi3326-project-rehome-003.md` before this verdict.
- `bridge/gtkb-wi3326-project-rehome-003.md:17-20` cites the project,
  project authorization, work item, and owner decision metadata.
- `bridge/gtkb-wi3326-project-rehome-003.md:39-51` limits scope to two
  membership commands and forbids source, test, setting, specification,
  deployment, credential, and history rewrite changes.
- `bridge/gtkb-wi3326-project-rehome-003.md:117-132` maps linked
  specifications to relation-state checks.
- `gt projects show PROJECT-GTKB-STARTUP-ENHANCEMENTS --json` showed active
  membership `PWM-PROJECT-GTKB-STARTUP-ENHANCEMENTS-WI-3326` on the retired
  startup project.
- `gt backlog show WI-3326 --json` showed WI-3326 remains open with
  `project_name: null`.
- `gt projects show PROJECT-GTKB-DETERMINISTIC-SERVICES-001 --json` confirmed
  the cited PAUTH is active, allows only `project_membership_mutation`, includes
  WI-4266 and WI-3326, and forbids source/test/CLI/config/deployment/spec/
  credential changes.
- Current source contains the verified operator surfaces:
  `groundtruth-kb/src/groundtruth_kb/cli.py:1953` for `projects_add_item`,
  `groundtruth-kb/src/groundtruth_kb/cli.py:1995` for `projects_remove_item`,
  `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py:166` for
  `add_project_item`, and
  `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py:193` for
  `remove_project_item`.
- `groundtruth-kb/tests/test_projects_remove_item.py:82-240` covers detach,
  append-only history, active-status rejection, remove/re-add cycle, and CLI
  command behavior.

## Findings

No blocking findings.

Residual risk is confined to operator execution and post-report evidence. The
implementation report must include before/after `gt projects show` and
`gt backlog show` evidence proving the old active-on-retired membership became
non-active history and WI-3326 became active under deterministic services.

## Implementation Conditions

Prime Builder may implement only the two commands described in the proposal,
using the repo-native CLI path if `gt` is not on PATH:

```powershell
.\groundtruth-kb\.venv\Scripts\gt.exe projects remove-item PROJECT-GTKB-STARTUP-ENHANCEMENTS WI-3326 --change-reason "Detach active-on-retired residual per DELIB-20260624"
.\groundtruth-kb\.venv\Scripts\gt.exe projects add-item PROJECT-GTKB-DETERMINISTIC-SERVICES-001 WI-3326 --change-reason "Re-home per DELIB-20260624"
```

No source, test, configuration, deployment, specification, credential, or git
history mutation is authorized by this GO.

## Commands Executed

```text
python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-wi3326-project-rehome --format json
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi3326-project-rehome
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi3326-project-rehome
.\groundtruth-kb\.venv\Scripts\gt.exe deliberations search "WI-3326 re-home deterministic services DELIB-20260624 retired startup project membership" --limit 5
.\groundtruth-kb\.venv\Scripts\gt.exe deliberations get DELIB-20260624
.\groundtruth-kb\.venv\Scripts\gt.exe deliberations get DELIB-20260741
.\groundtruth-kb\.venv\Scripts\gt.exe backlog show WI-3326 --json
.\groundtruth-kb\.venv\Scripts\gt.exe backlog show WI-4266 --json
.\groundtruth-kb\.venv\Scripts\gt.exe projects show PROJECT-GTKB-STARTUP-ENHANCEMENTS --json
.\groundtruth-kb\.venv\Scripts\gt.exe projects show PROJECT-GTKB-DETERMINISTIC-SERVICES-001 --json
rg -n "projects_remove_item" groundtruth-kb/src/groundtruth_kb/cli.py
rg -n "projects_add_item" groundtruth-kb/src/groundtruth_kb/cli.py
rg -n "def add_project_item|def remove_project_item|membership_status|status.*active|removed" groundtruth-kb/src/groundtruth_kb/project/lifecycle.py
rg -n "test_cli_remove_item|test_remove|remove-item|readd" groundtruth-kb/tests/test_projects_remove_item.py
```

Observed result: mandatory preflight passed with `missing_required_specs: []`;
mandatory clause preflight passed with zero blocking gaps.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
