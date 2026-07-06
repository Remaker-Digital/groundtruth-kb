NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f38c2-14c9-7dc0-aa9f-a4bf0183c344
author_model: gpt-5-codex
author_model_version: gpt-5-codex-2026-07-06
author_model_configuration: Codex desktop interactive Prime Builder; cwd=E:\GT-KB; sandbox=danger-full-access; approval=never
author_metadata_source: codex-interactive-env

# Implementation Proposal - Advisory Proposal Intake Workflow Umbrella

bridge_kind: prime_proposal
Document: gtkb-advisory-proposal-intake-workflow
Version: 002
Date: 2026-07-06 UTC
Responds-To: bridge/gtkb-advisory-proposal-intake-workflow-001.md

Project Authorization: PAUTH-PROJECT-GTKB-ADVISORY-PROPOSAL-INTAKE-WORKFLOW-WI-5053-UMBRELLA
Project: PROJECT-GTKB-ADVISORY-PROPOSAL-INTAKE-WORKFLOW
Work Item: WI-5053

target_paths: ["groundtruth.db", "bridge/gtkb-advisory-proposal-intake-workflow-*.md"]

implementation_scope: metadata
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

## Summary

Prime Builder proposes converting the source `ADVISORY` into a governed umbrella implementation slice. If Loyal Opposition returns GO, Prime Builder will create the approved child MemBase work items and linked tests for the advisory proposal intake workflow, then file an implementation report on this same bridge thread.

This umbrella is project-inception and child-WI formation only. It does not authorize protected source, config, test, hook, skill, credential, deployment, or Agent Red application mutation. Each child implementation must later receive its own bridge proposal, GO verdict, work-intent claim, implementation-start authorization, implementation report, and Loyal Opposition verification.

## Source Advisory Disposition

Source advisory: `bridge/gtkb-advisory-proposal-intake-workflow-001.md`.

Disposition: adopt/adapt into a governed project-inception umbrella.

The source advisory requested a formal advisory-proposal-to-Prime-Builder-intake workflow:

- deliberation can produce a bridge `ADVISORY` only after final owner confirmation;
- Prime Builder does not start automatically from advisory capture;
- Prime Builder intake selects a live `ADVISORY`, summarizes it, runs owner-grilling, and drafts project plus scoping/investigation WIs;
- project and initial WIs are created only after explicit owner approval;
- final implementation WIs/proposals proceed through normal bridge lifecycle after investigation.

This proposal preserves that structure while using the stricter existing umbrella precedent: create the project shell and seed umbrella WI from owner decisions, file this reviewable proposal, and create detailed child WIs only after Loyal Opposition GO.

## Owner Decisions / Input

- `DELIB-202665483` - owner approved project id/name/scope and ordered the `WI-4840` relationship as dependency first, vocabulary/procedure reuse second, sibling/revision alignment third.
- `DELIB-202665484` - owner approved the implementation-bearing `ADVISORY` filter predicate: require both `adopt/adapt` classification and a `Required Prime Builder Owner-Grilling Gate` section.
- `DELIB-202665485` - owner approved draft-first filing mode for the deliberation-side skill before any governed writer files an `ADVISORY`.
- `DELIB-202665486` - owner approved the minimal initial plan shape: one investigation/scoping WI plus separate skill, helper, integration, and test WIs.
- `DELIB-202665487` - owner approved the topic-gated `::open deliberation` prompt:
  `What should we deliberate? If this turns into implementation-bearing future work, I can draft a bridge ADVISORY for your final confirmation before anything is filed.`

## Prior Deliberations

