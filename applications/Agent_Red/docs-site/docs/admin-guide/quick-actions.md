---
sidebar_position: 12
title: Quick action prompts
description: Configure pre-defined prompt buttons that appear in the chat widget greeting area — page-aware, template-driven shortcuts for common customer questions.
---

# Quick action prompts

Quick action prompts are pre-defined buttons that appear in the chat widget's greeting area. When a customer clicks one, the prompt text is sent as their first message, starting a conversation immediately without typing.

## How it works

1. You create prompt buttons in the admin console (e.g., "What's your return policy?", "Track my order").
2. You assign each prompt to one or more page types (product pages, collection pages, all pages, etc.).
3. The widget displays the relevant prompts as pill-shaped buttons below the greeting message.
4. When a customer clicks a button, the prompt text is sent as their message and the AI responds.

## Creating prompts

From the admin console, go to **Quick Actions** and click **Add prompt**.

| Field | Required | Description |
|---|---|---|
| **Label** | Yes | The text displayed on the button (keep under 40 characters). |
| **Prompt text** | Yes | The message sent when the customer clicks the button. Can be different from the label. |
| **Page types** | Yes | Which pages this prompt appears on (product, collection, cart, home, all). |
| **Sort order** | No | Controls the display order. Lower numbers appear first. |
| **Active** | Yes | Toggle to show or hide the prompt without deleting it. |

## Template variables

Prompt text supports template variables that are replaced at runtime with page-specific information:

| Variable | Replaced with | Available on |
|---|---|---|
| `\{\{product_name\}\}` | The current product title | Product pages |
| `\{\{collection_name\}\}` | The current collection title | Collection pages |
| `\{\{page_handle\}\}` | The current page handle | All pages |

**Example:** A prompt with the text `Tell me about \{\{product_name\}\}` on a product page for "Classic Leather Wallet" becomes `Tell me about Classic Leather Wallet` when the customer clicks it.

## Page type assignment

Each prompt can be assigned to one or more page types. The widget only shows prompts assigned to the current page type.

| Page type | Matches |
|---|---|
| `product` | Shopify product detail pages |
| `collection` | Shopify collection pages |
| `cart` | Cart page |
| `home` | Home page |
| `page` | Custom Shopify pages |
| `all` | Every page (use sparingly) |

**Tip:** Create general prompts (FAQ, contact info) assigned to `all`, and specific prompts (product questions, size guides) assigned to `product` only.

## Starter prompts

If you haven't created any quick actions yet, use the **Load starter prompts** button to seed your account with four pre-built prompts covering common e-commerce questions:

1. **Track my order** — Assigned to all pages
2. **Return policy** — Assigned to all pages
3. **Tell me about \{\{product_name\}\}** — Assigned to product pages (uses template variable)
4. **What's on sale?** — Assigned to collection pages

Starter prompts give you a working baseline that you can customize or replace. They are only loaded once — pressing the button again has no effect if prompts already exist.

## Page assignments

After creating quick action prompts, assign them to page types to control where they appear.

1. Go to **Quick Actions** and click the **Page assignments** tab.
2. Each row represents a page type (All pages, Home, Product, Collection, Cart, Search, Blog, Page, Other).
3. Assign up to **2 quick actions per page type** using the dropdown selectors (Slot 1 and Slot 2).
4. Optionally enable **Auto-open** per page type — the chat widget opens automatically after a configurable delay (1–60 seconds).

**Priority rule:** Page-specific assignments take precedence over the "All pages" fallback. If a product page has its own assignments, those are shown instead of the "All pages" defaults.

## Tuning and testing quick actions

### Testing your prompts

1. **Preview in the widget.** Visit your website (or use the widget preview in the admin console) and verify that the correct prompts appear on each page type.
2. **Click each button.** Confirm the AI produces a relevant, accurate response. If the response is poor, the issue is likely in your knowledge base — add or improve articles covering that topic.
3. **Test template variables.** On a product page, verify that `\{\{product_name\}\}` resolves to the actual product title. On a collection page, verify `\{\{collection_name\}\}` resolves correctly.
4. **Test on mobile.** Open your website on a phone or use browser developer tools to simulate a mobile viewport. Confirm buttons do not wrap awkwardly or overflow the greeting area.

### Tuning prompt effectiveness

After your first week of live traffic, review quick action performance:

1. **Check click rates.** In the Dashboard, review which quick actions customers are clicking. Low click rates indicate the prompt label is not resonating — try rewording it.
2. **Review conversation outcomes.** Filter Inbox conversations that started from a quick action click. If they frequently escalate, the prompt may be triggering questions your knowledge base cannot answer well.
3. **Iterate on prompt text.** The button label is what customers see; the prompt text is what gets sent. You can use a friendly label ("Need help with sizing?") with a more specific prompt text ("What size should I order? I need help with your sizing guide.").
4. **Rotate seasonal prompts.** Create holiday-specific or sale-specific quick actions and toggle them active/inactive as needed. Inactive prompts are preserved but not shown to customers.

### Common tuning patterns

| Symptom | Fix |
|---|---|
| Button is never clicked | Shorten the label, make it more specific, or replace with a more relevant topic |
| AI gives a vague response after click | Add or improve the knowledge base article for that topic |
| Template variable shows as raw text | Verify the page type assignment matches — `\{\{product_name\}\}` only works on product pages |
| Too many buttons crowd the greeting | Reduce to 2 prompts per page type. Use "All pages" for universal prompts only |

## Best practices

- **Keep labels short.** Buttons with more than 5-6 words wrap awkwardly on mobile.
- **Limit to 2 prompts per page type.** The page assignment system supports two slots per page type — this prevents overcrowding.
- **Use template variables on product pages.** A generic "Tell me about this product" is less engaging than "Tell me about \{\{product_name\}\}".
- **Test on mobile.** The greeting area has limited vertical space. Verify that your prompts display correctly on small screens.
- **Review analytics regularly.** If a prompt is rarely clicked, replace it with something more relevant to what customers actually ask about.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
