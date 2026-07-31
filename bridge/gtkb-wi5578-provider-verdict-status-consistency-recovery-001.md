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

# Implementation Proposal - Prevent provider verdict status/content mismatch from exhausting publisher recovery

bridge_kind: prime_proposal
Document: gtkb-wi5578-provider-verdict-status-consistency-recovery
Version: 001
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE","coverage":"project_membership_fallback","included_work_item_count":null,"specificity_rank":[2,0],"selected":true}]
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5578

target_paths: ["scripts/gtkb_bridge_writer.py", "scripts/cloud_harness_base.py", "scripts/ollama_harness.py", "platform_tests/scripts/test_provider_verdict_status_consistency.py", "bridge/hunks/gtkb-wi5578-provider-verdict-status-consistency.patch"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Make provider verdict status/content mismatch recovery explicit, bounded, fail-closed, and parity-safe for OpenRouter F and Ollama D without changing dispatcher topology.

Work item description: Genuine OpenRouter F Loyal Opposition dispatch 2026-07-18T18-52-52Z-loyal-opposition-F-2e6ad3 performed substantive review and invoked PublishBridgeVerdict four times, but every governed publication attempt failed because the verdict argument did not match the content's first status token. Publisher-only recovery repeated the same structurally invalid request until it exhausted the bounded recovery budget and the worker exited 1 with no bridge advancement. Diagnose and implement a deterministic status-consistency path that preserves target-authored review intent, role-correct transition authority, fail-closed publication, generous worker allowances, and current A/D/F topology. The provider must either repair the envelope through a bounded explicit correction turn or receive a stable actionable error that prevents an identical retry loop; it must never silently rewrite a substantive GO/NO-GO/VERIFIED choice, accept an invalid transition, or report success without a governed verdict path.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5578` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/gtkb_bridge_writer.py`, `scripts/cloud_harness_base.py`, `scripts/ollama_harness.py`, `platform_tests/scripts/test_provider_verdict_status_consistency.py`, `bridge/hunks/gtkb-wi5578-provider-verdict-status-consistency.patch`.

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
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - auto-linked governing or work-item specification.
- `ADR-CLOUD-HARNESS-TEMPLATE-001` - auto-linked governing or work-item specification.
- `DCL-OLLAMA-TOOL-PARITY-GATE-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202666204` - Authorize WI-5253 Ollama D publisher recovery repair
- `DELIB-202666250` - Loyal Opposition Verification Verdict - WI-5245 Alibaba H Publisher Recovery
- `DELIB-20260716-WI5169-ALIBABA-H-REARM-BUDGET-LIVE` - Owner decision: Alibaba budget live; re-arm harness H dispatch eligibility now (WI-5169 EXPEDITE)
- `DELIB-202666266` - Loyal Opposition Proposal Review - WI-5258 Alibaba H HTTP 400 Publisher Recovery
- `DELIB-202666265` - Loyal Opposition VERIFIED Verdict - WI-5258 Alibaba H HTTP 400 Publisher Recovery

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE` - active project authorization covering `WI-5578`.

## Proposed Scope

- In scripts/gtkb_bridge_writer.py, preserve fail-closed status consistency validation but emit a stable mismatch code, the normalized verdict argument, the content first-status value, an explicit no-publication statement, and a correction instruction that requires the provider to choose its intended substantive verdict and resend matching values.
- In scripts/cloud_harness_base.py and scripts/ollama_harness.py, recognize only the stable status-mismatch code, allow exactly one publisher-only correction turn carrying the writer diagnostic, and on a second mismatch stop with a bounded stable reroutable error instead of consuming the generic four-attempt recovery budget.
- Never infer or rewrite GO, NO-GO, or VERIFIED; preserve transition validation, claim/session/role provenance, credential scanning, finalization, generous model/session allowances, and the current A PB-only plus D/F LO topology.
- Add a new clean focused test module and an exact hunk patch so WI-5578 bytes remain attributable; do not adopt current foreign dirty bytes. Sequence implementation after WI-5422, WI-5471, and WI-5495 are terminal unless the independent GO explicitly proves exact hunk separation is safe.

## Cross-Harness Disposition

- **A**: PB-only path unchanged; final readiness and substantive governed PB dispatch evidence remain mandatory.
- **B**: No direct source-path change; shared governance writer behavior remains fail-closed.
- **C**: No direct source-path change; shared governance writer behavior remains fail-closed.
- **D**: Implement and test identical one-correction mismatch recovery in the Ollama loop, then obtain fresh dispatcher proof.
- **E**: No direct source-path change; shared governance writer behavior remains fail-closed.
- **F**: Implement and test one-correction mismatch recovery in the cloud loop, then obtain fresh OpenRouter dispatcher proof.
- **H**: Cloud-loop behavior inherits the same bounded correction rule and must remain nonimpaired by focused tests.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5578; PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "Genuine OpenRouter F Loyal Opposition dispatch 2026-07-18T18-52-52Z-loyal-opposition-F-2e6ad3 performed substantive review and invoked PublishBridgeVerdict four times, but every governed publication attempt failed because the verdict argument did not match the content's first status token. Publisher-only recovery repeated the same structurally invalid request until it exhausted the bounded recovery budget and the worker exited 1 with no bridge advancement. Diagnose and implement a deterministic status-consistency path that preserves target-authored review intent, role-correct transition authority, fail-closed publication, generous worker allowances, and current A/D/F topology. The provider must either repair the envelope through a bounded explicit correction turn or receive a stable actionable error that prevents an identical retry loop; it must never silently rewrite a substantive GO/NO-GO/VERIFIED choice, accept an invalid transition, or report success without a governed verdict path.",
  "after_behavior": "Make provider verdict status/content mismatch recovery explicit, bounded, fail-closed, and parity-safe for OpenRouter F and Ollama D without changing dispatcher topology.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5578",
    "project": "PROJECT-GTKB-GOOSE-HARNESS-ADOPTION",
    "target_paths": [
      "scripts/gtkb_bridge_writer.py",
      "scripts/cloud_harness_base.py",
      "scripts/ollama_harness.py",
      "platform_tests/scripts/test_provider_verdict_status_consistency.py",
      "bridge/hunks/gtkb-wi5578-provider-verdict-status-consistency.patch"
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
      "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001",
      "GOV-HARNESS-ONBOARDING-CONTRACT-001",
      "ADR-CLOUD-HARNESS-TEMPLATE-001",
      "DCL-OLLAMA-TOOL-PARITY-GATE-001"
    ]
  },
  "expected_result": {
    "summary": "Make provider verdict status/content mismatch recovery explicit, bounded, fail-closed, and parity-safe for OpenRouter F and Ollama D without changing dispatcher topology.",
    "scope": [
      "In scripts/gtkb_bridge_writer.py, preserve fail-closed status consistency validation but emit a stable mismatch code, the normalized verdict argument, the content first-status value, an explicit no-publication statement, and a correction instruction that requires the provider to choose its intended substantive verdict and resend matching values.",
      "In scripts/cloud_harness_base.py and scripts/ollama_harness.py, recognize only the stable status-mismatch code, allow exactly one publisher-only correction turn carrying the writer diagnostic, and on a second mismatch stop with a bounded stable reroutable error instead of consuming the generic four-attempt recovery budget.",
      "Never infer or rewrite GO, NO-GO, or VERIFIED; preserve transition validation, claim/session/role provenance, credential scanning, finalization, generous model/session allowances, and the current A PB-only plus D/F LO topology.",
      "Add a new clean focused test module and an exact hunk patch so WI-5578 bytes remain attributable; do not adopt current foreign dirty bytes. Sequence implementation after WI-5422, WI-5471, and WI-5495 are terminal unless the independent GO explicitly proves exact hunk separation is safe."
    ],
    "acceptance_criteria": [
      "The writer rejects a mismatched verdict argument and content first status before publication, reports both sanitized values under a stable mismatch code, and leaves the bridge version absent.",
      "OpenRouter/cloud recovery publishes successfully when the provider corrects both fields on its one explicit retry; a second mismatch terminates immediately with a stable bounded diagnostic and no false verdict_path.",
      "Ollama recovery has the same one-correction success and second-mismatch fail-closed behavior.",
      "Existing role, transition, claim, metadata, credential, finalization, timeout, and provider-recovery regressions pass without weakening any guard.",
      "Fresh substantive dispatcher-produced D and F Loyal Opposition work each advances a governed bridge item with exit code 0; A remains PB-only and passes its independent readiness checks before the 60-item acceptance sequence."
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
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Run the new focused status-consistency tests plus existing cloud and Ollama recovery suites; then prove one fresh governed D dispatch and one fresh governed F dispatch each exit 0 and advance their claimed bridge document. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Assert mismatches create no numbered verdict, preserve claim/session/role transition checks, and only provider-authored corrected content can publish. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Map every linked specification to named tests and exact observed commands in the implementation report, then obtain independent VERIFIED. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Run D/F tool-loop parity and harness readiness coverage without direct harness invocation or dispatcher topology mutation. |
| `ADR-CLOUD-HARNESS-TEMPLATE-001` | Exercise OpenAI-chat publisher-only recovery with one corrected retry and deterministic second-mismatch termination. |
| `DCL-OLLAMA-TOOL-PARITY-GATE-001` | Exercise the equivalent Ollama native loop behavior and prove no raw bridge mutation or prose-only completion path is introduced. |

## Acceptance Criteria

- The writer rejects a mismatched verdict argument and content first status before publication, reports both sanitized values under a stable mismatch code, and leaves the bridge version absent.
- OpenRouter/cloud recovery publishes successfully when the provider corrects both fields on its one explicit retry; a second mismatch terminates immediately with a stable bounded diagnostic and no false verdict_path.
- Ollama recovery has the same one-correction success and second-mismatch fail-closed behavior.
- Existing role, transition, claim, metadata, credential, finalization, timeout, and provider-recovery regressions pass without weakening any guard.
- Fresh substantive dispatcher-produced D and F Loyal Opposition work each advances a governed bridge item with exit code 0; A remains PB-only and passes its independent readiness checks before the 60-item acceptance sequence.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/gtkb_bridge_writer.py`
- `scripts/cloud_harness_base.py`
- `scripts/ollama_harness.py`
- `platform_tests/scripts/test_provider_verdict_status_consistency.py`
- `bridge/hunks/gtkb-wi5578-provider-verdict-status-consistency.patch`

## Recommended Commit Type

`feat`
