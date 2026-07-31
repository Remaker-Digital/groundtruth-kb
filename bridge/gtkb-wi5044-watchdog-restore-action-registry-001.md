NEW

# WI-5044 Watchdog Restore-Action Registry

bridge_kind: prime_proposal
Document: gtkb-wi5044-watchdog-restore-action-registry
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-06 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3821-e2fc-75d2-814f-2a3ec0f71244
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop interactive Prime Builder; approval_policy=never; workspace=E:\GT-KB

Project Authorization: PAUTH-PROJECT-GTKB-SERVICE-SOT-WATCHDOG-WATCHDOG-FULL-PROJECT-IMPLEMENTATION
Project: PROJECT-GTKB-SERVICE-SOT-WATCHDOG
Work Item: WI-5044

target_paths: ["config/registry/sot-artifacts.toml", "groundtruth-kb/src/groundtruth_kb/project/sot_registry.py", "groundtruth-kb/tests/test_sot_registry.py", "platform_tests/scripts/test_check_sot_registry_completeness.py", "platform_tests/scripts/test_gtkb_service_sot_restore_registry.py"]

implementation_scope: config, source, tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Add an explicit restore-action declaration surface to the SoT artifact registry so the watchdog can distinguish how each registered artifact or service should be restored. The implementation should extend the TOML schema and typed registry reader with a `restore_action` field, then populate existing records with concrete values or an explicit no-op/manual value where automatic action is not allowed.

This slice defines metadata only. It must not execute restore actions, overwrite canonical stores from backups, or install scheduled tasks. Execution policy and resource bounding remain in WI-5045 and WI-5046.

## Specification Links

- `ADR-PLATFORM-SERVICE-SOT-WATCHDOG-001` - Requires the watchdog to use SoT-registry `health_check_function` and `backup_policy` coverage as the platform-wide inventory.
- `DCL-SERVICE-SOT-WATCHDOG-RESTORATION-SAFETY-001` - Requires each restore action to be classified before any safe automatic execution can exist.
- `GOV-PLATFORM-SOT-REGISTRY-001` - Requires platform SoT classes to be registered in the canonical SoT registry.
- `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` - Governs the per-record schema that this proposal extends with restore-action metadata.
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` - Requires TOML registry changes and MemBase projection behavior to remain aligned.
- `GOV-SOT-SINGLETON-001` - Requires the registry to remain the single authoritative inventory for SoT artifact metadata.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - Requires state claims and registry-derived behavior to come from fresh canonical reads.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Requires all implementation targets to remain inside `E:\GT-KB` and not silently resolve to Agent Red or out-of-root surfaces.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Requires the bridge file chain and dispatcher/TAFE state to be the workflow authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Requires complete specification linkage and test mapping.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Requires the project authorization, project, and work item metadata above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Requires executed spec-derived tests before VERIFIED.
- `GOV-STANDING-BACKLOG-001` - Treats WI-5044 and the project record as the durable work authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Require durable artifact linkage and explicit lifecycle evidence.

## Prior Deliberations

- `DELIB-20260706-WATCHDOG-PROJECT-AUTHORIZATION` - Owner authorized all six watchdog work items with per-WI bridge GO.
- `DELIB-20260706-WATCHDOG-RESTORATION-SAFETY-TIERED` - Owner selected safe/idempotent automatic restoration and fail-loud canonical escalation.
- `DELIB-20266276` - Dispatcher self-healing precedent for supervised restoration behavior.
- `DELIB-20266140` - Visibility-only precedent that must be representable by registry metadata.

Deliberation search command used before drafting:

```powershell
gt deliberations search "WI-5044 restore action registry SoT health_check_function backup_policy safe canonical restore_action" --json
```

## Owner Decisions / Input

- `DELIB-20260706-WATCHDOG-PROJECT-AUTHORIZATION` authorizes implementation of WI-5044 inside the active project authorization envelope.
- `DELIB-20260706-WATCHDOG-RESTORATION-SAFETY-TIERED` requires restore-action metadata to distinguish safe/idempotent, canonical/fail-loud, and visibility-only behavior before execution exists.

## Requirement Sufficiency

Existing requirements sufficient. The SoT registry ADR/DCL set plus the watchdog ADR/DCL and WI-5044 define enough scope to add schema, reader, registry records, and tests.

## Spec-Derived Verification Plan

| Specification | Required evidence | Verification command |
| --- | --- | --- |
| `GOV-PLATFORM-SOT-REGISTRY-001`, `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` | `restore_action` is schema-validated for every active registry record. | `python -m pytest groundtruth-kb/tests/test_sot_registry.py platform_tests/scripts/test_gtkb_service_sot_restore_registry.py -q --tb=short` |
| `DCL-SOT-REGISTRY-PROJECTION-PARITY-001`, `GOV-SOT-SINGLETON-001` | TOML reader and projection behavior remain aligned; no duplicate registry source is introduced. | `python -m pytest platform_tests/scripts/test_check_sot_registry_completeness.py groundtruth-kb/tests/test_sot_registry.py -q --tb=short` |
| `DCL-SERVICE-SOT-WATCHDOG-RESTORATION-SAFETY-001` | Registry metadata can express safe, canonical, manual/visibility-only, and no-op actions without executing them. | `python -m pytest platform_tests/scripts/test_gtkb_service_sot_restore_registry.py -q --tb=short` |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Changed files stay under the declared GT-KB root target paths. | `git diff --name-only -- config/registry/sot-artifacts.toml groundtruth-kb/src/groundtruth_kb/project/sot_registry.py groundtruth-kb/tests/test_sot_registry.py platform_tests/scripts/test_check_sot_registry_completeness.py platform_tests/scripts/test_gtkb_service_sot_restore_registry.py` |

Implementation report must also include `ruff check` and `ruff format --check` for changed Python files.

## Risk / Rollback

Primary risk is treating registry metadata as execution authority too early. The implementation should make restore-action metadata explicit and testable while preserving execution as a separate policy-engine concern. Rollback is a single-commit revert of the schema, registry entries, reader changes, and tests.

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing numbered bridge file for `gtkb-wi5044-watchdog-restore-action-registry`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

feat: this slice adds restore-action metadata to the SoT registry and tests the new registry capability.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
