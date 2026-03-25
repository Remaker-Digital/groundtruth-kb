import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { ROLES, getRoleColors } from './constants';
export const RoleTooltip = ({ isDark, onMouseEnter, onMouseLeave, }) => {
    const roleColors = getRoleColors(isDark);
    return (_jsxs("div", { style: {
            position: 'absolute',
            top: '100%',
            left: '50%',
            transform: 'translateX(-50%)',
            marginTop: 8,
            background: '#1f2937',
            color: '#f9fafb',
            fontSize: 12,
            lineHeight: 1.5,
            padding: '12px 16px',
            borderRadius: 8,
            width: 340,
            maxWidth: 380,
            zIndex: 9999,
            boxShadow: '0 4px 16px rgba(0,0,0,0.3)',
            pointerEvents: 'auto',
        }, onMouseEnter: onMouseEnter, onMouseLeave: onMouseLeave, children: [_jsx("span", { style: {
                    position: 'absolute',
                    bottom: '100%',
                    left: '50%',
                    transform: 'translateX(-50%)',
                    width: 0,
                    height: 0,
                    borderLeft: '6px solid transparent',
                    borderRight: '6px solid transparent',
                    borderBottom: '6px solid #1f2937',
                } }), _jsx("div", { style: { fontWeight: 600, fontSize: 13, marginBottom: 10 }, children: "Role permissions" }), _jsx("table", { style: { width: '100%', borderCollapse: 'collapse' }, children: _jsx("tbody", { children: ROLES.map((role) => (_jsxs("tr", { children: [_jsx("td", { style: { padding: '6px 12px 6px 0', verticalAlign: 'top', whiteSpace: 'nowrap' }, children: _jsx("span", { style: {
                                        display: 'inline-block',
                                        padding: '1px 8px',
                                        borderRadius: 10,
                                        fontSize: 11,
                                        fontWeight: 600,
                                        background: (roleColors[role.value] || roleColors.viewer).bg,
                                        color: (roleColors[role.value] || roleColors.viewer).text,
                                    }, children: role.label }) }), _jsx("td", { style: {
                                    padding: '6px 0',
                                    fontSize: 11,
                                    color: '#d1d5db',
                                    verticalAlign: 'top',
                                    textTransform: 'none',
                                    letterSpacing: 'normal',
                                    fontWeight: 400,
                                }, children: role.description })] }, role.value))) }) })] }));
};
//# sourceMappingURL=RoleTooltip.js.map