# UI Enhancement Proposal — Agent Red Customer Experience

**Document Type:** Proposal (non-binding)  
**Created:** 2026-02-17  
**Purpose:** Detailed recommendations for enhancing the user interfaces across all admin surfaces, aligned with contemporary SaaS norms, consistency, usability, performance, and implementation quality.

---

## Executive Summary

Agent Red Customer Experience has **four distinct UI surfaces**: Provider Admin (platform operator), Standalone Admin (Stripe-direct merchants), Shopify Embedded Admin (Shopify merchants), and the customer-facing Chat Widget. The current implementation is functional and production-ready (178 UI tests, v1.39.0), but there are clear opportunities to improve consistency, maintainability, usability, and alignment with modern SaaS expectations. This proposal prioritizes changes by impact and effort.

---

## 1. Current UI Architecture Summary

### 1.1 Surface Inventory

| Surface | Location | Framework | Auth | Pages |
|--------|----------|-----------|------|-------|
| **Provider Admin** | `admin/provider/` | Mantine 7 | API key (SUPERADMIN) | 13 (Dashboard, Tenants, Deployments, Queues, Integrations, Status, Alerts, Compliance, Secrets, Billing, SLA, MFA) |
| **Standalone Admin** | `admin/standalone/` | Mantine 7 | API key | 10 (Dashboard, Inbox, Configuration, KB, Widget, Quick Actions, Integrations, Memory & Privacy, Billing, Team) |
| **Shopify Admin** | `admin/shopify/` | Polaris 12 + App Bridge | Session token | 7 (Dashboard, Inbox, Configuration, Knowledge Base, Widget, Billing, Settings) |
| **Chat Widget** | `widget/` | Preact | Widget key | N/A (embedded) |

### 1.2 Shared Components

Fifteen shared components in `admin/shared/` are consumed by Standalone and (via Polaris wrappers) Shopify Admin:

- `ActivationDialog`, `ActivationBanner`, `RestoreDialog`, `ConfirmDialog`
- `ConfigEditor`, `WidgetConfigurator`, `KnowledgeBaseManager`
- `ConversationInbox`, `IntegrationsManager`, `McpConfigPanel`
- `BillingPortal`, `UsageDashboard`, `TeamManager`
- `HelpTooltip`, `AnalyticsOverview`

### 1.3 Design System

- **Primary:** `#ff3621` (Agent Red)
- **Dark hierarchy:** Chrome `#0a0a0a` → Page `#141414` → Surface `#1f1f1f` → Border `#272727`
- **Font:** Inter (primary), JetBrains Mono (monospace)
- **Default:** Dark mode for Provider and Standalone; Polaris light for Shopify embedded

---

## 2. Contemporary SaaS Product Norms & Standards

Based on 2024–2026 design research and product benchmarks:

| Norm | Description | Current State |
|------|-------------|---------------|
| **F-pattern layout** | Critical metrics and nav in top-left quadrant | Partially met (sidebar + header) |
| **Progressive disclosure** | Essential info first; reveal complexity on demand | Mixed — some pages dense |
| **Operational dashboards** | Next-best-action, not just reporting | Limited — mostly read-only |
| **Modular UI** | User-configurable views, filters, widgets | Not implemented |
| **AI co-pilot integration** | Predictive insights, recommendations | Not implemented |
| **Accessibility (a11y)** | WCAG 2.1 AA, keyboard nav, screen readers | Partial (some `aria-label`, `role`) |
| **Dark mode support** | Required, not optional | Provider/Standalone: yes; Shopify: Polaris default |
| **Empty states with CTAs** | Clear next steps when no data | Some pages use "No data" text only |
| **Responsive / mobile** | Collapsible sidebar, touch-friendly | Burger menu present; variable quality |

---

## 3. Findings & Recommendations

### 3.1 Consistency

#### Issue: Theme duplication

**Finding:** The `agentRedTheme` object is duplicated in `admin/provider/index.tsx` and `admin/standalone/index.tsx` (with minor differences). Any design change requires edits in multiple files.

**Recommendation:**

- Extract theme to a shared design tokens module: `admin/shared/theme/agentRedTheme.ts` (or `theme.ts`).
- Export `agentRedTheme` and consume it from both Provider and Standalone entry points.
- Consider `admin/shared` as a workspace package if not already, so it can host theme, tokens, and shared components.

#### Issue: Navigation icon inconsistency