- `DELIB-202665483` - Advisory Proposal Intake Workflow Scope Decisions.
- `DELIB-202665484` - Advisory Proposal Intake Workflow Filter Predicate Decision.
- `DELIB-202665485` - Advisory Proposal Intake Workflow Filing Mode Decision.
- `DELIB-202665486` - Advisory Proposal Intake Workflow Initial Plan Decision.
- `DELIB-202665487` - Advisory Proposal Intake Workflow Deliberation Prompt Decision.
- `DELIB-20260703-GTKB-MUTATION-PERMISSION-GENERAL-PRIMITIVE-FIRST` and `bridge/gtkb-wi5005-permission-reconciliation-approach-001.md` - precedent for a project shell plus GO-reviewed downstream work-item proposal before detailed child work-item creation.
- `bridge/harness-equivalence-phase-3-umbrella-001.md` and `bridge/harness-equivalence-phase-3-umbrella-003.md` - precedent for an umbrella proposal that creates child WIs/tests only after LO GO.
- `bridge/gtkb-wi4840-advisory-disposition-skill-scaffold-008.md` - current `NO-GO` boundary for related advisory-disposition skill work; this umbrella depends on and reuses that vocabulary, but does not claim WI-4840 is complete.
- `bridge/gtkb-lo-advisory-owner-grilling-gate-slice3-lint-*.md` - verified owner-grilling gate context for adopt/adapt advisory flows.

## Requirement Sufficiency

Existing requirements are sufficient for this umbrella because the work is limited to project/backlog metadata formation. The owner decisions define the project boundary, the filter predicate, the filing mode, the initial child plan, and the user-facing deliberation prompt. `WI-5053` and its linked `TEST-11291` define the seed umbrella acceptance check.

The detailed child WIs may later require additional specifications or ADR/DCL amendments if they add new enforcement mechanisms, helper schemas, dispatcher behavior, activity-profile contracts, or protected implementation gates. This umbrella intentionally does not assert those child requirements are already complete.

## Proposed Scope

After Loyal Opposition GO, Prime Builder will:

1. Run `scripts/implementation_authorization.py begin --bridge-id gtkb-advisory-proposal-intake-workflow`.
2. Acquire the bridge work-intent claim for this thread.
3. Create child MemBase work items and linked manual tests through `gt backlog add-work-item`, with `PHASE-001` test-plan assignment, under `PROJECT-GTKB-ADVISORY-PROPOSAL-INTAKE-WORKFLOW`.
4. File an implementation report on this bridge thread listing the created child WIs/tests and verification evidence.
5. Leave all child implementation work blocked until each child has its own bridge proposal and GO.

## Child Work Items To Create After GO

The child plan follows `DELIB-202665486`:

| Child area | Intended purpose | Initial priority |
| --- | --- | --- |
| Investigation/scoping | Map WI-4840, owner-grilling gate, live `ADVISORY` routing, advisory-candidate tooling, and peer-solution loop to this workflow. | P1 |
| Deliberation-side `advisory-proposal` skill | Draft-first deliberation output path that can prepare, review, and only after final confirmation file implementation-bearing bridge `ADVISORY` artifacts. | P1 |
| Build-side `advisory-intake` skill | Prime Builder project-inception workflow for selecting an `ADVISORY`, summarizing it, running owner-grilling, and preparing project/WI proposals. | P1 |
| Bridge `ADVISORY` scanner/helper | Deterministic listing, filtering, and summarization of live implementation-bearing `ADVISORY` entries using the approved both-filter predicate. | P1 |
| Activity-profile and skill-scenario surfacing | Make the deliberation and build-side workflows discoverable in appropriate activity profiles and generated skill surfaces. | P2 |
| Test/parity coverage | Cover ADVISORY filtering, owner-grilling gate behavior, skill catalog registration, adapter generation, activity-profile surfacing, and parity expectations. | P1 |

Insights-dropbox disposition cleanup remains excluded and should become a separate follow-on only if separately approved.

## Out Of Scope

