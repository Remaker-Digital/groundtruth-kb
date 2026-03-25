import { jsx as _jsx } from "react/jsx-runtime";
import { COLOR_LIGHT_GRAY, COLOR_GRAY, STALENESS_BADGE_STYLES } from './styles';
export const KBStalenessBadge = ({ category }) => {
    if (!category) {
        return (_jsx("span", { style: {
                display: 'inline-block',
                fontSize: '11px',
                fontWeight: 600,
                padding: '2px 8px',
                borderRadius: '10px',
                backgroundColor: COLOR_LIGHT_GRAY,
                color: COLOR_GRAY,
            }, children: "--" }));
    }
    const style = STALENESS_BADGE_STYLES[category] ?? STALENESS_BADGE_STYLES.fresh;
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
//# sourceMappingURL=KBStalenessBadge.js.map