NEW

# gtkb-wi4728-duplicate-project-record-merge — Retire duplicate-name program project record into the canonical one

bridge_kind: prime_proposal
Document: gtkb-wi4728-duplicate-project-record-merge
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-21 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: d209f895-a107-4379-be37-d4ecf5e8ea00
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: default (1m context window)

Project Authorization: PAUTH-PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-BOUNDED-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH
Work Item: WI-4728

target_paths: ["groundtruth.db"]

implementation_scope: governance
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

WI-4728 (P2 defect) records that two **active** MemBase project records share the
identical display name "Activity-Envelope Disposition and Autonomous Dispatch":

- `PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH` — the **canonical**
  record. Holds the active PAUTH
  (`PAUTH-PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-...-BOUNDED-IMPLEMENTATION-AUTHORIZATION`),
  the program bridge link, and members WI-4682..WI-4694 (13 work items). It is the
  record named as canonical by the program epicenter `DELIB-20265287` and the
  reframe `DELIB-20260621-EXPLICIT-HINT-CONTEXT-LOAD-REFRAME`.
- `PROJECT-ACTIVITY-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH` — the
  **non-canonical** duplicate. No PAUTH, no bridge link. Members WI-4682..WI-4694
  **plus** WI-4729 and WI-4730 (the only two members not already on the canonical
  record).

The duplicate display name makes name-based project resolution ambiguous and
pollutes the active project list, contradicting the single-canonical-project
intent of the program. This proposal reconciles the duplicate into the canonical
record using the governed `gt projects` CLI, append-only.

This is a **KB-only** reconciliation: it modifies MemBase project records and
memberships only; it touches **no source, test, hook, configuration, or
deployment file**. `target_paths` is `["groundtruth.db"]` (the canonical MemBase
file — the sole mutated artifact) with `kb_mutation_in_scope: true`, per the
bridge-compliance-gate's KB-mutation target-paths completeness rule. The
membership model is id-based (`link_project_work_item`, stable `PWM-<project>-<wi>`
ids); `cli_projects_reconcile.py` is scoped to doubled-prefix phantoms
(`PROJECT-PROJECT-*`) and does **not** apply to this same-name/different-id case,
so the fix uses the documented `gt projects` lifecycle commands directly.

## Implementation Plan

After Loyal Opposition `GO` and creation of the implementation-start packet
(`python scripts/implementation_authorization.py begin --bridge-id
gtkb-wi4728-duplicate-project-record-merge`), three governed, append-only
`gt projects` commands, each with an explicit `--change-reason` citing WI-4728:

1. `gt projects add-item PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH WI-4729 --change-reason "WI-4728: re-home unique member from duplicate PROJECT-ACTIVITY-... before retiring it"`
2. `gt projects add-item PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH WI-4730 --change-reason "WI-4728: re-home unique member from duplicate PROJECT-ACTIVITY-... before retiring it"`
3. `gt projects retire PROJECT-ACTIVITY-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH --change-reason "WI-4728: retire duplicate-name project; all members re-homed to canonical PROJECT-GTKB-ENVELOPE-... per DELIB-20265287; methodological precedent WI-3355/DELIB-2505/2506"`

