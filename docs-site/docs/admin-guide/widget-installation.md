---
sidebar_position: 14
title: Widget Installation
description: How to find your widget key, copy your embed snippet, and install the Agent Red chat widget on your website.
---

# Widget Installation

After activating your Agent Red configuration, the Widget page in your admin dashboard shows your widget key and a ready-to-use embed snippet. This page explains how to install the widget on your website.

## Finding your widget key

Your widget key is displayed in the **Installation** section at the top of the Widget page. The key follows the format `pk_live_...` and uniquely identifies your tenant.

### Copying the key

Click the clipboard icon next to the widget key to copy it to your clipboard. You can also select the text directly from the read-only input field.

### Rotating your key

If you believe your widget key has been compromised, click the **Rotate key** button. This immediately generates a new key and invalidates the old one.

:::warning Key rotation is immediate
Rotating your widget key immediately invalidates the current key. Any websites still using the old key will stop connecting to Agent Red. Update your embed code after rotating.
:::

## Installing the embed snippet

The Widget page displays a ready-to-use HTML snippet. Click **Copy snippet** to copy it to your clipboard.

### Placement

Paste the snippet before the closing `</body>` tag on every page where you want the chat widget to appear:

```html
<script
  src="https://YOUR_API_URL/widget.js"
  data-widget-key="pk_live_..."
  data-api-url="https://YOUR_API_URL"
></script>
```

The snippet includes your actual widget key and API URL — no manual editing is needed after copying.

### Shopify stores

For Shopify stores, the widget is installed automatically through the Agent Red Shopify app extension. No manual embed code is required. The extension handles widget injection, key configuration, and Shopify customer identity passthrough.

### Custom websites

For non-Shopify websites, paste the embed snippet into your site's HTML template. The widget loads asynchronously and does not block page rendering. It appears as a floating chat launcher in the bottom-right corner of the page (configurable under Widget Appearance settings).

## Verifying the installation

After adding the snippet to your website:

1. Visit your website in a browser
2. Look for the chat launcher icon in the bottom-right corner
3. Click the launcher to open the chat widget
4. Send a test message — you should receive an AI response within a few seconds

If the widget does not appear, check your browser's developer console for errors. Common issues include:

- **Invalid widget key:** Verify the key matches the one shown in your admin dashboard
- **Configuration not activated:** The widget requires an activated configuration. Check the activation status in your admin dashboard.
- **Content Security Policy:** If your site uses a strict CSP, you may need to allow scripts from your Agent Red API URL.

## Widget key not showing

If the Installation section shows "No widget key found," your configuration has not been activated yet. Complete the following steps:

1. Go to the **Configuration** page and fill in the required fields (brand name, brand voice)
2. Click **Save** to save your draft
3. Click **Activate** to publish your configuration

After activation, return to the Widget page — your widget key and embed snippet will be displayed.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
