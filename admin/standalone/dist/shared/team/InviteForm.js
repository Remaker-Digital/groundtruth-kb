import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { INVITABLE_ROLES } from './constants';
import { HelpTooltip } from '../HelpTooltip';
export const InviteForm = ({ styles: s, palette, inviteEmail, inviteName, inviteRole, inviting, inviteError, onEmailChange, onNameChange, onRoleChange, onInvite, }) => {
    return (_jsxs("div", { style: {
            padding: 20,
            background: palette.hoverBg,
            border: `1px solid ${palette.border}`,
            borderRadius: 8,
            marginBottom: 20,
        }, children: [_jsxs("div", { style: {
                    fontSize: 15,
                    fontWeight: 600,
                    color: palette.textPrimary,
                    marginBottom: 12,
                }, children: ["Invite new team member", _jsx(HelpTooltip, { text: "Send an invitation to a new team member. They will receive an email with access instructions.", docLink: "https://agentredcx.com/docs/admin-guide/team-management#inviting-team-members" })] }), _jsxs("div", { style: s.formRow, children: [_jsxs("div", { style: s.formField, children: [_jsx("label", { style: s.formLabel, children: "Email *" }), _jsx("input", { type: "email", style: s.input, value: inviteEmail, onChange: (e) => onEmailChange(e.target.value), placeholder: "colleague@company.com", onKeyDown: (e) => {
                                    if (e.key === 'Enter')
                                        onInvite();
                                } })] }), _jsxs("div", { style: s.formField, children: [_jsx("label", { style: s.formLabel, children: "Name" }), _jsx("input", { type: "text", style: s.input, value: inviteName, onChange: (e) => onNameChange(e.target.value), placeholder: "Jane Smith" })] }), _jsxs("div", { style: { ...s.formField, minWidth: 140, flex: '0 0 auto' }, children: [_jsxs("label", { style: s.formLabel, children: ["Role *", _jsx(HelpTooltip, { text: "Controls what actions a team member can perform. Admin has full access; Viewer is read-only.", docLink: "https://agentredcx.com/docs/admin-guide/team-management#roles" })] }), _jsx("select", { style: s.select, value: inviteRole, onChange: (e) => onRoleChange(e.target.value), children: INVITABLE_ROLES.map((r) => (_jsx("option", { value: r.value, children: r.label }, r.value))) })] }), _jsx("button", { style: {
                            ...s.inviteButton,
                            ...(inviting ? s.inviteButtonDisabled : {}),
                        }, disabled: inviting, onClick: onInvite, children: inviting ? 'Inviting...' : 'Send invite' })] }), inviteError && (_jsx("div", { style: {
                    marginTop: 8,
                    fontSize: 13,
                    color: '#DC2626',
                }, children: inviteError }))] }));
};
//# sourceMappingURL=InviteForm.js.map