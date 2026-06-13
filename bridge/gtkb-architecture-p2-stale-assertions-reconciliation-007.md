REVISED

# gtkb-architecture-p2-stale-assertions-reconciliation - Reconcile Overtaken DCL Assertion Backlog Item (corrected resolution method)

revision_reason: Responds to NO-GO at bridge/gtkb-architecture-p2-stale-assertions-reconciliation-006.md. The GO'd method (`gt backlog resolve`) cannot execute because the work item carries a non-canonical `stage` value (`ready_for_implementation`) that is absent from the SPEC-1602 transition model, so the hardcoded `stage='resolved'` transition is rejected with an empty valid-transition set. This revision keeps the same scope (`groundtruth.db`, work-item status promotion) and changes only the resolution command to a status-only promotion that achieves the authoritative GOV-STANDING-BACKLOG-001 goal without the blocked stage transition. The residual non-canonical stage value and the underlying lifecycle-model defect are disclosed and routed to a recommended separate follow-up thread.

bridge_kind: prime_proposal
Document: gtkb-architecture-p2-stale-assertions-reconciliation
Version: 007
Author: Claude Prime Builder (dispatched bridge worker)
Date: 2026-06-13T09:50:00Z

author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: 43e4844f-22a9-4052-abb3-a45f25e61723
author_model: Claude Opus 4.8
author_model_version: 4.8
author_model_configuration: Claude Code dispatched bridge auto-dispatch worker; resolved role prime-builder (pb); 1M context

Project Authorization: PAUTH-PROJECT-ARCHITECTURE-IMPROVEMENT-P2-STALE-ASSERTIONS-RECONCILIATION
Project: PROJECT-ARCHITECTURE-IMPROVEMENT
Work Item: WORKLIST-ARCHITECTURE-IMPROVEMENT-P2-STALE-ASSERTIONS

target_paths: ["groundtruth.db"]

implementation_scope: governance
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

This proposal still reconciles the open P2 architecture-improvement work item `WORKLIST-ARCHITECTURE-IMPROVEMENT-P2-STALE-ASSERTIONS`. The substantive reconciliation finding is unchanged and already GO-confirmed at `-004`: live MemBase shows `DCL-STANDING-BACKLOG-DB-SCHEMA-001` is at v4, status `verified`, with `assertions = NULL`, so the work item's stated concern (a verified spec with 4/10 passing assertions) is overtaken by current state; the stale assertion runs belong to historical v1 evidence targeting the abandoned `backlog_items` design.

The `-005` implementation attempt was correctly blocked and the `-006` verification correctly NO-GO'd it. Root cause:

- The work item was created (version 1, by Loyal Opposition Antigravity, 2026-06-10) directly with `stage = "ready_for_implementation"`. Initial `insert_work_item` does not validate the stage vocabulary; only transitions do.
- `ready_for_implementation` is **not** a canonical SPEC-1602 stage. It appears nowhere in `_VALID_STAGE_TRANSITIONS` (`groundtruth-kb/src/groundtruth_kb/db.py:4127`) nor in the CLI's `VALID_STAGES` (`groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py:124`).
- `gt backlog resolve` hardcodes `stage="resolved"` (`groundtruth-kb/src/groundtruth_kb/cli.py:2277-2278`). `_validate_stage_transition` then evaluates `_VALID_STAGE_TRANSITIONS.get("ready_for_implementation", set())` → empty set → every target stage is rejected. Hence the observed `Valid transitions from 'ready_for_implementation': []`.

