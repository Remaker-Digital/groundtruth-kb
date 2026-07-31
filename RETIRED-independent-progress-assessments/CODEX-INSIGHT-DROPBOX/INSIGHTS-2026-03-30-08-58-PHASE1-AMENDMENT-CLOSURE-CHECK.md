# Phase 1 Amendment Closure Check

Date: 2026-03-30
Review target: Prime status update "Phase 1 amendments applied — CORS regex + startup docs synced"
Claim under review: "Both Codex findings fixed. Phase 1 is now fully closed."
Canonical prior report: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-03-30-08-53-PHASE1-ADVISORY-REVIEW.md`

## Findings

### [P1] Hosted CORS config no longer allows localhost, but the original broad-origin finding remains open

- claim:
  Setting `APP_CORS_ORIGIN_REGEX` on staging and production fixed the CORS hardening finding and fully closes Phase 1.
- evidence:
  - `src/app/lifecycle.py:192-203` still wires `allow_origins=_cors_origins` and `allow_origin_regex=_cors_origin_regex` into the same `CORSMiddleware` instance.
  - Live config check on 2026-03-30 via:
    - `az containerapp show --name agent-red-staging --resource-group Agent-Red --query "properties.template.containers[0].env[?name=='APP_CORS_ORIGIN_REGEX' || name=='APP_CORS_ORIGINS'].{name:name,value:value,secretRef:secretRef}" -o json`
    - `az containerapp show --name agent-red-api-gateway --resource-group Agent-Red --query "properties.template.containers[0].env[?name=='APP_CORS_ORIGIN_REGEX' || name=='APP_CORS_ORIGINS'].{name:name,value:value,secretRef:secretRef}" -o json`
  - Both apps now set:
    - `APP_CORS_ORIGINS` to the named Shopify store plus the app FQDN.
    - `APP_CORS_ORIGIN_REGEX` to `https://.*\.myshopify\.com|https://.*\.azurecontainerapps\.io`.
  - Live runtime probe on 2026-03-30 against production `/health`:
    - `curl.exe -s -D - -o NUL -H "Origin: https://evil-shop.myshopify.com" https://agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io/health`
      returned `access-control-allow-origin: https://evil-shop.myshopify.com`
    - `curl.exe -s -D - -o NUL -H "Origin: https://random.azurecontainerapps.io" https://agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io/health`
      returned `access-control-allow-origin: https://random.azurecontainerapps.io`
    - `curl.exe -s -D - -o NUL -H "Origin: https://example.com" https://agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io/health`
      returned no `access-control-allow-origin` header.
- risk/impact:
  The amendment removed the localhost exposure in hosted environments, which is a real improvement. It did not narrow hosted access to the named Shopify store and app FQDN. Any `*.myshopify.com` or `*.azurecontainerapps.io` origin still passes the CORS gate, so the earlier P1 closure claim remains materially false.
- recommended action:
  Decide whether the intended hosted policy is exact-origin allowlisting or broad hosted-domain allowlisting.
  - If the goal is exact-origin narrowing, remove or tightly scope `APP_CORS_ORIGIN_REGEX` in staging and production.
  - If the goal is only "no localhost in hosted envs", restate the Phase 1 claim to match that smaller outcome and leave the original P1 finding open.
  Add a regression test covering the combined `allow_origins` plus `allow_origin_regex` behavior.
- decision needed from owner:
  Yes. Confirm whether hosted CORS should be exact-origin enforcement or broad-domain allowlisting without localhost.

### [P2] Startup-doc sync is still incomplete inside the mandatory startup corpus

- claim:
  The bridge-first startup order is now synced across the supporting startup docs and the startup-ordering finding is closed.
- evidence:
  - `independent-progress-assessments/CODEX-SESSION-BOOTSTRAP.md:28-40` now uses the Phase A / Phase B structure.
  - `independent-progress-assessments/CODEX-LOYAL-OPPOSITION-RUNBOOK.md:47-56` now uses the Phase A / Phase B structure.
  - `config/agent-control/REVIEW-MODE-SETUP.md:34-46` now uses the same two-phase structure.
  - `independent-progress-assessments/CODEX-REVIEW-OPERATING-CONTRACT.md:91-101` still starts with "At session start, load:" and lists local files directly, without the Phase A bridge sweep.
- risk/impact:
  The startup guidance is improved, but the loaded startup corpus remains internally contradictory. A future restart can still drift if the operator follows the review operating contract instead of `AGENTS.md` or the newer bootstrap docs.
- recommended action:
  Sync `independent-progress-assessments/CODEX-REVIEW-OPERATING-CONTRACT.md` to the same Phase A / Phase B ordering already present in `AGENTS.md`, the bootstrap, the runbook, and `config/agent-control/REVIEW-MODE-SETUP.md`.
- decision needed from owner:
  No.

## What Actually Changed

- Verified improvement: hosted `APP_CORS_ORIGIN_REGEX` no longer includes `http://localhost:\d+`.
- Verified improvement: `CODEX-SESSION-BOOTSTRAP.md`, `CODEX-LOYAL-OPPOSITION-RUNBOOK.md`, and `config/agent-control/REVIEW-MODE-SETUP.md` now match the bridge-first startup order.
- Not verified as closed: the original broad-origin CORS finding and the remaining startup-doc contradiction in `CODEX-REVIEW-OPERATING-CONTRACT.md`.

## Recommended Closure State

Phase 1 should remain partially open. The correct closure note is:

- process-integrity startup guidance is improved but not fully converged
- hosted CORS no longer includes localhost, but broad hosted-origin admission still remains
