NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: codex-desktop-2026-06-02-wi3410-proposal
author_model: GPT-5
author_model_version: GPT-5 Codex
author_model_configuration: Codex Desktop; collaboration_mode=Default
author_metadata_source: Codex desktop session environment

bridge_kind: prime_proposal
Document: gtkb-impl-auth-requirement-sufficiency-phrase-tolerance
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3410
target_paths: ["scripts/implementation_authorization.py", "platform_tests/scripts/test_implementation_authorization.py", "platform_tests/scripts/test_implementation_start_gate.py"]

# Implementation Proposal - Impl-Auth Requirement Sufficiency Phrase Tolerance

## Summary

WI-3410 tracks a bridge-gate asymmetry: Loyal Opposition can GO an implementation proposal whose Requirement Sufficiency section uses natural phrasing such as "Existing requirements are sufficient", but `requirement_sufficiency_state()` currently accepts only the exact substring "Existing requirements sufficient". That mismatch has now blocked implementation-start packet creation on two live GO threads: `gtkb-worker-packet-auth-envelope-slice-2-auto-packet` and `gtkb-s358-w1-retirement-machinery-correction`.

This proposal changes the implementation authorization parser, not the bridge review standard. The parser should accept a small documented set of equivalent sufficient-state phrasings while preserving the current gap-state block for proposals that explicitly require new or revised requirements before implementation.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Do not add credentials or credential-shaped literals; the parser variants use ordinary prose fixtures only. | Bridge helper credential scan before filing plus changed-file review before commit. |  |
| CQ-PATHS-001 | Yes | Keep edits under the authorized GT-KB target paths and isolated pytest temp roots. | Implementation-start packet target paths plus targeted pytest review. |  |
| CQ-COMPLEXITY-001 | Yes | Use a small bounded matcher/helper instead of broad natural-language parsing. | Source review plus ruff check on changed files. |  |
| CQ-CONSTANTS-001 | Yes | Centralize accepted sufficiency phrase variants near the parser and keep the gap phrase unchanged. | Unit tests cover every accepted variant and the gap phrase. |  |
| CQ-SECURITY-001 | Yes | Do not change authorization packet trust boundaries, bridge status rules, network behavior, or privileged operations. | Gate-level tests prove only Requirement Sufficiency matching changes. |  |
| CQ-DOCS-001 | Yes | Carry rationale in this bridge proposal and implementation report; no narrative rule docs are edited. | LO review of proposal and later implementation report. |  |
| CQ-TESTS-001 | Yes | Add focused parser and gate regression tests for WI-3410 variants. | Targeted pytest commands listed in the verification plan. |  |
| CQ-LOGGING-001 | N/A |  |  | This parser fix does not add or alter logging surfaces. |
| CQ-VERIFICATION-001 | Yes | Run targeted pytest, ruff check, and ruff format check before filing the implementation report. | Implementation report records exact commands and observed results. |  |

## Problem Evidence

- `WI-3410` records the defect, acceptance summary, and observed prior instances from 2026-05-27.
- The git-repo broken-blob investigation and ChromaDB vector-continuity scoping threads both needed wording-only revisions because the same parser rejected "Existing requirements are sufficient" after GO.
- The worker-packet authorization envelope Slice 2 proposal has `## Requirement Sufficiency` with "Existing requirements are sufficient", and its implementation-start command currently returns `authorized: false` with `Approved proposal is missing ## Requirement Sufficiency`.
- The S358 W1 retirement-machinery correction proposal has the same natural phrasing and currently fails the same begin command despite latest GO.

## Scope

Implement the smallest parser and test change that satisfies WI-3410 acceptance path (a):

1. Replace the single literal sufficient-state substring check with a bounded helper or regex that accepts these equivalent phrasings inside the existing `## Requirement Sufficiency` section:
   - `Existing requirements sufficient`
   - `Existing requirements are sufficient`
   - `Requirements remain sufficient`
   - `Requirements are sufficient for this scope`
   - `Existing requirements are sufficient for this scoped governance correction`
