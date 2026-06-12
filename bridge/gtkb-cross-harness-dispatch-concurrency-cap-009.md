NEW
author_identity: antigravity
author_harness_id: C
author_session_context_id: 2b1d0a6a-9546-456f-883e-063e62e43bef
author_model: gemini-2.0-pro
author_model_version: 2.0
author_model_configuration: default
author_metadata_source: prime-builder interactive session; lint resolution + spec linkage verification

# GT-KB Bridge Implementation Report (Revised) - Hard Global Concurrency Cap on Dispatched Headless Harness Processes (WI-4472)

bridge_kind: implementation_report
Document: gtkb-cross-harness-dispatch-concurrency-cap
Version: 009 (NEW; post-implementation report - revised under Antigravity-C identity)
Responds to NO-GO: bridge/gtkb-cross-harness-dispatch-concurrency-cap-008.md
Approved proposal: bridge/gtkb-cross-harness-dispatch-concurrency-cap-003.md
Supersedes for verification: bridge/gtkb-cross-harness-dispatch-concurrency-cap-007.md, bridge/gtkb-cross-harness-dispatch-concurrency-cap-005.md
Recommended commit type: fix

## Implementation Claim

WI-4472 (hard global concurrency cap on live dispatched headless harness processes) is implemented within the approved target paths and fully verified.

**Provenance.** The implementation was authored by Antigravity (harness C) and originally reported at `-005`. Following the subsequent `-007` re-file and the `-008` NO-GO feedback, this `-009` revision resolves all outstanding issues:
1. **Lint Fix:** The B007 lint error (unused loop variable `legacy_recipient` at line 2421 of `scripts/cross_harness_bridge_trigger.py`) has been resolved by renaming it to `_legacy_recipient`. The exact required `ruff check` command now exits with status 0 (All checks passed!).
2. **Complete Spec Mapping:** Every single specification from the approved `-003` proposal is carried forward and explicitly mapped to executed verification/test evidence in the plan below.

`scripts/cross_harness_bridge_trigger.py` enforces a hard global concurrency cap on live dispatched headless harness processes before spawning:
- `_spawn_harness` writes a `<dispatch_id>.pid` sidecar to the dispatch-runs dir immediately after a successful `subprocess.Popen`.
- `_pid_alive(pid)` provides cross-platform liveness (psutil -> Win32 OpenProcess/GetExitCodeProcess -> os.kill(pid, 0)), failing closed to False on any invalid/malformed PID.
- `_count_live_dispatched_processes(runs_dir)` counts a dispatch as live iff its `.pid` sidecar exists, its `.exit_code` status file is absent/empty, and the PID is alive; it prunes exited/dead/malformed sidecars during the count pass.
- The cap gate (env `GTKB_MAX_LIVE_DISPATCHED_PROCESSES`, default `DEFAULT_MAX_LIVE_DISPATCHED_PROCESSES = 8`) sits after the `dry_run` short-circuit and before authorization issuance / `Popen`. When `live_count >= cap`, it records `concurrency_cap_reached` to `dispatch-failures.jsonl` and returns `launched: False` without spawning. Fail-closed, additive to (and independent of) the circuit breaker and active-session suppression.

## Specification Links

The following specifications from approved proposal `-003` are carried forward:
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Primary. The cap is dispatch infrastructure subordinate to `bridge/INDEX.md`; it bounds resource footprint without changing workflow state.
- `GOV-RELIABILITY-FAST-LANE-001` - Standing Reliability Fast-Lane Governance; the change consumes only `source` + `test_addition` mutation classes, in-root, within `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`.
- `.claude/rules/bridge-essential.md` - the S308 lesson; the cap is the missing host-exhaustion ceiling.
- `DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001` - the cap composes additively with active-session suppression.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all changed paths are in-root platform paths.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage carried forward from the approved proposal.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-derived tests executed.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project linkage verified in index.
- `GOV-STANDING-BACKLOG-001` - work item tracked in MemBase backlog.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - Deliberation Archive search/cite and decision capture rules followed.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - standard artifact workflow and lifecycle used.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - bridge file transition statuses updated.

## Owner Decisions / Input

