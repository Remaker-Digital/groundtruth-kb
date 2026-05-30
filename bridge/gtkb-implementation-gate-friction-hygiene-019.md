REVISED

# Prime Builder Revised Implementation Report - Implementation Gate Friction Hygiene

bridge_kind: implementation_report
Document: gtkb-implementation-gate-friction-hygiene
Version: 019
Author: Codex Prime Builder (harness A)
Date: 2026-05-19 UTC
Reviewed NO-GO: bridge/gtkb-implementation-gate-friction-hygiene-018.md

## Claim

This revision addresses the -018 finding by adding the missing IP-D regression
coverage needed to substantiate the approved 32-test matrix from
bridge/gtkb-implementation-gate-friction-hygiene-005.md.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - this REVISED report is filed in bridge/INDEX.md.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - all changed files are under E:\GT-KB.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - this report maps the added tests to IP-D.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - post-GO NO-GO corrective work remains authorized by the pinned GO chain.
- GOV-STANDING-BACKLOG-001 - WI-3310 v2 evidence from -017 remains carried forward.

## Implementation Evidence

Changed files:

- platform_tests/scripts/test_implementation_start_gate.py
- platform_tests/scripts/test_implementation_authorization.py

Added coverage:

- F1/null-sink and redirect cases: file-descriptor duplication allow cases and mixed real-file plus null-sink block case.
- F2/F3 sqlite cases: EXPLAIN read allow case; writable_schema PRAGMA block; variable-sourced execute block; executemany block; executescript block.
- IP-C chain cases: unchanged latest GO allow; post-GO revised-report awaiting-review deny; NO-GO after revised report allow; missing pinned GO file deny.

WI-3310 related_bridge_threads evidence from -017 remains unchanged and carried forward.

## Spec-to-Test Mapping

| Spec / Approved IP-D item | Added or Executed Test Evidence |
|---|---|
| F1 null-sink ALLOW/BLOCK matrix | `test_gate_allows_fd_dup_to_stderr`, `test_gate_allows_stdout_fd_dup_to_stderr`, `test_gate_allows_stderr_fd_dup_to_stdout`, `test_gate_blocks_real_file_redirect_plus_null_sink_redirect` |
| F3 sqlite safe-read/write-disqualifier matrix | `test_gate_allows_python_sqlite_explain_read`, `test_gate_blocks_python_sqlite_writable_schema_assignment`, `test_gate_blocks_python_sqlite_variable_sourced_execute`, `test_gate_blocks_python_sqlite_executemany`, `test_gate_blocks_python_sqlite_executescript` |
| IP-C chain-walk matrix | `test_validate_packet_succeeds_with_unchanged_latest_go`, `test_validate_packet_fails_with_revised_report_awaiting_review`, `test_validate_packet_succeeds_with_no_go_after_revised_report`, `test_validate_packet_fails_when_go_file_not_in_chain` |

## Commands Executed

- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_implementation_start_gate.py -q --tb=short --basetemp=.pytest-basetemp-bridge -k "fd_dup or real_file_redirect_plus_null_sink_redirect or sqlite_explain_read or sqlite_writable_schema_assignment or sqlite_variable_sourced_execute or sqlite_executemany or sqlite_executescript"` -> 9 passed.
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_implementation_authorization.py -q --tb=short --basetemp=.pytest-basetemp-auth -k "unchanged_latest_go or revised_report_awaiting_review or no_go_after_revised_report or go_file_not_in_chain"` -> 6 passed.
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb\src\groundtruth_kb\db.py groundtruth-kb\tests\test_db.py platform_tests\scripts\test_implementation_start_gate.py platform_tests\scripts\test_implementation_authorization.py` -> All checks passed.
- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-implementation-gate-friction-hygiene` -> preflight_passed true; missing_required_specs []; missing_advisory_specs [].
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-implementation-gate-friction-hygiene` -> exit 0; zero blocking gaps.

Residual full-suite note:

- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_implementation_start_gate.py platform_tests\scripts\test_implementation_authorization.py -q --tb=short --basetemp=.pytest-basetemp-bridge-full` -> 151 passed, 3 failed. The failures are pre-existing/stale expectation failures in `test_go_authorization_packet_allows_in_scope_apply_patch`, `test_non_go_bridge_entry_cannot_create_authorization`, and `test_start_gate_enforces_canonical_edit_from_worktree`; they are not introduced by the added IP-D cases, but they prevent claiming a fully green two-file suite.

## Acceptance Status

- -018 F1 missing-test-count finding: addressed for the added missing IP-D cases.
- Full two-file pytest target: not fully green because of the three residual failures above.

## Recommended Commit Type

test: - adds missing regression tests and reporting evidence for an already-implemented gate behavior slice.

