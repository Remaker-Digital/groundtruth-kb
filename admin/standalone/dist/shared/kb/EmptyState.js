import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { COLOR_TEXT, COLOR_TEXT_SECONDARY } from './styles';
export const EmptyState = ({ icon, title, subtitle }) => (_jsxs("div", { style: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '48px 16px',
        color: COLOR_TEXT_SECONDARY,
    }, children: [_jsx("span", { style: { fontSize: '40px', marginBottom: '12px' }, children: icon }), _jsx("span", { style: { fontSize: '15px', fontWeight: 600, color: COLOR_TEXT, marginBottom: '4px' }, children: title }), subtitle && _jsx("span", { style: { fontSize: '13px' }, children: subtitle })] }));
//# sourceMappingURL=EmptyState.js.map