# Agent Red Customer Experience — Brand Guidelines

> **Version:** 1.0
> **Status:** Approved
> **Date:** 2026-01-29
> **Owner:** Remaker Digital (DBA of VanDusen & Palmeter, LLC)

---

## 1. Brand Overview

### Brand Name

| Form | Usage |
|------|-------|
| **Full** | Agent Red Customer Experience |
| **Short** | Agent Red |
| **Product Line** | Agent Red (parent brand) > Customer Experience (product) |

### Brand Personality

Agent Red is **bold, authoritative, and professional** — a commercial SaaS brand that conveys enterprise trust while remaining approachable. The visual identity follows a **Bold/Corporate** direction.

| Attribute | Description |
|-----------|-------------|
| **Bold** | Strong red brand color, confident typography, clear visual hierarchy |
| **Authoritative** | Dark neutrals, precise type, clean layouts that convey expertise |
| **Professional** | Consistent, polished, enterprise-ready |
| **Approachable** | Warm red (not aggressive), readable body text, clear CTAs |

### Brand Voice

| Do | Don't |
|----|-------|
| Use clear, direct language | Use jargon without explanation |
| Focus on customer benefits | Lead with technical specifications |
| Be confident but not arrogant | Make unsubstantiated claims |
| Use data and metrics as proof points | Use vague superlatives ("best", "ultimate") |
| Address business decision-makers | Write exclusively for developers |
| Emphasize that Persistent Customer Memory makes every conversation smarter than the last | Describe memory features as "tracking" or "surveillance" |

### Messaging Pillars

| Pillar | Key Message | Supporting Points |
|--------|-------------|-------------------|
| **Best Customer Experience** | Agent Red delivers the most personalized AI support in e-commerce | Six specialized agents, 98% accuracy, <2s response time, Persistent Customer Memory |
| **Best Price** | Enterprise-quality AI support at a fraction of competitor pricing | 2–13x cheaper per interaction than Gorgias/Intercom/Zendesk, transparent usage-based pricing |
| **Persistent Customer Memory** | Every conversation builds on the last | Four-layer personalization (context profiles, conversation memory, cross-session learning, dedicated model training), no repeat explanations, preference adaptation, tier-appropriate depth |

**Key phrases to use:**
- "Conversations that remember"
- "Every interaction builds on the last"
- "Your customers never repeat themselves"
- "Persistent Customer Memory"
- "Four layers of personalization"

**Phrases to avoid:**
- "Tracking customers" / "customer tracking"
- "Surveillance" / "monitoring behavior"
- "Data harvesting" / "collecting data on customers"
- "AI watching your customers"

---

## 2. Logo

### Concept: The Beacon

A solid Agent Red rounded rectangle with a white "AR" monogram in Inter Extra Bold. Bold, instantly recognizable, and scales from 16px to any size.

### Variants

| Variant | Use Case |
|---------|----------|
| **Primary** | Icon + "Agent Red" wordmark, horizontal layout. Website headers, documents, presentations. |
| **Icon Only** | AR rounded rectangle alone. Favicons, app icons, social avatars, small spaces. |
| **Wordmark Only** | "Agent Red" text without icon. Inline references, space-constrained contexts. |

### Color Applications

| Background | Icon Background | Monogram | "Agent" Text | "Red" Text |
|------------|----------------|----------|--------------|------------|
| White / Light | `#C41E2A` | `#FFFFFF` | `#1A1A2E` | `#C41E2A` |
| Charcoal / Dark | `#C41E2A` | `#FFFFFF` | `#FFFFFF` | `#C41E2A` |
| Agent Red | `#FFFFFF` | `#C41E2A` | `#FFFFFF` | `#FFFFFF` |

### Clear Space & Minimum Size

- **Clear space:** Minimum padding equal to the height of the "A" character in the monogram, on all four sides
- **Minimum icon size:** 16px (favicon)
- **Minimum primary logo width:** 120px

### Logo Misuse

- Do not stretch, skew, or rotate the logo
- Do not change the logo colors outside of the approved variants
- Do not add effects (shadows, gradients, outlines) to the logo
- Do not place the logo on busy photographic backgrounds without a container
- Do not rearrange the icon and wordmark relationship

### Detailed Specification

