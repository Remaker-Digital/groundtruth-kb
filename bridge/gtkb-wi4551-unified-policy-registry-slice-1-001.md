NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f0cf7-9439-7cc3-8b58-cdad991c5890
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex desktop Prime Builder interactive session

# GT-KB Bridge Implementation Proposal - gtkb-wi4551-unified-policy-registry-slice-1 - 001

bridge_kind: prime_proposal
Document: gtkb-wi4551-unified-policy-registry-slice-1
Version: 001
Project Authorization: PAUTH-PROJECT-OMNIGENT-ALIGNMENT-OMNIGENT-ALIGNMENT-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-OMNIGENT-ALIGNMENT
Work Item: WI-4551
Recommended commit type: feat:

target_paths: ["config/agent-control/unified-policy-registry.toml", "groundtruth-kb/src/groundtruth_kb/policy/registry.py", "groundtruth-kb/src/groundtruth_kb/policy/engine.py", "groundtruth-kb/tests/test_unified_policy_registry.py"]

implementation_scope: source_config_test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Claim

Implement WI-4551 Slice 1 by adding a declarative unified policy-registry inventory layer that sits beside the existing deterministic AUQ policy engine.

This first slice does not migrate or replace existing PreToolUse hooks. It creates the common registry shape needed to inventory gate/action classes, bind them to existing hook or CLI adapter surfaces, validate registry integrity, and expose deterministic metadata for later migration slices. Existing hooks keep their current behavior until a later bridge proposal explicitly moves one adapter at a time behind the central policy engine.

## Specification Links

- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries Project Authorization, Project, Work Item, and inline JSON `target_paths` metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the proposal cites the governing policy-engine, action-class, adapter, and bridge-authority specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must map tests to the linked requirements.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected config/source/test implementation requires a live bridge `GO`, a work-intent claim, and an implementation-start packet.
- `GOV-STANDING-BACKLOG-001` - WI-4551 is the MemBase-backed Omnigent Alignment backlog item being processed.
- `SPEC-AUQ-POLICY-ENGINE-001` - the central deterministic policy engine is the intended single decision point; this slice prepares the registry metadata it needs.
- `SPEC-AUQ-ACTION-CLASSES-001` - action classes must be registered explicitly and rejected when unknown or duplicated.
- `SPEC-AUQ-ADAPTER-PATTERN-001` - adapters must remain thin delegators and must not grow parallel policy logic.
- `SPEC-AUQ-NO-LLM-CLASSIFIER-001` - the registry and loader must remain deterministic and must not call LLM, network, or provider APIs.
- `SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001` - the registry inventory must make harness governance-gate parity auditable instead of scattered across hook files alone.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - hook availability is per-harness, so registry entries must describe adapter availability without assuming every harness has the same live hook surface.

## Requirement Sufficiency

Existing requirements are sufficient for this first slice.

WI-4551 requests a unified declarative policy registry to consolidate bespoke GT-KB hooks. The existing AUQ policy specs already define a central deterministic engine, explicit action classes, thin adapters, no LLM classifiers, and a CLI surface. This proposal narrows the first implementation to registry inventory and validation only, avoiding an all-at-once hook migration.

No new owner input is requested. Later enforcement-migration slices should remain separately proposed and reviewed because each existing gate has its own operational risk.

## Target Paths

The implementation is limited to:

- `config/agent-control/unified-policy-registry.toml`
- `groundtruth-kb/src/groundtruth_kb/policy/registry.py`
- `groundtruth-kb/src/groundtruth_kb/policy/engine.py`
- `groundtruth-kb/tests/test_unified_policy_registry.py`

No existing hook file, `.claude/settings.json`, `.codex/hooks.json`, bridge runtime state, MemBase, formal artifact, deployment, credential, or production application file is in scope.

## Implementation Plan

