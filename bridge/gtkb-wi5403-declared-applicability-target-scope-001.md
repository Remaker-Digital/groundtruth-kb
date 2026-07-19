NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: GPT-5 Codex
author_model_version: 5
author_model_configuration: OpenAI Codex desktop interactive; reasoning=xhigh; approval_policy=never
author_metadata_source: codex-inline-non-bypass-writer

# Implementation Proposal - Complete declared applicability target-scope separation after false closure

bridge_kind: prime_proposal
Document: gtkb-wi5403-declared-applicability-target-scope
Version: 001
Date: 2026-07-17 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5403-DECLARED-TARGET-SCOPE-20260717
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5403

target_paths: ["scripts/bridge_applicability_preflight.py", "platform_tests/scripts/test_bridge_applicability_preflight.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

WI-5403 proposal to complete declared applicability target-scope separation after false closure while preserving shared-file boundaries with WI-5387 and WI-5408.

Work item description: WI-5363 was metadata-resolved after its bridge thread became terminal, but the current source still assigns the document-wide declared-plus-incidental path scan to packet.target_paths. The only dirty source hunk in the same files implements corrected operative-version handling after NO-ACTION and does not separate declared mutation scope from normalized cited applicability evidence. Add the originally required packet and Markdown distinction without weakening conservative path-driven specification applicability or missing-parent warning behavior, preserve the foreign operative-version hunk, and sequence finalization through WI-5386 physical-residue closure.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5403` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/bridge_applicability_preflight.py`, `platform_tests/scripts/test_bridge_applicability_preflight.py`.

## Specification Links

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - auto-linked governing or work-item specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - auto-linked governing or work-item specification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform command out of adopter application scope.
- `GOV-STANDING-BACKLOG-001` - auto-linked governing or work-item specification.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - auto-linked governing or work-item specification.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - auto-linked governing or work-item specification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - auto-linked governing or work-item specification.
- `GOV-WORK-TREE-HYGIENE-001` - auto-linked governing or work-item specification.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - auto-linked governing or work-item specification.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - requires bounded PAUTH envelopes for new authorization state.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202666269` - Loyal Opposition GO Verdict - WI-5266 Backlog Versus Bridge Resource Routing
- `DELIB-202666301` - Loyal Opposition Superseding NO-GO - WI-5266 Clean-Checkout Package Closure
- `DELIB-202666273` - WI-5266 five-path baseline preservation exception
- `DELIB-20266287` - Found an existing PAUTH that's a strong scope match: `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BATCH` v2 (project:
- `DELIB-202666294` - Loyal Opposition NO-GO Verdict - WI-5249 Prime NO-ACTION Claim/Filer

## Owner Decisions / Input

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - owner-decision evidence supplied to this command.
- `PAUTH-DISPATCHER-BLACK-BOX-WI5403-DECLARED-TARGET-SCOPE-20260717` - active project authorization covering `WI-5403`.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "after_behavior": "declared mutation scope is exposed separately from normalized cited/applicability path evidence in JSON and Markdown output",
  "applicability": "applicable",
  "baseline": {
    "current_preflight_output": "declared plus incidental path evidence can be conflated in target_paths"
  },
  "before_behavior": "packet.target_paths can contain declared paths mixed with incidental prose/applicability path evidence",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 plus DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001",
  "essential_context_preservation": "reviewers retain both conservative applicability evidence and a precise mutation-scope allowlist while preserving related shared-file ownership boundaries",
  "expected_result": {
    "current_preflight_output": "declared target scope and cited/applicability path evidence are separately observable with deterministic packet hash behavior"
  },
  "fail_closed_conditions": [
    "shared-file byte drift before implementation start",
    "declared target scope remains indistinguishable from prose/cited path evidence",
    "missing-parent warnings regress to incidental prose paths",
    "implementation attempts without exact GO, claim, and start packet"
  ],
  "hard_invariants": [
    "do not weaken conservative spec applicability matching",
    "do not adopt WI-5387 or WI-5408 shared-file hunks",
    "do not treat gtkb-research-clean-branch-publication as WI-5403 authority"
  ],
  "history_preservation": "existing WI-5363, WI-5387, WI-5408, and research-clean-branch bridge history remains append-only and explicitly non-adopted",
  "obsolete_guidance_disposition": "older mixed target_paths output is treated as false-closure residue and not retained as authoritative mutation scope",
  "primary_route": "bridge_applicability_preflight declared target-scope separation",
  "provenance": "WI-5403 false-closure residue after WI-5363 terminal metadata; fleet hardening authorization DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION",
  "rollback": {
    "instructions": "revert only WI-5403-owned hunks in scripts/bridge_applicability_preflight.py and platform_tests/scripts/test_bridge_applicability_preflight.py",
    "test": "python -m pytest platform_tests/scripts/test_bridge_applicability_preflight.py -q --tb=short"
  },
  "schema_version": 1,
  "self_descriptive_naming": "field and heading names distinguish declared target paths from cited applicability path evidence"
}
```

## Known Non-Authoritative Thread

- `gtkb-research-clean-branch-publication` currently cites `WI-5403` under a conflicting project and is latest `NO-ACTION`; WI-5409 owns that proposal-linkage defect. This WI-5403 proposal does not rely on that thread as approval, implementation scope, or evidence.

## Proposed Scope

- Separate exact declared mutation scope from normalized cited/applicability path evidence in bridge_applicability_preflight output so packet.target_paths and Markdown cannot be mistaken for incidental prose path evidence.
- Preserve conservative path-driven specification applicability, packet hashing, and missing-parent warning behavior; missing-parent warnings must remain tied to deliberate implementation fields, not incidental prose citations.
- Preserve WI-5387 operative-version-after-NO-ACTION behavior and WI-5408 PAUTH amendment owner-evidence validation as separate shared-file concerns; implementation must sequence against exact shared pre-start bytes and must not adopt or overwrite foreign hunks.
- Treat the existing gtkb-research-clean-branch-publication NO-ACTION thread as an unrelated cross-project metadata defect owned by WI-5409, not as an implementation proposal for WI-5403.
- No protected source/test mutation is authorized until independent GO, matching claim, implementation-start packet, and shared-file ownership checks are present.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live applicability plus ADR/DCL clause preflights with no missing required specs. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Confirm numbered bridge proposal, GO, report, and verification chain remains role-correct and append-only. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Bind focused tests in platform_tests/scripts/test_bridge_applicability_preflight.py to the linked specs before requesting VERIFIED. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Confirm Project, Work Item, PAUTH, target_paths, and owner-decision metadata match the black-box project membership and do not reuse the research-clean-branch mismatch. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-WORK-TREE-HYGIENE-001` | Run focused tests proving incidental prose paths no longer appear as declared mutation target scope while shared foreign hunks remain excluded from WI-5403 finalization. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Run focused applicability-preflight regressions proving declared-scope separation does not impair conservative applicability matching, corrected operative-version handling, or WI-5408 owner-evidence validation. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Run implementation_authorization.py begin after GO and confirm only the two declared shared target paths are authorized under PAUTH-DISPATCHER-BLACK-BOX-WI5403-DECLARED-TARGET-SCOPE-20260717. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` | Document exact shared-file pre-start bytes and sequence WI-5403 relative to WI-5387, WI-5408, and WI-5386 before implementation start. |

## Acceptance Criteria

- Applicability JSON exposes exact declared target scope separately from normalized cited/applicability path evidence.
- Markdown output labels declared target paths and cited/applicability evidence distinctly enough that reviewers cannot confuse mutation scope with prose citations.
- Existing required/advisory spec applicability matches and packet hashes remain deterministic; conservative path-driven matching is not weakened.
- Focused applicability-preflight tests cover declared-scope separation while preserving operative-version-after-NO-ACTION and WI-5408 owner-evidence behavior.
- Finalization is sequenced through WI-5386 physical-residue closure and avoids whole-file attribution of shared dirty content.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/bridge_applicability_preflight.py`
- `platform_tests/scripts/test_bridge_applicability_preflight.py`

## Recommended Commit Type

`feat`
