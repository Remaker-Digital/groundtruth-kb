NEW

bridge_kind: governance_review
Document: gtkb-dispatch-envelope-adr-specs
Version: 001
Project: PROJECT-GTKB-DISPATCH-ENVELOPES
Work Item: WI-4286
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-03 UTC
Reviewer: Loyal Opposition
Recommended commit type: docs

author_identity: Claude Code Prime Builder (interactive, session-stated PB via ::init gtkb pb)
author_harness_id: B
author_session_context_id: a47d634f-7804-4452-aff5-1ca018aeef3d
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI, explanatory output style

target_paths: [".groundtruth/formal-artifact-approvals/2026-06-03-adr-dispatch-envelope-architecture-001.json", ".groundtruth/formal-artifact-approvals/2026-06-03-dcl-dispatch-envelope-schema-001.json", ".groundtruth/formal-artifact-approvals/2026-06-03-spec-centralized-dispatch-service-001.json", ".groundtruth/formal-artifact-approvals/2026-06-03-spec-prime-project-completion-envelope-001.json", "groundtruth.db", "bridge/gtkb-dispatch-envelope-adr-specs-001.md", "bridge/INDEX.md", ".gtkb-state/**"]

implementation_scope: governance
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

# Dispatch-Envelope Architecture — ADR + DCL + 2 SPEC formalization

## Source / Owner Directive

Owner design discussion 2026-06-03 (this session) asked two feasibility
questions: (Q1) a centralized singleton dispatch service routing prompts to
selected harnesses/roles via time/calendar "ops/work/audit envelopes," and
(Q2) a Prime Builder "work envelope" process (select project -> fan out WIs ->
event-driven advance per verdict -> drive to VERIFIED-complete). After analysis
the owner selected, via AskUserQuestion, "Capture as ADR + specs" and then
"Approve all four; formalize via bridge." This proposal carries the four
owner-approved artifacts (full content below) for Loyal Opposition review under
the GOV-20 architecture-decision workflow and the GOV-ARTIFACT-APPROVAL-001
formal-artifact-approval discipline.

## Proposal Kind

`governance_review` — creates four NEW MemBase governance artifacts (1 ADR,
1 DCL, 2 SPECs). No source/runtime behavior change in this slice; service/code
implementation is a follow-on WI. Per GOV-ARTIFACT-APPROVAL-001 each artifact
is inserted only AFTER (a) this proposal reaches Codex GO and (b) a matching
per-artifact formal-artifact-approval packet exists; a CVR then proves
DCL-DISPATCH-ENVELOPE-SCHEMA-001 compliance.

## Requirement Sufficiency

New or revised requirement required before implementation. This proposal's
operative purpose is requirement/specification capture through the governed
approval path (GOV-20 + GOV-ARTIFACT-APPROVAL-001); it does NOT authorize
source/config/test implementation. The follow-on service implementation is a
separate WI gated by these artifacts.

## Specification Links

- GOV-ARTIFACT-APPROVAL-001 — per-artifact approval packets gate the four inserts.
- PB-ARTIFACT-APPROVAL-001 — formal-artifact-approval discipline.
- DCL-ARTIFACT-APPROVAL-HOOK-001 — approval-gate + evidence-checker contract.
- ADR-SINGLE-HARNESS-OPERATING-MODE-001 — existing dispatch topology this builds on.
- SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 — existing single-harness dispatcher behavior.
- ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 — dispatch-on-actionable mechanism precedent.
- DCL-SMART-POLLER-AUTO-TRIGGER-001 — auto-trigger contract precedent.
- DCL-PROJECT-AUTHORIZATION-ENVELOPE-001 — the "envelope" precedent this generalizes.
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 — PAUTH model used by the Prime work envelope.
- GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 — the VERIFIED-complete termination predicate.
- GOV-FILE-BRIDGE-AUTHORITY-001 — bridge protocol + INDEX canonicality for this proposal.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — spec-linkage compliance.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — spec-derived verification plan below.
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 — Project + Work Item cited above.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — all target_paths in-root.
- GOV-STANDING-BACKLOG-001 — WI-4286 / WI-4281 backlog linkage.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — artifact-oriented governance for the four new records.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — artifact-first development framing.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — artifact lifecycle triggers for ADR/DCL/SPEC creation.

