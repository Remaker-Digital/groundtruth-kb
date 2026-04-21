# NO-GO: WI-3142 Credential Scan Narrowing Review

**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-11
**Source reviewed:** `bridge/credential-scan-narrowing-001.md`
**Verdict:** NO-GO

## Claim

The proposal is directionally correct because the blanket `tests/conftest.py`
exclusion is a real fail-open scan gap, but the proposed implementation is not
safe enough to approve as written.

## Evidence

- `.claude/hooks/credential-scan.py:48-50` only detects quoted
  `ar_(spa|tenant|widget)_...` and `ar_spa_plat_...` values.
- `.claude/hooks/credential-scan.py:105-106` excludes both
  `tests/conftest.py` and
  `tests/multi_tenant/test_middleware_pipeline.py` completely.
- `tests/conftest.py:169-180` contains six deterministic auth fixture values,
  not five: three `arsk_test_*` keys, `TEST_SPA_KEY`,
  `TEST_USER_KEY = "ar_user_test_user_key_001"`, and `TEST_WIDGET_KEY`.
- Runtime probe against `.claude/hooks/credential-scan.py`:
  - `conftest full content: allow`
  - `ar_widget real-looking in conftest: allow`
  - `ar_widget outside conftest: block`
  - `ar_user real format outside: allow`
  - `ar_live real format outside: allow`
  - `pk_live real format outside: allow`
  - `ar_spa_plat real format outside: block`
- Real project key formats are broader than the hook currently detects:
  - `src/multi_tenant/auth.py:82` defines `ar_user_`.
  - `src/multi_tenant/auth.py:88` defines `ar_spa_`.
  - `src/multi_tenant/auth.py:92` defines `pk_live_`.
  - `src/multi_tenant/auth.py:404-421` generates `ar_user_{tenant_prefix}_{random}`.
  - `src/multi_tenant/auth.py:484-497` generates `ar_spa_plat_{random}`.
  - `src/multi_tenant/auth.py:633-653` generates `pk_live_{tenant_hash}_{random}`.
  - `src/multi_tenant/admin_apikey_api.py:60` defines `ar_live_`.
  - `src/multi_tenant/admin_apikey_api.py:134-147` generates
    `ar_live_{tenant_prefix}_{random}`.
- `tests/multi_tenant/test_middleware_pipeline.py:42-43`,
  `tests/multi_tenant/test_middleware_pipeline.py:432`, and
  `tests/multi_tenant/test_middleware_pipeline.py:582-688` show the second
  excluded file has the same fixture/negative-path rationale and would remain
  a full blind spot under the proposal if left unchanged.

## Findings

### 1. Unscoped content allowlist creates a new bypass

The proposal adds `_FAKE_KEY_ALLOWLIST` inside `_scan_content()` without
passing or checking `file_path`. That means any future content match using an
allowlisted fake prefix could be skipped anywhere in the repository, not only
inside the reviewed fixture files.

This conflicts with the proposal's own test plan item 3, which says another
file containing `arsk_test_` should still block. A content-only allowlist cannot
enforce that path boundary.

**Required action:** Scope any allowlist to explicit fixture paths and exact
known deterministic fixture values, or pass `file_path` into the filtering
logic and require both path and value to match before suppressing a finding.

### 2. The proposed scanner shape still misses real Agent Red key formats

Removing the `tests/conftest.py` exclusion does not by itself protect
`conftest.py` from accidental real credentials. The current hook misses
`ar_user_`, `ar_live_`, and `pk_live_` strings even outside excluded files, and
the runtime probe confirmed those values are allowed.

This is material because those are documented/generated project formats in
`src/multi_tenant/auth.py` and `src/multi_tenant/admin_apikey_api.py`.

**Required action:** Update the detection patterns before or as part of this
work so the hook covers the actual project key families it claims to protect:
at minimum `ar_user_`, `ar_live_`, `ar_spa_plat_`, and `pk_live_`, with
format-aware regexes that account for underscores in real key shapes. Use
noncapturing groups where possible so `findall()` behavior does not obscure
full matches.

### 3. The fixture inventory is incomplete

The proposal lists five intentional constants, but `tests/conftest.py:177`
also defines `TEST_USER_KEY = "ar_user_test_user_key_001"`. If the scanner is
corrected to detect `ar_user_`, that value becomes part of the false-positive
set that must be handled deliberately.

**Required action:** Include `TEST_USER_KEY` in the reviewed fixture allowlist
or replace the fixture values with shapes that are explicitly non-secret while
still exercising the intended auth branches.

### 4. The parallel blanket exclusion remains unresolved

The same hook comment groups `tests/conftest.py` and
`tests/multi_tenant/test_middleware_pipeline.py` together as the S271-reviewed
exception. Narrowing only `conftest.py` leaves
`tests/multi_tenant/test_middleware_pipeline.py` as a complete fail-open file.

**Required action:** Either include `tests/multi_tenant/test_middleware_pipeline.py`
in the same path-scoped narrowing design, or explicitly split it into a
separate work item with an owner-visible risk note. The safer path is to handle
both now because they share the same exclusion rationale.

## Required Conditions For GO

1. Replace global content-prefix allowlisting with path-scoped and value-scoped
   fixture suppression.
2. Cover the actual Agent Red key formats used in source: `ar_user_`,
   `ar_live_`, `ar_spa_plat_`, and `pk_live_`; retain any existing supported
   families only if still valid.
3. Account for `TEST_USER_KEY` in `tests/conftest.py`.
4. Address the second blanket exclusion for
   `tests/multi_tenant/test_middleware_pipeline.py` in this proposal or in an
   explicit follow-up risk decision.
5. Add automated hook tests that execute the JSON hook entrypoint for Write and
   Edit payloads, including:
   - known fixture values in approved fixture files are allowed;
   - real-looking project keys in those fixture files are blocked;
   - allowlisted fixture-looking values outside approved fixture files are not
     globally suppressed;
   - Azure FQDN and connection-string detection still works after the change.

## Decision Needed From Owner

No owner decision is needed unless Prime wants to intentionally keep
`tests/multi_tenant/test_middleware_pipeline.py` as a separate risk. Otherwise,
Prime should revise the proposal with the scoped allowlist and actual key-format
coverage above.
