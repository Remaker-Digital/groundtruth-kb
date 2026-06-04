NEW

bridge_kind: governance_review
Document: gtkb-major-release-content-goal-gov
Version: 001
Project: PROJECT-GTKB-V1-RELEASE-STRATEGY-001
Work Item: WI-4303
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-04 UTC
Reviewer: Loyal Opposition
Recommended commit type: docs

author_identity: Claude Code Prime Builder (interactive, session-stated PB via ::init gtkb pb)
author_harness_id: B
author_session_context_id: a47d634f-7804-4452-aff5-1ca018aeef3d
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI, explanatory output style

target_paths: [".groundtruth/formal-artifact-approvals/2026-06-04-gov-major-release-content-goal-001.json", ".groundtruth/formal-artifact-approvals/2026-06-04-dcl-major-release-content-gate-001.json", "groundtruth.db", "bridge/gtkb-major-release-content-goal-gov-001.md", "bridge/INDEX.md", ".gtkb-state/**"]

implementation_scope: governance
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

# Promote the standing major-release content goal to a GOV spec + release-gate DCL

## Source / Owner Directive

Owner AUQ (2026-06-04): (1) confirmed the major-release work order
"Stabilize -> machinery -> envelope -> gate"; (2) directed that the standing
content goal (GT-KB v1.0 includes the Envelope program incl. the rule-driven
dispatcher) be **promoted to a GOV specification** so it is mechanically
enforced in release-gate checks rather than only consulted. DELIB-20260638
recorded the goal; this proposal formalizes it as GOV + DCL under the GOV-20
workflow + GOV-ARTIFACT-APPROVAL-001.

## Proposal Kind

`governance_review` — creates two NEW MemBase governance artifacts (1 GOV, 1 DCL).
No source/runtime change in this slice; the release-gate code that consumes the
DCL assertions is follow-on implementation (Phase 1 release machinery). Each
artifact inserts only AFTER Codex GO + a matching formal-artifact-approval
packet; a CVR then proves DCL compliance.

## Requirement Sufficiency

New requirement required before implementation. This proposal's operative purpose
is requirement/specification capture through the governed approval path; it does
NOT authorize source/config/test implementation. The release-gate enforcement
code is a separate follow-on WI.

## Specification Links

- GOV-ARTIFACT-APPROVAL-001 - per-artifact approval packets gate the two inserts.
- PB-ARTIFACT-APPROVAL-001 - formal-artifact-approval discipline.
- DCL-ARTIFACT-APPROVAL-HOOK-001 - approval-gate + evidence-checker contract.
- GOV-RELEASE-READINESS-GOVERNED-TESTING-001 - production release readiness requires governed evidence; the new gate DCL extends release-readiness checks.
- GOV-STANDING-BACKLOG-001 - standing-work authority; the standing content goal is a sibling standing-governance artifact.
- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge protocol + INDEX canonicality.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - spec-linkage compliance.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - spec-derived verification plan below.
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 - Project + Work Item cited above.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - all target_paths in-root.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - artifact-oriented governance for the new records.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - artifact-first development framing.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - artifact lifecycle triggers for GOV/DCL creation.

## Prior Deliberations

- DELIB-2234 - GT-KB v1.0 release strategy (the release this goal governs).
- DELIB-20260638 - the standing major-release content goal owner_decision this promotes.
- Envelope lineage DELIB-2238 -> 2500 -> 20260635 -> 20260636 -> 20260637 - the included content.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - the dispatcher/force-multiplier rationale.

## Owner Decisions / Input

- AskUserQuestion 2026-06-04 (release order): "Stabilize -> machinery -> envelope -> gate" - the confirmed standing work order.
- AskUserQuestion 2026-06-04 (goal teeth): "Promote to a GOV spec (Recommended)" - directs creating GOV-MAJOR-RELEASE-CONTENT-GOAL-001 + a release-gate DCL with a machine-checkable assertion. This AUQ is the owner-decision authority; per-artifact formal-artifact-approval packets remain required at insert time.

## Spec-Derived Verification Plan

Specification-derived verification (spec-to-test) for governance artifact creation:

