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
 * Sub-components extracted into admin/shared/team/:
 *   - InviteForm, TeamMemberRow, ConfirmRemoveDialog, EditMemberDialog, RoleTooltip
 *   - constants, styles, utils, types
 *
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useState, useCallback } from 'react';
import type { BaseComponentProps, TeamMember, TeamRole } from './types';
import { useTeamMembers, useInviteTeamMember } from './hooks';

// Extracted sub-modules
import {
  ROLES,
  getPalette,
  useIsDark,
  makeStyles,
  InviteForm,
  TeamMemberRow,
  ConfirmRemoveDialog,
  EditMemberDialog,
  RoleTooltip,
} from './team';

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
  const palette = getPalette(isDark);
  const s = makeStyles(palette, isDark);

  // State
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteName, setInviteName] = useState('');
  const [inviteRole, setInviteRole] = useState<TeamRole>('escalation_agent');
  const [inviteDomainTags, setInviteDomainTags] = useState<string[]>([]);
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
  const [editDomainTags, setEditDomainTags] = useState<string[]>([]);
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

    const result = await invite(
      inviteEmail.trim(), inviteRole, inviteName.trim() || undefined,
      inviteDomainTags.length > 0 ? inviteDomainTags : undefined,
    );
    if (result) {
      onNotify(`Invited ${inviteEmail.trim()} as ${inviteRole}.`, 'success');
      setInviteEmail('');
      setInviteName('');
      setInviteRole('escalation_agent');
      setInviteDomainTags([]);
      setShowInviteForm(false);
      team.refetch();
    } else {
      onNotify(inviteError || 'Failed to invite team member.', 'error');
    }
  }, [inviteEmail, inviteName, inviteRole, inviteDomainTags, invite, inviteError, onNotify, team]);

  // -------------------------------------------------------------------------
  // Edit handler
  // -------------------------------------------------------------------------

  const openEdit = useCallback((member: TeamMember) => {
    setEditMember(member);
    setEditRole(member.role as TeamRole);
    setEditCategories(member.escalationCategories || []);
    setEditDomainTags(member.staffDomainTags || []);
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

      // Domain tags (Phase 4c)
      const origTags = editMember.staffDomainTags || [];
      const tagsChanged = editDomainTags.length !== origTags.length
        || editDomainTags.some((t) => !origTags.includes(t));
      if (tagsChanged) body.staff_domain_tags = editDomainTags;

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
  }, [editMember, editRole, editCategories, editDomainTags, apiFetch, onNotify, team]);

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
  // Active/inactive toggle (WI #280)
  // -------------------------------------------------------------------------

  const handleToggleActive = useCallback(async (member: TeamMember) => {
    const newActive = !member.isActive;
    try {
      const resp = await apiFetch(`/api/admin/team/${member.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_active: newActive }),
      });
      if (!resp.ok) throw new Error(`${resp.status}`);
      onNotify(
        newActive
          ? `${member.displayName || member.email} is now active.`
          : `${member.displayName || member.email} has been disabled.`,
        'success',
      );
      team.refetch();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Status update failed';
      onNotify(`Failed to update status: ${msg}`, 'error');
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
          className="ar-btn-action"
          style={s.inviteButton}
          onClick={() => setShowInviteForm(!showInviteForm)}
        >
          {showInviteForm ? 'Cancel' : '+ Invite member'}
        </button>
      </div>

      {/* Invite form — shown above table when open */}
      {showInviteForm && (
        <InviteForm
          styles={s}
          palette={palette}
          inviteEmail={inviteEmail}
          inviteName={inviteName}
          inviteRole={inviteRole}
          inviteDomainTags={inviteDomainTags}
          inviting={inviting}
          inviteError={inviteError}
          onEmailChange={setInviteEmail}
          onNameChange={setInviteName}
          onRoleChange={setInviteRole}
          onDomainTagsChange={setInviteDomainTags}
          onInvite={handleInvite}
        />
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
                    {roleTooltipOpen && (
                      <RoleTooltip
                        isDark={isDark}
                        onMouseEnter={() => setRoleTooltipOpen(true)}
                        onMouseLeave={() => setRoleTooltipOpen(false)}
                      />
                    )}
                  </span>
                </th>
                <th style={s.th}>Joined</th>
                <th style={s.th}>Last active</th>
                <th style={s.th}>Escalations</th>
                <th style={{ ...s.th, textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {members.map((member) => (
                <TeamMemberRow
                  key={member.id}
                  member={member}
                  styles={s}
                  palette={palette}
                  isDark={isDark}
                  onRoleChange={handleInlineRoleChange}
                  onCategoryToggle={handleCategoryToggle}
                  onToggleActive={handleToggleActive}
                  onEdit={openEdit}
                  onRemove={(m) => {
                    setConfirmMember(m);
                    setConfirmAction('remove');
                  }}
                />
              ))}
            </tbody>
          </table>
        </div>
      )}
      </div>{/* end single container box */}

      {/* Confirmation Dialog (Remove) */}
      {confirmMember && confirmAction && (
        <ConfirmRemoveDialog
          member={confirmMember}
          styles={s}
          actionLoading={actionLoading}
          onConfirm={handleConfirmAction}
          onCancel={() => {
            setConfirmMember(null);
            setConfirmAction(null);
          }}
        />
      )}

      {/* Edit Dialog */}
      {editMember && (
        <EditMemberDialog
          member={editMember}
          styles={s}
          palette={palette}
          isDark={isDark}
          editRole={editRole}
          editCategories={editCategories}
          editDomainTags={editDomainTags}
          editLoading={editLoading}
          onRoleChange={setEditRole}
          onCategoriesChange={setEditCategories}
          onDomainTagsChange={setEditDomainTags}
          onSave={handleSaveEdit}
          onCancel={() => setEditMember(null)}
        />
      )}
    </div>
  );
};

export default TeamManager;
