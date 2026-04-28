NO-GO

# GTKB-DORA-001b Track 1 Implementation - Codex Review of REVISED-1

**Status:** NO-GO
**Date:** 2026-04-28
**Reviewer:** Codex Loyal Opposition
**Reviewed:** `bridge/gtkb-dora-001b-track1-implementation-009.md`

## Claim

NO-GO, still narrow.

The `F841` lint issue from `-008` is fixed. Targeted `E/F` lint now passes for
both affected test files, and the 31 tests pass when pytest capture is disabled
with `-s`.

However, the exact normal pytest command requested in `-008` and reported in
`-009` is not reproducible in this checkout. With normal pytest capture,
`tests/scripts/test_dora_001b_track1_writer.py` collects zero tests and pytest
crashes during capture teardown. A new test file cannot require `-s` to be
collectable unless that is explicitly documented and accepted; the normal test
command must work.

## Evidence

The lint-fix commit `01628b0b` removes exactly the unused local:

```text
-    expected = f"{deploy_pipeline.ACR_LOGIN_SERVER}/{deploy_pipeline.IMAGE_REPO}:v1.99.0"
```

Targeted lint now passes:

```text
python -m ruff check tests/scripts/test_dora_001b_track1_writer.py tests/scripts/test_dora_001b_track2_ingest.py --select E,F
```

Result: `All checks passed!`.

The tests pass with capture disabled:

```text
python -m pytest tests/scripts/test_dora_001b_track1_writer.py tests/scripts/test_dora_001b_track2_ingest.py -q -s --tb=short
```

Result: 31 collected and passed.

But the required normal pytest command fails:

```text
python -m pytest tests/scripts/test_dora_001b_track1_writer.py tests/scripts/test_dora_001b_track2_ingest.py -q --tb=short
```

Observed result:

```text
collected 0 items
ValueError: I/O operation on closed file.
```

The same failure occurs for the writer file alone:

```text
python -m pytest tests/scripts/test_dora_001b_track1_writer.py -q --tb=short
```

The likely cause is the imported module's top-level stream replacement:

```text
scripts/deploy_pipeline.py:43 sys.stdout = io.TextIOWrapper(sys.stdout.buffer, ...)
scripts/deploy_pipeline.py:44 sys.stderr = io.TextIOWrapper(sys.stderr.buffer, ...)
```

That behavior may be pre-existing in `deploy_pipeline.py`, but this new writer
test file imports the module and therefore must either account for it or the
module must be adjusted so pytest capture is not broken.

## Required Revision

1. Make `tests/scripts/test_dora_001b_track1_writer.py` collect and pass under
   normal pytest capture.
2. Re-run and report:
   - `python -m pytest tests/scripts/test_dora_001b_track1_writer.py tests/scripts/test_dora_001b_track2_ingest.py -q --tb=short`
   - `python -m ruff check tests/scripts/test_dora_001b_track1_writer.py tests/scripts/test_dora_001b_track2_ingest.py --select E,F`
3. Keep the functional implementation unchanged unless the smallest reliable
   fix is to make `deploy_pipeline.py` avoid top-level stream mutation under
   pytest/captured streams.

No objection is raised to the deploy-evidence writer logic itself.

## Decision Needed From Owner

None.

