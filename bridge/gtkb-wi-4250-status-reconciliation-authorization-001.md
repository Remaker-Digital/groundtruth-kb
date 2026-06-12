NEW

# gtkb-wi-4250-status-reconciliation-authorization — Create the narrow PAUTH needed to reconcile WI-4250 stale status

bridge_kind: governance_advisory
Document: gtkb-wi-4250-status-reconciliation-authorization
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-12 UTC

author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: hygiene-sweep-automation-2026-06-12
author_model: GPT-5 Codex coding agent
author_model_version: GPT-5 family; exact runtime build not exposed in session context
author_model_configuration: Codex desktop session; workspace-write; approval_policy=never

Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Work Item: WI-4250

target_paths: ["groundtruth.db", ".groundtruth/formal-artifact-approvals/**"]

---

## Summary

This governance pre-step creates the missing authorization surface needed to finish `WI-4250` cleanly. The stale-row defect is real: `WI-4250` remains `open` / `backlogged` even though its implementation scope already landed and was independently VERIFIED by the two hygiene CLI UTF-8/portability slices. The first direct reconciliation proposal (`gtkb-wi-4250-backlog-reconciliation-001.md`) correctly identified the contradiction but could not receive GO because no active PAUTH currently authorizes the required `work_item_status_promotion` mutation for `WI-4250`.

The scope of this thread is governance-only. It does NOT reconcile `WI-4250` yet. It requests Loyal Opposition review of the narrow PAUTH-creation plan that will authorize a subsequent single-row status/linkage reconciliation thread for `WI-4250`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — the authorization creation must be reviewed and tracked through the canonical bridge flow.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this governance pre-step still carries explicit governing spec linkage and target paths before any later KB mutation thread is filed.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the later PAUTH-creation implementation report must provide concrete command evidence for the deliberation and authorization records it claims.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — this thread exists to create the missing project authorization envelope for the later status-reconciliation implementation.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` — the planned PAUTH must make the allowed mutation class and included work item explicit.
- `GOV-ARTIFACT-APPROVAL-001` — the deliberation and PAUTH inserts will require formal-artifact approval packets in the follow-on implementation thread.
- `GOV-STANDING-BACKLOG-001` — `WI-4250` is a durable backlog artifact whose terminal state must be reconciled through governed lifecycle updates.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the verified implementation evidence and the backlog lifecycle repair must be connected through durable governed artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — the authorization record, follow-on reconciliation thread, and final WI closure should form one durable artifact chain.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — this thread advances `WI-4250` from blocked-by-missing-authorization to implementation-authorized for the specific status-reconciliation mutation.

## Prior Deliberations

- `bridge/gtkb-wi-4250-backlog-reconciliation-002.md` — Loyal Opposition NO-GO that precisely identified the authorization gap blocking direct reconciliation.
- `bridge/gtkb-hygiene-cli-utf8-portability-slice-1-004.md` — verified implementation evidence for the first half of `WI-4250`.
- `bridge/gtkb-hygiene-cli-utf8-portability-slice-2-guidance-005.md` — verified implementation evidence completing the remaining `WI-4250` scope.
- `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-STALE-STATUS-RECONCILIATION` — adjacent pattern showing that stale-status reconciliation work uses `work_item_status_promotion` authorization, but its included work items do not cover `WI-4250`.
- `_No exact Deliberation Archive hits surfaced for the literal query "WI-4250 status reconciliation authorization" on 2026-06-12; this proposal is driven by the live NO-GO plus the verified child-thread evidence._`

## Owner Decisions / Input

Owner directive on 2026-06-12: "Please proceed with the cleanup plan and WI-4250 and WI-4251." This proposal still anticipates the normal formal-artifact approval packets for the deliberation and PAUTH records before those KB inserts occur. No additional product-scope decision is required before Loyal Opposition review of this governance pre-step.

## Proposed Authorization Shape

The follow-on implementation thread should create one narrow PAUTH for `PROJECT-GTKB-DETERMINISTIC-SERVICES-001` scoped to `WI-4250` only with:

- allowed mutation class: `work_item_status_promotion`
- included work item ids: `["WI-4250"]`
- scope summary: reconcile the single `WI-4250` backlog row to already-VERIFIED child-thread evidence using `gt backlog resolve/update`
- forbidden operations: source edits, test edits, CLI extension, spec promotion, deploy, force-push

## Specification-Derived Verification Plan

| Specification | Verification command or artifact | Expected result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-wi-4250-status-reconciliation-authorization --format json --preview-lines 120` | Thread files and `bridge/INDEX.md` agree; no drift. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Future implementation report: `python -m groundtruth_kb projects authorizations PROJECT-GTKB-DETERMINISTIC-SERVICES-001 --json` | New PAUTH exists for `WI-4250` with `work_item_status_promotion` scope only. |
| `GOV-ARTIFACT-APPROVAL-001` | Future implementation report inspects the two approval packets under `.groundtruth/formal-artifact-approvals/`. | Both packets exist and were approved before KB insertion. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Future implementation report carries the exact commands and observed results above. | Verification evidence is concrete and replayable. |

## Review Questions

1. Is a WI-specific `work_item_status_promotion` PAUTH the correct narrow authorization shape for this stale-row reconciliation?
2. Should the later implementation thread cite this new PAUTH directly, or should `WI-4250` instead be added to the existing deterministic-services stale-status batch authorization?
3. Is any additional governing specification required before the PAUTH-creation implementation thread is filed?

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted into the `gtkb-wi-4250-status-reconciliation-authorization` document list in `bridge/INDEX.md`; no prior version is deleted or rewritten. `bridge/INDEX.md` remains the canonical workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Recommended Commit Type

`docs` — this thread scopes a governance pre-step only.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
