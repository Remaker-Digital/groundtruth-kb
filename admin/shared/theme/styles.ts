/**
 * Agent Red Design Tokens — TypeScript Constants & Style Factories
 *
 * Layer 2 of the three-layer design system:
 *   Layer 1: tokens.css — CSS custom properties (hover, overrides, utility classes)
 *   Layer 2: THIS FILE — typed constants for React.CSSProperties consumers + shared style factories
 *   Layer 3: agentRedTheme.ts — Mantine theme props
 *
 * All values here are the canonical hex/rgba strings.
 * They MUST match the CSS custom properties in tokens.css and the Mantine theme in agentRedTheme.ts.
 *
 * Usage:
 *   import { tokens, dialog, card, button, text } from '../theme/styles';
 *   <div style={{ background: tokens.surface, color: tokens.textPrimary }}>
 *   <div style={dialog.overlay}>
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import type React from 'react';

// ===========================================================================
// 1. Design Tokens (canonical values)
// ===========================================================================

export const tokens = {
  // --- Stone neutral surface hierarchy (resolved via CSS custom properties) ---
  chrome:  'var(--ar-chrome)',
  page:    'var(--ar-page)',
  surface: 'var(--ar-surface)',
  border:  'var(--ar-border)',

  // --- Text hierarchy (resolved via CSS custom properties) ---
  textPrimary:   'var(--ar-text-primary)',
  textSecondary: 'var(--ar-text-secondary)',
  textMuted:     'var(--ar-text-muted)',
  textTertiary:  'var(--ar-text-tertiary)',

  // --- Action colors ---
  action:        '#3B82F6',
  actionHover:   '#2563EB',
  activate:      '#2b8a3e',
  activateHover: '#237032',
  danger:        '#D32F2F',
  dangerHover:   '#B71C1C',
  brand:         '#ff3621',

  // --- Semantic status ---
  success: '#0D7C3E',
  warning: '#E5A100',
  error:      '#D32F2F',
  errorLight: '#ff6b6b',
  info:       '#1E3A5F',

  // --- Chart / data visualization ---
  chartGrid:    '#44403c',
  chartAxis:    '#787878',
  chartLine1:   '#4c6ef5',   // indigo — P50, professional tier
  chartLine2:   '#E5A100',   // amber — P95
  chartLine3:   '#D32F2F',   // red — P99
  chartLine4:   '#787878',   // gray — volume / misc
  chartPurple:  '#7950f2',   // enterprise tier
  chartViolet:  '#7C3AED',   // Stripe accent
  chartBlue:    '#1E88E5',   // API key accent

  // --- White (for button text on colored backgrounds) ---
  white: '#FFFFFF',

  // --- Overlay / modal (resolved via CSS custom properties) ---
  overlayBg:  'var(--ar-overlay-bg)',
  modalShadow: 'var(--ar-modal-shadow)',

  // --- Transition ---
  transitionFast: '150ms ease',
} as const;

// ===========================================================================
// 1b. Recharts Style Helpers
// ===========================================================================

/** Reusable Recharts axis tick props */
export const chartAxisTick = { fill: tokens.chartAxis, fontSize: 11 } as const;

/** Reusable Recharts Tooltip contentStyle */
export const chartTooltipStyle = {
  backgroundColor: tokens.surface,
  border: `1px solid ${tokens.border}`,
  color: tokens.textSecondary,
} as const;

/** Reusable Recharts Tooltip labelStyle */
export const chartLabelStyle = { color: tokens.textMuted } as const;


// ===========================================================================
// 2. Shared Style Factories
// ===========================================================================

// ---------------------------------------------------------------------------
// 2a-pre. Modal/input style helpers — shared across Provider Console modals
// ---------------------------------------------------------------------------

/** Mantine Modal styles prop for dark-themed modals */
export const modalStyles = {
  content: { backgroundColor: tokens.surface },
  header: { backgroundColor: tokens.surface },
} as const;

/** Mantine input styles for dark-themed modal inputs */
export const modalInputStyles = {
  input: {
    backgroundColor: tokens.page,
    borderColor: tokens.border,
    color: tokens.textPrimary,
  },
} as const;

// ---------------------------------------------------------------------------
// 2a. Dialog styles — shared across ConfirmDialog, RestoreDialog, ActivationDialog
// ---------------------------------------------------------------------------

