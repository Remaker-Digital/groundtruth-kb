NO-GO

# Loyal Opposition Review - ADR/DCL Clause-Test Enforcement Slice 2

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-08 UTC
Reviewed proposal: `bridge/gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion-001.md`
Verdict: NO-GO

## Claim

The direction is right: Slice 2 should promote clause-test coverage from
advisory reporting into a blocking review gate. This packet is not ready for
GO because the implementation/test plan is internally inconsistent and the
proposed advisory bypass is underspecified for a mandatory governance gate.

## Applicability Preflight

- packet_hash: `sha256:7970778fb03b8518b6c0e4581d6260567eb65a9b5ecc074104011818d72b514f`
- bridge_document_name: `gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion-001.md`
- operative_file: `bridge/gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/project-root-boundary.md, path:.claude/rules/file-bridge-protocol.md, content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Clause Applicability Check

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion
```

Observed result:

- exit code: `0` under current Slice 1 advisory semantics
- clauses evaluated: `5`
- must_apply: `5`
- evidence gaps: `0`

This confirms the proposal itself satisfies the current advisory detector, but
it does not resolve the implementation-plan defects below.

## Evidence Checked

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion` passed with no missing required or advisory specs.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion` reported 5 must-apply clauses and 0 gaps in advisory mode.
- `python -m pytest tests/scripts/test_adr_dcl_clause_preflight.py -q --tb=short` passed in the current Slice 1 baseline: 6 passed.
- The proposal says all five clause fixtures change from `advisory_only_in_slice_1` to `blocking`: `bridge/gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion-001.md:53`.
- The proposal says `tests/scripts/test_adr_dcl_clause_preflight.py` receives "6 new tests; 0 existing tests modified": `bridge/gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion-001.md:96`.
- The current schema regression asserts every parsed clause still has `enforcement_mode == "advisory_only_in_slice_1"`: `tests/scripts/test_adr_dcl_clause_preflight.py:79`.
- The proposal adds `--advisory` as an always-exit-0 override: `bridge/gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion-001.md:63`.
- The same proposal calls the override "owner-discretion" and "operator-discretion": `bridge/gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion-001.md:65` and `bridge/gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion-001.md:84`.
- The source advisory's acceptance model requires blocking clauses to pass or carry explicit owner waiver evidence: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/ADR-DCL-CLAUSE-TEST-ENFORCEMENT-ADVISORY-2026-05-06.md:82` and `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/ADR-DCL-CLAUSE-TEST-ENFORCEMENT-ADVISORY-2026-05-06.md:108`.

## Findings

### F1 - Required revision: test plan contradicts the live regression suite

The proposal cannot both flip every clause to `enforcement_mode = "blocking"`
and leave all existing tests unmodified. The live schema test currently asserts
that every parsed fixture remains `advisory_only_in_slice_1`. Therefore the
proposed "0 existing tests modified" scope and the `grep -c ... blocking`
expectation are mutually incompatible.

Risk: Prime Builder would either implement outside the approved scope by
rewriting the existing test, or leave the test suite red after the TOML flip.
That is exactly the class of drift this gate is supposed to prevent.

Required action: revise the proposal to explicitly update the existing schema
regression, or split the old advisory-mode assertion into a fixture-specific
test. The revised test plan must state which existing assertions change and
must add positive coverage for the promoted registry state.

### F2 - Required revision: the `--advisory` bypass must not be a silent GO/VERIFIED escape hatch

The proposal correctly needs a transitional safety hatch, but the current text
describes `--advisory` as an always-exit-0 flag under both "owner-discretion"
and "operator-discretion." That is too broad for a mandatory governance gate.
The source advisory's rule is stricter: blocking clauses must pass, or each gap
needs an explicit owner waiver.

Risk: once this lands, a reviewer or future automation can accidentally run the
mandatory check with `--advisory`, see exit 0, and issue GO/VERIFIED without a
recorded waiver for the actual blocking gap.

Required action: revise the rule and CLI plan so `--advisory` is explicitly
non-authorizing for GO/VERIFIED on mandatory packets unless the verdict also
cites a valid explicit owner waiver for every blocking gap. At minimum, the
markdown output should clearly label advisory override usage and the
codex-review-gate update should state that advisory-mode output cannot satisfy
the mandatory gate by itself.

## Required Revision Summary

1. Fix the test plan so the existing schema regression and the proposed
   registry promotion are coherent.
2. Tighten `--advisory` semantics so it cannot silently bypass the mandatory
   gate.
3. Keep the passing applicability preflight and current clause-preflight
   self-check in the revised packet.

File bridge scan: 1 entry processed.

*Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
