# NO-GO: WI-3142 Credential Scan Narrowing Re-Review

**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-11
**Source reviewed:** `bridge/credential-scan-narrowing-007.md`
**Prior reviews:** `bridge/credential-scan-narrowing-002.md`, `bridge/credential-scan-narrowing-004.md`, `bridge/credential-scan-narrowing-006.md`
**Verdict:** NO-GO

## Claim

The v4 proposal materially improves the earlier design: it inventories the
existing test fixtures, removes the two blanket exclusions, adds path-and-value
suppression, and covers YAML/env-style assignment contexts for Agent Red key
families.

It is still not ready for GO because the proposed detector still misses valid
project key shapes and realistic Claude Edit payloads, and the inventory /
remediation plan has mismatches that would either block reviewed examples or
leave known credentials in deploy artifacts.

## Evidence

- `bridge/credential-scan-narrowing-007.md:126-137` proposes quoted patterns
  with `[A-Za-z0-9_]{10,}` but unquoted patterns with `[A-Za-z0-9_-]{10,}`.
- `src/multi_tenant/auth.py:420` and `src/multi_tenant/auth.py:496` generate
  user and SPA keys with `secrets.token_urlsafe(24)`, whose output can include
  hyphens.
- Regex probe against the proposed shapes:
  - quoted fake key with hyphen: not matched;
  - quoted fake key without hyphen: matched;
  - assignment-form unquoted fake key with hyphen: matched.
- `.claude/hooks/credential-scan.py:171-174` scans only `content` for `Write`
  and only `new_string` for `Edit`; an Edit payload can contain just the raw
  replacement value without surrounding `KEY=` or YAML `value:` context.
- Regex probe against the proposed unquoted shapes:
  - YAML `value: ar_user_demo_...`: matched;
  - env assignment `KEY=ar_user_demo_...`: matched;
  - bare `ar_user_demo_...`: not matched.
- Inventory verification command:
  `rg -o --pcre2 '(ar_user|ar_live|ar_spa_plat|ar_spa|ar_tenant|ar_widget|pk_live|arsk)_[A-Za-z0-9_]{10,}' tests scripts src -g '!tests/results/**'`
  produced these redacted counts:
  - 97 matches / 43 unique values across 35 test files outside the two old
    exclusions;
  - 12 matches / 9 unique values in the two old excluded files;
  - 4 matches / 2 unique values in `scripts/`;
  - 5 matches / 5 unique values in `src/`.
- `bridge/credential-scan-narrowing-007.md:92-99` lists Group D as four source
  example values, and `bridge/credential-scan-narrowing-007.md:211-212` says
  `_DOCSTRING_EXAMPLE_VALUES` contains four exact values.
- Source scan found five source example values:
  - `src/multi_tenant/admin_apikey_api.py:138`;
  - `src/multi_tenant/auth.py:405`;
  - `src/multi_tenant/auth.py:485`;
  - `src/multi_tenant/auth.py:637`;
  - `src/multi_tenant/auth.py:660`.
- `bridge/credential-scan-narrowing-007.md:35` attributes `arsk_test_status_`
  to `conftest.py`, but the actual match is
  `tests/multi_tenant/test_middleware_pipeline.py:432`.
- `bridge/credential-scan-narrowing-007.md:159-160` says the new unquoted
  detector will block future hardcoded values in deploy files.
- The deploy artifacts also contain other hardcoded credential-style
  assignments not covered by the proposed Agent Red key patterns, including:
  - `scripts/deploy/production-gateway-generated.yaml:70-81`;
  - `scripts/deploy/_prod_env_vars.txt:15-22`;
  - `scripts/deploy/_prod_env_vars_clean.txt:15-22`.

## Findings

### P1 - Proposed key detection still misses valid project keys

The quoted key patterns exclude hyphens, while the project generates user and
SPA keys with `secrets.token_urlsafe(24)`. That means a real quoted
`ar_user_...` or `ar_spa_plat_...` value containing a hyphen can pass through
the quoted detector. The unquoted detector allows hyphens, so this is an
inconsistent regex boundary rather than an intentional format decision.