**Finding:** Provider uses Unicode emoji for nav items (📊, 👥, etc.); Standalone uses inline SVG icons. This creates visual and semantic inconsistency.

**Recommendation:**

- Standardize on SVG icons for both surfaces. Standalone already has a robust `Icons` object in `StandaloneLayout.tsx`.
- Extract shared icons to `admin/shared/icons/` (or similar) and import them in both Provider and Standalone layouts.

#### Issue: Shopify ↔ Mantine visual disconnect

**Finding:** Shopify embedded admin uses Polaris (light theme, Shopify design language); Standalone and Provider use Mantine (dark theme, Agent Red brand). Users who switch between “Open full admin” and embedded Shopify may experience a jarring visual change.

**Recommendation:**

- Accept platform constraints: Polaris is required for Shopify embedded. Document the design split and ensure shared *components* (ConfigEditor, KB, etc.) are visually coherent within each context.
- Add a brief “design system” note in `CLAUDE-ARCHITECTURE.md` or `docs/architecture/` explaining the dual-surface approach.

### 3.2 Style & Completeness

#### Issue: Inline styles in key components

**Finding:** `ApiKeyLogin` (Provider and Standalone), `McpConfigPanel`, and parts of `IntegrationsManager` use inline `React.CSSProperties` instead of Mantine components. This bypasses theming and makes global style changes harder.

**Recommendation:**

- Migrate login pages and McpConfigPanel to Mantine `TextInput`, `Button`, `Paper`, etc., while preserving the dark look and feel.
- Use Mantine’s `styles` API or CSS modules for component-specific overrides rather than full inline styles.

#### Issue: Provider Docs ActionIcon

**Finding:** Provider header “Docs” link uses `ActionIcon` with `<Text size="sm">Docs</Text>` instead of an icon, inconsistent with Standalone’s `Icons.docs`.

**Recommendation:**

- Replace with the same `Icons.docs` SVG used in Standalone (after extracting to shared).

### 3.3 Usability

#### Issue: Empty states

**Finding:** Some pages (e.g., “No conversations yet,” “No volume data available”) use plain text without clear CTAs or guidance.

**Recommendation:**

- Add empty-state components with illustration (or minimal icon), short copy, and a primary CTA (e.g., “Add your first article” → Knowledge Base).
- Reuse pattern across Provider, Standalone, and shared components.

#### Issue: Loading states

**Finding:** Loading states vary: `Loader`, `Skeleton`, “Loading...”, and raw spinners. No consistent pattern.

**Recommendation:**

- Standardize on Mantine `Skeleton` for content placeholders and `Loader` for full-page/centered loads.
- Document in a short “UI patterns” guide and apply consistently.

#### Issue: Help tooltips

**Finding:** `HelpTooltip` exists and is used on Dashboard; coverage is uneven across other pages.

**Recommendation:**

- Audit pages for metrics and controls that would benefit from `HelpTooltip` and add tooltips with doc links.
- Consider a “?” icon pattern for dense configuration sections.

### 3.4 Performance & Quality

#### Issue: Recharts on Dashboard

**Finding:** `Dashboard.tsx` uses `recharts` (AreaChart, etc.). Recharts can add noticeable bundle size. No explicit code-splitting or lazy-loading for charts.

**Recommendation:**

- Use `React.lazy` + `Suspense` to lazy-load the chart section, or consider lighter chart libraries (e.g., Chart.js with tree-shaking, or CSS-based mini-charts for simple metrics).
- Measure bundle impact before and after.

#### Issue: Provider emoji in DOM

**Finding:** Unicode emoji in nav may render differently across OS/browsers and can affect accessibility (screen readers may announce emoji names).

**Recommendation:**

- Replace with SVG icons; improves consistency and a11y.

### 3.5 Accessibility

#### Issue: Partial a11y coverage

**Finding:** Some components have `aria-label`, `role`, `tabIndex`; many interactive elements do not. No systematic audit.

**Recommendation:**

- Run `eslint-plugin-jsx-a11y` (and/or `axe-core`) in CI.
- Add `aria-label` to all icon-only buttons, ensure form labels are associated, and verify focus order on modals.
- Add keyboard support for critical flows (e.g., Escape to close dialogs).

### 3.6 Correctness

#### Issue: Shopify route mismatch

**Finding:** `ShopifyAppLayout` nav registers `destination: '/knowledge-base'`, but `index.tsx` defines `Route path="/knowledge"`. Clicking “Knowledge Base” navigates to a non-existent route.

**Recommendation (urgent):**

