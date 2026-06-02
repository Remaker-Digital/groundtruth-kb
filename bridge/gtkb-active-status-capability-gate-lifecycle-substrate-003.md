NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: codex-gtkb-pb-2026-06-02
author_model: GPT-5 Codex
author_model_version: 2026-06-02
author_model_configuration: reasoning=high

# GT-KB Bridge Implementation Report - Active-Status Capability Gate Lifecycle and Substrate Alignment

bridge_kind: implementation_report
Document: gtkb-active-status-capability-gate-lifecycle-substrate
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-active-status-capability-gate-lifecycle-substrate-002.md
Approved proposal: bridge/gtkb-active-status-capability-gate-lifecycle-substrate-001.md
Project Authorization: PAUTH-WI-4213-ACTIVE-STATUS-CAPABILITY-GATE
Project: PROJECT-GTKB-ROLE-STATUS-ORTHOGONALITY-DISPATCH
Work Item: WI-4213
Recommended commit type: feat:

## Implementation Claim

The lifecycle/substrate companion slice for WI-4213 is complete.

Mode-switch transaction handling now preserves retained roles on non-active harness records instead of clearing those roles merely because the harness is not active. Active assignment still clears and suspends active harnesses that no longer hold an active role.

Mode-switch topology derivation and bridge-substrate Prime Builder attribution now require the active event-capability predicate before treating a role-retaining harness as bridge-event-capable. A harness must have the relevant role, `status == "active"`, and `event_driven_hooks is True` before topology/substrate helpers count it as an active bridge-event participant.

Targeted fixtures that exercise cross-harness dispatch now write `event_driven_hooks=true` for dispatch-capable active Codex/Claude records and write the DB-backed `harness-state/harness-registry.json` projection where the trigger now resolves role/status/capability state.

WI-3513 remains separate. This slice does not implement bridge writer serialization or INDEX write-contention remediation.

## Scope Boundary

This report covers only the target files authorized by `bridge/gtkb-active-status-capability-gate-lifecycle-substrate-001.md` and the implementation-start packet for `gtkb-active-status-capability-gate-lifecycle-substrate`.

The working tree also contains unrelated already-verified or previously started changes, including inventory drift files, registry/dispatch WI-4213 files, implementation authorization updates, and multiple bridge artifacts. Those are not part of this implementation report.

## Specification Links

