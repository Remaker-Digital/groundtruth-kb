# Admin Design System — Dual-Surface Architecture

> Reference for UI development across Agent Red's three admin surfaces.

## Surfaces

| Surface | Framework | Entry | Target User |
|---------|-----------|-------|-------------|
| **Provider** | Mantine v7 | `admin/provider/` | Platform operator (SPA) |
| **Standalone** | Mantine v7 | `admin/standalone/` | Stripe-direct merchant |
| **Shopify** | Polaris v12 | `admin/shopify/` | Shopify merchant (embedded app) |

## Dark Theme Hierarchy

All surfaces use a consistent dark palette:

| Token | Hex | Usage |
|-------|-----|-------|
| `chrome` | `#0a0a0a` | Header, sidebar, login background |
| `page` | `#141414` | Page content background, input bg |
| `surface` | `#1f1f1f` | Cards, papers, modals |
| `border` | `#272727` | Card borders, dividers, input borders |
| `border-subtle` | `#1E1E1E` | Nav dividers, header/sidebar borders |
| `text-primary` | `#F5F5F5` | Titles, emphasized text |
| `text-body` | `#E0E0E0` | Body text, labels |
| `text-muted` | `#A0A0A0` | Descriptions, secondary info |
| `text-dim` | `#787878` | Timestamps, hints, nav descriptions |
| `text-disabled` | `#5C5C5C` | Group labels, disabled icon color |
| `brand` | `#ff3621` | Primary buttons, active nav, links |
| `error` | `#ff6b6b` | Error text, error borders |

## Shared Components (`admin/shared/`)

Framework-agnostic React components using inline CSS. Safe to import from any surface.

| Component | File | Purpose |
|-----------|------|---------|
| `Icons` | `icons/index.tsx` | Consolidated SVG icon library (25+ icons) |
| `EmptyState` | `EmptyState.tsx` | Centered empty state with icon, title, subtitle, CTA |
| `LoadingState` | `LoadingState.tsx` | Spinner or skeleton loading placeholder |
| `HelpTooltip` | `HelpTooltip.tsx` | Inline "?" icon with hover tooltip |
| `ConversationInbox` | `ConversationInbox.tsx` | Shared conversation list + detail view |
| `KnowledgeBaseManager` | `KnowledgeBaseManager.tsx` | KB article CRUD + conflict scanner |
| `TeamManager` | `TeamManager.tsx` | Team member invite/edit/role management |
| `IntegrationsManager` | `IntegrationsManager.tsx` | Integration enable/disable with status |
| `UsageDashboard` | `UsageDashboard.tsx` | Conversation usage metrics |
| `BillingPortal` | `BillingPortal.tsx` | Subscription and billing management |
| `AnalyticsOverview` | `AnalyticsOverview.tsx` | Charts and topic analytics |
| `McpConfigPanel` | `McpConfigPanel.tsx` | MCP/Stripe credential config |

## Icon Library (`admin/shared/icons/`)

Single source of truth for all SVG icons across surfaces.

```tsx
import { Icons } from '../../shared/icons';

// Render with default size
<Icons.dashboard />

// Custom size + accessibility label
<Icons.alerts size={20} aria-label="Alert notifications" />
```

- Default: `aria-hidden`, `width/height` from `size` prop (default 18)
- With `aria-label`: adds `role="img"` for screen readers
- Aliases map surface-specific names: `tenants → Team`, `sla → Analytics`

## Mantine Usage (Provider + Standalone)

### Component Mapping

| Pattern | Component | Notes |
|---------|-----------|-------|
| Page loading | `<LoadingState />` | Shared, not Mantine Loader |
| Empty state | `<EmptyState />` | Shared, not ad hoc text |
| Card container | `<Card withBorder bg="#1f1f1f">` | Always `withBorder` |
| Form input | `<TextInput styles={{input:{...}}}` | Dark input styles |
| Password | `<PasswordInput>` | Auto-hide toggle |
| Data table | `<Table striped highlightOnHover>` | |
| Toast | `notifications.show()` | Via `@mantine/notifications` |
| Layout | `<AppShell>` | Header + sidebar + main |
| Modal | `<Modal styles={{content:{bg},header:{bg}}}>` | Dark backgrounds |
| Tabs | `<Tabs color="red">` | Brand color tabs |

### Input Style Pattern

```tsx
const inputStyles = {
  input: {
    backgroundColor: '#141414',
    borderColor: '#272727',
    color: '#e0e0e0',
    '&:focus': { borderColor: '#ff3621' },
  },
  label: { color: '#e0e0e0', fontWeight: 500 },
};
```

### Button Styles

- **Primary action**: `color="#ff3621"` (brand)
- **Destructive**: `color="red"` (Mantine red)
- **Secondary**: `variant="light"` or `variant="subtle"`
- **Link-style**: `<Anchor c="#ff3621">`

## HelpTooltip Convention

Place inline after labels, headers, or metrics that need explanation:

```tsx
<Text fw={600}>Queue Depth
  <HelpTooltip text="Number of unprocessed messages in the NATS queue." />
</Text>
```

- Keep text to 1-2 sentences
- Optional `docLink` for full documentation
- Coverage: all Provider SPA pages, standalone config/billing/dashboard pages

## Polaris Usage (Shopify)

Shopify embedded apps must use Polaris components exclusively.
The `admin/shopify/` surface does not import from `admin/shared/` (except
framework-agnostic components like `HelpTooltip` which use no CSS framework).

## Accessibility Standards

- **ESLint**: `eslint-plugin-jsx-a11y` enforced via `admin/.eslintrc.json`
- **aria-labels**: Required on all interactive elements (buttons, inputs, links)
- **Icons**: `aria-hidden` by default; use `aria-label` for standalone icon buttons
- **Loading**: `role="status"` on loading indicators
- **Empty states**: `role="status"` + `aria-label` on empty state containers
- **Focus management**: Brand color (`#ff3621`) focus rings on inputs

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
