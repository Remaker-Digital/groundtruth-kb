VERIFIED

# GTKB-WRAPUP-ENHANCEMENTS Slice 1 Stage 1 Post-Implementation Verification

**Date:** 2026-04-26
**Reviewed report:** `bridge/gtkb-wrapup-enhancements-slice1-013.md`
**Implementation commit:** `4bf9360c`
**Mode:** Post-implementation verification
**Decision:** VERIFIED

## Verdict

VERIFIED. Stage 1 implements the allowlist mechanism without adding production baseline entries, keeps current W2 error behavior for empty/absent allowlists, and keeps live performance testing out of the release candidate gate.

## Evidence

Targeted command run:

```powershell
python -m pytest tests/scripts/test_wrap_scan_hygiene_skip_dirs.py tests/scripts/test_wrap_scan_consistency_allowlist.py -q --tb=short
```

Result: PASS, 12 tests passed in 0.29s.

Additional perf command run:

```powershell
python -m pytest tests/perf/test_wrap_scan_hygiene_perf.py -q --tb=short
```

Result: PASS, 1 test passed in 4.50s.

Implementation checks:

- `.groundtruth/wrap-scan/historical-phantoms.toml` is tracked and contains `phantoms = []`.
- `scripts/release_candidate_gate.py` includes `tests/scripts/test_wrap_scan_hygiene_skip_dirs.py` and `tests/scripts/test_wrap_scan_consistency_allowlist.py`.
- `scripts/release_candidate_gate.py` does not include `tests/perf/test_wrap_scan_hygiene_perf.py`.
- `pyproject.toml` registers the `perf` marker.
- The W2 allowlist loader raises on malformed TOML or wrong schema version.

## Notes

The pre-existing old-root pattern bug fix is acceptable in this commit because the fixture tests directly exposed it and the change is tightly coupled to making W1's hardcoded-root check meaningful.

Stage 2 still must return through the bridge before any production historical phantom entries are added to the allowlist or demoted to `info`.

## Verification

I inspected the implementation, checked the commit stat/tracked files, and ran the targeted fixture tests plus the separated perf test.

## Decision Needed From Owner

None.

