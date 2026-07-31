NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f247b-4dc8-7b32-a2ab-25839614d33f
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive; approval_policy=never; reasoning_effort not exported by local environment

# Implementation Proposal - Phase 3 gap 02: harness and model configuration truth

bridge_kind: prime_proposal
Document: gtkb-headless-dispatch-model-pinning
Version: 001
Date: 2026-07-02 UTC

Project Authorization: PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI-4964-HEADLESS-MODEL-PINNING
Project: PROJECT-HARNESS-EQUIVALENCE-PHASE-3
Work Item: WI-4964

target_paths: ["groundtruth-kb/src/groundtruth_kb/harness_ops.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_harness_ops.py", "platform_tests/groundtruth_kb/cli/test_harness_cli.py", "harness-state/harness-registry.json", "config/dispatcher/rules.toml"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

File a narrow WI-4964 implementation proposal to make headless dispatch model identity explicit: Claude Code/B uses claude-opus-4-8 with max effort and Codex/A uses gpt-5.5 with Extra High reasoning.

Work item description: Reconcile UI model labels, headless dispatch routes, provider shim routing, harness registry entries, and owner-visible status so OpenRouter/Kimi/Goose/deepseek model identity divergences cannot silently mislead evaluation. The child proposal must model UI, headless, provider-shim, and dispatch identity separately.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4964` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/harness_ops.py`, `groundtruth-kb/src/groundtruth_kb/cli.py`, `groundtruth-kb/tests/test_harness_ops.py`, `platform_tests/groundtruth_kb/cli/test_harness_cli.py`, `harness-state/harness-registry.json`, `config/dispatcher/rules.toml`.

## Specification Links

- `ADR-CROSS-HARNESS-PARITY-001` - auto-linked governing or work-item specification.
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
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - auto-linked governing or work-item specification.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - auto-linked governing or work-item specification.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded project implementation authority.

## Prior Deliberations

- _No prior deliberations auto-loaded; author must confirm before review._

## Owner Decisions / Input

- `PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI-4964-HEADLESS-MODEL-PINNING` - active project authorization covering `WI-4964`.

## Proposed Scope

- Add a narrow canonical gt harness command/API path for updating an existing harness invocation_surfaces JSON without changing role, lifecycle status, identity, or dispatch eligibility.
- Use the canonical harness writer/projection path to pin Codex A headless dispatch to codex exec --model gpt-5.5 with model_reasoning_effort=xhigh, and Claude Code B headless dispatch to claude --model claude-opus-4-8 --effort max.
- Align dispatcher budget/status model labels for A and B so owner-visible dispatch status matches the actual headless CLI model identity.
- Preserve existing placeholders {{PROMPT}} and {{PROJECT_ROOT}}, approval_policy=never for Codex, and Claude JSON output behavior.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `ADR-CROSS-HARNESS-PARITY-001` | Verify model identity is explicit in headless dispatch routes and owner-visible status for Codex A and Claude B. |
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
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Run gt bridge dispatch config --json and inspect selected headless-capable A/B route metadata after the update. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | Run the dispatcher control/config command instead of treating ad hoc files or cached reports as authority. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Before implementation, acquire a live GO work-intent claim and implementation-start packet for PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI-4964-HEADLESS-MODEL-PINNING; keep mutations within listed target paths and forbidden operations. |

## Acceptance Criteria

- gt harness roles shows A headless argv containing --model gpt-5.5 and -c model_reasoning_effort=xhigh, and B headless argv containing --model claude-opus-4-8 and --effort max.
- gt bridge dispatch config --json reports budget.harnesses.A.model as gpt-5.5 and budget.harnesses.B.model as claude-opus-4-8.
- Focused tests cover the new invocation-surface update path and projection refresh without changing harness role/status/precedence.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/harness_ops.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/tests/test_harness_ops.py`
- `platform_tests/groundtruth_kb/cli/test_harness_cli.py`
- `harness-state/harness-registry.json`
- `config/dispatcher/rules.toml`

## Recommended Commit Type

`feat`
