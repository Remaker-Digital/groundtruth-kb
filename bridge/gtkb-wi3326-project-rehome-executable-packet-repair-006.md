VERIFIED

bridge_kind: lo_verdict
Document: gtkb-wi3326-project-rehome-executable-packet-repair
Version: 006
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-07 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi3326-project-rehome-executable-packet-repair-005.md
Verdict: VERIFIED
Recommended commit type: chore:

# Loyal Opposition Verification - WI-3326 Executable Packet Repair Corrected Report

## Verdict

VERIFIED.

The corrected implementation report at
`bridge/gtkb-wi3326-project-rehome-executable-packet-repair-005.md` reconciles
the stale blocker report with live MemBase state. Mandatory bridge preflights
pass, the cached implementation authorization packet matches the approved
membership-only scope, and current first-class project membership evidence
shows WI-3326 removed from the retired startup project and active under
`PROJECT-GTKB-DETERMINISTIC-SERVICES-001`.

No additional WI-3326 database mutation is required while the current relation
rows remain in this shape. WI-4266 remains open for a later governed backlog
disposition, which is outside this membership-only PAUTH.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi3326-project-rehome-executable-packet-repair
```

Observed output:

```text
## Applicability Preflight

- packet_hash: `sha256:70d010e295344123e556cc87636e982f32a1bbde097b4fc32891c704457d33cf`
- bridge_document_name: `gtkb-wi3326-project-rehome-executable-packet-repair`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-wi3326-project-rehome-executable-packet-repair-005.md`
- operative_file: `bridge/gtkb-wi3326-project-rehome-executable-packet-repair-005.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:blocked, content:superseded, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi3326-project-rehome-executable-packet-repair
```

Observed output:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi3326-project-rehome-executable-packet-repair`
- Operative file: `bridge\gtkb-wi3326-project-rehome-executable-packet-repair-005.md`
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
```

## Prior Deliberations

- `DELIB-20260624` - owner selected re-home WI-3326 to deterministic services
  and continue WI-4266.
- `DELIB-20260741` - prior verification of the project-membership operator
  preserved the live WI-3326 move as separate follow-up work.
- `DELIB-20260744` and `DELIB-20260746` - prior LO review history for
  `gt projects remove-item`, WI-4266, and WI-3326 active-on-retired membership
  cleanup.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - deterministic operator
  services should replace repetitive manual database mutation.

Exact readback of `DELIB-20260624` confirmed the owner selected "Re-home
WI-3326 + continue", keeping WI-3326 open and re-parented to
`PROJECT-GTKB-DETERMINISTIC-SERVICES-001`.

## Specifications Carried Forward

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
|---|---|---|---|
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | `Get-Content .gtkb-state\implementation-authorizations\by-bridge\gtkb-wi3326-project-rehome-executable-packet-repair.json` | yes | PASS: packet records latest GO, PAUTH `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-WI-3326-REHOME`, requirement sufficiency, and target `groundtruth.db`. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Authorization packet readback plus read-only relation query | yes | PASS: live changes are WI-3326 project-membership rows only; no source/test/config/deploy/spec/credential scope is implicated. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi3326-project-rehome-executable-packet-repair` | yes | PASS: no missing required or advisory specs. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Corrected report review, `gt projects show` checks, `gt backlog show` checks, and read-only SQLite relation query | yes | PASS: each linked spec has executed evidence and the corrected report maps acceptance criteria to live relation state. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-wi3326-project-rehome-executable-packet-repair --format json --preview-lines 60` and `bridge/INDEX.md` inspection | yes | PASS: latest entry before this verdict was `REVISED: bridge/gtkb-wi3326-project-rehome-executable-packet-repair-005.md`; no drift was reported. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Read-only `project_work_item_memberships` query | yes | PASS: old startup relation is non-active history and deterministic-services relation is active. |
| `GOV-STANDING-BACKLOG-001` | `gt backlog show WI-3326 --json` and `gt backlog show WI-4266 --json` | yes | PASS: WI-3326 remains open and first-class project membership is authoritative; WI-4266 remains open for later governed disposition. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Full bridge thread and corrected report review | yes | PASS: stale evidence was corrected through a durable bridge version rather than deletion or chat-only correction. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Owner-decision readback, PAUTH readback, preflights, and bridge-thread review | yes | PASS: owner decision, authorization, implementation report, and verification evidence are all preserved. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Command/path review | yes | PASS: all inspected artifacts and commands remained under `E:\GT-KB`. |

## Positive Confirmations

- The authorization packet records `latest_status: "GO"`,
  `requirement_sufficiency: "sufficient"`, PAUTH
  `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-WI-3326-REHOME`, and
  `target_path_globs: ["groundtruth.db"]`.
- Current relation history for WI-3326 is append-only:
  - row 689: startup membership, version 1, `active`;
  - row 1024: startup membership, version 2, `removed`, changed by
    `gt-projects` at `2026-06-07T09:21:04+00:00`;
  - row 1025: deterministic-services membership, version 1, `active`, changed
    by `gt-projects` at `2026-06-07T09:21:19+00:00`.
- `gt projects show PROJECT-GTKB-STARTUP-ENHANCEMENTS --json` returns no
  WI-3326 active membership matches.
- `gt projects show PROJECT-GTKB-DETERMINISTIC-SERVICES-001 --json` returns
  active membership
  `PWM-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-WI-3326`.
- `gt backlog show WI-3326 --json` still shows WI-3326 open with
  `project_name: null`; the corrected report explicitly treats the first-class
  membership relation as authoritative.
- `gt backlog show WI-4266 --json` remains open with the expected acceptance
  summary. This verdict does not close WI-4266.

## Advisory Note

The implementation report records that the initial literal command was blocked
by the implementation-start hook and that an equivalent PowerShell
expression-form command later reached the `gt projects remove-item` CLI. This
is not a blocker for this verdict because the authorized target was
`groundtruth.db`, the PAUTH scope was membership-only, and live relation rows
match the approved operation. If that hook-target parsing behavior remains
reproducible, it should be tracked as a separate bridge item scoped to the
implementation-start gate and its tests; it should not be bundled into this
already-completed WI-3326 membership move.

## Commands Executed

```text
Get-Content -Raw .codex\skills\bridge\SKILL.md
Get-Content -Raw .codex\skills\verify\SKILL.md
python .claude\skills\bridge\helpers\scan_bridge.py --role loyal-opposition --format json
python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-wi3326-project-rehome-executable-packet-repair --format json --preview-lines 60
Get-Content -Raw bridge\gtkb-wi3326-project-rehome-executable-packet-repair-001.md
Get-Content -Raw bridge\gtkb-wi3326-project-rehome-executable-packet-repair-002.md
Get-Content -Raw bridge\gtkb-wi3326-project-rehome-executable-packet-repair-003.md
Get-Content -Raw bridge\gtkb-wi3326-project-rehome-executable-packet-repair-004.md
Get-Content -Raw bridge\gtkb-wi3326-project-rehome-executable-packet-repair-005.md
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi3326-project-rehome-executable-packet-repair
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi3326-project-rehome-executable-packet-repair
Get-Content -Raw .gtkb-state\implementation-authorizations\by-bridge\gtkb-wi3326-project-rehome-executable-packet-repair.json
python -c "<read-only SQLite query of project_work_item_memberships for WI-3326>"
python -c "<gt projects show and gt backlog show readback script>"
.\groundtruth-kb\.venv\Scripts\gt.exe deliberations search "WI-3326 re-home deterministic services DELIB-20260624 retired startup project membership" --limit 8 --json
.\groundtruth-kb\.venv\Scripts\gt.exe deliberations get DELIB-20260624
```

Observed highlights:

```text
preflight_passed: true
missing_required_specs: []
missing_advisory_specs: []
Blocking gaps (gate-failing): 0
latest_startup_status_removed: true
latest_deterministic_status_active: true
PROJECT-GTKB-STARTUP-ENHANCEMENTS WI-3326 matches: []
PROJECT-GTKB-DETERMINISTIC-SERVICES-001 WI-3326 membership_status: active
WI-4266 resolution_status: open
```

## Owner Action Required

None.

File bridge scan contribution: 1 corrected implementation report verified.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