- `ADR-ROLE-STATUS-ORTHOGONALITY-001`
- `DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001`
- `REQ-HARNESS-REGISTRY-001`
- `GOV-HARNESS-ROLE-PORTABILITY-001`
- `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Owner Decisions / Input

No new owner decision is required. The implementation follows the approved proposal, PAUTH-WI-4213-ACTIVE-STATUS-CAPABILITY-GATE, the verified WI-4213 formalization threads, and the owner directive to continue until the listed work items are completed.

## Prior Deliberations

- `bridge/gtkb-active-status-capability-gate-lifecycle-substrate-001.md` - approved implementation proposal.
- `bridge/gtkb-active-status-capability-gate-lifecycle-substrate-002.md` - Loyal Opposition GO verdict.
- `bridge/gtkb-active-status-capability-gate-formalization-004.md` - VERIFIED formal authority for role/status/capability orthogonality.
- `bridge/gtkb-active-status-capability-gate-registry-dispatch-004.md` - VERIFIED registry/dispatch half of WI-4213.
- `DELIB-2813` - owner directive and active project authorization context cited by the proposal.

## Implementation-Start Authorization

- `python scripts\implementation_authorization.py begin --bridge-id gtkb-active-status-capability-gate-lifecycle-substrate` created packet `sha256:0a0f39832d7a40c800a9024500641868cca8b59f34ba48dea0df42b8cdaad6a8` before implementation work began; expires `2026-06-02T15:13:06Z`.
- A fresh pre-filing packet readback for the same bridge id returned `sha256:d486fc67882266450e02f746c1d706e0ab6bbc7ff07b7b20cd9617514155494a`, `latest_status: "GO"`, and `requirement_sufficiency: "sufficient"`.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `ADR-ROLE-STATUS-ORTHOGONALITY-001` | `test_apply_role_switch_preserves_non_active_retained_roles` proves non-active retained roles survive mode-switch role assignment. |
| `DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001` | `test_single_harness_substrate_rejects_non_event_capable_single_holder` and dispatch fixture regressions prove topology/substrate eligibility requires active status plus `event_driven_hooks=true`. |
| `REQ-HARNESS-REGISTRY-001` | Updated tests write/read the DB-backed `harness-state/harness-registry.json` projection with role/status/capability fields. |
| `GOV-HARNESS-ROLE-PORTABILITY-001` | Transaction coverage proves non-active C can retain Prime Builder role without active assignment. |
| `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` | Combined WI-4213 regression set keeps cross-harness dispatch, suppression, durable-keyed dispatch, and substrate behavior passing together. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This report is filed after latest `GO`; the implementation-report helper inserts `NEW: bridge/gtkb-active-status-capability-gate-lifecycle-substrate-003.md` under the canonical `bridge/INDEX.md` entry. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation-start packets were issued for the latest-GO bridge thread before this report was filed. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Git target diff is limited to the proposal target paths. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Work proceeded through bridge GO and implementation-start packet paths. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | This report carries Project Authorization, Project, and Work Item metadata. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Linked specs from the approved proposal are carried forward here. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This table maps each linked governing surface to executed verification evidence. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Bridge thread, implementation packet, preflight, and verification commands were run from live files during this run. |
| `GOV-STANDING-BACKLOG-001` | WI-4213 completion remains pending until Loyal Opposition verifies this report. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Source/test changes, implementation-start packet, and this bridge report preserve durable implementation evidence. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Work remains in GO -> implementation report NEW -> Loyal Opposition verification lifecycle. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | The lifecycle/substrate correction is preserved as bridge and test artifacts rather than transient chat state. |

## Commands Run

- `python scripts\implementation_authorization.py begin --bridge-id gtkb-active-status-capability-gate-lifecycle-substrate`
- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-active-status-capability-gate-lifecycle-substrate`
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-active-status-capability-gate-lifecycle-substrate`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff format groundtruth-kb\src\groundtruth_kb\mode_switch\bridge_substrate.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\groundtruth_kb\test_mode_switch_transaction.py platform_tests\groundtruth_kb\test_mode_switch_bridge_substrate.py platform_tests\scripts\test_cross_harness_trigger_durable_keyed_regression.py platform_tests\scripts\test_cross_harness_trigger_suppression.py platform_tests\scripts\test_governing_specs_preserved.py -q --tb=short --basetemp=.gtkb-state\pytest-tmp-lifecycle-substrate-kw-0602-rerun`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb\src\groundtruth_kb\mode_switch\derive.py groundtruth-kb\src\groundtruth_kb\mode_switch\transaction.py groundtruth-kb\src\groundtruth_kb\mode_switch\bridge_substrate.py platform_tests\groundtruth_kb\test_mode_switch_transaction.py platform_tests\groundtruth_kb\test_mode_switch_bridge_substrate.py platform_tests\scripts\test_cross_harness_trigger_durable_keyed_regression.py platform_tests\scripts\test_cross_harness_trigger_suppression.py platform_tests\scripts\test_governing_specs_preserved.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check groundtruth-kb\src\groundtruth_kb\mode_switch\derive.py groundtruth-kb\src\groundtruth_kb\mode_switch\transaction.py groundtruth-kb\src\groundtruth_kb\mode_switch\bridge_substrate.py platform_tests\groundtruth_kb\test_mode_switch_transaction.py platform_tests\groundtruth_kb\test_mode_switch_bridge_substrate.py platform_tests\scripts\test_cross_harness_trigger_durable_keyed_regression.py platform_tests\scripts\test_cross_harness_trigger_suppression.py platform_tests\scripts\test_governing_specs_preserved.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_cross_harness_bridge_trigger.py platform_tests\groundtruth_kb\test_mode_switch_invariants.py groundtruth-kb\tests\test_harness_projection.py platform_tests\groundtruth_kb\test_mode_switch_transaction.py platform_tests\groundtruth_kb\test_mode_switch_bridge_substrate.py platform_tests\scripts\test_cross_harness_trigger_durable_keyed_regression.py platform_tests\scripts\test_cross_harness_trigger_suppression.py platform_tests\scripts\test_governing_specs_preserved.py -q --tb=short --basetemp=.gtkb-state\pytest-tmp-wi4213-combined-kw-0602`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb\src\groundtruth_kb\mode_switch\derive.py groundtruth-kb\src\groundtruth_kb\mode_switch\transaction.py groundtruth-kb\src\groundtruth_kb\mode_switch\bridge_substrate.py groundtruth-kb\src\groundtruth_kb\harness_ops.py groundtruth-kb\src\groundtruth_kb\harness_projection.py scripts\cross_harness_bridge_trigger.py platform_tests\scripts\test_cross_harness_bridge_trigger.py platform_tests\groundtruth_kb\test_mode_switch_invariants.py groundtruth-kb\tests\test_harness_projection.py platform_tests\groundtruth_kb\test_mode_switch_transaction.py platform_tests\groundtruth_kb\test_mode_switch_bridge_substrate.py platform_tests\scripts\test_cross_harness_trigger_durable_keyed_regression.py platform_tests\scripts\test_cross_harness_trigger_suppression.py platform_tests\scripts\test_governing_specs_preserved.py`
- `git diff --name-only -- groundtruth-kb\src\groundtruth_kb\mode_switch\transaction.py groundtruth-kb\src\groundtruth_kb\mode_switch\derive.py groundtruth-kb\src\groundtruth_kb\mode_switch\bridge_substrate.py platform_tests\groundtruth_kb\test_mode_switch_transaction.py platform_tests\groundtruth_kb\test_mode_switch_bridge_substrate.py platform_tests\scripts\test_cross_harness_trigger_durable_keyed_regression.py platform_tests\scripts\test_cross_harness_trigger_suppression.py platform_tests\scripts\test_governing_specs_preserved.py`
- `git diff --stat -- groundtruth-kb\src\groundtruth_kb\mode_switch\transaction.py groundtruth-kb\src\groundtruth_kb\mode_switch\derive.py groundtruth-kb\src\groundtruth_kb\mode_switch\bridge_substrate.py platform_tests\groundtruth_kb\test_mode_switch_transaction.py platform_tests\groundtruth_kb\test_mode_switch_bridge_substrate.py platform_tests\scripts\test_cross_harness_trigger_durable_keyed_regression.py platform_tests\scripts\test_cross_harness_trigger_suppression.py platform_tests\scripts\test_governing_specs_preserved.py`
- `rg -n "(?i)(api[_-]?key|secret|password|token|credential|bearer|BEGIN (RSA|OPENSSH|PRIVATE) KEY)" <target files>`

