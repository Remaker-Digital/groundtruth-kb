REVISED

# Implementation Proposal - Legacy GOV WI Cleanup / Disposition Record (GTKB-GOV-CODE-QUALITY-BASELINE / GTKB-GOV-DA-ENFORCEMENT / GTKB-GOV-004)

bridge_kind: implementation_proposal
Document: gtkb-legacy-gov-wi-cleanup
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S353+

Project Authorization: PAUTH-PROJECT-GTKB-GOVERNANCE-HARDENING-GOVERNANCE-HARDENING-BATCH
Project: PROJECT-GTKB-GOVERNANCE-HARDENING
Work Item: GTKB-GOV-CODE-QUALITY-BASELINE

target_paths: []

This REVISED proposal triages three GTKB-GOV-* work items — GTKB-GOV-CODE-QUALITY-BASELINE, GTKB-GOV-DA-ENFORCEMENT, GTKB-GOV-004 — that an earlier draft mistakenly framed as vestigial placeholders. `-003` revises `-001` after the `-002` NO-GO. Live MemBase and prior bridge evidence show **all three work items are active**; the correct disposition for every one of them is **keep open**. Because no work item is retired or reframed, this proposal performs **no `groundtruth.db` mutation**: its output is the evidence-backed disposition record below, captured in this bridge thread.

## Revision Notes

The `-002` NO-GO raised three findings (F1, F2 blocking; F3 P2). Each is addressed below.

- F1 (P1 / blocking — `GTKB-GOV-CODE-QUALITY-BASELINE` is not a vestigial placeholder): confirmed. A live MemBase read shows `GTKB-GOV-CODE-QUALITY-BASELINE` is `open`, `backlogged`, carries a substantive description ("Defines a default code-quality checklist (CQ-* rule IDs)..."; "Slice 1 governance design filed at `bridge/gtkb-gov-code-quality-baseline-slice1-001.md`; awaits Codex GO"), and its `related_bridge_threads` field cites `bridge/gtkb-gov-code-quality-baseline-slice1-001.md`. Live `bridge/INDEX.md` shows the `gtkb-gov-code-quality-baseline-slice1` thread at latest status `GO` (`-006`). The placeholder/retire framing is dropped. `-003`'s disposition for this WI is **keep open as an active work item** with an active prior GO trail (see `## Per-Work-Item Dispositions`).
- F2 (P1 / blocking — `GTKB-GOV-DA-ENFORCEMENT` disposition is conditional and under-specified): confirmed. A live MemBase read shows `GTKB-GOV-DA-ENFORCEMENT` is `open`, `backlogged`, `status_detail` = "passive tracking; root-boundary reconciliation required". Prior bridge evidence `bridge/gtkb-gov-da-enforcement-slice1-010.md` is `VERIFIED` and its Required Action says to keep `GTKB-GOV-DA-ENFORCEMENT` in passive tracking until the upstream `gtkb-da-governance-completeness-implementation` thread reaches `VERIFIED`. The implementation-time `resolved`/`wont_fix` choice is removed. `-003`'s disposition for this WI is a concrete, evidence-backed **keep open in passive tracking** (see `## Per-Work-Item Dispositions`).
- F3 (P2 — project-authorization framing does not match the proposed mutation class): confirmed. The cited authorization `PAUTH-PROJECT-GTKB-GOVERNANCE-HARDENING-GOVERNANCE-HARDENING-BATCH` has `allowed_mutation_classes` = `hook_upgrade`, `cli_extension`, `test_addition`, `spec_status_promotion` — none of which is a work-item / backlog data mutation. `-003` resolves the mismatch **at its root**: because all three dispositions are "keep open" and the proposal no longer retires, resolves, reframes, or renames any work item, the proposal performs **no `groundtruth.db` mutation at all**. `target_paths` is therefore `[]` (empty). With no mutation, there is no mutation class to reconcile — the disposition is recorded in this bridge thread as a durable artifact, which is itself the deliverable. The `## Specification Links` section additionally cites the three project-authorization governing specs (`GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`) per the NO-GO's recommended action, and `## Authorization Reconciliation` explains why the current envelope suffices for a no-mutation disposition record.

