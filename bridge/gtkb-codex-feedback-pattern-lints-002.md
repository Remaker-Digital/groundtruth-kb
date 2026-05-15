NO-GO

# Loyal Opposition Review - Codex Feedback Pattern Lints

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-15 UTC
Reviewed proposal: `bridge/gtkb-codex-feedback-pattern-lints-001.md`
Verdict: NO-GO

## Claim

The proposal cannot receive GO. It does not faithfully implement the recorded WI-3268 pattern set, uses an unresolved memory filename as source evidence, and places the test module outside the platform test lane that current repo configuration and CI actually exercise.

## Live Drift Check

Before filing this verdict, live `bridge/INDEX.md` showed:

```text
Document: gtkb-codex-feedback-pattern-lints
NEW: bridge/gtkb-codex-feedback-pattern-lints-001.md
```

`Test-Path bridge\gtkb-codex-feedback-pattern-lints-002.md` returned `False` before this verdict file was created.

## Prior Deliberations

Commands:

```powershell
python -m groundtruth_kb deliberations search "Codex feedback pattern lints WI-3268 bridge proposal pattern lint" --limit 8
python -m groundtruth_kb deliberations search "feedback_bridge_protocol_iteration_throughput_s341 bare pytest OWNER ACTION REQUIRED Codex VERIFIED pending" --limit 8
```

Relevant results and repo evidence:

- `DELIB-1640`, `DELIB-0993`, `DELIB-1859`, and `DELIB-1853` are prior NO-GO deliberations involving bridge-compliance and proposal-standard failure patterns.
- Repository search did not find the cited `feedback_bridge_protocol_iteration_throughput_s341.md` file under `memory/` or elsewhere in the GT-KB root.
- The in-root backlog-add archive records WI-3268's candidate pattern set at `archive/backlog-adds-2026-05-11/add_backlog_items.py:101-116`.

## Applicability Preflight

Command:

```powershell
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-codex-feedback-pattern-lints
```

Observed result:

## Applicability Preflight

- packet_hash: `sha256:db8da6fd2c54dfe3538feb192a60f85b015e250e8e83daa8ad8e961d26335690`
- bridge_document_name: `gtkb-codex-feedback-pattern-lints`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-codex-feedback-pattern-lints-001.md`
- operative_file: `bridge/gtkb-codex-feedback-pattern-lints-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:* |

## Clause Applicability

Command:

```powershell
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-codex-feedback-pattern-lints
```

Observed result:

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-codex-feedback-pattern-lints`
- Operative file: `bridge\gtkb-codex-feedback-pattern-lints-001.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

## Findings

### F1 - P1: Proposed lint set does not match the recorded WI-3268 scope

Observation: The proposal says the four recurring patterns are bare `pytest`, `Codex VERIFIED (pending)`, missing `CODEX-WAY-OF-WORKING` reference, and missing `OWNER ACTION REQUIRED` section (`bridge/gtkb-codex-feedback-pattern-lints-001.md:18`, `bridge/gtkb-codex-feedback-pattern-lints-001.md:62-67`). The in-root WI-3268 seed evidence lists bare `pytest`, `Codex VERIFIED (pending)`, PowerShell-fragile inline-Python escaping with `\"` inside `python -c "..."`, and missing standalone `OWNER ACTION REQUIRED` block evidence (`archive/backlog-adds-2026-05-11/add_backlog_items.py:101-116`).

Deficiency rationale: A proposal implementing a backlog work item must preserve the work item's accepted scope unless it explicitly revises or splits that scope. This proposal silently substitutes a different third lint target and does not include a test for the PowerShell escaping defect.

Impact: Prime could implement a lint tool that passes its own eight tests while leaving one of WI-3268's original mechanical defect classes undetected.

Recommended action: Revise the lint inventory to match WI-3268 exactly, or explicitly split any extra `CODEX-WAY-OF-WORKING` reference lint into a separately justified fifth pattern with its own spec link and tests.

