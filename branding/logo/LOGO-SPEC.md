# Agent Red Customer Engagement — Logo Specification

> **Status:** Approved
> **Concept:** The Beacon (AR Monogram)
> **Visual Preview:** [`logo-concepts.html`](logo-concepts.html)
> **Export Tool:** [`export-all-sizes.html`](export-all-sizes.html)

---

## Logo Concept

A solid Agent Red (`#C41E2A`) rounded rectangle with a white "AR" monogram inside, set in Inter Extra Bold. Clean, bold, and modern — scales from 16px favicon to any size without losing legibility.

## Logo Variants

| Variant | Description | Usage |
|---------|-------------|-------|
| **Primary** | AR icon + "Agent Red" wordmark (horizontal) | Website header, documents, presentations |
| **Icon Only** | AR rounded rectangle | Favicon, app icon, social avatars, small spaces |
| **Wordmark Only** | "Agent Red" text (no icon) | Contexts where icon is redundant or space is limited |

## Icon Specification

| Property | Value |
|----------|-------|
| **Shape** | Rounded rectangle |
| **Corner Radius** | ~21% of width (e.g., 10px on 48px icon) |
| **Background** | Agent Red `#C41E2A` |
| **Monogram** | "AR" in white `#FFFFFF` |
| **Font** | Inter, weight 800 (Extra Bold) |
| **Letter Spacing** | -1px (tight) |
| **Monogram Position** | Centered vertically, slight left offset for optical balance |

## Wordmark Specification

| Property | Value |
|----------|-------|
| **Font** | Inter, weight 700 (Bold) |
| **Size** | Proportional to icon height |
| **"Agent"** | Charcoal `#1A1A2E` (light backgrounds) / White `#FFFFFF` (dark backgrounds) |
| **"Red"** | Agent Red `#C41E2A` (all backgrounds) |
| **Spacing** | Standard word spacing |

## Color Variants

| Background | Icon | "Agent" | "Red" |
|------------|------|---------|-------|
| Light / White | `#C41E2A` bg, `#FFFFFF` text | `#1A1A2E` | `#C41E2A` |
| Dark / Charcoal | `#C41E2A` bg, `#FFFFFF` text | `#FFFFFF` | `#C41E2A` |
| Agent Red bg | `#FFFFFF` bg, `#C41E2A` text | `#FFFFFF` | `#FFFFFF` |

---

## Complete Asset Manifest

### SVG Source Files

| File | Variant | Usage |
|------|---------|-------|
| `icon-master.svg` | Icon only (1200x1200 viewBox) | Master source for all icon exports |
| `primary-logo-light.svg` | Icon + wordmark, light bg | Website header, documents (light backgrounds) |
| `primary-logo-dark.svg` | Icon + wordmark, dark bg | Website header, documents (dark backgrounds) |
| `wordmark-light.svg` | Wordmark only, light bg | Space-constrained contexts (light backgrounds) |
| `wordmark-dark.svg` | Wordmark only, dark bg | Space-constrained contexts (dark backgrounds) |
| `og-image.svg` | Icon + wordmark on charcoal | Social media link previews (source) |

### Required Raster Exports (PNG)

| File | Dimensions | Format | Usage | Platform |
|------|-----------|--------|-------|----------|
| `favicon-16x16.png` | 16 x 16 | PNG | Browser tab favicon | Web |
| `favicon-32x32.png` | 32 x 32 | PNG | Browser tab favicon (HiDPI) | Web |
| `favicon.ico` | 16x16 + 32x32 | ICO | Legacy browser favicon | Web |
| `apple-touch-icon.png` | 180 x 180 | PNG | iOS home screen bookmark | iOS |
| `android-chrome-192.png` | 192 x 192 | PNG | Android Chrome home screen | Android |
| `android-chrome-512.png` | 512 x 512 | PNG | Android Chrome splash screen | Android |
| `app-icon-1024.png` | 1024 x 1024 | PNG | General app icon | General |
| `shopify-app-icon.png` | 1200 x 1200 | PNG | Shopify App Store listing icon | Shopify |
| `primary-logo-light.png` | 960 x 256 | PNG | Website header (light bg) | Web |
| `primary-logo-dark.png` | 960 x 256 | PNG | Website header (dark bg) | Web |
| `og-image.png` | 1200 x 630 | PNG | Social media link previews | Social |

### Platform-Specific Requirements

| Platform | Asset | Dimensions | Format | Special Notes |
|----------|-------|-----------|--------|---------------|
| **Shopify App Store** | App icon | 1200 x 1200 | PNG or JPEG | No transparency, no text overlays, no Shopify marks. Square corners (auto-rounded by Shopify). Logo fills 750-900px of canvas with 75px margin. |
| **Shopify App Store** | Screenshots | 1600 x 900 | PNG or JPEG | 3-6 required. At least one showing app UI. No browser chrome, pricing, or testimonials. |
| **Shopify App Store** | Key benefits images | 1600 x 1200 | PNG or JPEG | Up to 3. No text, no app dashboards. Abstract/conceptual only. |
| **Web (favicon)** | favicon.ico | 16x16 + 32x32 multi-res | ICO | Bundle both sizes in one .ico file |
| **Web (manifest)** | Icons | 192x192, 512x512 | PNG | Referenced in site.webmanifest |
| **iOS** | Apple touch icon | 180 x 180 | PNG | No transparency. Referenced via `<link rel="apple-touch-icon">` |
| **Open Graph** | Social image | 1200 x 630 | PNG | Include wordmark + tagline. Referenced via `<meta property="og:image">` |
| **Docusaurus** | Navbar logo | SVG or PNG | SVG preferred | Use `primary-logo-light.svg` or `primary-logo-dark.svg` |
| **GitHub** | Repo avatar | 500 x 500 min | PNG or JPEG | Use icon-only variant |

