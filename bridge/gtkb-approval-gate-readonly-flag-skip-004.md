GO

# Loyal Opposition Review - Approval-Gate Read-Only-Flag Skip REVISED-1

bridge_kind: loyal_opposition_review
Document: gtkb-approval-gate-readonly-flag-skip
Version: 004
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-15 UTC
Reviewed proposal: `bridge/gtkb-approval-gate-readonly-flag-skip-003.md`
Verdict: GO

## Claim

The `-003` revision resolves the prior NO-GO findings from
`bridge/gtkb-approval-gate-readonly-flag-skip-002.md`. Prime Builder may
implement the revised proposal within the stated scope: add segment-aware
read-only flag handling to `.claude/hooks/formal-artifact-approval-gate.py` and
add focused tests in `platform_tests/hooks/test_formal_artifact_approval_gate.py`.

This GO does not authorize whole-command read-only matching, exempting a formal
mutation because a read-only-looking token appears in a different shell segment,
or weakening strict formal-artifact approval for real mutations.

## Review Scope

- Read live `bridge/INDEX.md`; latest status for
  `gtkb-approval-gate-readonly-flag-skip` was `REVISED`, actionable for Loyal
  Opposition.
- Read the full thread chain:
  `bridge/gtkb-approval-gate-readonly-flag-skip-001.md`,
  `bridge/gtkb-approval-gate-readonly-flag-skip-002.md`, and
  `bridge/gtkb-approval-gate-readonly-flag-skip-003.md`.
- Read `.claude/rules/file-bridge-protocol.md` and the bridge skill operating
  contract.
- Ran mandatory applicability and ADR/DCL clause preflights.
- Searched and retrieved deliberation evidence.
- Inspected the current formal-artifact approval gate and the current platform
  test path.

## Prior Deliberations

Commands:

```text
python -m groundtruth_kb deliberations search "WI-3273 formal artifact approval gate read-only help dry-run validate-only DELIB-0835" --limit 8 --json
python -m groundtruth_kb deliberations get DELIB-0835 --json
python -m groundtruth_kb deliberations get DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS --json
```

Relevant results:

- `DELIB-0835` remains the controlling owner decision for strict formal
  artifact approval and audit-trail discipline.
- `DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS` records the 2026-05-14
  owner authorization for `PAUTH-PROJECT-GTKB-BRIDGE-TOOLING-ENHANCEMENTS`,
  including WI-3273.

No prior deliberation surfaced that contradicts a segment-aware read-only
exemption for genuine help, version, dry-run, or validation invocations.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-approval-gate-readonly-flag-skip
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:99b1a96653cf812d462226dba4183b2e3a663b0b60f21e2b80766db3babc979b`
- bridge_document_name: `gtkb-approval-gate-readonly-flag-skip`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-approval-gate-readonly-flag-skip-003.md`
- operative_file: `bridge/gtkb-approval-gate-readonly-flag-skip-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-approval-gate-readonly-flag-skip
```

Observed:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-approval-gate-readonly-flag-skip`
- Operative file: `bridge\gtkb-approval-gate-readonly-flag-skip-003.md`
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

No blocking findings.

### C1 - Prior F1 is resolved: the exemption is segment-aware

Evidence:

- `bridge/gtkb-approval-gate-readonly-flag-skip-003.md:24-37` removes the
  whole-command early-return design and requires the read-only flag to be in
  the same command segment as the formal mutation.
- The current hook already exposes relevant separator and token helpers:
  `COMMAND_SEPARATORS`, `_command_tokens()`, `_is_command_separator()`, and
  `_script_args()` (`.claude/hooks/formal-artifact-approval-gate.py:72`,
  `.claude/hooks/formal-artifact-approval-gate.py:134`,
  `.claude/hooks/formal-artifact-approval-gate.py:151`,
  `.claude/hooks/formal-artifact-approval-gate.py:165`).
- The revised test plan includes negative tests for semicolon, `&&`, and pipe
  compound commands (`bridge/gtkb-approval-gate-readonly-flag-skip-003.md:154-172`).

Impact: The revised design preserves `DELIB-0835` and
`GOV-ARTIFACT-APPROVAL-001` for real formal mutations while eliminating the
read-only false positives.

### C2 - Prior F2 is resolved: verification path now targets the live platform test file

Evidence:

- `bridge/gtkb-approval-gate-readonly-flag-skip-003.md:14` limits
  `target_paths` to `.claude/hooks/formal-artifact-approval-gate.py` and
  `platform_tests/hooks/test_formal_artifact_approval_gate.py`.
- `bridge/gtkb-approval-gate-readonly-flag-skip-003.md:176` corrects the
  verification command to
  `python -m pytest platform_tests/hooks/test_formal_artifact_approval_gate.py -q --tb=short`.
- `Test-Path` confirmed
  `platform_tests/hooks/test_formal_artifact_approval_gate.py` exists and
  `tests/hooks` does not exist. The top-level `tests` directory currently
  exists, but the old `tests/hooks/...` target remains absent; that does not
  affect this revised scope.

Impact: Prime Builder now has an executable, in-root verification target.

### C3 - Prior F3 is resolved: applicability preflight is clean

Evidence: the live mandatory preflight on the indexed `-003` operative file
reports `preflight_passed: true`, `missing_required_specs: []`, and
`missing_advisory_specs: []`.

Impact: The proposal now satisfies the bridge specification-linkage floor.

### C4 - Baseline targeted tests are executable

Command:

```text
python -m pytest platform_tests/hooks/test_formal_artifact_approval_gate.py -q --tb=short
```

Observed result: 12 passed.

Impact: The target test file is healthy before Prime Builder adds the new
spec-derived cases.

## Opportunity Radar

No additional material advisory is needed. This reviewed item is itself a
deterministic governance-hook fix, and the revised segment-aware design avoids
turning read-only inspection into recurring approval friction.

## Expected Implementation Report Evidence

The post-implementation report should carry forward:

- the linked specifications from the `-003` proposal;
- exact files changed;
- evidence that formal mutation evaluation is segment-aware and that there is
  no whole-command read-only early return;
- observed results for
  `python -m pytest platform_tests/hooks/test_formal_artifact_approval_gate.py -q --tb=short`
  and `python -m ruff check .`;
- applicability and clause preflight outputs after implementation.

## Decision

GO. Prime Builder may implement
`bridge/gtkb-approval-gate-readonly-flag-skip-003.md` within the approved scope.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
