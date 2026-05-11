// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * TeamManager constants — role definitions, color palettes, status display.
 *
 * Extracted from TeamManager.tsx to reduce monolith size. These constants are
 * consumed by sub-components (InviteForm, TeamMemberRow, RoleTooltip, etc.).
 *
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import type { ThemePalette, RoleDef } from './types';
import type { TeamRole } from '../types';
import { tokens } from '../theme/styles';

// ---------------------------------------------------------------------------
// Role definitions
// ---------------------------------------------------------------------------

export const ROLES: RoleDef[] = [
  { value: 'superadmin', label: 'Superadmin', description: 'Full access — hidden safety-net account, auto-provisioned' },
  { value: 'admin', label: 'Admin', description: 'Configuration, team management, and analytics access' },
  { value: 'escalation_agent', label: 'Escalation agent', description: 'Read-only Inbox access for handling escalated conversations' },
  { value: 'viewer', label: 'Viewer', description: 'Read-only access to analytics and conversations' },
];

export const INVITABLE_ROLES = ROLES.filter((r) => r.value !== 'superadmin');

// ---------------------------------------------------------------------------
// Role badge colors
// ---------------------------------------------------------------------------

export const ROLE_COLORS_LIGHT: Record<string, { bg: string; text: string }> = {
  superadmin: { bg: '#FEF2F2', text: '#991B1B' },
  admin: { bg: '#EDE9FE', text: '#5B21B6' },
  escalation_agent: { bg: '#DBEAFE', text: '#1E40AF' },
  viewer: { bg: '#F3F4F6', text: '#374151' },
};

export const ROLE_COLORS_DARK: Record<string, { bg: string; text: string }> = {
  superadmin: { bg: '#371520', text: '#FCA5A5' },
  admin: { bg: '#2E1065', text: '#C4B5FD' },
  escalation_agent: { bg: '#1E2A47', text: '#93C5FD' },
  viewer: { bg: tokens.border, text: tokens.textMuted },
};

export function getRoleColors(isDark: boolean): Record<string, { bg: string; text: string }> {
  return isDark ? ROLE_COLORS_DARK : ROLE_COLORS_LIGHT;
}

// ---------------------------------------------------------------------------
// Status display
// ---------------------------------------------------------------------------

export const STATUS_DISPLAY: Record<string, { label: string; color: string }> = {
  active: { label: 'Active', color: '#059669' },
  invited: { label: 'Invited', color: '#D97706' },
  disabled: { label: 'Disabled', color: '#9CA3AF' },
};

// ---------------------------------------------------------------------------
// Theme palettes
// ---------------------------------------------------------------------------

export const LIGHT_PALETTE: ThemePalette = {
  surface: '#FFFFFF',
  border: '#E5E7EB',
  borderSubtle: '#F3F4F6',
  textPrimary: '#111827',
  textSecondary: '#6B7280',
  textTertiary: '#374151',
  inputBg: '#FFFFFF',
  inputBorder: '#D1D5DB',
  hoverBg: '#F9FAFB',
  modalBg: '#FFFFFF',
  overlayBg: 'rgba(0,0,0,0.4)',
};

export const DARK_PALETTE: ThemePalette = {
  surface: tokens.surface,
  border: tokens.border,
  borderSubtle: '#3a3633',
  textPrimary: tokens.textSecondary,  // palette textPrimary = Stone 1 (#f5f5f4) = tokens.textSecondary
  textSecondary: tokens.textMuted,    // palette textSecondary = Stone 4 (#a8a29e) = tokens.textMuted
  textTertiary: '#d6d3d1',            // Stone 3 — not in token system
  inputBg: tokens.page,
  inputBorder: tokens.textTertiary,   // #57534e
  hoverBg: tokens.border,
  modalBg: tokens.surface,
  overlayBg: tokens.overlayBg,
};

export function getPalette(isDark: boolean): ThemePalette {
  return isDark ? DARK_PALETTE : LIGHT_PALETTE;
}

// ---------------------------------------------------------------------------
// Lookup helper — find a role label by value
// ---------------------------------------------------------------------------

export function getRoleLabel(role: TeamRole | string): string {
  return (ROLES.find((r) => r.value === role) || ROLES[3]).label;
}