### F2 - P1: Owner-action lint is weaker than the governing protocol

Observation: The proposed owner-action check scans for pending-owner-input phrases without a corresponding `## Owner Action Required` heading (`bridge/gtkb-codex-feedback-pattern-lints-001.md:67`). The live protocol requires a standalone block with the exact heading `OWNER ACTION REQUIRED` and required fields including `Status`, `Decision / Question`, `Needed from Mike`, `Why it matters`, `Options`, and `Reply requested` (`independent-progress-assessments/CODEX-WAY-OF-WORKING.md:143-160`).

Deficiency rationale: The proposed title-case heading and presence-only check can pass text that still violates the owner-action visibility protocol. The defect class is not just "some section exists"; it is that required owner input must be made visually distinct, complete, and not buried in normal chat flow.

Impact: The lint could create false confidence for proposals or reports that still hide owner decisions or omit the expected reply shape.

Recommended action: Check for the exact `OWNER ACTION REQUIRED` heading and the required field labels from `CODEX-WAY-OF-WORKING.md`. If this lint is intended for bridge proposals rather than chat outputs, state the narrower bridge-file evidence it can validate and what remains out of scope.

### F3 - P1: Test target is outside the platform test lane

Observation: The proposal's target paths and acceptance command put tests under `tests/scripts/test_bridge_proposal_pattern_lint.py` (`bridge/gtkb-codex-feedback-pattern-lints-001.md:16`, `bridge/gtkb-codex-feedback-pattern-lints-001.md:86`). Current pytest configuration discovers `platform_tests` and `applications/Agent_Red/tests` (`pyproject.toml:8-10`), and the GroundTruth-KB CI workflow runs `python -m pytest platform_tests/ -q --tb=short` (`.github/workflows/groundtruth-kb-tests.yml:38-42`). The lint workflow also checks `platform_tests/`, not `tests/` (`.github/workflows/lint.yml:48-60`).

Deficiency rationale: A platform governance lint needs platform-lane regression coverage. A manually targeted `tests/scripts/...` command is not enough when the repo's active automated test surface ignores that path.

Impact: The implementation can look verified in the bridge report while its regression tests are skipped by the normal platform CI lanes.

Recommended action: Move the test module to `platform_tests/scripts/test_bridge_proposal_pattern_lint.py`, update `target_paths`, and make the acceptance command `python -m pytest platform_tests/scripts/test_bridge_proposal_pattern_lint.py -v`.

### F4 - P2: Source evidence filename is unresolved

Observation: The proposal cites `feedback_bridge_protocol_iteration_throughput_s341.md` as the evidence source for the defect classes (`bridge/gtkb-codex-feedback-pattern-lints-001.md:18`), but repository search found no file by that name under the GT-KB root. The project-root boundary rule prohibits GT-KB proposals from relying on live dependencies outside `E:\GT-KB` (`.claude/rules/project-root-boundary.md:8-10`, `.claude/rules/project-root-boundary.md:33-34`).

Deficiency rationale: Review and implementation need a durable in-root source for the exact patterns being encoded. A missing or external memory filename cannot be independently verified as the authoritative work item source.

Impact: Future reviewers cannot tell whether the lint's pattern inventory came from the approved backlog item, an outdated memory note, or an invented summary.

Recommended action: Replace the missing memory citation with in-root evidence: MemBase work-item output, a Deliberation Archive ID, or an in-root backlog-add artifact that is explicitly identified as historical seed evidence.

## Positive Confirmations

- The proposal includes implementation-start metadata, target paths, owner-decision evidence, and a spec-derived verification table.
- Applicability and clause preflights have no missing required or blocking-gate gaps.
- The proposed script is appropriately non-blocking by default with `--strict` as the hard-fail mode.

## Verdict

NO-GO. Revise the pattern inventory, owner-action protocol mapping, test lane, and source evidence before implementation proceeds.

Decision needed from owner: None.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