1. Add `config/agent-control/unified-policy-registry.toml` with schema version, registry id, action-class entries, adapter inventory, enforcement status, and owning hook or CLI surface for the initial policy inventory.
2. Add `groundtruth_kb.policy.registry` with a pure loader/parser, typed dataclasses, deterministic hash, duplicate-action validation, unknown-outcome validation, adapter-status validation, and path-boundary checks.
3. Keep the existing `groundtruth_kb.policy.engine` behavior intact; add only the minimal integration needed for shared constants or registry reuse if the implementation proves that is cleaner than duplicating constants.
4. Seed the registry with inventory-only entries for the existing AUQ policy actions and representative governance hook surfaces such as bridge-compliance, implementation-start, scanner-safe-writer, narrative-artifact approval, SOT-read discipline, and owner-decision tracking.
5. Mark migrated/enforced status explicitly. In this slice, existing bespoke hooks remain the load-bearing enforcement path unless already backed by the AUQ engine.
6. Add tests for registry parsing, integrity hash stability, duplicate/unknown rejection, inventory-only status, no hidden enforcement migration, and deterministic/no-network/no-LLM behavior.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
| --- | --- | --- | --- | --- |
| CQ-SECRETS-001 | Yes | Registry entries use names, paths, and action tokens only; no credentials, endpoint secrets, or key-shaped literals. | Bridge helper credential scan and focused test/source review. | |
| CQ-PATHS-001 | Yes | Limit implementation to the four declared target paths; do not edit hook registrations or hook implementations in this slice. | Implementation-start target validation and `git diff --name-only`. | |
| CQ-COMPLEXITY-001 | Yes | Keep parser and validator table-driven with small dataclasses and explicit validation functions. | Ruff check and focused test coverage for each validation branch. | |
| CQ-CONSTANTS-001 | Yes | Name schema version, valid outcomes, valid adapter statuses, and registry path constants rather than scattering string literals. | Tests assert accepted/rejected tokens and schema version. | |
| CQ-SECURITY-001 | Yes | The registry loader is deterministic and read-only; it must not call network, subprocess, provider, or LLM surfaces. | `test_unified_policy_registry_has_no_llm_network_or_subprocess_dependency` plus source review. | |
| CQ-DOCS-001 | Yes | Include concise comments in the TOML registry that distinguish inventory-only entries from enforced engine-backed entries. | Test or source review confirms status labels are present and parsed. | |
| CQ-TESTS-001 | Yes | Add tests for parsing, hash stability, invalid outcome, duplicate action class, adapter inventory, and no enforcement migration. | `python -m pytest groundtruth-kb/tests/test_unified_policy_registry.py -q --tb=short`. | |
| CQ-LOGGING-001 | N/A | The registry loader does not add runtime logging. | Target diff review confirms no logging surface is added. | No runtime logging behavior is introduced. |
| CQ-VERIFICATION-001 | Yes | Run focused pytest, Ruff check, Ruff format-check, bridge applicability preflight, and ADR/DCL clause preflight before reporting implementation. | Command output included in the post-implementation report. | |

## Out Of Scope

- Migrating any existing hook behavior into the central engine.
- Altering `.claude/settings.json`, `.codex/hooks.json`, or hook registrations.
- Replacing bridge-compliance, implementation-start, scanner-safe-writer, narrative-artifact, SOT-read, owner-decision, or formal-artifact gates.
- Adding phone/web owner approval surfaces; that is WI-4553.
- Adding declarative agent/role YAML; that is WI-4552.
- Adding cost/token budget enforcement; that is WI-4550.
- Mutating MemBase or formal GOV/ADR/DCL/SPEC records.

## Owner Decisions / Input

No new owner input is requested.

Relevant existing decisions:

- `DELIB-OMNIGENT-ADVISORY-20260614` - owner accepted the Omnigent advisory as a source of GT-KB alignment backlog candidates.
- `DELIB-20263229` - owner selected patterns-only Omnigent emulation: borrow design shape without importing Omnigent or creating runtime dependency.
- `DELIB-20265586` - owner-approved project authorization snapshot covering the Omnigent Alignment bounded implementation scope.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - central deterministic services with thin adapters are the preferred GT-KB shape for repeatable policy decisions.

