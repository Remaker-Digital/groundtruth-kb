NEW
author_identity: codex
author_harness_id: A
author_session_context_id: 019f3d79-c37d-7432-8c82-a66b675a389a
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop interactive Prime Builder session; collaboration_mode=Default; approval_policy=never; cwd=E:/GT-KB

# Implementation Proposal - Add governed dispatcher budget model setter transaction

bridge_kind: prime_proposal
Document: gtkb-wi5070-dispatch-budget-model-setter
Version: 001
Date: 2026-07-07 UTC

Project Authorization: PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI5070-DISPATCH-MODEL-SETTER-20260707
Project: PROJECT-HARNESS-EQUIVALENCE-PHASE-3
Work Item: WI-5070

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge_dispatch_transactions.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "config/dispatcher/rules.toml", "platform_tests/scripts/test_bridge_dispatch_transactions.py", "platform_tests/scripts/test_bridge_dispatch_config.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Add the missing governed dispatcher budget-model setter needed to complete WI-5047 without bypassing DCL-DISPATCHER-CONFIG-CLI-ONLY-001.

Work item description: WI-5047 remains NO-GO because the dispatcher control surface has no governed gt bridge dispatch config transaction for budget.harnesses.<id>.model, leaving harness D budget/status metadata at deepseek-v4-pro-cloud after the owner-directed Kimi switch. Add a narrow setter transaction with validation, CLI exposure, audit evidence, and focused tests, then use the governed transaction to set harness D to kimi-k2-7-code-cloud.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5070` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_transactions.py`, `groundtruth-kb/src/groundtruth_kb/cli.py`, `config/dispatcher/rules.toml`, `platform_tests/scripts/test_bridge_dispatch_transactions.py`, `platform_tests/scripts/test_bridge_dispatch_config.py`.

## Specification Links

- `DCL-DISPATCHER-CONFIG-CLI-ONLY-001` - auto-linked governing or work-item specification.
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
- `ADR-CROSS-HARNESS-PARITY-001` - auto-linked governing or work-item specification.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - auto-linked governing or work-item specification.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - auto-linked governing or work-item specification.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded project implementation authority.

## Prior Deliberations

- `DELIB-202665815` - Loyal Opposition Review - WI-5047 Ollama Kimi Route Switch - 004
- `DELIB-202665814` - Loyal Opposition Review — WI-5047 Ollama Kimi Route Switch (NO-GO)
- `DELIB-20260706-OLLAMA-KIMI-K2-7-CODE-CLOUD` - Ollama/D headless dispatch should use Kimi K2.7 Code cloud
- `DELIB-20260702-OLLAMA-DEEPSEEK-V4-PRO-CLOUD` - Ollama headless dispatch model should use DeepSeek V4 Pro cloud
- `DELIB-202665813` - Loyal Opposition Review — WI-5047 Ollama/D → Kimi K2.7 Code cloud route switch (GO)

## Owner Decisions / Input

- `PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI5070-DISPATCH-MODEL-SETTER-20260707` - active project authorization covering `WI-5070`.

## Proposed Scope

- Add a governed dispatcher config transaction function that updates budget.harnesses.<id>.model only through the existing transaction/audit path.
- Expose the transaction as gt bridge dispatch config set-model with dry-run and defer-to-next-session support consistent with the existing dispatcher-control verbs.
- Preserve existing budget harness fields such as pricing and estimated_usd_per_dispatch, reject missing harnesses and empty model values, and avoid changing provider credentials, roles, reviewer precedence, dispatch eligibility, or unrelated harness settings.
- After GO and implementation-start, use the governed transaction to set harness D model metadata from deepseek-v4-pro-cloud to kimi-k2-7-code-cloud.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `DCL-DISPATCHER-CONFIG-CLI-ONLY-001` | Run focused dispatcher transaction and CLI tests proving the config model changes through gt bridge dispatch config set-model, not direct TOML editing. |
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
| `ADR-CROSS-HARNESS-PARITY-001` | Verify the dispatcher budget/status model label agrees with the already-applied WI-5047 Kimi route/harness metadata. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | Run gt bridge dispatch config --json before and after the transaction and verify harness D model metadata changes only through the governed control surface. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |

## Acceptance Criteria

- Focused transaction tests prove set_model updates only budget.harnesses.<id>.model, preserves sibling budget fields, supports dry-run without file writes, and rejects invalid inputs.
- Focused CLI coverage proves gt bridge dispatch config set-model calls the transaction and exposes --dry-run, --defer-to-next-session, and --json behavior.
- Dispatcher config/status evidence after implementation reports budget.harnesses.D.model as kimi-k2-7-code-cloud.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_transactions.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `config/dispatcher/rules.toml`
- `platform_tests/scripts/test_bridge_dispatch_transactions.py`
- `platform_tests/scripts/test_bridge_dispatch_config.py`

## Recommended Commit Type

`feat`
