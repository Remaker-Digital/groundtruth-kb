---
sidebar_position: 14
title: Widget Installation
description: How to install the Agent Red chat widget on Shopify, WordPress, Squarespace, Wix, and any custom website.
---

# Widget Installation

After activating your Agent Red configuration, the Widget page in your admin dashboard shows your widget key and a ready-to-use embed snippet. This page explains how to install the widget on any website.

## Finding your widget key

Your widget key is displayed in the **Installation** section at the top of the Widget page. The key follows the format `pk_live_...` and uniquely identifies your tenant.

### Copying the key

Click the clipboard icon next to the widget key to copy it to your clipboard. You can also select the text directly from the read-only input field.

### Rotating your key

If you believe your widget key has been compromised, click the **Rotate key** button. This immediately generates a new key and invalidates the old one.

:::warning Key rotation is immediate
Rotating your widget key immediately invalidates the current key. Any websites still using the old key will stop connecting to Agent Red. Update your embed code after rotating.
:::

## The embed snippet

The Widget page displays a ready-to-use HTML snippet. Click **Copy snippet** to copy it to your clipboard.

```html
<script
  src="https://YOUR_API_URL/widget.js"
  data-widget-key="pk_live_..."
  data-api-url="https://YOUR_API_URL"
></script>
```

The snippet you copy from the Widget page includes your actual widget key and API URL — no manual editing is needed.

---

## Installation by platform

### Shopify stores

For Shopify stores, the widget is installed automatically through the Agent Red Shopify app extension. No manual embed code is required.

**What the extension handles:**
- Widget script injection on all storefront pages
- Widget key configuration
- Shopify customer identity passthrough (logged-in customers are automatically identified)
- Page type detection for quick action targeting

**If the widget does not appear on your Shopify store:**
1. Check that the Agent Red app extension is enabled in your Shopify admin under **Online Store → Themes → Customize → App embeds**.
2. Ensure the app embed toggle is turned **on**.
3. Save and preview your theme.

### WordPress

1. **Copy the embed snippet** from the Widget page in the Agent Red admin console.
2. In your WordPress admin, go to **Appearance → Theme File Editor** (or **Appearance → Editor** in older versions).
3. Select your theme's `footer.php` file from the file list on the right.
4. Paste the snippet just before the `</body>` tag.
5. Click **Update File**.

**Alternative — using a plugin:**
If you prefer not to edit theme files directly, use a plugin like "Insert Headers and Footers" or "WPCode":

1. Install and activate the plugin.
2. Go to the plugin's settings (usually under **Settings** or **Code Snippets**).
3. Add a new footer snippet.
4. Paste the Agent Red embed snippet.
5. Set it to load on all pages and save.

**WordPress-specific notes:**
- The widget works with all WordPress themes (classic and block themes).
- If you switch themes, you need to re-add the snippet to the new theme's footer.
- Using a header/footer plugin persists the snippet across theme changes.
- If your site uses a caching plugin (WP Super Cache, W3 Total Cache, etc.), clear the cache after adding the snippet.

### Squarespace

1. **Copy the embed snippet** from the Widget page in the Agent Red admin console.
2. In your Squarespace admin, go to **Settings → Advanced → Code Injection**.
3. Paste the snippet into the **Footer** field.
4. Click **Save**.

The widget appears on all pages of your Squarespace site immediately.

**Squarespace-specific notes:**
- Code Injection is available on Business and Commerce plans. Basic and Personal plans do not support custom code injection.
- If you need the widget on specific pages only, use the Agent Red [page visibility rules](/docs/admin-guide/widget-appearance) instead of Squarespace page-level controls.

### Wix

1. **Copy the embed snippet** from the Widget page in the Agent Red admin console.
2. In your Wix dashboard, go to **Settings → Custom Code** (under Advanced).
3. Click **Add Custom Code**.
4. Paste the Agent Red snippet into the code field.
5. Set the placement to **Body - end**.
6. Choose **All pages** under "Add Code to Pages."
7. Click **Apply**.

