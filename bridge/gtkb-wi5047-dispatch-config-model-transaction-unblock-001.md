NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f38dc-dc71-7af2-a3ba-d3e17ae4f13b
author_model: gpt-5
author_model_version: codex-desktop-2026-07-06
author_model_configuration: codex-desktop; approval_policy=never; sandbox=danger-full-access

# Operational State Change - WI-5047 Dispatcher Model Transaction Unblock

bridge_kind: operational_state_change
Document: gtkb-wi5047-dispatch-config-model-transaction-unblock
Version: 001
Date: 2026-07-06 UTC

## Claim

`WI-5047` cannot finish cleanly until GT-KB has a governed `gt bridge dispatch config` transaction for `budget.harnesses.<id>.model`. The current WI-5047 PAUTH covers route/config/test evidence but not the source/CLI extension needed for that missing transaction.

## Evidence

- The WI-5047 bridge thread is latest `NO-GO` at version 006 with an owner hold because dispatcher budget model metadata remains stale and direct `config/dispatcher/rules.toml` edits are prohibited.
- Active PAUTH `PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI5047-OLLAMA-KIMI-K2-7-CLOUD-20260706` includes `WI-5047` but allows `config`, `test`, `generated_projection`, `membase_record`, and `governance_evidence`, not source or CLI extension.
- Current dispatcher config still reports `budget.harnesses.D.model = deepseek-v4-pro-cloud` while harness D route metadata should become `kimi-k2-7-code-cloud`.

## Requested Disposition

- Review and approve the narrow governance path for a model-budget transaction, or require a child work item/PAUTH expansion before implementation.
- Future implementation must add a governed `gt bridge dispatch config` transaction with validation and audit evidence, then use it to set harness D model metadata to `kimi-k2-7-code-cloud`.
- Provider credentials, model access settings, durable role assignments, reviewer precedence, dispatch eligibility, and unrelated harness settings remain out of scope.

## Candidate Target Paths

- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_transactions.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/src/groundtruth_kb/cli_bridge_dispatch.py`
- `config/dispatcher/rules.toml`
- `platform_tests/scripts/test_bridge_dispatch_config.py`
- `platform_tests/scripts/test_dispatcher_config_transactions.py`

## Specification Links

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification linkage on proposals that may lead to implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project/authorization linkage or a valid non-implementation exemption.
- `ADR-CROSS-HARNESS-PARITY-001` - requires truthful harness/model parity evidence.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - covers centralized dispatcher behavior.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - requires dispatcher changes through governed CLI surfaces.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - requires bounded authority for source/CLI work.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves bridge-gated implementation.
- `DCL-DISPATCHER-CONFIG-CLI-ONLY-001` - prohibits direct dispatcher TOML edits for this change.

## Prior Deliberations

- `DELIB-20260706-OLLAMA-KIMI-K2-7-CODE-CLOUD` - owner selected Kimi K2.7 Code cloud for Ollama/D.
- WI-5047 bridge versions 001-006 - attempted route switch, implementation report, and latest NO-GO/hold for missing governed transaction.


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

- Owner requested this work in the current Prime Builder session, then directed Prime Builder to file proposals after the bridge/authorization blocker was surfaced.

## Verification Plan For Future Implementation

| Requirement | Verification |
| --- | --- |
| Governed transaction | Focused tests must prove the budget model changes only through `gt bridge dispatch config` transaction code. |
| D metadata | `gt bridge dispatch config --json` must show `budget.harnesses.D.model` equals `kimi-k2-7-code-cloud` after the transaction. |
| Follow-up WI-5047 report | Rerun WI-5047 targeted tests, dispatch status/health, and ruff checks before filing a new implementation report. |

## Rollback

This proposal changes no protected implementation files. Future rollback must revert only authorized source/test/config changes and preserve bridge, PAUTH, and audit records as append-only evidence.
