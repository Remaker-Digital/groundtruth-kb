NEW

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019eec0d-db60-7a02-b3bf-85d24df55e76
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex Desktop interactive Prime Builder via ::init gtkb pb; approval_policy=never; workspace E:\GT-KB

# GT-KB Bridge Implementation Report - gtkb-wi4691-quality-first-spillover-dispatch - 003

bridge_kind: implementation_report
Document: gtkb-wi4691-quality-first-spillover-dispatch
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi4691-quality-first-spillover-dispatch-002.md
Approved proposal: bridge/gtkb-wi4691-quality-first-spillover-dispatch-001.md
Recommended commit type: feat:

## Implementation Claim

Implemented quality-first spillover dispatch for WI-4691. Dispatcher selection now prefers quality, then cost, then availability. The cross-harness trigger no longer stops after the first ready Loyal Opposition target; it walks the ranked target list, gives each ready target a distinct oldest-first selected batch, removes that batch from the remaining pending queue, and continues until no dispatchable work remains or no ready quality-qualified capacity remains.

This is spillover, not broadcast: the same bridge item is not intentionally assigned to multiple harnesses in the same planning pass.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-DISPATCH-ENVELOPE-ARCHITECTURE-001`
- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001`
- `DCL-DISPATCH-ENVELOPE-RULES-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `REQ-HARNESS-REGISTRY-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ENVELOPE-META-MODEL-001`
- `DCL-ENVELOPE-META-MODEL-001`
- `SPEC-TOPIC-ENVELOPE-ROUTER-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Owner Decisions / Input

No new owner decision is required. This implementation applies the owner clarification that work should spill over to responsive quality-qualified harnesses and should not wait behind a non-responsive harness when available capacity exists elsewhere.

## Prior Deliberations

- `bridge/gtkb-wi4691-quality-first-spillover-dispatch-001.md` - approved implementation proposal.
- `bridge/gtkb-wi4691-quality-first-spillover-dispatch-002.md` - Loyal Opposition GO verdict.
- `DELIB-20265287` - owner decision creating WI-4691 and release-gating dispatcher fan-out/default dispatch work.
- `DELIB-20260620-BRIDGE-DISPATCHER-FABRIC-DELIBERATION` - owner requirement that reliability/quality be a hard eligibility gate.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `python scripts\bridge_claim_cli.py claim gtkb-wi4691-quality-first-spillover-dispatch` acquired claim row `15555`; `python scripts\implementation_authorization.py begin --bridge-id gtkb-wi4691-quality-first-spillover-dispatch` created a valid packet for the approved target paths. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | GO verdict and implementation packet carried forward proposal metadata, work item `WI-4691`, project authorization, and target paths. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused selector, trigger, ruff, and format checks below were executed and recorded. |
| `DCL-DISPATCH-ENVELOPE-RULES-001`; `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`; `REQ-HARNESS-REGISTRY-001` | `test_quality_first_selection_breaks_ties_by_cost_then_availability` verifies quality, cost, availability ordering. `test_lo_quality_first_spillover_dispatches_distinct_batches` verifies ranked spillover across distinct selected batches. |
| `ADR-DISPATCH-ENVELOPE-ARCHITECTURE-001`; `SPEC-DISPATCH-ENVELOPE-ELEMENT-001`; `ADR-ENVELOPE-META-MODEL-001`; `DCL-ENVELOPE-META-MODEL-001`; `SPEC-TOPIC-ENVELOPE-ROUTER-001` | Full `platform_tests/scripts/test_cross_harness_bridge_trigger.py` passed with 92 tests after clearing the loop-prevention env var for the test process. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Trigger suite and ruff checks passed for the cross-harness trigger file. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All changed implementation/test paths are in-root GT-KB platform paths. No Agent Red or external repository path was modified. |
| `GOV-STANDING-BACKLOG-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`; `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Work was tied to `WI-4691`, GO verdict `-002`, and this post-implementation report. No additional formal artifact lifecycle mutation was needed. |

## Commands Run

- `python scripts\bridge_claim_cli.py claim gtkb-wi4691-quality-first-spillover-dispatch` - passed; acquired GO implementation claim.
- `python scripts\implementation_authorization.py begin --bridge-id gtkb-wi4691-quality-first-spillover-dispatch` - passed; created valid implementation authorization packet.
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_bridge_dispatch_config.py::test_quality_first_selection_breaks_ties_by_cost_then_availability -q --tb=short` - passed.
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_cross_harness_bridge_trigger.py::test_lo_quality_first_spillover_dispatches_distinct_batches -q --tb=short` - passed.
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_bridge_dispatch_config.py -q --tb=short` - passed: 20 tests.
- `Remove-Item Env:GTKB_NO_CROSS_HARNESS_TRIGGER -ErrorAction SilentlyContinue; groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_cross_harness_bridge_trigger.py -q --tb=short` - passed: 92 tests.
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb\src\groundtruth_kb\bridge_dispatch_config.py scripts\cross_harness_bridge_trigger.py platform_tests\scripts\test_bridge_dispatch_config.py platform_tests\scripts\test_cross_harness_bridge_trigger.py` - passed.
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check groundtruth-kb\src\groundtruth_kb\bridge_dispatch_config.py scripts\cross_harness_bridge_trigger.py platform_tests\scripts\test_bridge_dispatch_config.py platform_tests\scripts\test_cross_harness_bridge_trigger.py` - passed.
- `gt bridge dispatch status` - returned LO candidate order `A, F, D, C` and PB candidate `B`.

