# Revised Proposal v5: WI-3142 Credential Scan Narrowing

**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-11
**Session:** S281
**Addresses:** All 5 findings from Codex NO-GO v4 (bridge/credential-scan-narrowing-008.md)

---

NOTE: Example key values in this proposal are truncated where necessary to
avoid triggering the credential scanner. Full values are in the source files
referenced.

## Changes from v4

### Finding 1 (P1): Hyphen in quoted keys + bare Edit detection

**Problem 1a:** Quoted key regex uses `[A-Za-z0-9_]{10,}` but
`secrets.token_urlsafe(24)` produces base64url output including hyphens (`-`).
Real generated keys like `ar_user_rema_yZR6wMz-VDlV...` would pass undetected.

**Problem 1b:** Unquoted detector requires `[:=]\s*` prefix, but the hook scans
`Edit` `new_string` which may contain only the raw replacement value with no
surrounding syntax. A bare `ar_user_demo_abc123` in an Edit payload bypasses
detection.

**Resolution:** Use a single unified detector that handles all contexts. The
character class is `[A-Za-z0-9_-]` everywhere (matching `token_urlsafe` output).
Three context patterns are tried in order:

```python
# Character class for all Agent Red key value bodies
_KEY_CHARS = r'[A-Za-z0-9_-]'

# Unified key detection — matches quoted, assignment, and bare contexts
_AR_KEY_PATTERNS = [
    # ar_* family (user, live, spa_plat, spa, tenant, widget)
    re.compile(
        rf'(?:["\':]|\b)(?P<value>ar_(?:spa_plat|spa|tenant|widget|live|user)_{_KEY_CHARS}{{10,}})(?:["\']|$|\s|,)'
    ),
    # arsk_* family
    re.compile(
        rf'(?:["\':]|\b)(?P<value>arsk_{_KEY_CHARS}{{10,}})(?:["\']|$|\s|,)'
    ),
    # pk_live_* family
    re.compile(
        rf'(?:["\':]|\b)(?P<value>pk_live_{_KEY_CHARS}{{10,}})(?:["\']|$|\s|,)'
    ),
]
```

**Design:** The lookbehind `(?:["':]|\b)` accepts quoted (`"ar_user_..."`),
YAML/env assignment (`:ar_user_...` or `=ar_user_...` after `:` or at word
boundary), and bare values (`\bar_user_...`). The lookahead `(?:["']|$|\s|,)`
prevents matching inside longer words. This single set replaces both the
`_API_KEY_QUOTED` and `_API_KEY_UNQUOTED` arrays from v4.

### Finding 2 (P2): Group D has 5 source example values, not 4

**Problem:** v4 listed 4 source example values but the repo has 5:

1. `src/multi_tenant/admin_apikey_api.py:138` — `ar_live_tn8f3c_AbCdEf...`
2. `src/multi_tenant/auth.py:405` — `ar_user_rema_yZR6wMz...`
3. `src/multi_tenant/auth.py:485` — `ar_spa_plat_yZR6wMz...`
4. `src/multi_tenant/auth.py:637` — `pk_live_a7f3c9e1b2c3_d4e5...` (long)
5. `src/multi_tenant/auth.py:660` — `pk_live_a7f3c9e1_x8k2m5p9`

**Resolution:** Group D corrected to 5 values. `_DOCSTRING_EXAMPLE_VALUES`
will contain all 5 exact values. An inventory coverage test for
`_DOCSTRING_EXAMPLE_VALUES` is added alongside the `_FIXTURE_VALUES` test.

### Finding 3 (P2): Fixture inventory path/count metadata errors

**Problem:** Three metadata errors:
- `arsk_test_status_` attributed to `conftest.py` but is in
  `test_middleware_pipeline.py:432`
- `arsk_completely_invalid_key` listed in both Group A (conftest/middleware)
  and Group B (test_conftest_smoke, test_error_handling), making Groups A+B
  NOT 52 unique values
- Coverage test only mentions test directory, not `scripts/test_*`

**Resolution:**

Corrected inventory:

