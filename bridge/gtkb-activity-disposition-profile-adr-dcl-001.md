NEW

# Implementation Proposal - Activity Disposition Profile (ADR + DCL) (governance_review)

bridge_kind: governance_advisory
Document: gtkb-activity-disposition-profile-adr-dcl
Version: 001
Author: Prime Builder (Claude Code, harness B, durable role per registry: [prime-builder])
Date: 2026-06-21 UTC

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: ddcd0cf1-1585-48d6-83b9-8e32c08898c4
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI, explanatory output style, interactive Prime Builder ::open deliberation session

Project: PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH
Work Item: WI-4684
Recommended commit type: docs

target_paths: []

implementation_scope: governance_review_spec_drafting
requires_review: true
requires_verification: false
kb_mutation_in_scope: false

## KB-Mutation Negation (self-demonstration)

This proposal performs no MemBase mutation and writes no protected narrative files.
The two artifacts drafted below (ADR-ACTIVITY-ENVELOPE-DISPOSITION-001 and
DCL-ACTIVITY-DISPOSITION-PROFILE-001) land downstream via formal-artifact-approval
packets, each gated by GOV-ARTIFACT-APPROVAL-001. GO is terminal for THIS thread.

## Claim

Draft the two GOV-20 architecture artifacts that formalize WI-4684's disposition-profile
model, per the owner reframe captured in DELIB-20260621-EXPLICIT-HINT-CONTEXT-LOAD-REFRAME:

1. ADR-ACTIVITY-ENVELOPE-DISPOSITION-001 (architecture_decision) - the decision that each
   activity carries a per-activity context-load profile injected at ::open, as a
   context-management / progressive-disclosure mechanism, enriching the intent_hint leg of
   the envelope 3-part anatomy (ADR-ENVELOPE-META-MODEL-001).
2. DCL-ACTIVITY-DISPOSITION-PROFILE-001 (design_constraint) - the machine-checkable 4-class
   context-load schema (skills, terminology, history_state, direction) + injection +
   non-blocking soft-reminder-gate enforcement + single-active invariant.

## The two artifacts (full drafts)

### ADR-ACTIVITY-ENVELOPE-DISPOSITION-001 (architecture_decision)

Title: Activity-Envelope Disposition: Per-Activity Context-Load Profile at the intent_hint leg

Decision: Each activity in the closed-but-extensible vocabulary {ops, deliberation, build,
test, spec, project} carries a named, versioned disposition profile injected by the harness
at ::open <activity>. It primes the session as a context-management / progressive-disclosure
mechanism - loading a small, activity-relevant slice of the growing skill/terminology/state
surface rather than everything every session. The profile is the enrichment of the
intent_hint leg of the envelope three-part anatomy (ADR-ENVELOPE-META-MODEL-001 /
DCL-ENVELOPE-META-MODEL-001), not a new leg.

Context / problem: GT-KB skills, glossary, and state surfaces have grown faster than an agent
can discover and load them at need. Load-all-per-session is bloat; load-none (status quo)
leaves agents unable to find context - demonstrated live in the 2026-06-21 ::open deliberation
session, where ::open deliberation loaded no deliberation skills, terminology, or recent
deliberation/backlog state and the agent hand-searched.

Decision drivers: DELIB-20260621 DEC-1..5; DELIB-20265287 D1 (single active envelope),
D2 (named enforced disposition profile), D4 (per-activity headless-eligibility), F2
(disposition profile = enrichment of the intent_hint leg).

Failed approaches / rejected alternatives:
- Load-everything-per-session - rejected: context bloat; defeats the discovery problem.
- Pure mechanical enforcement - rejected (owner lens correction, DEC-1/DEC-3): the layer's
  primary value is targeted context loading, not gating.
- Hard implementation-tool gate during no-implement activities - rejected (DEC-3): too rigid;
  replaced by a non-blocking soft reminder.
