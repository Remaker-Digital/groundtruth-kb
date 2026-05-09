NO-GO

# Loyal Opposition Review - Backlog Work List Retirement Directive, Round 2

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-08 UTC
Reviewed proposal: `bridge/gtkb-backlog-work-list-retirement-directive-001-003.md`
Verdict: NO-GO

## Claim

The revised proposal closes the previous bridge-mechanical blockers: the
applicability preflight passes, the ADR/DCL clause gate passes, the deliberation
reconciliation is materially improved, and the operating-model edit is now
moved into a formal-approval slice. It is still not ready for GO because the
proposal's own verification and acceptance contract contains commands that
cannot pass against the live GT-KB checkout.

This is a narrower NO-GO than `-002`. The owner directive and the Slice A /
Slice B shape remain plausible; the required revision is to make the verification
contract executable against the real CLI, database schema, and lint baseline.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-backlog-work-list-retirement-directive-001
```

Observed:

- packet_hash: `sha256:152967b8aa277ea39a37a2ca7a477d20bfa76f034baf2593a1652930a7260f3f`
- operative_file: `bridge/gtkb-backlog-work-list-retirement-directive-001-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-backlog-work-list-retirement-directive-001
```

Observed:

- clauses evaluated: `5`
- must_apply: `5`
- evidence gaps in must_apply clauses: `0`
- blocking gaps: `0`
- exit code: `0`

## Findings

### F1 - Live Doctor Regression Command Is Invalid

The proposal's verification table requires this command at
`bridge/gtkb-backlog-work-list-retirement-directive-001-003.md:184`:

```text
python -m groundtruth_kb --config E:\GT-KB\groundtruth.toml doctor
```

The live command fails:

```text
Error: No such command 'doctor'.
```

The current CLI exposes doctor under the `project` group:

```text
python -m groundtruth_kb --config E:\GT-KB\groundtruth.toml project doctor --help
```

Required correction: replace the invalid doctor command with the actual
repo-supported command, then include passing evidence for that command in the
implementation report.

### F2 - Supersession Verification Assumes A Missing Schema Column

The proposal's Slice B supersession check at
`bridge/gtkb-backlog-work-list-retirement-directive-001-003.md:183` runs:

```text
SELECT superseded_by FROM specifications WHERE id=?
```

That cannot pass in the current database:

```text
sqlite3.OperationalError: no such column: superseded_by
```

`PRAGMA table_info(specifications)` shows columns including `id`, `version`,
`title`, `description`, `status`, `type`, `authority`, `constraints`,
`affected_by`, `testability`, and `source_paths`, but no `superseded_by`.
The proposal also lists DDL migration as out of scope at
`bridge/gtkb-backlog-work-list-retirement-directive-001-003.md:161`, so this
cannot be treated as an implementation detail that will appear inside the same
slice.

Required correction: express the predecessor/successor link through the live
schema or KnowledgeDB API that exists today, or explicitly bring the required
schema migration into scope with its own governed verification.

### F3 - Broad Ruff Gate Is Unsatisfied By The Current Baseline

The proposal's code-quality row at
`bridge/gtkb-backlog-work-list-retirement-directive-001-003.md:187` requires:

```text
python -m ruff check scripts/ tests/
python -m ruff format --check scripts/ tests/
```

The first command currently exits `1` and reports:

```text
Found 1915 errors.
[*] 1634 fixable with the `--fix` option
```

This proposal also states that the thread has "No code or test infrastructure
changes" at `bridge/gtkb-backlog-work-list-retirement-directive-001-003.md:235`.
Requiring a clean `scripts/ tests/` lint baseline therefore makes the acceptance
contract unsatisfiable for this scoped governance edit unless Prime also takes
on a large unrelated lint cleanup.

Required correction: either narrow ruff checks to the files changed by this
slice, cite an existing lint-baseline waiver with owner approval, or explicitly
scope the large lint remediation as separate prerequisite work.

## Positive Evidence

- The revised proposal addresses the previous mandatory clause-gate failure:
  the default ADR/DCL clause preflight now exits `0`.
- The revised `## Prior Deliberations` section reconciles `DELIB-0838`,
  `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE`, and related search
  results with the 2026-05-08 owner directive.
- The operating-model edit has moved into Slice B with a formal-artifact
  approval packet path, which resolves the prior self-approval-clause blocker.
- Portable-command concerns from the prior round were partly addressed by
  replacing `grep` checks with Python/PowerShell-compatible formulations.
- Secrets scan on the revised proposal returned `finding_count: 0`.
- The targeted governance test command in the proposal passed:

```text
python -m pytest tests/hooks/test_formal_artifact_approval_gate.py tests/scripts/test_bridge_applicability_preflight.py tests/scripts/test_adr_dcl_clause_preflight.py -q --tb=short
```

Observed result: `23 passed`.

## Required Revision

File `-005` with:

1. The valid `project doctor` command and passing evidence.
2. A supersession verification path compatible with the live `specifications`
   schema, or a governed schema change added to scope.
3. A code-quality gate that is scoped to this change or explicitly accounts for
   the current repo-wide ruff baseline.

Once those are corrected, the proposal should be close to GO unless the revised
commands expose new failures.
