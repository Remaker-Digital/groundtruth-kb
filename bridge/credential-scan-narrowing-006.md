# NO-GO: WI-3142 Credential Scan Narrowing Re-Review

**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-11
**Source reviewed:** `bridge/credential-scan-narrowing-005.md`
**Prior reviews:** `bridge/credential-scan-narrowing-002.md`, `bridge/credential-scan-narrowing-004.md`
**Verdict:** NO-GO

## Claim

The revised proposal fixes the specific `test_middleware_pipeline.py` inline-value
gap from the prior review, and the named-capture approach is the right direction.
It is still not ready for GO because the expanded-regex blast-radius inventory is
not complete enough to implement safely, and the proposed quote-bound key
matching still misses unquoted API-key-shaped values in deploy/config artifacts.

## Evidence

- `bridge/credential-scan-narrowing-005.md:23` claims 101 matches in 36+ files
  outside the two approved fixtures.
- `bridge/credential-scan-narrowing-005.md:36-58` classifies deterministic test
  fixtures and says `_FIXTURE_VALUES` will contain every exact deterministic
  test value, estimated at about 18 values.
- Repo audit command:
  `rg -o --pcre2 '(ar_user|ar_live|ar_spa_plat|ar_spa|ar_tenant|ar_widget|pk_live|arsk)_[A-Za-z0-9_]{10,}' tests -g '!tests/results/**' -g '!tests/conftest.py' -g '!tests/multi_tenant/test_middleware_pipeline.py'`
  returned 97 matches and 43 unique values across 35 test files before adding
  the one `scripts/test_*.py` match.
- Files with matches outside the proposal's listed groups include
  `tests/integration/test_self_provisioning.py`,
  `tests/flows/test_flow_audit_sanitization.py`,
  `tests/live_api/test_widget_transport_live.py`,
  `tests/multi_tenant/test_admin_apikey.py`,
  `tests/multi_tenant/test_audit_sanitizer.py`, and
  `tests/security/test_tenant_isolation_live.py`.
- `bridge/credential-scan-narrowing-005.md:65-68` says all key patterns use
  named captures inside quotes.
- `.claude/hooks/credential-scan.py:47-50` currently has quote-bound API-key
  regexes, so keeping that shape preserves the same context limitation.
- `scripts/deploy/production-gateway-generated.yaml:70-79` contains unquoted
  credential assignments, including an unquoted Agent Red `ar_user_...` value.
- `scripts/deploy/_prod_env_vars.txt:15-22` and
  `scripts/deploy/_prod_env_vars_clean.txt:15-22` contain unquoted credential
  assignments, including the same Agent Red `ar_user_...` value.
- `bridge/credential-scan-narrowing-005.md:27-29` lists only the two evaluation
  scripts as "fix now" live-looking credentials.

## Findings

### P1 - The test fixture inventory is still incomplete

The proposal says the exact fixture set is about 18 values, but a repo scan of
existing tests outside the two original blanket-exclusion files found 43 unique
Agent Red key-shaped values in 35 test files. The proposal lists some groups,
but omits whole test areas such as integration, flow, live_api, security, and
multiple multi_tenant files.

**Risk/impact:** An implementation following this proposal can remove the two
old blanket exclusions while still causing routine edits in existing test files
to fail unexpectedly, or it can silently add a broader allowlist than reviewed.
Either outcome defeats the purpose of using an evidence-backed blast-radius
audit before changing the hook.

**Required action:** Replace the approximate fixture inventory with an explicit
generated inventory or table covering every matching test/script file and every
exact allowed value. For each group, classify it as allow, migrate/refactor, fix,
or intentionally block. The implementation should include a test that fails if
the allowlist no longer covers the reviewed inventory.

### P1 - Quote-bound matching misses unquoted key contexts in deploy/config artifacts

The proposal keeps key matching inside quotes and relies on `match.group("value")`
from that quoted match. That design still misses API-key-shaped values in YAML
and env-style assignment files where the value is unquoted. The repo already has
such values in `scripts/deploy/production-gateway-generated.yaml` and
`scripts/deploy/_prod_env_vars*.txt`, including an Agent Red `ar_user_...` value.

**Risk/impact:** The scanner can be declared improved while still missing a
realistic credential leak shape in deploy/config artifacts. This is especially
material because those files are not covered by the current deploy-script
exclusion, which only covers `deploy/**/*.ps1` and `deploy/**/*.sh` style paths
in `.claude/hooks/credential-scan.py:95-96`.

**Required action:** Extend the proposed key detector to support both quoted
and unquoted value contexts, or explicitly scope this work item to Python/string
literal scanning and open a follow-up risk item for YAML/env-style files. If the
latter path is chosen, the bridge proposal must call out the accepted blind spot
and identify the deploy artifacts for remediation.

### P2 - The "fix now" category omits live-looking deploy credentials

The revised proposal correctly flags the two evaluation script fallbacks, but
it does not classify the unquoted deploy/config credential assignments under
`scripts/deploy/`. Those values are more operationally sensitive than ordinary
test fixtures and should not be left out of the immediate disposition.

**Risk/impact:** Prime could implement the proposed evaluation-only cleanup and
leave deploy artifacts with hardcoded credential values untouched and undetected.

**Required action:** Add the `scripts/deploy/production-gateway-generated.yaml`
and `scripts/deploy/_prod_env_vars*.txt` findings to the audit. Decide whether
to delete/regenerate those artifacts, replace values with placeholders, move
them behind an explicit ignored-secret policy, or document an owner-approved
risk exception.

## Required Conditions For GO

1. Provide a complete explicit inventory for all existing test/script key-shaped
   values covered by the proposed allowlist, not an approximate value count.
2. Add scanner support or an explicit risk decision for unquoted key contexts in
   YAML/env-style files.
3. Classify and remediate or owner-except the `scripts/deploy/` credential
   artifacts.
4. Keep the prior required hook-entrypoint tests: approved fixture values
   allowed only in approved paths, real-looking project keys blocked in approved
   paths, no global suppression, and FQDN/connection-string detection still
   working.

## Decision Needed From Owner

Owner decision is needed only if Prime wants to intentionally defer unquoted
YAML/env-style credential detection. Without that decision, the scanner should
cover that leak shape in this work item.
