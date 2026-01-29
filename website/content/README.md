# Website Content - AGNTCY Customer Engagement Platform

> **Purpose:** Marketing website content for the AGNTCY Customer Engagement Platform
> **Format:** Structured markdown optimized for implementation in Webflow, Framer, or Next.js
> **Status:** Phase 1 Complete - Core Pages Ready

---

## Content Inventory

| Page | File | Status | Lines | Priority |
|------|------|--------|-------|----------|
| Homepage | `homepage.md` | ✅ Complete | ~450 | P0 |
| Features | `features.md` | ✅ Complete | ~650 | P0 |
| Pricing | `pricing.md` | ✅ Complete | ~550 | P0 |
| Integrations | `integrations.md` | ✅ Complete | ~550 | P1 |
| About | `about.md` | ✅ Complete | ~350 | P2 |

**Total Content:** ~2,550 lines across 5 core pages

---

## Content Structure

Each page file includes:

1. **Meta Information** - Title, description, keywords, OG image, canonical URL
2. **Section-by-Section Content** - Headlines, descriptions, CTAs
3. **Structured Data** - Tables, feature lists, comparison matrices
4. **CTA Specifications** - Primary and secondary calls-to-action
5. **Technical Notes** - SEO, analytics events, schema markup
6. **A/B Test Variants** - Alternative headlines for testing

---

## Implementation Guide

### For Webflow/Framer

1. Create page structure matching section headers
2. Copy content directly into CMS or page components
3. Replace placeholder images with actual assets
4. Implement navigation using section anchors
5. Add analytics tracking per technical notes

### For Next.js/React

1. Parse markdown files with gray-matter + remark
2. Map sections to React components
3. Use MDX for interactive elements (calculators, forms)
4. Implement schema.org JSON-LD from provided specs
5. Add event tracking per analytics specifications

---

## Brand Guidelines

### Voice & Tone

| Attribute | Guideline |
|-----------|-----------|
| **Tone** | Professional but approachable |
| **Language** | Clear, jargon-free, benefit-focused |
| **Perspective** | Second person ("you", "your") |
| **Urgency** | Confident, not pushy |
| **Technical Level** | Accessible to non-technical readers |

### Messaging Hierarchy

1. **Primary:** Reduce costs, improve customer satisfaction
2. **Secondary:** 24/7 availability, instant responses
3. **Tertiary:** Easy setup, no coding required
4. **Proof Points:** 70% automation, 98% accuracy, <2s response

### CTA Patterns

| CTA Type | Text | Destination |
|----------|------|-------------|
| Primary | "Start Free Trial" | /signup |
| Secondary (Sales) | "Talk to Sales" | /contact |
| Secondary (Demo) | "Watch Demo" | /demo |
| Tertiary | "Learn More" | /features |

---

## Image Requirements

### Homepage
- [ ] Hero image/animation (1920x1080 or responsive)
- [ ] Agent workflow diagram (animated preferred)
- [ ] Customer logo cloud (6-8 logos, grayscale)
- [ ] Testimonial headshots (3, 200x200)
- [ ] Integration logo row (6 logos)

### Features
- [ ] AI agent icons (6, consistent style)
- [ ] Feature icons (9, consistent style)
- [ ] Dashboard screenshot (1440x900)
- [ ] Integration screenshots (4, 800x600)

### Pricing
- [ ] Plan icons (3, consistent style)
- [ ] Trust badges (security, compliance)
- [ ] ROI calculator mockup

### Integrations
- [ ] Integration partner logos (6+, official assets)
- [ ] Setup flow screenshots (4 per integration)
- [ ] API code snippet styling

### About
- [ ] Team headshots (6+, consistent style, 400x400)
- [ ] Office/workspace photo (1920x1080)
- [ ] Investor logos (if applicable)
- [ ] Press outlet logos (if applicable)

---

## SEO Specifications

### Target Keywords

| Page | Primary Keyword | Secondary Keywords |
|------|----------------|-------------------|
| Homepage | AI customer service | chatbot, automation, Shopify support |
| Features | customer service AI features | intent classification, smart escalation |
| Pricing | AI customer service pricing | chatbot cost, support automation price |
| Integrations | Shopify customer service integration | Zendesk integration, API |
| About | customer service AI company | team, mission |

### Schema Markup Required

- **Homepage:** Organization, Product, FAQPage
- **Features:** Product, ItemList (features)
- **Pricing:** Product, Offer (per tier)
- **Integrations:** SoftwareApplication, ItemList
- **About:** Organization, Person (team)

---

## Analytics Events

### Homepage
| Event | Trigger | Parameters |
|-------|---------|------------|
| `page_view` | Page load | page_name |
| `cta_click` | CTA button click | cta_type, cta_location |
| `video_play` | Demo video started | video_id |
| `scroll_depth` | Section viewed | section_name |

### Pricing
| Event | Trigger | Parameters |
|-------|---------|------------|
| `pricing_view` | Pricing section visible | - |
| `plan_select` | Plan card clicked | plan_name |
| `toggle_billing` | Monthly/Annual toggle | billing_period |
| `calculator_use` | ROI calculator interaction | input_values |

### All Pages
| Event | Trigger | Parameters |
|-------|---------|------------|
| `cta_click` | Any CTA clicked | cta_text, cta_destination |
| `outbound_link` | External link clicked | destination_url |
| `form_submit` | Form submitted | form_name |

---

## Planned Additional Pages

### Phase 2 (Weeks 5-8)
- [ ] `/customers` - Case studies and testimonials
- [ ] `/demo` - Interactive demo or video
- [ ] `/contact` - Contact form and sales inquiry
- [ ] `/signup` - Trial registration
- [ ] `/login` - Customer login

### Phase 3 (Weeks 9-12)
- [ ] `/blog` - Company blog with categories
- [ ] `/changelog` - Product updates
- [ ] `/careers` - Job listings
- [ ] `/partners` - Partner program
- [ ] `/press` - Press releases and media kit

### Future
- [ ] `/customers/{slug}` - Individual case studies
- [ ] `/blog/{slug}` - Blog posts
- [ ] `/docs` - Documentation (Docusaurus)
- [ ] `/api` - API reference

---

## Content Maintenance

### Review Schedule
| Page | Review Frequency | Owner |
|------|-----------------|-------|
| Homepage | Monthly | Marketing |
| Features | Quarterly | Product |
| Pricing | As needed | Finance |
| Integrations | Monthly | Engineering |
| About | Quarterly | Marketing |

### Update Triggers
- New feature launch → Features, Homepage
- Pricing change → Pricing, Homepage
- New integration → Integrations
- Team change → About
- Customer milestone → Homepage (stats)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-29 | Initial content for 5 core pages |

---

## Related Documents

- `docs/COMMERCIAL-SAAS-PROPOSAL.md` - Strategic plan
- `docs/COMMERCIAL-MATERIALS-PLAN.md` - Project tracking
- `docs/PRODUCT-FEATURES-RAG.md` - Complete feature reference

---

*Owner: Marketing Team*
*Last Updated: 2026-01-29*
