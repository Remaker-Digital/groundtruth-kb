NO-GO

# Loyal Opposition Verification - Spec-to-Test Mapping Helper Slice 2

bridge_kind: lo_verdict
Document: gtkb-verify-skill-spec-to-test-mapping
Version: 008
Author: Loyal Opposition (Codex, harness A)
Date: 2026-05-29 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-verify-skill-spec-to-test-mapping-007.md
Verdict: NO-GO

## Claim

The implementation is not ready for `VERIFIED`. The approved target paths are
present, the focused pytest suite passes when run with an in-repo temp
directory, and Ruff passes. However, two implemented behaviors diverge from the
GO'd `-005` helper data contract in ways that can make the verify helper return
incorrect machine-consumable evidence.

## Applicability Preflight

- packet_hash: `sha256:059e17e75aa37cb5b648f815c3223df1935d32320a6ab777a97137fc5d0322d5`
- bridge_document_name: `gtkb-verify-skill-spec-to-test-mapping`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-verify-skill-spec-to-test-mapping-007.md`
- operative_file: `bridge/gtkb-verify-skill-spec-to-test-mapping-007.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-verify-skill-spec-to-test-mapping`
- Operative file: `bridge\gtkb-verify-skill-spec-to-test-mapping-007.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | - | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Prior Deliberations

Deliberation review was performed against live `groundtruth.db`. The `gt`
command is not available on PATH in this auto-dispatch shell; a read-only
SQLite query against `current_deliberations` was used instead.

- `DELIB-S350-BATCH3-DETERMINISTIC-SERVICES` records the owner authorization
  for the deterministic-services batch containing WI-3261.
- `DELIB-2416` records the prior NO-GO on the original combined `/verify`
  skill + helper proposal.
- `DELIB-2415` records the prior GO on the narrowed helper-only proposal.
- `DELIB-2472` records the VERIFIED Slice 1 `/verify` verdict-author skill
  thread that this Slice 2 helper depends on.

No cited deliberation waives bridge review, spec-derived verification, or the
GO'd helper data contract.

## Specifications Carried Forward

- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- GOV-FILE-BRIDGE-AUTHORITY-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001
- SPEC-AUQ-POLICY-ENGINE-001
- ADR-ISOLATION-APPLICATION-PLACEMENT-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- GOV-STANDING-BACKLOG-001
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001
- DCL-PROJECT-AUTHORIZATION-ENVELOPE-001
- DELIB-S350-BATCH3-DETERMINISTIC-SERVICES

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
|---|---|---|---|
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | `uvx --with pytest-timeout --with pytest-asyncio pytest platform_tests/scripts/test_spec_to_test_mapper.py -q --tb=short --basetemp=.pytest-basetemp-specmapper-review-20260529b -p no:cacheprovider` | yes | PASS, 13 passed |
| GOV-FILE-BRIDGE-AUTHORITY-001 | `python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-verify-skill-spec-to-test-mapping --format json` | yes | PASS, no drift |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-verify-skill-spec-to-test-mapping` | yes | PASS, missing required/advisory specs empty |
| ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-verify-skill-spec-to-test-mapping` | yes | PASS, cited advisory spec |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-verify-skill-spec-to-test-mapping` | yes | PASS, cited advisory spec |
| SPEC-AUQ-POLICY-ENGINE-001 | Source/report inspection of bridge `-007` Owner Decisions / Input and helper implementation | yes | PASS, no new owner decision required |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | `git status --short -- .claude/skills/verify/SKILL.md .codex/skills/verify/SKILL.md tests scripts/spec_to_test_mapper.py platform_tests/scripts/test_spec_to_test_mapper.py` | yes | PASS for approved files; unrelated staged root `tests/scripts/...` changes pre-existed and are not part of this implementation |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-verify-skill-spec-to-test-mapping` | yes | PASS, blocking gaps 0 |
| GOV-STANDING-BACKLOG-001 | `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-verify-skill-spec-to-test-mapping` | yes | PASS, no blocking gap |
| GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 | Implementation report metadata and prior GO inspection | yes | PASS, cited PAUTH/project/WI carried forward |
| DCL-PROJECT-AUTHORIZATION-ENVELOPE-001 | Implementation report metadata and prior GO inspection | yes | PASS, cited PAUTH/project/WI carried forward |
| DELIB-S350-BATCH3-DETERMINISTIC-SERVICES | Read-only `current_deliberations` query for `WI-3261` and related terms | yes | PASS, deliberation found |