---

## Clear Space

Minimum clear space around the logo is equal to the height of the "A" in the monogram on all sides.

## Minimum Size

- **Icon only:** 16px (favicon) — monogram remains legible
- **Primary logo (icon + wordmark):** 120px wide minimum

---

## Logo Update Procedure

When the logo design changes, follow this end-to-end procedure to ensure all assets are updated comprehensively.

### Step 1: Update Source Files

Edit these SVG source files in `branding/logo/`:

| File | What to Update |
|------|----------------|
| `icon-master.svg` | Icon shape, colors, monogram text, font, positioning |
| `primary-logo-light.svg` | Icon + wordmark layout, colors for light backgrounds |
| `primary-logo-dark.svg` | Icon + wordmark layout, colors for dark backgrounds |
| `wordmark-light.svg` | Wordmark text, font, colors for light backgrounds |
| `wordmark-dark.svg` | Wordmark text, font, colors for dark backgrounds |
| `og-image.svg` | Social preview layout, tagline text |
| `logo-concepts.html` | Visual concept preview (update Concept 3 / The Beacon section) |

### Step 2: Update Export Tool and Re-Export PNGs

1. Open `export-all-sizes.html` in a text editor
2. Update the `BRAND` constants and `drawIcon()` / `drawPrimaryLogo()` / `drawOGImage()` functions to match the new design
3. Open `export-all-sizes.html` in Chrome
4. Click "Export All" to download all 11 PNG assets
5. Move exported PNGs into `branding/logo/exports/`

### Step 3: Update ICO Favicon

Generate `favicon.ico` from the 16x16 and 32x32 PNGs using one of:
- Online tool: realfavicongenerator.net
- CLI: `magick convert favicon-16x16.png favicon-32x32.png favicon.ico` (ImageMagick)

### Step 4: Update Platform Deployments

| Location | Files to Replace | How to Update |
|----------|-----------------|---------------|
| **Website / Docusaurus** | favicon.ico, apple-touch-icon.png, android-chrome PNGs, og-image.png, navbar logo SVG | Replace files in `docs-site/static/img/`, update `docusaurus.config.js` if paths changed |
| **Shopify App Store** | shopify-app-icon.png (1200x1200) | Upload via Shopify Partner Dashboard → App Setup → App icon |
| **Shopify Dev Dashboard** | App icon | Must match App Store listing icon exactly |
| **GitHub repository** | Avatar | Upload via GitHub → Organization Settings → Avatar |
| **Marketing website** | Logo in header/footer, og-image | Replace in website assets directory |
| **Email templates** | Header logo | Replace in email template assets (when created) |
| **Social media** | Profile pictures, cover images | Upload to each platform manually |
| **Stripe** | Branding icon | Upload via Stripe Dashboard → Settings → Branding |
| **Legal documents** | Header logo (if embedded) | Re-export PDFs with updated logo |

### Step 5: Verify

- [ ] Website renders correct logo (all pages, light/dark if applicable)
- [ ] Browser favicon shows updated icon (clear browser cache)
- [ ] Shopify App Store listing shows updated icon
- [ ] Shopify Dev Dashboard icon matches listing
- [ ] Social media link previews show updated OG image (use og:image debugger tools)
- [ ] GitHub repo avatar is updated
- [ ] Stripe checkout/portal shows updated branding
- [ ] All SVG source files in `branding/logo/` are consistent

### Step 6: Commit

Commit all updated source files, export tool, and raster exports together in a single commit with message: `Update logo assets — [describe change]`

---

## Files in This Directory

```
branding/logo/
├── LOGO-SPEC.md              # This file — specification, manifest, update procedure
├── logo-concepts.html         # Visual preview of all 3 logo concepts (approved: The Beacon)
├── export-all-sizes.html      # Interactive export tool — generates all PNG assets
├── icon-master.svg            # SVG source: icon only (1200x1200)
├── primary-logo-light.svg     # SVG source: icon + wordmark, light background
├── primary-logo-dark.svg      # SVG source: icon + wordmark, dark background
├── wordmark-light.svg         # SVG source: wordmark only, light background
├── wordmark-dark.svg          # SVG source: wordmark only, dark background
├── og-image.svg               # SVG source: Open Graph social preview (1200x630)
└── exports/                   # Raster exports (generated from export tool)
    ├── favicon-16x16.png
    ├── favicon-32x32.png
    ├── favicon.ico
    ├── apple-touch-icon.png
    ├── android-chrome-192.png
    ├── android-chrome-512.png
    ├── app-icon-1024.png
    ├── shopify-app-icon.png
    ├── primary-logo-light.png
    ├── primary-logo-dark.png
    └── og-image.png
```

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
