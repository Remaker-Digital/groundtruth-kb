NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: reasoning_effort=xhigh; thread_source=user
author_metadata_source: x-codex-turn-metadata

# Implementation Proposal - OpenRouter F retries VERIFIED publication that requires unavailable atomic commit finalization

bridge_kind: prime_proposal
Document: gtkb-wi5576-provider-verified-finalization-guard-ordering
Version: 001
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE","coverage":"project_membership_fallback","included_work_item_count":null,"specificity_rank":[2,0],"selected":true}]
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5576

target_paths: ["scripts/gtkb_bridge_writer.py", "platform_tests/scripts/test_lo_verified_commit_atomicity.py", "bridge/hunks/gtkb-wi5576-provider-verified-finalization-guard-ordering.patch"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Repair the provider VERIFIED publication ordering defect that runs bridge compliance before the canonical atomic finalizer has appended mandatory commit-finalization evidence. Preserve credential scanning before finalization and preserve the full guard path for GO/NO-GO. Use hunk-scoped implementation/finalization so concurrent WI-5422 model-provenance changes remain untouched.

Work item description: Genuine OpenRouter F LO dispatch 2026-07-18T18-25-55Z-loyal-opposition-F-be6ad3 exited 1 after the governed publisher recovery exhausted four attempts. The canonical dispatcher classified guard_denial; bounded diagnostic readback showed every attempt was rejected because a VERIFIED verdict lacked Commit Finalization Evidence and a same-transaction path set. This is a fresh recurrence of WI-5040 capability-blind finalization routing in the active A/D/F acceptance program. Diagnose and provide a governed path that either routes finalization-required work to a finalization-capable independent LO context or emits a stable reroutable result without treating the provider run as successful. Preserve F dispatchability, current topology, full allowances, fail-closed VERIFIED commit-finalization, and bridge/lease integrity.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5576` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/gtkb_bridge_writer.py`, `platform_tests/scripts/test_lo_verified_commit_atomicity.py`, `bridge/hunks/gtkb-wi5576-provider-verified-finalization-guard-ordering.patch`.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - auto-linked governing or work-item specification.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - auto-linked governing or work-item specification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - auto-linked governing or work-item specification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform command out of adopter application scope.
- `GOV-STANDING-BACKLOG-001` - auto-linked governing or work-item specification.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - auto-linked governing or work-item specification.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - auto-linked governing or work-item specification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202666421` - Loyal Opposition Disposition Verdict - WI-5240 WI-5236 PAUTH Registered Vocabulary Stand-Down
- `DELIB-20260716-WI5169-ALIBABA-H-REARM-BUDGET-LIVE` - Owner decision: Alibaba budget live; re-arm harness H dispatch eligibility now (WI-5169 EXPEDITE)
- `DELIB-202666159` - WI-5204 Stop-Hook Outcome Preservation With Genuine H Proof — Post-Implementation Verification
- `DELIB-202666162` - WI-5204 Successor — Stop-Hook Outcome Preservation — Post-Implementation Verification
- `DELIB-202665849` - Loyal Opposition Verdict: OpenRouter direct timeout retry (WI-5060)

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE` - active project authorization covering `WI-5576`.

## Proposed Scope

- For VERIFIED provider publication, retain the credential scanner preflight but defer bridge-compliance validation to the canonical atomic finalizer after it appends Commit Finalization Evidence.
- Keep GO and NO-GO on the existing complete provider-verdict guard sequence without weakening role, claim, transition, metadata, hunk-integrity, evidence-anchor, or append-only checks.
- Add a focused regression in the clean atomic-finalization test module and preserve the concurrent WI-5422 hunks in scripts/gtkb_bridge_writer.py through an exact reviewed hunk patch.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5576; PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "Genuine OpenRouter F LO dispatch 2026-07-18T18-25-55Z-loyal-opposition-F-be6ad3 exited 1 after the governed publisher recovery exhausted four attempts. The canonical dispatcher classified guard_denial; bounded diagnostic readback showed every attempt was rejected because a VERIFIED verdict lacked Commit Finalization Evidence and a same-transaction path set. This is a fresh recurrence of WI-5040 capability-blind finalization routing in the active A/D/F acceptance program. Diagnose and provide a governed path that either routes finalization-required work to a finalization-capable independent LO context or emits a stable reroutable result without treating the provider run as successful. Preserve F dispatchability, current topology, full allowances, fail-closed VERIFIED commit-finalization, and bridge/lease integrity.",
  "after_behavior": "Repair the provider VERIFIED publication ordering defect that runs bridge compliance before the canonical atomic finalizer has appended mandatory commit-finalization evidence. Preserve credential scanning before finalization and preserve the full guard path for GO/NO-GO. Use hunk-scoped implementation/finalization so concurrent WI-5422 model-provenance changes remain untouched.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5576",
    "project": "PROJECT-GTKB-GOOSE-HARNESS-ADOPTION",
    "target_paths": [
      "scripts/gtkb_bridge_writer.py",
      "platform_tests/scripts/test_lo_verified_commit_atomicity.py",
      "bridge/hunks/gtkb-wi5576-provider-verified-finalization-guard-ordering.patch"
    ],
    "linked_specifications": [
      "SPEC-CENTRALIZED-DISPATCH-SERVICE-001",
      "GOV-FILE-BRIDGE-AUTHORITY-001",
      "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001",
      "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001",
      "DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001",
      "DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001",
      "SPEC-AUQ-POLICY-ENGINE-001",
      "ADR-ISOLATION-APPLICATION-PLACEMENT-001",
      "GOV-STANDING-BACKLOG-001",
      "ADR-CODEX-HOOK-PARITY-FALLBACK-001",
      "ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001",
      "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"
    ]
  },
  "expected_result": {
    "summary": "Repair the provider VERIFIED publication ordering defect that runs bridge compliance before the canonical atomic finalizer has appended mandatory commit-finalization evidence. Preserve credential scanning before finalization and preserve the full guard path for GO/NO-GO. Use hunk-scoped implementation/finalization so concurrent WI-5422 model-provenance changes remain untouched.",
    "scope": [
      "For VERIFIED provider publication, retain the credential scanner preflight but defer bridge-compliance validation to the canonical atomic finalizer after it appends Commit Finalization Evidence.",
      "Keep GO and NO-GO on the existing complete provider-verdict guard sequence without weakening role, claim, transition, metadata, hunk-integrity, evidence-anchor, or append-only checks.",
      "Add a focused regression in the clean atomic-finalization test module and preserve the concurrent WI-5422 hunks in scripts/gtkb_bridge_writer.py through an exact reviewed hunk patch."
    ],
    "acceptance_criteria": [
      "A provider-backed VERIFIED verdict lacking a pre-authored Commit Finalization Evidence section reaches the canonical atomic finalizer, which appends the section, writes the verdict, creates the focused local commit, returns verdict_path and commit_sha, and releases the claim exactly once.",
      "The credential scanner still runs before provider VERIFIED finalization, while the pre-finalizer bridge-compliance gate does not reject the body that only the finalizer can complete.",
      "GO and NO-GO continue to run both existing provider verdict guards; invalid VERIFIED bodies, unsafe include paths, missing hunk coverage, fabricated evidence, self-review, and finalization failures remain fail closed.",
      "The focused provider atomic-finalization and writer suites pass, Ruff check/format pass, and a fresh substantive F dispatch no longer ends in the missing Commit Finalization Evidence guard-denial loop."
    ]
  },
  "rollback": {
    "instructions": "Revert only the approved source and test implementation targets under separate authority.",
    "verification": "Rerun the proposal's specification-derived tests and bridge preflights."
  },
  "hard_invariants": [
    "Bridge review, implementation-start, and independent verification gates remain mandatory.",
    "Only the declared in-root target paths are attributable to this implementation proposal.",
    "Dispatcher, TAFE, credential, deployment, release, and unrelated work remain outside generated authority."
  ],
  "fail_closed_conditions": [
    "Project membership or active PAUTH coverage is missing.",
    "Target paths escape the project root or candidate/live preflights fail.",
    "Required proposal evidence is empty, malformed, duplicated, or still contains authoring placeholders."
  ],
  "essential_context_preservation": "The generated proposal retains PAUTH, project, work item, targets, specifications, prior deliberations, owner decisions, scope, verification, acceptance, risk, rollback, and expected file changes."
}
```

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | TEST-11623 plus focused provider atomic-finalization regression and fresh substantive F dispatcher proof |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Existing GO/NO-GO guard-denial tests plus VERIFIED finalizer write-path assertions |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest, Ruff check, Ruff format check, exact diff, and hunk-integrity validation |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |

## Acceptance Criteria

- A provider-backed VERIFIED verdict lacking a pre-authored Commit Finalization Evidence section reaches the canonical atomic finalizer, which appends the section, writes the verdict, creates the focused local commit, returns verdict_path and commit_sha, and releases the claim exactly once.
- The credential scanner still runs before provider VERIFIED finalization, while the pre-finalizer bridge-compliance gate does not reject the body that only the finalizer can complete.
- GO and NO-GO continue to run both existing provider verdict guards; invalid VERIFIED bodies, unsafe include paths, missing hunk coverage, fabricated evidence, self-review, and finalization failures remain fail closed.
- The focused provider atomic-finalization and writer suites pass, Ruff check/format pass, and a fresh substantive F dispatch no longer ends in the missing Commit Finalization Evidence guard-denial loop.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/gtkb_bridge_writer.py`
- `platform_tests/scripts/test_lo_verified_commit_atomicity.py`
- `bridge/hunks/gtkb-wi5576-provider-verified-finalization-guard-ordering.patch`

## Recommended Commit Type

`feat`
