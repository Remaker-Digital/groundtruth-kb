NEW

# GTKB-GOV-004 inventory evidence capture (Slice 2)

bridge_kind: prime_proposal
Document: gtkb-gov-004-inventory-evidence-slice-2
Version: 001
Author: Prime Builder (Cursor, harness E)
Date: 2026-07-01 UTC

author_identity: prime-builder/cursor
author_harness_id: E
author_session_context_id: cursor-s529-governance-hardening-auto-process
author_model: Cursor Agent
author_model_version: interactive
author_model_configuration: ::init gtkb pb; owner-directed PROJECT-GTKB-GOVERNANCE-HARDENING auto-process

Project Authorization: PAUTH-PROJECT-GTKB-GOVERNANCE-HARDENING-GOVERNANCE-HARDENING-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-GOVERNANCE-HARDENING
Work Item: GTKB-GOV-004

target_paths: []

implementation_scope: membase_backlog_metadata
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

`PROJECT-GTKB-GOVERNANCE-HARDENING` has no activatable Prime Builder `GO` threads
remaining; child `WI-3268` is already **VERIFIED** and was resolved in MemBase
during S529. The remaining open member `GTKB-GOV-004` needs a bounded follow-on
slice that captures the **read-only inventory evidence** produced by the
VERIFIED `gtkb-project-membership-reconciliation-slice-1-inventory-tool` and
refreshes `GTKB-GOV-004` backlog metadata so future apply-slices have a durable,
fresh baseline.

This slice is **metadata-only**:

1. Persist the inventory JSON/Markdown outputs under
   `.gtkb-state/governance-hardening/` (already generated in this session).
2. Update `GTKB-GOV-004` `status_detail` and `related_bridge_threads` to cite
   the inventory run, deferred-metadata refresh VERIFIED slice, and the
   classification summary counts.
3. **Do not** bulk-resolve, retire, or reclassify the 11
   `obsolete_or_duplicate_candidate` rows flagged by the inventory heuristic —
   those rows carry keyword signals only and lack `superseded_by` evidence.

## Live inventory evidence (2026-07-01)

Command:

```powershell
python scripts/inventory_project_membership_reconciliation.py --format json --output-json .gtkb-state/governance-hardening/inventory-20260701.json --output-markdown .gtkb-state/governance-hardening/inventory-20260701.md
```

Observed summary:

| Metric | Value |
|--------|------:|
| `total_non_terminal_work_items` | 187 |
| `duplicate_inventory_rows` | 0 |
| `omitted_non_terminal_work_items` | 0 |
| `already_active_project_member` | 49 |
| `new_project_candidate_cluster` | 100 |
| `existing_project_candidate_weak` | 15 |
| `obsolete_or_duplicate_candidate` | 11 |
| `needs_manual_triage` | 7 |
| `dangling_or_terminal_project_membership` | 5 |

Follow-on apply slices (separate bridge proposals, out of scope here):

- dangling membership repair (5 ids)
- manual triage queue (7 ids)
- obsolete-keyword review (11 ids; requires per-WI evidence, not heuristic alone)

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — append-only numbered bridge chain is live workflow authority.
- `GOV-STANDING-BACKLOG-001` — MemBase `work_items` is backlog authority; `GTKB-GOV-004` metadata must reflect fresh inventory evidence.
- `GOV-08` — KB is single source of truth; stale umbrella status misleads prioritization.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — inventory counts derive from a fresh read-only MemBase scan.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — bounded metadata slice under active PAUTH.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — linkage block above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — read-back verification plan below.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all paths remain under `E:\GT-KB`.

## Prior Deliberations

- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` — MemBase-backed formal backlog direction.
- `DELIB-S342-BACKLOG-WORK-ITEMS-CANONICAL-PIVOT` — live backlog records are canonical.
- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` — owner-approved governance-hardening PAUTH batch.
- `bridge/gtkb-project-membership-reconciliation-slice-1-inventory-tool-004.md` — VERIFIED read-only inventory tool.
- `bridge/gtkb-deferred-backlog-metadata-refresh-008.md` — VERIFIED deferred-metadata refresh under `GTKB-GOV-004`.
- `bridge/gtkb-codex-feedback-pattern-lints-006.md` — VERIFIED; parent `WI-3268` resolved S529.


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

Owner directive (2026-07-01, this session): auto-process all PB-actionable work for
`PROJECT-GTKB-GOVERNANCE-HARDENING`; all child work items approved for
implementation; nothing deferred. This slice advances the remaining open member
`GTKB-GOV-004` without over-scoping into unreviewed bulk disposition.

## Requirement Sufficiency

Existing requirements are sufficient. This is backlog metadata reconciliation and
evidence capture under `GTKB-GOV-004`; no new SPEC/GOV/ADR is required before this
metadata slice.

## Spec-Derived Verification Plan

Post-implementation read-back (all must pass):

1. `Test-Path .gtkb-state/governance-hardening/inventory-20260701.json` — `True`.
2. `Test-Path .gtkb-state/governance-hardening/inventory-20260701.md` — `True`.
3. `gt backlog show GTKB-GOV-004 --json` — `status_detail` cites inventory date,
   total non-terminal count `187`, and classification bucket counts; `related_bridge_threads`
   includes `gtkb-project-membership-reconciliation-slice-1-inventory-tool`,
   `gtkb-deferred-backlog-metadata-refresh`, and `gtkb-gov-004-inventory-evidence-slice-2`.
4. Re-run inventory CLI — `total_non_terminal_work_items` remains `187` (±0) and
   `duplicate_inventory_rows` remains `0`.
5. Specification-derived regression for the inventory tool surface:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_inventory_project_membership_reconciliation.py -q --tb=short
```

Observed baseline (2026-07-01): **5 passed**.

## Risk / Rollback

Risk: mis-stating inventory counts in `status_detail`. Mitigation: copy counts
directly from the JSON summary block. Rollback: single MemBase append-only revert
via a follow-on `gt backlog update` restoring prior `status_detail` / thread list.

## Bridge Filing

Append-only numbered chain for `gtkb-gov-004-inventory-evidence-slice-2` per
`GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

docs(governance): GTKB-GOV-004 inventory evidence slice 2 metadata

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
