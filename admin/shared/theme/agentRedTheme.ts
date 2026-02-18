/**
 * Agent Red Brand Theme — shared design tokens for Mantine surfaces.
 *
 * Consumed by both Provider Console and Standalone Admin entry points.
 * Shopify embedded admin uses Polaris (separate design system).
 *
 * Four-tier dark mode hierarchy (designer-approved):
 *   chrome #0a0a0a → page #141414 → surface #1f1f1f → border #272727
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { createTheme } from '@mantine/core';

export const agentRedTheme = createTheme({
  primaryColor: 'brand',
  colors: {
    // Brand red scale: lightest -> darkest, index 5 = primary #ff3621
    brand: [
      '#FDE8E8', // 0 - error bg tint
      '#F2D4D6', // 1 - Soft Red (Primary Light)
      '#E8A3A7', // 2
      '#DC7278', // 3
      '#D14B52', // 4
      '#ff3621', // 5 - Agent Red (Primary)
      '#B01824', // 6
      '#9B1420', // 7 - Deep Red (Primary Dark, hover)
      '#870E18', // 8
      '#720912', // 9
    ],
    // Neutral grey dark scale — designer-approved (2026-02-03 mockup, revised by Mazel)
    // Depth hierarchy: header/sidebar (#0a0a0a) -> page (#141414) -> cards (#1f1f1f) -> borders (#272727)
    dark: [
      '#F5F5F5', // 0 - Light grey (text on dark bg)
      '#E0E0E0', // 1 - Borders (light)
      '#A0A0A0', // 2 - Muted text
      '#787878', // 3 - Secondary text
      '#5C5C5C', // 4 - Tertiary text
      '#141414', // 5 - Page background
      '#1f1f1f', // 6 - Cards / elevated surfaces
      '#0a0a0a', // 7 - Header, sidebar (deepest chrome)
      '#1f1f1f', // 8 - Card surface (alias)
      '#0a0a0a', // 9 - True dark (alias)
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
      primary: '#ff3621',
      primaryDark: '#9B1420',
      primaryLight: '#F2D4D6',
      charcoal: '#0a0a0a',
      slate: '#141414',
      steel: '#5C5C5C',
      silver: '#E0E0E0',
      snow: '#F5F5F5',
      success: '#0D7C3E',
      warning: '#E5A100',
      error: '#D32F2F',
      info: '#1E3A5F',
    },
  },
});
