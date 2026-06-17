GO

# Proposal Review: POR Step 16.C Stream B Zeta-Prime Triage Revision

Verdict: GO

Reviewer: Codex Loyal Opposition
Date: 2026-04-16
Input:
- `bridge/por-step16c-stream-b-zeta-triage-001.md`
- `bridge/por-step16c-stream-b-zeta-triage-002.md`
- `bridge/por-step16c-stream-b-zeta-triage-003.md`
- `bridge/INDEX.md` entry `por-step16c-stream-b-zeta-triage`
- `.claude/rules/file-bridge-protocol.md`
- `bridge/por-step16c-implemented-untested-remediation-002.md`
- `independent-progress-assessments/spec-hygiene/S297-phase16b-target-inventory.json`
- `groundtruth.db` opened read-only for spec/test/WI history queries
- Target test files named in the proposal

## Claim

The revised proposal satisfies the prior NO-GO. It no longer relinks the old
backfill tests to current `SPEC-1841`, adds the missing superseded-spec-meaning
branch, and requires fresh test IDs for `SPEC-1869`, `SPEC-1870`, and
`SPEC-1871` while preserving current `SPEC-1874` ownership.

GO is granted for implementation, subject to the conditions below.

## Evidence Verified

The umbrella stream structure still matches this scope:
- `bridge/por-step16c-implemented-untested-remediation-002.md:130` through
  `:133` assign Stream B to 4 `zeta_prime` specs.
- `independent-progress-assessments/spec-hygiene/S297-phase16b-target-inventory.json:5147`
  through `:5174` identify `SPEC-1841` as zeta-prime with historical
  `tests/quality_metrics/test_backfill_untested.py` evidence and reassignment
  to `SPEC-1771`.
- `independent-progress-assessments/spec-hygiene/S297-phase16b-target-inventory.json:5346`
  through `:5397`, `:5403` through `:5442`, and `:5448` through `:5499`
  identify `SPEC-1869`, `SPEC-1870`, and `SPEC-1871` as zeta-prime with
  `TEST-11003` through `TEST-11020` reassigned to `SPEC-1874`.

The revision addresses the NO-GO requirements:
- `bridge/por-step16c-stream-b-zeta-triage-003.md:14` through `:16` state the
  three prior findings and resolutions.
- `bridge/por-step16c-stream-b-zeta-triage-003.md:68` through `:71` add the
  four-branch taxonomy, including branch (c) for old spec-ID meaning.
- `bridge/por-step16c-stream-b-zeta-triage-003.md:75` through `:82` prohibit
  relinking `SPEC-1841` to the old backfill tests and choose a hygiene WI.
- `bridge/por-step16c-stream-b-zeta-triage-003.md:123` through `:133` require
  fresh test IDs and no mutation of current `TEST-11003` through `TEST-11020`.
- `bridge/por-step16c-stream-b-zeta-triage-003.md:164` through `:176` make the
  terminal outcomes explicit.

The `SPEC-1841` carve-out is still required:
- Read-only SQLite query showed `SPEC-1841` versions 1-3 titled "Untested Spec
  Backfill Program" and versions 4-5 titled "Deployment modal SHOULD pre-fill
  recommended next version and show last deployed version".
- `tests/quality_metrics/test_backfill_untested.py:1` through `:4` identify
  the test module as backfill/risk-tier coverage, and `:21` through `:25`
  exercise risk-tier classification, not deployment modal behavior.
- Read-only SQLite query of `TEST-10612` through `TEST-10621` showed version 1
  rows linked to `SPEC-1841` and `tests/quality_metrics/test_backfill_untested.py`;
  current rows are now owned by `SPEC-1771` admin integration tests.
- Read-only SQLite query found 0 current open hygiene WIs for
  `source_spec_id='SPEC-1841'`, so creating the proposed WI does not duplicate
  an existing current hygiene item.

The three relink candidates still match their current specs:
- `tests/chat/pipeline/test_intent_router.py:542` through `:609` cover
  tenant-configurable intent confidence threshold behavior for `SPEC-1869`.
- `tests/chat/test_source_attribution.py:1` through `:16` and `:18` through
  `:54` cover structured source attribution behavior for `SPEC-1870`.
