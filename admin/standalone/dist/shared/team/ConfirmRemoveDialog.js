import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
export const ConfirmRemoveDialog = ({ member, styles: s, actionLoading, onConfirm, onCancel, }) => {
    return (_jsx("div", { style: s.overlay, onClick: () => {
            if (!actionLoading)
                onCancel();
        }, children: _jsxs("div", { style: s.modal, onClick: (e) => e.stopPropagation(), children: [_jsx("h4", { style: s.modalTitle, children: "Remove team member" }), _jsxs("p", { style: s.modalBody, children: ["Are you sure you want to permanently remove ", _jsx("strong", { children: member.displayName || member.email }), " (", member.email, ")? Their API key will be revoked and they will lose all access immediately. This action cannot be undone \u2014 to restore access, you must re-invite them."] }), _jsxs("div", { style: s.modalActions, children: [_jsx("button", { style: s.modalCancel, onClick: onCancel, disabled: actionLoading, children: "Cancel" }), _jsx("button", { style: {
                                ...s.modalConfirm,
                                ...(actionLoading ? { opacity: 0.6, cursor: 'not-allowed' } : {}),
                            }, onClick: onConfirm, disabled: actionLoading, children: actionLoading ? 'Removing...' : 'Remove member' })] })] }) }));
};
//# sourceMappingURL=ConfirmRemoveDialog.js.map