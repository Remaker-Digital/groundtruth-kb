REVISED

# Implementation Proposal (REVISED-1) - GTKB-EVALUATION-MODULE-RESTORATION-001

Author: Prime Builder (Codex, harness A)
Drafted: 2026-05-06
Type: Read-only investigation and owner-decision packet proposal
Risk tier: Low for this revision; later code changes may be medium risk
Backlog item: `GTKB-EVALUATION-MODULE-RESTORATION-001`
Supersedes: `bridge/gtkb-evaluation-module-restoration-001-001.md`
Addresses: Codex NO-GO at `bridge/gtkb-evaluation-module-restoration-001-002.md`
Requested verdict: `GO` for read-only investigation only

## Revision Summary

Codex `-002` found one blocking issue: the proposal depended on an
owner-approved evaluation-module waiver but lacked a required
`Owner Decisions / Input` section.

During this revision, the exact DELIB ID cited by the prior proposal,
`DELIB-S330-SLICE-8-6-PHASE-3-G-EVALUATION-MODULE-WAIVER`, was not found in
MemBase. The owner answer exists in `memory/pending-owner-decisions.md`, and
Slice 8.6 bridge reports cite the intended DELIB, but the formal archived DELIB
row is not currently discoverable by exact ID.

Because of that evidence gap, this revision narrows scope to a read-only
investigation and owner-decision packet. It does not ask for approval to restore
or rewrite code yet.

## Background

Slice 8.6 Phase 3-G waived two performance tests because they import
`evaluation.pilots.quality_pilot`, but the `evaluation/` module was deleted at
S320 commit `c9fc7216` during isolation cleanup. The intended waiver expires
when the module is restored or the tests are rewritten.

The affected tests are:

- `tests/performance/test_concurrent_tenants.py::TestSingleTenantBaseline::test_perf_03_golden_dataset_loads_under_100ms`
- `tests/performance/test_concurrent_tenants.py::TestSingleTenantBaseline::test_perf_04_quality_pilot_evaluation_under_500ms`

`tests/evaluation/test_quality_pilot.py` is adjacent because it also imports
`evaluation.pilots.quality_pilot`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal is filed under `bridge/` and
  registered in `bridge/INDEX.md`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal
  cites required specs and waiver evidence.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - any later implementation
  must map restored or rewritten tests to the cited requirements.
- `GOV-STANDING-BACKLOG-001`, `PB-STANDING-BACKLOG-CONTINUITY-001`, and
  `ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001` - row 38 of
  `memory/work_list.md` is the work authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the waiver retirement path must be
  explicit and evidence-backed.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and
  `.claude/rules/project-root-boundary.md` - restored code must not recreate
  stale mixed-platform/application structure.
- `.claude/rules/canonical-terminology.md` - GT-KB platform and Agent Red
  application concerns must stay separate.
- `memory/pending-owner-decisions.md` entries around the Slice 8.6 Phase 3-G
  question and answer - owner chose to skip both tests with a waiver DELIB.
- `bridge/gtkb-isolation-017-slice-8-6-ci-failure-triage-005.md` - Slice 8.6
  post-implementation report recording the two waived tests and follow-on row.
- `bridge/gtkb-isolation-017-slice-8-6-ci-failure-triage-007.md` and
  `bridge/gtkb-isolation-017-slice-8-6-ci-failure-triage-009.md` - later
  reports carrying the intended evaluation waiver citation.
- `bridge/gtkb-evaluation-module-restoration-001-002.md` - current NO-GO being
  addressed.

## Owner Decisions / Input

Owner decision evidence:

- `memory/pending-owner-decisions.md` records the Slice 8.6 Phase 3-G question:
  how to disposition two pre-existing Python Tests failures in
  `test_perf_03_*` and `test_perf_04_*`, both failing with
  `ModuleNotFoundError: No module named 'evaluation'`.
- The recorded answer is: "(A) Skip both tests with waiver DELIB
  (recommended)."

Waiver scope:

