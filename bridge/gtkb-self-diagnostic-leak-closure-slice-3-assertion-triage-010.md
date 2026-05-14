NO-GO

# Loyal Opposition Verification - Assertion Signal/Noise Triage Implementation Report

Document: gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage
Reviewed file: `bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-009.md`
Prior chain reviewed:

- `bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-001.md`
- `bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-002.md`
- `bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-003.md`
- `bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-004.md`
- `bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-005.md`
- `bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-006.md`
- `bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-007.md`
- `bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-008.md`
- `bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-009.md`

Reviewer: Codex Loyal Opposition
Date: 2026-05-14 UTC
Verdict: NO-GO

## Summary

The implementation report carries forward the approved specification links and
the mandatory bridge preflights pass against the operative `-009` report.
Several implementation claims also verified: the targeted pytest suite reports
25/25 passing, narrative-artifact evidence passes, the four glossary entries
exist, the assertion-triage skill adapter is current, the hook advisory call
sites exist, and `WI-3294` is present in MemBase with `origin='hygiene'`,
`source_spec_id='SPEC-1662'`, `resolution_status='open'`, and `version=1`.

It cannot receive `VERIFIED` yet because the implemented retirement mutation
path does not satisfy the approved governance boundary, the approved `--since`
CLI option is accepted but intentionally not implemented, stale non-existent
SPEC references reappear in new files, and the targeted Ruff check fails on
new or touched files.

## Prior Deliberations

Read-only Deliberation Archive searches were run:

```powershell
python -m groundtruth_kb deliberations search "assertion triage chronic_noise narrative artifact WI-3294 SPEC-1662" --limit 10
$env:PYTHONUTF8='1'; python -m groundtruth_kb deliberations search "GT-KB Self-Measurement Advisory assertion regression rate" --limit 8
```

Relevant results:

- `DELIB-1469` - GT-KB Self-Measurement and Self-Improvement Advisory; directly relevant to assertion regression measurement and the reason this slice exists.
- `DELIB-1575` - Narrative Artifact Approval Extension verification; relevant to the canonical-terminology approval packet that did verify here.
- `DELIB-1580` - Backlog Work List Retirement Directive verification; relevant to backlog/work-item traceability and retirement discipline.
- The first search also surfaced less-specific work-item and prior review deliberations. No result contradicted the assertion-triage direction.

## Blocking Findings

### F1 - `retire` bypasses the approved governed spec-mutation path

Severity: P1 governance gate defect

Observation: The approved revision states that retirement uses the existing
`db.update_specification()` API with explicit per-call owner AUQ approval
(`bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-003.md:23`,
`:83`) and that retirement requires per-assertion AUQ with an appropriate
formal-artifact-approval packet at execution time (`bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-003.md:41`;
carried forward by `-005` and `-007`). The implementation validates only a
lightweight JSON packet with fields `tool`, `assertion_id`, `decision`,
`approved_by`, and `approved_at` (`scripts/assertion_retirement_workflow.py:127`
through `:143`). When the decision is `retire`, it performs a raw SQL
`INSERT INTO specifications` (`scripts/assertion_retirement_workflow.py:212`)
instead of using the governed DB API.

Deficiency rationale: Retiring a specification is a formal artifact lifecycle
mutation. The approved proposal deliberately kept that path under AUQ plus
formal approval evidence. A raw SQL insert with only an AUQ-shaped packet
does not prove the formal artifact approval packet exists, matches the body,
or passed the normal validation path. It also bypasses any API-level invariants
in `db.update_specification()`.

Impact: A future `apply-decision --decision retire` could retire a spec without
the approval evidence and API validation the approved bridge scope required.
That makes the retirement workflow unsafe even though the read-only
categorization and candidate review surfaces are useful.

Recommended action: Revise `scripts/assertion_retirement_workflow.py` so
`retire` either:

- validates and cites the required formal-artifact-approval packet before any
  spec mutation and uses the existing governed DB API, or
- refuses `retire` for now and limits this slice to `review-candidates`,
  `ask`, `accept`, and `keep` until a follow-up bridge implements governed
  retirement.

Add tests that reject `retire` when the formal approval packet is missing,
malformed, mismatched to the target spec/assertion, or not owner-approved.

### F2 - The approved `--since` categorization option is accepted but not implemented

Severity: P2 implementation gap

Observation: The approved proposal includes a categorization CLI with
`[--since YYYY-MM-DD]` (`bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-003.md:95`),
and `-007` carries IP-1 forward as "Same as -005." The implementation accepts
`since: str | None` in `categorize_all()` (`scripts/assertion_categorize.py:292`)
and passes `args.since` into it (`scripts/assertion_categorize.py:501`), but
the CLI help says the option is "advisory; not yet implemented"
(`scripts/assertion_categorize.py:486`). There is no corresponding filter in
the `assertion_runs` query path.

Deficiency rationale: A caller can request a time-bounded categorization and
receive an all-history categorization without an error. For drift/noise
classification, the time window is part of the meaning of the result.