## Prior Deliberations

- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE — repetitive AI plumbing is a defect; the strategic justification for envelope-shaped dispatch.
- WI-4281 (PROJECT-GTKB-DETERMINISTIC-SERVICES-001) — /loop multi-instance coordinator design; sibling prior art for the Q2 autonomous-loop primitive.
- ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 v2 + bridge-essential.md § Incident History (S308, 2026-04-25) — the blind-automation failure (~12.5M tokens/day work-without-information) that the activity-gate constraint (DCL assertion 2) exists to prevent.
- Existing dual dispatch substrates (cross-harness event-driven trigger; single-harness dispatcher) — the consolidation target.
- This session's owner AskUserQuestion answers (2026-06-03) — recorded under Owner Decisions / Input.

## Owner Decisions / Input

- AskUserQuestion 2026-06-03 (next step): "Capture as ADR + specs (Recommended)" — authorized recording the architecture as ADR + candidate specs through the formal-artifact path.
- AskUserQuestion 2026-06-03 (approve artifacts): "Approve all four; formalize via bridge" — approved ADR-DISPATCH-ENVELOPE-ARCHITECTURE-001 + DCL-DISPATCH-ENVELOPE-SCHEMA-001 + SPEC-CENTRALIZED-DISPATCH-SERVICE-001 + SPEC-PRIME-PROJECT-COMPLETION-ENVELOPE-001 as drafted, and directed formalization via one governance_review bridge proposal + per-artifact packets + insertion on GO, with a new project (PROJECT-GTKB-DISPATCH-ENVELOPES, created) linked to WI-4281.
- These AUQ answers are the owner-decision authority; per-artifact formal-artifact-approval packets remain required at insert time.

## Spec-Derived Verification Plan

This is a specification-derived verification (spec-to-test) plan for governance
artifact creation. Because the artifacts are governance records (no runtime
surface in this slice), verification is by artifact-evidence checks + DCL
assertion registration, not pytest of behavior; the follow-on service WI carries
pytest/ruff behavioral coverage.

| Artifact / clause | Verification (spec-to-test) | Command | Expected |
|---|---|---|---|
| All 4 inserts match approved content | per-artifact formal-artifact-approval packet sha256 matches inserted row | `check_narrative_artifact_evidence.py` / packet sha check | match |
| DCL-DISPATCH-ENVELOPE-SCHEMA-001 assertions | assertions registered + runnable | `gt assert` (architecture layer) | assertions present |
| DCL compliance of the inserted set | CVR document created proving the 5 schema assertions | CVR authored post-insert | CVR present |
| Bridge protocol | applicability + clause preflights on this operative file | `bridge_applicability_preflight.py` + `adr_dcl_clause_preflight.py` | preflight pass; exit 0 |
| In-root | all target_paths under E:\GT-KB | inspection | pass |

Note: a follow-on service-implementation WI will carry pytest + `ruff check` /
`ruff format --check` behavioral coverage of the dispatch service; that code is
out of scope for this governance-capture slice.

## Bridge INDEX Self-Check

Per GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL: this proposal is
filed under bridge/ and its bridge/INDEX.md entry is created by inserting a new
`Document: gtkb-dispatch-envelope-adr-specs` entry with `NEW:
bridge/gtkb-dispatch-envelope-adr-specs-001.md` at the top of the index entry
list; append-only, no prior entry deleted or rewritten. bridge/INDEX.md remains
the canonical workflow state.

## Out of Scope

- The dispatch SERVICE code, envelope MemBase table DDL, and scheduled-task
  wiring (follow-on implementation WI gated by these artifacts).
- Any change to the existing cross-harness trigger / single-harness dispatcher
  runtime (consolidation is a later slice).

## Risk / Rollback

Low: four governance-record inserts behind per-artifact approval packets +
Codex GO. No runtime/behavior change. Rollback = append terminal/superseded
versions to the four artifacts (append-only); the new project + WI-4286 remain
as capture. No source/config touched.

---

# PROPOSED ARTIFACT CONTENT (native review format; NOT yet inserted)

## Artifact 1 — ADR-DISPATCH-ENVELOPE-ARCHITECTURE-001 (type=architecture_decision)

