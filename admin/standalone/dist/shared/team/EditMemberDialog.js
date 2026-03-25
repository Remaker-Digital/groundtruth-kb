import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { INVITABLE_ROLES } from './constants';
import { ESCALATION_CATEGORIES } from '../types';
import { HelpTooltip } from '../HelpTooltip';
import { tokens } from '../theme/styles';
export const EditMemberDialog = ({ member, styles: s, palette, isDark, editRole, editCategories, editLoading, onRoleChange, onCategoriesChange, onSave, onCancel, }) => {
    return (_jsx("div", { style: s.overlay, onClick: () => {
            if (!editLoading)
                onCancel();
        }, children: _jsxs("div", { style: s.editModal, onClick: (e) => e.stopPropagation(), children: [_jsx("h4", { style: s.modalTitle, children: "Edit team member" }), _jsxs("p", { style: {
                        fontSize: 13,
                        color: palette.textSecondary,
                        margin: '0 0 20px 0',
                    }, children: [member.displayName || member.email, " (", member.email, ")"] }), _jsxs("div", { style: { marginBottom: 16 }, children: [_jsxs("label", { style: s.formLabel, children: ["Role", _jsx(HelpTooltip, { text: "Controls what actions a team member can perform. Owner has full access; Viewer is read-only.", docLink: "https://agentredcx.com/docs/admin-guide/team-management#roles" })] }), _jsx("select", { style: { ...s.select, marginTop: 4 }, value: editRole, onChange: (e) => onRoleChange(e.target.value), children: INVITABLE_ROLES.map((r) => (_jsxs("option", { value: r.value, children: [r.label, " -- ", r.description] }, r.value))) })] }), editRole === 'escalation_agent' && (_jsxs("div", { style: { marginBottom: 16 }, children: [_jsxs("label", { style: s.formLabel, children: ["Escalation categories", _jsx(HelpTooltip, { text: "Select which types of escalated conversations this agent handles. Unselected categories will route to other available agents.", docLink: "https://agentredcx.com/docs/admin-guide/escalation-rules#escalation-notifications" })] }), _jsx("div", { style: { display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 8 }, children: ESCALATION_CATEGORIES.map((cat) => {
                                const isSelected = editCategories.includes(cat.id);
                                return (_jsxs("label", { title: cat.description, style: {
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
                                    }, children: [_jsx("input", { type: "checkbox", checked: isSelected, onChange: () => {
                                                const next = editCategories.includes(cat.id)
                                                    ? editCategories.filter((c) => c !== cat.id)
                                                    : [...editCategories, cat.id];
                                                onCategoriesChange(next);
                                            }, style: { accentColor: tokens.action, width: 14, height: 14 } }), cat.label] }, cat.id));
                            }) })] })), _jsxs("div", { style: s.modalActions, children: [_jsx("button", { style: s.modalCancel, onClick: onCancel, disabled: editLoading, children: "Cancel" }), _jsx("button", { style: {
                                ...s.editSaveButton,
                                ...(editLoading ? { opacity: 0.6, cursor: 'not-allowed' } : {}),
                            }, onClick: onSave, disabled: editLoading, children: editLoading ? 'Saving...' : 'Save changes' })] })] }) }));
};
//# sourceMappingURL=EditMemberDialog.js.map