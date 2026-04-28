---
name: Be careful distinguishing production vs staging environments
description: Double-check URLs and env vars before every API call — owner flagged accidental env confusion
type: feedback
---

Be VERY careful about distinguishing between production and staging environments. The owner flagged that I occasionally use the wrong URL without being aware.

**Why:** Accidentally calling a staging endpoint when intending production (or vice versa) can cause data corruption, misleading test results, or missed defects. The URLs are similar and easy to confuse.

**How to apply:**
- Production FQDN: `agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io`
- Staging FQDN: `agent-red-staging.orangeglacier-f566a4e7.eastus.azurecontainerapps.io`
- Always print/log which environment you're targeting before making API calls
- Use env vars from `.env.local` prefixed with `PRODUCTION_` or `STAGING_` accordingly
- When debugging, always state which environment the test targets in output
- Never assume — always verify the URL before executing
