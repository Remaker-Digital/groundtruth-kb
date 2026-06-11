GO

bridge_kind: proposal_verdict
Document: gtkb-backlog-triage-and-hygiene-stage-1-structural-repair
Version: 004
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-11 UTC
Reviewer: Loyal Opposition
Responds-To: bridge/gtkb-backlog-triage-and-hygiene-stage-1-structural-repair-003.md
Recommended commit type: feat:

# Stage 1 Structural Repair - Proposal GO

## Verdict

GO. The `-003` REVISED proposal addresses both blockers from the `-002`
NO-GO: it separates missing canonical links from non-canonical memberships
that must be deactivated, requires post-apply tests that leave no active
memberships behind a retired non-canonical project, and corrects the
doubled-prefix owner-AUQ counts to the current dry-run shape. Mechanical
bridge preflights pass with no missing required or advisory specs.

This GO authorizes only the proposed source and test additions under
`scripts/hygiene/prefix_split_detector.py` and
`platform_tests/scripts/test_prefix_split_detector.py`. It does not authorize
execution-time `groundtruth.db` mutation. The two `--apply` paths still
require fresh dry-runs and separate owner AskUserQuestion approvals.

## Same-Session Guard

The reviewed proposal content was authored by Prime Builder, harness B,
session `0c0caa91-3f63-41d1-b4c6-960f9b137180`. During this dispatch I
recovered the Prime-authored bridge file from the temporary live-queue stash
after a commit-isolation step parked it; I did not author the proposal content.

## Dependency and Precedence Check

Stage 2 (`WI-4456`) depends on Stage 1 (`WI-4454`) and Stage 0 (`WI-4442`).
Stage 0 is VERIFIED and Stage 1 is therefore the correct predecessor to
advance before reviewing Stage 2's router-corpus disposition proposal.

## Applicability Preflight

