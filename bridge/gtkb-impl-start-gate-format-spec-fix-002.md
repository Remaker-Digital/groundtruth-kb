NO-GO

# Loyal Opposition Review - implementation_start_gate Format-Spec Fix

Reviewer: Codex (Loyal Opposition, harness A)
Date: 2026-05-14 UTC
Reviewed proposal: `bridge/gtkb-impl-start-gate-format-spec-fix-001.md`
Verdict: NO-GO

## Claim

The proposal addresses a real implementation-start-gate false positive, and the
blocking mechanical preflights pass. It is not ready for `GO` because the
concrete proposed redirect regex would stop detecting existing real-file
redirect true positives, weakening the protected mutation gate the proposal is
meant to repair.

## Review Scope

- Read live `bridge/INDEX.md`; latest status for `gtkb-impl-start-gate-format-spec-fix` was `NEW`, actionable for Loyal Opposition.
- Read the full thread via `show_thread_bridge.py`; no drift was reported.
- Read `.claude/rules/file-bridge-protocol.md`, `.claude/rules/codex-review-gate.md`, `.claude/rules/deliberation-protocol.md`, `.claude/rules/operating-model.md`, `.claude/rules/loyal-opposition.md`, and `.claude/rules/report-depth-prime-builder-context.md`.
- Ran the mandatory applicability and clause preflights.
- Searched the Deliberation Archive before review.
- Inspected current `scripts/implementation_start_gate.py` and `platform_tests/scripts/test_implementation_start_gate.py`.

## Prior Deliberations

Commands:

```text
python -m groundtruth_kb deliberations search "MUTATING_COMMAND_RE format spec false positive WI-3317 Add as 6th WI" --limit 10 --json
python -m groundtruth_kb deliberations get DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT --json
```

Relevant result:

- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` records the 2026-05-14 owner directive and specifically says `MUTATING_COMMAND_RE format-spec false-positive -> Add as 6th WI`.

No prior deliberation found in this review contradicts fixing the false positive. The blocker below is the proposed implementation shape.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-impl-start-gate-format-spec-fix
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:33073ccbb9c9da3ce4668dabe1a0a11d86e66eceb0c76515a815fb7ff3b46a52`
- bridge_document_name: `gtkb-impl-start-gate-format-spec-fix`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-impl-start-gate-format-spec-fix-001.md`
- operative_file: `bridge/gtkb-impl-start-gate-format-spec-fix-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

The missing advisory specs are not the blocking reason for this verdict.

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-impl-start-gate-format-spec-fix
```

Observed:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-impl-start-gate-format-spec-fix`
- Operative file: `bridge\gtkb-impl-start-gate-format-spec-fix-001.md`
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
```

## Findings

### F1 - Proposed regex drops existing real-file redirect true positives

Severity: P1 / blocking

Evidence:

- The proposal's concrete replacement pattern is `r"(?:^|\s)>{1,2}\s*[^\s&>]"`.
- Current tests in `platform_tests/scripts/test_implementation_start_gate.py` assert these are mutating:
  - `cmd > out.txt`
  - `cmd 2> err.txt`
  - `cmd 1> out.txt`
  - `cmd &> out.txt`
- The proposed pattern requires beginning-of-line or whitespace immediately before `>`. It therefore does not match numbered or combined shell redirects where `1`, `2`, or `&` immediately precedes the redirect operator.
- The proposal links `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`; weakening redirect detection would cut against that protected behavior.

Risk / impact:

The implementation-start gate would become less strict for real file writes while trying to fix a read-only Python formatting false positive. That creates a false-negative path for shell redirection commands, including redirect forms the current test suite already treats as mutating.

Recommended action:

Revise IP-1 so the design explicitly preserves all current real-file redirect forms before excluding Python format specs. The revised test plan should include existing true positives for `>`, `>>`, `1>`, `2>`, and `&>`, plus the new false-positive cases for Python `:>`, `:<`, and `:^` format specs.

### F2 - Verification target includes a stale top-level test path

Severity: P2

Evidence:

- The proposal's `target_paths` and test command reference `tests/scripts/test_implementation_start_gate.py`.
- Live checkout inspection found no top-level `tests/` directory. The existing implementation-start-gate test file is `platform_tests/scripts/test_implementation_start_gate.py`.
- Running the proposed current command shape before implementation failed with `ERROR: file or directory not found: tests/scripts/test_implementation_start_gate.py`.

Risk / impact:

The proposal's verification command is not currently executable unless Prime creates a new top-level test tree. That may be intentional, but the proposal does not say why a duplicate test surface is needed when the existing platform test file already covers this gate.

Recommended action:

Revise the proposal to target the existing `platform_tests/scripts/test_implementation_start_gate.py`, or explicitly justify creating a new top-level `tests/scripts/` test surface and make the verification command executable after implementation.

## Positive Evidence

- The owner-decision evidence in `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` supports fixing this false positive.
- Root-boundary evidence is adequate.
- The proposal includes a substantive `Owner Decisions / Input` section.
- Applicability and clause preflights have no missing required specs and no blocking clause gaps.

## Required Revision

File a revised proposal that:

1. Replaces the proposed regex with a design that preserves current numbered and combined redirect detection.
2. Adds spec-derived tests for both the new Python format-spec false-positive cases and the existing redirect true-positive cases.
3. Corrects or justifies the test file layout and post-implementation command.

After those changes, the proposal should be reviewable for `GO`.
