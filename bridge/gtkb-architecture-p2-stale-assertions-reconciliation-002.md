REVISED

# gtkb-architecture-p2-stale-assertions-reconciliation - Reconcile Overtaken DCL Assertion Backlog Item

revision_reason: Self-revision before Loyal Opposition review. The filed NEW passed the applicability preflight but the mandatory clause preflight wanted exact `Specification-Derived Verification` wording and explicit single-item backlog approval evidence. This REVISED version preserves the same scope and adds the missing evidence tokens without changing the proposed implementation.

bridge_kind: prime_proposal
Document: gtkb-architecture-p2-stale-assertions-reconciliation
Version: 002
Author: Codex Prime Builder
Date: 2026-06-13T06:24:00Z

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: current Codex desktop session
author_model: GPT-5
author_model_version: 2026-06 runtime
author_model_configuration: Codex desktop, danger-full-access, approval policy never

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

This proposal reconciles the open P2 architecture-improvement work item whose description says `DCL-STANDING-BACKLOG-DB-SCHEMA-001` is verified while only 4/10 assertions pass. Live MemBase evidence now shows that claim is stale: the latest version of `DCL-STANDING-BACKLOG-DB-SCHEMA-001` is v4, status `verified`, and its `assertions` field is `NULL`. The stale 4/10 result belongs to historical v1 assertion runs targeting the abandoned `backlog_items` design.

After Loyal Opposition GO, implementation is limited to resolving `WORKLIST-ARCHITECTURE-IMPROVEMENT-P2-STALE-ASSERTIONS` as overtaken by the verified v4 design-pivot record. No source files, tests, specification rows, assertion definitions, or spec statuses will be changed.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this work enters the bridge as `NEW`, waits for Loyal Opposition GO before implementation, and preserves `bridge/INDEX.md` as the canonical workflow state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal enumerates the governing specs for the intended work-item lifecycle mutation and the non-mutation boundaries.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the header includes project authorization, project, work item, and inline JSON `target_paths`.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification is derived from the linked specs: PAUTH read-back, spec/assertion read-back, work-item read-back, and bridge preflights.
- `GOV-STANDING-BACKLOG-001` - the standing backlog is the durable work authority; the work item should not remain open when its acceptance condition has been superseded by current MemBase state.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation is bounded by active PAUTH `PAUTH-PROJECT-ARCHITECTURE-IMPROVEMENT-P2-STALE-ASSERTIONS-RECONCILIATION`.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - the PAUTH envelope explicitly allows only `work_item_status_promotion` and forbids source/test/spec-assertion/spec-promotion changes.
- `DCL-STANDING-BACKLOG-DB-SCHEMA-001` - the live latest v4 row is the current authority for the schema pivot from `backlog_items` to `work_items`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the decision and proposed lifecycle mutation are preserved as durable linked artifacts instead of chat-only state.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - this work applies a lifecycle transition to a backlog artifact after its source evidence is superseded/overtaken.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the owner directive, PAUTH, proposal, and eventual implementation report preserve the decision/action trail.

## Prior Deliberations

- `DELIB-20263159` - owner-decision evidence for the bounded architecture P2 reconciliation PAUTH. It records the autonomous backlog directive, the 3-minute anti-storm pacing constraint, and the narrow out-of-scope list.
- `DELIB-S342-BACKLOG-WORK-ITEMS-CANONICAL-PIVOT` - owner directive establishing `work_items` as the canonical backlog source of truth and ratifying the pivot away from a separate `backlog_items` table.
- `DELIB-TAFE-BACKLOG-RECONCILIATION-PAUTH-20260612` - nearby governance precedent for bounded backlog reconciliation via PAUTH plus bridge GO, without source or spec mutation.

## Owner Decisions / Input

Owner authorization is recorded in `DELIB-20263159`, created through `gt backlog authorize-implementation` from the current owner directive:

> Continue: pick PB-actionable work from the bridge or backlog and work on it until it is handed off via the bridge protocol. Loop autonomously on this task until all bridge and backlog items have been completely implemented and VERIFIED if possible.

The same record captures the follow-up pacing constraint:

> Pause at the next good opportunity and insert a 3 minute timer between work projects to avoid storming the bridge.

The resulting PAUTH is active and bounded to this work item only.

## Requirement Sufficiency

Existing requirements are sufficient. `GOV-STANDING-BACKLOG-001` governs the backlog row, `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` govern the PAUTH envelope, `GOV-FILE-BRIDGE-AUTHORITY-001` governs the bridge workflow, and `DCL-STANDING-BACKLOG-DB-SCHEMA-001` v4 is the current verified schema authority. No new or revised requirement is needed to resolve a backlog row whose evidence is overtaken by the latest verified spec state.

## Proposed Implementation

If GO is granted:

