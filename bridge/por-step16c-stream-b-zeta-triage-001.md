# POR Step 16.C Stream B — ζ' Test-ID Reassignment Triage (4 specs)

**Status:** NEW (proposal for Codex review)
**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-16
**Session:** S297
**Bridge thread:** por-step16c-stream-b-zeta-triage
**Umbrella:** `bridge/por-step16c-implemented-untested-remediation-002.md` (GO)

## Prior Deliberations

- `DELIB-0713` (S297): Owner decisions on 16.C scope.
- `DELIB-0712` (S297): Methodology review established ζ' as a distinct category.

## Objective

Triage the 4 ζ' specs whose test rows had their `spec_id` rewritten to point
at unrelated specs (SPEC-1771 or SPEC-1874). Determine per spec whether this
was legitimate refactoring (subsumed) or data corruption (relink).

## Scope — All 4 ζ' Specs

| Spec | Title | Reassigned to | Test file | Rows | Hypothesis |
|------|-------|---------------|-----------|-----:|------------|
| SPEC-1841 | Deployment modal should pre-fill next version | SPEC-1771 (Integration Framework Admin API) | `tests/quality_metrics/test_backfill_untested.py` | 10 | Corruption (titles unrelated) |
| SPEC-1869 | Intent Confidence Threshold | SPEC-1874 (Langfuse Trace Exporter) | `tests/chat/pipeline/test_intent_router.py` | 7 | Corruption (titles unrelated) |
| SPEC-1870 | Source Attribution Display | SPEC-1874 | `tests/chat/test_source_attribution.py` | 4 | Corruption |
| SPEC-1871 | Response Tone Presets | SPEC-1874 | `tests/multi_tenant/test_tone_presets.py` | 7 | Corruption |

**All 4 test files exist on disk.** The test *code* still covers the ζ'
specs' behavior — only the DB `spec_id` metadata is wrong.

## Triage Method (per spec)

For each ζ' spec `S` with reassigned test_id set `T = {t1, t2, ...}`:

1. **Open the test file** and read the function bodies for tests listed in
   `T`. Compare against `S.title` and `S.description`.
2. **Classify**:
   - **(b) Data corruption (relink)**: The test code clearly covers `S`'s
     behavior, not `now_owned_by`'s. Action: create new test rows with
     `spec_id=S.id`, preserving `test_file` and the test function name.
     Run the test → if pass, `last_result='pass'`; else escalate.
   - **(a) Legitimate refactor (retire)**: The test code actually covers
     `now_owned_by`'s behavior; `S` is subsumed. Action: retire `S` with
     forwarding pointer to `now_owned_by` in `change_reason`.
   - **(d) Ambiguous (needs owner)**: Can't confidently assign either way.
     Escalate to owner via question.
3. **Record** the decision in the post-impl triage log.

## Default Remediation Bias

Per the code-review insight above (unrelated titles suggest corruption),
the default path is **(b) relink**. `(a) retire` requires explicit evidence
that `S` is truly subsumed. Owner involvement is only sought for ambiguous
cases.

## Schema Invariant — Spin-off Ancillary

The 16.B review proposed a schema constraint: forbid `spec_id` changes on
test rows (force new `test_id` instead). **This constraint would have
prevented the ζ' corruption pattern.**

Stream B proposal does NOT introduce this constraint (out of scope), but
the post-impl report will spin off a WI for the schema work so it's
tracked for a future session.

## Files Changed

| File | Change Type | Description |
|------|------------|-------------|
| `groundtruth.db` | Write | Up to 4 new spec versions (if any retired), up to ~28 new test rows (if all relinked) |
| Impl script | New | `independent-progress-assessments/spec-hygiene/scripts/stream_b_zeta_triage.py` |
| Triage log | New | Per-spec decision log in post-impl report |

## Risks

- **Low:** 4 specs is small enough for per-spec manual inspection.
- **Medium:** Re-running tests may fail (code drift since original pass).
  Mitigation: relink still proceeds (test now covers spec); test row
  `last_result` reflects actual state; spec gains "tested" status only
  if test passes. If test fails, escalate to Stream C for repair.

## Exit Criteria

1. All 4 ζ' specs have a terminal bucket:
   - `relinked_pass` (test relinked and passes)
   - `relinked_fail_escalated_to_c` (relink done; test fails; Stream C)
   - `retired_subsumed` (retire with forwarding pointer)
   - `owner_pending` (escalated — should be 0 or near-0)
2. Post-impl report includes per-spec triage evidence (code excerpts +
   rationale).
3. Ancillary WI spun off for schema invariant proposal.

## Reconciliation Against Umbrella

Umbrella requires: "Stream B: 4 ζ' specs have a terminal decision (re-linked,
new test, or retired)." This proposal produces exactly that.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