- Align route and nav: either change route to `path="/knowledge-base"` or change nav to `destination: '/knowledge'`. Prefer `/knowledge-base` for URL clarity.

---

## 4. Prioritized Action Plan

### Phase 1: Quick Wins (1–2 days)

| # | Action | Surface(s) | Effort |
|---|--------|------------|--------|
| 1.1 | Fix Shopify route: `/knowledge` → `/knowledge-base` (or vice versa) | Shopify | S |
| 1.2 | Extract `agentRedTheme` to shared module; consume from Provider + Standalone | Provider, Standalone | S |
| 1.3 | Replace Provider “Docs” text with shared docs icon | Provider | S |
| 1.4 | Replace Provider emoji nav with SVG icons (reuse Standalone pattern) | Provider | S |

### Phase 2: Consistency & Maintainability (2–3 days)

| # | Action | Surface(s) | Effort |
|---|--------|------------|--------|
| 2.1 | Extract shared icons to `admin/shared/icons/` | Provider, Standalone | M |
| 2.2 | Migrate `ApiKeyLogin` (Provider + Standalone) to Mantine components | Provider, Standalone | M |
| 2.3 | Migrate `McpConfigPanel` to Mantine components | Shared | M |
| 2.4 | Add empty-state component with CTA pattern; apply to key pages | Shared, Standalone, Provider | M |

### Phase 3: Usability & Polish (3–5 days)

| # | Action | Surface(s) | Effort |
|---|--------|------------|--------|
| 3.1 | Standardize loading states (Skeleton vs Loader); document pattern | All | M |
| 3.2 | Extend HelpTooltip coverage to configuration and analytics pages | Shared, Standalone | M |
| 3.3 | Accessibility audit: add `aria-label` to icon buttons, fix focus order | All | M |
| 3.4 | Document design system (dual-surface: Polaris vs Mantine) | Docs | S |

### Phase 4: Performance & Advanced UX (optional, post-launch)

| # | Action | Surface(s) | Effort |
|---|--------|------------|--------|
| 4.1 | Lazy-load Recharts or evaluate lighter chart library | Standalone | M |
| 4.2 | Add global date/period filter to dashboard header | Standalone | M |
| 4.3 | Introduce `eslint-plugin-jsx-a11y` in CI | All | S |

---

## 5. Implementation Notes

### 5.1 Theme Extraction

Suggested structure:

```
admin/shared/
  theme/
    agentRedTheme.ts   # createTheme(...) export
    tokens.ts          # optional: raw color/spacing tokens
```

Both `admin/provider/index.tsx` and `admin/standalone/index.tsx` would import:

```ts
import { agentRedTheme } from '../../shared/theme/agentRedTheme';
```

### 5.2 Shared Icons

Suggested structure:

```
admin/shared/
  icons/
    index.tsx   # Icons object, same as StandaloneLayout today
```

Provider and Standalone layouts import:

```ts
import { Icons } from '../../shared/icons';
```

### 5.3 Empty State Component

Suggested API:

```tsx
<EmptyState
  icon="knowledge"
  title="No knowledge base articles yet"
  description="Add articles to help your AI answer customer questions."
  action={{ label: 'Add article', onClick: () => navigate('/knowledge-base') }}
/>
```

### 5.4 Route Fix

In `admin/shopify/index.tsx`:

- Change `path="/knowledge"` to `path="/knowledge-base"` to match `ShopifyAppLayout` nav.

---

## 6. Out of Scope (for this proposal)

- Widget UI redesign (separate review)
- Shopify Theme App Extension UI
- Marketing website (website/content/)
- Docs site (docs-site/)
- New features (modular dashboards, AI co-pilot, etc.) — track in backlog

---

## 7. Success Criteria

| Criterion | Target |
|-----------|--------|
| Theme duplication | 0 (single source) |
| Nav icon consistency | Provider and Standalone use same icon set |
| Shopify Knowledge Base | Navigable and functional |
| Empty states | At least Dashboard, Inbox, KB, Integrations |
| A11y | All icon-only buttons have `aria-label`; no critical axe violations |
| Loading pattern | Documented and applied consistently |

---

## 8. References

- `CLAUDE-ARCHITECTURE.md` — project structure
- `docs/operations/ui-test-procedure.md` — 178 UI regression tests
- `admin/provider/index.tsx`, `admin/standalone/index.tsx` — theme definitions
- `admin/shared/` — shared components
- SaaS Dashboard Design Best Practices (2024–2026)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