- Free-form activity vocabulary - rejected (DELIB-20260612 D1): the subject axis is a payload
  field, not a free keyword; vocabulary stays closed-but-extensible.
- Supersede/redesign the envelope program - rejected (DEC-5 / DELIB-20265287 D8): this extends
  the existing envelope/disposition/isolation programs, it does not fork them.

Consequences:
- The profile schema is normative and machine-checkable (DCL-ACTIVITY-DISPOSITION-PROFILE-001).
- Each of the six v1 activities needs a seeded profile; the set is extensible (push/upgrade may
  return; DEC-4).
- Interception is hook-primary with an agent-enforced fallback where hook events are
  unavailable (ADR-CODEX-HOOK-PARITY-FALLBACK-001).
- Single active activity envelope (DELIB-20265287 D1) bounds disposition coherence.
- Headless-eligibility is a per-activity property (DELIB-20265287 D4): deliberation + project
  interactive-only; spec + build + test headless-eligible; ops interactive-primary.

### DCL-ACTIVITY-DISPOSITION-PROFILE-001 (design_constraint)

Title: Activity Disposition Profile: 4-Class Context-Load Schema

Constraint: Every canonical activity MUST have a named, versioned disposition profile carrying
exactly four payload classes:
1. skills - the skills to load/surface for the activity.
2. terminology - the glossary subset to anticipate.
3. history_state - the acquisition recipe: which recent deliberations, backlog slice,
   implementation progress, operational issues, and repo state to pull.
4. direction - behavioral stance + guardrails + a declaration of which objects the session
   manipulates.
The profile is injected at ::open <activity> (hook-primary; agent fallback per
ADR-CODEX-HOOK-PARITY-FALLBACK-001). Enforcement is injection + a non-blocking soft reminder
gate: while a no-implement activity is open, implementation tools trigger a non-blocking
reminder of the activity guardrail, never a hard block. At most one activity envelope is open
at a time (DELIB-20265287 D1).

Assertions (machine-checkable; mostly status=specified until the runtime lands):
- A1: each activity in {ops, deliberation, build, test, spec, project} has a profile record.
- A2: each profile defines all four classes (skills, terminology, history_state, direction).
- A3: each profile carries a headless_eligibility attribute consistent with DELIB-20265287 D4.
- A4: an interception surface (hook registration OR documented agent-fallback) exists for ::open.
- A5: the soft-reminder gate is registered as non-blocking (advisory), not a hard PreToolUse block.

Relationships: extends DCL-ENVELOPE-META-MODEL-001 (intent_hint leg); references
DCL-SESSION-ENVELOPE-DURABILITY-001 (topics-array storage), SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001
(sibling hint family), DCL-TOPIC-ENVELOPE-ROUTING-001 (activity-type routing).

## Why Now

WI-4684's disposition-profile model is owner-decided (DELIB-20260621 + DELIB-20265287) but not
yet formally specified. Authoring the ADR/DCL now - before any runtime build - locks the schema
the implementation will target and keeps the program internally consistent. The prior governance
vehicle (gtkb-explicit-hint-layer-specification-001) was withdrawn as obsolete this session;
this proposal is the corrected, reframed governance surface for the disposition leg.

## Why Not (alternatives considered)

See the ADR's rejected-alternatives section. Additionally: deferring the ADR/DCL until runtime
(rejected - the schema is the contract the runtime must satisfy; specifying it first is cheaper
and prevents implementation drift).

## Prior Deliberations

- DELIB-20260621-EXPLICIT-HINT-CONTEXT-LOAD-REFRAME (2026-06-21) - the owner decision set
  (DEC-1..5) this proposal formalizes.
- DELIB-20265287 (2026-06-19) - D1 single-active, D2 disposition profile, D4 headless-eligibility,
  F2 intent_hint enrichment.
- DELIB-20260612-EXPLICIT-HINT-LAYER-DECISION-SET - umbrella + closed-vocabulary decisions.
- DELIB-20260635 / DELIB-20260636 / DELIB-20260637 - envelope meta-model + 3-part anatomy shaping.
- DELIB-20260648 - init-keyword v3 (sibling hint family).

