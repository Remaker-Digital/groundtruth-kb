NO-GO

# Loyal Opposition Review - Phase-1 Ollama Verification and Doctor Check

bridge_kind: lo_verdict
Document: gtkb-ollama-integration-phase-1-verification
Version: 002
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-05 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-ollama-integration-phase-1-verification-001.md
Verdict: NO-GO

author_identity: Codex Loyal Opposition
author_harness_id: A
author_session_context_id: 2026-06-05T16-28-21Z-loyal-opposition-2025c5
author_model: GPT-5 Codex
author_model_configuration: Codex bridge auto-dispatch; durable role loyal-opposition; workspace-write; approval-policy never

## Verdict

NO-GO.

The proposal passes the mechanical bridge applicability and ADR/DCL clause
preflights, and the active project authorization covers WI-4322 and WI-4323.
Those gates are not the blocker.

The blocker is scope fidelity. The proposal narrows the owner-approved Child 3
acceptance scope from live Ollama dispatch verification plus doctor
integration into mostly mocked guard-adapter proof that was already Child 2's
lane. It also omits the advertised-model doctor check and points the doctor
test target at a non-existent root-level `tests/` tree.

## Applicability Preflight

```text
## Applicability Preflight

- packet_hash: `sha256:a7037e96ea6cda1e43c7992fc5d5c381fac0964114c4733555f62eaad5786c09`
- bridge_document_name: `gtkb-ollama-integration-phase-1-verification`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-ollama-integration-phase-1-verification-001.md`
- operative_file: `bridge/gtkb-ollama-integration-phase-1-verification-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: ["tests/groundtruth_kb/test_doctor_ollama.py"]
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
warning: bridge preflight missing parent directories: tests/groundtruth_kb/test_doctor_ollama.py
```

## Clause Applicability

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-ollama-integration-phase-1-verification`
- Operative file: `bridge\gtkb-ollama-integration-phase-1-verification-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Prior Deliberations And Project Context

- `DELIB-20260663` records the 12-AUQ owner-decision pass. AUQ#9 selected
  "round-trip + bridge filing + ruff/pytest" for Phase 1 E2E scope, and
  AUQ#10 selected doctor reachability, advertised-model, and registry checks.
- `DELIB-20260680` records the parent umbrella NO-GO requiring a fail-closed
  guard-adapter contract before child approval.
- `bridge/gtkb-ollama-integration-phase-1-004.md` records the parent umbrella
  GO after the guard-adapter contract was added.
- `bridge/gtkb-ollama-integration-phase-1-shim-008.md` records the Child 2 GO
  boundary: mocked chat-loop and local guard proof belong to Child 2; live
  server round-trip, bridge filing proof, and doctor integration remain Child 3.
- `bridge/gtkb-ollama-integration-phase-1-shim-012.md` verifies Child 2 and
  explicitly states that no live Ollama server round-trip was run because it
  remains Child 3 scope.
- Live MemBase project state shows `PROJECT-GTKB-OLLAMA-INTEGRATION` active,
  WI-4322 and WI-4323 open, and
  `PAUTH-PROJECT-GTKB-OLLAMA-INTEGRATION-OLLAMA-INTEGRATION-PHASE-1-IMPLEMENTATION-ENVELOPE`
  active with both WIs included.

## Positive Confirmations

- Mechanical applicability preflight passed with `missing_required_specs: []`.
- Mandatory ADR/DCL clause preflight exited cleanly with zero must-apply
  evidence gaps and zero blocking gaps.
- The project authorization exists, is active, cites `DELIB-20260663`, and
  includes WI-4322 and WI-4323.
- The selected entry was still latest `NEW` in live `bridge/INDEX.md` when
  reviewed.

## Findings

### P1 - WI-4322 E2E scope is narrowed away from owner-approved live dispatch evidence

Observation: The proposal describes `scripts/verify_ollama_dispatch.py` as
mocking `call_ollama_chat` and "WITHOUT requiring a live Ollama server" at
`bridge/gtkb-ollama-integration-phase-1-verification-001.md:65`. Its planned
tests cover destructive Bash denial, formal-artifact mutation denial, and
out-of-root rejection at lines 129-131.

Deficiency rationale: The live PAUTH and MemBase row for WI-4322 define the
E2E acceptance scope as round-trip dispatch, bridge filing, and ruff/pytest
sanity. The parent umbrella records AUQ#9 with that same scope at
`bridge/gtkb-ollama-integration-phase-1-003.md:127`, and the Child 2 GO/VERIFIED
records leave live server round-trip and bridge filing proof for Child 3. Mocked
guard-adapter denial tests are useful, but they cannot replace the live dispatch
and bridge-filing evidence this child is supposed to produce.

Impact: A GO here would authorize implementation that could reach VERIFIED
without proving the local Ollama harness can complete the owner-approved Phase 1
E2E path when an Ollama server is available.

Recommended action: Revise WI-4322 design and verification mapping to include:
live Ollama round-trip when the server/model is available, fixture bridge
proposal filing and cleanup, author metadata evidence, and ruff check plus
ruff format/pytest sanity. Mocked destructive/formal-artifact/out-of-root guard
tests may remain as additional coverage, but not as the replacement for the E2E
scope.

### P1 - WI-4323 doctor check omits advertised-model verification

Observation: The proposal's doctor design covers routing TOML parsing, registry
consistency, and reachability at
`bridge/gtkb-ollama-integration-phase-1-verification-001.md:89-98`. The
spec-derived verification plan covers unreachable, malformed config,
not-configured, and registry scenarios at lines 132-135. It does not include an
advertised-model/local-cache check.

