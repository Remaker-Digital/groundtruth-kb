# POR Step 16.C Stream C — β' Broken-Path Triage (4 specs)

**Status:** NEW (proposal for Codex review)
**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-16
**Session:** S297
**Bridge thread:** por-step16c-stream-c-beta-triage
**Umbrella:** `bridge/por-step16c-implemented-untested-remediation-002.md` (GO)

## Prior Deliberations

- `DELIB-0713` (S297): Owner decisions on 16.C scope.
- `DELIB-0712` (S297): Methodology review established β' as specs whose
  historical `test_file` no longer exists on disk.

## Objective

Triage the 4 β' specs whose linked test files were deleted. Repair the
linkage (if the test moved), create a replacement test, or retire the spec.
Stream C will also absorb any A1/A3-fail escalations from Stream A (tests
that fail when re-run — bit-rot).

## Scope — All 4 β' Specs + Stream A Escalations

### Original β' set

| Spec | Title | Missing file |
|------|-------|-------------|
| SPEC-1585 | Pipeline Observatory: Traffic Flow visual topology tab | `tests/e2e/test_provider_pipeline_observatory.py` |
| SPEC-1586 | Pipeline Observatory: Agent Metrics performance cards tab | `tests/e2e/test_provider_pipeline_observatory.py` |
| SPEC-1587 | Pipeline Observatory: Tenant Comparison sortable/filterable table | `tests/e2e/test_provider_pipeline_observatory.py` |
| SPEC-1615 | Automated build/deploy pipeline — scripted, autonomous | `tests/integration/test_deploy_pipeline.py` |

**Observation:** 3 of 4 β' specs share the same missing file
(`test_provider_pipeline_observatory.py`). That file was likely deleted
in a single cleanup; all 3 specs can be resolved together if we either
restore the file or retire the 3 specs together.

### Stream A escalations (TBD at Stream A completion)

Any α' spec whose test fails when refreshed (bit-rot) is forwarded to
Stream C. Stream A's post-impl report lists these with file:line evidence.
Stream C's post-impl absorbs them and reports final disposition.

## Triage Method (per spec)

For each β' spec `S` with missing `test_file` path `P`:

1. **Git history search**: `git log --all --follow --diff-filter=D -- P`
   to find when `P` was deleted and whether it moved.
2. **Semantic search**: grep for the test function name in current test
   tree; the test may have been moved to another file.
3. **Spec-behavior check**: is `S`'s described behavior still part of the
   product? (For SPEC-1615 "Automated build/deploy pipeline", for instance,
   we actually have a `deploy.py` — test may have been retired, behavior
   persists.)
4. **Classify**:
   - **(I) Test moved — relink**: update the test row's `test_file` path
     and re-run.
   - **(II) Test deleted, behavior still tested elsewhere — relink**:
     bind spec to the new test.
   - **(III) Test deleted, behavior obsolete — retire spec**: retire `S`
     with rationale.
   - **(IV) Test deleted, behavior live but untested — create hygiene WI**:
     behavior shipped, no test covers it. Treat like Stream D.

## Files Changed

| File | Change Type | Description |
|------|------------|-------------|
| `groundtruth.db` | Write | Test row path repairs (up to 4) + any spec retirements + any hygiene WIs |
| Impl script | New | `independent-progress-assessments/spec-hygiene/scripts/stream_c_beta_triage.py` |
| Triage log | New | Per-spec decision in post-impl report |

## Risks

- **Low:** 4 specs + some A1/A3 escalations is a small manageable set.
- **Medium:** Git history search may be inconclusive. Mitigation: fallback
  to path (III) retire or (IV) create WI.
- **Low:** Stream A escalation count is unknowable until Stream A completes;
  Stream C may need to refresh its scope once A is VERIFIED.

## Exit Criteria

1. All 4 β' specs have a terminal bucket: relinked / retired / WI-created.
2. All Stream A escalations absorbed with same terminal-bucket assignments.
3. Post-impl report covers every original β' spec + every escalated α' spec.

## Reconciliation Against Umbrella

Umbrella requires: "Stream C: Final count = 4 β' + α'-escalations, all with
terminal decisions." This proposal meets that requirement, pending the
α'-escalation count from Stream A.

## Dependency on Stream A

Stream C's scope expands at runtime based on Stream A's escalations. Two
execution options:

- **Sequential: Wait for Stream A VERIFIED** before Stream C begins
  implementation. Simpler reconciliation.
- **Parallel with re-scope**: Stream C does the original 4 β' specs first,
  then absorbs any Stream A escalations in a post-impl amendment.

Per owner decision on parallel execution (DELIB-0713 Decision 3), the
parallel path is preferred. Stream C's post-impl report will note "final
scope" after Stream A lands.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
