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

import React, { useState, useCallback } from 'react';
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

const ROLE_COLORS: Record<string, { bg: string; text: string }> = {
  superadmin: { bg: '#FEF2F2', text: '#991B1B' },
  admin: { bg: '#EDE9FE', text: '#5B21B6' },
  escalation_agent: { bg: '#DBEAFE', text: '#1E40AF' },
  viewer: { bg: '#F3F4F6', text: '#374151' },
};

const STATUS_DISPLAY: Record<string, { label: string; color: string }> = {
  active: { label: 'Active', color: '#059669' },
  invited: { label: 'Invited', color: '#D97706' },
  disabled: { label: 'Disabled', color: '#9CA3AF' },
};

// ---------------------------------------------------------------------------
// Styles
// ---------------------------------------------------------------------------

const s = {
  container: {
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    maxWidth: 960,
    margin: '0 auto',
  } as React.CSSProperties,

  card: {
    background: '#FFFFFF',
    border: '1px solid #E5E7EB',
    borderRadius: 8,
    padding: 24,
    marginBottom: 24,
  } as React.CSSProperties,

  sectionTitle: {
    fontSize: 18,
    fontWeight: 600,
    color: '#111827',
    margin: '0 0 8px 0',
  } as React.CSSProperties,

  sectionDescription: {
    fontSize: 13,
    color: '#6B7280',
    margin: '0 0 20px 0',
    lineHeight: 1.5,
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
    color: '#6B7280',
    textTransform: 'uppercase' as const,
    letterSpacing: '0.05em',
    padding: '8px 12px',
    borderBottom: '2px solid #E5E7EB',
  } as React.CSSProperties,

  td: {
    padding: '12px',
    borderBottom: '1px solid #F3F4F6',
    fontSize: 14,
    color: '#111827',
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
    color: '#111827',
  } as React.CSSProperties,

  memberEmail: {
    fontSize: 13,
    color: '#6B7280',
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

  statusDot: (color: string): React.CSSProperties => ({
    display: 'inline-flex',
    alignItems: 'center',
    gap: 6,
    fontSize: 13,
    color: '#374151',
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
    color: '#6B7280',
  } as React.CSSProperties,

  // Actions
  actionRow: {
    display: 'flex',
    gap: 6,
  } as React.CSSProperties,

  actionButton: (variant: 'edit' | 'remove' | 'enable'): React.CSSProperties => ({
    padding: '4px 10px',
    fontSize: 12,
    fontWeight: 500,
    borderRadius: 4,
    cursor: 'pointer',
    border: '1px solid',
    borderColor:
      variant === 'remove' ? '#FECACA' : variant === 'enable' ? '#BBF7D0' : '#D1D5DB',
    background:
      variant === 'remove' ? '#FEF2F2' : variant === 'enable' ? '#F0FDF4' : '#F9FAFB',
    color:
      variant === 'remove' ? '#DC2626' : variant === 'enable' ? '#166534' : '#374151',
  }),

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
    color: '#374151',
  } as React.CSSProperties,

  input: {
    padding: '8px 12px',
    fontSize: 14,
    border: '1px solid #D1D5DB',
    borderRadius: 6,
    color: '#111827',
    background: '#FFFFFF',
    outline: 'none',
    boxSizing: 'border-box' as const,
    width: '100%',
  } as React.CSSProperties,

  select: {
    padding: '8px 12px',
    fontSize: 14,
    border: '1px solid #D1D5DB',
    borderRadius: 6,
    color: '#111827',
    background: '#FFFFFF',
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
    background: 'rgba(0,0,0,0.4)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 10000,
  } as React.CSSProperties,

  modal: {
    background: '#FFFFFF',
    borderRadius: 12,
    padding: 24,
    width: 420,
    maxWidth: '90vw',
    boxShadow: '0 20px 60px rgba(0,0,0,0.2)',
  } as React.CSSProperties,

  modalTitle: {
    fontSize: 16,
    fontWeight: 600,
    color: '#111827',
    margin: '0 0 8px 0',
  } as React.CSSProperties,

  modalBody: {
    fontSize: 14,
    color: '#374151',
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
    background: '#F3F4F6',
    color: '#374151',
    border: '1px solid #D1D5DB',
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
    background: '#FFFFFF',
    borderRadius: 12,
    padding: 24,
    width: 460,
    maxWidth: '90vw',
    boxShadow: '0 20px 60px rgba(0,0,0,0.2)',
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

  // Role descriptions
  roleCard: {
    padding: '10px 14px',
    background: '#F9FAFB',
    border: '1px solid #E5E7EB',
    borderRadius: 6,
    marginBottom: 8,
    display: 'flex',
    alignItems: 'center',
    gap: 12,
  } as React.CSSProperties,

  roleCardLabel: {
    fontSize: 13,
    fontWeight: 600,
    color: '#111827',
    minWidth: 60,
  } as React.CSSProperties,

  roleCardDesc: {
    fontSize: 12,
    color: '#6B7280',
    flex: 1,
  } as React.CSSProperties,

  // Empty & loading
  loadingContainer: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 48,
    color: '#6B7280',
    fontSize: 14,
  } as React.CSSProperties,

  errorContainer: {
    padding: 24,
    background: '#FEF2F2',
    border: '1px solid #FECACA',
    borderRadius: 8,
    color: '#991B1B',
    fontSize: 14,
    textAlign: 'center' as const,
  } as React.CSSProperties,

  retryButton: {
    marginTop: 12,
    padding: '6px 16px',
    background: '#DC2626',
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
    color: '#6B7280',
    fontSize: 14,
  } as React.CSSProperties,
};

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
  // State
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteName, setInviteName] = useState('');
  const [inviteRole, setInviteRole] = useState<TeamRole>('escalation_agent');
  const [showInviteForm, setShowInviteForm] = useState(false);

  // Confirmation dialog
  const [confirmMember, setConfirmMember] = useState<TeamMember | null>(null);
  const [confirmAction, setConfirmAction] = useState<'remove' | 'disable' | null>(null);
  const [actionLoading, setActionLoading] = useState(false);

  // Edit dialog
  const [editMember, setEditMember] = useState<TeamMember | null>(null);
  const [editRole, setEditRole] = useState<TeamRole>('escalation_agent');
  const [editActive, setEditActive] = useState(true);
  const [editCategories, setEditCategories] = useState<string[]>([]);
  const [editLoading, setEditLoading] = useState(false);

  // Data hooks
  const team = useTeamMembers(apiFetch);
  const { invite, loading: inviting, error: inviteError } = useInviteTeamMember(apiFetch);

  const members: TeamMember[] = team.data?.members ?? [];
  const activeCount = members.filter((m) => m.isActive).length;
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
    setEditActive(member.isActive);
    setEditCategories(member.escalationCategories || []);
  }, []);

  const handleSaveEdit = useCallback(async () => {
    if (!editMember) return;
    setEditLoading(true);

    try {
      const body: Record<string, unknown> = {};
      if (editRole !== editMember.role) body.role = editRole;
      const isNowActive = editActive;
      const wasActive = editMember.isActive;
      if (isNowActive !== wasActive) body.is_active = isNowActive;
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
  }, [editMember, editRole, editActive, apiFetch, onNotify, team]);

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

  const handleReactivate = useCallback(async (member: TeamMember) => {
    try {
      const resp = await apiFetch(`/api/admin/team/${member.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_active: true }),
      });

      if (!resp.ok) throw new Error(`${resp.status}`);
      onNotify(`Reactivated ${member.email}.`, 'success');
      team.refetch();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Reactivation failed';
      onNotify(`Failed to reactivate: ${msg}`, 'error');
    }
  }, [apiFetch, onNotify, team]);

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
  // Inline status toggle (WI #280)
  // -------------------------------------------------------------------------

  const handleInlineToggle = useCallback(async (member: TeamMember) => {
    const newActive = !member.isActive;
    try {
      const resp = await apiFetch(`/api/admin/team/${member.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_active: newActive }),
      });
      if (!resp.ok) throw new Error(`${resp.status}`);
      onNotify(`${member.email} ${newActive ? 'enabled' : 'disabled'}.`, 'success');
      team.refetch();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Toggle failed';
      onNotify(`Failed to update status: ${msg}`, 'error');
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
  // Render
  // -------------------------------------------------------------------------

  return (
    <div style={s.container}>
      {/* Header card with role descriptions */}
      <div style={s.card}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          marginBottom: 16,
        }}>
          <div>
            <h3 style={s.sectionTitle}>Team members<HelpTooltip text="Manage who can access your Agent Red admin dashboard and what they can do." /></h3>
            <p style={s.sectionDescription}>
              {activeCount} active member{activeCount !== 1 ? 's' : ''} of {totalCount} total.
              Manage roles and access for your support team.
            </p>
          </div>
          <button
            style={s.inviteButton}
            onClick={() => setShowInviteForm(!showInviteForm)}
          >
            {showInviteForm ? 'Cancel' : '+ Invite member'}
          </button>
        </div>

        {/* Role descriptions */}
        <div style={{ marginBottom: 20 }}>
          <div style={{
            fontSize: 13,
            fontWeight: 600,
            color: '#374151',
            marginBottom: 8,
          }}>
            Role permissions
          </div>
          {ROLES.map((role) => (
            <div key={role.value} style={s.roleCard}>
              <span style={{
                ...s.roleCardLabel,
                ...s.roleBadge(role.value),
                minWidth: 'auto',
              }}>
                {role.label}
              </span>
              <span style={s.roleCardDesc}>{role.description}</span>
            </div>
          ))}
        </div>

        {/* Invite form */}
        {showInviteForm && (
          <div style={{
            padding: 20,
            background: '#F9FAFB',
            border: '1px solid #E5E7EB',
            borderRadius: 8,
            marginBottom: 20,
          }}>
            <div style={{
              fontSize: 15,
              fontWeight: 600,
              color: '#111827',
              marginBottom: 12,
            }}>
              Invite new team member
              <HelpTooltip text="Send an invitation to a new team member. They will receive an email with access instructions." />
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
                <label style={s.formLabel}>Role *<HelpTooltip text="Controls what actions a team member can perform. Owner has full access; Viewer is read-only." /></label>
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
      </div>

      {/* Team member table */}
      <div style={s.card}>
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
                  <th style={s.th}>Role<HelpTooltip text="Controls what actions a team member can perform. Owner has full access; Viewer is read-only." /></th>
                  <th style={s.th}>Status</th>
                  <th style={s.th}>Joined</th>
                  <th style={s.th}>Last Active</th>
                  <th style={{ ...s.th, textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {members.map((member) => {
                  const isOwner = member.role === 'superadmin';
                  const isDisabled = !member.isActive;
                  const memberStatus = member.isActive ? 'active' : 'disabled';
                  const statusInfo = STATUS_DISPLAY[memberStatus] || STATUS_DISPLAY.active;

                  return (
                    <tr key={member.id} style={s.tr(isDisabled)}>
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
                              borderRadius: 12,
                              fontSize: 12,
                              fontWeight: 600,
                              border: '1px solid #e1e4e8',
                              background: (ROLE_COLORS[member.role] || ROLE_COLORS.viewer).bg,
                              color: (ROLE_COLORS[member.role] || ROLE_COLORS.viewer).text,
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
                                    border: `1px solid ${isSelected ? '#93C5FD' : '#E5E7EB'}`,
                                    background: isSelected ? '#DBEAFE' : '#F9FAFB',
                                    color: isSelected ? '#1E40AF' : '#9CA3AF',
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

                      {/* Status toggle (WI #280) */}
                      <td style={s.td}>
                        {isOwner ? (
                          <span style={s.statusDot(statusInfo.color)}>
                            <span style={s.dot(statusInfo.color)} />
                            {statusInfo.label}
                          </span>
                        ) : (
                          <label style={{ display: 'inline-flex', alignItems: 'center', gap: 6, cursor: 'pointer' }}>
                            <input
                              type="checkbox"
                              checked={member.isActive}
                              onChange={() => handleInlineToggle(member)}
                              style={{ accentColor: '#059669', width: 16, height: 16, cursor: 'pointer' }}
                            />
                            <span style={{ fontSize: 12, color: member.isActive ? '#059669' : '#9CA3AF', fontWeight: 500 }}>
                              {member.isActive ? 'Active' : 'Disabled'}
                            </span>
                          </label>
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
                              style={s.actionButton('remove')}
                              onClick={() => {
                                setConfirmMember(member);
                                setConfirmAction('remove');
                              }}
                            >
                              Remove
                            </button>
                          )}
                          {isOwner && (
                            <span style={{
                              fontSize: 12,
                              color: '#9CA3AF',
                              padding: '4px 8px',
                            }}>
                              --
                            </span>
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
      </div>

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
              Are you sure you want to remove <strong>{confirmMember.displayName || confirmMember.email}</strong> ({confirmMember.email})?
              They will no longer have access to the admin dashboard or be able to handle
              escalated conversations. This action can be reversed by reactivating the member.
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
              color: '#6B7280',
              margin: '0 0 20px 0',
            }}>
              {editMember.displayName || editMember.email} ({editMember.email})
            </p>

            <div style={{ marginBottom: 16 }}>
              <label style={s.formLabel}>Role<HelpTooltip text="Controls what actions a team member can perform. Owner has full access; Viewer is read-only." /></label>
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
                  <HelpTooltip text="Select which types of escalated conversations this agent handles. Unselected categories will route to other available agents." />
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
                          border: `1px solid ${isSelected ? '#93C5FD' : '#E5E7EB'}`,
                          background: isSelected ? '#DBEAFE' : '#F9FAFB',
                          color: isSelected ? '#1E40AF' : '#6B7280',
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

            <div style={{ marginBottom: 20 }}>
              <label style={s.formLabel}>Status</label>
              <div style={{ marginTop: 8, display: 'flex', gap: 16 }}>
                <label style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 6,
                  cursor: 'pointer',
                  fontSize: 14,
                  color: '#111827',
                }}>
                  <input
                    type="radio"
                    name="edit-status"
                    checked={editActive}
                    onChange={() => setEditActive(true)}
                  />
                  Active
                </label>
                <label style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 6,
                  cursor: 'pointer',
                  fontSize: 14,
                  color: '#111827',
                }}>
                  <input
                    type="radio"
                    name="edit-status"
                    checked={!editActive}
                    onChange={() => setEditActive(false)}
                  />
                  Disabled
                </label>
              </div>
            </div>

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
