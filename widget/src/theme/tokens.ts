/**
 * Design tokens — the single source of truth for all visual values.
 *
 * This file defines the token interface and derives concrete tokens from
 * the merchant's widget config. Components reference tokens, never
 * hardcoded values. A design specialist modifies only this directory
 * to change the widget's visual identity.
 *
 * Architecture:
 *   - WidgetConfig (from /api/config) → resolveTokens() → DesignTokens
 *   - Components consume DesignTokens via context
 *   - Light/dark modes are separate token sets
 *
 * Visual reference: Zapier (layouts, spacing, forms, buttons).
 * Functional reference: Tidio (controls, behaviors, workflows).
 * Brand: Agent Red (Inter, #ff3621, 15-color palette).
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

// ---------------------------------------------------------------------------
// Token interface
// ---------------------------------------------------------------------------

export interface DesignTokens {
  // Colors
  colorPrimary: string;
  colorPrimaryHover: string;
  colorPrimaryText: string;
  colorBackground: string;
  colorSurface: string;
  colorSurfaceHover: string;
  colorBorder: string;
  colorText: string;
  colorTextSecondary: string;
  colorTextMuted: string;
  colorAgentBubble: string;
  colorAgentBubbleText: string;
  colorCustomerBubble: string;
  colorCustomerBubbleText: string;
  colorError: string;
  colorSuccess: string;
  colorOverlay: string;

  // Typography (Zapier reference: clean, readable, consistent)
  fontFamily: string;
  fontFamilyMono: string;
  fontSizeXs: string;
  fontSizeSm: string;
  fontSizeMd: string;
  fontSizeLg: string;
  fontSizeXl: string;
  fontWeightNormal: number;
  fontWeightMedium: number;
  fontWeightSemibold: number;
  fontWeightBold: number;
  lineHeightTight: number;
  lineHeightNormal: number;
  lineHeightRelaxed: number;

  // Spacing (Zapier reference: 4px base grid)
  space1: string;  // 4px
  space2: string;  // 8px
  space3: string;  // 12px
  space4: string;  // 16px
  space5: string;  // 20px
  space6: string;  // 24px
  space8: string;  // 32px
  space10: string; // 40px
  space12: string; // 48px

  // Borders & radii (Zapier reference: subtle, consistent)
  borderRadius: string;
  borderRadiusSm: string;
  borderRadiusLg: string;
  borderRadiusFull: string;
  borderWidth: string;

  // Shadows
  shadowSm: string;
  shadowMd: string;
  shadowLg: string;

  // Sizing
  launcherSize: string;
  panelWidth: string;
  panelHeight: string;
  headerHeight: string;
  inputBarHeight: string;
  avatarSize: string;
  avatarSizeSm: string;

  // Transitions
  transitionFast: string;
  transitionNormal: string;

  // Z-index (widget sits above merchant content)
  zIndexLauncher: number;
  zIndexPanel: number;
  zIndexOverlay: number;
}

// ---------------------------------------------------------------------------
// Widget config shape (subset of PreferencesDocument widget_* fields)
// ---------------------------------------------------------------------------

export interface WidgetConfig {
  widget_primary_color?: string | null;
  widget_background_color?: string | null;
  widget_position?: 'bottom-right' | 'bottom-left' | null;
  widget_offset_x?: number | null;
  widget_offset_y?: number | null;
  widget_agent_avatar_url?: string | null;
  widget_agent_display_name?: string | null;
  widget_agent_title?: string | null;
  widget_logo_url?: string | null;
  widget_show_branding?: boolean | null;
  widget_mobile_enabled?: boolean | null;
  widget_dark_mode?: boolean | null;
  widget_offline_message?: string | null;
  widget_auto_open?: boolean | null;
  widget_auto_open_delay?: number | null;
  widget_operating_hours?: Record<string, unknown> | null;
  widget_offline_behavior?: 'ai_only' | 'show_form' | 'hide_widget' | null;
  widget_prechat_form?: Record<string, unknown> | null;
  widget_chat_rating_enabled?: boolean | null;
  widget_sound_enabled?: boolean | null;
  widget_file_upload_enabled?: boolean | null;
  widget_header_text?: string | null;
  widget_input_placeholder?: string | null;
  widget_page_rules?: string[] | null;
  // Non-widget fields used for display
  brand_name?: string | null;
  greeting_message?: string | null;
}

// ---------------------------------------------------------------------------
// Defaults
// ---------------------------------------------------------------------------

const DEFAULTS = {
  primaryColor: '#ff3621',
  backgroundColor: '#FFFFFF',
  position: 'bottom-right' as const,
  offsetX: 20,
  offsetY: 20,
};

// ---------------------------------------------------------------------------
// Color utilities
// ---------------------------------------------------------------------------

/** Darken a hex color by a percentage (0-1). */
function darken(hex: string, amount: number): string {
  const num = parseInt(hex.replace('#', ''), 16);
  const r = Math.max(0, Math.min(255, ((num >> 16) & 0xff) - Math.round(255 * amount)));
  const g = Math.max(0, Math.min(255, ((num >> 8) & 0xff) - Math.round(255 * amount)));
  const b = Math.max(0, Math.min(255, (num & 0xff) - Math.round(255 * amount)));
  return `#${((r << 16) | (g << 8) | b).toString(16).padStart(6, '0')}`;
}