The 13 overlapping memberships (WI-4682..WI-4694) already exist on the canonical
record, so only WI-4729 and WI-4730 are re-homed. Per `DELIB-2506` ("re-link to
retired canonical"), the duplicate's membership rows are intentionally left as
historical fact on the now-retired project rather than hard-deleted; append-only
versioning preserves the complete audit trail.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — a project-record state change is an
  implementation mutation; it must proceed through the bridge protocol
  (proposal → GO → impl-start authorization → report → VERIFIED) with an
  append-only audit trail. This proposal is that bridge artifact.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — requires the proposal
  cite every governing specification; this section satisfies it.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — requires project/WI
  linkage metadata; `Project`, `Work Item`, and `Project Authorization` are set
  above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — requires the verification
  plan derive its checks from the linked specs; the Spec-Derived Verification Plan
  below maps each governing spec to a concrete post-state check.
- `GOV-STANDING-BACKLOG-001` — the MemBase `work_items`/projects store is the
  single canonical work authority. Two active project records for one program
  corrupt the backlog's project-grouping integrity; reconciling to one canonical
  record restores single-source-of-truth backlog organization.

## Prior Deliberations

- `DELIB-20265287` — program epicenter (Activity-Envelope Disposition, Autonomous
  Fan-Out Dispatch & Scope Isolation). Establishes the single canonical program
  project. The non-canonical `PROJECT-ACTIVITY-...` is an accidental second record
  for the same program; retiring it preserves the epicenter's one-canonical-project
  intent. This proposal builds on (does not alter) that deliberation.
- `DELIB-20260621-EXPLICIT-HINT-CONTEXT-LOAD-REFRAME` — the 2026-06-21 reframe
  continuing the same program; consistent with consolidating onto the canonical
  project record.
- `DELIB-2505` / `DELIB-2506` (WI-3355) — methodological precedent: owner-directed
  reconciliation of duplicate/phantom project records by re-linking members to the
  canonical record and retiring the duplicate, append-only. `DELIB-2506`'s "re-link
  to retired canonical" disposition is the authority for leaving the duplicate's
  membership rows on the retired project as historical fact. This proposal differs
  from WI-3355 in that the duplicate here is a **same-name, different-id** record
  (`PROJECT-ACTIVITY-...` vs `PROJECT-GTKB-...`), not a doubled-prefix phantom, so
  the automated `cli_projects_reconcile.py` does not match and the documented
  `gt projects` CLI is used directly.

## Owner Decisions / Input

No owner decision is required for this proposal. Rationale:

1. WI-4728 is an authorized autonomous drive-list item under the active program
   PAUTH; it is not a formal-artifact (GOV/SPEC/ADR/DCL/PB) mutation.
2. `gt projects retire` is an **append-only lifecycle status change**, fully
   reversible by a subsequent `gt projects update ... --status active` version. It
   is **not** a destructive delete, so it is not an AUQ-class destructive action.
3. The operation is bounded to the two named project records and the re-homing of
   two work items, all within the canonical project's existing authorization.

Implementation proceeds under Loyal Opposition `GO` + the implementation-start
authorization packet derived from that `GO`.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-STANDING-BACKLOG-001` (single canonical
work/project authority) and the operating-model definition of a *project* (a
uniquely-identified grouping of known work) require that the program have exactly
one canonical project record. The duplicate violates that invariant; no new or
revised requirement is needed to authorize its reconciliation.

## Spec-Derived Verification Plan

Each linked specification maps to a deterministic post-state check run after the
three CLI commands:

| Linked spec | Derived check | Expected result |
|-------------|---------------|-----------------|
| `GOV-STANDING-BACKLOG-001` (single canonical project) | `gt projects list` filtered for the display name | Exactly **one** active record: `PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH`; `PROJECT-ACTIVITY-...` absent from the active list |
| `GOV-STANDING-BACKLOG-001` (no orphaned work) | `gt projects show PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH` | Lists all 15 members: WI-4682..WI-4694 **+ WI-4729 + WI-4730** |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (append-only audit) | `gt projects show PROJECT-ACTIVITY-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH` | Status `retired`; prior active version preserved (new version appended, not overwritten) |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (CLI surface intact) | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_projects_cli.py -q --no-header` | All tests pass (the projects CLI surface is unbroken by the lifecycle operations) |

Evidence (command transcripts) will be captured in the post-implementation report.

## Risk / Rollback

Low risk; KB-only. Risk surface = MemBase project records + memberships. No source
behavior changes and no work items are deleted (append-only versioning preserves
all history). Rollback is a single append-only reversal:
`gt projects update PROJECT-ACTIVITY-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH --status active --change-reason "rollback WI-4728"`
(and, if desired, the two re-homed memberships may be superseded). The canonical
record and all program work items are untouched on rollback.

Recommended follow-up (out of scope; capture as a separate WI): a deterministic
guard — doctor check or assertion — that no two **active** project records share a
normalized display name, to prevent recurrence platform-wide. Not included here to
keep this fix proportionate and avoid coupling to any other latent duplicates.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi4728-duplicate-project-record-merge`; no prior version is
deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file
chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`chore` — MemBase project-record reconciliation (backlog/project hygiene). No
net-new capability, no source behavior change; purely project-record maintenance.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
