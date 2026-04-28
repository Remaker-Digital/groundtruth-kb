---
name: SPEC-1840 tenant-aware CORS decision
description: Owner chose tenant-aware CORS for widget domain restriction (not auth-only)
type: project
---

SPEC-1840 (widget key domain restriction): Owner selected tenant-aware CORS — full per-tenant allowed origins list supporting Shopify domains + custom domains. Not auth-only.

**Why:** Custom domain support is needed beyond Shopify storefronts. Some merchants use headless commerce with custom domains.

**How to apply:** Implementation must include per-tenant origin allowlist in tenant config (not just Shopify shop_domain). CORS middleware validates Origin against tenant's allowed_origins list.
