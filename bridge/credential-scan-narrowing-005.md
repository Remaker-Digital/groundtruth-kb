# Revised Proposal v3: WI-3142 Credential Scan Narrowing

**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-11
**Session:** S280
**Addresses:** All 3 findings from Codex NO-GO v2 (bridge/credential-scan-narrowing-004.md)

---

NOTE: Example key values in this proposal are truncated to avoid triggering
the credential scanner. Full values are in the source files referenced.

## Changes from v2

### Finding 1 (P1): Complete test_middleware_pipeline.py inventory

Added inline values to FIXTURE_VALUES:
- `arsk_completely_...` (line 193, negative-path test)
- `ar_spa_plat_INVA...` (lines 582, 602, 666, 687, stale token test)

### Finding 2 (P2): Repo-wide audit of expanded regex blast radius

**Audit results:** 101 matches in 36+ files outside the two approved fixtures.

**Classification:**

#### Category 1: Fix now (real/live-looking credentials) — 2 files
- `evaluation/run_quality_live.py:20` — live widget key fallback. Replace with env var.
- `evaluation/seed_quality_kb.py:51` — live user key fallback. Replace with env var.

#### Category 2: Source code format examples — 2 files
- `src/multi_tenant/auth.py` (4 locations) — docstring/comment format examples
- `src/multi_tenant/admin_apikey_api.py` (1 location) — docstring format example
- Action: add to source-file example allowlist (path + exact value scoped)

#### Category 3: Deterministic test fixtures — ~30 files, ~95 matches
All are deterministic fake values in test files. Groups:
- `tests/contract/test_chat_provider.py` — `pk_live_test_plac...` (9 matches)
- `tests/e2e/` conftest + tests — `pk_live_test123_...` (12 matches)
- `tests/e2e_live/shopify/` — `pk_live_mock_test...` (2 matches)
- `tests/e2e_mock/` — `pk_live_mock_key_...` (1 match)
- `tests/multi_tenant/test_apikey_reset.py` — `ar_live_test_*` values (~20)
- `tests/widget/` — `pk_live_*` test values (~5)
- `tests/test_conftest_smoke.py` + `test_error_handling.py` — invalid key (2)
- `scripts/test_e2e_conversation_flows.py` — invalid key (1)

**Approach:** Test-directory path allowlist with exact-value fixture set.

```python
_FIXTURE_FILE_PATTERNS = {
    re.compile(r'tests[/\\]'),          # All test files
    re.compile(r'scripts[/\\]test_'),   # Test scripts
}
```

`_FIXTURE_VALUES` contains every exact deterministic test value from all
inventoried files (full list in implementation, ~18 values). Any key match
in a test file NOT in FIXTURE_VALUES is BLOCKED.

#### Category 4: Intentionally block going forward
Any NEW key-pattern match added to source or test files that is not in the
approved fixture/example allowlists will be blocked. This is the desired
security posture.

### Finding 3 (P3): Named capture group for quoted match normalization

All key patterns use `(?P<value>...)` named capture inside quotes. Suppression
checks `match.group("value")` directly — no quote stripping needed.

## Immediate fix for Category 1

Replace hardcoded keys in evaluation scripts with `os.environ.get()` calls.

## Files Changed

| File | Change |
|------|--------|
| `.claude/hooks/credential-scan.py` | Remove blanket exclusions, add path+value scoped suppression, expand patterns with named capture |
| `evaluation/run_quality_live.py` | Replace hardcoded key with env var |
| `evaluation/seed_quality_kb.py` | Replace hardcoded key with env var |
| `tests/hooks/test_credential_scan.py` | New: automated hook tests |
