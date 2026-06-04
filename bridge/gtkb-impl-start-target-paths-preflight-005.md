GO

# Loyal Opposition Review - Implementation-Start Target-Paths Preflight

bridge_kind: loyal_opposition_verdict
Document: gtkb-impl-start-target-paths-preflight
Version: 005
Author: Loyal Opposition (Codex, harness A)
Automation: keep-working-lo
Date: 2026-06-04 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-impl-start-target-paths-preflight-004.md
Verdict: GO
Work Item: WI-3380

## Verdict

GO. The revised proposal resolves the corrective NO-GO at
`bridge/gtkb-impl-start-target-paths-preflight-003.md`.

The original proposal was not eligible for the reliability fast lane because
`WI-3380` is an improvement-origin item and the scope creates a new
operator-invoked script surface. The revision removes that authorization theory
and routes the work through `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` plus
active project PAUTH
`PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BATCH`,
which permits `cli_extension`, `hook_upgrade`, `source`, and `test_addition`.

Implementation is approved only for:

- `scripts/impl_start_target_paths_preflight.py`
- `groundtruth-kb/tests/test_impl_start_target_paths_preflight.py`
- `.claude/hooks/bridge-compliance-gate.py`

## Prior Deliberations

Deliberation searches executed:

```text
groundtruth-kb\.venv\Scripts\gt.exe deliberations search "WI-3380 target paths preflight bridge protocol reliability PAUTH" --limit 10 --json
```

Relevant context:

- `DELIB-20260638` is cited by the proposal for the Phase 0 bridge reliability
  work order naming `WI-3380`.
- `DELIB-S367-PAUTH-BRIDGE-PROTOCOL-RELIABILITY-AMENDMENT-WORK-INTENT` is the
  owner-decision record on the cited active PAUTH.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` remains relevant only as a
  negative boundary: this revised proposal no longer relies on that fast lane.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` supports deterministic preflight
  services replacing repeated manual target-path comparison.

No searched deliberation contradicted the revised authorization path.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-impl-start-target-paths-preflight
```

Observed result:

```text
## Applicability Preflight

- packet_hash: `sha256:d5f143d5b46c787837d64643ba7692684ea7815fcc22ccefaf1157a5160c451b`
- bridge_document_name: `gtkb-impl-start-target-paths-preflight`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-impl-start-target-paths-preflight-004.md`
- operative_file: `bridge/gtkb-impl-start-target-paths-preflight-004.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-impl-start-target-paths-preflight
```

Observed result:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-impl-start-target-paths-preflight`
- Operative file: `bridge\gtkb-impl-start-target-paths-preflight-004.md`
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

## Authorization Evidence

Read-only MemBase and source checks confirmed:

- `WI-3380` is `origin=improvement`, priority `P1`, `resolution_status=open`,
  and `stage=backlogged`.
- `WI-3380` has active membership in
  `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` via
  `PWM-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-3380`.
- The cited PAUTH is active, unexpired, and permits `hook_upgrade`,
  `cli_extension`, `test_addition`, `source`, `rules`, and
  `governance_evidence`.
- `scripts/implementation_authorization.py::validate_project_authorization_row`
  accepts a work item when it is either explicitly included in the PAUTH or an
  active member of the PAUTH's project. That makes active project membership
  sufficient for this proposal even though the PAUTH's explicit
  `included_work_item_ids` list does not name `WI-3380`.

## Positive Confirmations

- The revised proposal removes the rejected fast-lane claim.
- The target path set remains the same three files reviewed in the original
  proposal.
- The new operator-invoked script surface is now covered by a PAUTH whose
  allowed mutation classes include `cli_extension`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` is now cited, closing the previous
  advisory preflight gap.
- The implementation plan keeps the hook integration advisory-only and requires
  regression coverage that the existing block/pass behavior is not widened.

## Implementation Constraints

Prime Builder must:

1. Run `python scripts/implementation_authorization.py begin --bridge-id gtkb-impl-start-target-paths-preflight` before editing the approved files.
2. Keep the new script read-only.
3. Keep `.claude/hooks/bridge-compliance-gate.py` integration advisory-only.
4. Include in the post-implementation report the targeted pytest, ruff check,
   ruff format check, preflight smoke, and implementation-authorization packet
   smoke evidence named in the revised proposal.

## Commands Executed

```text
python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-impl-start-target-paths-preflight --format json --preview-lines 80
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-impl-start-target-paths-preflight
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-impl-start-target-paths-preflight
groundtruth-kb\.venv\Scripts\gt.exe backlog show WI-3380 --json
groundtruth-kb\.venv\Scripts\gt.exe deliberations search "WI-3380 target paths preflight bridge protocol reliability PAUTH" --limit 10 --json
groundtruth-kb\.venv\Scripts\gt.exe projects show PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY --json
groundtruth-kb\.venv\Scripts\gt.exe projects authorizations PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY --json
SQLite read of current_project_work_item_memberships/current_project_authorizations for WI-3380 and the cited PAUTH
Source read of scripts\implementation_authorization.py validate_project_authorization_row
```

File bridge scan contribution: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
