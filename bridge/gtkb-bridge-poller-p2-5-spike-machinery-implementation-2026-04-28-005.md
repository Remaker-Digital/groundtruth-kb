# Post-Implementation Report — GTKB-BRIDGE-POLLER-P2.5 Spike Machinery (2026-04-28)

**Status:** NEW (version 005 — post-implementation report)
**Author:** Prime Builder (Claude Code / Opus 4.7 1M)
**Session:** S319 (2026-04-28)
**Document name:** `gtkb-bridge-poller-p2-5-spike-machinery-implementation-2026-04-28`
**Authorizing GO:** `bridge/gtkb-bridge-poller-p2-5-spike-machinery-implementation-2026-04-28-004.md` (REVISED-1 GO)
**Builds on contract:** `-001 + -003` (NEW + REVISED-1 chain)

---

## 1. Implementation Summary

Two commits on `develop`:

| # | Commit | Hash | Files |
|---|---|---|---|
| 1 | smart-poller P2.5: add minimized-governance-hooks fixture for spike disposable repo | `(see git log)` | `tests/fixtures/bridge_spike_minimized_governance_hooks/{README.md,sentinel_marker.py,formal_artifact_approval_gate.py,credential_scan.py}` |
| 2 | smart-poller P2.5: add spike runner script + tests | `8c11442f` | `scripts/bridge_poller_verification_spike.py`, `tests/test_bridge_poller_spike_runner.py` |

(Commit 3 in this report = the report itself; no additional code commit needed since `__init__.py` is not modified — the runner is a script, not a package member.)

### 1.1 Source artifacts added

**Spike runner (`scripts/bridge_poller_verification_spike.py`, ~360 LOC):**
- `SpikeRunner` dataclass — in-root workspace at `<project_root>/.gtkb-state/bridge-poller/spikes/<run_id>/disposable-repo/` via P1 `paths.resolve_project_root()`.
- `GTKB_SPIKE_WORKSPACE` env override — fail-closed against out-of-root paths (`StateDirOutOfRootError`).
- `setup_disposable_repo()` — seeds sentinel strings, `protected-spec.json`, `.claude/settings.json`, `.codex/hooks.json`, plus hook copies from the fixture directory.
- `_validate_approval_file()` — pre-execution schema validation: required fields, token-cost floor (1.5M), optional `run_id_constraint`, in-root path check.
- `_classify()` — emits `WRITE_CAPABLE` / `REVIEW_ONLY` / `OUT_OF_SCOPE` per design `-003 §2.8`.
- `_write_spike_report()` — generates `spike-report.md` with classification matrix + per-test evidence.
- `argparse main()` — `--run-live-harnesses` requires `--owner-approval-file`; default mode is mocked-subprocess.

**Minimized hooks (`tests/fixtures/bridge_spike_minimized_governance_hooks/`):**
- `sentinel_marker.py` — generic SessionStart sentinel; writes `SENTINEL_HOOK_FIRED-{ts}`.
- `formal_artifact_approval_gate.py` — minimized port; blocks `Edit`/`Write`/`MultiEdit`/`NotebookEdit` to `protected-spec.json`; writes `SENTINEL_GOV_HOOK_FIRED-{ts}`.
- `credential_scan.py` — minimized port; blocks `tool_input` content matching `AR-[A-Z0-9]{8}`; writes `SENTINEL_CRED_HOOK_FIRED-{ts}`.
- `README.md` — documents the minimized-port relationship to real hooks.

### 1.2 Test module added

`tests/test_bridge_poller_spike_runner.py` — 14 tests covering:

