/**
 * Agent Red Brand Theme — shared design tokens for Mantine surfaces.
 *
 * Consumed by both Provider Console and Standalone Admin entry points.
 * Shopify embedded admin uses Polaris (separate design system).
 *
 * Design system (2026-02-19 revision):
 *   - "action" (blue) is primaryColor for affirmative controls (Save, Activate, etc.)
 *   - "brand" (red #ff3621) is accent-only — active nav, badges, brand highlights
 *   - "dark" uses Stone neutral scale from MantineHub for warm depth hierarchy
 *
 * Four-tier dark mode hierarchy (Stone neutrals):
 *   chrome #0c0a09 → page #1c1917 → surface #292524 → border #44403c
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { createTheme } from '@mantine/core';
export const agentRedTheme = createTheme({
    primaryColor: 'action',
    // NOTE: No primaryShade override — Mantine default { light: 6, dark: 8 } applies.
    // The action palette is structured so index 8 = #3B82F6 (dark-mode primary).
    // This preserves correct shade selection for built-in palettes (red, green, yellow).
    colors: {
        // Affirmative action blue — buttons, switches, checkboxes, loaders
        // Structured for dark mode: index 8 is the primary shade Mantine picks.
        // Scale is monotonically light→dark (0=lightest, 9=darkest).
        action: [
            '#eff6ff', // 0 - Lightest tint
            '#dbeafe', // 1
            '#bfdbfe', // 2
            '#93c5fd', // 3
            '#7db8fc', // 4
            '#60a5fa', // 5
            '#4b94f7', // 6 - Light-mode primary
            '#3B82F6', // 7 - Our target blue
            '#3B82F6', // 8 - Primary (dark mode) ← Mantine picks this in dark mode
            '#2563EB', // 9 - Darkest (hover/pressed)
        ],
        // Brand red scale — accent only (NOT for affirmative controls)
        // Used for: active nav indicator, brand badges, logo highlights
        brand: [
            '#FDE8E8', // 0 - error bg tint
            '#F2D4D6', // 1 - Soft Red (Primary Light)
            '#E8A3A7', // 2
            '#DC7278', // 3
            '#D14B52', // 4
            '#ff3621', // 5 - Agent Red (Primary)
            '#B01824', // 6
            '#9B1420', // 7 - Deep Red (Primary Dark)
            '#870E18', // 8
            '#720912', // 9
        ],
        // Stone neutral dark scale (MantineHub Stone, warm undertone)
        // Depth hierarchy: chrome (#0c0a09) → page (#1c1917) → surface (#292524) → border (#44403c)
        dark: [
            '#fafaf9', // 0 - Lightest (text on dark bg)
            '#f5f5f4', // 1 - Light text / borders
            '#e7e5e4', // 2
            '#d6d3d1', // 3
            '#a8a29e', // 4 - Muted text
            '#57534e', // 5 - Tertiary text
            '#44403c', // 6 - Border
            '#292524', // 7 - Surface (cards, paper)
            '#1c1917', // 8 - Page background
            '#0c0a09', // 9 - Chrome (header, sidebar)
        ],
    },
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    fontFamilyMonospace: "'JetBrains Mono', ui-monospace, monospace",
    headings: {
        fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        fontWeight: '600',
    },
    defaultRadius: 'md',
    cursorType: 'pointer',
    other: {
        colors: {
            // Brand accent (identity, not interactive)
            brand: '#ff3621',
            brandDark: '#9B1420',
            brandLight: '#F2D4D6',
            // Action (affirmative controls)
            action: '#3B82F6',
            actionDark: '#2563EB',
            actionLight: '#dbeafe',
            // Surface hierarchy (Stone)
            chrome: '#0c0a09',
            page: '#1c1917',
            surface: '#292524',
            border: '#44403c',
            // Text hierarchy
            textPrimary: '#fafaf9',
            textSecondary: '#f5f5f4',
            textMuted: '#a8a29e',
            textTertiary: '#57534e',
            // Semantic
            success: '#0D7C3E',
            warning: '#E5A100',
            error: '#e03131',
            info: '#1E3A5F',
        },
    },
});
//# sourceMappingURL=agentRedTheme.js.map