## Claim

The three named GTKB-GOV-* work items are **not** vestigial placeholders. Live MemBase and prior bridge evidence show each is an active, meaningful work item. The correct disposition for all three is **keep open**, each with a concrete evidence-backed rationale. This proposal records those dispositions; it does not mutate `groundtruth.db`. No work item is retired, resolved, reframed, or renamed by this proposal.

## Per-Work-Item Dispositions

Each disposition cites live MemBase state and prior bridge evidence. The chosen state for every work item is a concrete, non-conditional **keep open**.

### IP-1: GTKB-GOV-CODE-QUALITY-BASELINE — KEEP OPEN (active, prior GO trail)

- Live MemBase: `id=GTKB-GOV-CODE-QUALITY-BASELINE`, version 1, `resolution_status=open`, `stage=backlogged`, `origin=hygiene`, `component=backlog`. `related_spec_ids_at_creation=["GOV-CODE-QUALITY-BASELINE"]`. `related_bridge_threads=["bridge/gtkb-gov-code-quality-baseline-slice1-001.md"]`.
- Description (substantive, not empty): "Defines a default code-quality checklist (CQ-* rule IDs) applying to all GT-KB adopter project proposals..."; status note "scoping in flight; root-contained routing required"; "Slice 1 governance design filed at `bridge/gtkb-gov-code-quality-baseline-slice1-001.md`; awaits Codex GO."
- Prior bridge evidence: `bridge/INDEX.md` records the `gtkb-gov-code-quality-baseline-slice1` thread at latest status `GO` (`bridge/gtkb-gov-code-quality-baseline-slice1-006.md`); that GO approves the revised Slice 1 governance design to proceed to a Slice 2 implementation proposal.
- **Chosen disposition state: keep `open` (no change).** This work item has an active design thread with a current Codex GO. Retiring or resolving it would erase real governance work. The next step for this WI is the owner-/Prime-directed filing of its Slice 2 implementation proposal under the `gtkb-gov-code-quality-baseline-slice1` thread family; that is out of scope here. This proposal makes no mutation to this WI.

### IP-2: GTKB-GOV-DA-ENFORCEMENT — KEEP OPEN (passive tracking, pending upstream VERIFIED)

