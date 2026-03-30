/**
 * InviteForm — Invite-new-team-member form, extracted from TeamManager.
 *
 * Presentational component: receives all state and callbacks as props.
 * No API calls or local state management — all owned by the parent.
 *
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React from 'react';
import type { TeamRole, InviteFormProps } from './types';
import { INVITABLE_ROLES } from './constants';
import { HelpTooltip } from '../HelpTooltip';

export const InviteForm: React.FC<InviteFormProps> = ({
  styles: s,
  palette,
  inviteEmail,
  inviteName,
  inviteRole,
  inviteDomainTags,
  inviting,
  inviteError,
  onEmailChange,
  onNameChange,
  onRoleChange,
  onDomainTagsChange,
  onInvite,
}) => {
  return (
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
            onChange={(e) => onEmailChange(e.target.value)}
            placeholder="colleague@company.com"
            onKeyDown={(e) => {
              if (e.key === 'Enter') onInvite();
            }}
          />
        </div>
        <div style={s.formField}>
          <label style={s.formLabel}>Name</label>
          <input
            type="text"
            style={s.input}
            value={inviteName}
            onChange={(e) => onNameChange(e.target.value)}
            placeholder="Jane Smith"
          />
        </div>
        <div style={{ ...s.formField, minWidth: 140, flex: '0 0 auto' }}>
          <label style={s.formLabel}>Role *<HelpTooltip text="Controls what actions a team member can perform. Admin has full access; Viewer is read-only." docLink="https://agentredcx.com/docs/admin-guide/team-management#roles" /></label>
          <select
            style={s.select}
            value={inviteRole}
            onChange={(e) => onRoleChange(e.target.value as TeamRole)}
          >
            {INVITABLE_ROLES.map((r) => (
              <option key={r.value} value={r.value}>
                {r.label}
              </option>
            ))}
          </select>
        </div>
        <div style={{ ...s.formField, minWidth: 180, flex: '1 1 auto' }}>
          <label style={s.formLabel}>Domain tags</label>
          <input
            type="text"
            style={s.input}
            placeholder="tag1, tag2..."
            value={inviteDomainTags.join(', ')}
            onChange={(e) => {
              const tags = e.target.value
                .split(',')
                .map((t) => t.trim().toLowerCase())
                .filter(Boolean);
              onDomainTagsChange(tags);
            }}
          />
        </div>
        <button
          style={{
            ...s.inviteButton,
            ...(inviting ? s.inviteButtonDisabled : {}),
          }}
          disabled={inviting}
          onClick={onInvite}
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
  );
};