/** Calculate relative luminance for WCAG contrast. */
function luminance(hex: string): number {
  const num = parseInt(hex.replace('#', ''), 16);
  const rsrgb = ((num >> 16) & 0xff) / 255;
  const gsrgb = ((num >> 8) & 0xff) / 255;
  const bsrgb = (num & 0xff) / 255;
  const r = rsrgb <= 0.03928 ? rsrgb / 12.92 : ((rsrgb + 0.055) / 1.055) ** 2.4;
  const g = gsrgb <= 0.03928 ? gsrgb / 12.92 : ((gsrgb + 0.055) / 1.055) ** 2.4;
  const b = bsrgb <= 0.03928 ? bsrgb / 12.92 : ((bsrgb + 0.055) / 1.055) ** 2.4;
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

/** Choose white or black text for contrast against a background. */
function contrastText(bgHex: string): string {
  return luminance(bgHex) > 0.179 ? '#1A1A1A' : '#FFFFFF';
}

// ---------------------------------------------------------------------------
// Token resolution
// ---------------------------------------------------------------------------

export function resolveTokens(config: WidgetConfig): DesignTokens {
  const primary = config.widget_primary_color || DEFAULTS.primaryColor;
  const bg = config.widget_background_color || DEFAULTS.backgroundColor;
  const isDark = config.widget_dark_mode === true;

  // Shared structural tokens (Zapier-derived)
  const base: Omit<DesignTokens,
    | 'colorPrimary' | 'colorPrimaryHover' | 'colorPrimaryText'
    | 'colorBackground' | 'colorSurface' | 'colorSurfaceHover'
    | 'colorBorder' | 'colorText' | 'colorTextSecondary' | 'colorTextMuted'
    | 'colorAgentBubble' | 'colorAgentBubbleText'
    | 'colorCustomerBubble' | 'colorCustomerBubbleText'
    | 'colorError' | 'colorSuccess' | 'colorOverlay'
  > = {
    // Typography — Inter (brand), JetBrains Mono (code)
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    fontFamilyMono: "'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace",
    fontSizeXs: '11px',
    fontSizeSm: '12px',
    fontSizeMd: '14px',
    fontSizeLg: '16px',
    fontSizeXl: '18px',
    fontWeightNormal: 400,
    fontWeightMedium: 500,
    fontWeightSemibold: 600,
    fontWeightBold: 700,
    lineHeightTight: 1.25,
    lineHeightNormal: 1.5,
    lineHeightRelaxed: 1.75,

    // Spacing — 4px base grid (Zapier pattern)
    space1: '4px',
    space2: '8px',
    space3: '12px',
    space4: '16px',
    space5: '20px',
    space6: '24px',
    space8: '32px',
    space10: '40px',
    space12: '48px',

    // Borders (Zapier: subtle, 1px, medium radius)
    borderRadius: '8px',
    borderRadiusSm: '4px',
    borderRadiusLg: '12px',
    borderRadiusFull: '9999px',
    borderWidth: '1px',

    // Shadows (Zapier: minimal, functional)
    shadowSm: '0 1px 2px rgba(0,0,0,0.05)',
    shadowMd: '0 4px 12px rgba(0,0,0,0.1)',
    shadowLg: '0 8px 24px rgba(0,0,0,0.15)',

    // Sizing
    launcherSize: '60px',
    panelWidth: '380px',
    panelHeight: '520px',
    headerHeight: '64px',
    inputBarHeight: '56px',
    avatarSize: '40px',
    avatarSizeSm: '28px',

    // Transitions
    transitionFast: '120ms ease',
    transitionNormal: '200ms ease',

    // Z-index
    zIndexLauncher: 2147483640,
    zIndexPanel: 2147483641,
    zIndexOverlay: 2147483642,
  };

  // Color tokens — split by light/dark mode
  if (isDark) {
    return {
      ...base,
      colorPrimary: primary,
      colorPrimaryHover: darken(primary, -0.1),
      colorPrimaryText: contrastText(primary),
      colorBackground: '#1A1A1A',
      colorSurface: '#2A2A2A',
      colorSurfaceHover: '#333333',
      colorBorder: '#3A3A3A',
      colorText: '#F0F0F0',
      colorTextSecondary: '#AAAAAA',
      colorTextMuted: '#777777',
      colorAgentBubble: '#2A2A2A',
      colorAgentBubbleText: '#F0F0F0',
      colorCustomerBubble: primary,
      colorCustomerBubbleText: contrastText(primary),
      colorError: '#EF4444',
      colorSuccess: '#22C55E',
      colorOverlay: 'rgba(0, 0, 0, 0.6)',
    };
  }

  return {
    ...base,
    colorPrimary: primary,
    colorPrimaryHover: darken(primary, 0.08),
    colorPrimaryText: contrastText(primary),
    colorBackground: bg,
    colorSurface: '#F7F7F8',
    colorSurfaceHover: '#EFEFEF',
    colorBorder: '#E5E5E5',
    colorText: '#1A1A1A',
    colorTextSecondary: '#6B6B6B',
    colorTextMuted: '#9A9A9A',
    colorAgentBubble: '#F0F0F2',
    colorAgentBubbleText: '#1A1A1A',
    colorCustomerBubble: primary,
    colorCustomerBubbleText: contrastText(primary),
    colorError: '#DC2626',
    colorSuccess: '#16A34A',
    colorOverlay: 'rgba(0, 0, 0, 0.4)',
  };
}
