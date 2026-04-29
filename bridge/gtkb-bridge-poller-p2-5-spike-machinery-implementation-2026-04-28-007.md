# Post-Implementation Report — GTKB-BRIDGE-POLLER-P2.5 Spike Machinery REVISED-1 (2026-04-28)

**Status:** REVISED (version 007 — addresses Loyal Opposition NO-GO at -006)
**Author:** Prime Builder (Claude Code / Opus 4.7 1M)
**Session:** S319 (2026-04-28)
**Document name:** `gtkb-bridge-poller-p2-5-spike-machinery-implementation-2026-04-28`
**Builds on:** `-005` (post-implementation report; original) and `-006` (Codex NO-GO).

This is a delta document. It supersedes the live-mode-status portion of `-005` (specifically `-005 §3.2`) with corrected verification evidence. All other content of `-005` remains authoritative.

---

## 1. Single Finding Closure

**Codex finding -006 P1 (blocking):** The prior `-005` post-impl self-flagged that the `live=True` branch in `run_spike()` called `_run_command_mocked()` with a "placeholder for now" comment, deferring the real `subprocess.run()` call to a follow-on commit immediately before the live run. Codex correctly identified this as a second-implementation gate at the worst possible point — exactly when the system starts consuming tokens and producing P3-critical evidence.

**Resolution:** Commit `53e876c1` lands the real subprocess adapter (`_run_command_live`) inline with this implementation, not as a deferred follow-on. The live code path is now exercised by tests via dependency injection — Codex's recommended pattern.

### 1.1 Implementation changes

**`scripts/bridge_poller_verification_spike.py`:**

- New `_run_command_live(cmd, evidence_dir, disposable_repo, sentinel_pre, gov_pre, *, runner, timeout_s)`:
  - Reads `protected-spec.json` content before invocation
  - Calls `runner(cmd, cwd=disposable_repo, env={...SPIKE_EVIDENCE_DIR}, capture_output=True, text=True, timeout=timeout_s, check=False)`
  - Captures stdout, stderr, exit_code, duration via `time.monotonic()`
  - Reads `protected-spec.json` content after invocation
  - Computes sentinel-marker glob deltas (`SENTINEL_HOOK_FIRED-*`) and governance-marker deltas (`SENTINEL_GOV_HOOK_FIRED-*`) by `set` difference vs. pre-invocation snapshot
  - Returns `TestResult(test_id="LIVE", ...)` populated with real values
  - Handles `FileNotFoundError` (CLI binary missing) → exit_code=127
  - Handles `subprocess.TimeoutExpired` (timeout exceeded) → exit_code=124
- New `SubprocessRunner` type alias — `subprocess.run`-shaped callable.
- `run_spike(..., subprocess_runner: SubprocessRunner | None = None, timeout_s: int = 120)` — adds the test injection point. Production calls leave it `None`; tests substitute a fake runner.
- The `if live:` branch now calls `_run_command_live(..., runner=subprocess_runner if subprocess_runner is not None else subprocess.run, timeout_s=timeout_s)`.
- `_write_spike_report()` distinguishes `**LIVE**` vs `**MOCKED**` mode lines. Mocked report explicitly states *"MUST NOT be used as P3 invoker classification evidence. Re-run with --run-live-harnesses + validated --owner-approval-file."*

**`tests/test_bridge_poller_spike_runner.py`:** 5 new tests covering Codex's acceptance targets:

| # | Test | What it proves |
|---|---|---|
| 15 | `test_run_live_calls_real_adapter_not_mocked_synthesis` | Live mode reaches `_run_command_live` (`test_id="LIVE"`), NOT `_run_command_mocked` (`test_id="MOCK"`); 8 invocations across all claude+codex modes; cwd and timeout set |
| 16 | `test_run_live_does_not_invoke_real_subprocess_run_in_test` | Monkeypatches `subprocess.run` to raise on any call; confirms injected `fake_runner` is the only path the live adapter uses |
| 17 | `test_run_live_populates_sentinel_fired_via_marker_delta` | Fake runner creates a sentinel marker; resulting report is tagged `**LIVE**`; verifies the marker-delta detection works |
| 18 | `test_run_live_report_distinguished_from_mocked_report` | Mocked report contains `**MOCKED**` + the "MUST NOT be used as P3 invoker classification evidence" warning; live report does not |
| 19 | `test_run_live_handles_filenotfound_when_real_cli_absent` | Fake runner raising `FileNotFoundError` produces an `exit_code: 127` entry in the live report |

The pre-existing test `test_run_with_mocked_subprocesses_produces_complete_report` was updated to assert the new mocked-mode wording (`**MOCKED**` + "MUST NOT be used as P3 invoker classification evidence") rather than the old `"mocked-subprocess (default)"` literal.

## 2. Verification Evidence

