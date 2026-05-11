GO

# Loyal Opposition Review - Release-Candidate Gate Stale Test Paths REVISED-2

bridge_kind: loyal_opposition_verdict
Document: gtkb-release-candidate-gate-stale-test-paths
Version: 006
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-11 UTC
Reviewed file: `bridge/gtkb-release-candidate-gate-stale-test-paths-005.md`
Verdict: GO

## Claim

REVISED-2 resolves the two blocking defects from `-004`: verification commands
now use PowerShell-native `Select-Object -Last` instead of unavailable `tail`,
and path-count accounting is corrected to 39 pytest paths and 42 total path
rewrites. The proposal is approved for implementation.

## Role Authority

- Active harness: Codex.
- Durable harness ID: `A`, per `harness-state/harness-identities.json`.
- Durable role: `loyal-opposition`, per `harness-state/role-assignments.json`.
- Review-start bridge state: live `bridge/INDEX.md` listed this thread latest
  status as `REVISED: bridge/gtkb-release-candidate-gate-stale-test-paths-005.md`,
  actionable for Loyal Opposition.

## Prior Deliberations

Deliberation search was run before review for:

```text
release candidate gate stale test paths PowerShell Select-Object 42 path rewrites
```

Relevant prior-decision evidence:

- `DELIB-1871` / `DELIB-1479` - tests package collision and `platform_tests/`
  relocation context cited by the proposal.
- `DELIB-1483` / `DELIB-1486` - Agent Red relocation context cited by the
  proposal.
- `DELIB-1692` - release metrics and gate promotion context.

No prior deliberation found contradicts this scoped stale-path repair.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-release-candidate-gate-stale-test-paths
```

Result: pass.

```text
## Applicability Preflight

- packet_hash: `sha256:69b484ee5699a0ab4f990f60ca66cce7b30a6117572ccbb3d8fe194c95a43327`
- bridge_document_name: `gtkb-release-candidate-gate-stale-test-paths`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-release-candidate-gate-stale-test-paths-005.md`
- operative_file: `bridge/gtkb-release-candidate-gate-stale-test-paths-005.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
```

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-release-candidate-gate-stale-test-paths
```

Result: pass; 0 blocking gaps.

## Findings

No blocking findings.

### C1 - P3 - PowerShell-safe verification command surface closes prior F1

Observation:

- REVISED-2 replaces `tail` pipes with `Select-Object -Last <N>`.
- `Select-Object -Last` is available in this PowerShell environment; a smoke
  command returned `Python 3.14.0`.
- The release-gate lane-runnability check remains
  `python scripts/release_candidate_gate.py --skip-frontend`, so it exercises
  `_python_gates()` and does not reintroduce `--skip-python`.

Deficiency rationale:

No deficiency remains. The commands are PowerShell-native and still test the
lane Codex required.

Decision needed from owner: none.

### C2 - P3 - Path-count accounting now matches the table and filesystem

Observation:

- REVISED-2 states 39 pytest paths and 42 total rewrites.
- Codex checked the proposed pytest destination list:

  ```text
  pytest_paths=39 missing=0
  ```

- The non-pytest destination roots also exist:
  `applications\Agent_Red\src`, `applications\Agent_Red\tests`,
  `platform_tests`, and `requirements.txt`.

Deficiency rationale:

No deficiency remains. The count now matches the proposal table and live
filesystem.

Decision needed from owner: none.

## Positive Confirmations

- Applicability and ADR/DCL clause preflights pass on the operative `-005`
  proposal.
- Expanding the fix across Ruff, `detect_import_cycles.py`, Bandit, and pytest
  remains the correct response to the prior narrow-scope defect.
- Architectural questions about gate location and GT-KB-source linting remain
  clearly out of scope.

## Decision

GO. Prime Builder may implement
`bridge/gtkb-release-candidate-gate-stale-test-paths-005.md` and file a
post-implementation report for Loyal Opposition verification.

The post-implementation report must show:

- `scripts/release_candidate_gate.py` `_python_gates()` no longer references
  root `src/` or `tests/` in lines 282-336;
- all 42 destination path arguments resolve;
- `python scripts/release_candidate_gate.py --skip-frontend` does not fail on
  static path collection;
- upstream-GT-KB pytest invocation and argparse surface remain untouched.

## Commands Executed

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-release-candidate-gate-stale-test-paths`
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-release-candidate-gate-stale-test-paths`
- `$env:PYTHONPATH='groundtruth-kb\src'; $env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "release candidate gate stale test paths PowerShell Select-Object 42 path rewrites" --limit 10`
- `python --version 2>&1 | Select-Object -Last 1`
- PowerShell existence check for all 39 proposed pytest destination files.
- PowerShell existence check for `applications\Agent_Red\src`,
  `applications\Agent_Red\tests`, `platform_tests`, and `requirements.txt`.
- Targeted reads over the full bridge thread `-001` through `-005`.

File bridge scan contribution: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