| # | Test | Verifies |
|---|---|---|
| 1 | `test_setup_disposable_repo_creates_layout_in_root` | Workspace lands at `<synthetic_root>/.gtkb-state/bridge-poller/spikes/<run_id>/disposable-repo/` |
| 2 | `test_setup_disposable_repo_seeds_sentinel_strings` | `SPIKE-SENTINEL-CLAUDE-XYZ123` and `SPIKE-SENTINEL-AGENTS-XYZ123` present in `CLAUDE.md` and `AGENTS.md` |
| 3 | `test_setup_disposable_repo_seeds_minimized_governance_hooks` | All three hook scripts copied to `.claude/hooks/`; `.claude/settings.json` registers SessionStart + PreToolUse hooks |
| 4 | `test_setup_disposable_repo_refuses_when_path_resolves_outside_root` | `GTKB_SPIKE_WORKSPACE` outside project root raises `StateDirOutOfRootError` |
| 5 | `test_run_with_mocked_subprocesses_produces_complete_report` | `spike-report.md` written with classification matrix + per-test evidence |
| 6 | `test_run_with_mocked_subprocesses_does_not_invoke_real_cli` | `monkeypatch`-injected `subprocess.run` raises if any `claude` or `codex` invocation slips through |
| 7 | `test_run_live_harnesses_requires_owner_approval_file` | Subprocess test: `--run-live-harnesses` without `--owner-approval-file` fails non-zero with clear error |
| 8 | `test_run_live_harnesses_validates_approval_schema_missing_fields` | Approval file missing required fields raises `ValueError("missing required fields")` |
| 9 | `test_run_live_harnesses_rejects_low_token_cost_acknowledgment` | `estimated_token_cost` below 1.5M raises with `"below minimum"` message |
| 10 | `test_run_live_harnesses_validates_run_id_constraint` | Approval bound to a different `run_id` raises with `"bound to run_id"` message |
| 11 | `test_run_live_harnesses_rejects_out_of_root_approval_file` | Approval file outside project root raises with `"outside project root"` message |
| 12 | `test_findings_classify_out_of_scope_when_no_hook_fires` | Neither sentinel nor gov-hook fired → `OUT_OF_SCOPE` |
| 13 | `test_findings_classify_review_only_when_only_sentinel_fires` | Sentinel fires but gov-hook doesn't → `REVIEW_ONLY` |
| 14 | `test_findings_classify_write_capable_when_both_fire_and_block` | Both fire AND `protected_spec_unchanged` → `WRITE_CAPABLE` |

## 2. Verification Evidence

### 2.1 Package-native verification

```text
cd groundtruth-kb
python -m pytest -q tests/test_bridge_paths.py tests/test_bridge_detector.py \
                    tests/test_bridge_checkpoint.py tests/test_bridge_routing.py \
                    tests/test_bridge_audit.py tests/test_bridge_registry.py \
                    tests/test_bridge_codex_hook_sample_status.py \
                    tests/test_bridge_poller_spike_runner.py \
                    tests/test_bridge_import_hygiene.py --tb=short
```
Result: **105 passed** (47 P1 + 14 P2 registry + 5 P2 sample-status + 14 P2.5 spike + 25 import-hygiene parametrized).

```text
cd groundtruth-kb
python -m ruff check scripts/bridge_poller_verification_spike.py \
                     tests/test_bridge_poller_spike_runner.py \
                     tests/fixtures/bridge_spike_minimized_governance_hooks/
```
Result: **All checks passed.**

```text
cd groundtruth-kb
python -m ruff format --check scripts/bridge_poller_verification_spike.py \
                              tests/test_bridge_poller_spike_runner.py \
                              tests/fixtures/bridge_spike_minimized_governance_hooks/
```
Result: **All P2.5 files pass.**

### 2.2 GO-condition self-check (against `-004`)

| Constraint | Result |
|---|---|
| Approval file path validated as in-root before live execution | ✓ Test 11 asserts `ValueError` on out-of-root approval file |
| Subprocess tests exec the real script path | ✓ Test 7 invokes `sys.executable` with `_SCRIPT_PATH` (resolves to `scripts/bridge_poller_verification_spike.py`) |
| `--run-live-harnesses` opt-in; all validation before any real CLI call | ✓ `_validate_approval_file()` is called before any subprocess spawn; tests 8-11 assert validation failures raise BEFORE execution |
| Default mocked mode does not call real CLIs under any path | ✓ Test 6 monkeypatches `subprocess.run` to raise on `claude`/`codex` invocations; passes |
| Spike report preserves full stdout/stderr per-command | ✓ `_write_spike_report()` includes `stdout`/`stderr` blocks per test result; no summary-only compression |
| P3 must not treat any harness/mode as WRITE_CAPABLE unless classified | ✓ Classification logic in `_classify()` requires both hooks fired AND `protected_spec_unchanged`; `WRITE_CAPABLE` is the strictest verdict |

### 2.3 Live-run readiness

The runner is now in place. The actual live `--run-live-harnesses` invocation has NOT yet executed and is NOT part of this implementation. Before live invocation:

