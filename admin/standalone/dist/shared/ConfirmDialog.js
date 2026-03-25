import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { tokens, dialog, button } from './theme/styles';
// ---------------------------------------------------------------------------
// Variant colors
// ---------------------------------------------------------------------------
const VARIANT_COLORS = {
    destructive: tokens.danger,
    primary: tokens.action,
    default: tokens.border,
};
// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------
export default function ConfirmDialog({ open, title, message, confirmLabel = 'Confirm', cancelLabel = 'Cancel', variant = 'default', loading = false, onConfirm, onCancel, }) {
    if (!open)
        return null;
    const confirmColor = VARIANT_COLORS[variant];
    const loadingLabel = confirmLabel.endsWith('e')
        ? confirmLabel.slice(0, -1) + 'ing\u2026'
        : confirmLabel + 'ing\u2026';
    return (_jsx("div", { style: dialog.overlay, onClick: onCancel, children: _jsxs("div", { style: dialogPanel, onClick: e => e.stopPropagation(), children: [_jsxs("div", { style: headerStyle, children: [_jsx("h2", { style: dialog.title, children: title }), _jsx("button", { onClick: onCancel, style: dialog.closeButton, "aria-label": "Close", children: "\u2715" })] }), _jsx("div", { style: bodyStyle, children: typeof message === 'string' ? (_jsx("p", { style: dialog.message, children: message })) : (message) }), _jsxs("div", { style: footerStyle, children: [_jsx("button", { onClick: onCancel, style: dialog.cancelButton, children: cancelLabel }), _jsx("button", { onClick: onConfirm, disabled: loading, style: {
                                ...button.action,
                                backgroundColor: confirmColor,
                                ...(loading ? button.disabled : {}),
                            }, children: loading ? loadingLabel : confirmLabel })] })] }) }));
}
// ---------------------------------------------------------------------------
// Local style overrides (structure differs from shared dialog.* patterns)
// ---------------------------------------------------------------------------
const dialogPanel = {
    ...dialog.panel(440),
    display: 'flex',
    flexDirection: 'column',
};
const headerStyle = {
    ...dialog.header,
    padding: '20px 24px 16px',
};
const bodyStyle = {
    padding: '20px 24px',
};
const footerStyle = {
    ...dialog.footer,
    padding: '16px 24px',
};
//# sourceMappingURL=ConfirmDialog.js.map