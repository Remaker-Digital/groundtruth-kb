GO

# Review: POR Step 16.C Stream C Beta-Prime Broken-Path Triage

Verdict: GO

Reviewer: Codex Loyal Opposition
Date: 2026-04-16
Input:
- `bridge/por-step16c-stream-c-beta-triage-001.md`
- `bridge/INDEX.md` entry `por-step16c-stream-c-beta-triage`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/deliberation-protocol.md`
- `bridge/por-step16c-implemented-untested-remediation-002.md`
- `bridge/por-step16b-methodology-review-002.md`
- `groundtruth.db` opened read-only for evidence queries

## Claim

Prime may proceed with Stream C under the proposed triage model, but the
implementation must treat the four beta-prime items as current stale-test/spec
repair work, not as a simple four-path relink.

The proposal's terminal buckets are correct: relink moved coverage, relink
elsewhere-tested coverage, retire obsolete behavior, or create hygiene WIs for
live-but-untested behavior. The critical condition is that relinking is allowed
only when current tests actually assert the spec behavior with enough strength
to stand as evidence.

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`, I searched current
deliberations before review.

Relevant read-only DB results:

```text
TERM 16.C COUNT 2
  DELIB-0712 | POR Step 16.B methodology review: Phase 1.5 pattern does not generalize; 5-stream multi-remediation scope for 16.C | bridge/por-step16b-methodology-review-002.md
  DELIB-0713 | Owner Decisions: POR 16.C Scope and Stream Configuration | bridge/por-step16b-methodology-review-006.md

TERM SPEC-1585 COUNT 0
TERM SPEC-1586 COUNT 0
TERM SPEC-1587 COUNT 0
TERM SPEC-1615 COUNT 0
TERM Pipeline Observatory COUNT 1
TERM deploy pipeline COUNT 12
```

`DELIB-0713` remains the governing scope decision: run the four 16.C streams in
parallel and reconcile exact final counts through the umbrella.

## Evidence

The index entry for this document contains only the submitted NEW version:

```text
13: Document: por-step16c-stream-c-beta-triage
14: NEW: bridge/por-step16c-stream-c-beta-triage-001.md
```

The proposal correctly identifies the four original beta-prime specs at
`bridge/por-step16c-stream-c-beta-triage-001.md:29` through `:32`, and defines
the right terminal bucket model at `:57` through `:65`.

The missing historical files are absent from disk, while the current product
artifacts still exist:

```text
Test-Path tests/e2e/test_provider_pipeline_observatory.py -> False
Test-Path tests/integration/test_deploy_pipeline.py -> False
Test-Path scripts/deploy.py -> True
Test-Path scripts/deploy_pipeline.py -> True
```

`git log --all --follow --diff-filter=D --name-status --` returned no deletion
commit for either missing historical path:

```text
tests/e2e/test_provider_pipeline_observatory.py -> no output
tests/integration/test_deploy_pipeline.py -> no output
```

So the implementation should not depend on Git deletion history being
conclusive. The safer source of truth is the current DB row shape plus semantic
search over the current tree.

Read-only DB inspection shows the current rows have `test_file = NULL`; the
missing paths are in historical version 1 rows:

```text
SPEC-1585 TEST-2771 v2 test_file=None last_result=stale
SPEC-1585 TEST-2772 v2 test_file=None last_result=stale
SPEC-1586 TEST-2773 v2 test_file=None last_result=stale
SPEC-1586 TEST-2774 v2 test_file=None last_result=stale
SPEC-1587 TEST-2775 v2 test_file=None last_result=stale
SPEC-1587 TEST-2776 v2 test_file=None last_result=stale
SPEC-1587 TEST-2777 v2 test_file=None last_result=stale
SPEC-1615 TEST-2941 v2 test_file=None last_result=stale
```

The same read-only query found current spec versions and statuses:

```text
SPEC-1585 v2 implemented
SPEC-1586 v3 implemented
SPEC-1587 v3 implemented
SPEC-1615 v7 implemented
```

The Pipeline Observatory product surface is present:
- `admin/provider/pages/PipelineObservatory.tsx:3` identifies the page as
  covering `SPEC-1585..1587`.
- `admin/provider/pages/PipelineObservatory.tsx:159` starts the Traffic Flow
  tab implementation.
- `admin/provider/pages/PipelineObservatory.tsx:310` starts the Agent Metrics
  tab implementation.
- `admin/provider/pages/PipelineObservatory.tsx:406` starts the Tenant
  Comparison tab implementation.
- `admin/provider/pages/PipelineObservatory.tsx:779` through `:781` render the
  `Traffic Flow`, `Agent Metrics`, and `Tenant Comparison` tabs.

Current live E2E tests are candidate replacement evidence, but not automatically
sufficient:
- `tests/e2e_live/provider/test_operations_live.py:1225` through `:1258`
  exercise Traffic Flow.
- `tests/e2e_live/provider/test_operations_live.py:1261` through `:1291`
  exercise Agent Metrics.
- `tests/e2e_live/provider/test_operations_live.py:1294` through `:1345`
  exercise Tenant Comparison.
- Several of those tests return without assertion when data is unavailable,
  for example `tests/e2e_live/provider/test_operations_live.py:1239` through
  `:1240`, `:1249` through `:1250`, `:1289` through `:1291`, and `:1337`
  through `:1339`.

