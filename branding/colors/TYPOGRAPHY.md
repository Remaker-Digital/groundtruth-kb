# Agent Red Customer Engagement — Typography

> **Status:** Approved
> **Direction:** Bold/Corporate
> **Visual Preview:** [`color-palette.html`](color-palette.html) (Typography section)

---

## Font Stack

| Role | Font | Source | License |
|------|------|--------|---------|
| **Headings** | Inter | [Google Fonts](https://fonts.google.com/specimen/Inter) | SIL Open Font License |
| **Body** | Inter | [Google Fonts](https://fonts.google.com/specimen/Inter) | SIL Open Font License |
| **Code / Data** | JetBrains Mono | [Google Fonts](https://fonts.google.com/specimen/JetBrains+Mono) | SIL Open Font License |

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

---

## Type Scale

| Element | Size | Weight | Line Height | Letter Spacing | Usage |
|---------|------|--------|-------------|----------------|-------|
| **H1** | 40px / 2.5rem | 700 (Bold) | 1.2 | -0.02em | Page titles, hero headlines |
| **H2** | 30px / 1.875rem | 700 (Bold) | 1.25 | -0.01em | Section headers |
| **H3** | 24px / 1.5rem | 600 (Semi-Bold) | 1.3 | 0 | Subsection headers |
| **H4** | 20px / 1.25rem | 600 (Semi-Bold) | 1.35 | 0 | Card titles, feature names |
| **Body Large** | 18px / 1.125rem | 400 (Regular) | 1.6 | 0 | Hero subtitles, lead paragraphs |
| **Body** | 16px / 1rem | 400 (Regular) | 1.6 | 0 | Default body text |
| **Body Small** | 14px / 0.875rem | 400 (Regular) | 1.5 | 0 | Captions, helper text, metadata |
| **Code** | 14px / 0.875rem | 400 (Regular) | 1.5 | 0 | Code blocks, API references, data |
| **Label** | 12px / 0.75rem | 500 (Medium) | 1.4 | 0.5px | Badges, tags, uppercase labels |

---

## Weight Usage

| Weight | Value | Usage |
|--------|-------|-------|
| Regular | 400 | Body text, descriptions, paragraphs |
| Medium | 500 | Labels, badges, emphasized body text, nav links |
| Semi-Bold | 600 | H3, H4, buttons, table headers |
| Bold | 700 | H1, H2, hero stats, brand name |

---

## Design Rationale

- **Inter** was chosen for its precision at screen sizes, excellent readability, and professional character that aligns with the Bold/Corporate direction.
- **Single-family system** ensures visual consistency across all touchpoints while reducing font load times (one font family instead of two).
- **JetBrains Mono** provides clear, distinct characters for technical content — API docs, code samples, hex values, and metrics.
- All fonts are free via Google Fonts with SIL Open Font License (no licensing cost or restrictions).

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
