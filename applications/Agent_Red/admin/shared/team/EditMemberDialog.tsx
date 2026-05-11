// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * EditMemberDialog — Modal for editing a team member's role and escalation categories.
 *
 * Extracted from TeamManager.tsx. Presentational component: receives all
 * edit state and callbacks as props. No local state or API calls.
 *
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React from 'react';
import type { TeamRole, EditMemberDialogProps } from './types';
import { INVITABLE_ROLES } from './constants';
import { ESCALATION_CATEGORIES } from '../types';
import { HelpTooltip } from '../HelpTooltip';
import { tokens } from '../theme/styles';

export const EditMemberDialog: React.FC<EditMemberDialogProps> = ({
  member,
  styles: s,
  palette,
  isDark,
  editRole,
  editCategories,
  editDomainTags,
  editLoading,
  onRoleChange,
  onCategoriesChange,
  onDomainTagsChange,
  onSave,
  onCancel,
}) => {
  return (
    <div
      style={s.overlay}
      onClick={() => {
        if (!editLoading) onCancel();
      }}
    >
      <div style={s.editModal} onClick={(e) => e.stopPropagation()}>
        <h4 style={s.modalTitle}>Edit team member</h4>
        <p style={{
          fontSize: 13,
          color: palette.textSecondary,
          margin: '0 0 20px 0',
        }}>
          {member.displayName || member.email} ({member.email})
        </p>

        <div style={{ marginBottom: 16 }}>
          <label style={s.formLabel}>Role<HelpTooltip text="Controls what actions a team member can perform. Owner has full access; Viewer is read-only." docLink="https://agentredcx.com/docs/admin-guide/team-management#roles" /></label>
          <select
            style={{ ...s.select, marginTop: 4 }}
            value={editRole}
            onChange={(e) => onRoleChange(e.target.value as TeamRole)}
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
                      border: `1px solid ${isSelected ? (isDark ? tokens.actionHover : '#93C5FD') : palette.border}`,
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
                        const next = editCategories.includes(cat.id)
                          ? editCategories.filter((c) => c !== cat.id)
                          : [...editCategories, cat.id];
                        onCategoriesChange(next);
                      }}
                      style={{ accentColor: tokens.action, width: 14, height: 14 }}
                    />
                    {cat.label}
                  </label>
                );
              })}
            </div>
          </div>
        )}

        {/* Domain tags — visible for all roles (Phase 4c) */}
        <div style={{ marginBottom: 16 }}>
          <label style={s.formLabel}>
            Domain tags
            <HelpTooltip text="Controls which private-scope agents this member can interact with. Tags must match the agent's domain tags exactly (case-insensitive)." docLink="https://agentredcx.com/docs/admin-guide/domain-scoping" />
          </label>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 8, alignItems: 'center' }}>
            {editDomainTags.map((tag) => (
              <span
                key={tag}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 4,
                  padding: '3px 10px',
                  borderRadius: 14,
                  fontSize: 12,
                  fontWeight: 500,
                  border: `1px solid ${isDark ? tokens.actionHover : '#93C5FD'}`,
                  background: isDark ? '#1E2A47' : '#DBEAFE',
                  color: isDark ? '#93C5FD' : '#1E40AF',
                }}
              >
                {tag}
                <button
                  type="button"
                  onClick={() => onDomainTagsChange(editDomainTags.filter((t) => t !== tag))}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: 'inherit',
                    cursor: 'pointer',
                    fontSize: 14,
                    lineHeight: 1,
                    padding: 0,
                  }}
                >
                  ×
                </button>
              </span>
            ))}
            <input
              type="text"
              placeholder="Add tag..."
              style={{
                ...s.input,
                width: 120,
                padding: '3px 8px',
                fontSize: 12,
                borderRadius: 14,
              }}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  const val = (e.target as HTMLInputElement).value.trim().toLowerCase();
                  if (val && !editDomainTags.includes(val)) {
                    onDomainTagsChange([...editDomainTags, val]);
                  }
                  (e.target as HTMLInputElement).value = '';
                }
              }}
            />
          </div>
          <p style={{ fontSize: 11, color: palette.textSecondary, margin: '4px 0 0 0' }}>
            Type a tag and press Enter. Tags are normalized to lowercase.
          </p>
        </div>

        <div style={s.modalActions}>
          <button
            style={s.modalCancel}
            onClick={onCancel}
            disabled={editLoading}
          >
            Cancel
          </button>
          <button
            style={{
              ...s.editSaveButton,
              ...(editLoading ? { opacity: 0.6, cursor: 'not-allowed' } : {}),
            }}
            onClick={onSave}
            disabled={editLoading}
          >
            {editLoading ? 'Saving...' : 'Save changes'}
          </button>
        </div>
      </div>
    </div>
  );
};