## Observed Results

- Applicability preflight: passed; missing required specs `[]`; missing advisory specs `[]`.
- Clause preflight: passed; zero blocking gaps.
- Lifecycle/substrate focused pytest: `48 passed, 1 warning in 3.33s` and repeat report run `48 passed, 1 warning in 3.90s`; warning was `PytestCacheWarning` for `.pytest_cache` path creation.
- Target ruff check: `All checks passed!`.
- Target ruff format-check: `8 files already formatted`.
- Combined WI-4213 regression pytest: `109 passed, 1 warning in 5.88s`; warning was the same `.pytest_cache` warning.
- Combined WI-4213 ruff check: `All checks passed!`.
- Credential/string scan found no credential values. Matches were ordinary test/source uses of the word `token` in parser and sentinel tests.
- Authorized git target diff:
  - `groundtruth-kb/src/groundtruth_kb/mode_switch/bridge_substrate.py`
  - `groundtruth-kb/src/groundtruth_kb/mode_switch/derive.py`
  - `groundtruth-kb/src/groundtruth_kb/mode_switch/transaction.py`
  - `platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate.py`
  - `platform_tests/groundtruth_kb/test_mode_switch_transaction.py`
  - `platform_tests/scripts/test_cross_harness_trigger_durable_keyed_regression.py`
  - `platform_tests/scripts/test_cross_harness_trigger_suppression.py`
  - `platform_tests/scripts/test_governing_specs_preserved.py`
- Target diff stat: 8 files changed, 183 insertions, 30 deletions.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/mode_switch/bridge_substrate.py`
- `groundtruth-kb/src/groundtruth_kb/mode_switch/derive.py`
- `groundtruth-kb/src/groundtruth_kb/mode_switch/transaction.py`
- `platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate.py`
- `platform_tests/groundtruth_kb/test_mode_switch_transaction.py`
- `platform_tests/scripts/test_cross_harness_trigger_durable_keyed_regression.py`
- `platform_tests/scripts/test_cross_harness_trigger_suppression.py`
- `platform_tests/scripts/test_governing_specs_preserved.py`

## Acceptance Criteria Status

- [x] Mode-switch transaction and harness lifecycle paths do not erase retained roles from non-active harnesses merely because the harness is non-active.
- [x] Topology/substrate helpers require active status and `event_driven_hooks=true` before treating a role-retaining harness as a bridge-event-capable active participant.
- [x] Tests that exercise event-driven dispatch fixtures include explicit capability fields, and stale role-assignment-only trigger assertions are migrated to the registry projection where applicable.
- [x] Targeted pytest, ruff check, and ruff format-check passed.
- [x] Combined WI-4213 registry/dispatch plus lifecycle/substrate regression tests passed.
- [x] WI-3513 remains open/separate and is not implemented by this slice.

## Risk And Rollback

Residual risk is limited to mode-switch/substrate behavior in mixed active, registered, suspended, and non-event-capable topologies. The implementation keeps dispatch/substrate eligibility fail-closed for missing or false event capability while preserving retained non-active role metadata. Rollback restores the previous active-only role rewrite, topology predicate, bridge-substrate Prime Builder resolver, and targeted test fixtures; bridge audit files remain append-only.

## Loyal Opposition Asks

1. Verify that non-active retained roles are preserved by the mode-switch transaction path.
2. Verify that topology/substrate eligibility now requires role match, active status, and event-driven hook capability.
3. Verify that updated fixtures cover the DB-backed harness registry projection expected by the cross-harness trigger.
4. Verify that WI-3513 remains separate and was not implemented here.
5. Return VERIFIED if the implementation satisfies the approved proposal, otherwise return NO-GO with findings.
