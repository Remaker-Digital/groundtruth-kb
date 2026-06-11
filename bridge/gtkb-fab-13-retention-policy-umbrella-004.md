NO-GO

bridge_kind: loyal_opposition_review
Document: gtkb-fab-13-retention-policy-umbrella
Version: 004
Author: loyal-opposition (Codex, harness A)
Date: 2026-06-11 UTC
Responds-To: bridge/gtkb-fab-13-retention-policy-umbrella-003.md

# Loyal Opposition Review - FAB-13 Retention-Policy Umbrella

## Review Scope

Reviewed the full bridge thread for WI-4425 / PROJECT-FABLE-INVESTIGATION:

- `bridge/gtkb-fab-13-retention-policy-umbrella-001.md`
- `bridge/gtkb-fab-13-retention-policy-umbrella-002.md`
- `bridge/gtkb-fab-13-retention-policy-umbrella-003.md`

This review checked the prior NO-GO finding, live `bridge/INDEX.md` state,
mandatory bridge preflights, owner/project authority, backlog state, live
duplicate-file evidence, implementation target-path authorization semantics,
and the Loyal Opposition opportunity radar.

## Same-Session Guard

This Loyal Opposition session did not author the proposal under review. The
operative revision was authored by Prime Builder, harness B, session
`9660f4cb-1b84-410e-a024-febdabe7c541`.

## Applicability Preflight

Command:

```powershell
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-fab-13-retention-policy-umbrella
```

Observed output:

```text
## Applicability Preflight

- packet_hash: `sha256:35238089bb62e0318a18f6943c6c94c7e6528636d28d2d10d654cbf5d35e17b1`
- bridge_document_name: `gtkb-fab-13-retention-policy-umbrella`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-fab-13-retention-policy-umbrella-003.md`
- operative_file: `bridge/gtkb-fab-13-retention-policy-umbrella-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: ["memory/archive/**"]
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
warning: bridge preflight missing parent directories: memory/archive/**
```

The missing parent directory warning is consistent with the proposal creating
dated archive sidecars under `memory/archive/**`; it is not the blocker below.

## Clause Applicability

Command:

```powershell
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-fab-13-retention-policy-umbrella
```

Observed output:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-fab-13-retention-policy-umbrella`
- Operative file: `bridge\gtkb-fab-13-retention-policy-umbrella-003.md`
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

- `DELIB-FAB13-REMEDIATION-20260610`: owner decision batch for decision-ledger
  rotation, dispatch runtime-evidence retention, Drive duplicate purge, and
  `.driveignore` coverage. `gt deliberations get` reports outcome
  `owner_decision`, work item `WI-4425`, session `S430`.
- `DELIB-FABLE-GRILL-20260610-Q1..Q7`: project-chartering decisions cited by
  the proposal and backlog item.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`: relevant to the retention and
  garbage-collection routines.

## Authority Check

- `gt projects authorizations PROJECT-FABLE-INVESTIGATION --json` confirms
  `PAUTH-FAB13-20260610` is active, includes `WI-4425`, and allows source
  edits to hooks/triggers, additive governance config, owner-approved runtime
  evidence pruning, DA harvest of resolved decisions, Drive/gitignore coverage
  extension, and tests.
- The same authorization forbids push/deploy, owner Drive-sync infrastructure
  mutation, hard deletion of canonical specification or DA records, and
  external Agent Red repository mutation.
- `gt backlog list --json --id WI-4425` confirms the work item exists, remains
  open/backlogged, and is titled `FAB-13 Retention policy umbrella for runtime
  stores`.

## Blocking Finding

### F1 - Root SQLite conflict-copy sidecars are still outside target_paths

`bridge/gtkb-fab-13-retention-policy-umbrella-003.md` resolves most of the
prior deletion-perimeter gap by adding `.gtkb-state/**`, `.codex/gtkb-hooks/**`,
and `.claude/hooks/*.json` to `target_paths`. It still claims the repo-root
SQLite sidecar duplicates are covered because they are "siblings of
`groundtruth.db`, already in `target_paths`."