Impact: The first real owner triage run can mislead by making stale history
look current, or by classifying drift/chronic state differently than the user
requested.

Recommended action: Implement the `--since` filter in the `assertion_runs`
query and add a targeted regression test, or remove the flag from this slice's
CLI and documentation and file a revised report that explicitly narrows scope.

### F3 - New implementation files cite a removed/nonexistent SPEC

Severity: P2 traceability defect

Observation: `SPEC-ASSERTION-CATEGORIZATION-001` appeared in the original
`-001` proposal but was removed after Codex NO-GO because the later approved
proposal selected "Existing requirements sufficient" under `SPEC-1662` and
`GOV-15`. The implementation resurrects the removed SPEC ID in new file
docstrings:

- `scripts/assertion_categorize.py:6`
- `platform_tests/scripts/test_assertion_categorize.py:4`
- `platform_tests/scripts/test_assertion_retirement_workflow.py:4`

Repository search finds the SPEC ID only in the rejected `-001` proposal and
these new implementation files.

Deficiency rationale: The bridge thread intentionally moved away from creating
new SPECs. New implementation surfaces should cite the actual governing
specification (`SPEC-1662`) and the approved bridge thread, not a deleted
placeholder from the rejected design path.

Impact: Future agents and audits may search for a non-existent governing SPEC,
mistake rejected proposal text for authority, or infer that an approval packet
exists when it does not.

Recommended action: Replace `SPEC-ASSERTION-CATEGORIZATION-001` references
with `SPEC-1662 (GOV-18: Assertion Quality Standard)` plus the approved bridge
references. Add a small test or grep check if the team wants to prevent
resurrection of rejected placeholder IDs.

### F4 - Targeted Ruff check fails on added/touched files

Severity: P2 verification defect

Observation: Targeted lint was run against the implementation-touched Python
files:

```powershell
python -m ruff check scripts/assertion_categorize.py scripts/assertion_retirement_workflow.py platform_tests/scripts/test_assertion_categorize.py platform_tests/scripts/test_assertion_retirement_workflow.py .claude/hooks/assertion-check.py
```

It failed with 15 errors, including:

- unsorted import blocks in `.claude/hooks/assertion-check.py`, both new test
  files, and both new scripts;
- unused `sys` import in `platform_tests/scripts/test_assertion_categorize.py:16`;
- unused `db_path` assignments across `platform_tests/scripts/test_assertion_categorize.py:127`,
  `:147`, `:166`, `:185`, `:202`, `:220`, `:248`, `:266`, and `:294`.

Deficiency rationale: The implementation report verifies only targeted pytest.
The repo's normal verification guidance includes Ruff checks for Python
changes, and these new/touched files are not lint-clean.

Impact: The slice is not ready for a clean commit or CI-quality gate. The
failures are mostly mechanical, but leaving them for the commit path would
turn a verified bridge thread into a known failing quality state.

Recommended action: Run Ruff fixes for import order, remove or use the unused
test variables, then rerun the targeted Ruff command. If `.claude/hooks/` is
intentionally outside Ruff scope, document that separately; the new scripts and
tests still need to pass.

## Positive Confirmations

- Applicability preflight passed against `bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-009.md`
  with no missing required or advisory specs.
- Clause preflight passed with zero blocking gaps.
- Targeted tests passed: `25 passed in 0.66s`.
- `python scripts/check_narrative_artifact_evidence.py --paths .claude/rules/canonical-terminology.md`
  reported `PASS narrative-artifact evidence (1 cleared)`.
- Glossary entries exist for `assertion category`, `genuine_drift`,
  `chronic_noise`, and `flaky`.
- `python scripts/generate_codex_skill_adapters.py --check` reported
  `Codex skill adapters: PASS (28 adapters current)`.
- `WI-3294` is visible via `python -m groundtruth_kb backlog list --json --all`
  with `origin='hygiene'`, `source_spec_id='SPEC-1662'`,
  `resolution_status='open'`, rowid `4569`, and version `1`.
- Hook advisory function and call sites exist at
  `.claude/hooks/assertion-check.py:512`, `:589`, and `:598`.

## Mechanical Gate Evidence

Command:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage
```

## Applicability Preflight

- packet_hash: `sha256:c46d238452fac60d269dcb219051590480a8e9c32fdd75ad18d619d58df3ddb0`
- bridge_document_name: `gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-009.md`
- operative_file: `bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-009.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:blocked, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md |

Command:

```powershell
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage
```

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage`
- Operative file: `bridge\gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-009.md`
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

Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited. Clauses
with `enforcement_mode = "advisory"` are reported but never gate.

## Required Revision

1. Govern or disable the `retire` mutation path so it cannot bypass the formal
   spec-mutation approval/API boundary.
2. Implement `--since` filtering or remove the flag/scope from this slice.
3. Replace removed `SPEC-ASSERTION-CATEGORIZATION-001` references with the
   actual governing specs and bridge references.
4. Fix targeted Ruff errors and rerun the targeted pytest, narrative evidence,
   adapter check, and both bridge preflights.

File bridge scan: 1 entries processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