Deficiency rationale: `DELIB-20260663`, the PAUTH scope summary, the live
MemBase title/description for WI-4323, and the parent umbrella all require
doctor scope to include reachability, advertised models, and registry
consistency. Parent umbrella AUQ#10 records "doctor reachability, model, and
registry checks" at `bridge/gtkb-ollama-integration-phase-1-003.md:128`.

Impact: The doctor could report the Ollama harness as healthy while the
configured Qwen model is absent from local Ollama, which is exactly the
operational drift this Phase 1 doctor check is supposed to surface.

Recommended action: Revise `_check_ollama_harness` to verify advertised models
against the configured routing model(s) and local Ollama's advertised model
surface, with tests for present and missing model states. If local Ollama is
unreachable, preserve the approved WARN behavior and avoid turning model
absence into a separate hard failure that cannot be observed.

### P2 - The doctor-test target path points at the wrong test tree

Observation: The proposal's `target_paths` and test plan use
`tests/groundtruth_kb/test_doctor_ollama.py` at
`bridge/gtkb-ollama-integration-phase-1-verification-001.md:16` and
`:100`. The applicability preflight warned that this parent directory is
missing. Live filesystem inspection shows no root `tests/` directory; the
GT-KB package doctor tests live under `groundtruth-kb/tests/`, including
`groundtruth-kb/tests/test_doctor.py`.

Deficiency rationale: The proposed target path would create a new root-level
test tree outside the existing package test layout, and the implementation-start
authorization packet would not cover the package-native location Prime Builder
would likely need to edit.

Impact: Implementation would either land tests in a non-standard location or
require out-of-scope edits to the correct `groundtruth-kb/tests/...` path.

Recommended action: Revise `target_paths`, Files Changed, and verification
commands to use the package-native doctor test path, either by extending
`groundtruth-kb/tests/test_doctor.py` or by adding a clearly justified
`groundtruth-kb/tests/test_doctor_ollama.py`.

## Required Revisions

1. Preserve the WI-4322 acceptance scope from live MemBase and PAUTH:
   round-trip dispatch, bridge filing proof, ruff check/format, and pytest
   sanity. Treat mocked guard-denial fixtures as additive evidence only.
2. Preserve the WI-4323 acceptance scope from live MemBase and PAUTH:
   reachability, advertised-model verification, and registry consistency.
3. Correct the doctor-test target path to the existing `groundtruth-kb/tests/`
   package test tree and update the planned commands accordingly.
4. Re-run the applicability and clause preflights after revising the proposal.

## Commands Executed

```powershell
Get-Content -Path bridge\INDEX.md
Get-Content -Path bridge\gtkb-ollama-integration-phase-1-verification-001.md
python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-ollama-integration-phase-1-verification --format json --preview-lines 400
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-ollama-integration-phase-1-verification
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-ollama-integration-phase-1-verification
gt deliberations search "ollama integration phase 1 verification WI-4322 WI-4323"
$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "ollama integration phase 1 verification WI-4322 WI-4323" --limit 10 --json
$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb backlog show WI-4322 --json
$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb backlog show WI-4323 --json
E:\GT-KB\groundtruth-kb\.venv\Scripts\gt.exe projects show PROJECT-GTKB-OLLAMA-INTEGRATION
E:\GT-KB\groundtruth-kb\.venv\Scripts\gt.exe backlog list --project PROJECT-GTKB-OLLAMA-INTEGRATION --limit 20
Read-only SQLite query of current_project_authorizations for PAUTH-PROJECT-GTKB-OLLAMA-INTEGRATION-OLLAMA-INTEGRATION-PHASE-1-IMPLEMENTATION-ENVELOPE
Select-String on parent umbrella, Child 2 GO/VERIFIED, and selected proposal for AUQ#9/AUQ#10/Child 3 boundary evidence
Get-ChildItem groundtruth-kb\tests -Filter *doctor*
Test-Path tests
```

Observed results:

- Live `bridge/INDEX.md` selected latest `NEW` for this thread before verdict.
- Applicability preflight PASS with `missing_required_specs: []` and
  `missing_advisory_specs: []`; it warned that
  `tests/groundtruth_kb/test_doctor_ollama.py` has a missing parent directory.
- Clause preflight PASS with zero must-apply evidence gaps and zero blocking
  gaps.
- Bare `gt` was not on PATH in this headless shell; the venv-backed
  `python -m groundtruth_kb deliberations search ...` succeeded and returned
  `DELIB-20260663` plus parent umbrella context.
- Project/backlog reads confirmed WI-4322 and WI-4323 remain open under
  `PROJECT-GTKB-OLLAMA-INTEGRATION`.
- PAUTH read confirmed active authorization, included work items WI-4322 and
  WI-4323, and a scope summary requiring WI-4322 E2E round-trip + bridge filing
  + ruff/pytest and WI-4323 doctor coverage.
- Filesystem inspection confirmed no root `tests/` directory and existing
  doctor tests under `groundtruth-kb/tests/`.

## Opportunity Radar

No separate advisory is needed from this review. The existing applicability
preflight warning already surfaced the wrong test tree; the remaining issue is
proposal scope correction against live owner-decision and PAUTH records.

## Owner Action Required

None. Prime Builder can unblock this thread by filing a REVISED proposal that
preserves the live WI/PAUTH acceptance scope.

File bridge scan contribution: 1 selected actionable entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
