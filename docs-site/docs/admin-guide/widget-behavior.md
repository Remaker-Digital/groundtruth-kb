---
sidebar_position: 11
title: Widget behavior
description: Configure auto-open, offline mode, pre-chat forms, chat rating, sound notifications, and file upload for the chat widget.
---

# Widget behavior

These settings control how the widget behaves — when it opens, what happens outside business hours, and what information is collected from customers.

## Auto-open widget

| | |
|---|---|
| **Field** | `widget_auto_open` |
| **Type** | Toggle (on/off) |
| **Default** | Off |
| **Affects** | Widget |

When enabled, the chat panel opens automatically after a configurable delay. The customer does not need to click the launcher button.

**When to enable:**
- You are running a promotion and want to proactively engage visitors.
- Your store has a high bounce rate and you want to offer help before visitors leave.

**When to leave off:**
- Auto-opening can feel intrusive, especially on mobile. Many customers prefer to initiate conversations on their own terms.
- If your storefront has other popups (email capture, cookie consent), adding an auto-open chat widget creates a crowded experience.

---

## Auto-open delay

| | |
|---|---|
| **Field** | `widget_auto_open_delay` |
| **Type** | Number (1–120 seconds) |
| **Default** | `5` |
| **Affects** | Widget |

How long to wait after page load before auto-opening the widget (only relevant if auto-open is enabled).

**Guidance:**
- **1–3 seconds:** Feels aggressive. The page has barely loaded.
- **5–10 seconds:** The customer has had time to orient themselves. This is the recommended range.
- **15–30 seconds:** Delayed enough that the customer has started engaging with the page content. Good for product detail pages.
- **60+ seconds:** Only use for long-form content pages where the customer is expected to read for a while.

---

## Offline behavior

| | |
|---|---|
| **Field** | `widget_offline_behavior` |
| **Type** | Dropdown |
| **Options** | `ai_only`, `show_form`, `hide_widget` |
| **Default** | `ai_only` |
| **Affects** | Widget |

What the widget does outside your configured support hours.

| Setting | Behavior |
|---|---|
| **AI only** | The widget stays active and the AI handles conversations. No human escalation available. The AI mentions that human support is unavailable and provides your support hours. |
| **Show form** | The widget displays a "leave a message" form (name, email, message). Submissions are stored in the admin Inbox for your team to follow up during business hours. |
| **Hide widget** | The widget is completely hidden. Customers see no chat option. |

**Recommendation:** `ai_only` is the best choice for most stores because it provides 24/7 support for questions the AI can answer. Only use `show_form` or `hide_widget` if you do not want the AI handling conversations outside business hours.

---

## Offline message

| | |
|---|---|
| **Field** | `widget_offline_message` |
| **Type** | Multi-line text (up to 500 characters) |
| **Default** | None |
| **Affects** | Widget |

A message displayed when the widget is in offline mode (only relevant if offline behavior is `show_form`). Example: *"We're not available right now, but leave a message and we'll get back to you within 24 hours."*

---

## Pre-chat form

| | |
|---|---|
| **Field** | `widget_pre_chat_enabled` |
| **Type** | Toggle (on/off) |
| **Default** | Off |
| **Affects** | Widget |

When enabled, customers must fill out a form (name, email, and any custom fields you configure) before the conversation starts.

**When to enable:**
- You need to identify customers before they chat (e.g., to look up their account or order).
- Your team needs an email address to follow up on escalated conversations.
- You want to pre-qualify leads.

**When to leave off:**
- Pre-chat forms add friction. Every required field reduces the number of customers who start a conversation.
- If Persistent Customer Memory is enabled, the AI can often identify returning customers without a form.

---

## Pre-chat form fields

| | |
|---|---|
| **Field** | `widget_pre_chat_fields` |
| **Type** | JSON array |
| **Default** | None |
| **Affects** | Widget |

Custom fields for the pre-chat form. Each field has a name, type (text, email, phone, dropdown), and whether it is required.

**Example:**
```json
[
  {"name": "name", "type": "text", "required": true, "label": "Your name"},
  {"name": "email", "type": "email", "required": true, "label": "Email address"},
  {"name": "order_number", "type": "text", "required": false, "label": "Order number (if applicable)"}
]
```

---

## Chat rating

| | |
|---|---|
| **Field** | `widget_chat_rating_enabled` |
| **Type** | Toggle (on/off) |
| **Default** | Off |
| **Affects** | Widget |

When enabled, customers see a thumbs up/thumbs down prompt after the conversation resolves. They can optionally leave a comment. Ratings appear in the Analytics section of the admin console.

**Recommendation:** Enable this. Customer feedback is valuable for tuning your knowledge base and identifying gaps. The prompt is unobtrusive — customers can dismiss it without rating.

---

## Sound enabled

| | |
|---|---|
| **Field** | `widget_sound_enabled` |
| **Type** | Toggle (on/off) |
| **Default** | On |
| **Affects** | Widget |

Plays a notification sound when the AI sends a message and the widget is minimized (not visible on screen). The sound is a short, subtle tone.

**When to disable:**
- Your storefront has its own audio (music, video) and the notification sound conflicts.
- You serve a context where unexpected sounds are inappropriate (e.g., B2B during business meetings).

---

## File upload

| | |
|---|---|
| **Field** | `widget_file_upload_enabled` |
| **Type** | Toggle (on/off) |
| **Default** | On |
| **Affects** | Widget |

Allows customers to attach images and files in the chat. Useful for sending screenshots of issues, order confirmations, or product photos.

**Supported file types:** Images (JPG, PNG, GIF, WebP), documents (PDF).
**Maximum file size:** 10 MB.

---

## Page rules

| | |
|---|---|
| **Field** | `widget_page_rules` |
| **Type** | Tag list (glob patterns, up to 20 rules) |
| **Default** | None (widget appears on all pages) |
| **Affects** | Widget |

Controls which pages the widget appears on using URL path patterns.

**Pattern syntax:**
- `*` matches any characters within a path segment.
- `**` matches any path depth.

**Examples:**

| Pattern | Matches |
|---|---|
| `/products/*` | All product pages |
| `/collections/**` | All collection and sub-collection pages |
| `/pages/faq` | Only the FAQ page |
| `/checkout*` | Checkout pages (hides widget during checkout) |

**How rules work:**
- If no rules are set, the widget appears on all pages.
- If rules are set, the widget only appears on pages that match at least one rule.
- To hide the widget on specific pages, set rules that match the pages where you *want* the widget.

---

## Header text

| | |
|---|---|
| **Field** | `widget_header_text` |
| **Type** | Text (up to 100 characters) |
| **Default** | None (uses agent display name) |
| **Affects** | Widget |

Custom title text for the chat panel header. If not set, uses the agent display name or brand name.

---

## Input placeholder text

| | |
|---|---|
| **Field** | `widget_input_placeholder` |
| **Type** | Text (up to 200 characters) |
| **Default** | `Type a message...` |
| **Affects** | Widget |

The placeholder text shown in the message input field before the customer starts typing.

**Examples:**
- `Ask us anything...`
- `How can we help?`
- `Type your question here`

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
