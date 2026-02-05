# Workflow 1: Storefront Overview

> **Audience:** UX Designer, Product Owner
> **Environment:** Shopify dev store (blanco-9939.myshopify.com)
> **Last Updated:** 2026-02-04

---

## Purpose

This workflow documents the customer-facing storefront experience. A visitor arrives at the Agent Red storefront, browses marketing pages, views the product catalog, and interacts with the AI chat widget.

---

## Step 1: Homepage — Hero Section

**URL:** `https://blanco-9939.myshopify.com`

**What the visitor sees:**
- **Navigation bar** with 7 items: Home, Features, Pricing, Integrations, About, Contact, Catalog
- **Hero banner** with background image and headline: "Cut Support Costs 40-60%. Without Cutting Quality."
- **Subheadline:** "Agent Red deploys six AI agents that handle your customer conversations — instantly, accurately, and in your brand voice. Your team focuses on what matters. The AI handles the rest."
- **Two CTAs:** "Start Free Trial" (solid black button → /pages/pricing) and "See Features" (outline button → /pages/features)
- **Chat widget launcher** — red circle in bottom-right corner (always visible across all pages)

**Screenshot reference:** `ss_125459xfj` / `ss_3562vq0u2` — Homepage hero with navigation and widget launcher

**UX Notes:**
- Navigation is clearly organized with all key pages accessible from any page
- Hero messaging leads with the cost-saving value proposition
- Dual CTA approach: trial for ready buyers, features for researchers
- Widget launcher is persistent and non-intrusive

---

## Step 2: Homepage — Product Plans Section

**What the visitor sees (after scrolling):**
- **Section heading:** "AI-Powered Customer Service Plans"
- **Product cards** showing the subscription plans available for purchase
- Each card shows plan name, pricing, and key features
- Links to the full pricing page for detailed comparison

**UX Notes:**
- Products are rendered via Shopify's native Featured Collection section
- Plans are presented as Shopify products (enabling standard e-commerce checkout)

---

## Step 3: Homepage — Persistent Customer Memory Highlight

**What the visitor sees (after scrolling):**
- **Section heading:** "Conversations That Remember"
- **Description:** Explains that Agent Red remembers customer preferences, past issues, and communication style across sessions
- **Key differentiator messaging:** "No competitor offers this level of per-customer AI memory"
- **CTA:** "Learn More" → /pages/features

**UX Notes:**
- This section highlights Agent Red's primary launch differentiator
- Image-with-text layout creates visual interest
- Accent color scheme draws attention to this section

---

## Step 4: Homepage — Six Agents Overview

**What the visitor sees (at bottom of homepage):**
- **Section heading:** "Six AI Agents. One Seamless Experience."
- **Pipeline flow description:** Intent Classification (98% accuracy) → Knowledge Retrieval (real-time Shopify sync) → Response Generation (GPT-4o, your brand voice) → Critic Validation (100% content safety) → Smart Escalation (full context handoff) → Analytics (actionable insights)
- **Performance stats:** Response time under 2 seconds. 3,071 requests per second throughput. 99.95% uptime SLA. Starting at $149/month.
- **CTA:** "See All Features" → /pages/features

**UX Notes:**
- Combines the technical explanation with concrete performance metrics
- Pricing anchor ($149/month) is introduced early to set expectations

---

## Step 5: Features Page

**URL:** `https://blanco-9939.myshopify.com/pages/features`

**What the visitor sees:**
- **Page title:** "Features"
- **Heading:** "Six AI Agents. One Exceptional Support Experience."
- **Detailed breakdown** of each AI agent's capabilities
- Navigation bar with "Features" underlined as active page

**Screenshot reference:** `ss_7445p9xon` — Features page

**UX Notes:**
- Comprehensive feature list organized by agent
- Each agent's role and key metrics are clearly explained

---

## Step 6: Pricing Page

**URL:** `https://blanco-9939.myshopify.com/pages/pricing`

**What the visitor sees:**
- **Page title:** "Pricing"
- **Heading:** "Transparent Pricing. Every Cost Visible."
- **Two-component model explained:**
  - Component 1: Platform Fee — monthly plan covers infrastructure, integrations, support, and features
  - Component 2: AI Conversations — monthly allowance included, overage or pre-purchase packs available
