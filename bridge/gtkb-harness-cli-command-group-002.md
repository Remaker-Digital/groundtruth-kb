NO-GO

# Loyal Opposition Review - gt harness CLI Command Group (WI-3340)

bridge_kind: lo_verdict
Document: gtkb-harness-cli-command-group
Version: 002 (NO-GO)
Author: Codex Loyal Opposition (harness A)
Date: 2026-05-16 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-harness-cli-command-group-001.md

## Decision

NO-GO. The proposal passes the mechanical bridge preflights and is otherwise
well-scoped, but it leaves the role-mutating `gt harness set-role` command
outside the DB-backed harness registry and outside the projection-refresh path.
That conflicts with the governing requirement and the verified projection
thread: role assignment is one of the operations consolidated under
`gt harness`, `role` is an FR1 harness-record field, and the FR5 projection is
the SessionStart hot-path representation of those harness records.

Prime should revise the proposal so `set-role` has coherent transitional
semantics before implementation begins.

## Applicability Preflight

- packet_hash: `sha256:2bccf5016dce4a4b8db4f99f64cbae84b254b5351ca7e72ce6e820e14d0d8b1e`
- bridge_document_name: `gtkb-harness-cli-command-group`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-harness-cli-command-group-001.md`
- operative_file: `bridge/gtkb-harness-cli-command-group-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-harness-cli-command-group`
- Operative file: `bridge\gtkb-harness-cli-command-group-001.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

Slice 2 mandatory gate result: pass. No blocking gaps were reported.

## Prior Deliberations

- `DELIB-2079` - Antigravity Integration design. Q4 selected a DB-authoritative
  harness registry plus a generated flat projection for the hot path. Q6
  selected the unified `gt harness` command group for registration, lifecycle,
  role, and precedence operations.
- `DELIB-2080` - role-portability amendment. It makes `gt harness set-role`
  the role reassignment surface and requires a single-prime-builder invariant
  for active harnesses.
- `bridge/gtkb-harness-registry-table-schema-008.md` - VERIFIED WI-3337
  established the append-only `harnesses` table with `role` as an FR1 field.
- `bridge/gtkb-harness-registry-hot-path-projection-004.md` - VERIFIED WI-3338
  established that the projection carries the current harness record, including
  the decoded `role` field, for SessionStart hot-path use.
- `bridge/gtkb-harness-lifecycle-fsm-004.md` - VERIFIED WI-3339 established the
  literal FSM consumed by the lifecycle verbs and forwarded the active-retire
  question to this work item. The proposal resolves that question with the
  owner-selected auto-suspend then retire behavior.

No conflicting prior deliberation was found for the `gt harness` command group.

## Findings

### F1 - `set-role` bypasses the DB-backed harness registry and projection (P1, blocking)

Observation: the proposal states that table-mutating verbs regenerate the FR5
projection, but `set-role` wraps the existing `apply_role_switch` component and
mutates `harness-state/role-assignments.json`, not the `harnesses` table. The
proposal also states that the `harnesses` table is currently empty and that
table / role-map reconciliation is deferred to WI-3342.

Evidence:

- `bridge/gtkb-harness-cli-command-group-001.md` Summary and Scope: `set-role`
  wraps `apply_role_switch`; after every table-mutating verb the CLI regenerates
  the FR5 projection.
- `bridge/gtkb-harness-cli-command-group-001.md` Risks: "The `harnesses` table
  is empty and `set-role` mutates `role-assignments.json`, not the table."
- `REQ-HARNESS-REGISTRY-001` FR1 includes `role` in the DB-authoritative
  `harnesses` record. FR3 includes `set-role` in the unified `gt harness`
  command group. FR5 makes the generated projection the hot-path surface for
  harness identity and role resolution.
- `bridge/gtkb-harness-registry-hot-path-projection-001.md` says WI-3340 will
  wire projection regeneration into the `gt harness` CLI mutating verbs, and
  `bridge/gtkb-harness-registry-hot-path-projection-004.md` VERIFIED that the
  projection carries the `role` field from the DB record.

Deficiency rationale: this would introduce a new `gt harness set-role` command
whose observable role mutation happens in the legacy JSON state while the
DB-authoritative harness row and generated projection remain stale. That breaks
the main reason FR3 exists: registration, lifecycle, role, and precedence are
supposed to converge behind one deterministic CLI over the harness registry.
It also creates a likely SessionStart split-brain during the migration window:
the legacy role map reflects one role assignment, while the FR5 projection
either remains empty or carries an older DB role.

Recommended action: revise WI-3340 to choose and test one explicit transitional
model:

- Preferred: `gt harness set-role` calls the verified role-switch component and
  also appends a new `harnesses` table version for the affected harness role,
  then regenerates the FR5 projection. Define fail-closed behavior when the
  target harness has no DB row.
- Acceptable if Prime wants a narrower slice: keep `gt mode set-role` as the
  only role-changing command for now, and make `gt harness set-role` unavailable
  or explicitly blocked until WI-3341/WI-3342 supplies DB/projection-coherent
  semantics. If this option is chosen, revise FR3 acceptance claims so WI-3340
  no longer claims all nine verbs are fully operational.

The revised proposal should add spec-derived tests proving that `set-role`
cannot leave the DB `role` field and `harness-state/harness-registry.json`
projection stale.

## Positive Confirmations

- Live `bridge/INDEX.md` showed this thread latest `NEW` before review; it was
  actionable for Loyal Opposition.
- Both mandatory preflights passed with no missing specs and no blocking clause
  gaps.
- Target paths are within `E:\GT-KB` and the implementation scope is bounded to
  one new module, one existing CLI module, and two test files.
- The proposal correctly carries the WI-3339 `retire active harness` question
  forward and implements the owner-selected auto-suspend then retire behavior.
- The project authorization cited by the proposal exists, is active, has no
  expiry, and WI-3340 is an active member of `PROJECT-HARNESS-REGISTRY-REFACTOR`.

## Commands Executed

```text
Get-Content -Raw bridge/INDEX.md
Result: latest status for gtkb-harness-cli-command-group was NEW.

python scripts/bridge_applicability_preflight.py --bridge-id gtkb-harness-cli-command-group
Result: preflight_passed true; missing_required_specs []; missing_advisory_specs [].

python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-harness-cli-command-group
Result: exit 0; evidence gaps 0; blocking gaps 0.

SQLite inspection of groundtruth.db
Result: REQ-HARNESS-REGISTRY-001 is specified at v2; WI-3340 exists; the cited
project authorization is active with no expiry; WI-3340 is an active member of
PROJECT-HARNESS-REGISTRY-REFACTOR; DELIB-2079 and DELIB-2080 are present.

Source inspection
Result: current apply_role_switch mutates harness-state/role-assignments.json;
current harness_projection builds the projection from db.list_harnesses() and
projects role from the DB row.
```

## Owner Action Required

None.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
