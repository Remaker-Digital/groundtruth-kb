# Implementation Proposal: WI-3142 Narrow conftest.py Credential-Scan Exclusion

**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-11
**Session:** S280
**Work Item:** WI-3142
**Priority:** P2

---

## 1. Problem

`.claude/hooks/credential-scan.py` excludes ALL of `tests/conftest.py` from
credential scanning (line 105). This creates a fail-open blind spot — any
hardcoded credential accidentally added to conftest.py would pass undetected.

The exclusion exists because conftest.py contains 5 intentional fake-key
constants at lines 169-180:
- `TEST_API_KEY_STARTER = "arsk_test_starter_key_001"`
- `TEST_API_KEY_PROFESSIONAL = "arsk_test_pro_key_002"`
- `TEST_API_KEY_ENTERPRISE = "arsk_test_ent_key_003"`
- `TEST_SPA_KEY = "ar_spa_plat_test_spa_key_001"`
- `TEST_WIDGET_KEY = "pk_live_abcd1234efgh_5678ijkl9012mnop"`

## 2. Proposed Fix

Replace the blanket file exclusion with a content-level allowlist for known
fake-key prefixes. The scanner should:

1. Remove `re.compile(r'tests[/\\]conftest\.py$')` from `_EXCLUDED_PATHS`
2. Add a `_FAKE_KEY_ALLOWLIST` of regex patterns matching known test prefixes
3. In `_scan_content()`, filter out matches that hit allowlisted fake-key patterns

```python
_FAKE_KEY_ALLOWLIST = [
    re.compile(r'arsk_test_'),        # Test API keys
    re.compile(r'ar_spa_plat_test_'), # Test SPA keys
    re.compile(r'pk_live_abcd1234'),  # Test widget key (deterministic fake)
]
```

When the API key scanner finds a match, check if it matches any allowlisted
pattern. If so, skip it. This keeps the rest of conftest.py in the scan
surface while permitting the known fake constants.

## 3. Files Changed

| File | Change |
|------|--------|
| `.claude/hooks/credential-scan.py` | Remove conftest exclusion, add allowlist filtering |

## 4. Test Plan

Manual verification:
1. Edit conftest.py to add a real-looking credential → scanner should BLOCK
2. Edit conftest.py to modify a fake-key constant → scanner should ALLOW
3. Edit any other file with `arsk_test_` prefix → scanner should still BLOCK
   (allowlist only applies to the content pattern, not file-level exclusion)

## 5. Review Questions for Codex

1. Should the allowlist also cover `tests/multi_tenant/test_middleware_pipeline.py`
   (which has its own blanket exclusion at line 106)?
2. Should the fake-key allowlist be scoped to specific file paths, or is
   content-level filtering sufficient?
