# R9b: CDN / Static Hosting Architecture

**Status:** Design Document (Cycle 12)
**Priority:** Scale optimization — implement when approaching 50+ concurrent tenants
**Owner:** Remaker Digital

## Problem Statement

The current architecture serves all static assets (admin SPAs, widget bundle, provider console)
from the API Gateway container. This approach works at current scale but will encounter
performance and cost pressure as tenant count grows:

1. **Static assets compete with API requests** for Container Apps compute budget
2. **No edge caching** — all requests hit the single Azure East US region
3. **Widget bundle latency** — storefronts in other regions see higher TTFB
4. **Cold start penalty** — Container Apps consumption plan cold starts affect static asset delivery

## Current Architecture

```
Browser → Container Apps (api-gateway)
           ├── /widget.js              → Static file from container filesystem
           ├── /admin/standalone/**    → SPA HTML + JS/CSS bundles
           ├── /admin/provider/**      → SPA HTML + JS/CSS bundles
           ├── /admin/shopify/**       → Shopify-embedded admin (proxied)
           └── /api/**                 → FastAPI endpoints
```

**Static assets served today:**
- Widget bundle: `widget/dist/agent-red-widget.iife.js` (~120KB gzipped)
- Standalone admin: `admin/standalone/dist/` (Vite build, ~350KB gzipped)
- Provider admin: `admin/provider/dist/` (Vite build, ~300KB gzipped)
- Shopify admin: `admin/shopify/dist/` (Vite build, ~400KB gzipped)

## Proposed Architecture

```
Browser → Azure CDN / Front Door
           ├── /widget.js              → CDN edge cache (24h TTL, cache-bust via query param)
           ├── /admin/standalone/**    → CDN edge cache (content-hash filenames)
           ├── /admin/provider/**      → CDN edge cache (content-hash filenames)
           ├── /admin/shopify/**       → CDN edge cache (content-hash filenames)
           └── /api/**                 → Passthrough to Container Apps (no caching)

CDN Origin → Azure Blob Storage (static website hosting)
             └── $web container with all static assets

API requests → Container Apps (api-gateway) — no static file serving
```

## Implementation Plan

### Phase 1: Azure Blob Storage Static Website

1. Create storage account `stagentredstatic` (LRS, hot tier)
2. Enable static website hosting on `$web` container
3. Configure custom domain (e.g., `static.agentredcx.com`)
4. Upload static assets during CI/CD pipeline (after `npm run build`)

### Phase 2: Azure CDN Profile

1. Create Azure CDN profile (Standard Microsoft tier — cheapest)
2. Create CDN endpoint pointing to Blob Storage origin
3. Configure caching rules:
   - `*.js`, `*.css` with content-hash filenames: 365-day cache
   - `index.html`: 5-minute cache (or no-cache with revalidation)
   - `widget.js`: 24-hour cache with `?v={version}` cache-busting
4. Configure CORS headers for widget cross-origin embedding
5. Enable HTTPS with managed certificate

### Phase 3: API Gateway Refactoring

1. Remove static file serving from FastAPI `StaticFiles` mounts
2. Update `Dockerfile` to exclude admin dist/ and widget dist/ from image
3. Update health check to not depend on static files
4. Reduce container image size (~1.2GB → ~800MB estimated)

### Phase 4: DNS & Routing

1. Option A: Azure Front Door (premium, global load balancing)
   - Single domain, path-based routing to CDN vs API
   - Higher cost (~$35/month base)

2. Option B: Separate subdomains (simpler, cheaper)
   - `api.agentredcx.com` → Container Apps
   - `static.agentredcx.com` → CDN
   - Widget script tag updates needed
   - Lower cost (~$10/month for CDN)

**Recommendation:** Option B (separate subdomains) for launch. Migrate to Front Door
post-launch if single-domain routing becomes a requirement.

## Cost Impact

| Component | Current | With CDN (Option B) |
|-----------|---------|---------------------|
| Container Apps | ~$25/mo | ~$20/mo (reduced requests) |
| Blob Storage | $0 | ~$1/mo (static hosting) |
| CDN | $0 | ~$10/mo (Standard tier) |
| **Total** | **~$25/mo** | **~$31/mo** |

Net cost increase: ~$6/month, offset by:
- Reduced Container Apps request units (static requests eliminated)
- Lower cold start frequency (fewer concurrent requests)
- Global edge delivery (improved UX in non-US regions)

## Migration Checklist

- [ ] Create storage account with static website hosting
- [ ] Update CI/CD to deploy static assets to Blob Storage
- [ ] Create CDN profile and endpoint
- [ ] Configure custom domain with SSL
- [ ] Set caching rules (content-hash: 365d, HTML: 5min, widget: 24h)
- [ ] Configure CORS for widget embedding
- [ ] Update widget `<script>` tag documentation
- [ ] Update admin SPA `VITE_API_URL` environment variable
- [ ] Remove `StaticFiles` mounts from FastAPI
- [ ] Test all three admin surfaces load correctly from CDN
- [ ] Update Dockerfile to exclude static assets
- [ ] Update deployment procedure documentation
- [ ] Monitor CDN hit ratio for 1 week post-migration

## Trigger Criteria

Implement this when:
1. Monthly conversation volume exceeds 10,000 cross-tenant, OR
2. Container Apps cold starts are causing user-visible delays (>3s TTFB), OR
3. Tenant count exceeds 30 active tenants, OR
4. Multi-region deployment is needed

## Dependencies

- Azure Blob Storage account (new resource)
- Azure CDN profile (new resource)
- DNS management access (for custom domain)
- CI/CD pipeline update (GitHub Actions or manual deploy script)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
