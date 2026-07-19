NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: GPT-5 Codex
author_model_version: 5
author_model_configuration: OpenAI Codex desktop interactive; reasoning=xhigh; approval_policy=never
author_metadata_source: codex-inline-non-bypass-writer

# Implementation Proposal - Restore PAUTH amendment owner-evidence checks in applicability preflight

bridge_kind: prime_proposal
Document: gtkb-wi5408-pauth-amendment-owner-evidence-applicability
Version: 001
Date: 2026-07-17 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS
Work Item: WI-5408

target_paths: ["scripts/bridge_applicability_preflight.py", "platform_tests/scripts/test_bridge_applicability_preflight.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

WI-5408 proposal to restore structured PAUTH amendment owner-evidence validation inside bridge applicability preflight while preserving WI-5403 shared-file boundaries.

Work item description: WI-5254 is terminal/resolved, and WI-5346 restored the structured amendment validator in scripts/implementation_authorization.py: its nine focused validator/backstop tests pass. However, scripts/bridge_applicability_preflight.py still never invokes that validator or emits blocking_errors, so five existing preflight tests fail: missing owner packet is accepted; exact owner evidence has no blocking_errors field; out-of-root, malformed, non-owner, identity-conflicting, and non-covering packets are not rejected before GO. Integrate the canonical validator into build_packet, preserve current operative-version-after-NO-ACTION work and WI-5403 declared target-scope separation, surface deterministic blocking diagnostics, and do not consume implementation claims.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5408` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/bridge_applicability_preflight.py`, `platform_tests/scripts/test_bridge_applicability_preflight.py`.

## Specification Links

- `DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001` - auto-linked governing or work-item specification.
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
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - auto-linked governing or work-item specification.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded project implementation authority.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - auto-linked governing or work-item specification.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20265025` - Loyal Opposition Verification - WI-4556 Ollama Provider Fallback Backoff
- `DELIB-202665788` - WI-5009 Spec-Before-Code Structured Bridge Coverage — Loyal Opposition Review Verdict: GO
- `DELIB-20265012` - Loyal Opposition Verification - WI-4251 Diagnostic Write Envelope
- `DELIB-20265695` - Loyal Opposition Review - WI-4403 Advisory Router Compact Skipped-Existing Test
- `DELIB-20264300` - Loyal Opposition Review - Loop Coordinator Lifecycle Correction Scope

## Owner Decisions / Input

- `DELIB-202666274` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715-PROJECT-SCOPE` - active project authorization covering `WI-5408`.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "after_behavior": "missing or invalid owner-evidence packets fail closed with deterministic blocking_errors before a GO is accepted as applicable",
  "applicability": "applicable",
  "baseline": {
    "focused_applicability_preflight": "5 failed / 26 passed per WI-5403/WI-5408 shared-file status detail"
  },
  "before_behavior": "structured PAUTH amendment packets without valid owner evidence can be accepted without blocking_errors in applicability preflight",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 plus DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001",
  "essential_context_preservation": "reviewers can still distinguish declared target_paths, cited applicability paths, PAUTH amendment owner evidence, and corrected operative-version behavior",
  "expected_result": {
    "focused_applicability_preflight": "owner-evidence regressions pass with no regression of operative-version-after-NO-ACTION behavior"
  },
  "fail_closed_conditions": [
    "missing owner packet for a real amendment delta",
    "malformed or out-of-root owner evidence",
    "non-owner, identity-conflicting, or non-covering packet evidence",
    "shared-file byte drift before implementation start"
  ],
  "hard_invariants": [
    "do not consume implementation claims during applicability preflight",
    "do not mutate dispatcher, TAFE, runtime, or retained telemetry state",
    "preserve WI-5403 declared-target-scope separation as a separate ownership lane"
  ],
  "history_preservation": "existing bridge history, dirty shared-file hunks, and terminal WI-5254/WI-5346 evidence remain append-only and distinguishable",
  "obsolete_guidance_disposition": "older acceptance of missing owner evidence is treated as false-closure residue and not preserved as active behavior",
  "primary_route": "bridge_applicability_preflight build_packet structured owner-evidence validation",
  "provenance": "WI-5408 current-head applicability-preflight false-closure residue; owner directive DELIB-202666274 keeps Authority Foundations non-impairment gates active.",
  "rollback": {
    "instructions": "revert only scripts/bridge_applicability_preflight.py and platform_tests/scripts/test_bridge_applicability_preflight.py hunks owned by WI-5408",
    "test": "python -m pytest platform_tests/scripts/test_bridge_applicability_preflight.py -q --tb=short"
  },
  "schema_version": 1,
  "self_descriptive_naming": "blocking_errors and focused tests name owner-evidence validity, packet coverage, and amendment identity failure classes"
}
```

## Proposed Scope

- Integrate the canonical structured PAUTH amendment owner-evidence validator into bridge_applicability_preflight build_packet so amendment packets with missing, malformed, out-of-root, non-owner, identity-conflicting, or non-covering owner evidence fail closed with deterministic blocking_errors.
- Preserve current operative-version-after-NO-ACTION behavior and the separate WI-5403 declared-target-scope separation responsibility; this work must not adopt, overwrite, or finalize either shared-file hunk without exact current-byte sequencing.
- Do not consume implementation claims during preflight, mutate dispatcher or TAFE state, or weaken conservative applicability/spec-link harvesting.
- No protected source/test mutation is authorized until independent GO, matching claim, implementation-start packet, and exact shared-file ownership checks are present.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001` | Exercise missing, malformed, out-of-root, non-owner, identity-conflicting, and non-covering owner-evidence packets through bridge_applicability_preflight and assert deterministic blocking_errors. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Confirm numbered bridge proposal, GO, report, and verification chain remains role-correct and append-only. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live applicability plus ADR/DCL clause preflights with no missing required specs. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Bind the focused applicability-preflight regressions to these linked specs before requesting VERIFIED. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Confirm Project, Work Item, PAUTH, target_paths, and owner-decision metadata are present and match MemBase membership. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Confirm applicability preflight validates owner evidence without consuming implementation claims or bypassing implementation-start authority. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Run implementation_authorization.py begin after GO and confirm only the two declared shared target paths are authorized. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Run focused regression tests proving operative-version-after-NO-ACTION behavior and WI-5403 target-scope separation assumptions are preserved. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` | Document exact shared-file pre-start bytes and sequence WI-5408 relative to WI-5403 before implementation start. |

## Acceptance Criteria

- The five currently failing applicability-preflight tests for structured PAUTH amendment owner evidence pass without regressing the existing 26 passing cases.
- build_packet emits deterministic blocking_errors for missing owner packets and invalid owner evidence classes before a GO can be treated as applicable.
- The implementation preserves corrected operative-version handling and leaves WI-5403 declared-target-scope separation as a distinct owned concern.
- Focused test run python -m pytest platform_tests/scripts/test_bridge_applicability_preflight.py -q --tb=short passes or reports only explicitly unrelated pre-existing failures.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/bridge_applicability_preflight.py`
- `platform_tests/scripts/test_bridge_applicability_preflight.py`

## Recommended Commit Type

`feat`
