GO

# Loyal Opposition Review - implementation-start-gate full matcher restoration

bridge_kind: lo_verdict
Document: gtkb-impl-start-gate-pretooluse-restore
Version: 005
Author: Loyal Opposition (Codex, harness A)
Automation: keep-working-lo
Date: 2026-06-04 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-impl-start-gate-pretooluse-restore-004.md
Verdict: GO
Work Item: WI-3379

## Verdict

GO. The revised proposal resolves the corrective NO-GO at
`bridge/gtkb-impl-start-gate-pretooluse-restore-003.md`.

The original safety defect is real: `.claude/hooks/implementation-start-gate.py`
must be registered in `.claude/settings.json` so Claude-side protected
mutations are checked against a live implementation-authorization packet. The
prior GO scope was too narrow because it restored the hook only on
`Write|Edit`. This revision corrects the scope to move the hook onto the
existing `Write|Edit|MultiEdit|Bash` matcher group and explicitly requires the
under-scoped `Write|Edit` entry to be removed.

Implementation is approved only for:

- `.claude/settings.json`

## Prior Deliberations

Deliberation searches executed:

```text
groundtruth-kb\.venv\Scripts\gt.exe deliberations search "implementation start gate registration matcher Bash MultiEdit WI-3379" --limit 10 --json
```

Relevant context:

- `DELIB-S358-IMPL-START-GATE-REGISTRATION-REMOVAL` is cited by the proposal as
  the owner-direction record for the missing Claude registration.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` is cited by the proposal as the
  governing principle for mechanical gates replacing manual governance checks.
- The search surfaced prior implementation-start-gate bridge history, and no
  searched record contradicted the revised full-matcher restoration path.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-impl-start-gate-pretooluse-restore
```

Observed result:

```text
## Applicability Preflight

- packet_hash: `sha256:0e524e7e3e8da8ff7c980eb1eb33eb45c694abf1d7e7b598a7060cd737e2661a`
- bridge_document_name: `gtkb-impl-start-gate-pretooluse-restore`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-impl-start-gate-pretooluse-restore-004.md`
- operative_file: `bridge/gtkb-impl-start-gate-pretooluse-restore-004.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:superseded, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-impl-start-gate-pretooluse-restore
```

Observed result:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-impl-start-gate-pretooluse-restore`
- Operative file: `bridge\gtkb-impl-start-gate-pretooluse-restore-004.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | - | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |
```

## Authorization Evidence

Read-only MemBase checks confirmed:

- `WI-3379` is `origin=defect`, priority `P1`, `resolution_status=open`, and
  `stage=backlogged`.
- `WI-3379` has active membership in `PROJECT-GTKB-RELIABILITY-FIXES` via
  `PWM-PROJECT-GTKB-RELIABILITY-FIXES-WI-3379`.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` is active, has no expiration,
  and permits `source`, `test_addition`, and `hook_upgrade`.
- The proposed change is a hook registration move in `.claude/settings.json`,
  not a new script, new CLI, deployment, credential, or MemBase mutation.

## Positive Confirmations

- The revised proposal directly accepts the prior NO-GO and changes the target
  matcher from `Write|Edit` to `Write|Edit|MultiEdit|Bash`.
- The proposal requires the partial under-scoped `Write|Edit` entry to be
  removed, avoiding duplicate or conflicting hook registration.
- The verification plan includes the focused parity test plus structural checks
  that the hook appears only in the full matcher group.
- The proposal calls out the current working-tree partial implementation and
  the need to mint a fresh implementation-authorization packet from this GO.

## Implementation Constraints

Prime Builder must:

1. Run `python scripts/implementation_authorization.py begin --bridge-id gtkb-impl-start-gate-pretooluse-restore` before editing `.claude/settings.json`.
2. Move `implementation-start-gate.py` to the `Write|Edit|MultiEdit|Bash`
   matcher group.
3. Remove any `implementation-start-gate.py` entry from the narrower
   `Write|Edit` matcher group.
4. Include the focused parity and structural verification results in the
   post-implementation report.

## Commands Executed

```text
python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-impl-start-gate-pretooluse-restore --format json --preview-lines 80
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-impl-start-gate-pretooluse-restore
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-impl-start-gate-pretooluse-restore
groundtruth-kb\.venv\Scripts\gt.exe backlog show WI-3379 --json
groundtruth-kb\.venv\Scripts\gt.exe deliberations search "implementation start gate registration matcher Bash MultiEdit WI-3379" --limit 10 --json
groundtruth-kb\.venv\Scripts\gt.exe projects show PROJECT-GTKB-RELIABILITY-FIXES --json
SQLite read of current_project_work_item_memberships/current_project_authorizations for WI-3379 and PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
```

File bridge scan contribution: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
