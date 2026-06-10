NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 58f826b2-6551-47df-8edf-ceba6461be29
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: explanatory output style; interrogative-default Prime Builder

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3450

# Orphan-WI Membership Backfill — Slice 2 Scoping

bridge_kind: prime_proposal

Document: gtkb-orphan-wi-membership-backfill-slice-2-scoping
Version: 001 (NEW; scoping-only proposal for Slice 2 of the orphan-WI-membership workstream)
Date: 2026-05-29 UTC

## Summary

Scopes Slice 2 of the orphan-WI-membership workstream. Slice 1 (`gtkb-orphan-wi-membership-discovery-slice-1`, **VERIFIED** at `-012`) shipped a read-only discovery scanner (`scripts/discover_orphan_wi_memberships.py`) that inventories open work items with no active project membership and emits a structured report. Slice 1 explicitly deferred the **backfill mutation** to Slice 2. This proposal defines Slice 2's approach: drive a per-orphan, AUQ-gated resolution that assigns each orphan open work item to a named project (or records an owner-approved retire/exclude decision), so the standing rule "every work item belongs to a named project" holds.

**This is a SCOPING-only filing.** It requests Loyal Opposition approval of the Slice 2 approach. No source is mutated by this proposal. A follow-on Slice 2 *implementation* proposal will carry concrete `target_paths`, test specifications, and (if the AUQ volume warrants a dedicated home) a project/PAUTH confirmation.

## Problem Statement

The S373 backlog assessment (2026-05-29) Gap 6 recorded that the orphan-WI scanner Slice 2 was never filed. The discovery scanner found a large orphan class (Slice 1 evidence: `orphan_count=58`; the S373 deterministic query measured ~92 open orphans, dominated by a contiguous legacy block of `wont_fix` Agent Red pipeline-failure rows). Orphan open work items break the project→work-item traceability chain that the backlog-source-of-truth model depends on. The scanner is read-only by design; without Slice 2 the inventory never becomes resolution, and the orphan count drifts upward.

## Specification Links

