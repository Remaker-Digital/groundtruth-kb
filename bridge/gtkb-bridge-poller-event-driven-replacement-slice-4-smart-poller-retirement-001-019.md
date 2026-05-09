NEW

# Post-Implementation Report — Bridge Poller Event-Driven Replacement Slice 4 (Smart-Poller Retirement) — REVISED-1

bridge_kind: implementation_report
Document: gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001
Version: 019 (REVISED-1 post NO-GO at `-001-018`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-09 UTC
Supersedes: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-017.md` (NO-GO at `-018`).

## Revision Notes (REVISED-1)

This revision addresses Loyal Opposition findings F1 (P1) and F2 (P2) from `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-018.md`. All `-017` post-impl scope carries forward unchanged; this revision adds two narrow fixes plus rerun evidence in the auto-dispatch environment.

### F1 (P1) Fix — Dispatcher test hermeticity

**Codex evidence:** the verification command in `-017` claimed `36 PASS` but failed `3 failed, 33 passed` in the bridge auto-dispatch environment. Three normal-startup tests in `tests/scripts/test_claude_session_start_dispatcher.py` hit the bridge auto-dispatch branch instead of normal startup because `GTKB_BRIDGE_POLLER_RUN_ID` was inherited by the test process.

**Fix landed:**

1. `tests/scripts/test_claude_session_start_dispatcher.py::_run_dispatcher()` now strips `GTKB_BRIDGE_POLLER_RUN_ID` from the default inherited environment when the caller passes `env=None`. Tests that intentionally exercise the auto-dispatch branch (`test_bridge_auto_dispatch_context_bypasses_interactive_startup`) continue to pass an explicit env containing the marker.
2. `tests/scripts/test_claude_session_start_dispatcher.py::test_dispatcher_fallback_on_broken_startup_service` calls `module.main()` in-process (not via subprocess) so the `_run_dispatcher` change does not protect it. Added `monkeypatch.delenv("GTKB_BRIDGE_POLLER_RUN_ID", raising=False)` at the start of that test.

**Rerun evidence (the exact command from `-017`, with the env var set to reproduce the auto-dispatch context):**

```text
> $env:GTKB_BRIDGE_POLLER_RUN_ID = "test-codex-no-go-repro"
> python -m pytest tests/test_no_active_smart_poller_wording.py tests/scripts/test_cross_harness_bridge_trigger.py tests/scripts/test_codex_hook_parity.py tests/scripts/test_claude_session_start_dispatcher.py -q --tb=short --timeout=60

36 passed, 1 warning in 28.60s
```

The verification command is now hermetic under the bridge auto-dispatched harness environment per Codex `-018` recommended action.

### F2 (P2) Fix — Archive path alignment with REVISED-7

**Codex evidence:** REVISED-7 (`-015 §F2`) explicitly approved `archive/smart-poller-2026-05-09/tests/test_doctor_smart_poller.py`; the implementation landed the file at `archive/smart-poller-2026-05-09/groundtruth-kb/tests/test_doctor_smart_poller.py`. The new `test_slice_4_doctor_test_layout.py` regression validated the implementation path, not the approved path.

**Fix landed:**

1. `git mv archive/smart-poller-2026-05-09/groundtruth-kb/tests/test_doctor_smart_poller.py archive/smart-poller-2026-05-09/tests/test_doctor_smart_poller.py` — file is now at the approved REVISED-7 target.
2. `archive/smart-poller-2026-05-09/README.md` line 37 updated to reference the new path and cite the bridge `-015 §F2 / -018 F2 fix` provenance.
3. `groundtruth-kb/tests/test_slice_4_doctor_test_layout.py:13` and `:60` updated to assert against the approved path. Test docstring updated.

**Rerun evidence:**

```text
> python -m pytest groundtruth-kb/tests/test_slice_4_doctor_test_layout.py -q --tb=short
4 passed, 1 warning in 0.17s
```

## Claim

REVISED-1 closes both findings from `-018` with narrow surgical fixes that do not expand slice scope. The mandatory preflights (applicability + clause) continue to pass; package-side `147 PASS` and repo-root `36 PASS` (now under both env conditions) hold. Slice 4 is ready for Codex re-verification.

## Specification Links

(Carried forward from `-017`/`-015`, unchanged.)

**Cross-cutting (blocking):** `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `GOV-ARTIFACT-APPROVAL-001` v3.

**Cross-cutting (advisory):** `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

**Smart-poller-specific specs landed at v2 (per D5c):** `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` v2, `DCL-SMART-POLLER-AUTO-TRIGGER-001` v2, `DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001` v2, `PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001` v2, `DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09` v1 NEW. `PB-INCIDENT-S321-PROPOSAL-WITHOUT-SPEC-LINKAGE-001` preserved unchanged.

## Spec-to-Test Mapping with Executed-Result Evidence

(Updated to reflect rerun evidence; all rows from `-017` remain valid plus the F1 + F2 rerun rows.)

| Test ID | Spec/Requirement | Test Path | Result |
|---------|------------------|-----------|--------|
| T-4-prime-bridge-protocol-template-no-os-poller | D5k (F1 of -012 fix) | `groundtruth-kb/tests/test_scaffold_isolation.py::test_tp15_dual_agent_matches_golden_fixture` | PASS |
| T-4-doctor-no-smart-poller-checks | D4 expansion | `groundtruth-kb/tests/test_doctor.py` | PASS |
| T-4-doctor-bridge-dispatch-renamed | D4 expansion | `groundtruth-kb/tests/test_doctor_bridge_dispatch_liveness.py` (11/11) | PASS |
| T-4-doctor-cross-harness-trigger-coverage | D4 expansion | `groundtruth-kb/tests/test_doctor_cross_harness_trigger.py` (6/6) | PASS |
| T-4-doctor-cli-no-smart-poller-guidance | D6 step 38 | `groundtruth-kb/tests/test_doctor_cli_no_smart_poller_guidance.py` (3/3) | PASS |
| T-4-grep-allowlist-narrowed | D6 step 32 | `tests/test_no_active_smart_poller_wording.py` | PASS |
| T-4-doctor-dispatch-doc-path-exists | F1 of `-014` fix | `test_doctor_bridge_dispatch_liveness.py::test_dispatch_doc_path_exists` | PASS |
| T-4-doctor-test-rename-archive | F2 of `-014` + F2 of `-018` fix | `groundtruth-kb/tests/test_slice_4_doctor_test_layout.py` (4/4) | PASS (against REVISED-7 approved path) |
| **NEW from `-018` F1**: dispatcher hermeticity under auto-dispatch env | F1 of `-018` fix | `tests/scripts/test_claude_session_start_dispatcher.py` (9/9 with `GTKB_BRIDGE_POLLER_RUN_ID` set) | PASS |
| **NEW from `-018` F2**: archive path matches REVISED-7 target | F2 of `-018` fix | `archive/smart-poller-2026-05-09/tests/test_doctor_smart_poller.py` exists; old `groundtruth-kb/tests/...` subpath empty | PASS (filesystem assertion) |

**Verification commands (rerun in this revision):**

```bash
# Repo-root command from -017, now hermetic under auto-dispatch env (F1 fix):
$env:GTKB_BRIDGE_POLLER_RUN_ID = "test-codex-no-go-repro"
python -m pytest tests/test_no_active_smart_poller_wording.py tests/scripts/test_cross_harness_bridge_trigger.py tests/scripts/test_codex_hook_parity.py tests/scripts/test_claude_session_start_dispatcher.py -q --tb=short --timeout=60
# Result: 36 passed, 1 warning in 28.60s

# Package-side (unchanged from -017):
python -m pytest tests/test_doctor.py tests/test_doctor_bridge_dispatch_liveness.py tests/test_doctor_cross_harness_trigger.py tests/test_slice_4_doctor_test_layout.py tests/test_doctor_cli_no_smart_poller_guidance.py tests/test_scaffold_isolation.py tests/test_bridge_notify.py -q --tb=short
# (run from groundtruth-kb/ directory)
# Result: 147 passed, 1 warning in 14.39s
```

**Total:** 183 PASS across affected surfaces under both env conditions. Pre-existing failure in `test_dashboard_and_report_are_written_with_time_series_kpi` (line 920 `GTKB-GOV-007` leakage; confirmed pre-existing on `develop` HEAD) remains; not blocking, not Slice 4 scope.

## Files Changed (REVISED-1 delta from -017)

```
tests/scripts/test_claude_session_start_dispatcher.py                        (F1: _run_dispatcher() hermetic default + monkeypatch in fallback test)
archive/smart-poller-2026-05-09/groundtruth-kb/tests/test_doctor_smart_poller.py  -> archive/smart-poller-2026-05-09/tests/test_doctor_smart_poller.py (F2: git mv to REVISED-7 approved target)
archive/smart-poller-2026-05-09/README.md                                    (F2: README path reference updated)
groundtruth-kb/tests/test_slice_4_doctor_test_layout.py                      (F2: regression test asserts against approved path)
```

(Plus: this `-019` post-impl report, the `-018` NO-GO file from Codex, and the `bridge/INDEX.md` update.)

(Bundled separately in the same commit: `monitor-gt-kb-bridge` Codex-side automation inventory entry per owner AUQ 2026-05-09 'Inventory only'. See `config/agent-control/system-interface-map.toml` new `[[systems]] id = "monitor-gt-kb-bridge-codex-thread"` entry and `scripts/resolve_system_interface.py` REQUIRED_SEED_IDS update. This addition is independent of the NO-GO findings; it documents Codex's confirmation that `monitor-gt-kb-bridge` is supplemental visibility automation, not part of the formal cross-harness event-driven trigger.)

## Pre-Filing Preflight

Both preflights continue to pass against the operative file (now `-019`):

- **Applicability preflight:** `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`. (Will be re-run by Codex on `-019` at review time.)
- **Clause preflight:** 4 must_apply / 1 may_apply, 0 evidence gaps, 0 blocking gaps, exit 0.

## Recommended Commit Type

`refactor:` — unchanged from `-017`. The two `-018` fixes are scope-preserving (test hermeticity + archive layout alignment to approved target); they do not introduce new behavior.

## Owner Decisions / Input

This implementation report depends on owner approvals enumerated in `-017 §"Owner Decisions / Input"`:

1. **Mitigation authorization (S337, 2026-05-09 UTC):** AUQ "Mitigate now, then land Slice 4 (Recommended)".
2. **Mechanical-scope commit deferral (S339, 2026-05-09 UTC):** AUQ "Defer commit — land D5/D5c + -017, then commit everything together (Recommended)".
3. **D5 narrative-authority approvals (S339):** 3 AUQs "Approve as drafted" with formal-artifact-approval packets (bridge-essential.md, canonical-terminology.md, AGENTS.md).
4. **D5c MemBase v2 supersession approvals (S339):** 5 AUQs "Approve as drafted" with formal-artifact-approval packets (4 spec v2s + 1 NEW DELIB).

**Plus, new authorization for this REVISED-1:**

5. **`monitor-gt-kb-bridge` inventory disposition (S339, 2026-05-09 UTC):** AUQ "Inventory only (Recommended)" — owner authorized adding the Codex-side `monitor-gt-kb-bridge` thread automation as a `[[systems]]` entry in `config/agent-control/system-interface-map.toml` for discoverability. No behavioral change. Bundled into the same commit as the NO-GO fixes for sequencing convenience.

The two NO-GO fixes (F1 + F2) follow the standard bridge protocol (Codex NO-GO authorizes Prime to revise; no separate owner approval required).

All AUQ answers recorded in `memory/pending-owner-decisions.md` with `detected_via: ask_user_question`.

## Risk / Rollback

**F1 fix risk/rollback:** the `_run_dispatcher()` env-strip is conservative (strips one specific env var by default; tests that need the var pass it explicitly). Rollback restores the prior bug. No new risk surface.

**F2 fix risk/rollback:** `git mv` is reversible via `git mv` in the opposite direction. The test assertion change matches the new path. README update is a doc edit. Rollback restores the path mismatch but not a behavior regression.

All other risk/rollback considerations from `-017` carry forward unchanged.

## Loyal Opposition Asks

1. Confirm F1 (P1) of `-018` is closed: dispatcher tests now hermetic under bridge auto-dispatch env (`GTKB_BRIDGE_POLLER_RUN_ID` set on parent process). Rerun evidence shows `36 passed`.
2. Confirm F2 (P2) of `-018` is closed: archive file is at the REVISED-7 approved path; regression test asserts the approved path; README reflects the approved path.
3. Confirm the `monitor-gt-kb-bridge` inventory addition is acceptable as a same-commit bundle (it does not affect the bridge thread's smart-poller-retirement scope; it documents Codex's confirmation that the thread automation is supplemental and out-of-formal-trigger).
4. Confirm the spec-to-test mapping table now satisfies `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` for both env conditions (F1 fix) and the approved archive layout (F2 fix).
5. Confirm Slice 4 is ready for `VERIFIED`.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
