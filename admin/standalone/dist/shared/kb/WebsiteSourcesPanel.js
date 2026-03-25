import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
/**
 * WebsiteSourcesPanel — manage automated website crawl sources for knowledge base.
 *
 * Displays a list of website sources with status, crawl stats, and actions.
 * Supports adding new sources, triggering manual re-crawls, pausing/resuming,
 * and deleting sources.
 *
 * Framework-agnostic React component — no Polaris, no Tailwind, pure inline styles.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { useState, useCallback } from 'react';
import { useWebsiteSources, useCreateWebsiteSource, useDeleteWebsiteSource, useTriggerCrawl, useUpdateWebsiteSource, } from '../hooks/useWebsiteSources';
import { HelpTooltip } from '../HelpTooltip';
import { COLOR_SUCCESS, COLOR_DANGER, COLOR_GRAY, COLOR_LIGHT_GRAY, COLOR_BORDER, COLOR_TEXT, COLOR_TEXT_SECONDARY, COLOR_WARNING, inputStyle, buttonStyle, } from './styles';
import { LoadingSpinner } from './LoadingSpinner';
import { EmptyState } from './EmptyState';
import { ErrorBanner } from './ErrorBanner';
// ---------------------------------------------------------------------------
// Status badge styles
// ---------------------------------------------------------------------------
const STATUS_STYLES = {
    pending: { bg: '#fff8c5', color: COLOR_WARNING, label: 'Pending' },
    crawling: { bg: '#dbeafe', color: '#2563eb', label: 'Crawling' },
    active: { bg: '#dcffe4', color: COLOR_SUCCESS, label: 'Active' },
    failed: { bg: '#ffeef0', color: COLOR_DANGER, label: 'Failed' },
    paused: { bg: COLOR_LIGHT_GRAY, color: COLOR_GRAY, label: 'Paused' },
};
function SourceStatusBadge({ status }) {
    const s = STATUS_STYLES[status] ?? STATUS_STYLES.pending;
    return (_jsx("span", { style: {
            display: 'inline-block',
            padding: '2px 10px',
            borderRadius: '10px',
            fontSize: '12px',
            fontWeight: 600,
            backgroundColor: s.bg,
            color: s.color,
        }, children: s.label }));
}
// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function formatRelativeTime(isoStr) {
    if (!isoStr)
        return '\u2014';
    try {
        const d = new Date(isoStr);
        const now = Date.now();
        const diffMs = now - d.getTime();
        if (diffMs < 0) {
            // future
            const mins = Math.round(-diffMs / 60000);
            if (mins < 60)
                return `in ${mins}m`;
            const hrs = Math.round(mins / 60);
            if (hrs < 24)
                return `in ${hrs}h`;
            return `in ${Math.round(hrs / 24)}d`;
        }
        const mins = Math.round(diffMs / 60000);
        if (mins < 1)
            return 'just now';
        if (mins < 60)
            return `${mins}m ago`;
        const hrs = Math.round(mins / 60);
        if (hrs < 24)
            return `${hrs}h ago`;
        return `${Math.round(hrs / 24)}d ago`;
    }
    catch {
        return '\u2014';
    }
}
function formatNumber(n) {
    if (n >= 1000000)
        return `${(n / 1000000).toFixed(1)}M`;
    if (n >= 1000)
        return `${(n / 1000).toFixed(1)}K`;
    return String(n);
}
// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------
export const WebsiteSourcesPanel = ({ apiFetch, onNotify, }) => {
    const { data, loading, error, refetch } = useWebsiteSources(apiFetch);
    const { create, loading: creating, error: createError } = useCreateWebsiteSource(apiFetch);
    const { remove, loading: deleting } = useDeleteWebsiteSource(apiFetch);
    const { trigger, loading: triggering } = useTriggerCrawl(apiFetch);
    const { update, loading: updating } = useUpdateWebsiteSource(apiFetch);
    const [showAddForm, setShowAddForm] = useState(false);
    const [newUrl, setNewUrl] = useState('');
    const [newMaxPages, setNewMaxPages] = useState(25);
    const [newAutoRefresh, setNewAutoRefresh] = useState(true);
    const [newRefreshHours, setNewRefreshHours] = useState(24);
    const [confirmDelete, setConfirmDelete] = useState(null);
    const sources = data?.sources ?? [];
    const handleCreate = useCallback(async () => {
        if (!newUrl.trim())
            return;
        const result = await create({
            startUrl: newUrl.trim(),
            maxPages: newMaxPages,
            autoRefresh: newAutoRefresh,
            refreshIntervalHours: newRefreshHours,
        });
        if (result) {
            onNotify(`Website source added: ${result.domain}`, 'success');
            setNewUrl('');
            setNewMaxPages(25);
            setShowAddForm(false);
            refetch();
        }
        else {
            onNotify(createError || 'Failed to add website source', 'error');
        }
    }, [newUrl, newMaxPages, newAutoRefresh, newRefreshHours, create, createError, onNotify, refetch]);
    const handleDelete = useCallback(async (sourceId) => {
        const result = await remove(sourceId);
        if (result?.success) {
            onNotify(result.message, 'success');
            setConfirmDelete(null);
            refetch();
        }
        else {
            onNotify('Failed to delete website source', 'error');
        }
    }, [remove, onNotify, refetch]);
    const handleTriggerCrawl = useCallback(async (sourceId) => {
        const result = await trigger(sourceId);
        if (result?.success) {
            onNotify(result.message, 'success');
            refetch();
        }
        else {
            onNotify('Failed to trigger crawl', 'error');
        }
    }, [trigger, onNotify, refetch]);
    const handleTogglePause = useCallback(async (source) => {
        const newStatus = source.status === 'paused' ? 'active' : 'paused';
        const result = await update(source.id, { status: newStatus });
        if (result) {
            onNotify(`Source ${newStatus === 'paused' ? 'paused' : 'resumed'}: ${source.domain}`, 'success');
            refetch();
        }
        else {
            onNotify('Failed to update source', 'error');
        }
    }, [update, onNotify, refetch]);
    return (_jsxs("div", { children: [_jsxs("div", { style: {
                    padding: '16px 20px',
                    borderBottom: `1px solid ${COLOR_BORDER}`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                }, children: [_jsxs("div", { children: [_jsxs("h2", { style: { margin: 0, fontSize: '18px', fontWeight: 600, color: COLOR_TEXT }, children: ["Website Sources", _jsx(HelpTooltip, { text: "Add your website URL and Agent Red will automatically crawl it to build your knowledge base. Pages are re-crawled on a schedule to keep content fresh.", docLink: "https://agentredcx.com/docs/admin-guide/website-sources" })] }), _jsxs("span", { style: { fontSize: '13px', color: COLOR_TEXT_SECONDARY }, children: [sources.length, " source", sources.length !== 1 ? 's' : ''] })] }), _jsx("button", { onClick: () => setShowAddForm(!showAddForm), style: buttonStyle('primary'), children: "+ Add Website" })] }), showAddForm && (_jsxs("div", { style: {
                    padding: '16px 20px',
                    borderBottom: `1px solid ${COLOR_BORDER}`,
                    backgroundColor: COLOR_LIGHT_GRAY,
                }, children: [_jsxs("div", { style: { display: 'flex', gap: '12px', alignItems: 'flex-end', flexWrap: 'wrap' }, children: [_jsxs("div", { style: { flex: 1, minWidth: '300px' }, children: [_jsx("label", { style: { fontSize: '12px', fontWeight: 600, color: COLOR_TEXT_SECONDARY, display: 'block', marginBottom: '4px' }, children: "Website URL" }), _jsx("input", { type: "url", value: newUrl, onChange: (e) => setNewUrl(e.target.value), placeholder: "https://example.com", style: inputStyle(), onKeyDown: (e) => e.key === 'Enter' && handleCreate() })] }), _jsxs("div", { style: { width: '100px' }, children: [_jsx("label", { style: { fontSize: '12px', fontWeight: 600, color: COLOR_TEXT_SECONDARY, display: 'block', marginBottom: '4px' }, children: "Max pages" }), _jsx("input", { type: "number", value: newMaxPages, onChange: (e) => setNewMaxPages(Math.max(1, Math.min(100, parseInt(e.target.value) || 25))), min: 1, max: 100, style: inputStyle() })] }), _jsxs("div", { style: { width: '120px' }, children: [_jsx("label", { style: { fontSize: '12px', fontWeight: 600, color: COLOR_TEXT_SECONDARY, display: 'block', marginBottom: '4px' }, children: "Refresh interval" }), _jsxs("select", { value: newRefreshHours, onChange: (e) => setNewRefreshHours(parseInt(e.target.value)), style: inputStyle(), children: [_jsx("option", { value: 6, children: "Every 6h" }), _jsx("option", { value: 12, children: "Every 12h" }), _jsx("option", { value: 24, children: "Every 24h" }), _jsx("option", { value: 48, children: "Every 2 days" }), _jsx("option", { value: 168, children: "Weekly" })] })] }), _jsxs("div", { style: { display: 'flex', alignItems: 'center', gap: '6px', paddingBottom: '2px' }, children: [_jsx("input", { type: "checkbox", checked: newAutoRefresh, onChange: (e) => setNewAutoRefresh(e.target.checked), id: "auto-refresh-toggle" }), _jsx("label", { htmlFor: "auto-refresh-toggle", style: { fontSize: '13px', color: COLOR_TEXT_SECONDARY, cursor: 'pointer' }, children: "Auto-refresh" })] }), _jsxs("div", { style: { display: 'flex', gap: '8px' }, children: [_jsx("button", { onClick: handleCreate, disabled: creating || !newUrl.trim(), style: buttonStyle('primary', creating || !newUrl.trim()), children: creating ? 'Adding...' : 'Add & Crawl' }), _jsx("button", { onClick: () => { setShowAddForm(false); setNewUrl(''); }, style: buttonStyle('secondary'), children: "Cancel" })] })] }), createError && (_jsx("div", { style: { fontSize: '13px', color: COLOR_DANGER, marginTop: '8px' }, children: createError }))] })), loading && sources.length === 0 && (_jsx(LoadingSpinner, { text: "Loading website sources..." })), error && sources.length === 0 && (_jsx(ErrorBanner, { message: error, onRetry: refetch })), !loading && !error && sources.length === 0 && !showAddForm && (_jsx(EmptyState, { icon: String.fromCodePoint(0x1F310), title: "No website sources", subtitle: "Add your website URL to automatically crawl and import content into your knowledge base." })), sources.length > 0 && (_jsx("div", { style: { overflowX: 'auto' }, children: _jsxs("table", { style: {
                        width: '100%',
                        borderCollapse: 'collapse',
                        fontSize: '14px',
                    }, children: [_jsx("thead", { children: _jsx("tr", { style: { backgroundColor: COLOR_LIGHT_GRAY }, children: ['Domain', 'Status', 'Pages', 'Articles', 'Last crawled', 'Next crawl', 'Actions'].map((h) => (_jsx("th", { style: {
                                        padding: '10px 16px',
                                        textAlign: 'left',
                                        fontSize: '12px',
                                        fontWeight: 600,
                                        color: COLOR_TEXT_SECONDARY,
                                        borderBottom: `1px solid ${COLOR_BORDER}`,
                                        textTransform: 'uppercase',
                                        letterSpacing: '0.5px',
                                        whiteSpace: 'nowrap',
                                    }, children: h }, h))) }) }), _jsx("tbody", { children: sources.map((source) => (_jsxs("tr", { style: { borderBottom: `1px solid ${COLOR_BORDER}` }, children: [_jsxs("td", { style: { padding: '12px 16px' }, children: [_jsx("div", { style: { fontWeight: 500, color: COLOR_TEXT }, children: source.domain }), _jsx("div", { style: { fontSize: '12px', color: COLOR_TEXT_SECONDARY, marginTop: '2px' }, children: source.startUrl.length > 60 ? source.startUrl.slice(0, 57) + '...' : source.startUrl }), source.errorMessage && (_jsx("div", { style: { fontSize: '11px', color: COLOR_DANGER, marginTop: '4px' }, children: source.errorMessage.length > 80 ? source.errorMessage.slice(0, 77) + '...' : source.errorMessage }))] }), _jsx("td", { style: { padding: '12px 16px' }, children: _jsx(SourceStatusBadge, { status: source.status }) }), _jsxs("td", { style: { padding: '12px 16px', fontSize: '13px', color: COLOR_TEXT }, children: [source.pagesCrawled, "/", source.maxPages, _jsxs("div", { style: { fontSize: '11px', color: COLOR_TEXT_SECONDARY }, children: [formatNumber(source.totalChars), " chars"] })] }), _jsx("td", { style: { padding: '12px 16px', fontSize: '13px', color: COLOR_TEXT }, children: source.articlesCreated }), _jsx("td", { style: { padding: '12px 16px', fontSize: '13px', color: COLOR_TEXT_SECONDARY }, children: formatRelativeTime(source.lastCrawledAt) }), _jsx("td", { style: { padding: '12px 16px', fontSize: '13px', color: COLOR_TEXT_SECONDARY }, children: source.autoRefresh ? formatRelativeTime(source.nextCrawlAt) : 'Manual' }), _jsx("td", { style: { padding: '12px 16px' }, children: _jsxs("div", { style: { display: 'flex', gap: '6px', flexWrap: 'nowrap' }, children: [_jsx("button", { onClick: () => handleTriggerCrawl(source.id), disabled: triggering || source.status === 'crawling', style: {
                                                        ...buttonStyle('secondary', triggering || source.status === 'crawling'),
                                                        padding: '4px 10px',
                                                        fontSize: '12px',
                                                    }, title: "Trigger re-crawl", children: source.status === 'crawling' ? 'Crawling...' : 'Re-crawl' }), _jsx("button", { onClick: () => handleTogglePause(source), disabled: updating || source.status === 'crawling', style: {
                                                        ...buttonStyle('secondary', updating || source.status === 'crawling'),
                                                        padding: '4px 10px',
                                                        fontSize: '12px',
                                                    }, title: source.status === 'paused' ? 'Resume auto-refresh' : 'Pause auto-refresh', children: source.status === 'paused' ? 'Resume' : 'Pause' }), confirmDelete === source.id ? (_jsxs(_Fragment, { children: [_jsx("button", { onClick: () => handleDelete(source.id), disabled: deleting, style: {
                                                                ...buttonStyle('danger', deleting),
                                                                padding: '4px 10px',
                                                                fontSize: '12px',
                                                            }, children: "Confirm" }), _jsx("button", { onClick: () => setConfirmDelete(null), style: {
                                                                ...buttonStyle('secondary'),
                                                                padding: '4px 10px',
                                                                fontSize: '12px',
                                                            }, children: "Cancel" })] })) : (_jsx("button", { onClick: () => setConfirmDelete(source.id), style: {
                                                        ...buttonStyle('secondary'),
                                                        padding: '4px 10px',
                                                        fontSize: '12px',
                                                        color: COLOR_DANGER,
                                                    }, title: "Delete source and its KB entries", children: "Delete" }))] }) })] }, source.id))) })] }) }))] }));
};
export default WebsiteSourcesPanel;
//# sourceMappingURL=WebsiteSourcesPanel.js.map