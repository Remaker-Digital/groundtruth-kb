NEW

# GTKB-GOV-004 dangling membership manual triage (Slice 4)

bridge_kind: prime_proposal
Document: gtkb-gov-004-dangling-membership-manual-triage-slice-4
Version: 001
Author: Prime Builder (Cursor, harness E)
Date: 2026-07-01 UTC

author_identity: prime-builder/cursor
author_harness_id: E
author_session_context_id: cursor-s529-governance-hardening-auto-process
author_model: Cursor Agent
author_model_version: interactive
author_model_configuration: ::init gtkb pb; owner explicit PB session; GTKB-GOV-004 slice 4

Project Authorization: PAUTH-PROJECT-GTKB-GOVERNANCE-HARDENING-GOVERNANCE-HARDENING-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-GOVERNANCE-HARDENING
Work Item: GTKB-GOV-004

target_paths: []

implementation_scope: membase_project_membership_and_backlog_metadata
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

Slice 3 VERIFIED (`gtkb-gov-004-dangling-membership-repair-slice-3-006`) reduced
`dangling_or_terminal_project_membership` from **5 → 3**. This slice applies
**evidence-backed manual triage** for the three deferred rows: one PWM re-home
with active target, two **remove-only + metadata alignment** for long-deferred
exploratory items with zero inventory candidates.

Post-slice inventory target: **dangling count 3 → 0** (or **1 → 0** for WI-4851
re-home + two items becoming explicit deferred orphans with refreshed metadata).

## Manual triage disposition table

| Work item | Evidence | Operations |
|-----------|----------|------------|
| `WI-4851` | Active `PWM-...-ADOPTER-EXPERIENCE-WI-4851` on **retired** `PROJECT-GTKB-ADOPTER-EXPERIENCE`; 24 weak candidates; factory/agent Rosetta ADR aligns with active `PROJECT-GTKB-RUNTIME-ORCHESTRATION-DISCOVERY` (existing ADR work: WI-4911) | `remove-item` + `add-item` |
| `WORKLIST-OWNER-DIRECTED-BACKLOG-ADDITION-2026-04-17-CLAUDE-DESIGN-GUI-EXPLORATION` | Application-scoped GUI exploration; **zero** inventory candidates; retired `PROJECT-AGENT-RED-CLAUDE-DESIGN-GUI-EXPLORATION`; `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` | `remove-item` + `backlog update` (`resolution_status=deferred`) |
| `WORKLIST-ZERO-KNOWLEDGE-ARCHITECTURE-PHASE-4-LONGER-TERM` | Long-term ZK Phase 4; **zero** candidates; 3 retired PWM hosts (one already `removed`/`retired`) | `remove-item` (active row only) + `backlog update` (`resolution_status=deferred`) |

**Explicitly out of scope:**

- `needs_manual_triage` bucket (7 ids) — separate slice
- `obsolete_or_duplicate_candidate` (11 ids) — per-WI evidence slice
- WI retirement / `wont_fix` / new project creation
- Source/test/hook edits

## Live evidence (2026-07-01)

Inventory: `.gtkb-state/governance-hardening/inventory-post-slice3-20260701.json`

PWM latest-version read-back:

| WI | PWM id | project_id | PWM status | project status |
|----|--------|------------|------------|----------------|
| `WI-4851` | `PWM-PROJECT-GTKB-ADOPTER-EXPERIENCE-WI-4851` | `PROJECT-GTKB-ADOPTER-EXPERIENCE` | `active` | `retired` |
| `WORKLIST-...-GUI-EXPLORATION` | `PWM-PROJECT-AGENT-RED-...` | `PROJECT-AGENT-RED-CLAUDE-DESIGN-GUI-EXPLORATION` | `active` | `retired` |
| `WORKLIST-ZERO-KNOWLEDGE-...` | `PWM-PROJECT-ZERO-KNOWLEDGE-ARCHITECTURE-...` | `PROJECT-ZERO-KNOWLEDGE-ARCHITECTURE` | `active` | `retired` |
| `WORKLIST-ZERO-KNOWLEDGE-...` | `PWM-PROJECT-GTKB-SECURITY-PRIVACY-...` | `PROJECT-GTKB-SECURITY-PRIVACY` | `retired` | `retired` |
| `WORKLIST-ZERO-KNOWLEDGE-...` | `PWM-PROJECT-ZERO-KNOWLEDGE-ARCHITECTURE-PHASE-4-...` | `PROJECT-ZERO-KNOWLEDGE-ARCHITECTURE-PHASE-4` | `removed` | `retired` |