- `SPEC-AUQ-POLICY-ENGINE-001` — Slice 1 preserved AUQ gating for Slice 2 (`Discovery did not require AUQ; Slice 2 will`). Slice 2's per-orphan resolution is the AUQ-gated mutation; AskUserQuestion is the only valid owner-decision channel.
- `GOV-STANDING-BACKLOG-001` — backlog is the unified known-work view; every work item belongs to the backlog under a project/sub-project grouping. Slice 2 restores membership for orphan work items. See § Clause Scope Clarification (Slice 2 is AUQ-gated per-orphan resolution, not a blind bulk mutation).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — Slice 1 triggered no lifecycle mutation; Slice 2 backfill does (membership creation / retire decisions), so it is lifecycle-trigger-governed.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all Slice 2 artifacts remain in-root within `E:\GT-KB`: the discovery report under `.gtkb-state/orphan-wi-discovery/`, the resolution driver under `scripts/`, and tests under `tests/`. No artifact is placed outside the platform root; no application-directory placement is involved (the orphan rows are GT-KB platform backlog items, not application files).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — this proposal carries the `Project Authorization:` / `Project:` / `Work Item:` triple; `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` is active and covers WI-3450 by active project membership.
- `GOV-ARTIFACT-APPROVAL-001` — unrecoverable orphans requiring retire-vs-assign decisions use formal-artifact-approval packets (carried from Slice 1's deferred-decision marker).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section is the satisfaction; all relevant cross-cutting specs are cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the follow-on Slice 2 implementation proposal will carry the spec-to-test mapping; scoping defines the verification approach (§ Verification Approach).
- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed under the canonical bridge protocol; `bridge/INDEX.md` is authoritative; this entry inserts the new version at the top of the thread version list with no deletion or rewrite of prior versions.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — orphan resolution is artifact-first: the discovery report is the inventory artifact; per-orphan AUQ answers and membership rows are durable artifacts.

## Prior Deliberations

- `gtkb-orphan-wi-membership-discovery-slice-1` (VERIFIED `-012`) — the predecessor slice; its `-003` (GO at `-004`) defined the discovery output contract and the explicit Slice-1=inventory / Slice-2=mutation boundary this proposal honors.
- `DELIB-S357-WI-3353-PAUTH-COMPLETION` — precedent for owner-decision over project-authorization completion (the unrecoverable-orphan retire/assign pattern Slice 2 reuses).
- `DELIB-S353-GRILL-SKILL-NEW-PROJECT-2026-05-15` — precedent for an owner-decision creating a new dedicated project for an orphan-like work item (a Slice 2 resolution option for orphans with no recoverable project).
- Deliberation Archive search for `orphan work item membership backfill` (run S364 2026-05-29) returned no prior Slice 2 design; this is the first Slice 2 scoping.

## Requirement Sufficiency

Existing requirements sufficient for scoping. `SPEC-AUQ-POLICY-ENGINE-001`, `GOV-STANDING-BACKLOG-001`, and the Slice 1 discovery contract fully constrain the Slice 2 approach. The follow-on implementation proposal will re-state Requirement Sufficiency for the concrete mutation code.

## Slice 2 Scope (proposed approach)

Slice 2 consumes the Slice 1 discovery report (`.gtkb-state/orphan-wi-discovery/<run-id>/report.json`; per-WI `recoverability_class`, `candidate_project_id`, `confidence_score`, `root_cause_changed_by`) and resolves each orphan:

1. **Re-run discovery first (idempotent).** Slice 2 begins by re-running the Slice 1 scanner to refresh the orphan set (the count drifts between slices; Slice 1 noted this and made discovery idempotent).
2. **Recoverable, high-confidence** (`recoverable_via_title_match` etc. with `confidence_score` >= a threshold the implementation proposal will fix): present a grouped AUQ confirming assignment to the `candidate_project_id`, then `gt projects add-item` per confirmed orphan. Grouping (not one-AUQ-per-orphan for an obvious batch) keeps owner burden bounded while preserving per-decision auditability.
3. **Recoverable, low-confidence**: per-orphan AUQ (the candidate is a guess; the owner picks the project or rejects).
4. **Unrecoverable** (no candidate project — e.g., the legacy `wont_fix` Agent Red pipeline rows): owner decides via AUQ among {assign-to-new-project, assign-to-existing, retire, exclude}. Retire/assign decisions that mutate canonical state use `GOV-ARTIFACT-APPROVAL-001` formal-artifact-approval packets, and may use a default-retire policy for sufficiently-old unrecoverable orphans **only** with explicit owner pre-approval evidence.
5. **Every resolution is a durable artifact**: a membership row (`gt projects add-item`) or an owner-approved retire/exclude record, each citing the AUQ/packet evidence.

The mutation surface is the deterministic `gt projects` CLI + (for retire decisions) the approval-packet pathway — no ad-hoc `db.insert_*`. This keeps Slice 2 inside the deterministic-services principle (`DELIB-S312`).

## Slice Boundaries

**In scope (Slice 2):** consuming the discovery report; per-orphan AUQ-gated resolution; membership assignment via `gt projects add-item`; owner-approved retire/exclude for unrecoverables; a re-runnable resolution driver.

**Out of scope (deferred):** repairing the originating code paths that created orphans (Slice 1's `root_cause_changed_by` attribution feeds a separate reliability work item); the broader backlog reconciliation initiative (tracked separately — Slice 2 resolves *membership* orphans only, not the full open-work-item reconciliation); concrete `target_paths` + test code (the follow-on implementation proposal).

## Verification Approach (to be realized in the implementation proposal)

- A test asserting the resolution driver reads the discovery report and produces a per-orphan resolution plan without mutating canonical state in dry-run mode.
- A test asserting `recoverable_high_confidence` orphans map to their `candidate_project_id`.
- A test asserting unrecoverable orphans require owner-decision evidence before any retire mutation (mirrors Slice 1's `test_unrecoverable_class_requires_owner_decision`).
- Re-run idempotency: resolving an already-membered work item is a no-op.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal mentions "standing backlog" and "work item" but is **not** a bulk-operation standing-backlog mutation. It is a SCOPING filing that mutates nothing. Slice 2 itself resolves orphans through **per-orphan / grouped owner AUQ** with formal-artifact-approval evidence for retire decisions — the clarifying evidence required by `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` is the Slice 1 discovery **inventory** artifact (`report.json`) plus per-orphan owner-decision **formal-artifact-approval** evidence. No blind bulk write occurs at any stage.

## Acceptance Criteria (for this scoping GO)

- [ ] Loyal Opposition agrees the Slice 2 approach (consume discovery report → AUQ-gated per-orphan resolution → deterministic CLI mutation + approval-packet retire) is sound and faithful to Slice 1's deferred contract.
- [ ] Specification linkage is complete; applicability + clause preflights pass.
- [ ] Approach keeps mutation inside deterministic services (`gt projects` CLI) and AUQ/approval-packet gating; no ad-hoc `db.insert_*`.
- [ ] Slice boundaries (membership resolution only; not the broader reconciliation; not root-cause repair) are accepted.

## Risk / Rollback

- **Risk:** owner-AUQ volume for ~92 orphans. Mitigation: grouped AUQ for high-confidence recoverables; default-retire policy (owner pre-approved) for sufficiently-old unrecoverables; the implementation proposal sizes the AUQ batching.
- **Risk:** project-fit — `PROJECT-GTKB-RELIABILITY-FIXES` is a small-fix fast-lane; the Slice 2 *implementation* may be substantial. Mitigation: the implementation proposal may propose a dedicated project/PAUTH for the backfill if the volume warrants; this scoping stays in the Slice 1 lineage.
- **Rollback:** scoping mutates nothing; rollback is withdrawing the proposal. Slice 2 implementation mutations are append-only membership rows / approval-gated retires, each reversible by a compensating owner-approved action.

## Owner Decisions / Input

- **Gap selection / approach** (AskUserQuestion, S364 2026-05-29): Owner chose "Gap 6 first: scope orphan-WI Slice 2 (Recommended)" — authorizing capture of the Slice 2 work item (WI-3450) and filing this scoping proposal. Gap 3 (skill CLI delegation, already GO-scoped under the skill-modernization umbrella) and Gap 7 (`work_list.md` drift, overlaps the broader reconciliation) were queued as follow-ups.
- No further owner decision is required to review this scoping proposal. Slice 2 *implementation* will collect per-orphan owner decisions via AskUserQuestion at execution time.

## Notes for Loyal Opposition

- This is AXIS-1 dispatchable scoping review; no owner input is needed to GO/NO-GO the approach.
- Scoping-only: no `target_paths`, no source mutation. The follow-on implementation proposal carries `target_paths` + tests + the implementation-start packet.
- **KB-mutation checkpoint confirmation:** this scoping proposal performs **no** `groundtruth.db` / MemBase mutation. It is design-only; `groundtruth.db` is intentionally absent from target_paths (there are no target_paths). The membership/retire mutation language describes what the *Slice 2 implementation* will do; that follow-on implementation proposal will declare `groundtruth.db` in its target_paths for the `gt projects add-item` membership writes and approval-gated retires.
- **Conventional commit type** (when the implementation eventually commits): `feat:` for a new resolution driver, or `fix:` if framed as orphan-traceability repair — the implementation proposal will declare it.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
