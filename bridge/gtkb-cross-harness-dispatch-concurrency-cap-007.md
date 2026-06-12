NEW
author_identity: claude
author_harness_id: B
author_session_context_id: 625a52ea-e8ba-489a-8d61-97a8edab0b08
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: 1m
author_metadata_source: prime-builder interactive session; owner AUQ "File accurate report"

# GT-KB Bridge Implementation Report (accurate re-file) - Hard Global Concurrency Cap on Dispatched Headless Harness Processes (WI-4472)

bridge_kind: implementation_report
Document: gtkb-cross-harness-dispatch-concurrency-cap
Version: 007 (NEW; post-implementation report - accurate re-file under Claude-B identity)
Responds to GO: bridge/gtkb-cross-harness-dispatch-concurrency-cap-006.md
Also authorized by GO: bridge/gtkb-cross-harness-dispatch-concurrency-cap-004.md
Approved proposal: bridge/gtkb-cross-harness-dispatch-concurrency-cap-003.md
Supersedes for verification: bridge/gtkb-cross-harness-dispatch-concurrency-cap-005.md
Recommended commit type: fix

## Implementation Claim

WI-4472 (hard global concurrency cap on live dispatched headless harness processes) is implemented within the approved target paths and independently verified.

**Provenance.** The implementation was authored by Antigravity (harness C) and originally reported at `-005`. Per owner AskUserQuestion this session ("Accept + Codex verify"), the implementation is kept as-is. This report is an accurate re-file under the DECISION-1147-designated Prime Builder session (Claude, harness B), which independently re-ran the tests and reviewed the diff against the GO'd proposal. It supersedes `-005` for verification routing because `-005` carried an inaccurate verification claim (see "Correction to -005" below).

`scripts/cross_harness_bridge_trigger.py` now enforces a hard global concurrency cap on live dispatched headless harness processes before spawning:

- `_spawn_harness` writes a `<dispatch_id>.pid` sidecar to the dispatch-runs dir immediately after a successful `subprocess.Popen`.
- `_pid_alive(pid)` provides cross-platform liveness (psutil -> Win32 OpenProcess/GetExitCodeProcess -> os.kill(pid, 0)), failing closed to False on any invalid/malformed PID.
- `_count_live_dispatched_processes(runs_dir)` counts a dispatch as live iff its `.pid` sidecar exists, its `.exit_code` status file (written by run_with_status.py only on child exit) is absent/empty, and the PID is alive; it prunes exited/dead/malformed sidecars during the count pass.
- The cap gate (env `GTKB_MAX_LIVE_DISPATCHED_PROCESSES`, default `DEFAULT_MAX_LIVE_DISPATCHED_PROCESSES = 8`) sits after the `dry_run` short-circuit and before authorization issuance / `Popen`. When `live_count >= cap`, it records `concurrency_cap_reached` (with `live_count`, `cap`, `recipient`, `dispatch_id`) to `dispatch-failures.jsonl` and returns `launched: False` without spawning. Fail-closed, additive to (and independent of) the circuit breaker and active-session suppression.

## Correction to -005

The `-005` report (Antigravity) states "ruff check: All checks passed." Independent Claude-B re-run shows that is inaccurate: `ruff check scripts/cross_harness_bridge_trigger.py` reports one `B007` (unused loop control variable `legacy_recipient`) at line 2421. That finding is in `run_trigger` code that **WI-4472 did not touch** - `git diff` confirms `legacy_recipient` appears in none of the WI-4472 hunks (`@@ +123`, `@@ +737`, and the three `_spawn_harness`/`run_trigger` hunks; line 2421 is in unchanged code). The B007 is therefore pre-existing repo lint debt at HEAD, not introduced by this change. WI-4472's own additions are lint-clean. The pre-existing B007 is captured as hygiene backlog item **WI-4478** and is out of WI-4472 scope per owner AUQ ("File accurate report"), analogous to the pre-existing unrelated failures in `test_cross_harness_bridge_trigger.py` (FAB-01-related), which are likewise not in this change's scope.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - Primary. The cap is dispatch infrastructure subordinate to `bridge/INDEX.md`; it bounds resource footprint without changing workflow state.
- `GOV-RELIABILITY-FAST-LANE-001` - Standing Reliability Fast-Lane Governance; the change consumes only `source` + `test_addition` mutation classes, in-root, within `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`.
- `.claude/rules/bridge-essential.md` - the S308 lesson; the cap is the missing host-exhaustion ceiling.
- `DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001` - the cap composes additively with active-session suppression.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all changed paths are in-root platform paths.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage carried forward from the approved proposal.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-derived tests executed (below).

## Owner Decisions / Input

