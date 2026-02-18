/**
 * TeamManager styles — theme-aware style factory.
 *
 * Extracted from TeamManager.tsx. Produces a complete style map from a
 * ThemePalette + dark flag, consumed by all team sub-components.
 *
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import type React from 'react';
import type { ThemePalette, TeamStyles } from './types';
import { getRoleColors } from './constants';

// ---------------------------------------------------------------------------
// Style factory
// ---------------------------------------------------------------------------

export function makeStyles(p: ThemePalette, dark: boolean = false): TeamStyles {
  const ROLE_COLORS = getRoleColors(dark);
  return {
    container: {
      fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      maxWidth: 960,
      margin: '0 auto',
    } as React.CSSProperties,

    // Table
    table: {
      width: '100%',
      borderCollapse: 'collapse' as const,
    } as React.CSSProperties,

    th: {
      textAlign: 'left' as const,
      fontSize: 12,
      fontWeight: 600,
      color: p.textSecondary,
      textTransform: 'uppercase' as const,
      letterSpacing: '0.05em',
      padding: '8px 12px',
      borderBottom: `2px solid ${p.border}`,
    } as React.CSSProperties,

    td: {
      padding: '12px',
      borderBottom: `1px solid ${p.borderSubtle}`,
      fontSize: 14,
      color: p.textPrimary,
      verticalAlign: 'middle' as const,
    } as React.CSSProperties,

    tr: (isDisabled: boolean): React.CSSProperties => ({
      opacity: isDisabled ? 0.55 : 1,
    }),

    // Member info
    memberInfo: {
      display: 'flex',
      flexDirection: 'column' as const,
      gap: 2,
    } as React.CSSProperties,

    memberName: {
      fontSize: 14,
      fontWeight: 600,
      color: p.textPrimary,
    } as React.CSSProperties,

    memberEmail: {
      fontSize: 13,
      color: p.textSecondary,
    } as React.CSSProperties,

    // Badges
    roleBadge: (role: string): React.CSSProperties => ({
      display: 'inline-block',
      padding: '2px 10px',
      borderRadius: 12,
      fontSize: 12,
      fontWeight: 600,
      background: (ROLE_COLORS[role] || ROLE_COLORS.viewer).bg,
      color: (ROLE_COLORS[role] || ROLE_COLORS.viewer).text,
    }),

    statusDot: (_color: string): React.CSSProperties => ({
      display: 'inline-flex',
      alignItems: 'center',
      gap: 6,
      fontSize: 13,
      color: p.textTertiary,
    }),

    dot: (color: string): React.CSSProperties => ({
      width: 8,
      height: 8,
      borderRadius: '50%',
      background: color,
      flexShrink: 0,
    }),

    // Dates
    dateText: {
      fontSize: 13,
      color: p.textSecondary,
    } as React.CSSProperties,

    // Actions
    actionRow: {
      display: 'flex',
      gap: 6,
    } as React.CSSProperties,

    iconButton: {
      display: 'inline-flex',
      alignItems: 'center',
      justifyContent: 'center',
      width: 28,
      height: 28,
      borderRadius: 6,
      border: `1px solid ${dark ? 'rgba(255,255,255,0.12)' : p.border}`,
      background: dark ? 'rgba(255,255,255,0.06)' : p.hoverBg,
      color: p.textSecondary,
      cursor: 'pointer',
      outline: 'none',
      transition: 'all 0.15s ease',
    } as React.CSSProperties,

    // Invite form
    formRow: {
      display: 'flex',
      gap: 12,
      alignItems: 'flex-end',
      flexWrap: 'wrap' as const,
    } as React.CSSProperties,

    formField: {
      display: 'flex',
      flexDirection: 'column' as const,
      gap: 4,
      flex: 1,
      minWidth: 180,
    } as React.CSSProperties,

    formLabel: {
      fontSize: 13,
      fontWeight: 600,
      color: p.textTertiary,
    } as React.CSSProperties,

    input: {
      padding: '8px 12px',
      fontSize: 14,
      border: `1px solid ${p.inputBorder}`,
      borderRadius: 6,
      color: p.textPrimary,
      background: p.inputBg,
      outline: 'none',
      boxSizing: 'border-box' as const,
      width: '100%',
    } as React.CSSProperties,

    select: {
      padding: '8px 12px',
      fontSize: 14,
      border: `1px solid ${p.inputBorder}`,
      borderRadius: 6,
      color: p.textPrimary,
      background: p.inputBg,
      outline: 'none',
      boxSizing: 'border-box' as const,
      width: '100%',
      cursor: 'pointer',
    } as React.CSSProperties,

    inviteButton: {
      padding: '8px 20px',
      fontSize: 14,
      fontWeight: 600,
      background: '#ff3621',
      color: '#FFFFFF',
      border: 'none',
      borderRadius: 6,
      cursor: 'pointer',
      whiteSpace: 'nowrap' as const,
      height: 38,
    } as React.CSSProperties,

    inviteButtonDisabled: {
      opacity: 0.5,
      cursor: 'not-allowed',
    } as React.CSSProperties,

    // Confirmation modal
    overlay: {
      position: 'fixed' as const,
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: p.overlayBg,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 10000,
    } as React.CSSProperties,

    modal: {
      background: p.modalBg,
      borderRadius: 12,
      padding: 24,
      width: 420,
      maxWidth: '90vw',
      boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
      border: `1px solid ${p.border}`,
    } as React.CSSProperties,

    modalTitle: {
      fontSize: 16,
      fontWeight: 600,
      color: p.textPrimary,
      margin: '0 0 8px 0',
    } as React.CSSProperties,

    modalBody: {
      fontSize: 14,
      color: p.textTertiary,
      lineHeight: 1.5,
      margin: '0 0 20px 0',
    } as React.CSSProperties,

    modalActions: {
      display: 'flex',
      justifyContent: 'flex-end',
      gap: 8,
    } as React.CSSProperties,

    modalCancel: {
      padding: '8px 16px',
      fontSize: 14,
      fontWeight: 500,
      background: p.hoverBg,
      color: p.textTertiary,
      border: `1px solid ${p.border}`,
      borderRadius: 6,
      cursor: 'pointer',
    } as React.CSSProperties,

    modalConfirm: {
      padding: '8px 16px',
      fontSize: 14,
      fontWeight: 600,
      background: '#DC2626',
      color: '#FFFFFF',
      border: 'none',
      borderRadius: 6,
      cursor: 'pointer',
    } as React.CSSProperties,

    // Edit modal
    editModal: {
      background: p.modalBg,
      borderRadius: 12,
      padding: 24,
      width: 460,
      maxWidth: '90vw',
      boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
      border: `1px solid ${p.border}`,
    } as React.CSSProperties,

    editSaveButton: {
      padding: '8px 20px',
      fontSize: 14,
      fontWeight: 600,
      background: '#ff3621',
      color: '#FFFFFF',
      border: 'none',
      borderRadius: 6,
      cursor: 'pointer',
    } as React.CSSProperties,

    // Empty & loading
    loadingContainer: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: 48,
      color: p.textSecondary,
      fontSize: 14,
    } as React.CSSProperties,

    errorContainer: {
      padding: 24,
      background: dark ? '#371520' : '#FEF2F2',
      border: `1px solid ${dark ? '#5C2030' : '#FECACA'}`,
      borderRadius: 8,
      color: dark ? '#FCA5A5' : '#991B1B',
      fontSize: 14,
      textAlign: 'center' as const,
    } as React.CSSProperties,

    retryButton: {
      marginTop: 12,
      padding: '6px 16px',
      background: dark ? '#B91C1C' : '#DC2626',
      color: '#FFFFFF',
      border: 'none',
      borderRadius: 4,
      fontSize: 13,
      fontWeight: 600,
      cursor: 'pointer',
    } as React.CSSProperties,

    emptyState: {
      padding: 48,
      textAlign: 'center' as const,
      color: p.textSecondary,
      fontSize: 14,
    } as React.CSSProperties,
  };
}
