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

# Implementation Proposal - Give provider verdict recovery a deterministic applicability-preflight path

bridge_kind: prime_proposal
Document: gtkb-wi5600-provider-applicability-preflight-recovery
Version: 001
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE","coverage":"project_membership_fallback","included_work_item_count":null,"specificity_rank":[2,0],"selected":true}]
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5600

target_paths: ["scripts/gtkb_bridge_writer.py", "scripts/bridge_applicability_preflight.py", "scripts/cloud_harness_base.py", "scripts/ollama_harness.py", "platform_tests/scripts/test_provider_verdict_applicability_recovery.py", "bridge/hunks/gtkb-wi5600-provider-applicability-preflight-recovery.patch"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Give provider-backed GO and VERIFIED publication a deterministic canonical applicability-evidence path that does not depend on unavailable recovery tools, preserves fail-closed governance, and serializes behind WI-5554 and the overlapping provider-recovery chain.

Work item description: Genuine OpenRouter F Loyal Opposition dispatch 2026-07-18T20-29-03Z-loyal-opposition-F-1974bb performed a substantive review of gtkb-wi5216-provider-verdict-denial-loop-recovery, then exited 1 after 287 seconds and four governed publication attempts. Canonical stderr reports that every attempt was denied because the GO/VERIFIED body lacked a clean Applicability Preflight section with packet_hash and missing_required_specs: []. The dispatch prompt already carries the terminal WI-4388 remedy telling reviewers to run the canonical preflight, but once the first publish is denied, publisher-only recovery exposes only PublishBridgeVerdict, so the worker cannot execute the prescribed preflight command or obtain deterministic evidence and simply repeats an unsatisfiable request. Provide a trusted deterministic preflight/enrichment path for provider-backed GO/VERIFIED publication that computes evidence against the exact current source and final candidate contract, coordinates with WI-5554 candidate-evidence freshness, and never fabricates, guesses, or weakens applicability. NO-GO remains valid without a mandatory section. Preserve role, transition, claim, author provenance, credential, finalization, full allowances, D/F parity, and current dispatcher topology.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5600` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/gtkb_bridge_writer.py`, `scripts/bridge_applicability_preflight.py`, `scripts/cloud_harness_base.py`, `scripts/ollama_harness.py`, `platform_tests/scripts/test_provider_verdict_applicability_recovery.py`, `bridge/hunks/gtkb-wi5600-provider-applicability-preflight-recovery.patch`.

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
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` - auto-linked governing or work-item specification.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - auto-linked governing or work-item specification.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - auto-linked governing or work-item specification.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - auto-linked governing or work-item specification.
- `DCL-OLLAMA-TOOL-PARITY-GATE-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202666221` - WI-5139 - Restore fleet-goal MemBase carriers - Post-Implementation Verification
- `DELIB-202666183` - Loyal Opposition Verdict — WI-5216 Bound provider bridge-verdict denial loops and recover through the governed publisher
- `DELIB-202666304` - Loyal Opposition GO Verdict - WI-5280 Native PreToolUse Timeout Recovery
- `DELIB-20265502` - Loyal Opposition verification verdict - WI-4703 dispatch non-transient fast-trip
- `DELIB-202666140` - Loyal Opposition Verdict — WI-5189 / WI-5195 Document-Authoritative GO-Claim Corrective Finalization (VERIFIED: the corrected single-patch commit collects and passes in isolation)

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE` - active project authorization covering `WI-5600`.

## Proposed Scope

- Expose the canonical applicability packet builder as an in-process deterministic service over the exact current Responds-to bridge artifact; do not depend on CLI prose, harness scratchpads, or noncanonical evidence.
- When a provider-authored GO or VERIFIED candidate lacks the mandatory Applicability Preflight section, compute the packet against the exact canonical source and materialize it only when preflight passes with missing_required_specs empty, then bind the evidence to final candidate bytes under WI-5554 freshness rules.
- Never manufacture a passing packet, omit an applicable specification, alter the substantive verdict, weaken transition or role checks, or bypass credential, claim, provenance, compliance, finalization, or project-authorization enforcement.
- Teach cloud and Ollama publisher recovery to classify deterministic applicability-service failure as non-repairable for that candidate and stop after one stable actionable diagnostic instead of repeating an unsatisfiable PublishBridgeVerdict request.
- Serialize protected implementation after WI-5554, WI-5422, WI-5471, WI-5495, WI-5576, WI-5578, and WI-5599 unless an independent LO verdict explicitly approves one combined exact-hunk plan with clean ownership.

## Cross-Harness Disposition

- **A**: Prime Builder only; may prepare corrected candidates but must never author GO, NO-GO, or VERIFIED.
- **B**: Parity-covered provider surface; not required for the current A/D/F qualification topology.
- **C**: Parity-covered provider surface; not required for the current A/D/F qualification topology.
- **D**: Operative Ollama Loyal Opposition lane; must receive the deterministic applicability path and pass fresh target-authored dispatcher proof.
- **E**: Parity-covered native harness surface; no source change required unless shared governed-writer regressions expose one.
- **F**: Operative OpenRouter Loyal Opposition lane and reproducer; must publish once or fail once with a stable actionable diagnostic.
- **G**: Not an operative harness; retired registry metadata only and excluded from qualification.
- **H**: Parity-covered provider surface; not required for the current A/D/F qualification topology.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5600; PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "Genuine OpenRouter F Loyal Opposition dispatch 2026-07-18T20-29-03Z-loyal-opposition-F-1974bb performed a substantive review of gtkb-wi5216-provider-verdict-denial-loop-recovery, then exited 1 after 287 seconds and four governed publication attempts. Canonical stderr reports that every attempt was denied because the GO/VERIFIED body lacked a clean Applicability Preflight section with packet_hash and missing_required_specs: []. The dispatch prompt already carries the terminal WI-4388 remedy telling reviewers to run the canonical preflight, but once the first publish is denied, publisher-only recovery exposes only PublishBridgeVerdict, so the worker cannot execute the prescribed preflight command or obtain deterministic evidence and simply repeats an unsatisfiable request. Provide a trusted deterministic preflight/enrichment path for provider-backed GO/VERIFIED publication that computes evidence against the exact current source and final candidate contract, coordinates with WI-5554 candidate-evidence freshness, and never fabricates, guesses, or weakens applicability. NO-GO remains valid without a mandatory section. Preserve role, transition, claim, author provenance, credential, finalization, full allowances, D/F parity, and current dispatcher topology.",
  "after_behavior": "Give provider-backed GO and VERIFIED publication a deterministic canonical applicability-evidence path that does not depend on unavailable recovery tools, preserves fail-closed governance, and serializes behind WI-5554 and the overlapping provider-recovery chain.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5600",
    "project": "PROJECT-GTKB-GOOSE-HARNESS-ADOPTION",
    "target_paths": [
      "scripts/gtkb_bridge_writer.py",
      "scripts/bridge_applicability_preflight.py",
      "scripts/cloud_harness_base.py",
      "scripts/ollama_harness.py",
      "platform_tests/scripts/test_provider_verdict_applicability_recovery.py",
      "bridge/hunks/gtkb-wi5600-provider-applicability-preflight-recovery.patch"
    ],
    "linked_specifications": [
      "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001",
      "GOV-FILE-BRIDGE-AUTHORITY-001",
      "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001",
      "DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001",
      "DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001",
      "SPEC-AUQ-POLICY-ENGINE-001",
      "ADR-ISOLATION-APPLICATION-PLACEMENT-001",
      "GOV-STANDING-BACKLOG-001",
      "ADR-CODEX-HOOK-PARITY-FALLBACK-001",
      "ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001",
      "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001",
      "GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001",
      "DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001",
      "SPEC-CENTRALIZED-DISPATCH-SERVICE-001",
      "GOV-HARNESS-ONBOARDING-CONTRACT-001",
      "DCL-OLLAMA-TOOL-PARITY-GATE-001"
    ]
  },
  "expected_result": {
    "summary": "Give provider-backed GO and VERIFIED publication a deterministic canonical applicability-evidence path that does not depend on unavailable recovery tools, preserves fail-closed governance, and serializes behind WI-5554 and the overlapping provider-recovery chain.",
    "scope": [
      "Expose the canonical applicability packet builder as an in-process deterministic service over the exact current Responds-to bridge artifact; do not depend on CLI prose, harness scratchpads, or noncanonical evidence.",
      "When a provider-authored GO or VERIFIED candidate lacks the mandatory Applicability Preflight section, compute the packet against the exact canonical source and materialize it only when preflight passes with missing_required_specs empty, then bind the evidence to final candidate bytes under WI-5554 freshness rules.",
      "Never manufacture a passing packet, omit an applicable specification, alter the substantive verdict, weaken transition or role checks, or bypass credential, claim, provenance, compliance, finalization, or project-authorization enforcement.",
      "Teach cloud and Ollama publisher recovery to classify deterministic applicability-service failure as non-repairable for that candidate and stop after one stable actionable diagnostic instead of repeating an unsatisfiable PublishBridgeVerdict request.",
      "Serialize protected implementation after WI-5554, WI-5422, WI-5471, WI-5495, WI-5576, WI-5578, and WI-5599 unless an independent LO verdict explicitly approves one combined exact-hunk plan with clean ownership."
    ],
    "acceptance_criteria": [
      "TEST-11649 proves a provider GO or VERIFIED candidate with complete specification linkage but no embedded section receives the exact canonical applicability packet and publishes exactly once through the governed writer.",
      "Missing required specifications, stale source identity, malformed candidate structure, packet-hash mismatch, candidate-evidence mismatch, or deterministic service failure causes no verdict write and one stable diagnostic without four identical recovery attempts.",
      "NO-GO remains valid without a mandatory applicability section, and existing transition, role, author provenance, claim, credential, bridge-compliance, commit-finalization, and operation-time authorization guards remain green.",
      "Fresh substantive dispatcher-produced F and D reviews exit zero and publish target-authored governed verdicts; A remains Prime Builder only and dispatcher configuration, roles, eligibility, routing, caps, and allowances are unchanged."
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
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run TEST-11649 success, missing-spec, and exact-Responds-to identity cases against canonical proposal links. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run governed writer role, transition, claim, provenance, and no-write failure regressions for GO, NO-GO, and VERIFIED. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` | Prove byte-stable packet generation and a single stable failure diagnostic across repeated identical candidates. |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Run candidate and live applicability plus mandatory clause preflights and verify final candidate evidence binding. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Inspect canonical dispatcher telemetry for fresh D/F exit-zero completion, per-document verdict paths, released leases, and zero topology mutation. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Run provider harness regression suites and one fresh substantive dispatch per operative provider LO lane. |
| `DCL-OLLAMA-TOOL-PARITY-GATE-001` | Run equivalent D and F applicability-recovery fixtures and prove neither provider requires an unavailable tool after recovery begins. |

## Acceptance Criteria

- TEST-11649 proves a provider GO or VERIFIED candidate with complete specification linkage but no embedded section receives the exact canonical applicability packet and publishes exactly once through the governed writer.
- Missing required specifications, stale source identity, malformed candidate structure, packet-hash mismatch, candidate-evidence mismatch, or deterministic service failure causes no verdict write and one stable diagnostic without four identical recovery attempts.
- NO-GO remains valid without a mandatory applicability section, and existing transition, role, author provenance, claim, credential, bridge-compliance, commit-finalization, and operation-time authorization guards remain green.
- Fresh substantive dispatcher-produced F and D reviews exit zero and publish target-authored governed verdicts; A remains Prime Builder only and dispatcher configuration, roles, eligibility, routing, caps, and allowances are unchanged.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/gtkb_bridge_writer.py`
- `scripts/bridge_applicability_preflight.py`
- `scripts/cloud_harness_base.py`
- `scripts/ollama_harness.py`
- `platform_tests/scripts/test_provider_verdict_applicability_recovery.py`
- `bridge/hunks/gtkb-wi5600-provider-applicability-preflight-recovery.patch`

## Recommended Commit Type

`feat`
