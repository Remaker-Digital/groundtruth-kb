NEW

# GTKB-GOV-004 dangling membership repair (Slice 3)

bridge_kind: prime_proposal
Document: gtkb-gov-004-dangling-membership-repair-slice-3
Version: 001
Author: Prime Builder (Cursor, harness E)
Date: 2026-07-01 UTC

author_identity: prime-builder/cursor
author_harness_id: E
author_session_context_id: cursor-s529-governance-hardening-auto-process
author_model: Cursor Agent
author_model_version: interactive
author_model_configuration: ::init gtkb pb resume; PROJECT-GTKB-GOVERNANCE-HARDENING auto-process slice 3

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

`GTKB-GOV-004` inventory evidence (slice 2 VERIFIED) classified **5** work items as
`dangling_or_terminal_project_membership` — each has **no active membership in a
non-terminal project** while still carrying `active` PWM rows on **retired** projects.

This slice repairs the **two unambiguous cases** where the inventory reports exactly
**one** weak candidate target project. For each WI: append-only `gt projects remove-item`
on every retired-project `active` PWM, then `gt projects add-item` to the inventory
candidate. Finally refresh `GTKB-GOV-004` metadata to record slice completion.

**In scope (2 work items, 4 remove + 2 add operations):**

| Work item | Dangling retired projects (remove `active` PWM) | Target project (add `active` PWM) |
|-----------|--------------------------------------------------|-----------------------------------|
| `GTKB-DASHBOARD-RETENTION` | `PROJECT-GTKB-DASHBOARD`, `PROJECT-GTKB-DASHBOARD-RETENTION-POLICY` | `PROJECT-GTKB-DASHBOARD-OBSERVABILITY` |
| `GTKB-MASS-001` | `PROJECT-GTKB-MASS-001` | `GTKB-V1-RELEASE-STRATEGY-001` |

**Explicitly out of scope (deferred to manual-triage slice):**

- `WI-4851` — multiple weak candidates; no single inventory target
- `WORKLIST-OWNER-DIRECTED-BACKLOG-ADDITION-2026-04-17-CLAUDE-DESIGN-GUI-EXPLORATION` — zero candidates
- `WORKLIST-ZERO-KNOWLEDGE-ARCHITECTURE-PHASE-4-LONGER-TERM` — zero candidates
- Bulk disposition of `obsolete_or_duplicate_candidate` (11) or `needs_manual_triage` (7)
- Any source/test/hook edits; no WI retirement or `resolution_status` changes

## Live evidence (2026-07-01)

Inventory source: `.gtkb-state/governance-hardening/inventory-20260701.json` (slice 2 VERIFIED).

PWM read-back (latest version per `membership_id`):

| WI | PWM id | project_id | PWM status | project status |
|----|--------|------------|------------|----------------|
| `GTKB-DASHBOARD-RETENTION` | `PWM-PROJECT-GTKB-DASHBOARD-GTKB-DASHBOARD-RETENTION` | `PROJECT-GTKB-DASHBOARD` | `active` | `retired` |
| `GTKB-DASHBOARD-RETENTION` | `PWM-PROJECT-GTKB-DASHBOARD-RETENTION-POLICY-GTKB-DASHBOARD-RETENTION` | `PROJECT-GTKB-DASHBOARD-RETENTION-POLICY` | `active` | `retired` |
| `GTKB-MASS-001` | `PWM-PROJECT-GTKB-MASS-001-GTKB-MASS-001` | `PROJECT-GTKB-MASS-001` | `active` | `retired` |

Target projects are **active** (`gt projects show` 2026-07-01):

- `PROJECT-GTKB-DASHBOARD-OBSERVABILITY` — `status=active`
- `GTKB-V1-RELEASE-STRATEGY-001` — `status=active`

Note: `PWM-PROJECT-GTKB-METHODOLOGY-AI-MATURITY-GTKB-MASS-001` is already
`status=retired`; no remove-item needed for that row.

**ACID / PAUTH scope note:** target projects have snapshot-bound bounded PAUTHs that
do not list these WIs. This slice is **membership reconciliation** under
`GTKB-GOV-004` / governance-hardening PAUTH — not implementation authorization for
dashboard-observability or v1-release work. Adding membership restores correct project
grouping only; it does not authorize implementation of the added WIs' program scope.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — append-only numbered bridge chain.
- `GOV-STANDING-BACKLOG-001` — every non-terminal WI belongs to an active project grouping.
- `GOV-08` — MemBase is single source of truth for membership state.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — membership repair ≠ implementation approval.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — actions derive from fresh inventory + PWM reads.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — linkage block above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — read-back verification plan below.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all operations remain in-root.

## Prior Deliberations

- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` — governance-hardening PAUTH batch.
- `DELIB-20260745` — `gt projects remove-item` append-only non-active membership precedent.
- `DELIB-20261322` — remove/retire must never append an `active` membership incorrectly.
- `bridge/gtkb-gov-004-inventory-evidence-slice-2-002.md` — GO deferred dangling repair to follow-on apply slice.
- `bridge/gtkb-gov-004-inventory-evidence-slice-2-004.md` — VERIFIED inventory evidence baseline.
- `bridge/gtkb-project-membership-reconciliation-slice-1-scoping-002.md` — GO for decomposed membership slices.
- `bridge/gtkb-projects-remove-item-cli-slice-1-011.md` — VERIFIED `gt projects remove-item` CLI.


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

Owner directive (2026-07-01, S529): auto-process `PROJECT-GTKB-GOVERNANCE-HARDENING`; all
child work items approved for implementation. This slice advances `GTKB-GOV-004` dangling
repair for the two inventory-unambiguous rows only.

## Requirement Sufficiency

Existing requirements are sufficient. Inventory taxonomy + `gt projects` lifecycle service
fully constrain bounded membership repair; no new SPEC/GOV/ADR required.

## Implementation commands (exact)

All commands use `--change-reason` citing this bridge thread. Membership mutations use the
deterministic `gt projects` service (append-only PWM versions).

### 1. GTKB-DASHBOARD-RETENTION

```powershell
E:\GT-KB\groundtruth-kb\.venv\Scripts\gt.exe projects remove-item PROJECT-GTKB-DASHBOARD GTKB-DASHBOARD-RETENTION --change-reason "GTKB-GOV-004 slice 3: detach from retired PROJECT-GTKB-DASHBOARD per inventory dangling repair (bridge/gtkb-gov-004-dangling-membership-repair-slice-3)."

