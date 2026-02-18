/**
 * Shared style constants and helper factories for Knowledge Base sub-components.
 *
 * Framework-agnostic — no Polaris, no Tailwind, pure inline styles.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import type React from 'react';
import type { KBArticleStatus } from '../types';

// ---------------------------------------------------------------------------
// Color constants
// ---------------------------------------------------------------------------

export const BRAND_PRIMARY = '#ff3621';
export const COLOR_SUCCESS = '#22863a';
export const COLOR_DANGER = '#d73a49';
export const COLOR_GRAY = '#6a737d';
export const COLOR_LIGHT_GRAY = '#f6f8fa';
export const COLOR_BORDER = '#e1e4e8';
export const COLOR_WHITE = '#ffffff';
export const COLOR_TEXT = '#24292e';
export const COLOR_TEXT_SECONDARY = '#586069';
export const COLOR_WARNING = '#e36209';
export const FONT_FAMILY = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif";
export const BORDER_RADIUS = '6px';

// ---------------------------------------------------------------------------
// Badge style maps
// ---------------------------------------------------------------------------

export const STATUS_BADGE_STYLES: Record<KBArticleStatus, { bg: string; color: string; label: string }> = {
  draft: { bg: '#fff8c5', color: COLOR_WARNING, label: 'Draft' },
  published: { bg: '#dcffe4', color: COLOR_SUCCESS, label: 'Published' },
  archived: { bg: COLOR_LIGHT_GRAY, color: COLOR_GRAY, label: 'Archived' },
};

export const STALENESS_BADGE_STYLES: Record<string, { bg: string; color: string; label: string }> = {
  fresh: { bg: '#dcffe4', color: COLOR_SUCCESS, label: 'Fresh' },
  aging: { bg: '#fff8c5', color: COLOR_WARNING, label: 'Aging' },
  stale: { bg: '#ffeef0', color: COLOR_DANGER, label: 'Stale' },
  very_stale: { bg: '#ffeef0', color: COLOR_DANGER, label: 'Very stale' },
};

// ---------------------------------------------------------------------------
// Style helper factories
// ---------------------------------------------------------------------------

/** Standard text input / select / textarea base style. */
export function inputStyle(extraStyles?: React.CSSProperties): React.CSSProperties {
  return {
    width: '100%',
    padding: '8px 12px',
    border: `1px solid ${COLOR_BORDER}`,
    borderRadius: BORDER_RADIUS,
    fontSize: '14px',
    fontFamily: FONT_FAMILY,
    backgroundColor: COLOR_WHITE,
    color: COLOR_TEXT,
    boxSizing: 'border-box' as const,
    ...extraStyles,
  };
}

/** Standard button style with variant support. */
export function buttonStyle(variant: 'primary' | 'secondary' | 'danger', disabled = false): React.CSSProperties {
  const base: React.CSSProperties = {
    padding: '8px 16px',
    borderRadius: BORDER_RADIUS,
    fontSize: '13px',
    fontFamily: FONT_FAMILY,
    fontWeight: 500,
    cursor: disabled ? 'not-allowed' : 'pointer',
    opacity: disabled ? 0.6 : 1,
    transition: 'opacity 0.15s ease',
    border: 'none',
  };

  if (variant === 'primary') {
    return { ...base, backgroundColor: BRAND_PRIMARY, color: COLOR_WHITE };
  }
  if (variant === 'danger') {
    return { ...base, backgroundColor: COLOR_DANGER, color: COLOR_WHITE };
  }
  return {
    ...base,
    backgroundColor: COLOR_WHITE,
    color: COLOR_TEXT,
    border: `1px solid ${COLOR_BORDER}`,
  };
}