## Prior Deliberations

- `DELIB-OMNIGENT-ADVISORY-20260614` - established Omnigent Alignment work items including WI-4551.
- `DELIB-20263229` - patterns-only emulation decision for Omnigent-derived ideas.
- `DELIB-20265586` - project authorization snapshot for Omnigent Alignment.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - deterministic service plus thin-adapter architecture used by the existing AUQ policy specs.
- `bridge/gtkb-auq-policy-gates-001-010.md` - existing verified AUQ policy engine and CLI behavior that this registry should reuse rather than replace.
- `bridge/gtkb-wi4550-dispatch-cost-budget-policy-002.md` - adjacent Omnigent Alignment Slice 1 proposal; WI-4550 remains separate and waiting on Loyal Opposition.

## Spec-Derived Verification Plan

- `SPEC-AUQ-POLICY-ENGINE-001`: `test_unified_registry_can_feed_policy_engine_action_metadata` proves the registry can describe engine-backed action classes without bypassing the existing engine.
- `SPEC-AUQ-ACTION-CLASSES-001`: `test_unified_registry_rejects_duplicate_or_unknown_action_classes` proves action-class registration is explicit and deterministic.
- `SPEC-AUQ-ADAPTER-PATTERN-001`: `test_unified_registry_marks_inventory_only_hooks_without_parallel_policy_logic` proves hook inventory entries are metadata only and do not encode allow/deny branches.
- `SPEC-AUQ-NO-LLM-CLASSIFIER-001`: `test_unified_policy_registry_has_no_llm_network_or_subprocess_dependency` proves the loader does not import or call external classifiers, network clients, or subprocesses.
- `SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001`: `test_registry_inventory_includes_codex_and_claude_governance_surfaces` proves registry metadata can expose parity-relevant hook surfaces.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`: `test_registry_allows_per_harness_adapter_availability` proves entries can record harness-specific availability without assuming uniform hook support.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: the post-implementation report must include exact focused pytest, Ruff, format-check, bridge applicability, and ADR/DCL preflight outputs.
- `GOV-FILE-BRIDGE-AUTHORITY-001`: before implementation, Prime Builder must acquire a work-intent claim and create an implementation-start packet from the live latest `GO`; protected target validation must pass for all target paths.

## Verification Commands

```powershell
python -m pytest groundtruth-kb/tests/test_unified_policy_registry.py -q --tb=short
python -m ruff check groundtruth-kb/src/groundtruth_kb/policy/registry.py groundtruth-kb/src/groundtruth_kb/policy/engine.py groundtruth-kb/tests/test_unified_policy_registry.py
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/policy/registry.py groundtruth-kb/src/groundtruth_kb/policy/engine.py groundtruth-kb/tests/test_unified_policy_registry.py
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4551-unified-policy-registry-slice-1
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4551-unified-policy-registry-slice-1
```

## Acceptance Criteria

- A unified policy registry TOML file exists and parses deterministically.
- Registry output includes schema version, registry id, hash, action classes, adapter surface names, adapter availability, and enforcement status.
- Duplicate action classes and invalid outcome/status tokens fail closed with clear errors.
- Existing AUQ policy tests still pass.
- Existing bespoke hooks are inventoried but not behaviorally migrated in this slice.
- The loader performs no network, subprocess, provider, LLM, MemBase, or bridge-state mutation.
- Tests prove per-harness adapter availability can be represented.
- The implementation stays within the four target paths.

## Risk And Rollback

Risk is moderate because the registry will become a coordination point for later hook consolidation. The main risk is accidentally implying enforcement migration before adapters have been reviewed one by one. Mitigation: include explicit `inventory_only` or equivalent status values, keep existing hooks untouched, and test that no hook registration or hook implementation changes in this slice.

Rollback is deletion of the new registry config, loader module, and test file plus reversal of any minimal `engine.py` integration before VERIFIED. After VERIFIED, future migration slices should supersede or extend this registry through separate bridge threads.
