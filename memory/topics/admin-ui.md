# Admin UI — Operational Patterns

> Full architecture: KB DOC-ADMIN-UI

## Three Admin Surfaces (Critical Distinction)
- **Standalone Admin** (`admin/standalone/`) — merchant-facing. How tenant administrators manage their own tenancy. Public, documented, customer-visible. Authenticated via API key.
- **Shopify Admin** (`admin/shopify/`) — merchant-facing. Same functionality embedded within Shopify's admin shell. Authenticated via Shopify session token.
- **Service Provider Administrator (SPA) Console** (`admin/provider/`) — owner/operator-facing ONLY. Used by Remaker Digital to administer the entire multi-tenant platform. PRIVATE — must NEVER be mentioned in public documentation.

"Standalone" references in public docs are CORRECT (merchant admin). "Provider"/"SPA Console" references in public docs are WRONG and must be removed.

## Frontend-backend enum alignment
Always match TypeScript types to exact backend enum values. Python `MessageRole` enum: `CUSTOMER="customer"`, `AI="ai"`, `SYSTEM="system"`, `HUMAN_AGENT="human_agent"`. TS union must include `'ai'`, not `'agent'`. The S86 Inbox bug (all AI responses rendered as "Customer") was caused by TS checking `message.role === 'agent'` which never matched.

## False-success on 200 with failure flag (S85)
Backend may return 200 with `sent: false` when downstream delivery fails. Frontend must check the payload flag, not just HTTP status. Pattern: `if (res.ok && data.sent)` for success, `else if (res.ok && !data.sent)` for delivery failure.

## Static vs dynamic filter dropdowns (S85)
Dynamically populating filter options from aggregated data hides categories with zero items. Use a static options array matching the backend enum so all lifecycle states are always filterable.

## WidgetPreview is deliberately orphaned (S189)
The `WidgetPreview` component in `Widget.tsx` is defined but NOT rendered. This is intentional — the live chat widget embedded on the admin page IS the configuration preview. Do NOT add a two-column layout with WidgetPreview. Owner explicitly corrected this: "We previously removed this deliberately, because the functioning chat UI is the preview for the chat UI configuration."

## Widget panel width/height/shadow bug (S189)
Panel width, height, and shadow intensity controls don't update the live chat widget because the iframe's inline styles (`width`, `height`, `box-shadow`) are set once at creation in `widget/src/index.ts:336-340` and never re-applied when `setConfigPartial()` updates the store. Fix: add a store subscription that updates iframe dimensions/shadow when config changes.

## Pre-chat form config layers (S86)
`fields.yaml` `platform_default` only applies when no stored value exists. Changing the default doesn't affect tenants with an active config already stored. Additionally, widget IIFE bundles on Shopify CDN may cache old initialization logic — always run `npx shopify app deploy --force` after widget changes.

## fields.yaml max_length for data URI fields (S84)
`widget_agent_avatar_url` max_length was 500 (suitable for external URLs). Avatar upload stores base64 data URIs inline (~43KB for 32KB PNG, up to ~350KB). Validation silently rejected → generic 500. Fixed to `400000`. Rule: any field storing base64 data URIs needs max_length ≥400000.
