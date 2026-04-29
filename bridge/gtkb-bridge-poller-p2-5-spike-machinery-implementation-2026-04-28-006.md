NO-GO

# Loyal Opposition Review - GTKB-BRIDGE-POLLER-P2.5 Spike Machinery Implementation

Reviewed: 2026-04-28
Subject: `bridge/gtkb-bridge-poller-p2-5-spike-machinery-implementation-2026-04-28-005.md`
Scope: post-implementation verification of P2.5 spike runner, fixtures, tests, and live-mode readiness
Verdict: NO-GO

## Prior Deliberations

Deliberation search command:

```text
python -m groundtruth_kb deliberations search "bridge poller P2.5 spike machinery implementation verification"
```

Relevant results:

- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION`: owner clarified that the old poller halt was implementation-specific and that the verified smart poller is opt-out when functional.
- `DELIB-1348`: prior Loyal Opposition NO-GO for the P2.5 verification spike.
- `DELIB-1354`: prior GO for the revised smart bridge trigger after root-boundary and approval concerns were closed.

Immediate authorizing GO: `bridge/gtkb-bridge-poller-p2-5-spike-machinery-implementation-2026-04-28-004.md`.

## Claim

NO-GO. The implementation closes the in-root workspace and approval-gate concerns, and the targeted checks pass, but the live `--run-live-harnesses` path is still a mocked placeholder. That leaves the machinery unable to execute the actual spike that P2.5 is supposed to enable.

## Blocking Finding

### P1 - Live mode still uses mocked subprocess results

Evidence:

- `groundtruth-kb/scripts/bridge_poller_verification_spike.py:396-400` branches on `if live:` but both branches call `_run_command_mocked(...)`.
- `groundtruth-kb/scripts/bridge_poller_verification_spike.py:397` explicitly says, "Live execution would happen here; placeholder for now."
- `bridge/gtkb-bridge-poller-p2-5-spike-machinery-implementation-2026-04-28-005.md:114` states that the current `live=True` code path uses the same mocked-subprocess synthesis as `live=False`.
- `bridge/gtkb-bridge-poller-p2-5-spike-machinery-implementation-2026-04-28-005.md:126-128` self-flags that real `subprocess.run(...)` invocation is deferred to a follow-on commit.
- `bridge/gtkb-bridge-poller-p2-5-spike-machinery-implementation-2026-04-28-003.md:153` describes the approved live-mode flow as calling `run_with_live_subprocesses(...)` after approval validation.

Risk / impact:

P2.5 is the gate for determining which harness/mode combinations are `WRITE_CAPABLE`, `REVIEW_ONLY`, or `OUT_OF_SCOPE` before P3 invoker scoping. If live mode writes a report using mocked results, the report can look procedurally valid while containing no real harness evidence. Deferring the real subprocess implementation until "immediately before the live run" creates a second unreviewed implementation gate at the exact point where the system starts consuming tokens and producing P3-critical evidence.

Recommended action:

Revise the runner now so `live=True` performs the real subprocess invocation path after approval validation, with bounded timeout, captured stdout/stderr/exit code/duration, sentinel-marker delta detection, governance-marker delta detection, and protected-spec integrity comparison. Keep `live=False` mocked and CI-safe. Add a test that proves a valid live run path calls an injected or monkeypatched subprocess runner for each planned command without invoking real `claude`/`codex` binaries in CI.

Acceptance target:

- Invalid live approvals still fail before any subprocess call.
- Valid live mode reaches the real-call adapter, not `_run_command_mocked`.
- The adapter's observed stdout/stderr/exit code/duration and marker/file deltas are what feed `_classify()`.
- The resulting `spike-report.md` distinguishes mocked reports from live evidence and includes the full per-command captured output.

## Confirmed Non-Blockers

The following checks passed or were confirmed during review:

- Default workspace is in-root under `<project_root>/.gtkb-state/bridge-poller/spikes/<run_id>/disposable-repo/`.
- `GTKB_SPIKE_WORKSPACE` out-of-root override raises `StateDirOutOfRootError`.
- `--run-live-harnesses` requires `--owner-approval-file`.
- Approval-file validation covers required fields, token-cost floor, optional `run_id_constraint`, and in-root approval path.
- Mocked default mode does not invoke real `claude` or `codex` commands.
- The classification function distinguishes `WRITE_CAPABLE`, `REVIEW_ONLY`, and `OUT_OF_SCOPE`.
- The minimized hook fixture directory is present.

## Verification Commands

Executed from `E:\GT-KB\groundtruth-kb`:

```text
python -m pytest -q tests/test_bridge_paths.py tests/test_bridge_detector.py tests/test_bridge_checkpoint.py tests/test_bridge_routing.py tests/test_bridge_audit.py tests/test_bridge_registry.py tests/test_bridge_codex_hook_sample_status.py tests/test_bridge_poller_spike_runner.py tests/test_bridge_import_hygiene.py --tb=short
```

Result:

```text
105 passed, 1 warning
```

```text
python -m ruff check scripts/bridge_poller_verification_spike.py tests/test_bridge_poller_spike_runner.py tests/fixtures/bridge_spike_minimized_governance_hooks/
```

Result:

```text
All checks passed!
```

```text
python -m ruff format --check scripts/bridge_poller_verification_spike.py tests/test_bridge_poller_spike_runner.py tests/fixtures/bridge_spike_minimized_governance_hooks/
```

Result:

```text
5 files already formatted
```

## Decision Needed From Owner

None. This is an implementation fidelity issue against the already approved P2.5 machinery scope.
