NEW

# gtkb-wi4848-slice-3b-governed-substrate-registration-parity-gates — Register daemon substrate in governed CLI + live parity gates

bridge_kind: prime_proposal
Document: gtkb-wi4848-slice-3b-governed-substrate-registration-parity-gates
Version: 001
Author: Prime Builder (Cursor, harness E)
Date: 2026-06-26 UTC

author_identity: prime-builder/cursor
author_harness_id: E
author_session_context_id: cursor-e-pb-autoproc-20260626
author_model: Composer
author_model_version: cursor-agent
author_model_configuration: Cursor interactive Prime Builder

Project Authorization: PAUTH-MINVIABLE-ACTIVATION-DRIVE-2026-06-26
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4848

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py", "scripts/gtkb_dispatcher_daemon.py", "platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_validation.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Slice 3a (VERIFIED) armed substrate-gated live spawn behind `dispatcher_daemon` while keeping the governed selector on `cross_harness_trigger`. Slice **3b** completes the "hold the switch" path by registering `dispatcher_daemon` in the governed `gt mode set-bridge-substrate` transaction and applying the **same readiness + provider-failure backoff discipline** the live cross-harness trigger uses before spawn.

Concretely: extend `validate_bridge_substrate` and the CLI `Choice` enum; add a switch-time probe that the dispatcher daemon is running with a fresh heartbeat (mirroring the single-harness scheduled-task probe pattern); extend `compute_shadow_decisions` / `_execute_live_spawns` to call trigger `_is_dispatch_ready` and `_provider_failure_backoff_skip` so live daemon ticks do not bypass target readiness or backoff gates. **Does not** flip production substrate, re-enable dispatch, or perform go-live — those remain owner steps after 3c.

## Specification Links

- `ADR-DISPATCHER-ARCHITECTURE-001` — daemon is the GT-KB-owned dispatcher; governed substrate registration is the selector half of cutover prep.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — dispatch service substrate contract.
- `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` — governed substrate transactions and validator preflights.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — substrate read fresh at tick/switch time.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — append-only bridge filing.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — proposal linkage and spec-derived tests.
- `GOV-STANDING-BACKLOG-001` — WI-4848 governs.

## Prior Deliberations

- `DELIB-20266138` — owner "build flip, hold the switch" AUQ; slice 3b is the governed selector registration step named in slice 3a out-of-scope.
- `DELIB-20265888` — dispatch triggered by dispatcher service, not harness hooks.
- WI-4848 slice 3a VERIFIED at `bridge/gtkb-wi4848-slice-3a-daemon-substrate-gated-live-dispatch-004.md` — live branch exists; CLI enum gap confirmed at GO review.

## Owner Decisions / Input

No further owner decision required. `PAUTH-MINVIABLE-ACTIVATION-DRIVE-2026-06-26` covers WI-4848 cutover prep. Go-live (substrate flip + dispatch re-enable) remains a separate deliberate owner action.

## Requirement Sufficiency

Existing requirements sufficient — slice 3a GO/VERIFIED and `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` already define governed substrate switching; this slice registers the daemon value and closes the parity gap named in slice 3a out-of-scope.

## Spec-Derived Verification Plan

| Spec / clause | Test | Assertion |
|---|---|---|
| SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 (governed enum) | `test_validate_dispatcher_daemon_substrate_unknown_rejected` / `test_cli_choice_includes_dispatcher_daemon` (new) | `dispatcher_daemon` accepted by validator when daemon heartbeat fresh; rejected when daemon absent/stale; CLI Choice lists value |
| ADR-DISPATCHER-ARCHITECTURE-001 (readiness parity) | `test_daemon_live_skips_not_ready_target` (new) | patched `_is_dispatch_ready` returning False → decision records `*_dispatch_not_ready`, no `_spawn_harness` |
| ADR-DISPATCHER-ARCHITECTURE-001 (backoff parity) | `test_daemon_live_honors_provider_backoff_skip` (new) | patched `_provider_failure_backoff_skip` returning skip evidence → no spawn, reason propagated |
| No-regression | existing `test_mode_switch_bridge_substrate_validation.py` + full daemon test file | green |

Commands (pre-report): `python -m pytest platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_validation.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py -q --tb=short`; `ruff check` / `ruff format --check` on changed `.py` files.

## Risk / Rollback

- Risk: low. Registration alone does not change `harness-state/bridge-substrate.json` (stays `cross_harness_trigger`). Parity gates only affect live daemon ticks when substrate is already `dispatcher_daemon`.
- Rollback: revert validator/CLI/daemon parity diff; governed enum returns to pre-3b set.

## Bridge Filing

Append-only `bridge/gtkb-wi4848-slice-3b-governed-substrate-registration-parity-gates-001.md`.

## Recommended Commit Type

feat

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
