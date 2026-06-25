NEW

# gtkb-run-with-status-worker-lifetime-timeout — Post-Implementation Report (WI-4806)

bridge_kind: prime_proposal
Document: gtkb-run-with-status-worker-lifetime-timeout
Version: 003
Author: Prime Builder (harness B / claude)
Date: 2026-06-25 UTC
Responds to: bridge/gtkb-run-with-status-worker-lifetime-timeout-002.md (GO)

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 36bd90f3-6d5f-4f15-8a6f-28e45ada52f0
author_model: claude-opus-4-8
author_model_version: Opus 4.8
author_model_configuration: default

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4806

target_paths: ["scripts/run_with_status.py", "platform_tests/scripts/test_run_with_status.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary of Implementation

Implemented the GO'd (-002) worker-lifetime timeout in `scripts/run_with_status.py`:

- Added module constants `DEFAULT_WORKER_LIFETIME_TIMEOUT_SECONDS = 600` (10-minute generous Phase 0 baseline per the LO GO -002 recommendation), `TIMEOUT_EXIT_CODE = 124` (coreutils `timeout` convention), and `TERMINATE_GRACE_SECONDS = 10`. Fixed module-level default, **no new env/config knob** (fast-lane eligibility preserved; tests monkeypatch the constant; the Phase 2 daemon makes it configurable).
- Added `_terminate_process_tree(proc)`: on Windows runs `taskkill /F /T /PID <pid>` to walk and kill the whole tree; on POSIX kills the process group via `os.killpg` (the child is spawned with `start_new_session=True`); then reaps the root within the grace window.
- Replaced the bare `p.wait()` with `p.wait(timeout=DEFAULT_WORKER_LIFETIME_TIMEOUT_SECONDS)`. On `subprocess.TimeoutExpired`: tree-terminate, set the exit code to 124, and log the timeout to stderr (and to the redirected stderr file when one is configured). The existing `finally` writes 124 to the status file.
- Added `start_new_session=True` to the POSIX Popen path only (unset on Windows where `taskkill /T` handles the tree).

## Specification Links (carried forward)

- `GOV-RELIABILITY-FAST-LANE-001` — fast-lane defect fix under the standing PAUTH; eligibility preserved (fixed default, no new public/CLI/config surface).
- `GOV-FILE-BRIDGE-AUTHORITY-001` — reliability mandate; immortal workers that halt dispatch threaten the bridge.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping below.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `GOV-STANDING-BACKLOG-001`.

## Prior Deliberations

- `DELIB-20265882` — dispatcher target-architecture grill; this fix is the named Phase 0 keystone (mortal workers).
- `DELIB-20265877` — kill-switch emergency directive; this removes the corpse-accumulation cause behind that cascade.
- `DELIB-20264379` — adjacent Ollama dispatch-stall reliability review.

## Owner Decisions / Input

No per-fix owner approval required; authorized by the standing `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` per `GOV-RELIABILITY-FAST-LANE-001`. The Phase 0 sequencing was owner-directed and recorded in `DELIB-20265882`.

## Requirement Sufficiency

Existing requirements sufficient — the governing requirement is the reliability mandate (`GOV-FILE-BRIDGE-AUTHORITY-001` / bridge-essential.md: bridge integrity is top priority). This is a pure defect fix (an unbounded wait that leaked immortal processes); it introduced no new or revised requirement or specification.

## Spec-to-Test Mapping & Verification Evidence

| Linked spec / requirement | Test | Result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` (workers must not hang) + `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (distinguishable timeout outcome) | `test_worker_lifetime_timeout_records_124_and_terminates_tree` | PASS — on timeout the tree is terminated and the status file records 124 |
| LO GO -002 residual risk (Windows tree reaping) | `test_terminate_process_tree_reaps_grandchild_on_windows` | PASS — a child that spawns a grandchild has BOTH reaped |
| No regression | 3 existing creationflags / status-file tests | PASS |

Commands and observed results (repo venv interpreter):

```
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_run_with_status.py -q
  => 5 passed in 2.16s

ruff format --check scripts/run_with_status.py platform_tests/scripts/test_run_with_status.py
  => 2 files already formatted

ruff check scripts/run_with_status.py platform_tests/scripts/test_run_with_status.py
  => 2 findings (SIM115, UP015) at scripts/run_with_status.py line 92.
     PRE-EXISTING: identical findings appear on git HEAD at the original line 44
     (the unchanged stdin open), confirmed via `git show HEAD:scripts/run_with_status.py | ruff check -`.
     NOT introduced by this change; the added code is clean. Left untouched to keep
     scope to the GO'd worker-lifetime fix (SIM115 is a structural refactor of the
     file's manual handle management). The commit guardrail is ruff-format (clean).
```

## Acceptance Criteria Check

- Hung child terminated within timeout + grace — ✓
- Status file records the timeout sentinel (124) — ✓
- Child and grandchild both reaped (Windows tree-kill) — ✓
- Existing tests pass (no regression) — ✓
- Fast-lane eligibility preserved (no new config surface) — ✓

## Risk / Rollback

Single wrapper module plus its test. Single-commit rollback = revert the diff (returns to the bare `wait()`). The pre-existing ruff-check debt (SIM115/UP015) is intentionally left untouched to keep this change scoped to the GO'd fix; it is a candidate for a separate fast-lane cleanup.

## Recommended Commit Type

`fix` — repairs a reliability defect (an unbounded wait leaking immortal processes); adds regression tests but introduces no new capability surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