Logo assets are located in `branding/logo/SVG/` (source) and `branding/logo/PNG/` (rasterized):
- **Icon:** `icon-master` — AR monogram on split white/red rounded rectangle
- **Primary (dark bg):** `primary-logo-dark` — "AGENT RED" + "CUSTOMER EXPERIENCE" subtitle, white text for dark backgrounds
- **Primary (light bg):** `primary-logo-light` — "AGENT RED" + "CUSTOMER EXPERIENCE" subtitle, dark text for light backgrounds

---

## 3. Color Palette

### Primary Colors

| Role | Name | Hex | RGB | Usage |
|------|------|-----|-----|-------|
| **Primary** | Agent Red | `#C41E2A` | 196, 30, 42 | Logo, CTAs, key accents |
| **Primary Dark** | Deep Red | `#9B1420` | 155, 20, 32 | Hover states, active elements |
| **Primary Light** | Soft Red | `#F2D4D6` | 242, 212, 214 | Subtle backgrounds, highlights |

### Neutral Colors

| Role | Name | Hex | RGB | Usage |
|------|------|-----|-----|-------|
| **Dark** | Charcoal | `#1A1A2E` | 26, 26, 46 | Primary text, dark backgrounds |
| **Medium Dark** | Slate | `#3D3D56` | 61, 61, 86 | Secondary text, subheadings |
| **Medium** | Steel | `#6B6B80` | 107, 107, 128 | Tertiary text, placeholders |
| **Light** | Silver | `#E8E8ED` | 232, 232, 237 | Borders, dividers |
| **Background** | Snow | `#F8F8FA` | 248, 248, 250 | Page backgrounds |
| **White** | White | `#FFFFFF` | 255, 255, 255 | Cards, modals, inputs |

### Accent Colors

| Role | Name | Hex | RGB | Usage |
|------|------|-----|-----|-------|
| **Success** | Forest | `#0D7C3E` | 13, 124, 62 | Success states, confirmations |
| **Warning** | Amber | `#E5A100` | 229, 161, 0 | Warnings, pending states |
| **Error** | Crimson | `#D32F2F` | 211, 47, 47 | Errors, destructive actions |
| **Info** | Navy | `#1E3A5F` | 30, 58, 95 | Links, informational elements |

### Accessibility

All primary text combinations meet WCAG AA or AAA standards:

| Combination | Ratio | Rating |
|-------------|-------|--------|
| Charcoal on White | 16.2:1 | AAA |
| Charcoal on Snow | 15.1:1 | AAA |
| White on Charcoal | 16.2:1 | AAA |
| Agent Red on White | 4.65:1 | AA |
| White on Agent Red | 4.65:1 | AA |
| White on Navy | 9.4:1 | AAA |
| White on Deep Red | 6.72:1 | AAA |

### CSS Variables

```css
:root {
    /* Primary */
    --color-primary: #C41E2A;
    --color-primary-dark: #9B1420;
    --color-primary-light: #F2D4D6;

    /* Neutrals */
    --color-charcoal: #1A1A2E;
    --color-slate: #3D3D56;
    --color-steel: #6B6B80;
    --color-silver: #E8E8ED;
    --color-snow: #F8F8FA;
    --color-white: #FFFFFF;

    /* Accents */
    --color-success: #0D7C3E;
    --color-warning: #E5A100;
    --color-error: #D32F2F;
    --color-info: #1E3A5F;
}
```

### Detailed Specification

See [`branding/colors/COLOR-PALETTE.md`](../colors/COLOR-PALETTE.md) for full reference.
See [`branding/colors/color-palette.html`](../colors/color-palette.html) for visual preview.

---

## 4. Typography

### Font Stack

| Role | Font | Weights | Source |
|------|------|---------|--------|
| **Headings** | Inter | 600, 700 | Google Fonts (SIL OFL) |
| **Body** | Inter | 400, 500 | Google Fonts (SIL OFL) |
| **Code** | JetBrains Mono | 400, 500 | Google Fonts (SIL OFL) |

### Type Scale