- Live MemBase: `id=GTKB-GOV-DA-ENFORCEMENT`, version 1, `resolution_status=open`, `stage=backlogged`, `origin=hygiene`, `component=backlog`. `status_detail` = "passive tracking; root-boundary reconciliation required". `related_spec_ids_at_creation=["GOV-DA-ENFORCEMENT"]`.
- Description: "passive tracking; root-boundary reconciliation required"; "Previously described as owned by an external `groundtruth-kb` main. Owner root-boundary directive now requires the active GT-KB source of truth to be in `E:\GT-KB`. Next step: Reconcile tracking to an in-root GT-KB artifact/source path before further action."
- Prior bridge evidence: `bridge/gtkb-gov-da-enforcement-slice1-010.md` is `VERIFIED`; its Required Action 2 says "Keep `GTKB-GOV-DA-ENFORCEMENT` in passive tracking until upstream `gtkb-da-governance-completeness-implementation` reaches `VERIFIED`."
- **Chosen disposition state: keep `open` (no change).** The work item is correctly in passive tracking per a `VERIFIED` prior bridge decision; the passive-tracking exit condition (upstream `gtkb-da-governance-completeness-implementation` reaching `VERIFIED`) has not been shown satisfied, so the WI must not be retired. No fresh owner decision supersedes the passive-tracking contract. This proposal makes no mutation to this WI. (Note: the WI's description references a root-boundary reconciliation step; that reconciliation is a separate concern, not part of this disposition record, and would itself require its own authorized proposal if pursued.)

### IP-3: GTKB-GOV-004 — KEEP OPEN (active, reframed scope, TOP priority)

- Live MemBase: `id=GTKB-GOV-004`, version 2 (already reframed), `resolution_status=open`, `stage=backlogged`. Title: "Reconcile legacy MemBase work items into a high-quality unified backlog". Description marked "**Priority:** TOP" with a concrete reconciliation scope. `acceptance_summary` present. `status_detail` = "Reframed 2026-05-06 under unified backlog taxonomy...".
- **Chosen disposition state: keep `open` (no change).** GTKB-GOV-004 is already at version 2, already carries a clear reframed title and a TOP-priority reconciliation scope. The `-001` draft's proposed title rename ("reframe as GTKB-GOV-004-LEGACY-WI-RECONCILE") is unnecessary: the live v2 title is already descriptive, and renaming the WI id would break the `related_*` references that point at it. No mutation is needed or proposed.

### IP-4: No spec promotion, no `groundtruth.db` mutation

This proposal promotes no specification and mutates no `groundtruth.db` row. Its sole deliverable is the disposition record above, captured durably in this bridge thread.

## In-Root Placement Evidence

This proposal creates and modifies only bridge files under `E:\GT-KB\bridge\`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied. No path outside `E:\GT-KB` is created, read as a live dependency, or required. `target_paths` is empty because the proposal performs no implementation mutation.

## Specification Links

- `GOV-STANDING-BACKLOG-001` - backlog hygiene; the three work items are tracked standing-backlog items and this proposal records their dispositions.
- `GOV-ARTIFACT-APPROVAL-001` - formal-artifact-approval discipline; relevant because the project authorization this proposal cites was created under that discipline.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority governing this proposal as a bridge artifact and the disposition record as its deliverable.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root placement; all touched paths are in-root.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - cross-cutting; this proposal must cite every relevant governing specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - cross-cutting; the verification plan maps the disposition deliverable to verifiable checks.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs project-scoped implementation authorization; cited per the `-002` NO-GO F3 recommended action.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - defines the project-authorization envelope (allowed mutation classes, included work items); cited per F3. This proposal's no-mutation scope sits inside any envelope because it requests no mutation class.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - a project authorization does not bypass the bridge; cited per F3. This proposal honors it: it goes through the bridge for review and requests `GO` before any follow-on WI work.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - durable artifact-graph model; the disposition record is a durable artifact in the bridge graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - artifact lifecycle trigger discipline; this triage was triggered by the governance-hardening project scope.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - artifact-oriented governance baseline; the disposition is captured as a governed bridge artifact.
- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - owner-decision evidence for the project authorization covering the three work items.

## Authorization Reconciliation

The `-002` NO-GO F3 found that the cited authorization's `allowed_mutation_classes` (`hook_upgrade`, `cli_extension`, `test_addition`, `spec_status_promotion`) do not describe a work-item / backlog data mutation. `-003` resolves this at the root rather than by argument: the proposal no longer performs any work-item or backlog data mutation. The `-001` draft's `resolved` / `wont_fix` / title-rename operations are all removed, because the evidence-backed disposition for every one of the three work items is **keep open with no change**.

With no mutation requested, there is no mutation class to reconcile. The authorization is still cited for provenance (it is the active owner-approval envelope that placed the three work items under `PROJECT-GTKB-GOVERNANCE-HARDENING`, confirmed active in a live `current_project_authorizations` read, with all three work item IDs present in `included_work_item_ids`). A no-mutation disposition record is within the scope of any active authorization because it requests none of the envelope's gated mutation classes. If a future proposal does need to mutate one of these work items (for example, retiring `GTKB-GOV-DA-ENFORCEMENT` once its upstream passive-tracking condition is met), that future proposal must either obtain an authorization whose `allowed_mutation_classes` explicitly covers work-item / backlog data mutation, or carry an explicit owner decision for that mutation; this proposal does not pre-authorize it.

## Prior Deliberations

- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - batch-4 project authorization covering the three GTKB-GOV-* work items under `PROJECT-GTKB-GOVERNANCE-HARDENING`.
- `gtkb-gov-code-quality-baseline-slice1` bridge thread - the active design thread for `GTKB-GOV-CODE-QUALITY-BASELINE`; latest status `GO` at `bridge/gtkb-gov-code-quality-baseline-slice1-006.md`. Cited so the keep-open disposition for that WI is anchored to its active GO trail.
- `bridge/gtkb-gov-da-enforcement-slice1-010.md` - `VERIFIED` verdict that put `GTKB-GOV-DA-ENFORCEMENT` into passive tracking pending upstream `VERIFIED`. Cited so the keep-open-in-passive-tracking disposition is anchored to a `VERIFIED` prior decision.
- `DELIB-1117` / `DELIB-1133` - the `-002` NO-GO's deliberation search surfaced these as the prior `gtkb-gov-code-quality-baseline-slice1` (`GO`) and `gtkb-gov-da-enforcement-slice1` (`VERIFIED`) bridge-thread records; cited here to demonstrate the prior-decision history was consulted.

No prior deliberation supports treating the three work items as name-only placeholders; the `-001` draft's placeholder framing was the error this revision corrects.

## Owner Decisions / Input

This proposal depends on owner approval and is authorized by:

- 2026-05-14 UTC, S350+: owner approved the `GTKB-GOVERNANCE-HARDENING` project authorization (`DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS`), which includes all three GTKB-GOV-* work items. This triage operates within that authorized project scope.
- No new owner AskUserQuestion decision is required for `-003`. The revision corrects an evidence error (the three WIs are active, not placeholders) and removes all `groundtruth.db` mutation; the result is a no-mutation disposition record. Because nothing is retired, resolved, reframed, or renamed, no owner approval beyond the existing project authorization is needed. Any future *mutation* of these work items (e.g., a later retirement of `GTKB-GOV-DA-ENFORCEMENT`) would require its own owner decision; this proposal does not request it.

## Requirement Sufficiency

Existing requirements sufficient. The disposition of each work item is determined by live MemBase state and `VERIFIED` / `GO` prior bridge decisions, not by a new requirement. No new or revised requirement or specification is created by this work.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a disposition record for three named work items; it is **not** a bulk backlog operation. It performs no batch resolve, promote, or retire — in fact it performs no work-item mutation at all. Each of the three work items receives an individually evidenced disposition in `## Per-Work-Item Dispositions`. The three work items are members of `PROJECT-GTKB-GOVERNANCE-HARDENING` per the `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch4-four-project-authorizations.json`. References to "work item", "backlog", and "standing backlog" describe only these three named WIs. The review-packet inventory enumerates a per-WI rationale and the chosen (no-change) state for each.

## Bridge INDEX Maintenance

`bridge/INDEX.md` is the canonical bridge workflow state. This proposal adds a `REVISED` line to the existing `Document: gtkb-legacy-gov-wi-cleanup` entry, preserving the prior `NO-GO` and `NEW` lines (append-only audit trail). It does not edit, reorder, or remove any other `Document:` entry.

## Specification-Derived Verification Plan

This proposal's deliverable is a disposition record, not a code change, so verification confirms the record's accuracy against live MemBase rather than executing new unit tests. Each linked specification maps to a verification check below.

| Behavior / spec clause | Verification check | Covers |
|---|---|---|
| `GTKB-GOV-CODE-QUALITY-BASELINE` is `open` with an active GO trail; disposition is keep-open | Read live MemBase row and confirm `resolution_status=open`; read `bridge/INDEX.md` and confirm `gtkb-gov-code-quality-baseline-slice1` latest status is `GO` | GOV-STANDING-BACKLOG-001, GOV-FILE-BRIDGE-AUTHORITY-001 |
| `GTKB-GOV-DA-ENFORCEMENT` is `open` in passive tracking; disposition is keep-open | Read live MemBase row and confirm `resolution_status=open` and `status_detail` passive-tracking text; confirm `bridge/gtkb-gov-da-enforcement-slice1-010.md` is `VERIFIED` | GOV-STANDING-BACKLOG-001, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 |
| `GTKB-GOV-004` is `open`, version 2, already reframed; disposition is keep-open | Read live MemBase row and confirm `version=2`, `resolution_status=open`, descriptive title present | GOV-STANDING-BACKLOG-001 |
| Proposal performs no `groundtruth.db` mutation | Confirm `target_paths` is empty and no IP mutates a work-item row | DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 |
| Authorization is active and covers the three work items; no mutation class is requested | Read live `current_project_authorizations` and confirm the authorization is `active` with the three WI IDs in `included_work_item_ids` | GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001, DCL-PROJECT-AUTHORIZATION-ENVELOPE-001, PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001 |
| In-root placement | Confirm all touched paths are under `E:\GT-KB` | ADR-ISOLATION-APPLICATION-PLACEMENT-001 |

The verification checks above were already executed during the drafting of `-003` (the live MemBase reads and `bridge/INDEX.md` reads are the evidence cited in `## Per-Work-Item Dispositions` and `## Authorization Reconciliation`). Loyal Opposition can independently re-run them. DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 is satisfied for a no-code-change disposition record: every linked specification maps to a re-runnable verification check, and the disposition record stands or falls on those checks.

## Acceptance Criteria

- IP-1, IP-2, IP-3 each record an evidence-backed, concrete keep-open disposition; no work item is retired, resolved, reframed, or renamed.
- The proposal performs no `groundtruth.db` mutation; `target_paths` is empty.
- The three project-authorization governing specs are cited and the authorization mismatch from `-002` F3 is resolved (by removing all mutation).
- Both mandatory preflights pass for this proposal.
- The disposition record is captured durably in this bridge thread.

## Risks / Rollback

- Risk: a future session re-reads the `-001` placeholder framing and retires a live work item. Mitigation: `-003` records the evidence for keep-open explicitly; this superseding revision is the durable correction.
- Risk: the keep-open disposition for `GTKB-GOV-DA-ENFORCEMENT` leaves a long-lived passive-tracking item in the backlog. Mitigation: that is the correct state per a `VERIFIED` prior bridge decision; the exit condition (upstream `VERIFIED`) is documented so a future session knows when retirement becomes appropriate.
- Rollback: this proposal mutates no durable state, so there is nothing to roll back. Withdrawing the proposal would simply leave the three work items in their current (correct) `open` state.

## Recommended Commit Type

`docs` - this proposal and its disposition record are governance/bridge artifacts; no code, no `groundtruth.db` row, and no test is changed. The deliverable is the evidence-backed disposition record itself.

## Pre-Filing Preflight

Both mandatory pre-filing preflights were run on this proposal content; the observed output is embedded in the `## Applicability Preflight` and `## Clause Applicability` sections below.

## Applicability Preflight

```
## Applicability Preflight

- packet_hash: `sha256:2922485d61e083ab9da66435d536e584dc8bf8dacd94b5b151a8c0eb84e1b015`
- bridge_document_name: `gtkb-legacy-gov-wi-cleanup`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-legacy-gov-wi-cleanup-003.md`
- operative_file: `bridge/gtkb-legacy-gov-wi-cleanup-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

Result: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.

## Clause Applicability

```
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-legacy-gov-wi-cleanup`
- Operative file: `bridge\gtkb-legacy-gov-wi-cleanup-003.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |
```

Result: exit 0; must_apply 5/5 with evidence; blocking gaps: 0.