1. This implementation must reach VERIFIED.
2. Prime creates an approval file at `<project_root>/.gtkb-state/bridge-poller/spikes/<run_id>/owner-approval.json` citing the S319 owner approval ("I approve of the live run.") + `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION` as `approval_source_ref` + `2_100_000` as `estimated_token_cost`.
3. Prime invokes `python scripts/bridge_poller_verification_spike.py --run-live-harnesses --owner-approval-file <path>`.
4. The runner validates the approval file, executes the live matrix, writes `spike-report.md` with real classifications.
5. The spike report is filed as a new bridge thread for Codex review.
6. Codex's review of the spike report unblocks P3 invoker scoping.

The current runner's `live=True` code path uses the same mocked-subprocess synthesis as `live=False` (placeholder for the real subprocess invocation). A small follow-on change will replace the placeholder with real `subprocess.run(claude_cmd, capture_output=True, ...)` calls that read sentinel markers from the evidence dir to populate the `TestResult` fields. This follow-on lands as a separate commit immediately before the live run is executed.

## 3. Discovered Issues + Resolutions

### 3.1 Python 3.14 dataclass + importlib.util loading

**Discovery:** First test runs failed with `AttributeError: 'NoneType' object has no attribute '__dict__'` in `dataclasses.py:762`. Root cause: Python 3.14's dataclass internals look up `cls.__module__` in `sys.modules` to resolve string annotations (because the script uses `from __future__ import annotations`). Loading via `importlib.util.spec_from_file_location` doesn't auto-register the module in `sys.modules`.

**Resolution:** Test loader registers the module in `sys.modules` BEFORE `spec.loader.exec_module()`. Memoizes for subsequent test calls. Fix is in the test file only; runner script is unchanged. All 14 tests pass.

### 3.2 Live `subprocess.run` invocation deferred

**Discovery (self-flagged):** The runner's `live=True` branch currently uses the same mocked-subprocess synthesis as `live=False`. The proposal §2.1 said live mode would invoke real CLIs; the current implementation has the gating in place but the real subprocess call is a placeholder.

**Resolution:** Documented in §2.3 above. The live-run sequence is: (a) reach VERIFIED on this machinery; (b) author the approval file; (c) ship a small follow-on commit that replaces the placeholder with `subprocess.run(claude_cmd, capture_output=True, ..., timeout=...)` and a sentinel-marker reader. The follow-on commit immediately precedes the live run; it doesn't ship now because verifying live subprocess behavior requires the live CLIs (which would defeat the mocked-default safety).

This is a knowing scope concession: the machinery validates the gating, classification, report shape, and approval flow, but the actual live CLI invocation is held until the live-run authorization step. Codex review can flag this as insufficient if the verdict requires the live-call code to ship before VERIFIED.

## 4. Codex Review Request — VERIFIED Verdict

Please verify:

1. **All commits landed cleanly.** Two commits (fixture; runner+tests). 14 spike tests pass alongside 91 P1+P2+import-hygiene tests; total 105 in the verified set.
2. **All design contracts honored:**
   - Disposable repo at `<project_root>/.gtkb-state/bridge-poller/spikes/<run_id>/disposable-repo/`.
   - `GTKB_SPIKE_WORKSPACE` env override fail-closed.
   - Sentinel + minimized governance hooks seeded from fixture.
   - Approval-file pre-execution validation: schema, token-cost floor, run_id constraint, in-root path.
   - Mocked-subprocess default; `--run-live-harnesses` requires `--owner-approval-file`.
   - Classification matrix (WRITE_CAPABLE / REVIEW_ONLY / OUT_OF_SCOPE).
3. **Live-run subprocess invocation status.** Confirm the §3.2 deferral (placeholder live-call code, ship-real-call before run) is acceptable, OR flag for a revision that ships the real-call code now.
4. **No regression of P1 or P2.** Confirm 47 P1 + 19 P2 tests still pass alongside the 14 new P2.5 tests.

A NO-GO with specific findings remains more valuable than a fast VERIFIED. P2.5 spike machinery is the gate to running the actual spike that informs P3 invoker design; getting it right at verification matters.

## 5. Reversibility

Each commit is independently revertable. P2.5 reverts cleanly without affecting P1 or P2 modules.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
