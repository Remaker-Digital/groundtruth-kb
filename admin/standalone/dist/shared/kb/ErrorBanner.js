import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { COLOR_DANGER, BORDER_RADIUS, FONT_FAMILY } from './styles';
export const ErrorBanner = ({ message, onRetry }) => (_jsxs("div", { style: {
        padding: '12px 16px',
        backgroundColor: '#ffeef0',
        border: `1px solid ${COLOR_DANGER}33`,
        borderRadius: BORDER_RADIUS,
        margin: '16px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '12px',
    }, children: [_jsx("span", { style: { fontSize: '13px', color: COLOR_DANGER }, children: message }), onRetry && (_jsx("button", { onClick: onRetry, style: {
                padding: '4px 12px',
                border: `1px solid ${COLOR_DANGER}`,
                borderRadius: BORDER_RADIUS,
                backgroundColor: 'transparent',
                color: COLOR_DANGER,
                fontSize: '12px',
                fontFamily: FONT_FAMILY,
                cursor: 'pointer',
                whiteSpace: 'nowrap',
            }, children: "Retry" }))] }));
//# sourceMappingURL=ErrorBanner.js.map