# Workflow 3: Widget Activation & Configuration

> **Audience:** UX Designer, Product Owner
> **Environment:** Shopify theme editor (admin.shopify.com/store/blanco-9939/themes/.../editor)
> **Last Updated:** 2026-02-04

---

## Purpose

This workflow documents how a merchant activates the Agent Red chat widget on their Shopify storefront using the Shopify Theme Editor's App Embeds feature. This is the standard Shopify pattern for enabling theme app extensions.

---

## Step 1: Open the Theme Editor

**URL:** `https://admin.shopify.com/store/blanco-9939/themes/149122777271/editor`

**How to get here:**
1. In Shopify admin, navigate to **Online Store** (under Sales channels)
2. Click **Themes**
3. On the current theme ("test-data"), click **Customize**

**What the merchant sees:**
- Theme editor with a live preview of the homepage on the right
- Left sidebar showing the page structure:
  - **Header:** Announcement bar, Header, Add section
  - **Template:** Image banner, Featured collection, Image with text, Rich text, Add section
  - **Footer:** Add section, Footer
- Top bar: Theme name ("test-data"), "Live" badge (green), device preview buttons, Save button
- The storefront preview shows the homepage with all Agent Red content and the chat widget launcher (if enabled)

**Screenshot reference:** `ss_7646s69ib` — Theme editor showing homepage sections

**UX Notes:**
- The theme editor is the standard Shopify interface for all theme customization
- Merchants are familiar with this interface from other Shopify workflows
- The left sidebar shows all homepage sections that were created via the Theme Files API

---

## Step 2: Navigate to App Embeds

**What the merchant does:**
1. In the theme editor left sidebar, look for the icon bar on the far left
2. Click the **App embeds icon** (puzzle piece / grid icon, third from top)

**What the merchant sees:**
- Left sidebar changes to show **"App embeds"** heading
- Search box: "Search app embeds"
- **"Agent Red Chat"** listed with subtitle "Agent Red Customer Ex..."
- **Toggle switch** next to the app name (controls whether the widget is active)
- Note at bottom: "Find apps built for themes on the Shopify App Store."

**Screenshot reference:** `ss_4485b7dr9` — App embeds panel showing Agent Red Chat toggle

**UX Notes:**
- App embeds is the standard Shopify mechanism for injecting app code into the theme
- The toggle is immediately visible — no need to search or navigate menus
- Only one app embed is shown (Agent Red Chat) — clean, uncluttered

---

## Step 3: Enable the Widget

**What the merchant does:**
1. Click the **toggle switch** next to "Agent Red Chat" to turn it ON
2. The toggle moves to the right and turns green
3. Click **Save** (top-right of theme editor)

**What happens:**
- The widget launcher (red circle with chat icon) appears in the bottom-right corner of the storefront preview
- The widget is now active on ALL pages of the storefront
- Visitors can click the launcher to open the chat panel

**UX Notes:**
- Single toggle activation — no additional configuration required to get started
- Widget appears immediately in the theme editor preview
- Save is required to publish the change to the live storefront
- The widget loads the pre-built IIFE bundle from Shopify's CDN (deployed via `shopify app deploy`)

---

## Step 4: Verify Widget on Live Storefront

**What the merchant does:**
1. After saving, navigate to the live storefront (e.g., `blanco-9939.myshopify.com`)
2. Confirm the red chat widget launcher is visible in the bottom-right corner
3. Click the launcher to verify the chat panel opens

**What the merchant sees:**
- **Widget launcher:** Red circle with speech bubble icon, fixed position bottom-right
- **Chat panel (when opened):**
  - Header: "Chat with us" with status indicator and "Agent Red" label
  - Close button (X)
  - Message input: "Type a message..." placeholder
  - File attach button (paperclip)
  - Send button (arrow)
  - Footer: "Powered by Agent Red"

**UX Notes:**
- The widget loads automatically via the Shopify Theme App Extension
- Shadow DOM isolates widget styles from the merchant's theme CSS
- The widget connects to the production API Gateway for AI-powered conversations
- Widget appearance is configurable via the admin dashboard (colors, position, branding)

---

## Step 5: Disable the Widget (If Needed)

**What the merchant does:**
1. Return to the theme editor
2. Navigate to App embeds
3. Click the toggle to turn Agent Red Chat OFF
4. Click Save

**What happens:**
- The widget launcher disappears from the storefront
- No widget code is loaded on the storefront (clean removal)
- All conversation history is preserved — re-enabling the widget restores full functionality

---

## Technical Details

### Widget Delivery Architecture

```
Shopify Theme App Extension
    └── extensions/agent-red-chat/
        ├── shopify.extension.toml     (extension manifest)
        ├── blocks/
        │   └── agent-red-chat.liquid  (Liquid template, app embed block)
        └── assets/
            └── agent-red-widget.iife.js  (compiled widget bundle, ~17KB gzip)
```

### How It Works
1. Shopify loads the Theme App Extension's Liquid template on every page
2. The Liquid template injects the widget IIFE script
3. The script creates a custom element (`<agent-red-widget>`) with Shadow DOM (closed)
4. The launcher button is rendered inside the Shadow DOM
5. Clicking the launcher creates an iframe for the conversation panel (full DOM isolation)
6. The widget reads configuration from the API Gateway (`/api/config`)
7. Conversations use HTTP POST (messages), SSE (AI streaming), and WebSocket (typing indicators)

### Widget SDK
The widget exposes a JavaScript SDK on `window.AgentRed`:

```javascript
AgentRed.open()           // Open the chat panel
AgentRed.close()          // Close the chat panel
AgentRed.toggle()         // Toggle open/closed
AgentRed.isOpen()         // Check if panel is open
AgentRed.setUnreadCount(n) // Set unread badge count
AgentRed.hide()           // Hide the launcher
AgentRed.show()           // Show the launcher
AgentRed.destroy()        // Remove widget completely
```

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