- Protected source, config, hook, skill, script, or test mutation.
- Implementing any child WI.
- Treating `ADVISORY` capture as implementation approval.
- Bypassing draft-first final owner confirmation for deliberation-side advisory filing.
- Credential lifecycle, production deployment, or Agent Red application mutation.
- Retiring or resolving `WI-4840`.
- Insights-dropbox disposition cleanup.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge status authority, role-correct bridge writing, append-only numbered chain.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - owner decisions and actionable advisory findings become durable governed artifacts.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - implementation proposals must carry concrete specification links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation reports must map linked specs to executed evidence before verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - implementation-targeting bridge files require PAUTH, project, WI, and parseable target paths.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps GT-KB platform work inside the GT-KB root and out of lifecycle-independent adopter repositories.
- `GOV-STANDING-BACKLOG-001` - future work belongs in MemBase work items/tests, not chat or scratchpads.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - bounded PAUTH controls project implementation authority.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - preserve decisions, plans, and future work as governed artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - advisory findings that cross into future work need explicit lifecycle routing.
- `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` - adopt/adapt advisories must carry owner-grilling before conversion to implementation work.
- `DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001` - owner-grilling gate behavior must be visible and testable for advisory adoption.

## Specification-Derived Verification Plan

| Spec / governing surface | Verification expectation |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `gt bridge show gtkb-advisory-proposal-intake-workflow --json` confirms this same chain advances from `ADVISORY` to `NEW`, then later to GO/report/VERIFIED or NO-GO. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Implementation report cites the source advisory, five owner decisions, project, WI, PAUTH, and created child WIs/tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-advisory-proposal-intake-workflow` passes for this proposal. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report maps every linked spec to command/artifact evidence before Loyal Opposition verification. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Bridge compliance and applicability preflight confirm PAUTH, project, WI, and `target_paths` are present. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Proposal and implementation report confirm all artifacts are under `E:\GT-KB` and no Agent Red lifecycle-independent repository mutation occurs. |
| `GOV-STANDING-BACKLOG-001` | `gt projects show PROJECT-GTKB-ADVISORY-PROPOSAL-INTAKE-WORKFLOW --json` and `gt backlog list --project PROJECT-GTKB-ADVISORY-PROPOSAL-INTAKE-WORKFLOW --json` confirm child WIs/tests exist after GO. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | `scripts/implementation_authorization.py begin --bridge-id gtkb-advisory-proposal-intake-workflow` validates GO, PAUTH, WI-5053, and target paths before metadata mutation. |
| `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` / `DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001` | Child WI descriptions preserve the approved owner-grilling questions and the both-filter predicate for implementation-bearing advisories. |

## Acceptance Criteria

- `PROJECT-GTKB-ADVISORY-PROPOSAL-INTAKE-WORKFLOW` exists and is active.
- `WI-5053` and `TEST-11291` exist under the project.
- `PAUTH-PROJECT-GTKB-ADVISORY-PROPOSAL-INTAKE-WORKFLOW-WI-5053-UMBRELLA` is active and bounded to bridge plus metadata work only.
- This bridge file is filed as version 002 on the original `gtkb-advisory-proposal-intake-workflow` chain.
- After GO, child WIs/tests are created for the six approved child areas.
- Implementation report confirms no protected source/config/test/hook/skill/script files were changed.
- Child implementation remains blocked behind child bridge proposals and GO verdicts.

## Risks / Rollback

Risk: the umbrella becomes an accidental broad permission slip. Mitigation: PAUTH is limited to `bridge` and `metadata`; child implementation is explicitly forbidden.

Risk: this duplicates WI-4840. Mitigation: `DELIB-202665483` orders the relationship as dependency first, vocabulary/procedure reuse second, sibling/revision alignment third.

Risk: child WIs are too broad. Mitigation: this umbrella creates child WIs/tests only; each child still needs its own proposal and GO before implementation.

Rollback: file a revised bridge version narrowing or withdrawing this umbrella. MemBase project/WI/PAUTH rows are append-only audit artifacts; do not delete them.

## Files Expected To Change After GO

- `groundtruth.db` - child WI/test/project membership records.
- `bridge/gtkb-advisory-proposal-intake-workflow-*.md` - implementation report and eventual Loyal Opposition verdict.

## Recommended Commit Type

docs
