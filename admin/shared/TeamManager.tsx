/**
 * TeamManager — Team member management component for the admin dashboard.
 *
 * Displays a list of team members with role badges and status indicators,
 * provides an invite form for adding new members, supports inline editing
 * of role and active status, and handles member removal with confirmation.
 *
 * Props:
 *   - BaseComponentProps (tenantContext, apiFetch, onNotify, onNavigate)
 *
 * Data hooks:
 *   - useTeamMembers: fetches the team member list from GET /api/admin/team
 *   - useInviteTeamMember: invites a new member via POST /api/admin/team
 *
 * API endpoints consumed:
 *   - GET    /api/admin/team              (list)
 *   - POST   /api/admin/team              (invite)
 *   - PUT    /api/admin/team/{member_id}  (update)
 *   - DELETE /api/admin/team/{member_id}  (deactivate)
 *
 * Architecture references:
 *   - admin_team_api.py: WI #179 — Team Member CRUD
 *   - UI-UX-ARCHITECTURE-DECISIONS.md section 7: TeamManager spec
 *
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useState, useCallback, useEffect } from 'react';
import type { BaseComponentProps, TeamMember, TeamRole } from './types';
import { ESCALATION_CATEGORIES } from './types';
import { useTeamMembers, useInviteTeamMember } from './hooks';
import { HelpTooltip } from './HelpTooltip';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const ROLES: Array<{ value: TeamRole; label: string; description: string }> = [
  { value: 'superadmin', label: 'Superadmin', description: 'Full access — hidden safety-net account, auto-provisioned' },
  { value: 'admin', label: 'Admin', description: 'Configuration, team management, and analytics access' },
  { value: 'escalation_agent', label: 'Escalation agent', description: 'Read-only Inbox access for handling escalated conversations' },
  { value: 'viewer', label: 'Viewer', description: 'Read-only access to analytics and conversations' },
];

const INVITABLE_ROLES = ROLES.filter((r) => r.value !== 'superadmin');

const ROLE_COLORS_LIGHT: Record<string, { bg: string; text: string }> = {
  superadmin: { bg: '#FEF2F2', text: '#991B1B' },
  admin: { bg: '#EDE9FE', text: '#5B21B6' },
  escalation_agent: { bg: '#DBEAFE', text: '#1E40AF' },
  viewer: { bg: '#F3F4F6', text: '#374151' },
};

const ROLE_COLORS_DARK: Record<string, { bg: string; text: string }> = {
  superadmin: { bg: '#371520', text: '#FCA5A5' },
  admin: { bg: '#2E1065', text: '#C4B5FD' },
  escalation_agent: { bg: '#1E2A47', text: '#93C5FD' },
  viewer: { bg: '#272727', text: '#A0A0A0' },
};

function getRoleColors(isDark: boolean): Record<string, { bg: string; text: string }> {
  return isDark ? ROLE_COLORS_DARK : ROLE_COLORS_LIGHT;
}

const STATUS_DISPLAY: Record<string, { label: string; color: string }> = {
  active: { label: 'Active', color: '#059669' },
  invited: { label: 'Invited', color: '#D97706' },
  disabled: { label: 'Disabled', color: '#9CA3AF' },
};

// ---------------------------------------------------------------------------
// Dark mode detection hook — reads Mantine's data-mantine-color-scheme attribute
// ---------------------------------------------------------------------------

function useIsDark(): boolean {
  const [isDark, setIsDark] = useState(() => {
    if (typeof document === 'undefined') return false;
    return document.documentElement.getAttribute('data-mantine-color-scheme') === 'dark';
  });

  useEffect(() => {
    const observer = new MutationObserver(() => {
      setIsDark(document.documentElement.getAttribute('data-mantine-color-scheme') === 'dark');
    });
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['data-mantine-color-scheme'] });
    return () => observer.disconnect();
  }, []);

  return isDark;
}

// ---------------------------------------------------------------------------
// Theme-aware palette
// ---------------------------------------------------------------------------

interface ThemePalette {
  surface: string;       // card / container background
  border: string;        // borders
  borderSubtle: string;  // subtle row separators
  textPrimary: string;   // primary text
  textSecondary: string; // secondary / muted text
  textTertiary: string;  // labels, column headers
  inputBg: string;       // form inputs
  inputBorder: string;   // form input borders
  hoverBg: string;       // hover backgrounds
  modalBg: string;       // modal background
  overlayBg: string;     // modal overlay
}

const LIGHT_PALETTE: ThemePalette = {
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

const DARK_PALETTE: ThemePalette = {
  surface: '#1f1f1f',
  border: '#272727',
  borderSubtle: '#2a2a2a',
  textPrimary: '#E0E0E0',
  textSecondary: '#A0A0A0',
  textTertiary: '#B0B0B0',
  inputBg: '#141414',
  inputBorder: '#383838',
  hoverBg: '#272727',
  modalBg: '#1f1f1f',
  overlayBg: 'rgba(0,0,0,0.6)',
};

// ---------------------------------------------------------------------------
// Styles (theme-aware factory)
// ---------------------------------------------------------------------------

function makeStyles(p: ThemePalette, dark: boolean = false) {
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

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr) return '--';
  try {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  } catch {
    return dateStr;
  }
}

function formatRelativeDate(dateStr: string | null | undefined): string {
  if (!dateStr) return 'Never';
  try {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return formatDate(dateStr);
  } catch {
    return dateStr || 'Never';
  }
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export const TeamManager: React.FC<BaseComponentProps> = ({
  tenantContext,
  apiFetch,
  onNotify,
}) => {
  // Theme
  const isDark = useIsDark();
  const palette = isDark ? DARK_PALETTE : LIGHT_PALETTE;
  const roleColors = getRoleColors(isDark);
  const s = makeStyles(palette, isDark);

  // State
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteName, setInviteName] = useState('');
  const [inviteRole, setInviteRole] = useState<TeamRole>('escalation_agent');
  const [showInviteForm, setShowInviteForm] = useState(false);
  const [roleTooltipOpen, setRoleTooltipOpen] = useState(false);

  // Confirmation dialog
  const [confirmMember, setConfirmMember] = useState<TeamMember | null>(null);
  const [confirmAction, setConfirmAction] = useState<'remove' | 'disable' | null>(null);
  const [actionLoading, setActionLoading] = useState(false);

  // Edit dialog
  const [editMember, setEditMember] = useState<TeamMember | null>(null);
  const [editRole, setEditRole] = useState<TeamRole>('escalation_agent');
  const [editCategories, setEditCategories] = useState<string[]>([]);
  const [editLoading, setEditLoading] = useState(false);

  // Data hooks
  const team = useTeamMembers(apiFetch);
  const { invite, loading: inviting, error: inviteError } = useInviteTeamMember(apiFetch);

  const members: TeamMember[] = team.data?.members ?? [];
  const totalCount = members.length;

  // -------------------------------------------------------------------------
  // Invite handler
  // -------------------------------------------------------------------------

  const handleInvite = useCallback(async () => {
    if (!inviteEmail.trim()) {
      onNotify('Please enter an email address.', 'warning');
      return;
    }

    // Basic email validation
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(inviteEmail.trim())) {
      onNotify('Please enter a valid email address.', 'warning');
      return;
    }

    const result = await invite(inviteEmail.trim(), inviteRole, inviteName.trim() || undefined);
    if (result) {
      onNotify(`Invited ${inviteEmail.trim()} as ${inviteRole}.`, 'success');
      setInviteEmail('');
      setInviteName('');
      setInviteRole('escalation_agent');
      setShowInviteForm(false);
      team.refetch();
    } else {
      onNotify(inviteError || 'Failed to invite team member.', 'error');
    }
  }, [inviteEmail, inviteName, inviteRole, invite, inviteError, onNotify, team]);

  // -------------------------------------------------------------------------
  // Edit handler
  // -------------------------------------------------------------------------

  const openEdit = useCallback((member: TeamMember) => {
    setEditMember(member);
    setEditRole(member.role as TeamRole);
    setEditCategories(member.escalationCategories || []);
  }, []);

  const handleSaveEdit = useCallback(async () => {
    if (!editMember) return;
    setEditLoading(true);

    try {
      const body: Record<string, unknown> = {};
      if (editRole !== editMember.role) body.role = editRole;
      // Include categories if role is agent and categories changed (WI #279)
      const origCats = editMember.escalationCategories || [];
      const catsChanged = editRole === 'escalation_agent' && (
        editCategories.length !== origCats.length ||
        editCategories.some((c) => !origCats.includes(c))
      );
      if (catsChanged) body.escalation_categories = editCategories;

      if (Object.keys(body).length === 0) {
        setEditMember(null);
        return;
      }

      const resp = await apiFetch(`/api/admin/team/${editMember.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      if (!resp.ok) {
        const errText = await resp.text().catch(() => '');
        throw new Error(`${resp.status}: ${errText}`);
      }

      onNotify(`Updated ${editMember.email} successfully.`, 'success');
      setEditMember(null);
      team.refetch();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Update failed';
      onNotify(`Failed to update member: ${msg}`, 'error');
    } finally {
      setEditLoading(false);
    }
  }, [editMember, editRole, editCategories, apiFetch, onNotify, team]);

  // -------------------------------------------------------------------------
  // Remove / disable handler
  // -------------------------------------------------------------------------

  const handleConfirmAction = useCallback(async () => {
    if (!confirmMember || !confirmAction) return;
    setActionLoading(true);

    try {
      const resp = await apiFetch(`/api/admin/team/${confirmMember.id}`, {
        method: 'DELETE',
      });

      if (!resp.ok) {
        const errText = await resp.text().catch(() => '');
        throw new Error(`${resp.status}: ${errText}`);
      }

      onNotify(`Removed ${confirmMember.email} from the team.`, 'success');
      setConfirmMember(null);
      setConfirmAction(null);
      team.refetch();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Removal failed';
      onNotify(`Failed to remove member: ${msg}`, 'error');
    } finally {
      setActionLoading(false);
    }
  }, [confirmMember, confirmAction, apiFetch, onNotify, team]);

  // -------------------------------------------------------------------------
  // Inline role change (WI #275)
  // -------------------------------------------------------------------------

  const handleInlineRoleChange = useCallback(async (member: TeamMember, newRole: TeamRole) => {
    if (newRole === member.role) return;
    try {
      const resp = await apiFetch(`/api/admin/team/${member.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ role: newRole }),
      });
      if (!resp.ok) throw new Error(`${resp.status}`);
      onNotify(`Changed ${member.email} role to ${(ROLES.find((r) => r.value === newRole) || ROLES[3]).label}.`, 'success');
      team.refetch();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Role update failed';
      onNotify(`Failed to update role: ${msg}`, 'error');
    }
  }, [apiFetch, onNotify, team]);

  // -------------------------------------------------------------------------
  // Inline escalation category toggle (WI #279)
  // -------------------------------------------------------------------------

  const handleCategoryToggle = useCallback(async (member: TeamMember, categoryId: string) => {
    const current = member.escalationCategories || [];
    const next = current.includes(categoryId)
      ? current.filter((c) => c !== categoryId)
      : [...current, categoryId];
    try {
      const resp = await apiFetch(`/api/admin/team/${member.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ escalation_categories: next }),
      });
      if (!resp.ok) throw new Error(`${resp.status}`);
      team.refetch();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Category update failed';
      onNotify(`Failed to update categories: ${msg}`, 'error');
    }
  }, [apiFetch, onNotify, team]);

  // -------------------------------------------------------------------------
  // Loading state
  // -------------------------------------------------------------------------

  if (team.loading && !team.data) {
    return (
      <div style={s.container}>
        <div style={s.loadingContainer}>Loading team members...</div>
      </div>
    );
  }

  // -------------------------------------------------------------------------
  // Error state
  // -------------------------------------------------------------------------

  if (team.error && !team.data) {
    return (
      <div style={s.container}>
        <div style={s.errorContainer}>
          <div>Failed to load team: {team.error}</div>
          <button style={s.retryButton} onClick={team.refetch}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  // -------------------------------------------------------------------------
  // Role tooltip content — shown on hover of the "Role" column header
  // -------------------------------------------------------------------------

  const roleTooltipContent = (
    <div
      style={{
        position: 'absolute',
        top: '100%',
        left: '50%',
        transform: 'translateX(-50%)',
        marginTop: 8,
        background: '#1f2937',
        color: '#f9fafb',
        fontSize: 12,
        lineHeight: 1.5,
        padding: '12px 16px',
        borderRadius: 8,
        width: 340,
        maxWidth: 380,
        zIndex: 9999,
        boxShadow: '0 4px 16px rgba(0,0,0,0.3)',
        pointerEvents: 'auto' as const,
      }}
      onMouseEnter={() => setRoleTooltipOpen(true)}
      onMouseLeave={() => setRoleTooltipOpen(false)}
    >
      {/* Arrow pointing up */}
      <span style={{
        position: 'absolute',
        bottom: '100%',
        left: '50%',
        transform: 'translateX(-50%)',
        width: 0,
        height: 0,
        borderLeft: '6px solid transparent',
        borderRight: '6px solid transparent',
        borderBottom: '6px solid #1f2937',
      }} />
      <div style={{ fontWeight: 600, fontSize: 13, marginBottom: 10 }}>Role permissions</div>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <tbody>
          {ROLES.map((role) => (
            <tr key={role.value}>
              <td style={{ padding: '6px 12px 6px 0', verticalAlign: 'top', whiteSpace: 'nowrap' }}>
                <span style={{
                  display: 'inline-block',
                  padding: '1px 8px',
                  borderRadius: 10,
                  fontSize: 11,
                  fontWeight: 600,
                  background: (roleColors[role.value] || roleColors.viewer).bg,
                  color: (roleColors[role.value] || roleColors.viewer).text,
                }}>
                  {role.label}
                </span>
              </td>
              <td style={{
                padding: '6px 0',
                fontSize: 11,
                color: '#d1d5db',
                verticalAlign: 'top',
                textTransform: 'none',
                letterSpacing: 'normal',
                fontWeight: 400,
              }}>
                {role.description}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );

  // -------------------------------------------------------------------------
  // Render — flat layout: header row + table + invite form
  // -------------------------------------------------------------------------

  return (
    <div style={s.container}>
      {/* Single container box for all team content */}
      <div style={{
        background: palette.surface,
        border: `1px solid ${palette.border}`,
        borderRadius: 8,
        padding: 24,
      }}>
      {/* Header row with member count + invite button */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 16,
      }}>
        <p style={{
          fontSize: 13,
          color: palette.textSecondary,
          margin: 0,
          lineHeight: 1.5,
        }}>
          {totalCount} team member{totalCount !== 1 ? 's' : ''}
        </p>
        <button
          style={s.inviteButton}
          onClick={() => setShowInviteForm(!showInviteForm)}
        >
          {showInviteForm ? 'Cancel' : '+ Invite member'}
        </button>
      </div>

      {/* Invite form — shown above table when open */}
      {showInviteForm && (
        <div style={{
          padding: 20,
          background: palette.hoverBg,
          border: `1px solid ${palette.border}`,
          borderRadius: 8,
          marginBottom: 20,
        }}>
          <div style={{
            fontSize: 15,
            fontWeight: 600,
            color: palette.textPrimary,
            marginBottom: 12,
          }}>
            Invite new team member
            <HelpTooltip text="Send an invitation to a new team member. They will receive an email with access instructions." docLink="https://agentredcx.com/docs/admin-guide/team-management#inviting-team-members" />
          </div>
          <div style={s.formRow}>
            <div style={s.formField}>
              <label style={s.formLabel}>Email *</label>
              <input
                type="email"
                style={s.input}
                value={inviteEmail}
                onChange={(e) => setInviteEmail(e.target.value)}
                placeholder="colleague@company.com"
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleInvite();
                }}
              />
            </div>
            <div style={s.formField}>
              <label style={s.formLabel}>Name</label>
              <input
                type="text"
                style={s.input}
                value={inviteName}
                onChange={(e) => setInviteName(e.target.value)}
                placeholder="Jane Smith"
              />
            </div>
            <div style={{ ...s.formField, minWidth: 140, flex: '0 0 auto' }}>
              <label style={s.formLabel}>Role *<HelpTooltip text="Controls what actions a team member can perform. Admin has full access; Viewer is read-only." docLink="https://agentredcx.com/docs/admin-guide/team-management#roles" /></label>
              <select
                style={s.select}
                value={inviteRole}
                onChange={(e) => setInviteRole(e.target.value as TeamRole)}
              >
                {INVITABLE_ROLES.map((r) => (
                  <option key={r.value} value={r.value}>
                    {r.label}
                  </option>
                ))}
              </select>
            </div>
            <button
              style={{
                ...s.inviteButton,
                ...(inviting ? s.inviteButtonDisabled : {}),
              }}
              disabled={inviting}
              onClick={handleInvite}
            >
              {inviting ? 'Inviting...' : 'Send invite'}
            </button>
          </div>
          {inviteError && (
            <div style={{
              marginTop: 8,
              fontSize: 13,
              color: '#DC2626',
            }}>
              {inviteError}
            </div>
          )}
        </div>
      )}

      {/* Team member table — single flat container */}
      {members.length === 0 ? (
        <div style={s.emptyState}>
          <div style={{ fontSize: 24, marginBottom: 8 }}>No team members yet</div>
          <div>Invite your first team member to get started with collaborative support.</div>
        </div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table style={s.table}>
            <thead>
              <tr>
                <th style={s.th}>Team member</th>
                <th style={s.th}>
                  <span
                    style={{ position: 'relative', cursor: 'help' }}
                    onMouseEnter={() => setRoleTooltipOpen(true)}
                    onMouseLeave={() => setRoleTooltipOpen(false)}
                  >
                    Role
                    <span style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      width: 14,
                      height: 14,
                      borderRadius: '50%',
                      border: '1px solid #9ca3af',
                      color: '#9ca3af',
                      fontSize: 9,
                      fontWeight: 700,
                      marginLeft: 6,
                      verticalAlign: 'middle',
                      userSelect: 'none',
                    }}>?</span>
                    {roleTooltipOpen && roleTooltipContent}
                  </span>
                </th>
                <th style={s.th}>Joined</th>
                <th style={s.th}>Last active</th>
                <th style={{ ...s.th, textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {members.map((member) => {
                const isOwner = member.role === 'superadmin';

                return (
                  <tr key={member.id} style={s.tr(false)}>
                    {/* Member info */}
                    <td style={s.td}>
                      <div style={s.memberInfo}>
                        <span style={s.memberName}>
                          {member.displayName || '(No name)'}
                        </span>
                        <span style={s.memberEmail}>{member.email}</span>
                      </div>
                    </td>

                    {/* Role selector (WI #275) + escalation categories (WI #279) */}
                    <td style={s.td}>
                      {isOwner ? (
                        <span style={s.roleBadge(member.role)}>
                          {(ROLES.find((r) => r.value === member.role) || ROLES[3]).label}
                        </span>
                      ) : (
                        <select
                          value={member.role}
                          onChange={(e) => handleInlineRoleChange(member, e.target.value as TeamRole)}
                          style={{
                            padding: '3px 8px',
                            borderRadius: 6,
                            fontSize: 12,
                            fontWeight: 500,
                            border: `1px solid ${palette.inputBorder}`,
                            background: palette.inputBg,
                            color: palette.textPrimary,
                            cursor: 'pointer',
                            outline: 'none',
                            appearance: 'auto' as React.CSSProperties['appearance'],
                          }}
                        >
                          {INVITABLE_ROLES.map((r) => (
                            <option key={r.value} value={r.value}>{r.label}</option>
                          ))}
                        </select>
                      )}
                      {/* Escalation category chips (WI #279) — only for agent role */}
                      {member.role === 'escalation_agent' && (
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, marginTop: 6 }}>
                          {ESCALATION_CATEGORIES.map((cat) => {
                            const isSelected = (member.escalationCategories || []).includes(cat.id);
                            return (
                              <button
                                key={cat.id}
                                type="button"
                                title={cat.description}
                                onClick={() => handleCategoryToggle(member, cat.id)}
                                style={{
                                  padding: '1px 8px',
                                  borderRadius: 10,
                                  fontSize: 11,
                                  fontWeight: 500,
                                  border: `1px solid ${isSelected ? (isDark ? '#2563EB' : '#93C5FD') : palette.border}`,
                                  background: isSelected ? (isDark ? '#1E2A47' : '#DBEAFE') : palette.hoverBg,
                                  color: isSelected ? (isDark ? '#93C5FD' : '#1E40AF') : palette.textSecondary,
                                  cursor: 'pointer',
                                  outline: 'none',
                                  lineHeight: '18px',
                                  whiteSpace: 'nowrap',
                                  transition: 'all 0.15s ease',
                                }}
                              >
                                {cat.label}
                              </button>
                            );
                          })}
                        </div>
                      )}
                    </td>

                    {/* Joined */}
                    <td style={s.td}>
                      <span style={s.dateText}>{formatDate(member.createdAt)}</span>
                    </td>

                    {/* Last active */}
                    <td style={s.td}>
                      <span style={s.dateText}>
                        {formatRelativeDate(member.lastLoginAt)}
                      </span>
                    </td>

                    {/* Actions */}
                    <td style={{ ...s.td, textAlign: 'right' }}>
                      <div style={{ ...s.actionRow, justifyContent: 'flex-end' }}>
                        {!isOwner && (
                          <button
                            style={s.iconButton}
                            title="Remove member"
                            aria-label="Remove member"
                            onClick={() => {
                              setConfirmMember(member);
                              setConfirmAction('remove');
                            }}
                          >
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                              <polyline points="3 6 5 6 21 6" /><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6" /><path d="M10 11v6" /><path d="M14 11v6" /><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2" />
                            </svg>
                          </button>
                        )}
                        {isOwner && (
                          <span style={{ width: 28, display: 'inline-block' }} />
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
      </div>{/* end single container box */}

      {/* Confirmation Dialog (Remove) */}
      {confirmMember && confirmAction && (
        <div
          style={s.overlay}
          onClick={() => {
            if (!actionLoading) {
              setConfirmMember(null);
              setConfirmAction(null);
            }
          }}
        >
          <div style={s.modal} onClick={(e) => e.stopPropagation()}>
            <h4 style={s.modalTitle}>Remove team member</h4>
            <p style={s.modalBody}>
              Are you sure you want to permanently remove <strong>{confirmMember.displayName || confirmMember.email}</strong> ({confirmMember.email})?
              Their API key will be revoked and they will lose all access immediately.
              This action cannot be undone — to restore access, you must re-invite them.
            </p>
            <div style={s.modalActions}>
              <button
                style={s.modalCancel}
                onClick={() => {
                  setConfirmMember(null);
                  setConfirmAction(null);
                }}
                disabled={actionLoading}
              >
                Cancel
              </button>
              <button
                style={{
                  ...s.modalConfirm,
                  ...(actionLoading ? { opacity: 0.6, cursor: 'not-allowed' } : {}),
                }}
                onClick={handleConfirmAction}
                disabled={actionLoading}
              >
                {actionLoading ? 'Removing...' : 'Remove member'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Edit Dialog */}
      {editMember && (
        <div
          style={s.overlay}
          onClick={() => {
            if (!editLoading) setEditMember(null);
          }}
        >
          <div style={s.editModal} onClick={(e) => e.stopPropagation()}>
            <h4 style={s.modalTitle}>Edit team member</h4>
            <p style={{
              fontSize: 13,
              color: palette.textSecondary,
              margin: '0 0 20px 0',
            }}>
              {editMember.displayName || editMember.email} ({editMember.email})
            </p>

            <div style={{ marginBottom: 16 }}>
              <label style={s.formLabel}>Role<HelpTooltip text="Controls what actions a team member can perform. Owner has full access; Viewer is read-only." docLink="https://agentredcx.com/docs/admin-guide/team-management#roles" /></label>
              <select
                style={{ ...s.select, marginTop: 4 }}
                value={editRole}
                onChange={(e) => setEditRole(e.target.value as TeamRole)}
              >
                {INVITABLE_ROLES.map((r) => (
                  <option key={r.value} value={r.value}>
                    {r.label} -- {r.description}
                  </option>
                ))}
              </select>
            </div>

            {/* Escalation categories — visible only for agent role (WI #279) */}
            {editRole === 'escalation_agent' && (
              <div style={{ marginBottom: 16 }}>
                <label style={s.formLabel}>
                  Escalation categories
                  <HelpTooltip text="Select which types of escalated conversations this agent handles. Unselected categories will route to other available agents." docLink="https://agentredcx.com/docs/admin-guide/escalation-rules#escalation-notifications" />
                </label>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 8 }}>
                  {ESCALATION_CATEGORIES.map((cat) => {
                    const isSelected = editCategories.includes(cat.id);
                    return (
                      <label
                        key={cat.id}
                        title={cat.description}
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: 5,
                          padding: '4px 10px',
                          borderRadius: 14,
                          fontSize: 12,
                          fontWeight: 500,
                          border: `1px solid ${isSelected ? (isDark ? '#2563EB' : '#93C5FD') : palette.border}`,
                          background: isSelected ? (isDark ? '#1E2A47' : '#DBEAFE') : palette.hoverBg,
                          color: isSelected ? (isDark ? '#93C5FD' : '#1E40AF') : palette.textSecondary,
                          cursor: 'pointer',
                          transition: 'all 0.15s ease',
                          userSelect: 'none',
                        }}
                      >
                        <input
                          type="checkbox"
                          checked={isSelected}
                          onChange={() => {
                            setEditCategories((prev) =>
                              prev.includes(cat.id)
                                ? prev.filter((c) => c !== cat.id)
                                : [...prev, cat.id],
                            );
                          }}
                          style={{ accentColor: '#3B82F6', width: 14, height: 14 }}
                        />
                        {cat.label}
                      </label>
                    );
                  })}
                </div>
              </div>
            )}

            <div style={s.modalActions}>
              <button
                style={s.modalCancel}
                onClick={() => setEditMember(null)}
                disabled={editLoading}
              >
                Cancel
              </button>
              <button
                style={{
                  ...s.editSaveButton,
                  ...(editLoading ? { opacity: 0.6, cursor: 'not-allowed' } : {}),
                }}
                onClick={handleSaveEdit}
                disabled={editLoading}
              >
                {editLoading ? 'Saving...' : 'Save changes'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TeamManager;
