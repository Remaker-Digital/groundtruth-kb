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
| `{{product_name}}` | The current product title | Product pages |
| `{{collection_name}}` | The current collection title | Collection pages |
| `{{page_handle}}` | The current page handle | All pages |

**Example:** A prompt with the text `Tell me about {{product_name}}` on a product page for "Classic Leather Wallet" becomes `Tell me about Classic Leather Wallet` when the customer clicks it.

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

## Best practices

- **Keep labels short.** Buttons with more than 5-6 words wrap awkwardly on mobile.
- **Limit to 3-4 prompts per page type.** More than that overwhelms the greeting area and pushes the input field down.
- **Use template variables on product pages.** A generic "Tell me about this product" is less engaging than "Tell me about {{product_name}}".
- **Test on mobile.** The greeting area has limited vertical space. Verify that your prompts display correctly on small screens.
- **Review analytics.** If a prompt is rarely clicked, replace it with something more relevant to what customers actually ask about.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
