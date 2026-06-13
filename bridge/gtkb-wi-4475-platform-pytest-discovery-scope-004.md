NEW

# Implementation Report - Platform Pytest Discovery Scope

bridge_kind: implementation_report
Document: gtkb-wi-4475-platform-pytest-discovery-scope
Version: 004
Author: Codex Prime Builder
Date: 2026-06-12 UTC
Responds-To: bridge/gtkb-wi-4475-platform-pytest-discovery-scope-003.md
Approved-Proposal: bridge/gtkb-wi-4475-platform-pytest-discovery-scope-002.md
Recommended commit type: fix:

author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019ebd61-0067-73d0-bc59-142681b70a9e
author_model: GPT-5 Codex coding agent
author_model_version: GPT-5 family; exact runtime build not exposed in session context
author_model_configuration: Codex desktop session; Prime Builder override; approval_policy=never
author_metadata_source: Codex Prime Builder explicit metadata for bridge filing; CODEX_THREAD_ID=019ebd61-0067-73d0-bc59-142681b70a9e

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4475

target_paths: ["pyproject.toml", "platform_tests/governance/test_platform_tests_rename.py"]

Implementation authorization packet:
`sha256:8a328c47f28c8bd8968b06af0d22ab69079b2ad4c7420bb8bc0553fb5adf8d23`

## Implementation Claim

Implemented the approved two-file reliability fix from the GO verdict:

- narrowed root `pyproject.toml` default `testpaths` from
  `["platform_tests", "applications/Agent_Red/tests"]` to `["platform_tests"]`;
- extended `platform_tests/governance/test_platform_tests_rename.py` so the
  platform-test rename invariant now rejects `applications/Agent_Red/tests` in
  default root pytest discovery.

This changes only the default no-argument pytest discovery scope. Agent Red
tests remain runnable through explicit application test paths and their CI lanes.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge/INDEX remains the canonical workflow
  state; this report is appended as the next live bridge version.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - implementation
  remains inside the proposal's cited requirements and target paths.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - report carries project,
  work item, PAUTH, and target-path metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification maps to the
  linked bridge, isolation, backlog, and reliability requirements.
- `GOV-STANDING-BACKLOG-001` - WI-4475 is the durable backlog item addressed.
- `GOV-RELIABILITY-FAST-LANE-001` - change is a small reliability fix under the
  standing fast-lane authorization.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - default GT-KB platform pytest
  discovery no longer crosses into the adopter application test tree.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - implementation started only
  after GO and a valid implementation authorization packet.

## Owner Decisions / Input

No new owner decision was required. The work is covered by
`DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` and
`PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`.

## Prior Deliberations

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - owner-approved standing
  reliability fast-lane.
- `DELIB-S377-SLICE7PRIME-PYTEST-CONTAMINATION-WAIVER` - historical pytest
  contamination context; this implementation removes one current contamination
  source instead of requesting a waiver.
- `bridge/gtkb-wi-4475-platform-pytest-discovery-scope-002.md` - approved
  proposal.
- `bridge/gtkb-wi-4475-platform-pytest-discovery-scope-003.md` - GO verdict.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `show_thread_bridge` before implementation showed latest `GO` with `drift: []`; this report will append the next `NEW` row. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Diff is limited to the proposal target paths: `pyproject.toml` and `platform_tests/governance/test_platform_tests_rename.py`. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Implementation authorization packet created for `gtkb-wi-4475-platform-pytest-discovery-scope`; packet hash recorded above. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Root collect-only and targeted regression test executed successfully; command evidence below. |
| `GOV-STANDING-BACKLOG-001` | Work maps to WI-4475 under `PROJECT-GTKB-RELIABILITY-FIXES`; no bulk backlog mutation was performed. |
| `GOV-RELIABILITY-FAST-LANE-001` | Small test-config reliability fix under standing PAUTH; no deploy, force push, or spec deletion. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Root collect-only now reports `testpaths: platform_tests` and collects 4150 platform tests without importing Agent Red conftest. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | `implementation_authorization.py begin --bridge-id gtkb-wi-4475-platform-pytest-discovery-scope` succeeded after GO and before file edits. |

## Commands Run

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest --collect-only -q
```

Result: PASS; rootdir `E:\GT-KB`, config `pyproject.toml`,
`testpaths: platform_tests`, collected 4150 tests in 2.98s.

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\governance\test_platform_tests_rename.py -q --tb=short
```

Result: PASS; 5 passed in 0.14s.

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff check platform_tests\governance\test_platform_tests_rename.py
```

Result: PASS; all checks passed.

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check platform_tests\governance\test_platform_tests_rename.py
```

Result: PASS after formatting; 1 file already formatted.

```text
git diff --check -- pyproject.toml platform_tests\governance\test_platform_tests_rename.py
```

Result: PASS exit 0; emitted only Git's Windows LF-to-CRLF working-copy warning
for `pyproject.toml`.

## Files Changed

- `pyproject.toml`
- `platform_tests/governance/test_platform_tests_rename.py`

## Diff Summary

```text
pyproject.toml
- testpaths = ["platform_tests", "applications/Agent_Red/tests"]
+ testpaths = ["platform_tests"]

platform_tests/governance/test_platform_tests_rename.py
+ assert "applications/Agent_Red/tests" not in testpaths
```

## Acceptance Criteria Status

- [x] Bare root pytest no longer discovers Agent Red tests in the GT-KB platform
  venv.
- [x] Regression assertion protects the root `testpaths` boundary.
- [x] Existing platform-test rename invariants still pass.
- [x] Ruff check and format pass for the changed Python test file.

## Risk And Rollback

Residual risk: users who intentionally want Agent Red tests from the repository
root must pass the application test path explicitly. This matches the existing
CI shape and avoids coupling the GT-KB platform venv to Agent Red dependencies.

Rollback: revert the two target-file changes from this report. Bridge artifacts
remain append-only.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and command
   evidence.
2. Return `VERIFIED` if the two-file implementation satisfies the approved
   proposal; otherwise return `NO-GO` with findings.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
