# NO-GO: WI-3142 Credential Scan Narrowing Post-Implementation Verification v2

**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-11
**Source reviewed:** `bridge/credential-scan-narrowing-015.md`
**Approved proposal:** `bridge/credential-scan-narrowing-011.md`
**Prior GO:** `bridge/credential-scan-narrowing-012.md`
**Prior verification:** `bridge/credential-scan-narrowing-014.md`
**Verdict:** NO-GO

## Claim

The v2 post-implementation report fixes the prior verification blockers around
entrypoint tests, the `tests/hooks/test_credential_scan.py` blanket exclusion,
and changed-file ruff/format status.

It is still not ready for VERIFIED because the deploy artifacts retain a
hardcoded Agent Red `SUPERADMIN_PREVIEW_API_KEY` value and the installed hook
does not detect that `ar_stg_` key shape. This is not covered by the stated
third-party deploy-secret follow-up.

## Evidence

- `.claude/hooks/credential-scan.py:58-76` detects only:
  - `ar_(spa_plat|spa|tenant|widget|live|user)_...`
  - `arsk_...`
  - `pk_live_...`
  It does not include `ar_stg_`.
- `.claude/hooks/credential-scan.py:201-233` no longer excludes
  `tests/hooks/test_credential_scan.py`; the prior blanket-test-file exclusion
  finding is addressed.
- `tests/hooks/test_credential_scan.py:70-88` runs the hook through the JSON
  subprocess entrypoint, and `tests/hooks/test_credential_scan.py:299-344`
  includes Write/Edit entrypoint tests.
- `tests/hooks/test_credential_scan.py:230-290` now performs repo-scanning
  inventory coverage for fixture and docstring example allowlists.
- Verification commands:
  - `python -m pytest tests/hooks/test_credential_scan.py -q --tb=short`
    returned `33 passed in 0.63s`.
  - `python -m ruff check .claude/hooks/credential-scan.py evaluation/run_quality_live.py evaluation/seed_quality_kb.py tests/hooks/test_credential_scan.py --no-cache`
    returned `All checks passed!`.
  - `python -m ruff format --check .claude/hooks/credential-scan.py evaluation/run_quality_live.py evaluation/seed_quality_kb.py tests/hooks/test_credential_scan.py --no-cache`
    returned `4 files already formatted`.
- Entrypoint spot probes:
  - Write to `tests/hooks/test_credential_scan.py` with a new `ar_user_...`
    sample returned `decision=block`.
  - Edit to `src/config.py` with a bare punctuation-terminated `ar_user_...`
    sample returned `decision=block`.
  - Write to `scripts/deploy/_prod_env_vars.txt` with
    `SUPERADMIN_PREVIEW_API_KEY=ar_stg_...` returned `{}`.
- `scripts/deploy/PRODUCTION-ENV-CHANGES.md:21-22` says both
  `ADMIN_PREVIEW_API_KEY` and `SUPERADMIN_PREVIEW_API_KEY` are Key Vault
  backed secrets.
- The remediated admin key is placeholdered:
  - `scripts/deploy/production-gateway-generated.yaml:74-75`
  - `scripts/deploy/_prod_env_vars.txt:17`
  - `scripts/deploy/_prod_env_vars_clean.txt:17`
- The superadmin key remains hardcoded:
  - `scripts/deploy/production-gateway-generated.yaml:110-111`
  - `scripts/deploy/_prod_env_vars.txt:35`
  - `scripts/deploy/_prod_env_vars_clean.txt:35`

## Findings

### P1 - Agent Red superadmin deploy key remains hardcoded and undetected

The implementation remediates `ADMIN_PREVIEW_API_KEY`, but leaves
`SUPERADMIN_PREVIEW_API_KEY` as a hardcoded `ar_stg_...` value in the same
deploy artifacts. Project deploy documentation maps that variable to Key Vault,
so this is an Agent Red secret handling issue, not a third-party credential
follow-up.

The installed hook also allows the exact `SUPERADMIN_PREVIEW_API_KEY=ar_stg_...`
assignment shape. A future write to those deploy artifacts can therefore
reintroduce or retain this Agent Red credential without being blocked.

**Risk/impact:** The bridge report can be marked verified while a same-scope
Agent Red deploy credential remains in plaintext and outside the scanner's
coverage. That undercuts the security outcome of WI-3142.

**Required action:** Remediate `SUPERADMIN_PREVIEW_API_KEY` alongside
`ADMIN_PREVIEW_API_KEY` by replacing the hardcoded deploy value with a
deploy-time placeholder or Key Vault reference. If `ar_stg_` is a valid Agent
Red key family, add scanner coverage and entrypoint tests for it. If it is a
legacy/one-off format, document an owner-visible exception and include the
specific deploy files in the follow-up risk item.

## Passing Checks

- Hook-entrypoint tests now exist and pass.
- Inventory coverage tests now scan repo fixture/source-example scopes rather
  than checking counts only.
- `tests/hooks/test_credential_scan.py` is no longer a full hook exclusion.
- Changed-file ruff check and format check pass for the files claimed in the
  v2 post-implementation report.

## Required Conditions For VERIFIED

1. Remove or explicitly owner-except the hardcoded `SUPERADMIN_PREVIEW_API_KEY`
   value from the three deploy artifacts.
2. Decide whether `ar_stg_` is a supported Agent Red key family. If yes, add it
   to the detector and tests. If no, document the legacy exception and ensure
   it is not omitted from the deploy-secret follow-up.
3. Re-run the hook test target and changed-file ruff/format checks after the
   deploy remediation.

## Decision Needed From Owner

Owner decision is needed only if Prime wants to retain the hardcoded
`SUPERADMIN_PREVIEW_API_KEY` or defer `ar_stg_` handling. Otherwise Prime
should remediate it before requesting verification again.
