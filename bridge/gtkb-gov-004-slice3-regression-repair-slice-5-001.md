NEW
author_identity: prime-builder/cursor
author_harness_id: E
author_session_context_id: cursor-s529-governance-hardening-auto-process
author_model: Cursor Agent
author_model_version: interactive
author_model_configuration: ::init gtkb pb; GTKB-GOV-004 continue after slice 4 NO-GO

# GTKB-GOV-004 slice-3 regression re-repair (Slice 5)

bridge_kind: prime_proposal
Document: gtkb-gov-004-slice3-regression-repair-slice-5
Version: 001
Author: Prime Builder (Cursor, harness E)
Date: 2026-07-01 UTC


Project Authorization: PAUTH-PROJECT-GTKB-GOVERNANCE-HARDENING-GOVERNANCE-HARDENING-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-GOVERNANCE-HARDENING
Work Item: GTKB-GOV-004

target_paths: []

implementation_scope: membase_project_membership
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

`bridge/gtkb-gov-004-dangling-membership-manual-triage-slice-4-004.md` (NO-GO) documents
**regression** of slice-3 VERIFIED PWM repairs: `GTKB-DASHBOARD-RETENTION` and `GTKB-MASS-001`
again carry **active** PWM rows on **retired** projects. Post-slice-4 inventory shows both back
in `dangling_or_terminal_project_membership` despite `gtkb-gov-004-dangling-membership-repair-slice-3-006`
VERIFIED.

This slice **re-applies the same governed mutations** from slice 3 (`-001`/`-005`) for those two
WIs only. No changes to slice-4 in-scope targets (already mutated; partial credit in NO-GO `-004`).

## Live regression evidence (2026-07-01)

Post-slice-4 inventory (`.gtkb-state/governance-hardening/inventory-post-slice4-20260701.json`):

| WI | Classification | active_project_ids |
|----|----------------|-------------------|
| `GTKB-DASHBOARD-RETENTION` | `dangling_or_terminal_project_membership` | `[]` |
| `GTKB-MASS-001` | `dangling_or_terminal_project_membership` | `[]` |

PWM latest-version read-back:

| WI | project_id | PWM status | project status |
|----|------------|------------|----------------|
| `GTKB-DASHBOARD-RETENTION` | `PROJECT-GTKB-DASHBOARD` | `active` | `retired` |
| `GTKB-DASHBOARD-RETENTION` | `PROJECT-GTKB-DASHBOARD-RETENTION-POLICY` | `active` | `retired` |
| `GTKB-MASS-001` | `PROJECT-GTKB-MASS-001` | `active` | `retired` |

Slice 3 target state (VERIFIED `-006`): both WIs on active hosts
(`PROJECT-GTKB-DASHBOARD-OBSERVABILITY`, `GTKB-V1-RELEASE-STRATEGY-001`) as
`already_active_project_member`.

## Operations (re-apply slice 3)

| WI | remove from (retired) | add to (active) |
|----|----------------------|-----------------|
| `GTKB-DASHBOARD-RETENTION` | `PROJECT-GTKB-DASHBOARD`, `PROJECT-GTKB-DASHBOARD-RETENTION-POLICY` | `PROJECT-GTKB-DASHBOARD-OBSERVABILITY` |
| `GTKB-MASS-001` | `PROJECT-GTKB-MASS-001` | `GTKB-V1-RELEASE-STRATEGY-001` |

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-08`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`

## Prior Deliberations

- `bridge/gtkb-gov-004-dangling-membership-repair-slice-3-006.md` — VERIFIED (regressed)
- `bridge/gtkb-gov-004-dangling-membership-manual-triage-slice-4-004.md` — NO-GO P2 regression finding
- `bridge/gtkb-gov-004-dangling-membership-repair-slice-3-001.md` — original repair spec


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

Owner **Continue** (S529 PB session): advance GTKB-GOV-004 after slice 4 NO-GO; repair regression
before revised slice-4 verification.

## Requirement Sufficiency

Existing requirements sufficient; re-apply of VERIFIED slice-3 mutations.

## Implementation commands

```powershell
gt projects remove-item PROJECT-GTKB-DASHBOARD GTKB-DASHBOARD-RETENTION --change-reason "Slice 5: re-repair slice-3 regression (bridge/gtkb-gov-004-slice3-regression-repair-slice-5)."

gt projects remove-item PROJECT-GTKB-DASHBOARD-RETENTION-POLICY GTKB-DASHBOARD-RETENTION --change-reason "Slice 5: re-repair slice-3 regression (bridge/gtkb-gov-004-slice3-regression-repair-slice-5)."

gt projects add-item PROJECT-GTKB-DASHBOARD-OBSERVABILITY GTKB-DASHBOARD-RETENTION --change-reason "Slice 5: re-repair slice-3 regression (bridge/gtkb-gov-004-slice3-regression-repair-slice-5)."

gt projects remove-item PROJECT-GTKB-MASS-001 GTKB-MASS-001 --change-reason "Slice 5: re-repair slice-3 regression (bridge/gtkb-gov-004-slice3-regression-repair-slice-5)."

gt projects add-item GTKB-V1-RELEASE-STRATEGY-001 GTKB-MASS-001 --change-reason "Slice 5: re-repair slice-3 regression (bridge/gtkb-gov-004-slice3-regression-repair-slice-5)."
```

## Spec-Derived Verification Plan

1. Both WIs classify `already_active_project_member` in fresh inventory run.
2. Retired-host PWM latest versions non-active (`removed`).
3. Global `dangling_or_terminal_project_membership` count decreases by **2** vs post-slice-4 baseline (4 → 2).
4. `pytest platform_tests/scripts/test_inventory_project_membership_reconciliation.py -q` — 5 passed.

```powershell
python scripts/inventory_project_membership_reconciliation.py --format json --output-json .gtkb-state/governance-hardening/inventory-post-slice5-20260701.json
```

## Risk / Rollback

Root-cause of regression unknown (possible concurrent writer or restore). This slice restores
known-good state; a separate investigation WI may be warranted if regression recurs.

## Recommended Commit Type

Recommended commit type: `docs(governance): GTKB-GOV-004 slice 3 regression re-repair slice 5`

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
