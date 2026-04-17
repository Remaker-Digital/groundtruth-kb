# Post-Implementation Report: WI-3142 Credential Scan Narrowing

**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-11
**Session:** S281
**Implements:** bridge/credential-scan-narrowing-011.md (Codex GO: bridge/credential-scan-narrowing-012.md)

---

## Summary

Replaced blanket test-file exclusions in the credential scanner with
value-scoped suppression. Unified key detection now covers quoted,
assignment-form, and bare contexts with hyphen-aware character classes and
negative-lookahead boundaries. All remediation actions completed.

## Changes Made

### 1. `.claude/hooks/credential-scan.py` (rewritten)

**Removed:**
- Blanket path exclusions for `tests/conftest.py` and
  `tests/multi_tenant/test_middleware_pipeline.py` (lines 103-106 of old file)
- Old narrow `_API_KEY_PATTERNS` (quoted-only, no hyphens, lines 48-51)

**Added:**
- Unified `_AR_KEY_PATTERNS` with 3 patterns covering `ar_*`, `arsk_*`, and
  `pk_live_*` families. Character class `[A-Za-z0-9_-]` supports
  `token_urlsafe` output. Negative lookahead `(?![A-Za-z0-9_-])` catches keys
  followed by any non-key character (period, semicolon, parens, etc.)
- `_FIXTURE_VALUES` frozenset: 52 reviewed fixture values
- `_DOCSTRING_EXAMPLE_VALUES` frozenset: 5 reviewed source example values
- `_FIXTURE_FILE_PATTERNS`: tests/ and scripts/test_* paths
- `_DOCSTRING_EXAMPLE_PATHS`: auth.py and admin_apikey_api.py paths
- `_is_fixture_suppressed()`: value+path scoped suppression
- `_scan_content()` now takes `file_path` parameter for suppression checks
- Finding deduplication in `main()`
- Path exclusion for `bridge/` (proposals reference key patterns)
- Path exclusion for `tests/hooks/test_credential_scan.py` (test file
  intentionally contains non-fixture keys for detection verification)

### 2. `evaluation/run_quality_live.py`

Replaced hardcoded widget key fallback with mandatory env var:
```python
# Before: os.getenv("PREVIEW_WIDGET_KEY", "pk_live_c79a2bd0_960a9c23")
# After:
WIDGET_KEY = os.getenv("PREVIEW_WIDGET_KEY")
if not WIDGET_KEY:
    raise RuntimeError("PREVIEW_WIDGET_KEY environment variable is required")
```

### 3. `evaluation/seed_quality_kb.py`

Replaced hardcoded API key fallback with mandatory env var:
```python
# Before: os.environ.get("QUALITY_API_KEY", "ar_user_rema_uB7s...")
# After:
API_KEY = os.environ.get("QUALITY_API_KEY")
if not API_KEY:
    raise RuntimeError("QUALITY_API_KEY environment variable is required")
```

### 4. `scripts/archive/s157_kb_update.py`

Replaced staging key with redaction placeholder:
```
# Before: Staging key: ar_spa_plat_mdbq-Sm3v...
# After: Staging key: [REDACTED -- stored in Key Vault as SPA-PLATFORM-ADMIN-KEY].
```

### 5. `scripts/deploy/production-gateway-generated.yaml`

Replaced AR key with deploy-time placeholder:
```yaml
# Before: value: ar_user_stag_qejkqo2vSBoS-QceOJ8eg4wS0Gy82G5H
# After: value: __ADMIN_PREVIEW_API_KEY__  # substituted at deploy time
```

### 6. `scripts/deploy/_prod_env_vars.txt` and `_prod_env_vars_clean.txt`

```
# Before: ADMIN_PREVIEW_API_KEY=ar_user_stag_qejkqo2vSBoS-...
# After: ADMIN_PREVIEW_API_KEY=__ADMIN_PREVIEW_API_KEY__
```

### 7. `tests/hooks/test_credential_scan.py` (new)

24 automated tests in 9 test classes:

| Class | Tests | Verifies |
|-------|-------|----------|
| TestFixtureSuppression | 4 | Approved fixtures in approved paths pass |
| TestNonFixtureBlocked | 1 | Unknown keys blocked in test paths |
| TestFixtureWrongPath | 1 | Fixtures blocked outside approved paths |
| TestNoBlanketExclusions | 2 | New keys in formerly-excluded files blocked |
| TestFQDNAndConnStringDetection | 2 | FQDN and connection string detection preserved |
| TestUnquotedDetection | 2 | YAML and env-var assignment detection |
| TestBareEditPayload | 1 | Bare Edit new_string detection |
| TestHyphenKeys | 2 | Hyphen-containing keys detected |
| TestInventoryCoverage | 4 | Fixture (52) and example (5) set sizes + path scoping |
| TestPunctuationBoundary | 5 | Period, semicolon, paren, bracket, newline terminators |

### 8. `tests/hooks/__init__.py` (new)

Package init for test discovery.

## Test Results

```
24 passed in 0.21s
```

All tests pass. Lint clean (ruff check passes on all changed files).

## Follow-up Risk Item

**WI-DEPLOY-SECRETS:** Third-party credentials (Stripe, Shopify, Mailchimp,
webhook secrets) remain hardcoded in `scripts/deploy/` artifacts. The scanner
after this WI protects against Agent Red key-shaped values only. Documented
in the proposal for owner visibility.

## Verification Checklist

- [x] Blanket exclusions removed (no `tests[/\\]conftest\.py$` or
  `test_middleware_pipeline` in `_EXCLUDED_PATHS`)
- [x] 52 fixture values in `_FIXTURE_VALUES`
- [x] 5 source examples in `_DOCSTRING_EXAMPLE_VALUES`
- [x] Unified detector with `[A-Za-z0-9_-]` and negative lookahead
- [x] Evaluation scripts use mandatory env vars
- [x] Archive staging key redacted
- [x] Deploy AR key replaced with placeholder
- [x] 24/24 tests pass
- [x] Lint clean
