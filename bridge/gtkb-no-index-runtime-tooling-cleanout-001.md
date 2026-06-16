NEW

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ecc04-9ec8-7e81-a2e7-10000eba4ed9
author_model: gpt-5-codex
author_model_configuration: Codex desktop interactive session; Prime Builder

# No-Index Runtime Tooling Cleanout Proposal

bridge_kind: prime_proposal
Document: gtkb-no-index-runtime-tooling-cleanout
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-15 America/Los_Angeles

Project Authorization: PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4578-DISPATCH-ORTHOGONALITY-CLI
Project: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH
Work Item: WI-4578

target_paths: ["scripts/bridge_applicability_preflight.py", "scripts/run_spec_derived_tests.py", "scripts/harvest_session_deliberations.py", "scripts/retroactive_harvest_bridge_threads.py", "scripts/audit_gtkb_triad_completeness.py", "scripts/bridge_reconciliation_audit.py", "scripts/bridge_index_chain_audit.py", "groundtruth-kb/src/groundtruth_kb/session/handoff.py", "groundtruth-kb/src/groundtruth_kb/governance/context.py", "groundtruth-kb/src/groundtruth_kb/dispatcher/scheduler.py", "groundtruth-kb/src/groundtruth_kb/backlog/approval_state.py", "platform_tests/scripts/test_bridge_applicability_preflight.py", "platform_tests/scripts/test_run_spec_derived_tests.py", "platform_tests/scripts/test_session_handoff_service.py", "platform_tests/scripts/test_harvest_session_thread_level.py", "platform_tests/scripts/test_retroactive_harvest_bridge_threads.py", "platform_tests/scripts/test_membase_effective_use_audit.py", "bridge/gtkb-no-index-runtime-tooling-cleanout-*.md"]

implementation_scope: runtime_tooling_no_index_cleanup
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

The no-index sweep found active runtime tools that still require or derive authority from `bridge/INDEX.md`. These are not merely stale docs; some are currently failing because the file is absent.

Representative evidence:

- `scripts/bridge_applicability_preflight.py --bridge-id <new-thread>` exits with `ERR_NO_INDEX_ENTRY` even when a versioned bridge file exists or is about to be filed.
- `scripts/run_spec_derived_tests.py` documents `--bridge-id` as a document name from the old index and has fail-closed tests for missing index entries.
- `groundtruth-kb/src/groundtruth_kb/session/handoff.py` raises `Bridge INDEX missing` when the deleted file is absent.
- `groundtruth-kb/src/groundtruth_kb/governance/context.py`, `groundtruth-kb/src/groundtruth_kb/dispatcher/scheduler.py`, and `groundtruth-kb/src/groundtruth_kb/backlog/approval_state.py` still read the retired index for active state.
- Harvest/reconciliation/audit scripts still describe or compute from fresh index state instead of versioned bridge files plus dispatcher/TAFE state.

## Prior Deliberations

- `DELIB-20263438` - Owner requirement: corrected bridge-dispatch architecture and rule-based dispatch.
- `DELIB-20261236` - Prior LO verification on deterministic handoff-prompt service; relevant because handoff services must not fail on missing retired artifacts.
- `bridge/gtkb-no-index-implementation-authorization-bootstrap-003.md` - Bootstrap implementation report that fixed no-index implementation authorization and exposed remaining preflight/tooling defects.
- `bridge/gtkb-no-index-startup-control-cleanout-001.md` - Sibling proposal for startup/control prompt surfaces discovered in the same sweep.

## Specification Links

- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - implementation must proceed through a GO and live work-intent claim.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge lifecycle remains governed by proposal/review/report/verification files.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal includes project/work authorization metadata and target paths.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the proposal links governing requirements.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must map tests to linked requirements.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatcher/status/health and harness registry surfaces are the dispatch topology authorities.
- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` - routing/eligibility is rule-based over roles, subjects, and activities.
- `SPEC-TAFE-R4` - TAFE state and versioned artifacts supersede the old index as live coordination state.

## Requirement Sufficiency

Existing requirements are sufficient. Mike's explicit no-backward-compatibility directive converts every runtime break caused by deleting `bridge/INDEX.md` into a defect to fix. Runtime tools should resolve versioned bridge files and dispatcher/TAFE state directly.

## Pre-Filing Self-Check

The current applicability preflight is itself one of the target defects and cannot reliably validate new no-index bridge threads until repaired. Clause preflight already demonstrated that a versioned-file resolver is possible by resolving `bridge/gtkb-no-index-lo-harness-prompt-cleanout-001.md` without the retired index.

## Proposed Implementation

1. Replace active index-only bridge lookup in preflight, test runner, handoff, governance context, dispatcher scheduler, backlog approval, harvest, and audit tooling with a shared versioned bridge-file resolver or existing dispatcher/TAFE state APIs.
2. Preserve historical index-ingestion modules only when explicitly named as migration/audit tooling for pre-cutover artifacts.
3. Update tests to create status-bearing versioned bridge files instead of writing temp `bridge/INDEX.md` fixtures, except for tests explicitly asserting that attempts to create/use the retired file are blocked or historical.
4. Ensure runtime tools do not fail merely because `bridge/INDEX.md` is absent.

## Spec-Derived Verification Plan

Run:

```powershell
Test-Path bridge\INDEX.md
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-no-index-runtime-tooling-cleanout
python scripts\run_spec_derived_tests.py --bridge-id gtkb-no-index-runtime-tooling-cleanout --dry-run
python -m pytest platform_tests\scripts\test_bridge_applicability_preflight.py platform_tests\scripts\test_run_spec_derived_tests.py platform_tests\scripts\test_session_handoff_service.py platform_tests\scripts\test_harvest_session_thread_level.py platform_tests\scripts\test_retroactive_harvest_bridge_threads.py -q --tb=short
python -m ruff check scripts\bridge_applicability_preflight.py scripts\run_spec_derived_tests.py scripts\harvest_session_deliberations.py scripts\retroactive_harvest_bridge_threads.py scripts\audit_gtkb_triad_completeness.py scripts\bridge_reconciliation_audit.py scripts\bridge_index_chain_audit.py groundtruth-kb\src\groundtruth_kb\session\handoff.py groundtruth-kb\src\groundtruth_kb\governance\context.py groundtruth-kb\src\groundtruth_kb\dispatcher\scheduler.py groundtruth-kb\src\groundtruth_kb\backlog\approval_state.py
python -m ruff format --check scripts\bridge_applicability_preflight.py scripts\run_spec_derived_tests.py scripts\harvest_session_deliberations.py scripts\retroactive_harvest_bridge_threads.py scripts\audit_gtkb_triad_completeness.py scripts\bridge_reconciliation_audit.py scripts\bridge_index_chain_audit.py groundtruth-kb\src\groundtruth_kb\session\handoff.py groundtruth-kb\src\groundtruth_kb\governance\context.py groundtruth-kb\src\groundtruth_kb\dispatcher\scheduler.py groundtruth-kb\src\groundtruth_kb\backlog\approval_state.py
```

Expected:

- `Test-Path bridge\INDEX.md` returns `False`.
- Preflight and runtime tools resolve current versioned bridge files without requiring the retired index.
- Tests pass without recreating `bridge/INDEX.md` except explicit negative/historical cases.

## Risks

- Some TAFE index modules are historical/migration surfaces and should not be blindly deleted if they are still needed to ingest old audit material.
- Shared resolver extraction may be cleaner than ad hoc replacement in each tool; Loyal Opposition should check for duplication risk.

## Rollback

Revert changes in the target files. Do not restore `bridge/INDEX.md`; restoration would hide the runtime defects this proposal is meant to expose.
