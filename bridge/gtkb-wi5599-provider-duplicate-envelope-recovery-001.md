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

# Implementation Proposal - Canonicalize duplicate provider artifact-head envelope pairs before verdict publication

bridge_kind: prime_proposal
Document: gtkb-wi5599-provider-duplicate-envelope-recovery
Version: 001
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE","coverage":"project_membership_fallback","included_work_item_count":null,"specificity_rank":[2,0],"selected":true}]
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5599

target_paths: ["scripts/gtkb_bridge_writer.py", "scripts/cloud_harness_base.py", "scripts/ollama_harness.py", "platform_tests/scripts/test_provider_verdict_envelope_recovery.py", "bridge/hunks/gtkb-wi5599-provider-duplicate-envelope-recovery.patch"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Repair provider-backed verdict publication so duplicate exact canonical artifact-head envelope pairs converge deterministically while conflicting envelope structure fails once with a stable actionable diagnostic. Serialize this sibling with WI-5578 and preserve the current A PB plus D/F LO topology.

Work item description: Genuine OpenRouter F Loyal Opposition dispatch 2026-07-18T20-21-40Z-loyal-opposition-F-5e204d selected two substantive bridge documents, entered governed publisher recovery, and exited 1 after 391 seconds with both documents incomplete. Canonical stderr reports that all four PublishBridgeVerdict attempts failed because the provider verdict body contained duplicate artifact-head envelope lines: bridge artifact-head envelope must contain exactly one ::init line and exactly one ::open line. The governed writer owns these deterministic status-derived lines, but normalize_bridge_envelope_head currently rejects duplicate provider-authored pairs before it can materialize the canonical line-2/line-3 pair, while generic recovery repeats the same structural request through the full budget. Add a provider-specific bounded correction/canonicalization path that can collapse only duplicate exact expected envelope pairs to one canonical pair without changing substantive GO/NO-GO/VERIFIED intent. Conflicting, malformed, wrong-role, wrong-activity, or body-level envelope directives must remain fail closed with a stable non-repeating diagnostic. Preserve role, transition, claim, metadata, credential, finalization, generous allowance, D/F parity, and current dispatcher topology.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5599` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/gtkb_bridge_writer.py`, `scripts/cloud_harness_base.py`, `scripts/ollama_harness.py`, `platform_tests/scripts/test_provider_verdict_envelope_recovery.py`, `bridge/hunks/gtkb-wi5599-provider-duplicate-envelope-recovery.patch`.

## Specification Links

- `ADR-BRIDGE-ARTIFACT-HEAD-ENVELOPE-001` - auto-linked governing or work-item specification.
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
- `DCL-BRIDGE-ENVELOPE-LINE-AUTHORING-PLACEMENT-001` - auto-linked governing or work-item specification.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - auto-linked governing or work-item specification.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - auto-linked governing or work-item specification.
- `DCL-OLLAMA-TOOL-PARITY-GATE-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202666257` - Loyal Opposition Proposal Review - WI-5253 Ollama D Publisher Failure Recovery
- `DELIB-20261448` - Loyal Opposition Verification - Artifact Recorder CLI Slice 4 Owner-Decision Auto-Archive
- `DELIB-202665173` - Verdict Summary
- `DELIB-202666181` - WI-5214 Post-Implementation Verification Verdict — VERIFIED
- `DELIB-202666159` - WI-5204 Stop-Hook Outcome Preservation With Genuine H Proof — Post-Implementation Verification

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE` - active project authorization covering `WI-5599`.

## Proposed Scope

- Add a provider-publication-only envelope canonicalizer before the general bridge-envelope validator. It may collapse repeated exact expected status-derived ::init/::open pairs found in the artifact-head preamble to one canonical pair on fixed lines 2 and 3; it must not alter the status token or substantive verdict body.
- Reject malformed, mismatched-role, mismatched-activity, partial, or misplaced envelope directives with a stable structured error code and no bridge write. Never infer or rewrite GO, NO-GO, or VERIFIED.
- Teach the cloud and Ollama publisher-recovery loops to recognize only the stable envelope-structure diagnostic, offer at most one explicit correction turn where canonicalization is not safe, and stop before four identical retries on recurrence.
- Treat WI-5578 as a shared-target sibling: implementation must occur after WI-5422, WI-5471, WI-5495, WI-5576, and WI-5578 are terminal, or under one independently reviewed combined hunk plan that proves exact ownership and preserves all foreign bytes.

## Cross-Harness Disposition

- **A**: PB-only behavior unchanged; no provider verdict writer authority is added.
- **B**: Shared writer remains fail closed; no direct harness change.
- **C**: Shared writer remains fail closed; no direct harness change.
- **D**: Receives parity-safe Ollama recovery and must supply fresh substantive dispatcher proof.
- **E**: No direct harness change; shared writer remains fail closed.
- **F**: Receives cloud recovery and must supply fresh substantive dispatcher proof for the exact reproduced failure class.
- **H**: Cloud-loop inheritance must remain nonimpaired by focused regression tests.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5599; PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "Genuine OpenRouter F Loyal Opposition dispatch 2026-07-18T20-21-40Z-loyal-opposition-F-5e204d selected two substantive bridge documents, entered governed publisher recovery, and exited 1 after 391 seconds with both documents incomplete. Canonical stderr reports that all four PublishBridgeVerdict attempts failed because the provider verdict body contained duplicate artifact-head envelope lines: bridge artifact-head envelope must contain exactly one ::init line and exactly one ::open line. The governed writer owns these deterministic status-derived lines, but normalize_bridge_envelope_head currently rejects duplicate provider-authored pairs before it can materialize the canonical line-2/line-3 pair, while generic recovery repeats the same structural request through the full budget. Add a provider-specific bounded correction/canonicalization path that can collapse only duplicate exact expected envelope pairs to one canonical pair without changing substantive GO/NO-GO/VERIFIED intent. Conflicting, malformed, wrong-role, wrong-activity, or body-level envelope directives must remain fail closed with a stable non-repeating diagnostic. Preserve role, transition, claim, metadata, credential, finalization, generous allowance, D/F parity, and current dispatcher topology.",
  "after_behavior": "Repair provider-backed verdict publication so duplicate exact canonical artifact-head envelope pairs converge deterministically while conflicting envelope structure fails once with a stable actionable diagnostic. Serialize this sibling with WI-5578 and preserve the current A PB plus D/F LO topology.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5599",
    "project": "PROJECT-GTKB-GOOSE-HARNESS-ADOPTION",
    "target_paths": [
      "scripts/gtkb_bridge_writer.py",
      "scripts/cloud_harness_base.py",
      "scripts/ollama_harness.py",
      "platform_tests/scripts/test_provider_verdict_envelope_recovery.py",
      "bridge/hunks/gtkb-wi5599-provider-duplicate-envelope-recovery.patch"
    ],
    "linked_specifications": [
      "ADR-BRIDGE-ARTIFACT-HEAD-ENVELOPE-001",
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
      "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001",
      "DCL-BRIDGE-ENVELOPE-LINE-AUTHORING-PLACEMENT-001",
      "SPEC-CENTRALIZED-DISPATCH-SERVICE-001",
      "GOV-HARNESS-ONBOARDING-CONTRACT-001",
      "DCL-OLLAMA-TOOL-PARITY-GATE-001"
    ]
  },
  "expected_result": {
    "summary": "Repair provider-backed verdict publication so duplicate exact canonical artifact-head envelope pairs converge deterministically while conflicting envelope structure fails once with a stable actionable diagnostic. Serialize this sibling with WI-5578 and preserve the current A PB plus D/F LO topology.",
    "scope": [
      "Add a provider-publication-only envelope canonicalizer before the general bridge-envelope validator. It may collapse repeated exact expected status-derived ::init/::open pairs found in the artifact-head preamble to one canonical pair on fixed lines 2 and 3; it must not alter the status token or substantive verdict body.",
      "Reject malformed, mismatched-role, mismatched-activity, partial, or misplaced envelope directives with a stable structured error code and no bridge write. Never infer or rewrite GO, NO-GO, or VERIFIED.",
      "Teach the cloud and Ollama publisher-recovery loops to recognize only the stable envelope-structure diagnostic, offer at most one explicit correction turn where canonicalization is not safe, and stop before four identical retries on recurrence.",
      "Treat WI-5578 as a shared-target sibling: implementation must occur after WI-5422, WI-5471, WI-5495, WI-5576, and WI-5578 are terminal, or under one independently reviewed combined hunk plan that proves exact ownership and preserves all foreign bytes."
    ],
    "acceptance_criteria": [
      "TEST-11648 proves repeated exact canonical envelope pairs publish exactly once with one canonical line-2/line-3 pair and no generic recovery-budget consumption.",
      "Conflicting, malformed, wrong-role, wrong-activity, partial, or misplaced envelope directives publish nothing and produce one stable actionable diagnostic rather than four identical publisher attempts.",
      "Existing provider status-consistency, role, transition, claim, author-provenance, credential, GO/NO-GO, VERIFIED-finalization, cloud, and Ollama suites remain green.",
      "Fresh substantive dispatcher-produced F and D Loyal Opposition reviews each advance an assigned bridge document with exit code 0; A remains PB-only and dispatcher topology/configuration is unchanged."
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
| `ADR-BRIDGE-ARTIFACT-HEAD-ENVELOPE-001` | Run TEST-11648 and focused writer tests proving exact pair canonicalization plus malformed/conflicting fail-closed behavior. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-BRIDGE-ENVELOPE-LINE-AUTHORING-PLACEMENT-001` | Assert the written artifact has the status on line 1 and exactly one canonical envelope on lines 2 and 3, with no body-level directive accepted. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Run cloud/Ollama recovery suites and fresh genuine D/F dispatcher proofs without configuration or TAFE mutation. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Verify A remains PB-only, D/F remain LO, and provider publication uses only canonical dispatcher/bridge controls. |
| `DCL-OLLAMA-TOOL-PARITY-GATE-001` | Run equivalent D/Ollama duplicate-envelope success and conflicting-envelope bounded-failure tests. |

## Acceptance Criteria

- TEST-11648 proves repeated exact canonical envelope pairs publish exactly once with one canonical line-2/line-3 pair and no generic recovery-budget consumption.
- Conflicting, malformed, wrong-role, wrong-activity, partial, or misplaced envelope directives publish nothing and produce one stable actionable diagnostic rather than four identical publisher attempts.
- Existing provider status-consistency, role, transition, claim, author-provenance, credential, GO/NO-GO, VERIFIED-finalization, cloud, and Ollama suites remain green.
- Fresh substantive dispatcher-produced F and D Loyal Opposition reviews each advance an assigned bridge document with exit code 0; A remains PB-only and dispatcher topology/configuration is unchanged.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/gtkb_bridge_writer.py`
- `scripts/cloud_harness_base.py`
- `scripts/ollama_harness.py`
- `platform_tests/scripts/test_provider_verdict_envelope_recovery.py`
- `bridge/hunks/gtkb-wi5599-provider-duplicate-envelope-recovery.patch`

## Recommended Commit Type

`feat`