export const dialog = {
  overlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: tokens.overlayBg,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 10000,
  } as React.CSSProperties,

  /** Base panel — callers should spread and override maxWidth as needed. */
  panel: (maxWidth: number = 440): React.CSSProperties => ({
    background: tokens.surface,
    borderRadius: 12,
    padding: 24,
    width: maxWidth,
    maxWidth: '90vw',
    boxShadow: tokens.modalShadow,
    border: `1px solid ${tokens.border}`,
  }),

  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingBottom: 12,
    borderBottom: `1px solid ${tokens.border}`,
    marginBottom: 16,
  } as React.CSSProperties,

  title: {
    fontSize: 16,
    fontWeight: 600,
    color: tokens.textPrimary,
    margin: 0,
  } as React.CSSProperties,

  closeButton: {
    background: 'none',
    border: 'none',
    color: tokens.textTertiary,
    cursor: 'pointer',
    fontSize: 20,
    padding: 4,
  } as React.CSSProperties,

  body: {
    padding: '0',
  } as React.CSSProperties,

  /** Scrollable body variant (ActivationDialog) */
  bodyScrollable: {
    padding: '0',
    overflowY: 'auto',
    flex: 1,
  } as React.CSSProperties,

  message: {
    fontSize: 14,
    lineHeight: 1.6,
    color: tokens.textMuted,
    margin: '0 0 16px 0',
  } as React.CSSProperties,

  footer: {
    display: 'flex',
    justifyContent: 'flex-end',
    gap: 8,
    paddingTop: 16,
    borderTop: `1px solid ${tokens.border}`,
    marginTop: 16,
  } as React.CSSProperties,

  cancelButton: {
    padding: '8px 16px',
    fontSize: 14,
    fontWeight: 500,
    background: 'transparent',
    color: tokens.textMuted,
    border: `1px solid ${tokens.border}`,
    borderRadius: 6,
    cursor: 'pointer',
    transition: `background ${tokens.transitionFast}`,
  } as React.CSSProperties,

  /** Warning box (RestoreDialog, ActivationDialog) */
  warningBox: {
    background: 'rgba(255, 170, 0, 0.08)',
    border: '1px solid rgba(255, 170, 0, 0.2)',
    borderRadius: 8,
    padding: 12,
    marginBottom: 16,
  } as React.CSSProperties,

  warningText: {
    fontSize: 13,
    lineHeight: 1.5,
    color: tokens.textPrimary,
  } as React.CSSProperties,

  /** Error section (ActivationDialog) */
  errorSection: {
    background: 'rgba(255, 68, 68, 0.08)',
    borderRadius: 8,
    padding: 12,
    marginBottom: 12,
  } as React.CSSProperties,

  errorText: {
    fontSize: 13,
    color: '#ff6666',
  } as React.CSSProperties,

  /** Warning section title */
  warningSectionTitle: {
    fontSize: 13,
    fontWeight: 600,
    color: '#ffaa00',
    marginBottom: 6,
  } as React.CSSProperties,

  /** Error section title */
  errorSectionTitle: {
    fontSize: 13,
    fontWeight: 600,
    color: '#ff4444',
    marginBottom: 6,
  } as React.CSSProperties,
} as const;


// ---------------------------------------------------------------------------
// 2b. Card styles — shared across dashboard cards, settings panels
// ---------------------------------------------------------------------------

export const card = {
  /** Standard card container */
  container: {
    background: tokens.surface,
    border: `1px solid ${tokens.border}`,
    borderRadius: 12,
    padding: 20,
  } as React.CSSProperties,

  /** Card with no padding (for table-containing cards) */
  flush: {
    background: tokens.surface,
    border: `1px solid ${tokens.border}`,
    borderRadius: 12,
    overflow: 'hidden',
  } as React.CSSProperties,

  /** Section title inside a card */
  sectionTitle: {
    fontSize: 13,
    fontWeight: 600,
    color: tokens.textMuted,
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
    marginBottom: 12,
  } as React.CSSProperties,

  /** Stat value (large number) */
  statValue: {
    fontSize: 28,
    fontWeight: 700,
    color: tokens.textPrimary,
    lineHeight: 1,
  } as React.CSSProperties,

  /** Stat label */
  statLabel: {
    fontSize: 13,
    color: tokens.textMuted,
    marginTop: 4,
  } as React.CSSProperties,
} as const;


