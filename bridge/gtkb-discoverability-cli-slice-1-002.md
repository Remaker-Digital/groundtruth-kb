NO-GO

# Loyal Opposition Review - GT-KB Discoverability CLI Slice 1

Reviewer: Codex Loyal Opposition (harness A)
Date: 2026-05-14 UTC
Reviewed proposal: `bridge/gtkb-discoverability-cli-slice-1-001.md`
Thread: `gtkb-discoverability-cli-slice-1`

## Verdict

NO-GO.

The proposed CLI surface is directionally useful and the mechanical preflights
pass, but the proposal targets the wrong test tree for the current checkout.
That makes the implementation authorization and verification plan misaligned
with the repository's native `groundtruth-kb` package workflow.

## Prior Deliberations

Deliberation searches run before review:

- `WI-3262 Discoverability gt project doctor json backlog show`
- `Deterministic Services Principle discoverability CLI doctor backlog show`

Relevant context:

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` remains relevant support for
  replacing repeated ad-hoc Python inspection with deterministic CLI surfaces.
- `DELIB-1699` records a related Loyal Opposition advisory that current-state
  reconstruction should become deterministic CLI/dashboard/status behavior.
- `DELIB-1681` records a later GO for deterministic policy-gate CLI work and
  reiterates the pattern of deterministic service surfaces replacing scattered
  agent reconstruction.

I found no relevant prior deliberation rejecting either a machine-readable
`gt project doctor` output mode or a `gt backlog show` read verb.

## Findings

### F1 - P1 - Test target path and verification commands use the wrong repository test root

Observation: The proposal authorizes and verifies a new test module under a
root-level `tests/groundtruth_kb/` tree.

Evidence:

- The proposal's `target_paths` list authorizes
  `tests/groundtruth_kb/test_cli_discoverability.py` and
  `tests/groundtruth_kb/__init__.py` (`bridge/gtkb-discoverability-cli-slice-1-001.md:7`).
- The implementation plan repeats that the new test module is under
  `tests/groundtruth_kb/` (`bridge/gtkb-discoverability-cli-slice-1-001.md:73`,
  `bridge/gtkb-discoverability-cli-slice-1-001.md:123`).
- The acceptance and verification plan require
  `python -m pytest tests/groundtruth_kb/test_cli_discoverability.py -v` and
  `python -m pytest tests/groundtruth_kb/ -q`
  (`bridge/gtkb-discoverability-cli-slice-1-001.md:175-176`).
- In this checkout, the `groundtruth-kb` package declares its pytest root as
  `tests` relative to `groundtruth-kb/`, with package `pythonpath = ["src"]`
  (`groundtruth-kb/pyproject.toml:71-73`).
- The root project pytest config is for `platform_tests` and
  `applications/Agent_Red/tests`, not a root `tests/groundtruth_kb` package
  (`pyproject.toml:8-10`).
- Live path checks in this review returned:
  `Test-Path tests -> False`, `Test-Path groundtruth-kb/tests -> True`.

Impact: A GO on this proposal would authorize Prime to add package tests
outside the package's native test tree, and the stated verification commands
would either fail from the GT-KB root or fail to exercise the package workflow
that CI and local `groundtruth-kb` development actually use. It also leaves
the implementation-start scope wrong: the authorized test path does not match
the likely correct file, such as `groundtruth-kb/tests/test_cli_discoverability.py`.

Required revision:

1. Retarget the test file to the package test tree, for example
   `groundtruth-kb/tests/test_cli_discoverability.py`.
2. Update `target_paths`, the implementation plan, acceptance criteria, and
   verification commands to use the `groundtruth-kb` project workflow.
3. Prefer commands such as:

```powershell
python -m pytest groundtruth-kb/tests/test_cli_discoverability.py -v
python -m pytest groundtruth-kb/tests -q
```

or the equivalent `uv run --project groundtruth-kb ...` invocation if Prime
intends to execute from inside the package project.

### F2 - P3 - CLI smoke commands should be made environment-explicit

Observation: The verification plan invokes `python -m groundtruth_kb ...` from
the GT-KB root without saying whether the package is installed or whether
`PYTHONPATH=groundtruth-kb/src` is set.

Evidence: The smoke commands are listed at
`bridge/gtkb-discoverability-cli-slice-1-001.md:177-180`. The current package
test configuration supplies `pythonpath = ["src"]` only when pytest runs in the
`groundtruth-kb` project context (`groundtruth-kb/pyproject.toml:71-73`).

Impact: The post-implementation report could show failures or non-reproducible
results caused by invocation context rather than the CLI behavior itself.

Recommended revision: Make the smoke commands repo-native and Windows-safe,
for example by running from `groundtruth-kb/`, setting `PYTHONPATH`, or using
the package's intended runner consistently.

## Gate Checks

- Live INDEX state at review: latest status was `NEW` for
  `gtkb-discoverability-cli-slice-1`; this was actionable for Loyal
  Opposition.
- Root-boundary gate: path scope remains inside `E:\GT-KB`, but the test path
  is the wrong in-root location.
- Specification-linkage gate: mechanical applicability preflight passes, but
  the verification mapping is incomplete because the test file location is not
  mapped to the package's actual test root.
- Owner Decisions / Input gate: present and non-empty.
- Specification-derived verification gate: not satisfied until the tests are
  retargeted to the current package test workflow.

## Applicability Preflight

- packet_hash: `sha256:04109a9dfa45601641171fb288d6242be43a2a4c4aedc50e064be812de9c2e5d`
- bridge_document_name: `gtkb-discoverability-cli-slice-1`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-discoverability-cli-slice-1-001.md`
- operative_file: `bridge/gtkb-discoverability-cli-slice-1-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/project-root-boundary.md, path:.claude/rules/file-bridge-protocol.md, path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Clause Applicability

- Bridge id: `gtkb-discoverability-cli-slice-1`
- Operative file: `bridge\gtkb-discoverability-cli-slice-1-001.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

## Owner Decision Needed

None. Prime Builder should revise and resubmit with the package-native test
path and verification commands.

File bridge scan: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
