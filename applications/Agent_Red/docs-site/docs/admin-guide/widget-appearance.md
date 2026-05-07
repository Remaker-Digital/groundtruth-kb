---
sidebar_position: 10
title: Widget appearance
description: Customize the chat widget's visual design — colors, position, launcher icon, dark mode, mobile behavior, and branding.
---

# Widget appearance

These settings control how the chat widget looks on your storefront. Changes take effect immediately for new page loads — customers who already have the widget open will see the changes when they refresh.

![Widget configuration page showing installation code, appearance settings, and live preview](/img/admin/widget-configuration.png)

## Primary color

| | |
|---|---|
| **Field** | `widget_primary_color` |
| **Type** | Color picker (hex) |
| **Default** | `#ff3621` |
| **Affects** | Widget |

The main accent color used for the launcher button, send button, links, and active elements. Choose a color that matches your storefront branding.

**Tips:**
- Use a color with sufficient contrast against white and dark backgrounds. Agent Red checks WCAG contrast ratios in the live preview.
- Avoid very light colors (pastel yellow, light grey) — they are difficult to see against most storefront backgrounds.
- The widget automatically derives hover and pressed states from the primary color.

---

## Background color

| | |
|---|---|
| **Field** | `widget_background_color` |
| **Type** | Color picker (hex) |
| **Default** | `#FFFFFF` |
| **Affects** | Widget |

The chat panel's main background color. This is the area behind the message list.

---

## Position

| | |
|---|---|
| **Field** | `widget_position` |
| **Type** | Dropdown |
| **Options** | `bottom-right`, `bottom-left` |
| **Default** | `bottom-right` |
| **Affects** | Widget |

Where the launcher button and chat panel appear on the page. Most stores use `bottom-right` because it does not interfere with left-aligned navigation or content.

**When to use bottom-left:**
- Your storefront has a right-side panel, sidebar, or another floating element in the bottom-right corner.
- You already have a different widget (cookie consent, feedback) in the bottom-right position.

---

## Offset X / Offset Y

| | |
|---|---|
| **Field** | `widget_offset_x`, `widget_offset_y` |
| **Type** | Number (0–100 pixels) |
| **Default** | `20` each |
| **Affects** | Widget |

The distance in pixels from the edge of the viewport to the launcher button. Increase these values to move the widget further from the corner.

---

## Agent display name

| | |
|---|---|
| **Field** | `widget_agent_display_name` |
| **Type** | Text (up to 100 characters) |
| **Default** | None (uses brand name) |
| **Affects** | Widget |

The name displayed in the chat header. If not set, falls back to the brand name from [Brand and tone](./brand-and-tone.md).

**Example:** "Ava from ACME Support" or "ACME Help Bot"

---

## Agent avatar URL

| | |
|---|---|
| **Field** | `widget_agent_avatar_url` |
| **Type** | URL |
| **Default** | None (uses default agent icon) |
| **Affects** | Widget |

A URL to an image displayed as the agent's avatar in the chat header and next to agent messages. Use a square image (recommended 64x64 pixels or larger).

**Tips:**
- Use a brand mascot, team photo, or abstract logo — something that humanizes the experience.
- Host the image on your own CDN or Shopify files for reliability. External URLs may be blocked by Content Security Policy on some storefronts.

---

## Agent title

| | |
|---|---|
| **Field** | `widget_agent_title` |
| **Type** | Text (up to 100 characters) |
| **Default** | None |
| **Affects** | Widget |

A subtitle displayed under the agent name in the chat header. Examples: "AI Support Assistant", "Available 24/7", "Typically replies instantly".

---

## Logo URL

| | |
|---|---|
| **Field** | `widget_logo_url` |
| **Type** | URL |
| **Default** | None |
| **Affects** | Widget |

A custom brand logo displayed in the widget header. If set, replaces the default Agent Red logo.

---

## Show branding

| | |
|---|---|
| **Field** | `widget_show_branding` |
| **Type** | Toggle (on/off) |
| **Default** | On |
| **Affects** | Widget |

When enabled, displays "Powered by Agent Red" in the widget footer with a link to the Agent Red documentation site.

**Turning it off:**
The White-Label Package (Enterprise only, $399/month) removes all Agent Red branding. On other tiers, the toggle is visible but branding cannot be fully removed.

---

## Color mode

| | |
|---|---|
| **Field** | `widget_color_mode` |
| **Type** | Dropdown |
| **Options** | `light`, `dark`, `auto` |
| **Default** | `auto` |
| **Affects** | Widget |

Controls the widget's color scheme.

| Setting | Behavior |
|---|---|
| **Light** | White/light backgrounds, dark text. Works on most storefronts. |
| **Dark** | Dark backgrounds, light text. Matches dark-themed storefronts. |
| **Auto** | Follows the customer's OS or browser preference (`prefers-color-scheme`). |

---

## Mobile enabled

| | |
|---|---|
| **Field** | `widget_mobile_enabled` |
| **Type** | Toggle (on/off) |
| **Default** | On |
| **Affects** | Widget |

Controls whether the widget appears on mobile devices (screen width under 768px).

**When to disable:**
- Your mobile storefront has a native support channel (e.g., in-app chat) and you do not want the widget to compete with it.
- Your mobile experience is not optimized for a floating widget.

---

## Launcher color

| | |
|---|---|
| **Field** | `widget_launcher_color` |
| **Type** | Color picker (hex) |
| **Default** | Uses primary color |
| **Affects** | Widget |

The color of the floating launcher button. By default, the launcher uses the widget's primary color. Set this field to give the launcher a distinct color — useful when the primary color is used for links and buttons inside the chat panel but you want the launcher to stand out differently on your storefront.

---

## Launcher icon

| | |
|---|---|
| **Field** | `widget_launcher_icon` |
| **Type** | Dropdown |
| **Options** | `chat`, `headset`, `help` |
| **Default** | `chat` |
| **Affects** | Widget |

The icon displayed on the floating launcher button.

| Icon | Visual | Connotation |
|---|---|---|
| **Chat** | Speech bubble | Conversational, modern |
| **Headset** | Headset/microphone | Support team, customer service |
| **Help** | Question mark | Help center, FAQ |

---

## Launcher size

| | |
|---|---|
| **Field** | `widget_launcher_size` |
| **Type** | Number (40–80 pixels) |
| **Default** | `56` |
| **Affects** | Widget |

The diameter of the floating launcher button in pixels.

---

## Border radius

| | |
|---|---|
| **Field** | `widget_border_radius` |
| **Type** | Number (0–20 pixels) |
| **Default** | `8` |
| **Affects** | Widget |

The corner roundness of the chat panel. `0` gives sharp corners, `20` gives very rounded corners.

---

## Bubble colors

Four color fields control the appearance of message bubbles:

| Field | Default | Description |
|---|---|---|
| `widget_agent_bubble_color` | Theme default | Background color of agent message bubbles |
| `widget_agent_bubble_text_color` | Theme default | Text color in agent message bubbles |
| `widget_customer_bubble_color` | Primary color | Background color of customer message bubbles |
| `widget_customer_bubble_text_color` | White | Text color in customer message bubbles |

If not set, these derive from the primary color and color mode automatically. Only override them if the automatic colors do not have sufficient contrast on your storefront.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