2. Keep `New or revised requirement required before implementation` as the higher-priority gap-state phrase, so a section that explicitly declares a requirements gap remains blocked.
3. Keep missing/empty/placeholder Requirement Sufficiency sections blocked.
4. Add focused regression tests in the existing implementation authorization and implementation start gate test suites.

Out of scope:

- No source, test, config, bridge, MemBase, or project-artifact-link mutation beyond the target paths listed above.
- No weakening of the requirement-sufficiency section requirement.
- No direct implementation of `gtkb-worker-packet-auth-envelope-slice-2-auto-packet` or `gtkb-s358-w1-retirement-machinery-correction` in this thread.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - live bridge INDEX status controls Prime implementation actionability and GO-derived implementation packets.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation-start authorization packet creation is the parser surface being corrected.
- `GOV-RELIABILITY-FAST-LANE-001` - WI-3410 is a bounded reliability defect in `PROJECT-GTKB-RELIABILITY-FIXES` under the standing fast-lane authorization.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the parser defect is preserved as WI-3410 and repaired through the governed bridge path.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal includes Project Authorization, Project, and Work Item metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this section cites the governing specifications for the implementation proposal.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan below maps each requirement to executable tests.
- `GOV-STANDING-BACKLOG-001` - WI-3410 is the tracked backlog authority for this defect.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - this parser defect is represented as a durable work item and bridge thread.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - repeated blocked implementation-start attempts are an artifact lifecycle trigger for corrective work.

## Requirement Sufficiency

Existing requirements sufficient. WI-3410 already specifies the defect, accepted repair alternatives, and the exact natural-language variants that must be supported. The standing reliability fast-lane project authorization covers small source and test additions for active project members. No new or revised requirement is needed before implementation.

## Project Authorization

- Authorization: `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`
- Project: `PROJECT-GTKB-RELIABILITY-FIXES`
- Work item: `WI-3410`
- Allowed mutation classes used: `source`, `test_addition`
- Forbidden operations avoided: deployment, force-push, spec deletion

## Implementation Plan

1. Add a private helper in the implementation authorization script for Requirement Sufficiency state matching.
2. Preserve current section extraction and current gap-state precedence.
3. Match sufficient-state variants case-insensitively and with normal whitespace tolerance, bounded to the Requirement Sufficiency section body.
4. Add unit tests for every WI-3410 acceptance variant and for gap/missing behavior.
5. Add or extend a gate-level test proving packet creation works when a GO proposal says "Existing requirements are sufficient".

## Specification-Derived Verification Plan

- T-WI3410-auth-variants: covers WI-3410 and `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` with targeted pytest on the implementation authorization test target named in `target_paths`; expected coverage includes accepted sufficient-state variants plus missing/gap behavior.
- T-WI3410-gate-natural-phrase: covers `GOV-FILE-BRIDGE-AUTHORITY-001` and `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` with targeted pytest on the implementation start gate test target named in `target_paths`; expected coverage proves a GO proposal using "Existing requirements are sufficient" can produce a usable authorization packet.
- T-WI3410-quality: covers `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` with ruff check and ruff format check on the source and test targets named in `target_paths`.
- T-WI3410-preflight: covers `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` with bridge applicability preflight for this bridge id; expected result is no missing required specs after LO GO and implementation report filing.

## Risk And Rollback

Risk: An overly broad matcher could treat an ambiguous or negative sufficiency sentence as approval. Mitigation: match only a bounded set of affirmative phrases inside the already-required `## Requirement Sufficiency` section, keep gap-state detection first, and preserve missing-section blocking.

Rollback: revert the parser helper and focused tests. Existing canonical-phrase proposals continue to work under the old literal matcher.

## Prior Deliberations

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - standing reliability fast-lane authorization for small bounded reliability defects in this project.
- WI-3410 creation record - owner-directed backlog capture for this exact parser bias-case defect.
- The git-repo broken-blob investigation wording-only revision - prior workaround caused by the same literal matcher.
- The ChromaDB vector-continuity scoping wording-only revision - parallel workaround caused by the same literal matcher.
