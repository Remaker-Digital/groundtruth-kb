# S257 Widget Visual Gate — Staging Evidence

## Environment
- **Target:** STAGING v1.98.79
- **FQDN:** agent-red-staging.orangeglacier-f566a4e7.eastus.azurecontainerapps.io
- **Tenant:** remaker-digital-001 (professional tier)
- **Widget Key:** pk_live_c79a2bd0b3d4_864a...7ce4074f

## Evidence 1: Standalone Admin UI

**Timestamp:** 2026-04-04T02:55:26Z
**Method:** Chrome MCP → navigated to `/admin/standalone/?tenant=remaker-digital-001` → signed in with tenant API key → waited for dashboard + widget injection
**Screenshot ID:** ss_7396p4rr6 (saved to disk)

### DOM Verification
```json
{
  "agentRedLoaded": true,
  "widgetHost": true,
  "hostDisplay": "block",
  "sdkMethods": ["open","close","toggle","isOpen","setUnreadCount","hide","show","destroy","setLocale","setTheme","setConfigPartial","setTargetingRules"],
  "timestamp": "2026-04-04T02:55:26.860Z",
  "url": "https://agent-red-staging.orangeglacier-f566a4e7.eastus.azurecontainerapps.io/admin/standalone/?tenant=remaker-digital-001"
}
```

### Visual Confirmation
Blue circular launcher button visible at bottom-left of viewport, overlaying the admin dashboard sidebar. Dashboard shows 347 conversations, 100% resolution rate. Admin is authenticated and fully functional.

---

## Evidence 2: Shopify Storefront

**Timestamp:** 2026-04-04T04:32:39Z
**Method:** Chrome MCP → navigated to `https://blanco-9939.myshopify.com` → password gate bypassed → storefront homepage loaded with widget embed
**Screenshot ID:** ss_6416ck2gn (saved to disk)

### DOM Verification
```json
{
  "agentRedLoaded": true,
  "widgetHost": true,
  "hostDisplay": "block",
  "sdkMethods": ["open","close","toggle","isOpen","setUnreadCount","hide","show","destroy","setLocale","setTheme","setConfigPartial","setTargetingRules"],
  "timestamp": "2026-04-04T04:32:39.181Z",
  "url": "https://blanco-9939.myshopify.com/"
}
```

### Visual Confirmation
Red circular launcher button visible at bottom-right of viewport on the Shopify storefront homepage. Store title "Agent Red", hero banner, featured products section all loaded. Widget embed is served by the Shopify app embed block, not injected by admin console.

---

## What This Proves (Both Surfaces)
1. Widget key auth succeeds on BOTH surfaces (widget_key_hash present on tenant document)
2. /api/config returns valid configuration via widget key auth
3. widget.js bundle loads from the API gateway and executes without errors
4. Shadow DOM host element (#agent-red-widget) created with display:block
5. Preact Launcher component renders inside the closed shadow root
6. The launcher is visually present and clickable by a human user
7. **Standalone admin:** widget injection via StandaloneLayout.tsx works (activation-status poll → widget inject → SDK initialized)
8. **Shopify storefront:** widget embed via Shopify app embed block works (script tag in theme → config fetch → launcher render)

## What This Does NOT Prove
- Chat panel opens and AI responds (covered by deploy.py conversation smoke which PASSED)
- Widget renders on other Shopify pages beyond the homepage
- Widget renders for non-authenticated Shopify customers