The unquoted detector also requires `:` or `=` immediately before the value.
That covers full YAML/env assignment lines, but the hook scans `Edit`
`new_string` directly. A Claude Edit replacement that inserts only the raw
unquoted key value is therefore still a bypass.

**Required action:** Use a single format-aware extraction strategy that covers
quoted, assignment-form, and bare replacement values for all valid project key
characters. Add hook-entrypoint tests for:

1. quoted generated-shaped keys containing hyphens;
2. unquoted assignment-form keys;
3. bare Edit `new_string` values containing a key with no surrounding syntax.

### P2 - Source example allowlist is under-specified

The proposal says Group D has four source example values and that
`_DOCSTRING_EXAMPLE_VALUES` will contain four exact values. The repo has five
source example matches in the two approved source files. In particular,
`src/multi_tenant/auth.py` has two distinct `pk_live_...` docstring examples
at lines 637 and 660.

If Prime implements exactly four docstring values, one reviewed source example
will still be blocked. If Prime silently adds a fifth value, the implementation
will exceed the reviewed inventory.

**Required action:** Make Group D explicit with five separate exact redacted
entries and add an inventory coverage test for `_DOCSTRING_EXAMPLE_VALUES`, not
only `_FIXTURE_VALUES` in tests.

### P2 - Fixture inventory metadata has path/count errors

The proposal's test inventory is close to the verified counts, but the metadata
is not precise enough for a scanner allowlist:

- `arsk_test_status_` is attributed to `conftest.py`, but the match is in
  `tests/multi_tenant/test_middleware_pipeline.py:432`.
- `arsk_completely_invalid_key` appears in both Group A and Group B, so
  Groups A+B are not 52 unique fixture values even though
  `bridge/credential-scan-narrowing-007.md:171-189` describes a 53-value
  fixture set after adding Group C.
- The proposed inventory coverage test only mentions the test directory, but
  the allowlist also includes the `scripts/test_...` fixture value.

**Required action:** Regenerate the reviewed inventory into an exact
path-to-values table and make the coverage test assert all reviewed fixture
scopes: old excluded files, all other tests, and approved test scripts.

### P2 - Deploy remediation claim is broader than the detector

The proposal correctly remediates the Agent Red `ADMIN_PREVIEW_API_KEY` value
from the three deploy artifacts. However, those same artifacts also contain
other hardcoded credential-style assignments, including Stripe, Shopify,
Mailchimp, and webhook secrets. The proposed Agent Red key patterns will not
detect those values, so the statement that future hardcoded values in these
files will be blocked is not true as written.

**Required action:** Either narrow the claim to "future Agent Red key-shaped
values" and open an owner-visible follow-up risk for the remaining deploy
secrets, or include third-party secret patterns / remediation in this work item.
Do not present the deploy files as generally protected after replacing only the
Agent Red key.

## Required Conditions For GO

1. Fix the detector so quoted keys with valid hyphen-containing generated
   values are blocked.
2. Add bare-value detection or an equivalent hook-safe strategy for Edit
   payloads where `new_string` is only the replacement key.
3. Correct Group D to five exact source example values and add coverage for the
   source-example allowlist.
4. Correct the fixture inventory path/count metadata and include approved test
   scripts in the inventory coverage test.
5. Reword or expand the deploy remediation plan so it does not imply generic
   credential protection while third-party deploy secrets remain uncovered.
6. Keep all prior hook-entrypoint regression tests for fixture scope, no global
   suppression, FQDN detection, connection-string detection, YAML/env unquoted
   detection, and inventory coverage.

## Decision Needed From Owner

Owner decision is needed only if Prime wants to defer third-party deploy secret
detection/remediation. The detector gaps for valid Agent Red keys and bare Edit
payloads should be fixed in this work item before implementation.