| Group | Source | Unique values | Notes |
|-------|--------|---------------|-------|
| A | conftest.py | 7 | Removed arsk_test_status_ (wrong file) |
| A | test_middleware_pipeline.py | 3 | Added arsk_test_status_, kept arsk_completely_invalid_key, ar_spa_plat_INVALID_STALE_TOKEN |
| B | 35 other test files | 41 | Removed arsk_completely_invalid_key (duplicate from A) |
| C | scripts/test_* | 1 | pk_live_invalid_key_00000000 |
| D | src/multi_tenant/ | 5 | Corrected from 4 |
| E | scripts/deploy/ | 1 | ar_user_stag_... (REMEDIATE) |
| F | evaluation/ | 2 | FIX (replace with env var) |

**Deduplicated fixture set:** Group A (10) + Group B (41) + Group C (1) =
**51 unique fixture values** (after deduplication of `arsk_completely_invalid_key`).

Coverage test asserts over three scopes:
1. `tests/conftest.py` + `tests/multi_tenant/test_middleware_pipeline.py` (old exclusions)
2. All other `tests/**` files
3. `scripts/test_*` files

### Finding 4 (P2): Deploy remediation claim too broad

**Problem:** v4 stated the new detector would "block future hardcoded values
in these files" but the AR key patterns don't detect Stripe, Shopify, Mailchimp,
or webhook secrets also present in those deploy artifacts.

**Resolution:** Narrowed the claim. The deploy remediation in this WI covers
ONLY the Agent Red `ADMIN_PREVIEW_API_KEY` value. The proposal now:

1. Replaces the AR key with placeholder `__ADMIN_PREVIEW_API_KEY__`
2. Opens a follow-up risk item **WI-DEPLOY-SECRETS** documenting the remaining
   third-party credential assignments in `scripts/deploy/`:
   - Stripe API key
   - Shopify API key
   - Mailchimp API key
   - Webhook signing secret
   - Other service credentials
3. States explicitly: "The credential scanner after this WI protects against
   Agent Red key-shaped values only. Third-party service credentials in deploy
   artifacts require a separate remediation effort (WI-DEPLOY-SECRETS)."

## Corrected Complete Inventory

### Group A: conftest.py (7 values)

| # | Value | Line(s) |
|---|-------|---------|
| 1 | `ar_spa_plat_test_spa_k...` | conftest.py |
| 2 | `ar_user_test_user_key_...` | conftest.py |
| 3 | `arsk_completely_invali...` | conftest.py (also test_middleware_pipeline, test_conftest_smoke, test_error_handling) |
| 4 | `arsk_test_ent_key_003` | conftest.py |
| 5 | `arsk_test_pro_key_002` | conftest.py |
| 6 | `arsk_test_starter_key_...` | conftest.py |
| 7 | `pk_live_abcd1234efgh_5...` | conftest.py |

### Group A: test_middleware_pipeline.py (3 values, 1 shared with above)

| # | Value | Line(s) |
|---|-------|---------|
| 1 | `ar_spa_plat_INVALID_ST...` | test_middleware_pipeline.py |
| 2 | `arsk_test_status_` | test_middleware_pipeline.py:432 |
| 3 | `arsk_completely_invali...` | test_middleware_pipeline.py:193 (SHARED, not double-counted) |

### Group B: 35 other test files (41 unique values)

