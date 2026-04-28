# Spec Maturation Process

Meta-learning about the specification → test → owner verification → refinement cycle.

## Process (per area)

1. **Gather specs** — Query KB for existing SPEC-NNNN entries in the area domain
2. **Inspect implementation** — Read the actual source file to build a full inventory of elements (labels, controls, defaults, behavior)
3. **Specify on contact** — Elements found in implementation but missing from specs get retroactive specs
4. **Write E2E tests** — Playwright tests that validate each spec against the running admin UI
5. **Run tests** — Fix locator issues until all tests pass
6. **Owner verifies** — Owner manually checks the page and identifies spec gaps (things that pass tests but aren't "right")
7. **Refine specs** — Owner feedback → update specs → update tests → re-verify

## Lessons from Widget Configuration (S106, first area)

### Locator Patterns for Mantine UI

| Pattern | Issue | Fix |
|---------|-------|-----|
| `get_by_text("X", exact=True)` | Fails when Mantine component has child elements (HelpTooltip) inside the same `<Text>` wrapper | Remove `exact=True` for SectionHeader labels |
| `locator("code")` | Mantine `<Code block>` might not render immediately if data is loading async | Use broader `code, pre, [class*='Code']` selector + wait buffer |
| `.locator("..").evaluate("getComputedStyle(el).opacity")` | CSS property set on grandparent, not direct parent | Walk ancestor chain: `for (let i = 0; i < 5; i++) node = node.parentElement` |
| SegmentedControl options | Renders as `<label>` elements, not plain text | Use `locator("label", has_text=...)` for option verification |

### Data Flow for Widget Page

- `useConfig(apiFetch)` calls `GET /api/config?state=draft` → routes to MOCK_CONFIG in conftest
- MOCK_CONFIG.config must include all `widget_*` fields for deterministic testing
- Widget.tsx `configToWidgetConfig()` maps `widget_*` keys → local WidgetConfig shape
- Fields NOT in API response fall back to `DEFAULT_WIDGET_CONFIG` hardcoded values

### Test Architecture

- **73 tests** across 10 test classes for Widget page alone
- Categories: Structure (7), Installation (15), Appearance (21), Behavior (7), Content (9), Actions (3), Rotation (6), Interactions (3), Data Loading (4)
- Session-scoped Vite dev server on port 3300 (reused if already running)
- All API routes mocked via `AdminApiMocker` — no backend needed
- Each test navigates to Widget page fresh (per-test fixture isolation)

### What Worked Well

- Mantine's semantic structure makes most labels directly testable via `get_by_text()`
- The mock infrastructure (AdminApiMocker) makes tests fully deterministic
- Splitting tests by section matches the page structure and makes failures easy to locate

### What to Watch For

- **Timing**: Config loads async — tests that check values (not just labels) may need a wait
- **Ambiguous text**: "Standard" appears in both Panel width and Panel shadow SegmentedControls — scope to parent if individual option verification is needed
- **Conditional display**: Pre-chat fields, AI greeting mode description only appear after toggling a switch — tests must click first
- **Modal locators**: Use `[role='dialog']` scope to disambiguate buttons that appear both in page and modal (e.g., "Rotate key")

## Lessons from Dashboard (S108, second area)

### Override Pattern Pitfalls

| Pattern | Issue | Fix |
|---------|-------|-----|
| `api_mocker.override("/api/config", ...)` | `/api/config` substring matches `/api/config/activation-status`, `/api/config/schema`, etc. — hijacks unrelated endpoints | Use query-param-specific patterns: `state=draft`, `page_type=all` |
| Activation-status `is_active: False` | Layout's `isActivated` check triggers OnboardingWizard modal, blocking sidebar ("Dashboard" link invisible) | Keep `is_configured: True` + `active_activated_at` non-null to satisfy layout, flip only `is_active: False` for Dashboard's SetupChecklist |

### Data Flow for Dashboard

- **7 API hooks**: `useAnalyticsSummary`, `useDailyVolume`, `useInboxConversations`, `useIntentBreakdown`, `useKnowledgeGaps`, `useConfig`, `useActivationStatus`
- Analytics endpoints use `/api/analytics/*` prefix (NOT `/api/admin/analytics`), daily volume uses `/api/dashboard/usage/daily` — both needed new conftest routes
- Layout also calls `/api/config/activation-status` (polling) and `/api/config?page_type=all` (test mode) — overrides must not conflict
- `InboxConversation` type uses `conversationId` (not `id`) — mock must match TypeScript interface shape

### Test Architecture

- **72 tests** across 12 test classes
- Categories: Structure (6), StatCards (14), SetupChecklist (4), TestModeAlert (3), ConversationChart (5), RecentConversations (8), TopTopics (4), TopicBreakdownTable (6), KnowledgeGaps (9), PeriodFilter (3), DataLoading (6), HelpTooltips (5)
- Dashboard is the default landing page → uses `admin_page` fixture directly (no sidebar navigation needed)
- Tests requiring non-default state use `setup_admin_page()` with targeted overrides
- `agentDisplayLabel()` converts `"order-tracking"` → `"Order Tracking"` — tests must match this format

### What Worked Well

- Mock data shapes matching TypeScript interfaces produced immediate PASS on first run for most tests
- Using query-param patterns in overrides avoids the broad-match pitfall entirely
- All stat card values are deterministic derivations from MOCK_ANALYTICS_SUMMARY — easy to verify

### What to Watch For

- **Layout vs Dashboard state interaction**: The StandaloneLayout and DashboardPage both call `/api/config/activation-status` independently. Overrides affect BOTH. The layout gates sidebar rendering and the onboarding wizard. Override responses must satisfy the layout's `isActivated` check while still testing Dashboard-specific behavior.
- **Topic label transformation**: The `agentDisplayLabel()` utility transforms `"order-tracking"` to `"Order Tracking"` (replace hyphens, capitalize words). Tests must assert on the DISPLAY label, not the raw agent name.
- **SegmentedControl clicks**: Period filter options render as `<label>` elements. Use `.locator("label").filter(has_text="7d")` to click.

## Areas Remaining

After Widget Configuration and Dashboard, the following areas need the same cycle:
- Agent Configuration
- Team Members
- Knowledge Base
- Memory & Privacy
- Inbox
- Billing

Priority ordering is at Claude's discretion per GOV-04 (owner-approved in S106).
