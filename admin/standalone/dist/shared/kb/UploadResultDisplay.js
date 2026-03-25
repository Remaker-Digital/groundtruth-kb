import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { COLOR_SUCCESS, COLOR_TEXT, COLOR_TEXT_SECONDARY, BORDER_RADIUS, buttonStyle } from './styles';
export const UploadResultDisplay = ({ result, onDone }) => (_jsxs("div", { style: {
        padding: '24px', backgroundColor: '#dcffe4', border: `1px solid ${COLOR_SUCCESS}33`,
        borderRadius: BORDER_RADIUS, textAlign: 'center',
    }, children: [_jsx("div", { style: { fontSize: '32px', marginBottom: '8px' }, children: String.fromCodePoint(0x2705) }), _jsx("div", { style: { fontSize: '15px', fontWeight: 600, color: COLOR_TEXT, marginBottom: '4px' }, children: "Import Successful" }), _jsxs("div", { style: { fontSize: '13px', color: COLOR_TEXT_SECONDARY, marginBottom: '16px' }, children: ["Created ", result.entries_created, " ", result.entries_created === 1 ? 'entry' : 'entries', " from", ' ', result.source_filename || result.source_url || 'document', ' ', "(", Math.round(result.total_chars / 1000), "K characters)"] }), _jsx("button", { onClick: onDone, style: buttonStyle('primary'), children: "Back to Knowledge Base" })] }));
//# sourceMappingURL=UploadResultDisplay.js.map