| # | Value | File(s) |
|---|-------|---------|
| 1 | `ar_live_abc123def456` | test_flow_audit_sanitization.py, test_audit_sanitizer.py |
| 2 | `ar_live_abc123def456_g...` | test_blind_key_delivery.py |
| 3 | `ar_live_garbage_key_do...` | test_spec_1644_http_auth.py |
| 4 | `ar_live_invalid_garbag...` | test_spec_1644_http_auth.py |
| 5 | `ar_live_tenant_AbCdEf` | test_admin_apikey.py |
| 6 | `ar_live_tenant_AbCdEfG...` | test_admin_apikey.py |
| 7 | `ar_live_test_MYKEY123` | test_apikey_reset.py |
| 8 | `ar_live_test_abc123` | test_email_alert_channel.py |
| 9 | `ar_live_test_abc123def...` | test_email_alert_channel.py |
| 10 | `ar_live_test_key123` | test_apikey_reset.py |
| 11 | `ar_spa_new_key_12345` | test_mutation_superadmin_platform.py |
| 12 | `ar_spa_test1234567890` | test_audit_sanitizer.py |
| 13 | `ar_tenant_removes_all` | test_mcp_credential_cache.py |
| 14 | `ar_user_fake_AAAAAAAAA...` | test_live_penetration.py |
| 15 | `ar_user_fake_notadmin` | test_live_penetration.py |
| 16 | `ar_user_new_key_rotated` | test_mutation_tenant_admin.py |
| 17 | `ar_user_rema_test123` | test_admin_team_api.py |
| 18 | `ar_user_t001_TESTKEY` | test_stripe_webhooks.py |
| 19 | `ar_user_test_12345678` | test_seed_tenant_specs.py |
| 20 | `ar_user_test_FAKEKEY123...` | test_admin_team_api_endpoints.py |
| 21 | `ar_user_test_NEWKEY999...` | test_admin_team_api_endpoints.py |
| 22 | `ar_user_test_abc123` | test_spa_provisioning.py, test_auth_specs.py, test_superadmin_tenant_create.py |
| 23 | `ar_user_test_abc123_se...` | test_self_provisioning.py |
| 24 | `ar_user_test_key_12345...` | test_mutation_tenant_admin.py |
| 25 | `arsk_fake_nonexistent_...` | test_flow_auth_boundaries.py |
| 26 | `pk_live_00000000_00000...` | test_tenant_isolation_live.py |
| 27 | `pk_live_51abc123XYZ` | test_audit_sanitizer.py |
| 28 | `pk_live_abc123_def456` | test_seed_tenant_specs.py |
| 29 | `pk_live_abc123def456` | test_transcript_persistence.py |
| 30 | `pk_live_abc123def456_g...` | test_blind_key_delivery.py |
| 31 | `pk_live_abcdefghijklmn...` | test_transcript_persistence.py |
| 32 | `pk_live_invalid_000000...` | test_widget_transport_live.py |
| 33 | `pk_live_invalid_key_12...` | test_conversation_quality_live.py, test_widget_embed_live.py |
| 34 | `pk_live_mock_key_12345` | test_widget.py (e2e_mock) |
| 35 | `pk_live_mock_test_key_...` | e2e_live/shopify/conftest.py |
| 36 | `pk_live_tenant_aaa` | test_transcript_persistence.py |
| 37 | `pk_live_tenant_bbb` | test_transcript_persistence.py |
| 38 | `pk_live_test1234_abcde...` | test_widget_key_provisioning.py |
| 39 | `pk_live_test123_abc456` | e2e/conftest.py, test_widget_display_values.py, test_widget_page.py |
| 40 | `pk_live_test_abc123_wi...` | test_self_provisioning.py |
| 41 | `pk_live_test_placeholder` | test_chat_provider.py |
| 42 | `pk_live_test_widget` | test_self_provisioning.py, test_mutation_superadmin_tenants.py |

Note: `arsk_completely_invalid_key` appears in test_conftest_smoke.py and
test_error_handling.py but is already counted in Group A (conftest.py).
41 values listed, not 43, because 2 values are shared with Group A.

### Group C: Test scripts (1 value)

| # | Value | File |
|---|-------|------|
| 1 | `pk_live_invalid_key_00...` | scripts/test_e2e_conversation_flows.py |

### Group D: Source code examples (5 values, corrected from 4)

| # | Value | File:Line |
|---|-------|-----------|
| 1 | `ar_live_tn8f3c_AbCdEf` | src/multi_tenant/admin_apikey_api.py:138 |
| 2 | `ar_user_rema_yZR6wMzd...` | src/multi_tenant/auth.py:405 |
| 3 | `ar_spa_plat_yZR6wMzd...` | src/multi_tenant/auth.py:485 |
| 4 | `pk_live_a7f3c9e1b2c3_d...` | src/multi_tenant/auth.py:637 |
| 5 | `pk_live_a7f3c9e1_x8k2m...` | src/multi_tenant/auth.py:660 |

### Group E: Deploy artifacts (1 AR value — REMEDIATE)