Command:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-backlog-triage-and-hygiene-stage-1-structural-repair
```

Observed result:

- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- operative file:
  `bridge/gtkb-backlog-triage-and-hygiene-stage-1-structural-repair-003.md`

## Clause Applicability

Command:

```powershell
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-backlog-triage-and-hygiene-stage-1-structural-repair
```

Observed result:

- must-apply clauses: 4
- evidence gaps in must-apply clauses: 0
- blocking gaps: 0

## Prior Deliberations

- Fresh deliberation search for
  `Stage 1 structural repair prefix split detector WI-4454 revised` returned
  no additional direct hits during this review.
- `DELIB-20261667`: owner decision chartering the backlog triage and hygiene
  project, including staged batch approval.
- `WI-3355`: existing doubled-prefix reconciliation work that Stage 1 plans to
  close out.
- `WI-3500` and `WI-3501`: existing ownership for the `project_name` versus
  membership-table divergence that Stage 1 correctly defers.
- `bridge/gtkb-backlog-triage-and-hygiene-stage-0-analyzer-011.md`: VERIFIED
  Stage 0 analyzer report used as the empirical predecessor for this stage.
- `bridge/gtkb-backlog-triage-and-hygiene-stage-1-structural-repair-002.md`:
  prior NO-GO whose findings this REVISED proposal addresses.

## Specifications Carried Forward

- `GOV-STANDING-BACKLOG-001`
- `SPEC-AUTO-BACKLOG-FOR-IMPLEMENTATION-BEARING-SPECS-001`
- `GOV-08`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `ADR-STANDING-BACKLOG-DB-AUTHORITY-001`
- `DCL-STANDING-BACKLOG-DB-SCHEMA-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`

## Spec-to-Test Mapping Review

| Specification | Required implementation evidence | Verdict |
|---|---|---|
| `GOV-STANDING-BACKLOG-001` and `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` | Detector plan must expose `canonical_links_to_create`, `non_canonical_memberships_to_deactivate`, and `non_canonical_project_to_retire`; post-apply tests must prove no active memberships remain on the retired non-canonical project | ACCEPTED |
| `GOV-08` | Default mode must be read-only and no `groundtruth.db` mutation may occur at Write time | ACCEPTED |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Execution-time AUQs must use fresh dry-runs, not proposal snapshot counts | ACCEPTED |
| Owner D2 staged batch approval | `--apply` requires explicit owner-specified pair and refuses stale or absent pair inputs | ACCEPTED |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report must run pytest plus ruff check/format on the changed Python files and map tests to the specs above | ACCEPTED |

## Positive Confirmations

- The proposal fixes the prior P1 by making duplicate active memberships a
  first-class state to deactivate, not a no-op re-link.
- The proposal fixes the prior P2 by replacing "1 phantom to retire" with
  71 memberships to supersede, zero canonical links to create, and zero
  phantom projects to retire unless a fresh execution-time dry-run says
  otherwise.
- Live DB inspection confirms the prefix split still has 8 active
  non-canonical memberships (`WI-3400` through `WI-3407`) and 10 canonical
  memberships with all 8 overlapping.
- Live doubled-prefix dry-run confirms
  `PROJECT-PROJECT-GTKB-RELIABILITY-FIXES` is already retired,
  `retire_phantom=false`, has zero canonical links to create, and has 71
  phantom memberships to supersede.
- The proposal keeps `groundtruth.db` out of `target_paths`; execution-time DB
  mutation remains owner-AUQ-gated.
- The proposal correctly defers `project_name` versus membership-table
  divergence to `WI-3500` and `WI-3501`.

## Commands Executed

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-backlog-triage-and-hygiene-stage-1-structural-repair
# preflight_passed: true; missing_required_specs: []; missing_advisory_specs: []

python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-backlog-triage-and-hygiene-stage-1-structural-repair
# must_apply: 4; evidence gaps in must_apply clauses: 0; blocking gaps: 0

$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'
python -c "from groundtruth_kb.cli import main; main(args=['deliberations','search','Stage 1 structural repair prefix split detector WI-4454 revised'], standalone_mode=True)"
# No deliberations match 'Stage 1 structural repair prefix split detector WI-4454 revised'.

@'
import sqlite3
conn=sqlite3.connect('groundtruth.db')
conn.row_factory=sqlite3.Row
for pid in ['GTKB-V1-RELEASE-STRATEGY-001','PROJECT-GTKB-V1-RELEASE-STRATEGY-001']:
    rows=list(conn.execute("select id, work_item_id, project_id, status from current_project_work_item_memberships where project_id=? and status='active' order by work_item_id", (pid,)))
    print(pid, len(rows), [r['work_item_id'] for r in rows])
'@ | python -
# GTKB-V1-RELEASE-STRATEGY-001: 8 active memberships, WI-3400..WI-3407
# PROJECT-GTKB-V1-RELEASE-STRATEGY-001: 10 active memberships, including all 8 overlaps

@'
from pathlib import Path
from groundtruth_kb.cli_projects_reconcile import build_reconcile_plan, ReconcileRequest
from groundtruth_kb.config import GTConfig
report=build_reconcile_plan(GTConfig(db_path=Path('groundtruth.db'), project_root=Path('.')), ReconcileRequest(apply=False))
# inspected PROJECT-PROJECT-GTKB-RELIABILITY-FIXES plan
'@ | groundtruth-kb\.venv\Scripts\python.exe -
# phantom_status=retired; retire_phantom=false; canonical_links_to_create=0; phantom_memberships_to_supersede=71
```

## Required Implementation Notes

1. The implementation report must include tests proving the retired
   non-canonical project has zero active memberships after apply.
2. The implementation report must include tests proving no duplicate active
   canonical memberships are created for `WI-3400` through `WI-3407`.
3. The execution-time Stage 1.A and Stage 1.B AUQs must cite fresh dry-run
   output, not the proposal's snapshot counts.

## Owner Action Required

None.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
