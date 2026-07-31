ADVISORY
author_identity: owner-directed/prime-builder-codex
author_harness_id: A
author_session_context_id: 019f360f-0282-78b1-a070-7c60a158d8fb
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive Prime Builder; deliberation envelope; owner-directed ADVISORY filing

bridge_kind: governance_advisory
Document: gtkb-advisory-proposal-intake-workflow
Version: 001 (ADVISORY)
Author: Owner-directed Prime Builder (Codex, harness A)
Date: 2026-07-06 UTC

# Advisory: Formalize Deliberation-to-Implementation Advisory Proposal Intake

## Source
This advisory is owner-directed from the active `::open deliberation` envelope in Codex harness A on 2026-07-06. Mike asked to formalize a recurring deliberation-session instruction into a reusable path from deliberation to an approved implementation project.

Core owner instruction being formalized: the desired outcome is an advisory proposal that directs a PB to create a project, investigate and propose an implementation approach and a set of constituent work items which answer the need. If Mike is satisfied, he will manually direct a PB to pick up the advisory proposal and begin implementation.

Clarification decisions from this session:

- Use two envelope-specific skills, not one monolithic skill.
- PB intake should list implementation-bearing bridge `ADVISORY` proposals only.
- PB intake should live-scan bridge `ADVISORY` proposals first; the Insights dropbox is out of scope for intake.
- The deliberation-side workflow should file owner-directed bridge `ADVISORY` proposals.
- `::open deliberation` should use a topic-gated default: load the workflow, then start once Mike provides a concrete topic.
- PB intake should use a plan-then-create model for project and work-item mutations.
- Insights dropbox disposition cleanup is a separate project.
- The PB-side skill is a project-inception workflow, not an implementation-launch workflow.

## Claim
GT-KB should add a formal advisory-proposal-to-PB-intake workflow that turns implementation-bearing deliberations into owner-directed bridge `ADVISORY` proposals, then lets a later Prime Builder build envelope select one advisory and create a bounded project-inception plan.

The intended system behavior is:

1. In a deliberation envelope, the agent guides Mike through a structured clarification pass and produces a bridge `ADVISORY` proposal when the topic implies future implementation work.
2. Mike reviews the `ADVISORY`; nothing starts automatically.
3. If satisfied, Mike manually directs a PB to pick up the advisory in a build envelope.
4. The PB uses a build-side intake skill to select the advisory, summarize it, run any remaining owner-grilling pass, and draft a project plus initial scoping or investigation work items.
5. The PB creates the project and initial WIs only after explicit owner approval of that plan.
6. The actual implementation approach and final constituent implementation WIs are proposed after investigation, through the normal bridge lifecycle.

This should reuse existing GT-KB advisory machinery, especially bridge `ADVISORY` status, the owner-grilling gate, and the GO'd `WI-4840` advisory-disposition skill scaffold, rather than creating a second advisory queue or treating the Insights dropbox as PB intake authority.

## Owner Decision Needed
No additional owner decision is needed to file this advisory. This advisory records Mike's current direction and should wait for a later explicit PB pickup instruction.

Future owner decisions expected before mutation:

1. Mike must explicitly direct a Prime Builder to pick up this `ADVISORY` before creating a project or work items.
2. During PB intake, Mike must select the advisory proposal to convert.
3. After PB grilling, Mike must approve the proposed project and initial scoping or investigation WIs before the PB creates MemBase project/work-item records.
4. A separate owner decision should govern the independent Insights dropbox disposition cleanup project.

## Recommended Prime Action
When Mike later directs a PB to pick this up, the PB should open a build envelope and perform project inception, not direct implementation.

Recommended PB sequence:

