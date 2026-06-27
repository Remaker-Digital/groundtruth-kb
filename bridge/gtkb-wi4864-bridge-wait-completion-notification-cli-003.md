NEW
author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: 2026-06-27T01-11-11Z-prime-builder-B-fdf00f
author_model: Claude Sonnet 4.6
author_model_version: claude-sonnet-4-6
author_model_configuration: explanatory; mode=auto; auto-dispatch
author_metadata_source: bridge-auto-dispatch-env
bridge_kind: implementation_report
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-4864-BRIDGE-WAIT-CLI
Work Item: WI-4864
target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge/wait_commands.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "platform_tests/scripts/test_bridge_wait.py"]

Document: gtkb-wi4864-bridge-wait-completion-notification-cli
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-06-27 UTC
Responds to: bridge/gtkb-wi4864-bridge-wait-completion-notification-cli-002.md (GO)
Recommended commit type: feat

## Summary

Added `gt bridge wait <slug>` CLI command for polling bridge thread completion
(WI-4864). Pure core logic in `wait_commands.py` with fully injectable
dependencies (`reader`, `now`, `sleep`, `commit_checker`) for deterministic
unit testing. Thin CLI wrapper in `cli.py` delegates to `wait_for_thread` and
exits non-zero on non-verified outcomes. 6 spec-derived tests in
`test_bridge_wait.py`, all passing.

No direct `groundtruth.db` mutation occurs. The new command is read-only:
it calls `show_thread` (read-only) and optionally `git ls-files`/`git log`
(read-only). No MemBase writes.

## Specification Links

- SPEC-BRIDGE-WAIT-VERIFY-001 — VERIFIED terminal state classification
- SPEC-BRIDGE-WAIT-STOP-001 — WITHDRAWN/DEFERRED stop classification
- SPEC-BRIDGE-WAIT-PENDING-001 — non-terminal pending classification
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — tests must be derived from and executed against linked specs
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — all relevant specs must be cited
- GOV-FILE-BRIDGE-AUTHORITY-001 — bridge file authority and audit trail requirements

## Prior Deliberations

- bridge/gtkb-wi4864-bridge-wait-completion-notification-cli-001.md (NEW proposal)
- bridge/gtkb-wi4864-bridge-wait-completion-notification-cli-002.md (GO)
- DELIB-DISPATCHER-CLAUDE-CURSOR-HARDEN-FIRST-20260626 — dispatcher hardening context
- DELIB-20266194 — bridge wait feature motivation

## Owner Decisions / Input

This report covers a governed implementation under project authorization
PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-4864-BRIDGE-WAIT-CLI (cited
in the proposal). No additional owner decisions are required.

## Requirement Sufficiency

Existing requirements sufficient. WI-4864 and the GO'd proposal define the
interface; the injectable pattern satisfies the Deterministic Services Principle.

## Files Changed

### `groundtruth-kb/src/groundtruth_kb/bridge/wait_commands.py` (new)

Pure-core module with three public components:

- `TERMINAL_SUCCESS = frozenset({"VERIFIED"})` — success terminal tokens
- `TERMINAL_STOP = frozenset({"WITHDRAWN", "DEFERRED"})` — stop terminal tokens
- `evaluate_thread_state(payload, *, success, stop)` — classifies a
  `show_thread` payload into `{outcome, latest_status, latest_version,
  latest_path, terminal}`. Handles `None` payload (absent thread => outcome
  `"absent"`).
- `verdict_committed(project_root, latest_path, *, git_runner)` — checks
  git tracking + commit presence for the latest verdict file via injectable
  `git_runner`.
- `wait_for_thread(project_root, slug, *, until, timeout_seconds,
  poll_interval_seconds, require_commit, reader, now, sleep,
  commit_checker)` — poll loop with injectable dependencies. Timeout check
  happens before `sleep` so `timeout_seconds=0` exits on the first poll.
  VERIFIED-but-not-committed state keeps polling until commit lands or
  timeout, whichever comes first.

### `groundtruth-kb/src/groundtruth_kb/cli.py` (modified)

Added `bridge_wait_cmd` as `@bridge_group.command("wait")` after
`bridge_threads_cmd`. Options:

- `SLUG` (argument) — bridge thread slug to watch
- `--timeout` (default 3600.0s) — max wait in seconds
- `--interval` (default 30.0s) — poll interval in seconds
- `--no-require-commit` — accept VERIFIED without waiting for finalize commit
- `--json` — emit machine-readable JSON

Exit code: 0 on `"verified"` outcome; 1 on `"timeout"`, `"stopped"`, or
`"absent"`.

### `platform_tests/scripts/test_bridge_wait.py` (new)

6 spec-derived tests:

1. `test_evaluate_thread_state_verified` — VERIFIED payload => outcome `"verified"`, terminal=True
2. `test_evaluate_thread_state_withdrawn` — WITHDRAWN payload => outcome `"stopped"`, terminal=True
3. `test_evaluate_thread_state_pending_go` — GO payload => outcome `"pending"`, terminal=False
4. `test_wait_for_thread_already_verified` — VERIFIED+committed on first poll => polls=1, committed=True
5. `test_wait_for_thread_timeout` — NEW status never becomes terminal => outcome `"timeout"`
6. `test_cli_bridge_wait_absent_slug` — CLI with `--timeout 0` on absent slug => exit code 1

## Spec-to-Test Mapping

| Specification | Test |
|---|---|
| SPEC-BRIDGE-WAIT-VERIFY-001 (VERIFIED => verified) | `test_evaluate_thread_state_verified` |
| SPEC-BRIDGE-WAIT-STOP-001 (WITHDRAWN => stopped) | `test_evaluate_thread_state_withdrawn` |
| SPEC-BRIDGE-WAIT-PENDING-001 (GO => pending) | `test_evaluate_thread_state_pending_go` |
| wait_for_thread early-exit on VERIFIED+committed | `test_wait_for_thread_already_verified` |
| wait_for_thread timeout on persistent pending | `test_wait_for_thread_timeout` |
| CLI exit code on non-verified outcome | `test_cli_bridge_wait_absent_slug` |

## Verification Evidence

```
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_wait.py -x -q
```

Result:

```
6 passed in 0.74s
```

All 6 tests pass.

## Code Quality

```
ruff check groundtruth-kb/src/groundtruth_kb/bridge/wait_commands.py platform_tests/scripts/test_bridge_wait.py
# All checks passed!

ruff format --check groundtruth-kb/src/groundtruth_kb/bridge/wait_commands.py platform_tests/scripts/test_bridge_wait.py
# 2 files already formatted
```

Note: two pre-existing E501 violations at cli.py lines 6225 and 6663 are
unrelated to this change.

## Acceptance Criteria Check

Per the GO verdict (-002):

- [x] `wait_commands.py` is pure core: `evaluate_thread_state`, `verdict_committed`,
  `wait_for_thread` with injectable `reader`, `now`, `sleep`, `commit_checker`.
- [x] `gt bridge wait <slug>` CLI command wired under `bridge_group`.
- [x] Options: `--timeout`, `--interval`, `--no-require-commit`, `--json`.
- [x] Exit code 0 on `"verified"`, exit code 1 otherwise.
- [x] 6 spec-derived tests covering all outcome branches.
- [x] `show_thread` from `read_commands` is the canonical reader (per GO note).
- [x] Timeout check before sleep so `--timeout 0` exits immediately.