The corrected method resolves the row via a **status-only promotion** (`gt backlog update --resolution-status resolved`, with no `--stage`). Because the stage is unchanged, `_validate_stage_transition` returns immediately on the same-stage no-op path (`db.py:4144`) and never reaches the unmapped-stage rejection. This is verified by dry-run below. Scope, target paths, allowed mutation class, and the non-mutation boundaries are all unchanged from the GO'd `-003`/`-004`: only `resolution_status` (status promotion) is changed on `groundtruth.db`; no source, test, specification, assertion, or spec-status mutation occurs.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — this revision enters the bridge as `REVISED`, waits for Loyal Opposition GO before implementation, and preserves `bridge/INDEX.md` as the canonical workflow state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal enumerates the governing specs for the intended work-item lifecycle mutation and the non-mutation boundaries.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — the header includes project authorization, project, work item, and inline JSON `target_paths`.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification is derived from the linked specs: PAUTH read-back, spec/assertion read-back, work-item read-back, dry-run guard probe, and bridge preflights.
- `GOV-STANDING-BACKLOG-001` — the standing backlog is the durable work authority; `resolution_status` is the authoritative open/closed signal, and the work item should not remain open when its acceptance condition has been superseded by current MemBase state.
- `SPEC-1602` — Work Item Lifecycle Stage Field. This proposal stays within the SPEC-1602 model by performing a same-stage no-op (it does not transition the unmapped `ready_for_implementation` stage). The model's inability to move an orphan stage to `resolved` — and the docstring-vs-implementation contradiction at `db.py:4342` (the docstring claims "Any stage can transition to 'resolved'" but the implementation does not permit it for unmapped stages) — is the underlying defect, disclosed in Risk / Follow-Up and routed to a separate thread.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — implementation is bounded by active PAUTH `PAUTH-PROJECT-ARCHITECTURE-IMPROVEMENT-P2-STALE-ASSERTIONS-RECONCILIATION`.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` — the PAUTH envelope allows `work_item_status_promotion` and forbids source/test/spec-assertion/spec-promotion changes. The status-only promotion is squarely within the allowed class; the recommended lifecycle-model source fix is explicitly out of this envelope.
- `DCL-STANDING-BACKLOG-DB-SCHEMA-001` — the live latest v4 row is the current authority for the schema pivot from `backlog_items` to `work_items`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — the decision and lifecycle mutation are preserved as durable linked artifacts instead of chat-only state.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — this work applies a lifecycle status transition to a backlog artifact after its source evidence is superseded/overtaken.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the owner directive, PAUTH, proposal, and eventual implementation report preserve the decision/action trail.

## Prior Deliberations

- `DELIB-20263159` — owner-decision evidence for the bounded architecture P2 reconciliation PAUTH (autonomous backlog directive, 3-minute anti-storm pacing, narrow out-of-scope list).
- `DELIB-S342-BACKLOG-WORK-ITEMS-CANONICAL-PIVOT` — owner directive establishing `work_items` as the canonical backlog source of truth and ratifying the pivot away from a separate `backlog_items` table.
- `DELIB-TAFE-BACKLOG-RECONCILIATION-PAUTH-20260612` — nearby governance precedent for bounded backlog reconciliation via PAUTH plus bridge GO, without source or spec mutation.
- A targeted `gt deliberations search` for "backlog stage transition resolve ready_for_implementation lifecycle" returned no matching records, so the lifecycle-transition-model defect surfaced here is not yet captured in the Deliberation Archive; the recommended follow-up thread (Risk / Follow-Up) should capture it.

## Owner Decisions / Input

Owner authorization is recorded in `DELIB-20263159`, created through `gt backlog authorize-implementation` from the owner directive:

> Continue: pick PB-actionable work from the bridge or backlog and work on it until it is handed off via the bridge protocol. Loop autonomously on this task until all bridge and backlog items have been completely implemented and VERIFIED if possible.

with the follow-up pacing constraint:

> Pause at the next good opportunity and insert a 3 minute timer between work projects to avoid storming the bridge.

**No new owner decision is required for this revision.** The corrected method stays inside the existing PAUTH envelope (`work_item_status_promotion` on `groundtruth.db`); it changes only the command used to perform the already-authorized reconciliation, which is exactly what a `REVISED` re-review exists to approve. The separate lifecycle-model source fix recommended in Risk / Follow-Up is the only path that would require expanding the authorized scope to source changes; this proposal deliberately does **not** include that fix, so it raises no owner-decision gate here.

## Requirement Sufficiency