**WI-4851 target rationale:** `PROJECT-GTKB-RUNTIME-ORCHESTRATION-DISCOVERY` is **active**
with ADR-authoring members (WI-4911). WI-4851 is governance/factory-layer Rosetta ADR work;
retired adopter-experience host is stale per `DELIB-20266085`.

**WORKLIST dispositions:** zero inventory candidates → no `add-item`; align
`resolution_status` to `deferred` matching existing `status_detail` intent; remove dangling
`active` PWM on retired projects only. Items remain platform backlog rows without active
project membership until a future owner-directed re-home slice.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-08`
- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` — Agent Red GUI exploration is application-scoped
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — membership/metadata only
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` — governance-hardening PAUTH batch
- `DELIB-20266085` — `PROJECT-GTKB-ADOPTER-EXPERIENCE` retirement disposition
- `bridge/gtkb-gov-004-dangling-membership-repair-slice-3-006.md` — VERIFIED; deferred 3 ids
- `bridge/gtkb-gov-004-dangling-membership-repair-slice-3-002.md` — GO scope discipline
- `bridge/gtkb-deferred-backlog-metadata-refresh-008.md` — VERIFIED metadata-only precedent
- `DELIB-20260745` / `DELIB-20261322` — `gt projects remove-item` append-only precedent


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

Owner directive (S529): auto-process `PROJECT-GTKB-GOVERNANCE-HARDENING`; explicit **PB session**
for implementation. Slice 4 advances remaining dangling manual triage under `GTKB-GOV-004`.

## Requirement Sufficiency

Existing requirements sufficient. Manual triage dispositions derive from post-slice-3 inventory
+ live PWM/project reads; no new SPEC/GOV/ADR required.

## Implementation commands (exact)

All mutations cite this bridge thread in `--change-reason`. Use governed `gt projects` / `gt backlog`.

### 1. WI-4851 — re-home to runtime orchestration discovery

```powershell
gt projects remove-item PROJECT-GTKB-ADOPTER-EXPERIENCE WI-4851 --change-reason "GTKB-GOV-004 slice 4: detach from retired PROJECT-GTKB-ADOPTER-EXPERIENCE (bridge/gtkb-gov-004-dangling-membership-manual-triage-slice-4)."

gt projects add-item PROJECT-GTKB-RUNTIME-ORCHESTRATION-DISCOVERY WI-4851 --change-reason "GTKB-GOV-004 slice 4: manual triage re-home to active PROJECT-GTKB-RUNTIME-ORCHESTRATION-DISCOVERY (bridge/gtkb-gov-004-dangling-membership-manual-triage-slice-4)."
```

### 2. WORKLIST Agent Red GUI — remove dangling PWM + defer metadata

```powershell
gt projects remove-item PROJECT-AGENT-RED-CLAUDE-DESIGN-GUI-EXPLORATION WORKLIST-OWNER-DIRECTED-BACKLOG-ADDITION-2026-04-17-CLAUDE-DESIGN-GUI-EXPLORATION --change-reason "GTKB-GOV-004 slice 4: detach from retired Agent Red exploration project (bridge/gtkb-gov-004-dangling-membership-manual-triage-slice-4)."

