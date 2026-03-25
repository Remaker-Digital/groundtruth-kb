import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { COLOR_TEXT_SECONDARY, COLOR_BORDER, BRAND_PRIMARY } from './styles';
export const LoadingSpinner = ({ text = 'Loading...' }) => (_jsxs("div", { style: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '48px 16px',
        color: COLOR_TEXT_SECONDARY,
    }, children: [_jsx("div", { style: {
                width: '32px',
                height: '32px',
                border: `3px solid ${COLOR_BORDER}`,
                borderTopColor: BRAND_PRIMARY,
                borderRadius: '50%',
                animation: 'kbSpin 0.8s linear infinite',
                marginBottom: '12px',
            } }), _jsx("span", { style: { fontSize: '14px' }, children: text }), _jsx("style", { children: `@keyframes kbSpin { to { transform: rotate(360deg); } }` })] }));
//# sourceMappingURL=LoadingSpinner.js.map