| Artifact / clause | Verification (spec-to-test) | Command | Expected |
|---|---|---|---|
| Both inserts match approved content | per-artifact formal-artifact-approval packet sha256 matches inserted row | packet sha check / check_narrative_artifact_evidence pattern | match |
| DCL-MAJOR-RELEASE-CONTENT-GATE-001 assertions | assertions registered + runnable | `gt assert` (architecture layer) | assertions present |
| DCL compliance of the inserted set | CVR document proving the gate assertions | CVR authored post-insert | CVR present |
| Bridge protocol | applicability + clause preflights on this operative file | `bridge_applicability_preflight.py` + `adr_dcl_clause_preflight.py` | preflight pass; exit 0 |
| In-root | all target_paths under E:\GT-KB | inspection | pass |

The release-gate enforcement code (consuming the DCL assertions; pytest/ruff
coverage) is follow-on Phase-1 implementation, out of scope for this
governance-capture slice.

## Bridge INDEX Self-Check

Per GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL: this proposal is
filed under bridge/ and its bridge/INDEX.md entry is created by inserting a new
`Document: gtkb-major-release-content-goal-gov` entry with `NEW:
bridge/gtkb-major-release-content-goal-gov-001.md` at the top of the index entry
list; append-only, no prior entry deleted or rewritten. bridge/INDEX.md remains
canonical workflow state.

## Risk / Rollback

Low: two governance-record inserts behind per-artifact approval packets + Codex
GO. No runtime/behavior change in this slice. Rollback = append terminal/
superseded versions (append-only). No source/config touched.

---

# PROPOSED ARTIFACT CONTENT (native review format; NOT yet inserted)

## Artifact 1 - GOV-MAJOR-RELEASE-CONTENT-GOAL-001 (type=governance)

**Status:** proposed.
**Core rule:** The next GT-KB major release (v1.0, per DELIB-2234) MUST NOT be
cut until its content includes ALL THREE: (1) the DELIB-2234 v1.0 release
machinery (§10.1 mechanical-enforcement gate, §10.2 spec-corpus distillation,
Docker isolation-validator, §10.3 acceptance criteria); (2) the full Envelope
program (PROJECT-GTKB-ENVELOPE-OPEN-CLOSE-ACTION-REFINEMENT), including the
rule-driven dispatcher (dispatch envelopes to harness / role / topic / arbitrary
prompt, rule-scheduled); (3) the Agent Red green-on-clean release gate
(DELIB-2234 §9.3; WI-3248).
**Standing sequencing:** Phase 0 stabilize -> Phase 1 machinery -> Phase 2
envelope program -> Phase 3 Agent Red gate + cut (owner AUQ 2026-06-04).
**Standing force:** future sessions treat this as the major-release content
target and order discretionary work to advance it unless the owner supersedes.
Quality-driven; no date pressure (DELIB-2234 §9.2).
**Source:** DELIB-20260638; DELIB-2234; envelope lineage DELIB-2238/2500/20260635/20260636/20260637.

## Artifact 2 - DCL-MAJOR-RELEASE-CONTENT-GATE-001 (type=design_constraint; derived from GOV-MAJOR-RELEASE-CONTENT-GOAL-001)

Machine-checkable assertions (the v1.0 release-candidate gate MUST verify these
and FAIL the cut if any is incomplete):
1. **Envelope-program-complete:** every release-content WI in
   PROJECT-GTKB-ENVELOPE-OPEN-CLOSE-ACTION-REFINEMENT (the WI-4291..WI-4302 set)
   is resolved/VERIFIED before a v1.0 cut.
2. **Machinery-present:** §10.1 enforcement gate (WI-3401), §10.2 spec-corpus
   distillation (WI-3402), Docker isolation-validator (WI-3403), and §10.3
   acceptance criteria are complete.
3. **Agent-Red-gate:** WI-3248 / PROJECT-AGENT-RED-RELEASE-READINESS is
   green-on-clean.
4. **Gate binding:** the release-candidate gate (scripts/release_candidate_gate.py
   or successor) consumes assertions 1-3; a v1.0 cut is refused while any is
   incomplete.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