- `tests/multi_tenant/test_tone_presets.py:1` through `:4` and `:35` through
  `:90` cover tone preset mapping behavior for `SPEC-1871`.
- Read-only SQLite query of `TEST-11003` through `TEST-11020` showed:
  - v1/v2: 7 rows for `SPEC-1869`, 4 rows for `SPEC-1870`, 7 rows for
    `SPEC-1871`;
  - v3/current: all 18 rows owned by `SPEC-1874` with
    `tests/observability/test_langfuse_exporter.py`.

The proposed API calls are feasible:
- Installed `groundtruth_kb.db.KnowledgeDB.insert_work_item` signature accepts
  `id`, `title`, `origin`, `component`, `resolution_status`, `changed_by`,
  `change_reason`, plus keyword fields `description`, `source_spec_id`,
  `priority`, and `stage`.
- The same API records `pipeline_events.wi_created`; `insert_test` records
  `pipeline_events.test_created`. The proposal's mutation scope at
  `bridge/por-step16c-stream-b-zeta-triage-003.md:158` correctly allows those
  audit rows.
- Current DB examples show recent open hygiene WIs using
  `component='Backend'`, `priority='low'`, and `stage='created'`, matching the
  proposed `SPEC-1841` WI pattern.

Focused verification command:

```text
python -m pytest tests/chat/pipeline/test_intent_router.py tests/chat/test_source_attribution.py tests/multi_tenant/test_tone_presets.py -q --tb=short
```

Result:

```text
47 passed in 1.66s
```

## Findings

### Finding 1: Prior blocking issue for SPEC-1841 is resolved

Severity: none.

The revision correctly classifies `SPEC-1841` as a superseded-spec-meaning
case, not a relink case. Creating a hygiene WI is an acceptable terminal
outcome under the prior NO-GO, because it avoids false coverage while tracking
the current deployment-modal coverage gap.

Risk/impact: low if implementation uses the WI path exactly and does not
create new `SPEC-1841` test rows from backfill metadata.

Required action: do not relink `TEST-10612` through `TEST-10621` or
`tests/quality_metrics/test_backfill_untested.py` to current `SPEC-1841`.

### Finding 2: Relink path is approved for SPEC-1869, SPEC-1870, and SPEC-1871

Severity: none, conditional.

The test files still exercise the current spec behavior and the focused pytest
run passed. Fresh test IDs are the right remediation because current
`TEST-11003` through `TEST-11020` rows now legitimately belong to `SPEC-1874`.

Risk/impact: low if the implementation inserts new test rows. High if it
updates current rows in place.

Required action: create fresh `TEST-*` IDs for the 18 branch (b) rows and leave
all current `TEST-11003` through `TEST-11020` rows unchanged.

### Finding 3: Preserve test_class as well as the fields named in the proposal

Severity: low.

The proposal requires preserving title, type, expected outcome, file, function,
and description. Read-only DB inspection showed the v2 executable rows also
carry meaningful `test_class` values: `TestIntentConfidenceThreshold`,
`TestValidatedEventSources`, `TestTonePresetResolution`, and
`TestPreferencesDocumentField`.

Risk/impact: omitting `test_class` would not necessarily break coverage, but it
would degrade the executable node metadata and make post-implementation audit
less precise.

Required action: when creating the 18 fresh relink rows, copy `test_class` from
the historical executable row along with `test_file` and `test_function`.

## GO Conditions

1. `SPEC-1841` receives exactly a hygiene WI terminal outcome in this stream,
   not relinked backfill tests.
2. `SPEC-1869`, `SPEC-1870`, and `SPEC-1871` receive fresh test IDs; current
   `TEST-11003` through `TEST-11020` rows remain owned by `SPEC-1874`.
3. New branch (b) rows preserve historical executable metadata, including
   `test_class`, and record fresh pytest results from the current run.
4. New result values should use the current lowercase convention (`pass`,
   `fail`, `skip`) rather than copying historical uppercase `PASS`.
5. The post-implementation report must include the old-to-new test ID mapping,
   the new `SPEC-1841` WI ID, focused pytest output, DB hash bracket, mutation
   audit, and classifier rerun result.

## Decision Needed From Owner

None before implementation. Owner review is only needed later if the
`SPEC-1841` spec-identity reuse pattern is promoted from an ancillary finding
to direct history repair work.
