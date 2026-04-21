# GO: WI-3142 Credential Scan Narrowing Re-Review

**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-11
**Source reviewed:** `bridge/credential-scan-narrowing-011.md`
**Prior reviews:** `bridge/credential-scan-narrowing-002.md`, `bridge/credential-scan-narrowing-004.md`, `bridge/credential-scan-narrowing-006.md`, `bridge/credential-scan-narrowing-008.md`, `bridge/credential-scan-narrowing-010.md`
**Verdict:** GO

## Claim

The v6 proposal addresses the prior NO-GO blockers: final detector scope uses
hyphen-aware key bodies and punctuation-safe boundaries, existing fixture and
source-example inventories now match the repo, the archive staging key is
classified for remediation, and the deploy/evaluation cleanup scope is explicit.

No proposal-level blocker remains.

## Evidence

- Current hook still has the original narrow quoted detector and blanket
  exclusions:
  - `.claude/hooks/credential-scan.py:47-50` detects only quoted
    `ar_(spa|tenant|widget)_...` and `ar_spa_plat_...` shapes.
  - `.claude/hooks/credential-scan.py:74-114` includes the current excluded
    path list and excludes the two test files this proposal narrows.
- Current fixture-file scan:
  - `tests/conftest.py:169-180` has six key-shaped fixture constants.
  - `tests/multi_tenant/test_middleware_pipeline.py:193`, `:432`, `:582`,
    `:602`, `:666`, and `:687` has the three additional old-exclusion fixture
    values, including the dynamic `arsk_test_status_` source literal.
- Verification command using the final hyphen-aware value regex:
  `python` probe over `tests`, `scripts/test_*.py`, `src/multi_tenant`,
  `evaluation`, and `scripts/archive/s157_kb_update.py` returned:
  - old excluded files: `9` unique values / `12` matches
  - other tests: `43` unique values / `97` matches
  - test scripts: `1` unique value / `1` match
  - deduped fixture total: `52`
  - source examples: `5` unique values / `5` matches
  - evaluation values to fix: `2`
  - archive values to remediate: `1`
- Boundary probe using the v6 negative-lookahead detector returned matches for:
  - quoted hyphen key
  - bare Edit-style key
  - period-terminated key
  - semicolon-terminated key
  - paren-terminated key
  and returned `NO MATCH` for an embedded-word false positive.
- Existing live-looking values remain correctly classified for cleanup:
  - `evaluation/run_quality_live.py:20`
  - `evaluation/seed_quality_kb.py:51`
  - `scripts/archive/s157_kb_update.py:143`

## Findings

No blocking findings.

The proposal should proceed only if implementation preserves the reviewed
shape:

1. Use the v6 unified detector with named `value` captures, `[A-Za-z0-9_-]`
   key bodies, and a negative lookahead boundary meaning "next character is not
   a valid key character."
2. Remove the two blanket path exclusions and replace them with exact
   path-and-value suppression.
3. Populate `_FIXTURE_VALUES` with the exact 52 deduped fixture values and
   `_DOCSTRING_EXAMPLE_VALUES` with the exact five source example values.
4. Include inventory coverage tests for the old excluded files, all other
   tests, approved `scripts/test_*.py` files, and the two source-example files.
5. Remediate the two evaluation defaults, the deploy Agent Red value, and the
   archive staging key as proposed.
6. Keep the third-party deploy secret follow-up visible as `WI-DEPLOY-SECRETS`;
   this GO covers Agent Red key-family detection, not generic third-party
   secret detection.

## Required Action Items

- Implement `tests/hooks/test_credential_scan.py` with the v6 regression set,
  including punctuation-terminated bare keys, fixture scoping, no global
  suppression, FQDN detection, and connection-string detection.
- Run the hook test target and the repo's lint checks before requesting
  post-implementation verification.

## Decision Needed From Owner

No owner decision is needed for this proposal. The remaining third-party deploy
secret work is already split out as an owner-visible follow-up risk item.
