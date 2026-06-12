# Deploy: Environment Configuration

## Container App Parameters

| Parameter | Staging | Production |
|-----------|---------|------------|
| Container App | `agent-red-staging` | `agent-red-api-gateway` |
| Min Replicas | 0 | 2 |
| Max Replicas | 3 | 8 |
| Health Wait | 180s (cold start) | 90s |
| Resource Group | `Agent-Red` | `Agent-Red` |
| ACR | `acragentredeastus` | `acragentredeastus` |

## Build Phase Commands

### B.0: Clear API URL Hardcoding
```bash
echo "VITE_API_URL=" > admin/standalone/.env.local
echo "VITE_API_URL=" > admin/shopify/.env.local
echo "VITE_API_URL=" > admin/provider/.env.local
```

### B.1-B.3: Build Admin SPAs
```bash
cd admin/standalone && npx tsc && npx vite build
cd admin/shopify && npx tsc && npx vite build
cd admin/provider && npx tsc && npx vite build
```

### B.4: Build Widget
```bash
cd widget && npm run build
```

### B.5: Artifact Freshness Gate
Verify all 4 dist outputs were modified within the last 5 minutes:
- `admin/standalone/dist/index.html`
- `admin/shopify/dist/index.html`
- `admin/provider/dist/index.html`
- `widget/dist/agent-red-widget.iife.js`

**If ANY artifact is stale -> STOP. Stale artifacts cause 404s in production.**

### B.6: ACR Build
```bash
az acr build --registry acragentredeastus --image api-gateway:$1 --no-logs --file Dockerfile .
```
Use `--no-logs` to avoid Windows charmap crash. Verify image:
```bash
az acr repository show-tags --name acragentredeastus --repository api-gateway --orderby time_desc --top 3 -o table
```

## Post-Deploy Verification

### D.1: Version Header
```bash
curl -si https://<FQDN>/health | grep X-Product-Version
```

### D.2: Admin SPAs Return 200
```bash
curl -o /dev/null -w "%{http_code}" https://<FQDN>/admin/standalone/
curl -o /dev/null -w "%{http_code}" https://<FQDN>/admin/shopify/
curl -o /dev/null -w "%{http_code}" https://<FQDN>/admin/provider/
```

### D.3: Widget Accessible
```bash
curl -s https://<FQDN>/widget.js | wc -c
# Must be > 1,000 bytes
```

### D.4: Upgrade Verification (35 assertions per tenant)
```bash
python scripts/upgrade_verification.py phase-c --env <environment> --snapshot <phase_a_snapshot> --new-version <version>
```

## Rollback
```bash
az containerapp update --name <CONTAINER_APP> --resource-group Agent-Red --image acragentredeastus.azurecr.io/api-gateway:<PREVIOUS_VERSION>
```
Then run Tier 0 regression tests to confirm rollback succeeded.