gt backlog update WORKLIST-OWNER-DIRECTED-BACKLOG-ADDITION-2026-04-17-CLAUDE-DESIGN-GUI-EXPLORATION --resolution-status deferred --status-detail "Application-scoped Agent Red GUI exploration (GOV-AGENT-RED-NESTED); no active platform project membership after retired PROJECT-AGENT-RED-CLAUDE-DESIGN-GUI-EXPLORATION PWM removal. Resume only on owner elevation or active application project re-home." --owner-approved --change-reason "GTKB-GOV-004 slice 4 manual triage (S529)."
```

### 3. WORKLIST ZK Phase 4 — remove active dangling PWM + defer metadata

```powershell
gt projects remove-item PROJECT-ZERO-KNOWLEDGE-ARCHITECTURE WORKLIST-ZERO-KNOWLEDGE-ARCHITECTURE-PHASE-4-LONGER-TERM --change-reason "GTKB-GOV-004 slice 4: detach from retired PROJECT-ZERO-KNOWLEDGE-ARCHITECTURE (bridge/gtkb-gov-004-dangling-membership-manual-triage-slice-4)."

gt backlog update WORKLIST-ZERO-KNOWLEDGE-ARCHITECTURE-PHASE-4-LONGER-TERM --resolution-status deferred --status-detail "Long-term ZK Phase 4; all PWM hosts retired/removed as of slice 4. Re-home when an active ZK/security project is reactivated by owner directive." --owner-approved --change-reason "GTKB-GOV-004 slice 4 manual triage (S529)."
```

### 4. GTKB-GOV-004 metadata

```powershell
gt backlog update GTKB-GOV-004 --related-bridge-threads "[\"gtkb-project-membership-reconciliation-slice-1-inventory-tool\",\"gtkb-deferred-backlog-metadata-refresh\",\"gtkb-gov-004-inventory-evidence-slice-2\",\"gtkb-gov-004-dangling-membership-repair-slice-3\",\"gtkb-gov-004-dangling-membership-manual-triage-slice-4\"]" --status-detail "Inventory post-slice-3: dangling_or_terminal_project_membership=3; slice 4 manual triage targets all 3 (WI-4851 re-home; 2 WORKLIST deferred remove-only). Evidence: .gtkb-state/governance-hardening/inventory-post-slice3-20260701.json." --owner-approved --change-reason "GTKB-GOV-004 slice 4 proposal scope (S529)."
```

## Spec-Derived Verification Plan

1. `gt projects show PROJECT-GTKB-RUNTIME-ORCHESTRATION-DISCOVERY --json` — includes `WI-4851` active.
2. Latest PWM for `WI-4851` on `PROJECT-GTKB-ADOPTER-EXPERIENCE` — non-active (`removed`).
3. Latest PWM for Agent Red WORKLIST on `PROJECT-AGENT-RED-CLAUDE-DESIGN-GUI-EXPLORATION` — non-active.
4. Latest PWM for ZK WORKLIST on `PROJECT-ZERO-KNOWLEDGE-ARCHITECTURE` — non-active.
5. `gt backlog show WORKLIST-OWNER-DIRECTED-BACKLOG-ADDITION-2026-04-17-CLAUDE-DESIGN-GUI-EXPLORATION --json` — `resolution_status=deferred`.
6. `gt backlog show WORKLIST-ZERO-KNOWLEDGE-ARCHITECTURE-PHASE-4-LONGER-TERM --json` — `resolution_status=deferred`.
7. Re-run inventory; `dangling_or_terminal_project_membership` count **0**; WI-4851 classifies `already_active_project_member`.

```powershell
python scripts/inventory_project_membership_reconciliation.py --format json --output-json .gtkb-state/governance-hardening/inventory-post-slice4-20260701.json
```

8. `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_inventory_project_membership_reconciliation.py -q --tb=short` — **5 passed** (baseline).

## Risk / Rollback

| Risk | Mitigation |
|------|------------|
| WI-4851 wrong target among 24 weak candidates | Explicit ADR-cluster rationale + active project with ADR members |
| Agent Red WI treated as platform work | Metadata cites application isolation; deferred not retired |
| Orphan WORKLIST rows after remove-only | Accepted manual triage outcome; metadata documents deferral |

Rollback: compensating slice with append-only PWM reversals if LO directs.

## Bridge Filing

Append-only chain `gtkb-gov-004-dangling-membership-manual-triage-slice-4`.

## Recommended Commit Type

Recommended commit type: `docs(governance): GTKB-GOV-004 dangling manual triage slice 4`

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