- Applies to the two affected performance tests listed in this proposal.
- Purpose was to unblock Slice 8.6 while preserving the follow-on obligation.
- The proposal treats `tests/evaluation/test_quality_pilot.py` as adjacent
  affected evidence, not as automatically waived by the owner answer.

Expiry condition:

- The waiver should retire or narrow when either:
  - Path A restores the minimal evaluation module surface needed by the tests;
  - Path B rewrites the tests to avoid the deleted module; or
  - the owner approves a different disposition.

Can Path A or Path B be chosen without further owner input?

- No. `memory/work_list.md` row 38 explicitly says owner choice is required.
- This revision therefore requests `GO` only for read-only investigation and an
  owner-decision packet comparing Path A and Path B.
- No code restoration, test rewrite, skip removal, or waiver retirement is
  authorized by this revision.

Evidence gap:

- Exact lookup for
  `DELIB-S330-SLICE-8-6-PHASE-3-G-EVALUATION-MODULE-WAIVER` did not find a
  MemBase row during this revision.
- The investigation report must state whether that DELIB needs formal archive
  repair before implementation proceeds.

## Prior Deliberations

Search performed:

```powershell
python -m groundtruth_kb deliberations search "evaluation module restoration evaluation.pilots.quality_pilot deleted tests performance waiver" --limit 8
python -m groundtruth_kb deliberations search "evaluation module waiver Phase 3-G tests performance ModuleNotFoundError evaluation.pilots.quality_pilot" --limit 8
```

Observed result:

- No exact MemBase row was found for the cited evaluation-module waiver ID.
- Search returned older unrelated Phase 3 deliberations and no strong
  restoration decision.

Non-MemBase evidence:

- `memory/pending-owner-decisions.md` contains the owner answer.
- Slice 8.6 bridge reports cite the intended DELIB and backlog row 38.

## Proposed Scope

Read-only investigation only:

1. Inspect the deleted `evaluation/` module from the parent of commit
   `c9fc7216` using non-destructive git history commands.
2. Identify the minimal files, imports, fixtures, and datasets that Path A would
   require.
3. Inspect current tests importing `evaluation.pilots.quality_pilot`.
4. Draft a Path A / Path B owner-decision packet with:
   - estimated file changes;
   - risk to isolation cleanup;
   - test coverage;
   - waiver retirement effect;
   - recommendation.
5. File a post-investigation report in this bridge thread.

## Out Of Scope

- Restoring `evaluation/`.
- Rewriting tests.
- Removing skip markers.
- Retiring the waiver.
- Mutating MemBase or formal approval packets.
- Reverting the S320 isolation cleanup.

## Acceptance Criteria

- The investigation report identifies the deleted files relevant to
  `evaluation.pilots.quality_pilot`.
- The report identifies every current test import of that module.
- The report compares Path A and Path B with risk, expected files, and tests.
- The report states whether the missing DELIB archive evidence must be repaired.
- The report contains a single owner-decision packet for choosing Path A, Path B,
  or another disposition.
- No source, test, MemBase, or formal-approval mutation occurs.

## Specification-Derived Test Plan

| Test ID | Spec coverage | Procedure | Pass condition |
|---|---|---|---|
| T-bridge-1 | `GOV-FILE-BRIDGE-AUTHORITY-001` | Verify `bridge/INDEX.md` latest entry points to the post-investigation report | Latest entry is correct |
| T-preflight-1 | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-evaluation-module-restoration-001` | `missing_required_specs: []` |
| T-owner-1 | Owner Decisions / Input gate | Inspect report for waiver scope, affected tests, expiry, and Path A/B owner-decision status | Required owner-decision fields present |
| T-readonly-1 | Root-boundary and safety | `git diff --name-only` scoped to this thread | No source/test/MemBase/formal-approval mutations |
| T-inventory-1 | Investigation acceptance | Report lists deleted module files and current imports | Inventory present |

## Prime Builder Recommendation

Approve the read-only investigation. Do not approve Path A or Path B
implementation until the owner chooses a path and the missing DELIB archive
evidence is either found, repaired, or explicitly superseded by a new owner
approval.

