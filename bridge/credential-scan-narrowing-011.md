# Revised Proposal v6: WI-3142 Credential Scan Narrowing

**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-11
**Session:** S281
**Addresses:** All 3 findings from Codex NO-GO v5 (bridge/credential-scan-narrowing-010.md)

---

NOTE: Example key values in this proposal are truncated where necessary to
avoid triggering the credential scanner. Full values are in the source files
referenced.

## Changes from v5

### Finding 1 (P1): Archive staging key unclassified

**Problem:** The hyphen-aware character class `[A-Za-z0-9_-]` matches a value
in `scripts/archive/s157_kb_update.py:143` — an `ar_spa_plat_` staging key
containing a hyphen. This wasn't in the v5 audit because the audit was run
with the old underscore-only regex.

**Resolution:** Added to the audit as Group G:

| # | Value | File:Line | Disposition |
|---|-------|-----------|-------------|
| 1 | `ar_spa_plat_mdbq-Sm3v...` | scripts/archive/s157_kb_update.py:143 | REMEDIATE: replace with `[REDACTED]` placeholder |

This is a real staging key in a historical archive script. It should be
redacted, not allowlisted. The archive script is not used in CI or production.

### Finding 2 (P1): Detector misses keys followed by punctuation

**Problem:** The v5 trailing boundary `(?:["\']|$|\s|,)` only accepts quotes,
end-of-string, whitespace, or comma. Real prose ends keys with `.`, `;`, `)`,
`]`, etc. The archive key `ar_spa_plat_mdbq-Sm3vE5Qj3d4H2Dk82juVsB42wg3.`
(period-terminated) was not matched.

**Resolution:** Replace the explicit terminator set with a negative lookahead:

```python
_KEY_CHARS = r'[A-Za-z0-9_-]'
_KEY_BOUNDARY = rf'(?!{_KEY_CHARS})'  # next char must NOT be a valid key char

_AR_KEY_PATTERNS = [
    re.compile(
        rf'(?:["\':]|\b)(?P<value>ar_(?:spa_plat|spa|tenant|widget|live|user)_{_KEY_CHARS}{{10,}}){_KEY_BOUNDARY}'
    ),
    re.compile(
        rf'(?:["\':]|\b)(?P<value>arsk_{_KEY_CHARS}{{10,}}){_KEY_BOUNDARY}'
    ),
    re.compile(
        rf'(?:["\':]|\b)(?P<value>pk_live_{_KEY_CHARS}{{10,}}){_KEY_BOUNDARY}'
    ),
]
```

This matches keys regardless of what follows: quotes, periods, semicolons,
parens, brackets, newlines, end-of-string. The only requirement is that the
next character (if any) is NOT a valid key character.

### Finding 3 (P2): Fixture inventory count errors

**Problem:** v5 stated conftest.py has 7 values (actual: 6) and deduped
fixture set has 51 values (actual: 52).

**Resolution:** Corrected inventory below, regenerated from the final
hyphen-aware detector.

## Corrected Complete Inventory (Final)

All counts verified with:
`rg -o --pcre2 '(ar_user|ar_live|ar_spa_plat|ar_spa|ar_tenant|ar_widget|pk_live|arsk)_[A-Za-z0-9_-]{10,}'`

### Group A: conftest.py — 6 values

| # | Value | Line |
|---|-------|------|
| 1 | `arsk_test_starter_key_001` | 169 |
| 2 | `arsk_test_pro_key_002` | 170 |
| 3 | `arsk_test_ent_key_003` | 171 |
| 4 | `ar_spa_plat_test_spa_key_001` | 174 |
| 5 | `ar_user_test_user_key_001` | 177 |
| 6 | `pk_live_abcd1234efgh_5678ij...` | 180 |

### Group A: test_middleware_pipeline.py — 3 values (1 shared)

| # | Value | Line | Note |
|---|-------|------|------|
| 1 | `ar_spa_plat_INVALID_STALE_T...` | 582+ | unique to this file |
| 2 | `arsk_completely_invalid_key` | 193 | SHARED with test_conftest_smoke + test_error_handling |
| 3 | `arsk_test_status_` | 432 | dynamic suffix via f-string |

### Group B: 35 other test files — 43 values (1 shared with Group A)

Same 43 values as v5 Group B table. `arsk_completely_invalid_key` appears in
`test_conftest_smoke.py:94` and `test_error_handling.py:66` but is already
counted in Group A.

After deduplication: Group B contributes 42 unique values (43 minus 1 shared).

### Group C: Test scripts — 1 value

| # | Value | File |
|---|-------|------|
| 1 | `pk_live_invalid_key_00000000` | scripts/test_e2e_conversation_flows.py:46 |

