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

export const EditMemberDialog: React.FC<EditMemberDialogProps> = ({
  member,
  styles: s,
  palette,
  isDark,
  editRole,
  editCategories,
  editLoading,
  onRoleChange,
  onCategoriesChange,
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
                        const next = editCategories.includes(cat.id)
                          ? editCategories.filter((c) => c !== cat.id)
                          : [...editCategories, cat.id];
                        onCategoriesChange(next);
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
