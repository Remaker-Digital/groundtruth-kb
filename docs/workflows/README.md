# Agent Red Workflow Documentation

> **Purpose:** Step-by-step workflow guides for UX evaluation and stakeholder review
> **Created:** 2026-02-04
> **Environment:** Shopify dev store (blanco-9939.myshopify.com)

---

## Workflow Guides

| # | Workflow | Pages | Description |
|---|----------|-------|-------------|
| 1 | [Storefront Overview](01-Storefront-Overview.md) | 12 steps | Customer-facing storefront experience: homepage, marketing pages, product catalog, chat widget |
| 2 | [Embedded Admin Dashboard](02-Embedded-Admin-Dashboard.md) | 3 steps | Merchant admin experience inside Shopify: finding the app, installation details, dashboard |
| 3 | [Widget Activation](03-Widget-Activation.md) | 5 steps | Enabling/disabling the chat widget via Shopify theme editor app embeds |

---

## Screenshot Inventory

Screenshots captured 2026-02-04 using Chrome browser automation.

### Storefront Screenshots

| ID | Description | Page |
|----|-------------|------|
| `ss_125459xfj` | Homepage hero with navigation bar | Workflow 1, Step 1 |
| `ss_3562vq0u2` | Homepage hero (second capture) | Workflow 1, Step 1 |
| `ss_7445p9xon` | Features page | Workflow 1, Step 5 |
| `ss_5459xxv0s` | Pricing page | Workflow 1, Step 6 |
| `ss_2525onak9` | Integrations page | Workflow 1, Step 7 |
| `ss_9112tnb9j` | About page | Workflow 1, Step 8 |
| `ss_5998zhw4o` | Contact page | Workflow 1, Step 9 |
| `ss_1436w8x39` | Catalog (product listing) | Workflow 1, Step 10 |
| `ss_7932cme9m` | Widget open on homepage | Workflow 1, Step 12 |

### Admin Screenshots

| ID | Description | Page |
|----|-------------|------|
| `ss_1276a3pas` | Shopify Settings > Apps (app installed) | Workflow 2, Step 1 |
| `ss_05775d6vc` | App installation details | Workflow 2, Step 2 |
| `ss_92402dg2w` | Embedded admin dashboard | Workflow 2, Step 3 |

### Theme Editor Screenshots

| ID | Description | Page |
|----|-------------|------|
| `ss_7646s69ib` | Theme editor with homepage sections | Workflow 3, Step 1 |
| `ss_4485b7dr9` | App embeds with Agent Red Chat toggle | Workflow 3, Step 2 |

---

## For the UX Designer

### Key Areas for Evaluation

1. **Storefront Content Flow:** Does the homepage effectively communicate the value proposition? Is the progression from hero → plans → differentiator → features logical?

2. **Widget Experience:** Is the launcher visible but non-intrusive? Does the chat panel layout feel natural? Are input affordances clear?

3. **Admin Dashboard:** Is the Analytics Overview useful at a glance? Do the stat cards communicate clearly when there's no data? Is the navigation between Shopify admin and Agent Red intuitive?

4. **Widget Activation:** Is the single-toggle activation discoverable? Would a merchant know where to find it?

### Design Reference

The production admin dashboard design is documented in the renderable prototype:
```
cd prototype && npm run dev  # Port 3000
```

The prototype shows the full admin experience with mock data:
- Dark mode (default) with four-tier depth hierarchy
- Mantine v7 standalone shell (9 pages)
- Polaris embedded shell (7 pages)
- Comprehensive mock data for all components

### Persistent Customer Memory — Differentiator Focus

The primary differentiator to evaluate in customer conversations:
- Does the AI reference previous interaction history naturally?
- Are customer preferences remembered across sessions?
- Does the response quality improve with more interaction data?

This is the feature that no competitor has confirmed implementing. The UX evaluation should specifically test whether this differentiator is perceptible and valuable to end users.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