- Detailed tier comparison below

**Screenshot reference:** `ss_5459xxv0s` — Pricing page

**UX Notes:**
- Transparency-first messaging differentiates from competitors with opaque pricing
- Two-component model is explained before showing specific prices

---

## Step 7: Integrations Page

**URL:** `https://blanco-9939.myshopify.com/pages/integrations`

**What the visitor sees:**
- **Page title:** "Integrations"
- **Heading:** "Connects to Your Entire Stack"
- **Shopify integration** (all tiers) featured prominently with bullet points:
  - Real-time order status, tracking, and history
  - Product catalog search with pricing and availability
  - Customer profiles with purchase history
- Additional integrations listed below (Zendesk, Mailchimp, Google Analytics)

**Screenshot reference:** `ss_2525onak9` — Integrations page

**UX Notes:**
- Shopify-first positioning aligns with the primary distribution channel
- Tier availability clearly shown for each integration

---

## Step 8: About Page

**URL:** `https://blanco-9939.myshopify.com/pages/about`

**What the visitor sees:**
- **Page title:** "About Agent Red"
- **Heading:** "Great Customer Service Shouldn't Require a Massive Team"
- **Mission statement** in a blockquote: "To make world-class customer service accessible to every e-commerce business — regardless of team size or budget."
- Company philosophy and open-source foundation story

**Screenshot reference:** `ss_9112tnb9j` — About page

**UX Notes:**
- Honest, straightforward messaging about company mission
- Open-source foundation builds trust

---

## Step 9: Contact Page

**URL:** `https://blanco-9939.myshopify.com/pages/contact`

**What the visitor sees:**
- **Page title:** "Contact Us"
- **Heading:** "Let's Talk"
- **Team directory:**
  - Sales (sales@agentred.io) — pricing questions, demos, custom plans
  - Support — technical issues, setup help, account questions
- Response commitment: within 24 hours

**Screenshot reference:** `ss_5998zhw4o` — Contact page

**UX Notes:**
- Clear team routing reduces friction
- 24-hour response commitment sets expectations

---

## Step 10: Product Catalog

**URL:** `https://blanco-9939.myshopify.com/collections/all`

**What the visitor sees:**
- **Page title:** "Products"
- **Product grid** showing 14 products with images
- Filter and sort controls (Sort by: Alphabetically, A-Z)
- Standard Shopify collection layout

**Screenshot reference:** `ss_1436w8x39` — Catalog page

**UX Notes:**
- Standard Shopify product catalog experience
- Products include both Agent Red subscription plans and demo store products

---

## Step 11: Chat Widget — Launcher

**What the visitor sees:**
- Red circular button in the bottom-right corner of every page
- Chat icon (speech bubble) inside the circle
- Clicking opens the conversation panel

**UX Notes:**
- Persistent across all pages (app embed block)
- Non-intrusive size and position
- Brand color (#C41E2A) reinforces Agent Red identity

---

## Step 12: Chat Widget — Conversation Panel

**What the visitor sees after clicking the launcher:**
- **Header:** "Chat with us" with a green status dot and "Agent Red" label
- **Close button** (X) in top-right
- **Message area:** Empty conversation space (ready for first message)
- **Input bar:** "Type a message..." placeholder text
- **File attach button** (paperclip icon) on the left of input
- **Send button** (arrow icon) on the right of input
- **Footer:** "Powered by Agent Red" branding

**Screenshot reference:** `ss_7932cme9m` — Widget open on homepage

**UX Notes:**
- Clean, minimal design with clear affordances
- Agent status indicator shows availability
- File attachment support visible from first interaction
- "Powered by Agent Red" can be removed with White-Label Package (Enterprise)
- Widget connects to production API Gateway for AI conversations

---

## Navigation Summary

| Page | URL Path | Purpose |
|------|----------|---------|
| Home | `/` | Hero, plans, differentiators |
| Features | `/pages/features` | Detailed feature breakdown |
| Pricing | `/pages/pricing` | Transparent pricing model |
| Integrations | `/pages/integrations` | Integration ecosystem |
| About | `/pages/about` | Company mission and story |
| Contact | `/pages/contact` | Sales and support channels |
| Catalog | `/collections/all` | Product listing |

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
