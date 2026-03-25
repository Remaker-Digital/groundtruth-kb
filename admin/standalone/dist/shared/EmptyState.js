import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { tokens } from './theme/styles';
const styles = {
    container: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '48px 24px',
        textAlign: 'center',
        color: tokens.textMuted,
    },
    iconWrapper: {
        marginBottom: '16px',
        color: tokens.textTertiary,
    },
    title: {
        fontSize: '15px',
        fontWeight: 600,
        color: tokens.textSecondary,
        marginBottom: '6px',
        lineHeight: 1.4,
    },
    subtitle: {
        fontSize: '13px',
        color: tokens.textMuted,
        maxWidth: '360px',
        lineHeight: 1.5,
    },
    actionButton: {
        marginTop: '16px',
        padding: '8px 16px',
        fontSize: '13px',
        fontWeight: 500,
        borderRadius: '6px',
    },
};
export const EmptyState = ({ icon, title, subtitle, action }) => (_jsxs("div", { style: styles.container, role: "status", "aria-label": title, children: [_jsx("div", { style: styles.iconWrapper, children: icon }), _jsx("div", { style: styles.title, children: title }), subtitle && _jsx("div", { style: styles.subtitle, children: subtitle }), action && (_jsx("button", { type: "button", className: "ar-btn-action ar-opacity-hover", style: styles.actionButton, onClick: action.onClick, children: action.label }))] }));
export default EmptyState;
//# sourceMappingURL=EmptyState.js.map