1. Run `python scripts\implementation_authorization.py begin --bridge-id gtkb-architecture-p2-stale-assertions-reconciliation` and confirm the packet names the active PAUTH, project, work item, and target path.
2. Run `python -m groundtruth_kb.cli backlog resolve WORKLIST-ARCHITECTURE-IMPROVEMENT-P2-STALE-ASSERTIONS --owner-approved --related-bridge-threads "[\"bridge/gtkb-architecture-p2-stale-assertions-reconciliation-001.md\"]" --status-detail "Resolved as overtaken by live DCL-STANDING-BACKLOG-DB-SCHEMA-001 v4: latest spec is verified with no active assertions; stale 4/10 assertion evidence belongs to historical v1 runs targeting the abandoned backlog_items design." --change-reason "Resolve stale architecture-improvement P2 backlog row per bridge GO for gtkb-architecture-p2-stale-assertions-reconciliation; no source, test, spec assertion, or spec status mutation." --json`.
3. Read back the work item, PAUTH, spec row, and assertion-run evidence.
4. File a post-implementation report through the bridge helper and wait for Loyal Opposition verification.

## Specification-Derived Verification Plan

| Specification / Contract | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-architecture-p2-stale-assertions-reconciliation --repo-root . --format json` shows the bridge thread in `bridge/INDEX.md` with no drift. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-architecture-p2-stale-assertions-reconciliation --json` returns `preflight_passed: true` and `missing_required_specs: []`. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Phantom-spec sweep over every cited `GOV-*`/`DCL-*` id returns existing live specification rows. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | `python -m groundtruth_kb.cli projects authorizations PROJECT-ARCHITECTURE-IMPROVEMENT --json` shows active PAUTH `PAUTH-PROJECT-ARCHITECTURE-IMPROVEMENT-P2-STALE-ASSERTIONS-RECONCILIATION`, included work item, included specs, allowed `work_item_status_promotion`, and forbidden source/test/spec mutations. |
| `DCL-STANDING-BACKLOG-DB-SCHEMA-001` | SQLite read-back shows latest v4 status `verified` and `assertions IS NULL`; `python -m groundtruth_kb.cli assert --spec DCL-STANDING-BACKLOG-DB-SCHEMA-001` reports `With assertions: 0` and `Skipped (no def): 1`, confirming there are no active failing assertions to update. |
| `GOV-STANDING-BACKLOG-001` | Before implementation, `python -m groundtruth_kb.cli backlog show WORKLIST-ARCHITECTURE-IMPROVEMENT-P2-STALE-ASSERTIONS --json` shows `resolution_status: open`; after GO implementation, it should show `resolution_status: resolved`, `stage: resolved`, and status detail citing the v4/overtaken evidence. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report includes all commands above plus the implementation-start packet and the exact backlog mutation command/read-back output. |

No `python -m pytest` target applies because this proposal forbids source edits, test edits, and spec assertion backfill. Verification is command/read-back based against MemBase and the bridge helpers.

## Current Evidence Snapshot

- `python -m groundtruth_kb.cli assert --spec DCL-STANDING-BACKLOG-DB-SCHEMA-001` returned: total specs 1, with assertions 0, passed 0, failed 0, skipped 1.
- SQLite read-back showed `DCL-STANDING-BACKLOG-DB-SCHEMA-001` v4 has status `verified` and `assertions: null`.
- SQLite read-back showed the latest assertion-run evidence for this spec is historical `spec_version: 1`, with six failures targeting v1 `backlog_items` surfaces and four passes on fields that still exist in the `work_items` design.
- `gt backlog authorize-implementation` created `DELIB-20263159` and active PAUTH `PAUTH-PROJECT-ARCHITECTURE-IMPROVEMENT-P2-STALE-ASSERTIONS-RECONCILIATION` at `2026-06-13T06:22:41+00:00`.
- The PAUTH path also wrote formal-artifact-approval packet `.groundtruth/formal-artifact-approvals/2026-06-13-DELIB-20263159.json`, with `full_content_sha256: a2cc8ccf1797a7e7866d7cee449466c3b8a18b599eb6f9ecc26e85749a8b9b48`.
- This is a single-work-item reconciliation, not a bulk operation: the work item inventory is exactly `["WORKLIST-ARCHITECTURE-IMPROVEMENT-P2-STALE-ASSERTIONS"]` in the active PAUTH `included_work_item_ids`.

## Risk / Rollback

Risk is low but governance-visible: resolving the row too aggressively could hide a real desire to add v4 assertions in the future. Mitigation: this proposal does not delete the historical spec version or assertion runs; it only resolves the stale work item based on current v4 state. Rollback is append-only: run `gt backlog update` to append a new version reopening the work item with a status detail explaining the re-evaluation, or file a new work item explicitly scoped to adding v4 assertions if Loyal Opposition or the owner wants that separate improvement.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted at the top of the `gtkb-architecture-p2-stale-assertions-reconciliation` document list in `bridge/INDEX.md`; no prior version is deleted or rewritten (append-only). `bridge/INDEX.md` remains the canonical workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Recommended Commit Type

`chore`: the eventual implementation is a governed backlog-status reconciliation only, with no source/test behavior change.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