## Positive Confirmations

- The live bridge thread remains coherent and drift-free through version `007`.
- The implementation report carries forward the GO'd specification list and
  recommended commit type `feat`.
- `scripts/spec_to_test_mapper.py` and
  `platform_tests/scripts/test_spec_to_test_mapper.py` are present inside the
  authorized target paths.
- Ruff passes: `uvx ruff check ...` returned `All checks passed!`, and
  `uvx ruff format --check ...` returned `2 files already formatted`.
- Focused pytest passes when run with an in-repo temp directory:
  `13 passed in 0.48s`.

## Findings

### F1 - P1 - Bridge-id extraction reads the highest numbered file, not the latest proposal/report file required by the GO'd contract

Observation: The GO'd `-005` proposal says `--bridge-id <slug>` must "read the
latest NEW/REVISED/implementation report/proposal file for the bridge thread
and extract cited spec IDs" (`bridge/gtkb-verify-skill-spec-to-test-mapping-005.md:67`).
The implementation instead scans files by name, sorts by numeric suffix, and
uses the highest version regardless of bridge status
(`scripts/spec_to_test_mapper.py:80`, `scripts/spec_to_test_mapper.py:96-97`).
The platform test encodes that behavior as "highest-numbered file" rather than
the status-filtered contract
(`platform_tests/scripts/test_spec_to_test_mapper.py:217`).

Deficiency rationale: Verdict files commonly contain preflight and governance
spec IDs that are not the proposal/report's intended specification payload.
In a synthetic read-only check, a thread with `demo-001.md` as `NEW` citing
`SPEC-1111` and `demo-002.md` as `GO` citing
`GOV-FILE-BRIDGE-AUTHORITY-001` returned `demo-002.md` and extracted only
`GOV-FILE-BRIDGE-AUTHORITY-001`. That is the wrong source for the helper's
intended spec-to-test mapping and can corrupt later verification evidence.

Proposed solution: Resolve bridge source through `bridge/INDEX.md`, then select
the latest entry whose status/kind is a proposal or implementation report
(`NEW`/`REVISED`, with `bridge_kind` in `implementation_proposal` or
`implementation_report`). Explicitly skip `GO`, `NO-GO`, `VERIFIED`, and
`ADVISORY` verdict files for extraction.

Option rationale: Using `bridge/INDEX.md` matches `GOV-FILE-BRIDGE-AUTHORITY-001`
and avoids guessing queue state from filename order. It also makes the helper
robust after a thread has a later verdict file.

### F2 - P2 - JSON output does not normalize missing per-test status to `not_run`

Observation: The GO'd `-005` contract says "If a test row has no `last_result`,
status is `not_run`" (`bridge/gtkb-verify-skill-spec-to-test-mapping-005.md:83`).
Markdown honors this at `scripts/spec_to_test_mapper.py:173`, but JSON emits
the raw nullable database field at `scripts/spec_to_test_mapper.py:192`.
A read-only in-memory SQLite check with `last_result = NULL` produced markdown
`not_run` and JSON `"last_result": null`.

Deficiency rationale: The helper's JSON mode is the machine-consumable output
surface. Leaving `last_result` as `null` gives downstream consumers a different
status contract than markdown, while the proposal stated one status precedence
rule for both output modes.

Proposed solution: Normalize JSON test status the same way markdown does. The
minimal change is to emit `"last_result": t.last_result or "not_run"` for each
test row, or add an explicitly contracted `test_status` field while preserving
`last_result` only if a revised proposal changes the JSON contract.

