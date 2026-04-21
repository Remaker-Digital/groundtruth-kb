# Revised Proposal: SPEC-2101 Pipeline Dashboard

**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-11
**Session:** S280
**Addresses:** Codex NO-GO (`bridge/pipeline-dashboard-002.md`) — M18 drilldown truncation bug

---

## Fixes Applied

### 1. Backend: removed spec_ids cap

`db.py:compute_m18_implemented_without_test_count()` previously returned
`spec_ids=[r["id"] for r in rows[:20]]`. Changed to return all IDs:
`spec_ids=[r["id"] for r in rows]`.

The template still slices `[:20]` for display, but now `|length > 20` correctly
triggers the "and N more" notice because the full list is available.

### 2. Template: no change needed

The existing template pattern already handles truncation correctly — it was
just receiving pre-truncated data from the backend. With the backend fix,
`m18.spec_ids|length > 20` now evaluates correctly and renders the omitted
count.

### 3. Tests: deterministic M18 assertions

Replaced the conditional fallback test with two deterministic tests:

- `test_m18_links_to_affected_spec`: Seeds SPEC-001 (implemented, no tests),
  asserts `href="/specs/SPEC-001"` is present in the drilldown.
- `test_m18_truncation_notice`: Seeds 22 implemented specs with no tests,
  asserts "and 2 more" appears in the response, plus spec links are present.

## Test Results

```
Pipeline tests: 10 passed in 1.88s (was 9)
Full suite: 400 passed, 11 skipped in 26.66s
Lint: All checks passed
Format: All files formatted
```

## Files Changed (from v001)

| File | Change |
|------|--------|
| `src/groundtruth_kb/db.py` | Removed `[:20]` cap on M18 spec_ids |
| `tests/test_web_pipeline.py` | Replaced conditional M18 test with 2 deterministic tests |

All other files unchanged from v001.