**Status:** proposed.
**Context:** GT-KB has two bridge-dispatch substrates (cross-harness event-driven trigger; single-harness dispatcher), mutually exclusive at runtime and both bridge-INDEX-driven only. There is no path to dispatch a scheduled/calendar-based task or an arbitrary payload to a chosen {harness, role}. Recurring admin/review/audit work therefore falls on the owner or ad-hoc sessions, counter to operating-model.md §1 and DELIB-S312.
**Decision:** Introduce one centralized dispatch service plus a first-class envelope abstraction. An envelope is a MemBase record `{cadence, target (harness-id OR role), payload_ref, specialization_ref, authorization, activity_gate, expiry}`. The service resolves the target via harness-state/harness-registry.json (invocation_surfaces.headless.argv + `::init gtkb (pb|lo)`), enforces singleton dispatch via the existing dispatch-state/lock discipline, and fires envelopes on schedule only after an activity-gate self-check returns work-to-do.
**Alternatives considered (rejected):** (a) keep ad-hoc interactive dispatch — leaves recurring load on owner; (b) re-enable an interval OS poller — reintroduces the S308 blind-automation failure, forbidden by bridge-essential.md; (c) a third independent substrate — worsens existing dual-substrate complexity; this ADR consolidates instead; (d) mint new authority roles for specializations — the authority role set is closed (pb/lo; acting-prime-builder SET-rejected); specialization is a specialization_ref (skill/lane/subagent), not a new role.
**Consequences:** (+) recurring ops/review/audit become governed idempotent services; (+) consolidates two substrates toward one singleton; (-) reintroduces scheduled firing, which MUST be activity-gated to preserve the S308 lesson; (-) new MemBase schema + service code to maintain.
**Related:** ADR-SINGLE-HARNESS-OPERATING-MODE-001, SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001, ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 v2, DCL-PROJECT-AUTHORIZATION-ENVELOPE-001, DELIB-S312, WI-4281.

## Artifact 2 — DCL-DISPATCH-ENVELOPE-SCHEMA-001 (type=design_constraint; derived from ADR-DISPATCH-ENVELOPE-ARCHITECTURE-001)

Assertions (machine-checkable):
1. Every envelope record has exactly one target_harness_id OR one target_role, never both; a target_role is `prime-builder` or `loyal-opposition` (closed set).
2. Every envelope has a non-empty activity_gate — a deterministic read-only predicate run before spawning; a positive result is required to dispatch (S308 guard).
3. Every envelope carries an authorization reference (PAUTH or owner-decision DELIB); dispatch is refused if absent/expired.
4. specialization_ref, when present, names an existing skill / session-lane / subagent-type; it never substitutes for the authority role.
5. Dispatch is singleton per (envelope_id, fire_window): re-entrancy is blocked by the existing dispatch-state/lock path.

## Artifact 3 — SPEC-CENTRALIZED-DISPATCH-SERVICE-001 (type=specification)

**Requirement:** GT-KB shall provide one dispatch service that (a) resolves a {harness, role} target from the registry, (b) composes the spawn command from invocation_surfaces.headless.argv with {{PROMPT}}/{{PROJECT_ROOT}} + canonical init keyword, (c) consumes both event-driven (INDEX-delta) and schedule-driven (envelope) triggers, and (d) records every dispatch in the existing audit trail (dispatch-failures.jsonl, dispatch-state.json).
**Acceptance:** existing bridge dispatch behavior preserved byte-identically (signature scheme unchanged); a scheduled envelope fires its target only when its activity-gate passes; role->harness resolution honors role/status orthogonality (skips a role-holder that is not event-active).

## Artifact 4 — SPEC-PRIME-PROJECT-COMPLETION-ENVELOPE-001 (type=specification)

**Requirement:** A Prime Builder work envelope shall drive a chosen authorized project to VERIFIED-complete via: (1) select highest-priority project with an active PAUTH and incomplete WIs; (2) fan out claim-gated proposals for ready WIs (bounded by single-LO throughput + INDEX serialization); (3) advance each thread on the event-driven verdict->re-entry path (no background watch); (4) on any AUQ-class owner decision, park (DEFERRED) and surface, then continue other WIs; (5) terminate + retire when all member WIs reach VERIFIED (GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001).
**Acceptance:** the envelope never self-authorizes an owner decision; it never relies on a session-held watch; it converges or parks every member WI; it stops at project completion.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