Option rationale: Normalizing the existing field is the smallest change and
matches the current approved JSON shape. Adding a new field is acceptable only
if Prime Builder deliberately revises the contract to distinguish raw DB value
from display status.

## Required Revisions

1. Fix `--bridge-id` extraction to use the latest proposal/report source, not
   merely the highest-numbered bridge file.
2. Add regression coverage for a thread where a later `GO` or `NO-GO` verdict
   exists after a proposal/report; the helper must not extract specs from the
   verdict.
3. Normalize JSON output for tests with null `last_result` to the contracted
   `not_run` status, or file a REVISED proposal that explicitly changes the
   JSON data contract.
4. Add regression coverage proving JSON and markdown agree on the null
   `last_result` status rule.

Decision needed from owner: None.

## Commands Executed

```text
Get-Content -Raw bridge/INDEX.md
Get-Content -Raw bridge/gtkb-verify-skill-spec-to-test-mapping-001.md
Get-Content -Raw bridge/gtkb-verify-skill-spec-to-test-mapping-002.md
Get-Content -Raw bridge/gtkb-verify-skill-spec-to-test-mapping-003.md
Get-Content -Raw bridge/gtkb-verify-skill-spec-to-test-mapping-004.md
Get-Content -Raw bridge/gtkb-verify-skill-spec-to-test-mapping-005.md
Get-Content -Raw bridge/gtkb-verify-skill-spec-to-test-mapping-006.md
Get-Content -Raw bridge/gtkb-verify-skill-spec-to-test-mapping-007.md
Get-Content -Raw scripts/spec_to_test_mapper.py
Get-Content -Raw platform_tests/scripts/test_spec_to_test_mapper.py
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-verify-skill-spec-to-test-mapping
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-verify-skill-spec-to-test-mapping
python -m pytest platform_tests/scripts/test_spec_to_test_mapper.py -q --tb=short
python -m ruff check scripts/spec_to_test_mapper.py platform_tests/scripts/test_spec_to_test_mapper.py
python -m ruff format --check scripts/spec_to_test_mapper.py platform_tests/scripts/test_spec_to_test_mapper.py
.\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_spec_to_test_mapper.py -q --tb=short
.\.venv\Scripts\python.exe -m ruff check scripts/spec_to_test_mapper.py platform_tests/scripts/test_spec_to_test_mapper.py
uv run python -m pytest platform_tests/scripts/test_spec_to_test_mapper.py -q --tb=short
uvx --with pytest-timeout pytest platform_tests/scripts/test_spec_to_test_mapper.py -q --tb=short
uvx --with pytest-timeout --with pytest-asyncio pytest platform_tests/scripts/test_spec_to_test_mapper.py -q --tb=short --basetemp=.pytest-basetemp-specmapper-review-20260529b -p no:cacheprovider
uvx ruff check scripts/spec_to_test_mapper.py platform_tests/scripts/test_spec_to_test_mapper.py
uvx ruff format --check scripts/spec_to_test_mapper.py platform_tests/scripts/test_spec_to_test_mapper.py
python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-verify-skill-spec-to-test-mapping --format json
where.exe gt
read-only SQLite query against current_deliberations for WI-3261, spec-to-test mapping, verify skill, and DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
read-only in-memory SQLite checks for JSON null-status behavior and verdict-file bridge extraction behavior
```

Notes:

- The bare `python -m pytest` / `python -m ruff` and `.venv` commands failed
  because this shell's Python environment lacks `pytest` and `ruff`.
- `uv run` failed because the existing `.venv` also lacks those modules.
- `uvx` required `UV_CACHE_DIR` and `UV_TOOL_DIR` pinned under `E:\GT-KB`.
- The first `uvx pytest` run failed before exercising tests because pytest
  tried to use denied global temp path `C:\Users\micha\AppData\Local\Temp`.
  The rerun with an in-repo `--basetemp` passed.

File bridge scan contribution: 1 selected entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
