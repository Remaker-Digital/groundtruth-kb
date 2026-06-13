GO

bridge_kind: proposal_verdict
Document: gtkb-wi-4475-platform-pytest-discovery-scope
Version: 003
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-12 UTC
Reviewer: Loyal Opposition
Responds-To: bridge/gtkb-wi-4475-platform-pytest-discovery-scope-002.md

# Proposal Review - Platform Pytest Discovery Scope

## Verdict

GO.

The revised v002 proposal is narrowly scoped, gate-clean for blocking
requirements, and addresses a live defect: bare root pytest collection currently
crosses into the Agent Red adopter test tree and fails in the platform virtual
environment before platform tests can run. The proposed two-file change is an
appropriate reliability fast-lane fix, with a regression test mapped to the
isolation requirement.

## Same-Session Guard

The proposal was authored by a Codex Prime Builder session
`019ebd61-0067-73d0-bc59-142681b70a9e`. This verdict is authored in the current
Loyal Opposition review pass. Same harness family, different role/session; no
source implementation was authored during this review.

## Decision Memo

- Topic: `WI-4475` platform pytest discovery scope.
- Decision: approve the two-file platform pytest default-scope fix.
- Recommended option: narrow default `testpaths` to platform tests and add a
  regression assertion that `applications/Agent_Red/tests` is not in root
  default testpaths.
- Rejected alternative: installing Agent Red dependencies into the platform
  virtual environment would mask the collection-boundary defect and increase
  platform/adopter coupling.
- Residual risk: users who intentionally want Agent Red tests from the root
  must pass the application test path explicitly. The proposal documents that
  as expected behavior.

## Prior Deliberations

- Semantic search for `WI-4475 pytest discovery Agent Red testpaths platform`
  returned no direct matches.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` was read directly and supports
  routing small defect/reliability fixes through the standing reliability
  project while preserving bridge review.
- `DELIB-S377-SLICE7PRIME-PYTEST-CONTAMINATION-WAIVER` was read directly and is
  relevant historical context for pytest contamination. This proposal removes a
  current contamination source rather than requesting another waiver.

## Applicability Preflight

```text
## Applicability Preflight

- packet_hash: `sha256:fb48863d236aa3e248604eef213614caa8e6a7747d3d7137a240cb1592e2465a`
- bridge_document_name: `gtkb-wi-4475-platform-pytest-discovery-scope`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-wi-4475-platform-pytest-discovery-scope-002.md`
- operative_file: `bridge/gtkb-wi-4475-platform-pytest-discovery-scope-002.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

The three missing specs are advisory in this preflight output. Blocking
requirements are cited and satisfied, so they do not prevent GO.

## Clause Applicability

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi-4475-platform-pytest-discovery-scope`
- Operative file: `bridge\gtkb-wi-4475-platform-pytest-discovery-scope-002.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | - | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no owner-waiver line is cited. Clauses with `enforcement_mode = "advisory"` are
reported but never gate._
```

## Evidence

| Check | Result |
|---|---|
| Live bridge thread load | `show_thread_bridge` reported v002 latest with `drift: []`. |
| Work item | `gt backlog show WI-4475 --json` returned `origin=defect`, `priority=P1`, `project_name=PROJECT-GTKB-RELIABILITY-FIXES`, `stage=backlogged`, `resolution_status=open`. |
| Current config | `pyproject.toml` currently has `testpaths = ["platform_tests", "applications/Agent_Red/tests"]`. |
| Current failure class | `groundtruth-kb\.venv\Scripts\python.exe -m pytest --collect-only -q` fails while loading `applications\Agent_Red\tests\conftest.py` because `azure` is not installed. |
| Platform-only control | `groundtruth-kb\.venv\Scripts\python.exe -m pytest --collect-only -q platform_tests` succeeds and collects 4150 tests. |
| Existing regression target | `platform_tests/governance/test_platform_tests_rename.py` already parses `[tool.pytest.ini_options]` and asserts root pytest `testpaths`; adding the Agent Red exclusion assertion there is a natural local fit. |
| Dirty-source check | `git diff -- pyproject.toml platform_tests/governance/test_platform_tests_rename.py` produced no diff during review; implementation has not already been applied. |

## Findings

No blocking findings.

Non-blocking note: v002 is a self-revision before any Loyal Opposition NO-GO.
That is unusual for the standard lifecycle, but it preserved the full chain,
made the latest operative content clearer, and kept `bridge/INDEX.md` canonical.
It does not create a review blocker.

## Verification Expectations For Post-Implementation

Prime Builder's implementation report should include:

- the exact `pyproject.toml` `testpaths` diff;
- the new assertion in
  `platform_tests/governance/test_platform_tests_rename.py`;
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest --collect-only -q`;
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/governance/test_platform_tests_rename.py -q --tb=short`;
- `python -m ruff check pyproject.toml platform_tests/governance/test_platform_tests_rename.py` only for Python files where applicable; `ruff format --check` for the changed Python test file.

## Outcome

GO. Prime Builder may implement within the declared two-file target scope after
creating the normal implementation-start authorization packet from the latest
GO state.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
