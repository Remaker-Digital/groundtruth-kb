import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { ROLES, INVITABLE_ROLES } from './constants';
import { ESCALATION_CATEGORIES } from '../types';
import { formatDate, formatRelativeDate } from './utils';
import { tokens } from '../theme/styles';
export const TeamMemberRow = ({ member, styles: s, palette, isDark, onRoleChange, onCategoryToggle, onToggleActive, onRemove, }) => {
    const isOwner = member.role === 'superadmin';
    const isInactive = member.isActive === false;
    return (_jsxs("tr", { style: { ...s.tr(false), opacity: isInactive ? 0.5 : 1, transition: 'opacity 0.2s ease' }, children: [_jsx("td", { style: s.td, children: _jsxs("div", { style: s.memberInfo, children: [_jsx("span", { style: s.memberName, children: member.displayName || '(No name)' }), _jsx("span", { style: s.memberEmail, children: member.email })] }) }), _jsxs("td", { style: s.td, children: [isOwner ? (_jsx("span", { style: s.roleBadge(member.role), children: (ROLES.find((r) => r.value === member.role) || ROLES[3]).label })) : (_jsx("select", { value: member.role, onChange: (e) => onRoleChange(member, e.target.value), style: {
                            padding: '3px 8px',
                            borderRadius: 6,
                            fontSize: 12,
                            fontWeight: 500,
                            border: `1px solid ${palette.inputBorder}`,
                            background: palette.inputBg,
                            color: palette.textPrimary,
                            cursor: 'pointer',
                            outline: 'none',
                            appearance: 'auto',
                        }, children: INVITABLE_ROLES.map((r) => (_jsx("option", { value: r.value, children: r.label }, r.value))) })), member.role === 'escalation_agent' && (_jsx("div", { style: { display: 'flex', flexWrap: 'wrap', gap: 4, marginTop: 6 }, children: ESCALATION_CATEGORIES.map((cat) => {
                            const isSelected = (member.escalationCategories || []).includes(cat.id);
                            return (_jsx("button", { type: "button", title: cat.description, onClick: () => onCategoryToggle(member, cat.id), style: {
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
                                }, children: cat.label }, cat.id));
                        }) }))] }), _jsx("td", { style: s.td, children: _jsx("span", { style: s.dateText, children: formatDate(member.createdAt) }) }), _jsx("td", { style: s.td, children: _jsx("span", { style: s.dateText, children: formatRelativeDate(member.lastLoginAt) }) }), _jsx("td", { style: s.td, children: member.role === 'escalation_agent'
                    ? (member.unresolvedEscalationCount ?? 0)
                    : '--' }), _jsx("td", { style: { ...s.td, textAlign: 'right' }, children: _jsxs("div", { style: { ...s.actionRow, justifyContent: 'flex-end', gap: 6 }, children: [!isOwner && (_jsx("button", { type: "button", style: {
                                ...s.iconButton,
                                padding: '2px 8px',
                                borderRadius: 10,
                                fontSize: 11,
                                fontWeight: 500,
                                border: `1px solid ${isInactive ? (isDark ? '#7f1d1d' : '#fca5a5') : (isDark ? '#14532d' : '#86efac')}`,
                                background: isInactive ? (isDark ? '#450a0a' : '#fef2f2') : (isDark ? '#052e16' : '#f0fdf4'),
                                color: isInactive ? (isDark ? '#fca5a5' : '#dc2626') : (isDark ? '#86efac' : '#16a34a'),
                                cursor: 'pointer',
                                lineHeight: '18px',
                                whiteSpace: 'nowrap',
                                transition: 'all 0.15s ease',
                            }, title: isInactive ? 'Enable this team member' : 'Disable this team member', "aria-label": isInactive ? 'Enable member' : 'Disable member', onClick: () => onToggleActive(member), children: isInactive ? 'Disabled' : 'Active' })), !isOwner && (_jsx("button", { style: s.iconButton, title: "Remove member", "aria-label": "Remove member", onClick: () => onRemove(member), children: _jsxs("svg", { width: "16", height: "16", viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: "2", strokeLinecap: "round", strokeLinejoin: "round", children: [_jsx("polyline", { points: "3 6 5 6 21 6" }), _jsx("path", { d: "M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6" }), _jsx("path", { d: "M10 11v6" }), _jsx("path", { d: "M14 11v6" }), _jsx("path", { d: "M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2" })] }) })), isOwner && (_jsx("span", { style: { width: 28, display: 'inline-block' } }))] }) })] }, member.id));
};
//# sourceMappingURL=TeamMemberRow.js.map