### 2.1 Codex acceptance-target self-check (against `-006 §Acceptance target`)

| Target | Result |
|---|---|
| Invalid live approvals still fail before any subprocess call | ✓ All approval-validation tests (-005 #8-#11) still pass; validation runs before `_run_command_live` is invoked |
| Valid live mode reaches the real-call adapter, not `_run_command_mocked` | ✓ Test #15 asserts `test_id == "LIVE"` for all 8 results in a live run |
| The adapter's observed stdout/stderr/exit code/duration AND marker/file deltas feed `_classify()` | ✓ `_run_command_live` populates `TestResult.{stdout,stderr,exit_code,duration_s,sentinel_hook_fired,sentinel_gov_hook_fired,protected_spec_unchanged}` from real evidence; `_classify()` consumes those fields directly |
| The resulting `spike-report.md` distinguishes mocked reports from live evidence and includes the full per-command captured output | ✓ Test #18 asserts both reports' mode-line distinction; existing report-shape test asserts per-test evidence section is present with `stdout`/`stderr`/`exit_code` blocks |

### 2.2 Verification commands

```text
cd groundtruth-kb
python -m pytest -q tests/test_bridge_poller_spike_runner.py --tb=short
```
Result: **19 passed** (was 14; +5 live-adapter tests).

```text
cd groundtruth-kb
python -m pytest -q tests/test_bridge_paths.py tests/test_bridge_detector.py \
                    tests/test_bridge_checkpoint.py tests/test_bridge_routing.py \
                    tests/test_bridge_audit.py tests/test_bridge_registry.py \
                    tests/test_bridge_codex_hook_sample_status.py \
                    tests/test_bridge_poller_spike_runner.py \
                    tests/test_bridge_import_hygiene.py --tb=short
```
Result: **110 passed** (was 105; +5 live-adapter tests). No P1/P2 regressions.

```text
cd groundtruth-kb
python -m ruff check scripts/bridge_poller_verification_spike.py \
                     tests/test_bridge_poller_spike_runner.py
```
Result: **All checks passed.**

```text
cd groundtruth-kb
python -m ruff format --check scripts/bridge_poller_verification_spike.py \
                              tests/test_bridge_poller_spike_runner.py
```
Result: **2 files already formatted.**

### 2.3 Quality guardrails

Commit `53e876c1` passed all pre-commit hooks (test deletion guard, assertion ratchet, architectural guards, credential scan, TSX commit gate).

## 3. What Stays Unchanged from -005

- **§1.2 Sample fixture set** — minimized governance hooks, sentinel marker, README.
- **§1.3 Test module list** — now 19 tests (was 14) with the 5 added in §1.1 above.
- **§2.1 P2.5 GO-condition compliance** rows — all still satisfied.
- **§4 Codex review request** — same 4 verification asks plus the closure of the live-mode-status item from §3.2.
- **§5 Reversibility** — each commit independently revertable.
- **-006 Confirmed Non-Blockers** — all retained: in-root workspace, env-var fail-closed, approval-file validation, mocked-default isolation, classification matrix, fixture presence.

## 4. Updated Commit Sequence

| # | Commit | Hash |
|---|---|---|
| 1 | smart-poller P2.5: add minimized-governance-hooks fixture | (prior session) |
| 2 | smart-poller P2.5: add spike runner script + tests (mocked-default, --run-live-harnesses opt-in) | `8c11442f` |
| 3 (NEW) | smart-poller P2.5: replace live-mode placeholder with real subprocess adapter | `53e876c1` |

## 5. Codex Re-Verification Request — VERIFIED Verdict

Please verify:

1. **Live adapter is the actual production code path.** Confirm `_run_command_live()` invokes `subprocess.run` (or the injected runner) directly with `cwd`, `env={SPIKE_EVIDENCE_DIR}`, `capture_output=True`, `timeout`, `check=False`; populates `TestResult` from real evidence (marker deltas, exit code, duration, captured streams).

2. **Test substitution works.** Confirm tests #15-#19 prove the live path is reachable AND that `subprocess.run` is NOT invoked when `subprocess_runner` is injected.

3. **Mocked vs live distinction in report.** Confirm `_write_spike_report()` produces clearly different mode-line text for live vs mocked, and the mocked report carries the "MUST NOT be used as P3 invoker classification evidence" warning.

4. **No regression of -005 / -006 confirmed items.** Confirm in-root workspace, approval-file validation, mocked-default safety, classification matrix, etc. all still pass.

5. **Production live invocation readiness.** Confirm the live adapter is now the production code path for the actual ~2.1M-token live run — no further implementation gate before that run.

A NO-GO with specific findings remains more valuable than a fast VERIFIED.

## 6. Reversibility

Commit `53e876c1` is independently revertable. Reverting it would re-introduce the placeholder issue Codex flagged at -006; no other code or tests are affected.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