| Element | Size | Weight | Line Height | Usage |
|---------|------|--------|-------------|-------|
| H1 | 40px / 2.5rem | 700 | 1.2 | Page titles, hero headlines |
| H2 | 30px / 1.875rem | 700 | 1.25 | Section headers |
| H3 | 24px / 1.5rem | 600 | 1.3 | Subsection headers |
| H4 | 20px / 1.25rem | 600 | 1.35 | Card titles |
| Body Large | 18px / 1.125rem | 400 | 1.6 | Lead paragraphs |
| Body | 16px / 1rem | 400 | 1.6 | Default body text |
| Body Small | 14px / 0.875rem | 400 | 1.5 | Captions, metadata |
| Code | 14px / 0.875rem | 400 | 1.5 | Code blocks, API references |
| Label | 12px / 0.75rem | 500 | 1.4 | Badges, tags |

### CSS Import

```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
```

### CSS Variables

```css
:root {
    --font-heading: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    --font-body: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    --font-code: 'JetBrains Mono', 'Cascadia Code', 'Fira Code', 'Consolas', monospace;
}
```

### Detailed Specification

See [`branding/colors/TYPOGRAPHY.md`](../colors/TYPOGRAPHY.md) for full reference.

---

## 5. Iconography & UI Elements

### Buttons

| Type | Background | Text | Border | Usage |
|------|-----------|------|--------|-------|
| **Primary** | `#C41E2A` | `#FFFFFF` | None | Main CTAs ("Start Free Trial", "Get Started") |
| **Primary Hover** | `#9B1420` | `#FFFFFF` | None | Hover state for primary buttons |
| **Secondary** | `#1E3A5F` | `#FFFFFF` | None | Secondary actions ("Learn More") |
| **Outline** | Transparent | `#C41E2A` | 2px `#C41E2A` | Tertiary actions ("View Pricing") |
| **Outline Hover** | `#F2D4D6` | `#C41E2A` | 2px `#C41E2A` | Hover state for outline buttons |

Button properties: `border-radius: 8px`, `padding: 12px 28px`, `font-weight: 600`, `font-size: 15px`

### Cards

| Property | Value |
|----------|-------|
| Background | `#FFFFFF` |
| Border Radius | 12px |
| Shadow | `0 2px 8px rgba(0,0,0,0.08)` |
| Border | 1px `#E8E8ED` (optional) |

### Status Messages

| Type | Background | Text | Left Border |
|------|-----------|------|-------------|
| Success | `#e6f4ec` | `#0D7C3E` | 4px `#0D7C3E` |
| Warning | `#fef6e0` | `#9e7000` | 4px `#E5A100` |
| Error | `#fde8e8` | `#D32F2F` | 4px `#D32F2F` |
| Info | `#e4ecf4` | `#1E3A5F` | 4px `#1E3A5F` |

---

## 6. Favicon & App Icons

### Required Formats

| Asset | Size | Format | Usage |
|-------|------|--------|-------|
| Favicon | 16x16 | ICO/PNG | Browser tab |
| Favicon | 32x32 | PNG | Browser tab (retina) |
| Apple Touch Icon | 180x180 | PNG | iOS home screen |
| Android Chrome | 192x192 | PNG | Android home screen |
| Android Chrome | 512x512 | PNG | Android splash screen |
| Open Graph | 1200x630 | PNG | Social sharing (with wordmark) |
| Master Icon | 1024x1024 | PNG/SVG | Source file for all sizes |

All icons use the AR monogram on Agent Red background with rounded corners.

---

## 7. Photography & Imagery

### Style Guidelines

- Use clean, well-lit imagery
- Prefer abstract or technology-themed visuals over stock photography of people
- When using illustrations, maintain the brand color palette
- Avoid cluttered or busy backgrounds
- Data visualizations should use the brand accent colors

---

## 8. Copyright & Legal

### Copyright Notice

All materials must include:

```
© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
```

### Trademark

"Agent Red" and the AR monogram logo are trademarks of VanDusen & Palmeter, LLC.

---

## File Reference

| Asset | Location |
|-------|----------|
| Color Palette (reference) | `branding/colors/COLOR-PALETTE.md` |
| Color Palette (visual) | `branding/colors/color-palette.html` |
| Typography | `branding/colors/TYPOGRAPHY.md` |
| Logo SVG (source) | `branding/logo/SVG/` (icon-master, primary-logo-dark, primary-logo-light) |
| Logo PNG (rasterized) | `branding/logo/PNG/` (icon-master, primary-logo-dark, primary-logo-light) |
| Brand Guidelines | `branding/guidelines/BRAND-GUIDELINES.md` (this file) |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
