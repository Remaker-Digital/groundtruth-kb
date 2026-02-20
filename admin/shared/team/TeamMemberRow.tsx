/**
 * TeamMemberRow — Single team member table row, extracted from TeamManager.
 *
 * Renders member info, inline role selector, escalation category chips,
 * join date, last active date, escalation count, and action buttons.
 *
 * Presentational component: receives all data and callbacks as props.
 *
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React from 'react';
import type { TeamRole, TeamMemberRowProps } from './types';
import { ROLES, INVITABLE_ROLES } from './constants';
import { ESCALATION_CATEGORIES } from '../types';
import { formatDate, formatRelativeDate } from './utils';
import { tokens } from '../theme/styles';

export const TeamMemberRow: React.FC<TeamMemberRowProps> = ({
  member,
  styles: s,
  palette,
  isDark,
  onRoleChange,
  onCategoryToggle,
  onRemove,
}) => {
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
            onChange={(e) => onRoleChange(member, e.target.value as TeamRole)}
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
                  onClick={() => onCategoryToggle(member, cat.id)}
                  style={{
                    padding: '1px 8px',
                    borderRadius: 10,
                    fontSize: 11,
                    fontWeight: 500,
                    border: `1px solid ${isSelected ? (isDark ? tokens.actionHover : '#93C5FD') : palette.border}`,
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

      {/* Unresolved escalation count (D57) */}
      <td style={s.td}>
        {member.role === 'escalation_agent'
          ? (member.unresolvedEscalationCount ?? 0)
          : '--'}
      </td>

      {/* Actions */}
      <td style={{ ...s.td, textAlign: 'right' }}>
        <div style={{ ...s.actionRow, justifyContent: 'flex-end' }}>
          {!isOwner && (
            <button
              style={s.iconButton}
              title="Remove member"
              aria-label="Remove member"
              onClick={() => onRemove(member)}
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
};
