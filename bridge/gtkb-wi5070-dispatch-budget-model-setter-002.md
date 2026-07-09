REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3d79-c37d-7432-8c82-a66b675a389a
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop interactive Prime Builder session; collaboration_mode=Default; approval_policy=never; cwd=E:/GT-KB

# Implementation Proposal - WI-5070 Governed Dispatcher Budget Model Setter

bridge_kind: prime_proposal
Document: gtkb-wi5070-dispatch-budget-model-setter
Version: 002
Date: 2026-07-07 UTC
Responds to: bridge/gtkb-wi5070-dispatch-budget-model-setter-001.md

Project Authorization: PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI5070-DISPATCH-MODEL-SETTER-20260707
Project: PROJECT-HARNESS-EQUIVALENCE-PHASE-3
Work Item: WI-5070
work_item_ids: [WI-5070, WI-5047]

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge_dispatch_transactions.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "config/dispatcher/rules.toml", "platform_tests/scripts/test_bridge_dispatch_transactions.py", "platform_tests/scripts/test_bridge_dispatch_config.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

This revision supersedes version 001 only to make the implementation-start surface unambiguous. The implementation scope, project authorization, owner decision, and verification intent are unchanged.

Prime Builder proposes a bounded child implementation for WI-5070: add a governed dispatcher control transaction for the budget model label, expose it as a CLI verb, and after GO use that governed verb to finish the stale harness D metadata correction required by WI-5047.

## Requirement Sufficiency

Existing requirements are sufficient for implementation review.

- The owner decision DELIB-20260706-OLLAMA-KIMI-K2-7-CODE-CLOUD selects the Kimi route and requires a governed follow-on path.
- WI-5047 is latest NO-GO because direct dispatcher TOML mutation is prohibited and the governed control surface lacks the needed budget model transaction.
- WI-5070 and TEST-11301 capture the child implementation and verification obligation.
- The active PAUTH named above includes WI-5070 and permits source, test_addition, cli_extension, config, and governance_evidence mutations while forbidding credential, provider-account, role, reviewer-precedence, dispatch-eligibility, and unrelated harness-setting changes.

## In-Root Placement Evidence

All implementation outputs, generated artifacts, and bridge evidence stay under the GT-KB project root. No Agent Red, archive, external checkout, temp-directory dependency, or out-of-root target is in scope.

## Current State Evidence

- Live dispatcher control output still reports harness D budget model metadata as deepseek-v4-pro-cloud.
- Live WI-5047 route and harness evidence already point the operational Ollama route toward Kimi, so the remaining defect is the stale dispatcher budget/status label.
- The current dispatcher CLI exposes eligibility, weights, caps, rule, add-harness, and remove-harness transactions, but no budget model setter.

## Proposed Scope

- Add a transaction that updates only the selected budget harness model value through the existing transaction and audit path.
- Expose the transaction as gt bridge dispatch config set-model with dry-run, defer-to-next-session, and JSON output support consistent with existing dispatcher control verbs.
- Validate harness id and model input, reject missing budget harness rows, preserve sibling budget fields, and avoid unrelated dispatcher or harness authority changes.
- After GO and implementation-start, use the new governed command to set harness D metadata to kimi-k2-7-code-cloud.

## Out Of Scope

- Provider credentials, provider account settings, model access configuration, production deployment, GitHub settings, durable role assignment, reviewer precedence, dispatch eligibility, and unrelated harness settings.
- Retired poller restoration or alternate bridge queue creation.

## Specification Links

- DCL-DISPATCHER-CONFIG-CLI-ONLY-001 - direct dispatcher TOML mutation is prohibited; changes must flow through the governed dispatcher control surface.
- SPEC-DISPATCHER-CONTROL-SURFACE-001 - dispatcher changes must be inspectable and auditable through the dispatcher CLI.
- SPEC-CENTRALIZED-DISPATCH-SERVICE-001 - dispatcher metadata must remain truthful for centralized dispatch behavior.
- ADR-CROSS-HARNESS-PARITY-001 - model identity surfaces must remain truthful across harness and dispatcher reporting.
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 - implementation requires bounded active PAUTH coverage.
- GOV-FILE-BRIDGE-AUTHORITY-001 - implementation requires role-correct bridge review and GO before mutation.
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 - proposals must cite project, work item, PAUTH, and target paths.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - proposals must cite governing specifications.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - VERIFIED requires spec-derived test evidence.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - this is GT-KB platform work, not Agent Red application work.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - the child work item, PAUTH, proposal, and evidence preserve artifact traceability.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - the NO-GO blocker is promoted into explicit active work.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - owner decisions and implementation blockers remain durable artifacts.
- GOV-STANDING-BACKLOG-001 - future work is represented in MemBase rather than transient chat.

## Prior Deliberations

- DELIB-20260706-OLLAMA-KIMI-K2-7-CODE-CLOUD - owner decision for the Kimi route and governed follow-on path.
- DELIB-20260702-OLLAMA-DEEPSEEK-V4-PRO-CLOUD - prior model route decision superseded for this forward path.
- DELIB-202665814 - Loyal Opposition confirmed the WI-5047 budget model setter blocker.
- DELIB-202665815 - Loyal Opposition confirmed the subsequent WI-5047 hold.

## Owner Decisions / Input

No new owner decision is required for this proposal. Owner authority is carried by DELIB-20260706-OLLAMA-KIMI-K2-7-CODE-CLOUD and the active WI-5070 PAUTH.

## Acceptance Criteria

- A focused transaction test proves the model setter updates only the requested budget harness model field and preserves sibling budget fields.
- A focused CLI test proves the new command calls the transaction and supports dry-run, deferred transaction, and JSON output behavior.
- Invalid harness identifiers, missing budget harness rows, and empty model values fail closed with clear errors.
- Dispatcher evidence after implementation reports harness D budget model metadata as kimi-k2-7-code-cloud.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| DCL-DISPATCHER-CONFIG-CLI-ONLY-001 | Prove the model change is performed through the dispatcher control command, not by direct file editing. |
| SPEC-DISPATCHER-CONTROL-SURFACE-001 | Prove the command returns auditable transaction output and preserves existing transaction semantics. |
| ADR-CROSS-HARNESS-PARITY-001 | Prove the dispatcher budget/status model label agrees with the owner-selected Kimi route. |
| GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 | Begin implementation only after GO and implementation-start packet creation against this revised proposal. |
| GOV-FILE-BRIDGE-AUTHORITY-001 | File a post-implementation report and require independent LO VERIFIED before terminal closure. |

## Rollback

Rollback should use the same governed dispatcher control transaction to restore the prior budget model value if necessary, and revert only the bounded source and test changes introduced by this work. Bridge, PAUTH, deliberation, and audit records remain append-only evidence.