That claim does not match the implementation authorization matcher. The live
root contains duplicate SQLite sidecars such as:

```text
groundtruth (1).db-shm
groundtruth (1).db-wal
groundtruth (2).db-shm
groundtruth (2).db-wal
groundtruth (3).db-shm
groundtruth (4).db-shm
groundtruth (5).db-shm
groundtruth (6).db-shm
groundtruth (7).db-shm
groundtruth (8).db-shm
```

But `target_paths` only includes `groundtruth.db`, not a glob that matches
`groundtruth (N).db-shm`, `groundtruth (N).db-wal`, `groundtruth.db-shm`, or
`groundtruth.db-wal`.

Target-path authorization evidence:

```powershell
@'
from scripts.implementation_authorization import path_authorized
patterns = [
    "groundtruth.db",
    ".claude/hooks/owner-decision-tracker.py",
    ".claude/hooks/*.json",
    "memory/pending-owner-decisions.md",
    "memory/archive/**",
    "scripts/cross_harness_bridge_trigger.py",
    "groundtruth-kb/src/groundtruth_kb/session/envelope.py",
    "config/governance/runtime-evidence-retention.toml",
    ".gtkb-state/**",
    ".codex/gtkb-hooks/**",
    ".driveignore",
    ".gitignore",
    "platform_tests/scripts/**",
]
packet = {"target_path_globs": patterns}
for p in ["groundtruth.db", "groundtruth (1).db-wal", "groundtruth (1).db-shm", "groundtruth.db-wal", "groundtruth.db-shm"]:
    print(p, path_authorized(packet, p))
'@ | python -
```

Observed output:

```text
groundtruth.db True
groundtruth (1).db-wal False
groundtruth (1).db-shm False
groundtruth.db-wal False
groundtruth.db-shm False
```

Impact: Prime Builder would either be blocked by the implementation-start
target-path gate when trying to remove the root SQLite duplicates, or would
need to omit part of the owner-approved duplicate purge. The proposal is still
not precise enough for Loyal Opposition to verify the destructive-cleanup
perimeter.

## Required Revision

Submit a REVISED proposal that adds concrete target-path coverage for the root
SQLite duplicate/sidecar cleanup, for example a bounded set of globs or
concrete paths that match the intended `groundtruth (N).db-*` family and any
live `groundtruth.db-shm` / `groundtruth.db-wal` sidecars if those are part of
the cleanup. Alternatively, explicitly defer root SQLite sidecar cleanup out of
FAB-13 and keep the deletion perimeter to the already-scoped `.gtkb-state/**`,
`.codex/gtkb-hooks/**`, and `.claude/hooks/*.json` surfaces.

The revision should preserve the DA-harvest-before-archive invariant, the
dispatch evidence retention windows in `DELIB-FAB13-REMEDIATION-20260610`, and
the rule that full Drive-unsync remains an owner infrastructure recommendation
only.

## Opportunity Radar

- Defect pass: the root SQLite sidecar deletion perimeter remains outside the
  effective target-path matcher.
- Token-savings pass: no new separate advisory; FAB-13 already targets
  repeated context cost from unbounded runtime evidence.
- Deterministic-service pass: the target-path mismatch is a candidate for
  draft-linter / implementation-start preflight enhancement: when a proposal
  claims duplicate-file purging, enumerate matching live duplicate families and
  require target-path coverage or explicit deferral.
- Surface eligibility: draft-linter or target-path preflight; residual human
  judgement is classifying which duplicate families are canonical, regenerable,
  or out of scope.
- Routing: no new advisory filed in this verdict because this fits the existing
  lint/preflight improvement lane already active in the FABLE campaign.

## Verdict

NO-GO until root SQLite duplicate sidecar cleanup is either included in
`target_paths` with matcher-valid patterns or explicitly deferred.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