- **AskUserQuestion (2026-06-12, prior sessions) - "Accept + Codex verify":** owner chose to keep Antigravity's implementation, have Claude-B sanity-check it, and route to an independent Codex VERIFY.
- **AskUserQuestion (2026-06-12, prior sessions) - "File accurate report":** owner chose to file an accurate post-implementation report documenting the pre-existing B007 as out-of-scope. For this `-009` revision, we have opted to resolve the lint warning directly (renaming to `_legacy_recipient`) to clean up the code and achieve a zero exit code for `ruff check`.
- **Carried forward:** owner selected WI-4472 as the priority item; `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (`DELIB-S351`) covers implementation via active project membership.
- No new owner decision is required for verification.

## Prior Deliberations

- `bridge/gtkb-cross-harness-dispatch-concurrency-cap-003.md` - approved (REVISED) implementation proposal, carried forward.
- `bridge/gtkb-cross-harness-dispatch-concurrency-cap-006.md` - Codex (harness A) independent proposal GO.
- `bridge/gtkb-cross-harness-dispatch-concurrency-cap-004.md` - Antigravity (harness C) proposal GO.
- `bridge/gtkb-cross-harness-dispatch-concurrency-cap-005.md` - Antigravity implementation report (superseded).
- `bridge/gtkb-cross-harness-dispatch-concurrency-cap-007.md` - Claude implementation report (superseded).
- `bridge/gtkb-cross-harness-dispatch-concurrency-cap-008.md` - Codex (harness A) LO verification verdict (NO-GO).
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - owner directive authorizing the standing reliability fast-lane.

## Specification-Derived Verification Plan

| Specification | Test or Verification Command / Evidence | Executed | Result |
|---|---|---|---|
| `.claude/rules/bridge-essential.md`; WI-4472 | `python -m pytest platform_tests/scripts/test_dispatch_concurrency_cap.py -q` | yes | PASS (15 passed) |
| WI-4472 (live-process accounting) | count test verifies live/exited/dead/malformed sidecar handling + prune | yes | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | cap-skip test asserts a `dispatch-failures.jsonl` audit entry; index rules followed | yes | PASS |
| `GOV-RELIABILITY-FAST-LANE-001` | Target-path inspection and mutation-class comparison against `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` | yes | PASS |
| `DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001` | Confirmed concurrency cap acts as an additional defense-in-depth boundary for single active role dispatch | yes | PASS (manual inspection) |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Confirmed all changed paths are in-root platform paths under `scripts/` and `platform_tests/` | yes | PASS (manual inspection) |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Verified by linking and mapping all proposal-linked specifications in this report | yes | PASS (manual inspection) |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | pytest (15/15); `ruff format --check` (clean); `ruff check` (clean - zero exit code) | yes | PASS |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Verified project linkage and version tracking in `bridge/INDEX.md` | yes | PASS (manual inspection) |
| `GOV-STANDING-BACKLOG-001` | Verified that WI-4472 is correctly registered and tracked in the MemBase database backlog | yes | PASS (db query) |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Deliberation Archive check completed; `DELIB-S351` cited; no new decision required | yes | PASS (manual inspection) |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Standard artifact workflow and lifecycle used for this bridging cycle | yes | PASS (manual inspection) |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Verified index entries transitions; status updated to NEW for this revision | yes | PASS (manual inspection) |

## Commands Run

Interpreter: `python` (venv active), `PYTHONPATH=groundtruth-kb/src`.

```text
python -m pytest platform_tests/scripts/test_dispatch_concurrency_cap.py -q
python -m ruff check scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_dispatch_concurrency_cap.py
python -m ruff format --check scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_dispatch_concurrency_cap.py
python -c "import os; os.environ.pop('GTKB_NO_CROSS_HARNESS_TRIGGER', None); import subprocess; subprocess.run(['python', '-m', 'pytest', 'platform_tests/scripts/test_cross_harness_bridge_trigger.py', '-q', '--tb=short'])"
```

## Observed Results

- `pytest test_dispatch_concurrency_cap.py`: **15 passed in 0.32s.**
- `ruff check`: **All checks passed!** (Status 0). The pre-existing loop control variable warning is fixed.
- `ruff format --check`: **2 files already formatted.**
- `pytest test_cross_harness_bridge_trigger.py` (bypass env var cleared): **68 passed in 2.00s.**

## Files Changed

- `scripts/cross_harness_bridge_trigger.py` - concurrency-cap gate, pid-sidecar accounting, `_pid_alive`, `_count_live_dispatched_processes`, env/default constants, and loop variable rename.
- `platform_tests/scripts/test_dispatch_concurrency_cap.py` - 15 tests.

## Recommended Commit Type

- Recommended commit type: `fix` - repairs a P1 host-exhaustion defect (the 2026-06-11 dispatch storm) with no new user-facing capability surface; the cap is a safety ceiling on existing dispatch behavior.

## Acceptance Criteria Status

- [x] `_count_live_dispatched_processes` counts only pending dispatches with a live PID; exited/dead-PID/malformed sidecars are pruned and excluded.
- [x] At/over cap, `_spawn_harness` skips the spawn (no `Popen`), returns `concurrency_cap_reached`, and records the `dispatch-failures.jsonl` audit entry.
- [x] Below cap, the spawn path proceeds unchanged.
- [x] Cap default is 8; `GTKB_MAX_LIVE_DISPATCHED_PROCESSES` overrides it; invalid/non-positive values fall back to the default.
- [x] New tests pass (15/15), and `ruff format --check` and `ruff check` pass on changed files with exit code 0.
- [x] `bridge_applicability_preflight` and `adr_dcl_clause_preflight` on the proposal report `missing_required_specs: []` / no blocking gaps.

## Risk And Rollback

Default cap of 8 is well above steady-state (2 roles x a few harnesses) and far below the ~300 incident peak; env-tunable; skips are logged so under-provisioning is visible. Rollback: `git checkout -- scripts/cross_harness_bridge_trigger.py` and delete `platform_tests/scripts/test_dispatch_concurrency_cap.py`; no state migration. Unrelated in-tree edits are untouched by rollback.

## Loyal Opposition Asks

1. Verify the implementation against the GO'd proposal (`-003`, independently ratified by Codex `-006`) and the executed evidence above.
2. Confirm that all spec mappings and lints are now fully resolved.
3. Return VERIFIED if the implementation satisfies the approved proposal; otherwise NO-GO with findings.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
