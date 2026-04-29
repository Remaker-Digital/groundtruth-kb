VERIFIED

# Loyal Opposition Re-Verification - GTKB-BRIDGE-POLLER-P2.5 Spike Machinery Implementation

Reviewed: 2026-04-28
Subject: `bridge/gtkb-bridge-poller-p2-5-spike-machinery-implementation-2026-04-28-007.md`
Scope: revised live-mode subprocess adapter and tests after Codex NO-GO at `-006`
Verdict: VERIFIED

## Prior Deliberations

Deliberation searches:

```text
python -m groundtruth_kb deliberations search "bridge poller P2.5 spike machinery implementation verification"
python -m groundtruth_kb deliberations search "bridge poller P2.5 live adapter re-verification"
```

Relevant context includes:

- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION`: owner clarified that the old poller halt was implementation-specific and that the verified smart poller is opt-out when functional.
- `DELIB-1348`: prior Loyal Opposition NO-GO for the P2.5 verification spike.
- `DELIB-1354`: prior GO for the revised smart bridge trigger after root-boundary and approval concerns were closed.
- Prior bridge response `bridge/gtkb-bridge-poller-p2-5-spike-machinery-implementation-2026-04-28-006.md`: NO-GO because live mode still called mocked subprocess synthesis.

## Claim

VERIFIED. The revision closes the `-006` blocker. The production live path now reaches `_run_command_live()` after approval validation, and `_run_command_live()` invokes `subprocess.run` by default, with an injectable runner used only for test substitution.

## Evidence

### Live adapter is now the production path

- `groundtruth-kb/scripts/bridge_poller_verification_spike.py:300-369` defines `_run_command_live()`.
- `groundtruth-kb/scripts/bridge_poller_verification_spike.py:325-336` builds an environment containing `SPIKE_EVIDENCE_DIR` and invokes the supplied runner with:
  - `cwd=str(disposable_repo)`
  - `env=env`
  - `capture_output=True`
  - `text=True`
  - `timeout=timeout_s`
  - `check=False`
- `groundtruth-kb/scripts/bridge_poller_verification_spike.py:337-349` captures exit code, stdout, stderr, timeout and missing-binary cases, and duration.
- `groundtruth-kb/scripts/bridge_poller_verification_spike.py:351-368` computes sentinel and governance marker deltas, checks `protected-spec.json` before/after content, and returns `TestResult(test_id="LIVE", ...)`.
- `groundtruth-kb/scripts/bridge_poller_verification_spike.py:477-486` validates live approval input before entering the command loop.
- `groundtruth-kb/scripts/bridge_poller_verification_spike.py:496-505` calls `_run_command_live(...)` in the `if live:` branch.
- `groundtruth-kb/scripts/bridge_poller_verification_spike.py:503` uses the injected runner when present, otherwise `subprocess.run`; production CLI invocation leaves `subprocess_runner=None`.

### Mocked and live reports are distinguishable

- `groundtruth-kb/scripts/bridge_poller_verification_spike.py:415-426` writes distinct mode lines:
  - `**LIVE**` for live runs.
  - `**MOCKED**` for default CI-safe runs.
- The mocked mode line states that the report "MUST NOT be used as P3 invoker classification evidence."
- `groundtruth-kb/scripts/bridge_poller_verification_spike.py:437-449` preserves per-command evidence, including command, exit code, duration, sentinel/governance flags, protected-spec status, stdout, and stderr.

### Tests cover the revised path

- `groundtruth-kb/tests/test_bridge_poller_spike_runner.py:332-375` exercises valid live mode with an injected runner and verifies all 8 planned command invocations are reached with `cwd` and `timeout`.
- `groundtruth-kb/tests/test_bridge_poller_spike_runner.py:378-426` monkeypatches `subprocess.run` to fail and verifies the injected runner is the only path used in tests.
- `groundtruth-kb/tests/test_bridge_poller_spike_runner.py:429-474` verifies marker-delta live evidence through `SPIKE_EVIDENCE_DIR` and confirms the report is tagged `**LIVE**`.
- `groundtruth-kb/tests/test_bridge_poller_spike_runner.py:477-491` verifies mocked reports are tagged `**MOCKED**` and carry the P3-evidence warning.
- `groundtruth-kb/tests/test_bridge_poller_spike_runner.py:494-527` verifies missing real CLI binaries are recorded as `exit_code: 127`.

The test named `test_run_live_calls_real_adapter_not_mocked_synthesis` does not directly assert the internal `test_id`, despite its docstring, but it still proves the acceptance target: the mocked path cannot call the injected runner, while the live path does call that runner for all 8 command combinations.

## Regression Checks

The prior non-blockers from `-006` remain intact:

- Disposable workspace remains in-root under `<project_root>/.gtkb-state/bridge-poller/spikes/<run_id>/disposable-repo/`.
- `GTKB_SPIKE_WORKSPACE` out-of-root override remains fail-closed.
- Live mode still requires `--owner-approval-file`.
- Approval validation still covers required fields, token-cost floor, optional run-id binding, and in-root approval path.
- Mocked default remains CI-safe and does not invoke real `claude` or `codex` commands.
- Classification still distinguishes `WRITE_CAPABLE`, `REVIEW_ONLY`, and `OUT_OF_SCOPE`.

## Verification Commands

Executed from `E:\GT-KB\groundtruth-kb`:

```text
python -m pytest -q tests/test_bridge_poller_spike_runner.py --tb=short
```

Result:

```text
19 passed, 1 warning
```

```text
python -m pytest -q tests/test_bridge_paths.py tests/test_bridge_detector.py tests/test_bridge_checkpoint.py tests/test_bridge_routing.py tests/test_bridge_audit.py tests/test_bridge_registry.py tests/test_bridge_codex_hook_sample_status.py tests/test_bridge_poller_spike_runner.py tests/test_bridge_import_hygiene.py --tb=short
```

Result:

```text
110 passed, 1 warning
```

```text
python -m ruff check scripts/bridge_poller_verification_spike.py tests/test_bridge_poller_spike_runner.py
```

Result:

```text
All checks passed!
```

```text
python -m ruff format --check scripts/bridge_poller_verification_spike.py tests/test_bridge_poller_spike_runner.py
```

Result:

```text
2 files already formatted
```

## Risk / Impact

Residual risk is now operational rather than implementation-gate risk: the actual live spike still depends on real local `claude` and `codex` behavior, valid owner approval evidence, and the live run's captured output. The machinery no longer defers the live subprocess implementation to a later unreviewed change.

## Recommended Action

Proceed to the approved live spike run only after creating the required in-root owner approval file. File the resulting live `spike-report.md` as a new bridge thread for Loyal Opposition review before using it for P3 invoker scoping.

## Decision Needed From Owner

None for this implementation verification.
