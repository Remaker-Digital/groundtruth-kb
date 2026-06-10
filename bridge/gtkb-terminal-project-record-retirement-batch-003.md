REVISED
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: codex-pb-terminal-project-retirement-requirement-sufficiency-20260601
author_model: GPT-5
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop Prime Builder session

# Terminal Project Record Retirement Batch - Governance Review Proposal Revision

bridge_kind: governance_advisory
Document: gtkb-terminal-project-record-retirement-batch
Version: 003
Author: Prime Builder (Codex, harness A)
Date: 2026-06-01 UTC
target_paths: ["groundtruth.db", "bridge/gtkb-terminal-project-record-retirement-batch-*.md", "bridge/INDEX.md", ".gtkb-state/execute_terminal_project_retirement_batch.py", "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-01-14-54-PROJECT-LIFECYCLE-DRY-RUN.md"]
Recommended commit type: chore:

## Summary

Retire nine active MemBase project records whose live first-class project
memberships contain only terminal work items and whose live authorization
surface contains no active project authorizations.

This proposal is `bridge_kind: governance_review` because it requests a bounded
governance lifecycle correction to MemBase project records, not new
implementation work. The bulk mutation remains behind Loyal Opposition GO. This
proposal does not request source-code behavior changes.

## Revision Context

Version 003 preserves the nine-project retirement scope and target paths from
version 001. This revision exists because the implementation-start gate rejected
the GO'd proposal after review: the section `## Requirement Sufficiency` used
the plain-English phrase "Existing requirements are sufficient" while
`scripts/implementation_authorization.py` requires the exact operative state
`Existing requirements sufficient`. No project, path, or mutation scope is
expanded by this revision.

## Proposed Mutation Scope

After GO, Prime Builder will execute the retire batch through a repo-local
wrapper at `.gtkb-state/execute_terminal_project_retirement_batch.py`. The
wrapper will print exact command surfaces in dry-run mode and execute only under
`--apply`.

Proposed retire order:

1. `PROJECT-GTKB-BRIDGE-WORK-FRONT-DRAIN-001-WAVE-1-DRAINABLE`
2. `PROJECT-GTKB-BRIDGE-WORK-FRONT-DRAIN-001-WAVE-2-CARRY-OVER-NO-GO-TRIAGE`
3. `PROJECT-GTKB-BRIDGE-WORK-FRONT-DRAIN-001`
4. `PROJECT-GTKB-DORA-001B-TRACK-1`
5. `PROJECT-GTKB-DORA-001B`
6. `PROJECT-GTKB-ISOLATION-016`
7. `PROJECT-GTKB-GOV-PROPOSAL-STANDARDS-SLICE-1`
8. `PROJECT-GTKB-DETERMINISTIC-SERVICES-001-ARTIFACT-RECORDING`
9. `PROJECT-GTKB-GOV-CODE-QUALITY-BASELINE`

Each mutation will use the governed CLI surface:

```powershell
& "E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe" -m groundtruth_kb --config "E:\GT-KB\groundtruth.toml" projects retire <PROJECT_ID> --changed-by "prime-builder/codex/A" --change-reason "<batch-specific reason>"
```

The common change reason will cite this bridge thread and the dry-run inventory:

```text
Retire active project record after live first-class membership inspection found zero non-terminal work items and zero active project authorizations. Scope approved by bridge/gtkb-terminal-project-record-retirement-batch-001.md. Dry-run inventory: independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-01-14-54-PROJECT-LIFECYCLE-DRY-RUN.md.
```

## Excluded From This Batch

`PROJECT-GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT` is intentionally excluded
from this first retire batch. The dry-run inventory found terminal status counts
for the compatibility row, but the workstream is security-sensitive and the live
work-item status detail still says it is not terminal until containment/history
actions are verified or explicitly retired. That project should receive a
separate focused review before any retirement mutation.

The following records also remain active because they still have non-terminal
work item memberships or known membership discrepancies:

- `PROJECT-GTKB-DETERMINISTIC-SERVICES-001-BRIDGE-MECHANICS`
- `PROJECT-ANTIGRAVITY-INTEGRATION`
- `PROJECT-GTKB-DETERMINISTIC-SERVICES-001-PROJECT-LIFECYCLE`
- `PROJECT-GTKB-DASHBOARD-002-SLICE-2-3-INTEGRATION`
- `PROJECT-GTKB-DASHBOARD-002-SLICE-2-2-METRICS`
- `PROJECT-GTKB-GOV-PROPOSAL-STANDARDS`
- `PROJECT-GTKB-DETERMINISTIC-SERVICES-001-VERIFICATION-MECHANICS`
- `PROJECT-GTKB-DETERMINISTIC-SERVICES-001-DISCOVERABILITY`
- `PROJECT-GTKB-GOV-DA-ENFORCEMENT`
- `PROJECT-GTKB-DETERMINISTIC-SERVICES-001`

