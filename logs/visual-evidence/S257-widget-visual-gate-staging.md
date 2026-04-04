# S257 Widget Visual Gate — Staging Evidence

## Environment
- **Target:** STAGING v1.98.78
- **FQDN:** agent-red-staging.orangeglacier-f566a4e7.eastus.azurecontainerapps.io
- **Tenant:** remaker-digital-001 (professional tier)
- **Widget Key:** pk_live_c79a2bd0b3d4_864a...7ce4074f
- **Timestamp:** 2026-04-04T01:39:24Z (Chrome MCP capture)

## Method
Chrome MCP browser automation:
1. Navigated to staging gateway origin
2. Injected widget embed code (same-origin, `data-widget-key` + `data-api-url`)
3. Waited 8s for widget init (config fetch + Shadow DOM mount + Preact render)
4. Verified via JavaScript: `window.AgentRed` loaded, `#agent-red-widget` host exists, `display: block`
5. Captured screenshot showing launcher bubble (bottom-left, blue circle with chat icon)

## DOM Verification
```json
{
  "agentRedLoaded": true,
  "widgetHost": true,
  "hostDisplay": "block",
  "timestamp": "2026-04-04T01:39:43.030Z"
}
```

## Console State
No errors or warnings captured during widget initialization.

## Screenshot
Chrome MCP screenshot ID: ss_9136ipta8
Saved to disk by Chrome MCP extension.
Visual confirmation: blue circular launcher button visible at bottom-left of viewport.

## What This Proves
1. Widget key auth succeeds (widget_key_hash present on tenant document after S257 self-heal repair)
2. /api/config returns valid configuration with widget settings
3. widget.js bundle loads and executes without errors
4. Shadow DOM host element is created and rendered with display:block
5. Preact Launcher component renders inside the shadow root
6. The launcher is visually present and would be clickable by a human user

## What This Does NOT Prove
- Widget functionality in the standalone admin console (requires admin auth flow)
- Widget functionality on the Shopify storefront (requires store password + app embed)
- Chat panel opens and AI responds (requires conversation pipeline health)
- These are covered by TestAdminWidgetReadiness and TestStorefrontWidgetReadiness in the Phase 3/16 test suite.
