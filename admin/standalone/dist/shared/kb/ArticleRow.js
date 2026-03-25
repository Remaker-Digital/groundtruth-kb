import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { KBStatusBadge } from './KBStatusBadge';
import { KBStalenessBadge } from './KBStalenessBadge';
import { formatDate } from './utils';
import { COLOR_LIGHT_GRAY, COLOR_BORDER, COLOR_TEXT, COLOR_TEXT_SECONDARY, COLOR_SUCCESS, BORDER_RADIUS, FONT_FAMILY, } from './styles';
export const ArticleRow = ({ article, onClick, onVerify, verifying }) => (_jsxs("tr", { onClick: onClick, className: "ar-row-hoverable-light", style: { cursor: 'pointer' }, children: [_jsx("td", { style: { padding: '12px 16px', borderBottom: `1px solid ${COLOR_BORDER}` }, children: _jsx("span", { style: { fontSize: '14px', fontWeight: 500, color: COLOR_TEXT }, children: article.title }) }), _jsx("td", { style: { padding: '12px 16px', borderBottom: `1px solid ${COLOR_BORDER}` }, children: _jsx("span", { style: {
                    fontSize: '12px',
                    color: COLOR_TEXT_SECONDARY,
                    backgroundColor: COLOR_LIGHT_GRAY,
                    padding: '2px 8px',
                    borderRadius: '10px',
                }, children: article.category || 'Uncategorized' }) }), _jsx("td", { style: { padding: '12px 16px', borderBottom: `1px solid ${COLOR_BORDER}` }, children: _jsx(KBStatusBadge, { status: article.status, isActive: article.is_active }) }), _jsx("td", { style: { padding: '12px 16px', borderBottom: `1px solid ${COLOR_BORDER}` }, children: _jsx(KBStalenessBadge, { category: article.stalenessCategory }) }), _jsx("td", { style: {
                padding: '12px 16px',
                borderBottom: `1px solid ${COLOR_BORDER}`,
                fontSize: '13px',
                color: COLOR_TEXT_SECONDARY,
            }, children: formatDate(article.updatedAt) }), _jsx("td", { style: {
                padding: '12px 16px',
                borderBottom: `1px solid ${COLOR_BORDER}`,
            }, children: onVerify && (article.stalenessCategory === 'stale' || article.stalenessCategory === 'aging' || article.stalenessCategory === 'very_stale') && (_jsx("button", { onClick: (e) => {
                    e.stopPropagation();
                    onVerify(article.id);
                }, disabled: verifying, style: {
                    padding: '4px 10px',
                    border: `1px solid ${COLOR_SUCCESS}`,
                    borderRadius: BORDER_RADIUS,
                    backgroundColor: 'transparent',
                    color: COLOR_SUCCESS,
                    fontSize: '11px',
                    fontFamily: FONT_FAMILY,
                    fontWeight: 500,
                    cursor: verifying ? 'not-allowed' : 'pointer',
                    opacity: verifying ? 0.6 : 1,
                    whiteSpace: 'nowrap',
                }, children: verifying ? 'Verifying...' : 'Verify' })) })] }));
//# sourceMappingURL=ArticleRow.js.map