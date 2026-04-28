---
name: Widget visibility is a deployment gate
description: NEVER report deployment success unless widget launcher is verified visible on both Shopify storefront and standalone admin UI when config is Active
type: feedback
---

NEVER report a deployment as successful unless the widget launcher is verified visible on both the Shopify storefront AND the standalone admin UI when the configuration status is Active.

**Why:** Owner explicitly flagged this as a critical failure. A deployment that passes all backend tests but leaves the widget invisible to end users is a broken deployment — it defeats the entire product purpose. Prior sessions reported deployments as successful based on API/auth checks alone without verifying the actual widget renders.

**How to apply:**
- After any build/deploy, verify the widget launcher renders (not just that auth returns 200)
- Check BOTH surfaces: Shopify storefront embed AND standalone admin console
- If the widget is not visible despite Active config, treat it as a P0 blocker — do not proceed with other work
- Include widget visibility in smoke test assertions (not just HTTP status checks)
- When writing test pipeline phases, include a "widget launcher visible" assertion