**Wix-specific notes:**
- Custom Code requires a Wix Premium plan (not available on free plans).
- Wix Editor X (Studio) uses the same Settings → Custom Code path.
- After adding the code, preview your site to verify the widget appears.

### Webflow

1. **Copy the embed snippet** from the Widget page in the Agent Red admin console.
2. In your Webflow project, go to **Project Settings → Custom Code**.
3. Paste the snippet into the **Footer Code** field.
4. Click **Save Changes**.
5. **Publish** your site for the changes to take effect.

**Webflow-specific notes:**
- Custom Code is available on all paid Webflow plans.
- The snippet must be republished to appear on the live site — saving alone is not sufficient.

### Static HTML / custom website

For any website where you have access to the HTML source:

1. **Copy the embed snippet** from the Widget page in the Agent Red admin console.
2. Open your HTML file(s) in a text editor.
3. Paste the snippet just before the closing `</body>` tag:

```html
<!DOCTYPE html>
<html>
<head>
  <title>Your Page</title>
</head>
<body>
  <!-- Your page content -->

  <!-- Agent Red Chat Widget -->
  <script
    src="https://YOUR_API_URL/widget.js"
    data-widget-key="pk_live_..."
    data-api-url="https://YOUR_API_URL"
  ></script>
</body>
</html>
```

4. Upload the modified files to your web server.

### Single-page applications (React, Vue, Next.js)

For SPAs, add the widget script to your application shell so it loads once and persists across route changes.

**React / Next.js:**

Add the script tag to your `index.html` (Create React App) or `_document.tsx` (Next.js) before the closing `</body>` tag:

```html
<script
  src="https://YOUR_API_URL/widget.js"
  data-widget-key="pk_live_..."
  data-api-url="https://YOUR_API_URL"
></script>
```

For Next.js App Router, you can also use the `Script` component in your root layout:

```jsx
import Script from 'next/script';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <Script
          src="https://YOUR_API_URL/widget.js"
          data-widget-key="pk_live_..."
          data-api-url="https://YOUR_API_URL"
          strategy="afterInteractive"
        />
      </body>
    </html>
  );
}
```

**SPA-specific notes:**
- The widget handles client-side routing automatically — it persists across route changes without reloading.
- The widget SDK is available on `window.AgentRed` for programmatic control (open, close, send messages).
- The widget renders in a closed Shadow DOM to prevent CSS conflicts with your application styles.

---

## Verifying the installation

After adding the snippet to your website:

1. Visit your website in a browser (use an incognito/private window to avoid caching issues).
2. Look for the chat launcher icon in the bottom-right corner (or wherever you configured the launcher position).
3. Click the launcher to open the chat widget.
4. Send a test message — you should receive an AI response within a few seconds.
5. Verify that your brand colors, agent name, and greeting message appear correctly.

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| Widget does not appear | Configuration not activated | Go to Configuration page, save your settings, and click Activate |
| Widget does not appear | Invalid widget key | Verify the key in the snippet matches the key shown on the Widget page |
| Widget appears but shows an error | API URL incorrect | Check that `data-api-url` matches the URL shown on the Widget page |
| Widget blocked by browser | Content Security Policy | Add your Agent Red API URL to your site's CSP `script-src` and `connect-src` directives |
| Widget appears on wrong pages | No page visibility rules | Configure page visibility rules on the Widget page to control where the widget appears |
| Widget loads slowly | Large page or slow connection | The widget loads asynchronously and does not block page rendering. If the page itself is slow, the widget may take longer to appear |
| Widget does not match brand colors | Settings not saved | Check the Widget page for unsaved changes. Save and activate. |

## Widget key not showing

If the Installation section shows "No widget key found," your configuration has not been activated yet. Complete the following steps:

1. Go to the **Configuration** page and fill in the required fields (brand name, brand voice).
2. Click **Save** to save your draft.
3. Click **Activate** to publish your configuration.

After activation, return to the Widget page — your widget key and embed snippet will be displayed.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