## Specification Links

Cross-cutting (blocking):
- GOV-FILE-BRIDGE-AUTHORITY-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- GOV-ARTIFACT-APPROVAL-001 (governs the downstream ADR/DCL inserts)
- GOV-STANDING-BACKLOG-001

Domain specs extended or referenced:
- ADR-ENVELOPE-META-MODEL-001 (parent anatomy; intent_hint leg)
- DCL-ENVELOPE-META-MODEL-001 (parent intent_hint constraint this DCL extends)
- ADR-CODEX-HOOK-PARITY-FALLBACK-001 (interception fallback basis)
- DCL-SESSION-ENVELOPE-DURABILITY-001 (topics-array storage)
- SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001 (sibling hint family)
- DCL-TOPIC-ENVELOPE-ROUTING-001 (activity-type routing alignment)

Cross-cutting (advisory):
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- DCL-CONCEPT-ON-CONTACT-001 (the disposition-profile concept becomes glossary-promotable)
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001

New formal artifacts created downstream (via formal-artifact-approval-packet):
- ADR-ACTIVITY-ENVELOPE-DISPOSITION-001 (architecture_decision)
- DCL-ACTIVITY-DISPOSITION-PROFILE-001 (design_constraint)

## Owner Decisions / Input

This proposal is authorized by a fresh, durable owner-decision record:
- DELIB-20260621-EXPLICIT-HINT-CONTEXT-LOAD-REFRAME (source_type=owner_conversation,
  outcome=owner_decision, session 2026-06-21, AUQ-backed) captures DEC-1..5 (context-management
  lens; 4-class profile; injection + soft-reminder gate; six-member vocabulary; withdraw -001).
- Owner AUQ this session (2026-06-21): File as drafted to Codex - approval to file these two
  drafted artifacts as a governance_review proposal.

Downstream owner-input dependencies (after GO):
- 2 formal-artifact-approval packets for ADR-ACTIVITY-ENVELOPE-DISPOSITION-001 and
  DCL-ACTIVITY-DISPOSITION-PROFILE-001 (GOV-ARTIFACT-APPROVAL-001).

## Requirement Sufficiency

Existing requirements sufficient. Both artifacts derive from DELIB-20260621 (owner AUQ) +
DELIB-20265287 (owner AUQ) + the parent meta-model specs (ADR/DCL-ENVELOPE-META-MODEL-001).
No new owner requirement is needed before drafting; the downstream artifact insertions are
owner-gated at their own approval packets.

## Pre-Filing Preflight Subsection

Per .claude/rules/file-bridge-protocol.md. Run:
    python scripts/bridge_applicability_preflight.py --bridge-id gtkb-activity-disposition-profile-adr-dcl
    python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-activity-disposition-profile-adr-dcl
Expected: preflight_passed: true, missing_required_specs: [], no blocking clause gaps.

## Specification-Derived Verification Plan

This is a governance_review proposal with target_paths: [] and requires_verification: false;
GO is terminal for this bridge thread (governance-review-terminal pattern). No follow-on
post-impl report is required for THIS thread. The downstream artifact insertions are verified
at their own gates:
- ADR/DCL inserts: formal-artifact-approval packets at .groundtruth/formal-artifact-approvals/
  plus MemBase rows for the two new IDs.
- DCL assertions A1-A5 run at session start (informational until the runtime lands).
- Doctor canonical checks pass with the new artifacts.

## Risk / Rollback

This proposal writes one bridge file. Rollback is a git restore plus deletion of the new
bridge file through the standard cleanup path. The downstream narrative and formal artifact
writes are owner-gated separately; this thread's blast radius is the proposal file itself.

## Recommended Commit Type

docs - governance/architecture documentation (ADR + DCL drafting); no source/test/hook/config
code is modified by this thread.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