## Evidence

Primary dry-run inventory:

- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-01-14-54-PROJECT-LIFECYCLE-DRY-RUN.md`

The inventory compared live first-class project memberships against
compatibility-field summaries and found the nine in-scope records had only
terminal associated work items and no active project authorizations.

Additional live read-only DB probe on 2026-06-01 confirmed:

| Project record | Live status | Non-terminal member count | Active PAUTH count |
|---|---:|---:|---:|
| `PROJECT-GTKB-BRIDGE-WORK-FRONT-DRAIN-001-WAVE-1-DRAINABLE` | `active` | 0 | 0 |
| `PROJECT-GTKB-BRIDGE-WORK-FRONT-DRAIN-001-WAVE-2-CARRY-OVER-NO-GO-TRIAGE` | `active` | 0 | 0 |
| `PROJECT-GTKB-BRIDGE-WORK-FRONT-DRAIN-001` | `active` | 0 | 0 |
| `PROJECT-GTKB-DORA-001B-TRACK-1` | `active` | 0 | 0 |
| `PROJECT-GTKB-DORA-001B` | `active` | 0 | 0 |
| `PROJECT-GTKB-ISOLATION-016` | `active` | 0 | 0 |
| `PROJECT-GTKB-GOV-PROPOSAL-STANDARDS-SLICE-1` | `active` | 0 | 0 |
| `PROJECT-GTKB-DETERMINISTIC-SERVICES-001-ARTIFACT-RECORDING` | `active` | 0 | 0 |
| `PROJECT-GTKB-GOV-CODE-QUALITY-BASELINE` | `active` | 0 | 0 |

## Specification Links

Blocking specs:

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge `INDEX.md` remains the canonical
  queue surface; this proposal adds a new bridge thread and later a
  post-implementation report.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this section
  enumerates the governing specification and target-path surface. The
  project-linkage triad is not used because this is a `governance_review`
  lifecycle correction, not project-scoped implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan
  below maps every relevant requirement to a deterministic probe.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths are inside
  `E:\GT-KB`.

Governance and lifecycle specs:

- `GOV-STANDING-BACKLOG-001` - MemBase remains the backlog/project source of
  truth; project lifecycle rows should reflect terminal workstreams.
- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` - project retirement is the
  correct terminal lifecycle state when associated work is complete and no new
  work is expected.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - project lifecycle state is a durable
  artifact and should be reconciled through governed records.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - preserves the cleanup decision in a
  durable bridge artifact before mutation.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - terminal project records trigger
  lifecycle-state reconciliation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the
  `governance_review` classification is the metadata exemption for this
  governance lifecycle correction.

## Prior Deliberations

- `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM` - owner decision
  establishing bridge verification as lifecycle-close evidence for parent
  backlog/project surfaces.
- Project lifecycle dry-run inventory on 2026-06-01 captured the safe candidate
  set and explicitly recommended a bridge proposal before any multi-project
  retire batch.

## Requirement Sufficiency

Existing requirements sufficient. This scoped governance correction does not
introduce a new lifecycle rule; it applies the existing rule that active project
records should not remain active after their associated work is terminal and no
active authorization remains.

## Specification-Derived Verification Plan

| Requirement | Verification command or probe | Expected result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Re-read `bridge/INDEX.md` before apply and after filing the post-implementation report. | Latest status transitions are recorded in the canonical bridge index. |
| `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` | Query `current_projects` for the nine project IDs after apply. | Each latest project row has `status='retired'` and non-null `completed_at`. |
| `GOV-STANDING-BACKLOG-001` | Query active project authorizations and current project work-item memberships for the nine IDs. | No in-scope project has active PAUTHs or non-terminal active member work items. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Query excluded/keep-active project IDs after apply. | Excluded and keep-active records remain active. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Inspect wrapper target paths and execution log location. | All mutation and evidence artifacts remain under `E:\GT-KB`. |

Post-implementation evidence will include:

```powershell
& "E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe" .gtkb-state\execute_terminal_project_retirement_batch.py --dry-run
& "E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe" .gtkb-state\execute_terminal_project_retirement_batch.py --apply
& "E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe" .gtkb-state\execute_terminal_project_retirement_batch.py --verify
```

## Risk / Impact

Positive impact: removes nine stale active project records from project
dashboards and startup rollups, making active-project state easier to trust.

Main risk: bulk lifecycle mutation could accidentally retire a still-relevant
record. Mitigation: scope is limited to records with zero non-terminal active
member work items and zero active authorizations; security-sensitive and
membership-discrepant records are explicitly excluded.

## Decision Needed From Loyal Opposition

GO authorizes Prime Builder to create the batch wrapper, run dry-run/apply/verify
for the nine in-scope project records, and file a post-implementation report.

NO-GO should identify any project that must be removed from the batch, any
missing verification probe, or any additional governance record required before
the lifecycle mutation.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
