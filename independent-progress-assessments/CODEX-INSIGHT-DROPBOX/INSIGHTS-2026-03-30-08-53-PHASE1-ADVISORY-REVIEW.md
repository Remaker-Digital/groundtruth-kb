# Phase 1 Advisory Review - Process Integrity + CORS Hardening

Date: 2026-03-30
Review target: Prime Phase 1 changes for review-mode KB behavior, bridge-first startup ordering, shadow bridge DB removal, and CORS hardening
Claim under review: "Phase 1 complete: process integrity + CORS hardening"

## Findings

### [P1] CORS hardening does not narrow Shopify or Container Apps origins while the broad regex remains enabled

- claim:
  Setting `APP_CORS_ORIGINS` on staging and production hardens CORS to the named Shopify store and app FQDN, with the regex acting as defense-in-depth.
- evidence:
  - `src/app/lifecycle.py:192-203` configures both `allow_origins=_cors_origins` and `allow_origin_regex=_cors_origin_regex`.
  - `src/app/lifecycle.py:194-197` still defaults the regex to `https://.*\.myshopify\.com|https://.*\.azurecontainerapps\.io|http://localhost:\d+`.
  - Starlette primary-source check from `C:\Users\micha\AppData\Roaming\Python\Python314\site-packages\starlette\middleware\cors.py`:
    `CORSMiddleware.is_allowed_origin()` returns `True` if the regex matches before checking membership in `allow_origins`.
  - Live probe using the current Starlette middleware behavior with the claimed production-style config returned:
    - `https://blanco-9939.myshopify.com -> True`
    - `https://evil-shop.myshopify.com -> True`
    - `https://random.azurecontainerapps.io -> True`
    - `https://example.com -> False`
  - No repo tests were found for `APP_CORS_ORIGINS` / `APP_CORS_ORIGIN_REGEX` interaction (`rg -n "APP_CORS_ORIGINS|APP_CORS_ORIGIN_REGEX|allow_origin_regex|allow_origins" tests` returned no matches).
- risk/impact:
  The claimed hardening is operationally false while the regex remains broad. Browsers from any `*.myshopify.com` or `*.azurecontainerapps.io` origin still satisfy the CORS gate, so the new env var values do not produce the intended narrowing.
- recommended action:
  Narrow or disable `APP_CORS_ORIGIN_REGEX` in staging and production if explicit-origin enforcement is the goal. Add a regression test that proves unrelated Shopify and Container Apps origins are rejected when `APP_CORS_ORIGINS` is set.
- decision needed from owner:
  No.

### [P2] The "SPEC-1840 deferred" rationale is stale because tenant-specific origin enforcement already exists in backend code

- claim:
  SPEC-1840 was deferred because it still requires tenant config schema, middleware, and admin UI.
- evidence:
  - `src/multi_tenant/cosmos_schema.py:1079-1087` already defines `approved_widget_origins`.
  - `src/multi_tenant/middleware.py:764-810` already enforces widget-key origin validation and returns `403` when a configured origin is not approved.
  - `tests/multi_tenant/test_widget_origin_validation.py:1-87` explicitly covers the schema field, middleware source expectations, and request-origin plumbing.
  - `python -m pytest tests/multi_tenant/test_widget_origin_validation.py -q` passed: `8 passed in 0.23s`.
- risk/impact:
  Calling SPEC-1840 wholly deferred obscures that the backend control already exists. That can mis-sequence follow-up work by treating an operational rollout/configuration gap as if the feature is still absent.
- recommended action:
  Reframe the state as: backend support exists, but population of `approved_widget_origins` and any desired admin UX/documentation rollout may still be incomplete. Use that narrower statement in future phase notes.
- decision needed from owner:
  Yes. Decide whether approved widget origins must be populated before GA, or whether the current migration-mode default remains acceptable temporarily.

### [P2] Bridge-first startup is fixed in `AGENTS.md`, but supporting startup docs still preserve the old pre-bridge reading flow

- claim:
  The startup-ordering conflict is resolved.
- evidence:
  - `AGENTS.md:27-43` now correctly defines Phase A bridge sweep before Phase B local bootstrap.
  - `independent-progress-assessments/CODEX-REVIEW-OPERATING-CONTRACT.md:91-101` still says "At session start, load:" and then lists local files without the Phase A bridge sweep.
  - `independent-progress-assessments/CODEX-LOYAL-OPPOSITION-RUNBOOK.md:47-54` still begins the session start procedure with reading local files and choosing a review area, again without the bridge-first step.
- risk/impact:
  The primary contract is now correct, but the loaded startup corpus still contains contradictory guidance. That leaves room for future acknowledgement drift if an operator follows the subordinate docs instead of the updated `AGENTS.md`.
- recommended action:
  Update the review operating contract and Loyal Opposition runbook to reference the same Phase A / Phase B ordering now defined in `AGENTS.md`.
- decision needed from owner:
  No.

## Open Questions Or Assumptions

- I did not independently verify the Azure Container Apps environment variables; this review verifies application code and middleware behavior, not the live cloud configuration.
- `.claude/` is ignored local state in this repo, so the hook review is based on the current workspace file content rather than a tracked git diff.

## Change Summary

- Verified: `AGENTS.md:27-43` now makes bridge sweep the first startup phase.
- Verified: `.claude/hooks/assertion-check.py:530-551` now skips `_run_assertions()`, `_prune_assertion_runs()`, and handoff consumption in review read-only mode.
- Verified: `tools/knowledge-db/db.py:1-11` now distinguishes append-only core artifacts from operational tables that permit maintenance deletes.
- Verified: `.claude/hooks/prime_bridge.db` is currently absent in this workspace (`Test-Path '.claude\\hooks\\prime_bridge.db' -> False`).

## Verification Gaps

- Live Azure env-var values were not queried.
- No direct automated test was found for the combined CORS allowlist-plus-regex behavior; the CORS finding relies on source inspection plus a live Starlette middleware probe.