For `SPEC-1587`, the current product appears to cover sorting and table columns
but not the whole historical spec. The current page has a sort selector and
tenant table at `admin/provider/pages/PipelineObservatory.tsx:437` through
`:534`, but a targeted search for `CSV`, `Export`, `search`, `filter`, and
`TextInput` in `admin/provider/pages/PipelineObservatory.tsx` found only
sort-related matches. The current spec description still requires tier filter,
numeric filters, tenant text search, CSV export, and row drill-down.

For `SPEC-1615`, current behavior and tests are strong candidate evidence:
- `scripts/deploy_pipeline.py:2` through `:21` describe the SPEC-1615
  two-track autonomous deploy pipeline and success/failure exit codes.
- `scripts/deploy_pipeline.py:1264` through `:1273` define the non-interactive
  CLI contract.
- `scripts/deploy_pipeline.py:1312` through `:1440` wire the build, deploy,
  verification, staging, and production phases.
- `tests/unit/test_deploy_pipeline_production.py:1` through `:19` describe the
  canonical production deploy test matrix.

Targeted verification passed:

```text
python -m pytest tests/unit/test_deploy_pipeline_production.py -q --tb=short
30 passed in 41.71s
```

## Findings

### Finding 1: The row-count surface is eight current stale test rows, not four path repairs

Severity: medium.

The proposal says `groundtruth.db` writes are "test row path repairs (up to 4)"
at `bridge/por-step16c-stream-c-beta-triage-001.md:71`. Read-only DB evidence
shows eight current stale test rows across the four specs: two for SPEC-1585,
two for SPEC-1586, three for SPEC-1587, and one for SPEC-1615.

Risk/impact: if implementation updates one row per spec, it can leave stale
current tests behind and still appear to have handled all four specs by count.

Required action: the Stream C implementation and post-implementation report
must reconcile exact current test IDs `TEST-2771` through `TEST-2777` and
`TEST-2941`, plus exact spec IDs. Any row left stale/null must have an explicit
terminal reason.

### Finding 2: Existing Pipeline Observatory tests are candidates, not automatic relinks

Severity: medium.

The current live E2E file has tests for the three tabs, but some tests are
state-dependent and return without assertion when data is missing. That may be
acceptable for smoke coverage, but it is not automatically enough to prove the
historical spec assertions.

Risk/impact: blind relinking would convert stale evidence into weak or
non-assertive evidence, especially for tab internals that depend on live data.

Required action: before relinking SPEC-1585, SPEC-1586, or SPEC-1587 to
`tests/e2e_live/provider/test_operations_live.py`, Prime must document which
specific test functions cover which historical test IDs and why each test is
assertive enough. If a test can pass by returning early without checking the
behavior, either strengthen/create a test or classify the behavior as WI-needed.

### Finding 3: SPEC-1587 appears only partially live

Severity: medium.

Current code has sort selection and a tenant table, but I found no current page
evidence for CSV export, tenant text search, tier dropdown filter, numeric range
filters, or row drill-down. The historical SPEC-1587 description still requires
those behaviors.

Risk/impact: relinking SPEC-1587 as fully covered would overstate product and
test coverage. Retiring the whole spec would also be too broad if the sortable
tenant table remains live.

Required action: split the SPEC-1587 disposition in the post-implementation
logic: relink only the live-and-tested subset, and create hygiene WI(s), retire
obsolete clauses, or revise the spec record for the unsupported clauses with
clear rationale.

### Finding 4: Git history is not a reliable discriminator for this stream

Severity: low.

The proposal correctly starts with Git history search, but local history did
not expose deletion commits for either missing historical file. The current DB
already shows current rows with `test_file = NULL`, so this may be a KB row
versioning issue rather than a discoverable file deletion/move event.

Risk/impact: a script that treats missing Git history as enough reason to
retire or WI a spec could misclassify live behavior.

Required action: keep Git history as a diagnostic only. The terminal bucket
decision must be based on current product behavior, current test coverage, and
current DB row state.

## GO Conditions

1. Process the original Stream C set as exactly four specs and eight current
   stale test rows unless Stream A later supplies escalations.
2. For any relink, cite the replacement test file, class/function, command
   result when runnable, and a short coverage rationale tied to the historical
   test ID.
3. Do not relink to state-dependent live E2E tests unless the post-impl report
   explains why early-return paths do not weaken the evidence, or the tests are
   strengthened before relink.
4. Treat SPEC-1587 as partial until proven otherwise; unsupported filter,
   search, CSV export, range-filter, and drill-down clauses need WI/retirement/
   spec-revision handling.
5. If Stream A escalations are not available when Stream C begins, the post-impl
   report must clearly separate "original four beta-prime specs" from "later
   alpha-prime escalations" and must not claim umbrella completion until the
   umbrella reconciliation covers all escalations.

## Required Action Items

Prime may proceed with Stream C implementation under the conditions above.
The next review should verify exact ID-level reconciliation, not aggregate
counts alone.

## Decision Needed From Owner

None before implementation. Owner input may be needed later if Prime proposes
retiring or materially narrowing live Pipeline Observatory requirements rather
than creating hygiene work for missing behavior.
