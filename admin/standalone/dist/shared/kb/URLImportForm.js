import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * URLImportForm — form for importing KB content from a website URL,
 * with optional site-crawl mode.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { useState, useCallback } from 'react';
import { HelpTooltip } from '../HelpTooltip';
import { BRAND_PRIMARY, COLOR_TEXT, COLOR_TEXT_SECONDARY, COLOR_DANGER, BORDER_RADIUS, inputStyle, buttonStyle, } from './styles';
export const URLImportForm = ({ onImport, importing, error }) => {
    const [url, setUrl] = useState('');
    const [crawl, setCrawl] = useState(false);
    const [maxPages, setMaxPages] = useState(10);
    const handleSubmit = useCallback(() => {
        const trimmed = url.trim();
        if (!trimmed)
            return;
        onImport(trimmed, crawl, maxPages);
    }, [url, crawl, maxPages, onImport]);
    return (_jsxs("div", { children: [_jsx("label", { style: { display: 'block', fontSize: '13px', fontWeight: 600, color: COLOR_TEXT, marginBottom: '6px' }, children: "Website URL" }), _jsxs("div", { style: { display: 'flex', gap: '8px' }, children: [_jsx("input", { type: "url", value: url, onChange: (e) => setUrl(e.target.value), placeholder: "https://example.com/faq", style: inputStyle({ flex: '1' }), disabled: importing }), _jsx("button", { onClick: handleSubmit, disabled: !url.trim() || importing, style: buttonStyle('primary', !url.trim() || importing), children: importing ? 'Importing...' : 'Import' })] }), _jsxs("div", { style: { marginTop: '12px', display: 'flex', gap: '16px', alignItems: 'center' }, children: [_jsxs("label", { style: { display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', color: COLOR_TEXT, cursor: 'pointer' }, children: [_jsx("input", { type: "radio", name: "crawl_mode", checked: !crawl, onChange: () => setCrawl(false), disabled: importing, style: { accentColor: BRAND_PRIMARY } }), "Single page"] }), _jsxs("label", { style: { display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', color: COLOR_TEXT, cursor: 'pointer' }, children: [_jsx("input", { type: "radio", name: "crawl_mode", checked: crawl, onChange: () => setCrawl(true), disabled: importing, style: { accentColor: BRAND_PRIMARY } }), "Crawl site", _jsx(HelpTooltip, { text: "Follow links on the same domain and import multiple pages automatically.", docLink: "https://agentredcx.com/docs/admin-guide/knowledge-base-management#uploading-documents" })] }), crawl && (_jsxs("div", { style: { display: 'flex', alignItems: 'center', gap: '6px' }, children: [_jsx("label", { style: { fontSize: '12px', color: COLOR_TEXT_SECONDARY, whiteSpace: 'nowrap' }, children: "Max pages:" }), _jsx("input", { type: "number", value: maxPages, onChange: (e) => {
                                    const v = parseInt(e.target.value, 10);
                                    if (!isNaN(v))
                                        setMaxPages(Math.max(1, Math.min(50, v)));
                                }, min: 1, max: 50, disabled: importing, style: inputStyle({ width: '70px', padding: '4px 8px', fontSize: '13px' }) })] }))] }), _jsx("span", { style: { display: 'block', fontSize: '12px', color: COLOR_TEXT_SECONDARY, marginTop: '8px' }, children: crawl
                    ? `We'll follow same-domain links and import up to ${maxPages} pages.`
                    : "We'll extract text content from the page and create knowledge base entries." }), error && (_jsx("div", { style: {
                    marginTop: '8px', padding: '8px 12px', backgroundColor: '#ffeef0',
                    border: `1px solid ${COLOR_DANGER}33`, borderRadius: BORDER_RADIUS,
                    fontSize: '13px', color: COLOR_DANGER,
                }, children: error }))] }));
};
//# sourceMappingURL=URLImportForm.js.map