// ---------------------------------------------------------------------------
// 2c. Button styles — shared action, activate, danger, cancel patterns
// ---------------------------------------------------------------------------

export const button = {
  /** Base button properties (shared sizing) */
  base: {
    fontSize: 14,
    fontWeight: 600,
    borderRadius: 6,
    cursor: 'pointer',
    transition: `background ${tokens.transitionFast}`,
    whiteSpace: 'nowrap',
  } as React.CSSProperties,

  /** Action (blue) — affirmative: Save, Add, Create, Purchase, Subscribe */
  action: {
    padding: '8px 20px',
    fontSize: 14,
    fontWeight: 600,
    background: tokens.action,
    color: tokens.white,
    border: 'none',
    borderRadius: 6,
    cursor: 'pointer',
    transition: `background ${tokens.transitionFast}`,
    whiteSpace: 'nowrap',
  } as React.CSSProperties,

  /** Activate (green) — Activate, Enable */
  activate: {
    padding: '8px 20px',
    fontSize: 14,
    fontWeight: 600,
    background: tokens.activate,
    color: tokens.white,
    border: 'none',
    borderRadius: 6,
    cursor: 'pointer',
    transition: `background ${tokens.transitionFast}`,
    whiteSpace: 'nowrap',
  } as React.CSSProperties,

  /** Danger (red) — Delete, Deactivate, Disconnect */
  danger: {
    padding: '8px 16px',
    fontSize: 14,
    fontWeight: 600,
    background: tokens.danger,
    color: tokens.white,
    border: 'none',
    borderRadius: 6,
    cursor: 'pointer',
  } as React.CSSProperties,

  /** Cancel / ghost button */
  cancel: {
    padding: '8px 16px',
    fontSize: 14,
    fontWeight: 500,
    background: 'transparent',
    color: tokens.textMuted,
    border: `1px solid ${tokens.border}`,
    borderRadius: 6,
    cursor: 'pointer',
  } as React.CSSProperties,

  /** Disabled modifier — spread onto any button style */
  disabled: {
    opacity: 0.5,
    cursor: 'not-allowed',
  } as React.CSSProperties,

  /** Small variant */
  sm: {
    padding: '6px 12px',
    fontSize: 13,
  } as React.CSSProperties,
} as const;


// ---------------------------------------------------------------------------
// 2d. Text styles — common typography patterns
// ---------------------------------------------------------------------------

export const text = {
  /** Page title (h1-equivalent) */
  pageTitle: {
    fontSize: 20,
    fontWeight: 700,
    color: tokens.textPrimary,
    margin: '0 0 4px 0',
  } as React.CSSProperties,

  /** Section heading */
  sectionHeading: {
    fontSize: 15,
    fontWeight: 600,
    color: tokens.textPrimary,
    margin: '0 0 12px 0',
  } as React.CSSProperties,

  /** Body text */
  body: {
    fontSize: 14,
    color: tokens.textPrimary,
    lineHeight: 1.5,
  } as React.CSSProperties,

  /** Muted / secondary text */
  muted: {
    fontSize: 13,
    color: tokens.textMuted,
  } as React.CSSProperties,

  /** Tertiary / subtle text */
  tertiary: {
    fontSize: 13,
    color: tokens.textTertiary,
  } as React.CSSProperties,

  /** Label (form fields, table headers) */
  label: {
    fontSize: 12,
    fontWeight: 600,
    color: tokens.textMuted,
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
  } as React.CSSProperties,

  /** Monospace (code, IDs) */
  mono: {
    fontFamily: "'JetBrains Mono', ui-monospace, monospace",
    fontSize: 13,
  } as React.CSSProperties,
} as const;


// ---------------------------------------------------------------------------
// 2e. Layout utilities
// ---------------------------------------------------------------------------

export const layout = {
  /** Full-page centered loading / empty state */
  centered: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 48,
    color: tokens.textMuted,
    fontSize: 14,
  } as React.CSSProperties,

  /** Max-width content container */
  container: (maxWidth: number = 960): React.CSSProperties => ({
    maxWidth,
    margin: '0 auto',
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
  }),

  /** Section divider */
  divider: {
    borderTop: `1px solid ${tokens.border}`,
    margin: '16px 0',
  } as React.CSSProperties,
} as const;
