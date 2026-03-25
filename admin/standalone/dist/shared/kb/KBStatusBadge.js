import { jsx as _jsx } from "react/jsx-runtime";
import { STATUS_BADGE_STYLES } from './styles';
export const KBStatusBadge = ({ status, isActive }) => {
    // Backend may return is_active (boolean) instead of status (string).
    // Derive status from is_active if status is missing.
    const effectiveStatus = status ?? (isActive === false ? 'archived' : 'published');
    const style = STATUS_BADGE_STYLES[effectiveStatus] ?? STATUS_BADGE_STYLES.published;
    return (_jsx("span", { style: {
            display: 'inline-block',
            fontSize: '11px',
            fontWeight: 600,
            padding: '2px 8px',
            borderRadius: '10px',
            backgroundColor: style.bg,
            color: style.color,
        }, children: style.label }));
};
//# sourceMappingURL=KBStatusBadge.js.map