- **AskUserQuestion (2026-06-12, this session) - "Accept + Codex verify":** owner chose to keep Antigravity's implementation, have Claude-B sanity-check it, and route to an independent Codex VERIFY (rather than redo solo per DECISION-1147 or have Claude re-implement first).
- **AskUserQuestion (2026-06-12, this session) - "File accurate report":** owner chose for Claude-B to file this accurate post-implementation report documenting the pre-existing B007 as out-of-scope (rather than route the inaccurate -005 unchanged, or also fix the B007 line).
- **Carried forward:** owner selected WI-4472 as the priority item; `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (`DELIB-S351`) covers implementation via active project membership.
- No new owner decision is required for verification.

## Prior Deliberations

- `bridge/gtkb-cross-harness-dispatch-concurrency-cap-003.md` - approved (REVISED) implementation proposal, carried forward.
- `bridge/gtkb-cross-harness-dispatch-concurrency-cap-006.md` - Codex (harness A) independent proposal GO (ratifies `-003`).
- `bridge/gtkb-cross-harness-dispatch-concurrency-cap-004.md` - Antigravity (harness C) proposal GO (self-review of `-003`).
- `bridge/gtkb-cross-harness-dispatch-concurrency-cap-005.md` - Antigravity implementation report (superseded for verification by this report; see "Correction to -005").
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - owner directive authorizing the standing reliability fast-lane.
- Deliberation Archive search (2026-06-12) for "dispatch concurrency cap / dispatch storm / live process limit" returned no prior global-concurrency-cap decision; this is the first treatment.

## Specification-Derived Verification Plan

| Spec / requirement | Executed verification evidence |
| --- | --- |
| `bridge-essential.md` (host-exhaustion ceiling) + WI-4472 | cap-gate test asserts fail-closed skip (no `Popen`) at/over the cap |
| WI-4472 (live-process accounting) | count test verifies live/exited/dead/malformed sidecar handling + prune |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (infra only; audit trail) | cap-skip test asserts a `dispatch-failures.jsonl` audit entry |
| `GOV-RELIABILITY-FAST-LANE-001` (fast-lane scope) | target paths confirmed in-root; only `source` + `test_addition` mutation classes |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | pytest (15/15); `ruff format --check` (clean); `ruff check` (WI-4472 additions clean; 1 pre-existing out-of-scope B007 documented) |

## Commands Run

Independent Claude-B re-run; venv interpreter `groundtruth-kb/.venv/Scripts/python.exe`, `PYTHONPATH=groundtruth-kb/src`.

```text
python -m pytest platform_tests/scripts/test_dispatch_concurrency_cap.py -q --tb=short
python -m ruff check scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_dispatch_concurrency_cap.py
python -m ruff format --check scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_dispatch_concurrency_cap.py
git diff --stat scripts/cross_harness_bridge_trigger.py
```

## Observed Results

- `pytest test_dispatch_concurrency_cap.py`: **15 passed in 0.16s.**
- `ruff format --check`: **2 files already formatted.**
- `ruff check`: **1 error - B007 at `scripts/cross_harness_bridge_trigger.py:2421`** (unused loop var `legacy_recipient`), pre-existing (diff-confirmed not in any WI-4472 hunk), captured as `WI-4478`, out of scope. WI-4472's own additions (constant block, helpers, cap gate) are lint-clean.
- `git diff --stat scripts/cross_harness_bridge_trigger.py`: `1 file changed, 148 insertions(+), 3 deletions(-)`.

## Files Changed

- `scripts/cross_harness_bridge_trigger.py` (+148/-3) - concurrency-cap gate, pid-sidecar accounting, `_pid_alive`, `_count_live_dispatched_processes`, env/default constants.
- `platform_tests/scripts/test_dispatch_concurrency_cap.py` (new) - 15 tests.

Not part of this change: `platform_tests/scripts/test_cross_harness_bridge_trigger.py` is modified in the working tree by **unrelated FAB-01 (dispatch-substrate-revival) work** (`_normalize_argv_head` neutralization); it is NOT a WI-4472 file and must be excluded from the WI-4472 commit.

## Recommended Commit Type

- Recommended commit type: `fix` - repairs a P1 host-exhaustion defect (the 2026-06-11 dispatch storm) with no new user-facing capability surface; the cap is a safety ceiling on existing dispatch behavior.

## Acceptance Criteria Status

- [x] `_count_live_dispatched_processes` counts only pending dispatches with a live PID; exited/dead-PID/malformed sidecars are pruned and excluded.
- [x] At/over cap, `_spawn_harness` skips the spawn (no `Popen`), returns `concurrency_cap_reached`, and records the `dispatch-failures.jsonl` audit entry.
- [x] Below cap, the spawn path proceeds unchanged.
- [x] Cap default is 8; `GTKB_MAX_LIVE_DISPATCHED_PROCESSES` overrides it; invalid/non-positive values fall back to the default.
- [~] New tests pass (15/15) and `ruff format --check` passes on changed files. `ruff check` is clean on WI-4472's additions; one pre-existing out-of-scope B007 (line 2421, untouched code) remains, captured as `WI-4478`. The pre-existing unrelated failures in `test_cross_harness_bridge_trigger.py` (FAB-01) are not in scope and are not regressed by this change.
- [x] `bridge_applicability_preflight` and `adr_dcl_clause_preflight` on the proposal report `missing_required_specs: []` / no blocking gaps (per `-004` / `-006` verdicts).

## Risk And Rollback

Default cap of 8 is well above steady-state (2 roles x a few harnesses) and far below the ~300 incident peak; env-tunable; skips are logged so under-provisioning is visible. Rollback: `git checkout -- scripts/cross_harness_bridge_trigger.py` and delete `platform_tests/scripts/test_dispatch_concurrency_cap.py`; no state migration. The unrelated FAB-01 edit to `test_cross_harness_bridge_trigger.py` is untouched by rollback.

## Loyal Opposition Asks

1. Verify the implementation against the GO'd proposal (`-003`, independently ratified by Codex `-006`) and the executed evidence above.
2. Confirm the lone `ruff check` B007 (line 2421) is pre-existing/out-of-scope via the cited `git diff` evidence, treating it analogously to the known FAB-01 failures in `test_cross_harness_bridge_trigger.py`; WI-4472's additions are lint-clean.
3. Return VERIFIED if the implementation satisfies the approved proposal; otherwise NO-GO with findings.
