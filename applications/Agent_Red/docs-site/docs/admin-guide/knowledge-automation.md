---
sidebar_position: 14
title: Knowledge automation
description: Automatically populate your knowledge base from your Shopify storefront and industry templates, with AI-generated configuration suggestions.
---

# Knowledge automation

Agent Red can automatically build your knowledge base by importing content from your Shopify storefront and applying industry-specific templates. It also analyzes your knowledge base content to suggest optimal configuration values.

## Storefront content ingestion

When you connect your Shopify store, Agent Red can import the following content as knowledge base articles:

| Content type | Source | Article category |
|---|---|---|
| Product descriptions | Shopify product catalog | Products |
| Collection descriptions | Shopify collections | Products |
| Store policies | Shopify legal pages (refund, shipping, privacy, terms) | Policies |
| Page content | Shopify custom pages (About, FAQ, Contact) | General |

**How it works:**

1. Navigate to **Knowledge Base** in the admin console.
2. Click **Import from storefront** in the toolbar.
3. Agent Red fetches content from your connected Shopify store.
4. Imported articles appear as **drafts** — review and publish them before they are used by the AI.

:::tip
Storefront-ingested articles are tagged with a `storefront` source label. You can filter the knowledge base table by source to see which articles were automatically imported.
:::

**What gets imported:**
- Product titles, descriptions, prices, and variant information
- Collection titles and descriptions
- Policy page content (refund policy, shipping policy, privacy policy, terms of service)
- Custom page content (About Us, FAQ, Contact pages)

**What does not get imported:**
- Images and media (the AI uses text content only)
- Checkout and cart pages
- Password-protected content
- Draft or unpublished products

---

## Industry templates

Agent Red includes pre-built knowledge base templates for 11 industry categories. Each template provides FAQ articles, policy documents, and product information articles tailored to that industry.

| Template | Articles | Topics covered |
|---|---|---|
| Electronics & Gadgets | 8 | Warranty, compatibility, tech support, returns |
| Apparel & Fashion | 8 | Sizing, materials, care instructions, exchanges |
| Beauty & Cosmetics | 8 | Ingredients, skin types, application tips, allergies |
| Food & Beverage | 8 | Freshness, dietary info, storage, allergens |
| Health & Wellness | 8 | Usage guidelines, contraindications, certifications |
| Home & Garden | 8 | Assembly, dimensions, care, seasonal tips |
| Jewelry & Accessories | 8 | Materials, sizing, care, customization |
| Pet Supplies | 8 | Safety, sizing by breed, ingredients, storage |
| Sports & Outdoors | 8 | Equipment sizing, safety gear, maintenance |
| Toys & Games | 8 | Age recommendations, safety, batteries, assembly |
| General Goods | 8 | Universal shipping, returns, payment, support FAQs |

**How to apply a template:**

1. Navigate to **Knowledge Base** in the admin console.
2. Click **Apply template** in the toolbar.
3. Select the industry category that best matches your store.
4. Review the generated articles — they are created as drafts.
5. Edit the articles to match your specific policies and products.
6. Publish the articles when ready.

:::caution
Templates provide a starting point. Always review and customize the generated content to match your actual business policies, product details, and brand voice before publishing.
:::

---

## URL import

You can import content from any public web page directly into your knowledge base. This is useful for importing FAQ pages, help centers, or policy pages from your existing website — even if it is not on Shopify.

### How to import from a URL

1. Navigate to **Knowledge Base** in the admin console.
2. Click **Import** in the toolbar.
3. Select the **Import URL** tab.
4. Enter the full URL of the page you want to import (e.g., `https://example.com/faq`).
5. Click **Import**.
6. Agent Red fetches the page, extracts the text content, and creates knowledge base articles from it.
7. Imported articles appear as **drafts** — review, edit, and publish them.

### Supported page types

| Page type | How it is processed |
|---|---|
| FAQ pages | Questions and answers are detected and split into individual articles |
| Policy pages | Full text extracted and chunked into articles of approximately 300 words each |
| Help center articles | Headings used as article titles, body text as content |
| Product pages | Product description, specifications, and pricing extracted |
| Blog posts | Article text extracted, metadata (author, date) stripped |

### Best practices for URL import

- **Import one URL at a time.** Each URL creates a set of draft articles. Review them before importing the next URL to avoid duplication.
- **Use direct page URLs**, not site-level URLs. Import `https://example.com/shipping-policy`, not `https://example.com/` — the importer processes a single page, not an entire site.
- **Review auto-generated titles.** The importer creates titles from page headings, which may need editing for clarity.
- **Check for duplicates.** If you have already created articles covering the same topic, the import may create duplicates. Run a conflict scan after importing.
- **Publish after review.** Imported articles default to draft status. Only published articles are searchable by the AI.

---

## Configuration suggestions

After your knowledge base has content (from storefront ingestion, templates, or manual entry), Agent Red analyzes it to suggest optimal configuration values.

**Suggested fields:**

| Field | What the suggestion is based on |
|---|---|
| Brand name | Business name extracted from storefront or articles |
| Brand voice | Tone analysis of your existing content |
| Greeting message | Personalized greeting using your brand name and product focus |
| Escalation keywords | Common support triggers found in your FAQ content |
| Agent display name | Derived from your brand name |

**How suggestions appear:**

Configuration inputs that have an available suggestion display a **suggestion badge**. The badge shows the suggested value and its confidence score (0.0–1.0).

- Click the badge to preview the suggestion.
- Click **Apply** to fill the input with the suggested value.
- The suggestion does not auto-apply — you always choose whether to accept it.

**Confidence scores:**

| Range | Meaning |
|---|---|
| 0.8–1.0 | High confidence — the suggestion closely matches your content |
| 0.5–0.7 | Medium confidence — reasonable suggestion, review recommended |
| 0.3–0.4 | Low confidence — best guess based on limited content |
| Below 0.3 | Not shown — insufficient confidence to suggest |

---

## Onboarding wizard

New merchants who have not yet activated their configuration see a three-step setup wizard:

1. **Connect your store** — Link your Shopify storefront to import content automatically.
2. **Review your knowledge base** — Browse imported articles, apply an industry template, and publish the articles your AI should use.
3. **Configure your agent** — Review AI-generated suggestions for brand name, voice, greeting, and other settings. Accept or customize each value.

The wizard tracks progress and allows skipping ahead. Once all steps are complete, activate your configuration to go live.

:::info
The onboarding wizard is only shown to merchants who have not yet activated. After first activation, configuration is managed through the standard admin pages.
:::

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