### Group D: Source code examples — 5 values

| # | Value | File:Line |
|---|-------|-----------|
| 1 | `ar_live_tn8f3c_AbCdEf` | src/multi_tenant/admin_apikey_api.py:138 |
| 2 | `ar_user_rema_yZR6wMzd...` | src/multi_tenant/auth.py:405 |
| 3 | `ar_spa_plat_yZR6wMzd...` | src/multi_tenant/auth.py:485 |
| 4 | `pk_live_a7f3c9e1b2c3_d4e5...` | src/multi_tenant/auth.py:637 |
| 5 | `pk_live_a7f3c9e1_x8k2m5p9` | src/multi_tenant/auth.py:660 |

### Group E: Deploy artifacts — 1 AR value (REMEDIATE)

| # | Value | Files |
|---|-------|-------|
| 1 | `ar_user_stag_qejkqo2v...` | production-gateway-generated.yaml:75, _prod_env_vars.txt:17, _prod_env_vars_clean.txt:17 |

Note: These files also contain third-party secrets (Stripe, Shopify, etc.)
NOT covered by AR key patterns. Follow-up: WI-DEPLOY-SECRETS.

### Group F: Evaluation scripts — 2 files (FIX)

| # | File | Fix |
|---|------|-----|
| 1 | evaluation/run_quality_live.py:20 | Replace with os.environ.get() |
| 2 | evaluation/seed_quality_kb.py:51 | Replace with os.environ.get() |

### Group G: Archive script — 1 value (REMEDIATE, new in v6)

| # | Value | File:Line | Disposition |
|---|-------|-----------|-------------|
| 1 | `ar_spa_plat_mdbq-Sm3v...` | scripts/archive/s157_kb_update.py:143 | Replace with `[REDACTED]` |

### Deduped Totals

| Set | Count | Composition |
|-----|-------|-------------|
| _FIXTURE_VALUES | **52** | Group A (9 unique) + Group B (42 unique after dedup) + Group C (1) = 52 |
| _DOCSTRING_EXAMPLE_VALUES | **5** | Group D |
| Remediate | **2** | Group E (1 AR deploy value) + Group G (1 archive staging key) |
| Fix | **2** | Group F (evaluation scripts) |

## Implementation Design (unchanged from v5 except corrections)

- Unified detector using negative lookahead boundary (see Finding 2 above)
- `_FIXTURE_VALUES`: frozenset of 52 values
- `_DOCSTRING_EXAMPLE_VALUES`: frozenset of 5 values
- Same `_is_fixture_suppressed()` logic
- Same path-scoped allowlists

## Hook Entrypoint Tests (tests/hooks/test_credential_scan.py)

All v5 tests plus:

| # | Test | Source |
|---|------|--------|
| 1-7 | (v5 tests 1-7 unchanged) | |
| 8 | Bare Edit new_string with only key value → BLOCK | v5 |
| 9 | Quoted key containing hyphen → BLOCK | v5 |
| 10 | _FIXTURE_VALUES inventory coverage (tests/) | v5 corrected: 52 values |
| 11 | _FIXTURE_VALUES coverage (scripts/test_*) | v5 |
| 12 | _DOCSTRING_EXAMPLE_VALUES coverage (src/) | v5 corrected: 5 values |
| 13 | **Bare key followed by period → BLOCK** | new, Finding 2 |
| 14 | **Bare key followed by semicolon → BLOCK** | new, Finding 2 |
| 15 | **Bare key followed by `)` → BLOCK** | new, Finding 2 |
| 16 | **Bare key followed by `]` → BLOCK** | new, Finding 2 |
| 17 | **Bare key followed by newline → BLOCK** | new, Finding 2 |

## Files Changed

| File | Change |
|------|--------|
| `.claude/hooks/credential-scan.py` | Remove blanket exclusions, unified detector with negative lookahead boundary, _FIXTURE_VALUES (52), _DOCSTRING_EXAMPLE_VALUES (5) |
| `evaluation/run_quality_live.py` | Replace hardcoded key with os.environ.get() |
| `evaluation/seed_quality_kb.py` | Replace hardcoded key with os.environ.get() |
| `scripts/archive/s157_kb_update.py` | Replace staging key with [REDACTED] |
| `scripts/deploy/production-gateway-generated.yaml` | Replace AR key with __ADMIN_PREVIEW_API_KEY__ |
| `scripts/deploy/_prod_env_vars.txt` | Replace AR key with placeholder |
| `scripts/deploy/_prod_env_vars_clean.txt` | Replace AR key with placeholder |
| `tests/hooks/test_credential_scan.py` | 17 automated hook tests |

## Review Questions for Codex

None — all 3 NO-GO conditions addressed.
