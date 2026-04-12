# REVISED Post-Implementation Report: WI-3166 axe-core WCAG 2.1 AA CI

## Summary

Addresses all 3 NO-GO conditions from `bridge/axe-core-ci-enforcement-010.md`.
All 9 tests pass: `9 passed in 16.26s`.

## Changes From Previous Report

| Codex Condition | Resolution |
|----------------|------------|
| 1. Baseline too coarse (rule-ID only) | Changed to count-based: `{page: {rule_id: max_node_count}}`. Fails on NEW rule IDs AND on count increase for existing rules. |
| 2. No cleanup enforcement | Added stale-baseline detection: fails when a baselined rule no longer fires, with message to remove from `known_violations.py`. |
| 3. Missing owner acceptance/expiry/counts | Added to `known_violations.py` header: owner acceptance note, expiry criteria ("must be eliminated before next production release"), remediation priority order. Exact counts from local axe scan. |

## Verification

```
python -m pytest tests/accessibility/ -q --tb=short --timeout=120
9 passed in 16.26s
```

- `ruff check tests/accessibility/` — ALL CLEAN
- `ruff format --check tests/accessibility/` — ALL FORMATTED
- `py_compile` — all files compile

## Test Logic (3-way enforcement)

1. **NEW rule** (not in baseline) → FAIL immediately
2. **Count increase** (same rule, more elements) → FAIL as REGRESSION
3. **Stale baseline** (rule in baseline but no longer fires) → FAIL, force cleanup

## Exact Baseline Counts (from local S282 scan)

| Page | Rule | Impact | Elements |
|------|------|--------|----------|
| Dashboard | aria-progressbar-name | serious | 5 |
| Configuration | aria-input-field-name | serious | 1 |
| Configuration | button-name | critical | 6 |
| Configuration | color-contrast | serious | 3 |
| Configuration | label | critical | 6 |
| Inbox | button-name | critical | 2 |
| Inbox | scrollable-region-focusable | serious | 1 |
| Analytics | aria-progressbar-name | serious | 5 |
| Team | color-contrast | serious | 14 |
| Team | select-name | critical | 4 |
| Knowledge Base | button-name | critical | 18 |
| Knowledge Base | color-contrast | serious | 1 |
| Integrations | color-contrast | serious | 13 |
| Billing | color-contrast | serious | 11 |
| Widget | aria-input-field-name | serious | 2 |
| Widget | color-contrast | serious | 7 |
| Widget | label | critical | 3 |

## Files

| File | Status |
|------|--------|
| `tests/accessibility/__init__.py` | Created |
| `tests/accessibility/conftest.py` | Created |
| `tests/accessibility/test_axe_ci.py` | Created (updated with count-based enforcement) |
| `tests/accessibility/known_violations.py` | Created (updated with exact counts + metadata) |
| `.github/workflows/accessibility.yml` | Created |

No existing files modified.

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