1. Create a project candidate named `PROJECT-GTKB-ADVISORY-PROPOSAL-INTAKE-WORKFLOW` or a clearer final name chosen during PB grilling.
2. Investigate existing related work before proposing implementation, especially:
   - `WI-4840` / `gtkb-wi4840-advisory-disposition-skill-scaffold` (GO'd advisory-disposition skill scaffold).
   - `PROJECT-LO-ADVISORY-OWNER-GRILLING-GATE-001` and its verified owner-grilling-gate work.
   - `scripts/advisory_backlog_router.py` and `scripts/hygiene/advisory_candidate_promote.py`, because they stage advisory candidates but should not become PB intake authority.
   - `.claude/rules/peer-solution-advisory-loop.md`, which already defines the Required Prime Builder Owner-Grilling Gate.
3. Propose the implementation approach and constituent work items that answer the need. Expected work-item categories:
   - deliberation-side `advisory-proposal` skill;
   - build-side `advisory-intake` project-inception skill;
   - deterministic helper for live bridge `ADVISORY` listing, filtering, and summarization;
   - activity-profile and skill-scenario updates so deliberation and build envelopes surface the right skill at the right time;
   - tests for ADVISORY filtering, owner-grilling-gate detection, skill catalog registration, adapter generation, and activity-profile surfacing;
   - separate follow-on for Insights dropbox disposition cleanup.
4. Present the project/WI creation plan to Mike and wait for explicit approval before creating MemBase records.
5. After project inception is approved and created, file normal `NEW` implementation proposals for the scoped implementation slices and wait for independent Loyal Opposition `GO` before modifying protected paths.

## Classification Slot
Classification: adapt.

This is an implementation-bearing governance/workflow advisory. Prime Builder disposition options are:

- `adapt` / `adopt`: create the project-inception plan and follow normal bridge implementation after owner approval;
- `defer`: leave this `ADVISORY` on the Prime-visible queue until Mike asks to pick it up;
- `reject`: record why the two-skill advisory handoff is not desired.

The recommended disposition is `adapt`: adapt the existing advisory-disposition and owner-grilling-gate machinery into two role/envelope-specific skills and a bridge-ADVISORY intake helper.

## Required Prime Builder Owner-Grilling Gate

### Implementation implied
Yes. The advisory implies future skill, helper, activity-profile, registry/manifest, and test work. It does not authorize those mutations. It authorizes only later PB investigation and project inception if Mike explicitly picks it up.

### Grill-the-owner questions
Before filing any implementation proposal derived from this advisory, Prime Builder must obtain durable owner answers to:

1. What final project name and scope boundary should be used for the advisory-proposal/intake workflow?
2. Should `WI-4840` be treated as a dependency to complete first, a reusable vocabulary layer to integrate with, or a sibling workstream that this project may revise?
3. What exact filter makes a bridge `ADVISORY` implementation-bearing enough for PB intake: explicit `Classification: adopt/adapt`, presence of `Required Prime Builder Owner-Grilling Gate`, or both?
4. Should the deliberation-side skill file bridge `ADVISORY` entries directly, or produce a draft and call a governed writer only after an explicit final confirmation in that session?
5. What should count as the minimal initial project/WI plan: one investigation WI plus skill implementation WIs, or a broader project with separate discovery, specification, implementation, and verification slices?
6. What user-facing prompt should `::open deliberation` display for the topic-gated default so exploratory deliberations do not feel hijacked by a mandatory workflow?

### Required durable owner decisions
Before a `NEW` implementation proposal exists, Prime Builder must preserve decisions for:

- project name and scope boundary;
- whether `WI-4840` is dependency, sibling, or absorbed scope;
- implementation-bearing ADVISORY filter predicate;
- direct-file versus draft-first behavior for the deliberation-side skill;
- initial project/WI creation plan approval.

## Suggested Project-Inception Shape
Suggested project: `PROJECT-GTKB-ADVISORY-PROPOSAL-INTAKE-WORKFLOW`.

Suggested initial WIs for PB to propose after grilling:

1. Investigation/scoping WI: map existing advisory-disposition, owner-grilling-gate, ADVISORY bridge routing, and advisory-candidate tooling to the target workflow.
2. Skill WI: deliberation-side `advisory-proposal` skill.
3. Skill WI: build-side `advisory-intake` project-inception skill.
4. Helper WI: live bridge `ADVISORY` scanner/summarizer with implementation-bearing filter.
5. Envelope integration WI: activity disposition profile / skill scenario updates for deliberation and build envelopes.
6. Test/parity WI: skill catalog, adapter generation, activity-profile, and bridge-filter tests.
7. Separate follow-on candidate: Insights dropbox disposition cleanup.

## Boundaries
This `ADVISORY` does not approve implementation, does not create a project, does not create work items, and does not bypass bridge `GO` or implementation-start gates.

The Insights dropbox is explicitly not PB intake authority for this workflow. Items in the dropbox should eventually be resolved into Deliberation Archive records or bridge `ADVISORY` proposals through a separate governance cleanup project.

## Related Context
- `.claude/rules/file-bridge-protocol.md` defines `ADVISORY` as Prime-visible, interactive-only disposition work.
- `.claude/rules/peer-solution-advisory-loop.md` defines the Required Prime Builder Owner-Grilling Gate for `adopt`/`adapt` advisories.
- `bridge/gtkb-wi4840-advisory-disposition-skill-scaffold-002.md` is GO for the reusable advisory-disposition skill scaffold and should be reconciled rather than duplicated.
- `scripts/advisory_backlog_router.py` stages advisory candidates, but this advisory records Mike's direction that PB intake should live-scan bridge `ADVISORY` proposals and not use the Insights dropbox as the primary list.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