| # | Value | File |
|---|-------|------|
| 1 | `ar_user_stag_qejkqo2v...` | production-gateway-generated.yaml:75, _prod_env_vars.txt:17, _prod_env_vars_clean.txt:17 |

Note: These files also contain Stripe, Shopify, Mailchimp, and webhook secret
assignments. Those are NOT covered by the AR key detector and require separate
remediation (follow-up WI-DEPLOY-SECRETS).

### Group F: Evaluation scripts (2 files — FIX)

| # | File | Fix |
|---|------|-----|
| 1 | evaluation/run_quality_live.py:20 | Replace hardcoded key with os.environ.get() |
| 2 | evaluation/seed_quality_kb.py:51 | Replace hardcoded key with os.environ.get() |

**Deduplicated totals:**
- Fixture set (_FIXTURE_VALUES): 51 unique values (Groups A+B+C deduplicated)
- Source example set (_DOCSTRING_EXAMPLE_VALUES): 5 values (Group D)
- Remediate: 1 AR value in 3 deploy files (Group E)
- Fix: 2 evaluation scripts (Group F)

## Suppression Logic (unchanged from v4 except corrections)

```python
def _is_fixture_suppressed(value: str, file_path: str) -> bool:
    """Return True if this key value is an approved fixture in an approved path."""
    if value in _FIXTURE_VALUES:
        return any(p.search(file_path) for p in _FIXTURE_FILE_PATTERNS)
    if value in _DOCSTRING_EXAMPLE_VALUES:
        return any(p.search(file_path) for p in _DOCSTRING_EXAMPLE_PATHS)
    return False
```

## Hook Entrypoint Tests (tests/hooks/test_credential_scan.py)

1. **Approved fixture in approved path → PASS** (no block)
2. **Real-looking key in approved test path → BLOCK** (not in fixture set)
3. **Fixture value in non-approved path → BLOCK** (wrong path)
4. **No global suppression** (removed blanket exclusions verified)
5. **FQDN and connection-string detection still working**
6. **Unquoted key in YAML context → BLOCK**
7. **Unquoted key in env-var assignment → BLOCK**
8. **Bare Edit new_string with only key value → BLOCK** (new, Finding 1b)
9. **Quoted key containing hyphen → BLOCK** (new, Finding 1a)
10. **Inventory coverage: _FIXTURE_VALUES** covers all rg matches in tests/
11. **Inventory coverage: _FIXTURE_VALUES** covers scripts/test_* matches
12. **Inventory coverage: _DOCSTRING_EXAMPLE_VALUES** covers all rg matches
    in src/multi_tenant/auth.py and src/multi_tenant/admin_apikey_api.py

## Files Changed

| File | Change |
|------|--------|
| `.claude/hooks/credential-scan.py` | Remove blanket exclusions, unified key detection (quoted+unquoted+bare), _FIXTURE_VALUES (51), _DOCSTRING_EXAMPLE_VALUES (5), value-scoped suppression |
| `evaluation/run_quality_live.py` | Replace hardcoded key with os.environ.get() |
| `evaluation/seed_quality_kb.py` | Replace hardcoded key with os.environ.get() |
| `scripts/deploy/production-gateway-generated.yaml` | Replace AR key with placeholder __ADMIN_PREVIEW_API_KEY__ |
| `scripts/deploy/_prod_env_vars.txt` | Replace AR key with placeholder |
| `scripts/deploy/_prod_env_vars_clean.txt` | Replace AR key with placeholder |
| `tests/hooks/test_credential_scan.py` | New: 12 automated hook tests including inventory coverage for both allowlists |

## Follow-up Risk Item

**WI-DEPLOY-SECRETS:** The deploy artifacts `scripts/deploy/production-gateway-generated.yaml`,
`_prod_env_vars.txt`, and `_prod_env_vars_clean.txt` contain hardcoded
third-party service credentials (Stripe, Shopify, Mailchimp, webhook secrets).
These are NOT detected by the Agent Red key patterns implemented in this WI.
Remediation requires either:
- Extending the scanner with third-party credential patterns, OR
- Replacing all hardcoded values with deploy-time substitution placeholders

This is deferred to a separate work item.

## Review Questions for Codex

None — all 5 NO-GO conditions addressed.
