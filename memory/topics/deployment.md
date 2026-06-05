# Deployment — Operational Lessons

> Full reference: KB DOC-DEPLOYMENT

## Container Build Procedures (S209 — AUTHORITATIVE)

### API Gateway (Production/Staging)
Uses main `Dockerfile`. ACR cloud build works from Windows CLI because Docker layer caching keeps builds short (~3 min).
```
az acr build --registry acragentredeastus --image api-gateway:v{VERSION} --file Dockerfile . --no-logs
```
Then deploy:
```
az containerapp revision copy --name agent-red-staging --resource-group Agent-Red --image acragentredeastus.azurecr.io/api-gateway:v{VERSION} --revision-suffix v{VERSION_DASHES}
```

### Test Host Container — USE GITHUB ACTIONS (NOT az acr build)
**CRITICAL:** `az acr build` from Windows crashes with `UnicodeEncodeError: 'charmap'` on uncached builds (non-ASCII in apt-get/pip output). The `--no-logs` flag does NOT fix this — the CLI still processes logs internally and reports "Failed" even when it's actually a `COPY` failure or similar.

**Correct procedure:**
1. Commit and push changes to `main`
2. Trigger GitHub Actions: `gh workflow run build-test-host.yml --repo mike-remakerdigital/agent-red --ref main -f tag=v{VERSION}`
3. Monitor: `gh run list --repo mike-remakerdigital/agent-red --workflow=build-test-host.yml --limit 1`
4. Poll completion: `gh run view {RUN_ID} --repo mike-remakerdigital/agent-red --json status,conclusion`
5. If failed, check logs: `gh run view {RUN_ID} --repo mike-remakerdigital/agent-red --log-failed | tail -30`
6. Verify tag: `az acr repository show-tags --name acragentredeastus --repository test-host --orderby time_desc --top 3`
7. Deploy: `az containerapp revision copy --name agent-red-test-host --resource-group Agent-Red --image acragentredeastus.azurecr.io/test-host:v{VERSION} --revision-suffix v{VERSION_DASHES}`

**Resource group:** `Agent-Red` (not `rg-agentred-eastus`)

**GitHub secrets required:** `ACR_USERNAME` (acragentredeastus), `ACR_PASSWORD` (ACR admin password). Set via: `gh secret set ACR_USERNAME/ACR_PASSWORD --repo mike-remakerdigital/agent-red`

**Workflow file:** `.github/workflows/build-test-host.yml`

### .dockerignore Gotcha (S209 Root Cause)
Files excluded in `.dockerignore` will silently fail `COPY` in Dockerfile. When adding new `COPY` lines to any Dockerfile, ALWAYS check `.dockerignore` first. The error message in ACR builds is hidden by the Windows CLI charmap crash.

Key exclusions to be aware of:
- `CLAUDE.md` — NOT excluded (needed by test host)
- `docs/` — excluded (not copied to test host)
- `.claude/` — excluded
- `memory/` — excluded
- `.env*` — excluded (except admin .env.staging files)

### ACR Build Debugging (when az acr build fails)
1. Check actual status (ignore CLI exit code): `az acr task show-run --registry acragentredeastus --run-id {ID} --query status -o tsv`
2. Check if image was pushed: `az acr repository show-tags --name acragentredeastus --repository {REPO} --orderby time_desc --top 3`
3. If status=Failed + no image → real Docker build failure. Use GitHub Actions to see clear error logs.
4. If status=Failed + image exists → CLI charmap bug. Image is fine, deploy it.

## PowerShell Encoding (S12)
upgrade.ps1 had double-encoded UTF-8 (em-dashes, box-drawing). Also `(--Flag)` and `($var text)` inside double-quoted strings trigger subexpression parsing — use single quotes.

## YAML Bug (S15)
`az containerapp create --yaml` fails with "JSON value could not be converted to System.Boolean". Use CLI args instead.

## Git Bash MSYS Path Conversion (S87)
Git Bash on Windows converts `/partition_key` to `C:/Program Files/Git/partition_key` via MSYS path translation. Silently breaks Azure CLI `--partition-key-path` parameters. **Fix:** Use PowerShell for `az cosmosdb sql container` commands. Alternative: double slash `//partition_key`.

## AGNTCY SDK Import Resilience (S62)
agntcy_app_sdk breaking changes (removed BaseAgentProtocol) caused silent ImportError → 503. Fix: all agntcy imports wrapped in try/except with local ABC stubs.

## Stale Admin Dist (S11)
Always run `npm run build` in all 3 admin dirs before ACR build. Dockerfile `COPY admin/*/dist/` picks up whatever is on disk.

## Docker Layer Caching (S12)
Verify bundle hash matches local build after deploy. Hard-refresh (Ctrl+Shift+R) to bypass browser cache.

## Shopify App Version Deployment (S125)
KB procedure: `shopify-app-deploy`. Config file: `applications/Agent_Red/shopify.app.toml` (moved from repo root in ISOLATION-018). Deploy command: `shopify app deploy --force`. Creates a new versioned release in Shopify Partners Dashboard. **Critical:** All 5 URLs in the TOML must match the current production FQDN — check after any Azure environment migration. Verify in Dev Dashboard → Versions → newest Active version → "Privacy compliance webhook subscriptions". Three GDPR webhooks: `customers-data-request`, `customers-redact`, `shop-redact`.

## Documentation Site Deployment — agentredcx.com (S171)
KB procedure: `docs-site-deploy`. **CRITICAL: GitHub Pages uses `build_type=workflow`, source=main.** The `gh-pages` branch is NOT used.

**Correct procedure:**
1. Edit files in `docs-site/`
2. Commit to `main` branch
3. `git push origin main`
4. Workflow `.github/workflows/deploy-docs.yml` triggers automatically
5. Monitor: `gh run list --workflow=deploy-docs.yml --limit 1`
6. Verify: `curl -sI https://agentredcx.com/docs/`

**NEVER do any of these:**
- Push to `gh-pages` branch (not used)
- Run `docusaurus deploy` (broken on Windows, targets wrong branch)
- Use `git worktree` for gh-pages (unnecessary, wrong target)
- Modify SVG files from `branding/` (use as-is, use ThemedImage for light/dark)

## Production Deployment Verification Checklist (S171)
After deploying the API gateway to production, verify ALL external surfaces:

1. **API Health:** `curl https://agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io/health` → 200, correct version
2. **SPA Dashboard:** `curl -sI https://agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io/admin/provider/` → 200
3. **All 3 Admin Consoles:** standalone (`/admin/standalone/`), provider (`/admin/provider/`), shopify (`/admin/shopify/`) → 200
4. **Docs Site:** `curl -sI https://agentredcx.com/docs/` → 200 (separate deployment, see above)
5. **Storefront Widget:** Visit `https://blanco-9939.myshopify.com/` → widget launcher visible
6. **Upgrade Verification:** `python scripts/upgrade_verification.py phase-a --env production`
