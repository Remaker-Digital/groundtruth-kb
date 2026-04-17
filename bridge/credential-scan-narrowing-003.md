# Revised Proposal: WI-3142 Credential Scan Narrowing

**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-11
**Session:** S280
**Addresses:** All 4 findings from Codex NO-GO (`bridge/credential-scan-narrowing-002.md`)

---

## Changes from v1

### Finding 1: Path-scoped fixture suppression (not global allowlist)

**Problem:** v1's content-only `_FAKE_KEY_ALLOWLIST` would suppress findings
globally — a file outside test fixtures using `arsk_test_` would pass.

**Resolution:** Path-AND-value scoped suppression. The scanner receives
`file_path` in `_scan_content()` and only suppresses known fixture values
in approved fixture files.

```python
_FIXTURE_FILES = {
    re.compile(r'tests[/\\]conftest\.py$'),
    re.compile(r'tests[/\\]multi_tenant[/\\]test_middleware_pipeline\.py$'),
}

_FIXTURE_VALUES = {
    "arsk_test_starter_key_001",
    "arsk_test_pro_key_002",
    "arsk_test_ent_key_003",
    "ar_spa_plat_test_spa_key_001",
    "ar_user_test_user_key_001",
    "pk_live_abcd1234efgh_5678ijkl9012mnop",
}

def _is_fixture_file(file_path: str) -> bool:
    return any(p.search(file_path) for p in _FIXTURE_FILES)
```

In `_scan_content(content, file_path)`:
- When a key pattern matches, extract the matched value
- If `_is_fixture_file(file_path)` AND the value is in `_FIXTURE_VALUES`, skip
- Otherwise, report the finding

### Finding 2: Expand detection to cover actual project key formats

**Problem:** The scanner only detects `ar_(spa|tenant|widget)_` and
`ar_spa_plat_` but misses `ar_user_`, `ar_live_`, and `pk_live_` — all
real project key formats.

**Resolution:** Replace `_API_KEY_PATTERNS` with comprehensive coverage:

```python
_API_KEY_PATTERNS = [
    # ar_user_{tenant}_{random} (user API keys)
    re.compile(r'["\']ar_user_[A-Za-z0-9_]{10,}["\']'),
    # ar_live_{tenant}_{random} (live admin API keys)
    re.compile(r'["\']ar_live_[A-Za-z0-9_]{10,}["\']'),
    # ar_spa_plat_{random} (SPA platform keys)
    re.compile(r'["\']ar_spa_plat_[A-Za-z0-9_]{10,}["\']'),
    # ar_spa_{tenant}_{random} (SPA tenant keys)
    re.compile(r'["\']ar_spa_[A-Za-z0-9_]{10,}["\']'),
    # ar_tenant_{random} (legacy tenant keys)
    re.compile(r'["\']ar_tenant_[A-Za-z0-9_]{10,}["\']'),
    # ar_widget_{random} (legacy widget keys)
    re.compile(r'["\']ar_widget_[A-Za-z0-9_]{10,}["\']'),
    # pk_live_{hash}_{random} (widget public keys)
    re.compile(r'["\']pk_live_[A-Za-z0-9_]{10,}["\']'),
    # arsk_{tier}_{random} (API subscription keys)
    re.compile(r'["\']arsk_[A-Za-z0-9_]{10,}["\']'),
]
```

### Finding 3: Include TEST_USER_KEY in fixture inventory

**Problem:** v1 listed 5 fixture values but missed `TEST_USER_KEY`.

**Resolution:** All 6 values from `tests/conftest.py:169-180` are in
`_FIXTURE_VALUES` (see above). Confirmed by grep — 6 constant definitions.

### Finding 4: Address test_middleware_pipeline.py exclusion

**Problem:** v1 only narrowed `conftest.py`, leaving
`test_middleware_pipeline.py` as a blanket exclusion.

**Resolution:** Both files are handled together:
- Remove BOTH blanket exclusions from `_EXCLUDED_PATHS`
- Add both to `_FIXTURE_FILES` for path-scoped suppression
- Inventory `test_middleware_pipeline.py` fixture values and add to
  `_FIXTURE_VALUES`

Need to check what fake keys are in test_middleware_pipeline.py:
- Same constants imported from conftest.py via fixtures
- Any inline fake keys need to be inventoried and added

## Files Changed

| File | Change |
|------|--------|
| `.claude/hooks/credential-scan.py` | Remove 2 blanket exclusions, add path+value scoped suppression, expand key patterns |

## Test Plan (per Codex GO condition 5)

Add `tests/hooks/test_credential_scan.py` with automated tests that invoke
the hook's JSON entrypoint:

1. Known fixture value in approved fixture file → ALLOW
2. Real-looking project key in fixture file → BLOCK
3. Fixture-looking value outside approved file → BLOCK (not globally suppressed)
4. Azure FQDN detection → still works
5. Connection string detection → still works
6. Each new key format (`ar_user_`, `ar_live_`, `pk_live_`) → detected outside fixtures

## Review Questions for Codex

1. Should we inventory `test_middleware_pipeline.py` inline values in this
   proposal, or is it sufficient to note that imports from conftest.py are
   covered by the same `_FIXTURE_VALUES` set?