E:\GT-KB\groundtruth-kb\.venv\Scripts\gt.exe projects remove-item PROJECT-GTKB-DASHBOARD-RETENTION-POLICY GTKB-DASHBOARD-RETENTION --change-reason "GTKB-GOV-004 slice 3: detach from retired PROJECT-GTKB-DASHBOARD-RETENTION-POLICY per inventory dangling repair (bridge/gtkb-gov-004-dangling-membership-repair-slice-3)."

E:\GT-KB\groundtruth-kb\.venv\Scripts\gt.exe projects add-item PROJECT-GTKB-DASHBOARD-OBSERVABILITY GTKB-DASHBOARD-RETENTION --change-reason "GTKB-GOV-004 slice 3: active membership to inventory weak candidate PROJECT-GTKB-DASHBOARD-OBSERVABILITY (bridge/gtkb-gov-004-dangling-membership-repair-slice-3)."
```

### 2. GTKB-MASS-001

```powershell
E:\GT-KB\groundtruth-kb\.venv\Scripts\gt.exe projects remove-item PROJECT-GTKB-MASS-001 GTKB-MASS-001 --change-reason "GTKB-GOV-004 slice 3: detach from retired PROJECT-GTKB-MASS-001 per inventory dangling repair (bridge/gtkb-gov-004-dangling-membership-repair-slice-3)."

E:\GT-KB\groundtruth-kb\.venv\Scripts\gt.exe projects add-item GTKB-V1-RELEASE-STRATEGY-001 GTKB-MASS-001 --change-reason "GTKB-GOV-004 slice 3: active membership to inventory weak candidate GTKB-V1-RELEASE-STRATEGY-001 (bridge/gtkb-gov-004-dangling-membership-repair-slice-3)."
```

### 3. GTKB-GOV-004 metadata

```powershell
E:\GT-KB\groundtruth-kb\.venv\Scripts\gt.exe backlog update GTKB-GOV-004 --related-bridge-threads "[\"gtkb-project-membership-reconciliation-slice-1-inventory-tool\",\"gtkb-deferred-backlog-metadata-refresh\",\"gtkb-gov-004-inventory-evidence-slice-2\",\"gtkb-gov-004-dangling-membership-repair-slice-3\"]" --status-detail "Inventory 2026-07-01: total_non_terminal=186; dangling_or_terminal_project_membership=5 (slice 3 repairs 2 unambiguous: GTKB-DASHBOARD-RETENTION, GTKB-MASS-001). Remaining dangling: WI-4851 + 2 WORKLIST rows. Evidence: .gtkb-state/governance-hardening/inventory-20260701.json." --owner-approved --change-reason "GTKB-GOV-004 slice 3 dangling membership repair proposal scope (S529)."
```

## Spec-Derived Verification Plan

Post-implementation read-back (all must pass):

1. `gt projects show PROJECT-GTKB-DASHBOARD-OBSERVABILITY --json` — includes
   `GTKB-DASHBOARD-RETENTION` with `membership_status=active`.
2. `gt projects show GTKB-V1-RELEASE-STRATEGY-001 --json` — includes `GTKB-MASS-001`
   with `membership_status=active`.
3. Latest PWM for `GTKB-DASHBOARD-RETENTION` on `PROJECT-GTKB-DASHBOARD` and
   `PROJECT-GTKB-DASHBOARD-RETENTION-POLICY` — `status` is non-active (`removed`).
4. Latest PWM for `GTKB-MASS-001` on `PROJECT-GTKB-MASS-001` — `status` is non-active (`removed`).
5. Re-run inventory CLI; both WIs classify as `already_active_project_member` (not
   `dangling_or_terminal_project_membership`); `dangling_or_terminal_project_membership`
   bucket count decreases from **5** to **3**.

```powershell
python scripts/inventory_project_membership_reconciliation.py --format json --output-json .gtkb-state/governance-hardening/inventory-post-slice3-20260701.json
```

6. `gt backlog show GTKB-GOV-004 --json` — `related_bridge_threads` includes
   `gtkb-gov-004-dangling-membership-repair-slice-3`; `status_detail` cites slice 3
   completion and remaining dangling count **3**.
7. Specification-derived regression for inventory tool (unchanged surface):

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_inventory_project_membership_reconciliation.py -q --tb=short
```

Observed baseline: **5 passed**.

## Risk / Rollback

| Risk | Mitigation |
|------|------------|
| Wrong target project | Only the two single-candidate inventory rows; explicit PWM table in proposal |
| PAUTH scope confusion | Membership repair only; no implementation of added WIs' program work |
| Accidental retire vs remove | Use `remove-item` only (benign detach); no `retire-item` |

Rollback: append-only reverse — `remove-item` from new target, `add-item` back to prior
retired projects only if LO directs a compensating slice (not recommended; retired
projects should not regain active members).

## Bridge Filing

Append-only numbered chain for `gtkb-gov-004-dangling-membership-repair-slice-3` per
`GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

docs(governance): GTKB-GOV-004 dangling membership repair slice 3

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