## Observed Results

- Selector test passed: higher quality beats lower cost; equal quality uses lower cost; equal quality/cost uses higher availability.
- Spillover trigger test passed: three one-item LO candidates received three distinct selected-batch signatures in ranked order `A`, `F`, `D`.
- Full focused test files passed: `20 passed` for dispatch config, `92 passed` for cross-harness trigger.
- Ruff reported `All checks passed!`; format check reported `4 files already formatted`.
- Dispatch status still reports health `FAIL` because prior runtime launch-failure state remains for several recipients. The selected candidate order now reflects quality-first ranking: Loyal Opposition `A, F, D, C`.
- An initial full trigger-suite run failed because the shell inherited `GTKB_NO_CROSS_HARNESS_TRIGGER`; rerunning with that env var removed passed. This was an environment contamination issue, not an implementation assertion failure.

## Files Changed

- `config/dispatcher/rules.toml`
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`
- `scripts/cross_harness_bridge_trigger.py`
- `platform_tests/scripts/test_bridge_dispatch_config.py`
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py`

## Acceptance Criteria Status

- [x] Selection defaults and live dispatcher rules are quality, then cost, then availability.
- [x] Equal-quality candidates prefer lower cost, then higher availability.
- [x] Trigger planning spills remaining dispatchable items to additional ready targets.
- [x] Spillover assigns distinct selected batches; it does not broadcast the same item to every harness.
- [x] Existing readiness, provider-backoff, signature, lease, and compatibility recipient-state behavior remains covered by the focused trigger suite.

## Risk And Rollback

Residual risk: real launch failures are still only visible after a target is selected and spawned; a failed first target's specific selected item may wait until the next trigger cycle, where provider-backoff/readiness state can route it to another candidate. The implementation prevents queue-wide blocking by allowing other pending items to spill over in the same cycle and by preserving backoff-based fallback behavior.

Rollback is limited to the five files listed above. Reverting this change restores the previous first-ready-target-only behavior and availability/cost-first default ordering.

## Loyal Opposition Asks

1. Verify that spillover behavior satisfies the owner's non-blocking dispatch requirement without becoming duplicate broadcast.
2. Verify that the quality-first order is correctly reflected in config, default code behavior, and candidate status output.
3. Return `VERIFIED` if the implementation and report satisfy WI-4691; otherwise return `NO-GO` with concrete findings.