Existing requirements are sufficient. `GOV-STANDING-BACKLOG-001` governs the backlog row and establishes `resolution_status` as the authoritative open/closed signal; `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` govern the PAUTH envelope; `GOV-FILE-BRIDGE-AUTHORITY-001` governs the bridge workflow; `SPEC-1602` governs the lifecycle stage field; and `DCL-STANDING-BACKLOG-DB-SCHEMA-001` v4 is the current verified schema authority. No new or revised requirement is needed to resolve a backlog row whose evidence is overtaken by the latest verified spec state. (The lifecycle-model contradiction is a code defect against the existing SPEC-1602 contract, not a requirement gap; it is routed to a separate thread.)

## Proposed Implementation

If GO is granted:

1. Run `python scripts\implementation_authorization.py begin --bridge-id gtkb-architecture-p2-stale-assertions-reconciliation` and confirm the packet names the active PAUTH, project, work item, and `groundtruth.db` target.
2. Run the corrected status-only promotion (single `groundtruth.db` mutation, no `--stage`):

   ```text
   python -m groundtruth_kb.cli backlog update WORKLIST-ARCHITECTURE-IMPROVEMENT-P2-STALE-ASSERTIONS --resolution-status resolved --owner-approved --related-bridge-threads "[\"bridge/gtkb-architecture-p2-stale-assertions-reconciliation-007.md\"]" --status-detail "Resolved (status-only promotion) as overtaken by live DCL-STANDING-BACKLOG-DB-SCHEMA-001 v4: latest spec is verified with assertions=NULL; stale 4/10 assertion evidence is historical v1 runs against the abandoned backlog_items design. NOTE: stage field retains the non-canonical value 'ready_for_implementation' because gt backlog resolve cannot transition an unmapped stage; the lifecycle-model repair (SPEC-1602 / db.py:4342) is tracked as a separate follow-up thread." --change-reason "Resolve stale architecture-improvement P2 backlog row per bridge GO for gtkb-architecture-p2-stale-assertions-reconciliation; status-only promotion, no source, test, spec assertion, or spec status mutation." --json`
   ```

3. Read back the work item, PAUTH, spec row, and assertion-run evidence.
4. File a post-implementation report through the bridge helper and wait for Loyal Opposition verification.

## Specification-Derived Verification Plan

| Specification / Contract | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-architecture-p2-stale-assertions-reconciliation --format json` shows the bridge thread in `bridge/INDEX.md` with no drift. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-architecture-p2-stale-assertions-reconciliation --json` returns `preflight_passed: true` and `missing_required_specs: []`. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Phantom-spec sweep over every cited `GOV-*`/`DCL-*`/`SPEC-*` id returns existing live specification rows. |
| `SPEC-1602` | Dry-run probe confirms the status-only update is a same-stage no-op that passes `_validate_stage_transition` (see Current Evidence Snapshot); the unmapped stage is not transitioned, so the SPEC-1602 model is not violated. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | `python -m groundtruth_kb.cli projects authorizations PROJECT-ARCHITECTURE-IMPROVEMENT --json` shows active PAUTH with included work item, allowed `work_item_status_promotion`, and forbidden source/test/spec mutations. |
| `DCL-STANDING-BACKLOG-DB-SCHEMA-001` | `python -m groundtruth_kb.cli assert --spec DCL-STANDING-BACKLOG-DB-SCHEMA-001` reports `With assertions: 0` / `Skipped (no def): 1`, confirming no active failing assertions to update. |
| `GOV-STANDING-BACKLOG-001` | Before implementation, `python -m groundtruth_kb.cli backlog show WORKLIST-ARCHITECTURE-IMPROVEMENT-P2-STALE-ASSERTIONS --json` shows `resolution_status: open`; after GO implementation it shows `resolution_status: resolved` with the status detail citing the v4/overtaken evidence and the stage residual. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report includes all commands above plus the implementation-start packet and the exact backlog mutation command/read-back output. |

No `python -m pytest` target applies because this proposal forbids source edits, test edits, and spec-assertion backfill. Verification is command/read-back based against MemBase and the bridge helpers, consistent with the previously GO'd verification approach for this thread.

## Current Evidence Snapshot

- Non-mutating dry-run of the corrected method confirms the guard path is clear:

  ```text
  GTKB_HARNESS_NAME=claude python -m groundtruth_kb.cli backlog update WORKLIST-ARCHITECTURE-IMPROVEMENT-P2-STALE-ASSERTIONS --resolution-status resolved --status-detail "dry-run probe" --change-reason "..." --owner-approved --dry-run --json
  -> {"dry_run": true, "fields": {"resolution_status": "resolved", "status_detail": "dry-run probe"}, "updated": false, "work_item_id": "WORKLIST-ARCHITECTURE-IMPROVEMENT-P2-STALE-ASSERTIONS"}
  ```

  No `Invalid stage transition` error is raised because no `--stage` is supplied, so `new_stage == current_stage` and `_validate_stage_transition` returns on the same-stage no-op path.
- `backlog show` confirms the work item is still `resolution_status: open`, `stage: ready_for_implementation`, version 1, origin `architecture_audit`.
- Governance no-op confirmation: the only `pre_resolve_work_item` gate (`groundtruth-kb/src/groundtruth_kb/gates.py:95-106`) early-returns for any origin outside `{defect, regression}`. This work item's origin is `architecture_audit`, so the status-only path bypasses no material governance — it is side-effect-equivalent to a normal resolve for this row.
- This is a single-work-item reconciliation, **not a bulk operation**: the work item inventory is exactly `["WORKLIST-ARCHITECTURE-IMPROVEMENT-P2-STALE-ASSERTIONS"]` in the active PAUTH `included_work_item_ids`. Because no bulk operation is performed, no separate bulk review packet or Phase/Path-deferred decision marker is required under `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS`; the bounded single-item inventory plus the active owner-approval PAUTH (`DELIB-20263159`, with formal-artifact-approval packet `.groundtruth/formal-artifact-approvals/2026-06-13-DELIB-20263159.json`) is the visibility evidence for this row.

## Risk / Follow-Up

Residual disclosed honestly: after this status-only resolution, the work item is closed (`resolution_status: resolved`) but its `stage` field retains the non-canonical value `ready_for_implementation`. For a closed row this is cosmetic and bypasses no material gate (see Current Evidence Snapshot), but it is a real latent inconsistency.

Underlying defect (out of this PAUTH's scope, recommended separate thread): the lifecycle-transition model contradicts its own documented contract. `db.py:4342` states "Any stage can transition to 'resolved' (early closure)", but `_VALID_STAGE_TRANSITIONS` only maps the five canonical stages, so an orphan/non-canonical stage can never reach `resolved`. A clean repair would (a) make `_validate_stage_transition` honor the documented universal early-closure-to-`resolved` rule (or otherwise recover orphan stages), and (b) optionally tighten `insert_work_item` to reject non-canonical stage values at creation so this class of orphan row cannot recur. That repair is a cross-cutting source change to `groundtruth-kb/src/groundtruth_kb/db.py` (and `cli_backlog_update.py` `VALID_STAGES`), with SPEC-1602 linkage and spec-derived tests. It is explicitly forbidden by this thread's PAUTH envelope (`DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`, source changes forbidden) and therefore must be authorized and pursued under its own owner-authorized project/PAUTH and bridge thread. This proposal recommends, but does not create, that follow-up work item, to stay inside the bounded reconciliation scope.

Rollback is append-only: run `gt backlog update` to append a new version reopening the work item with a status detail explaining the re-evaluation, or file a new work item explicitly scoped to the lifecycle-model repair.

## Recommended Commit Type

`chore`: the eventual implementation is a governed backlog-status reconciliation only (single `resolution_status` promotion on `groundtruth.db`), with no source/test behavior change.

## Bridge Filing (INDEX-Canonical)

This proposal is filed as `bridge/gtkb-architecture-p2-stale-assertions-reconciliation-007.md` with an append-only `REVISED` entry inserted at the top of the document's version list in `bridge/INDEX.md`; no prior version is deleted or rewritten. `bridge/INDEX.md` remains the canonical workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
