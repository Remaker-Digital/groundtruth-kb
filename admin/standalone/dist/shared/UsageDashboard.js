import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
/**
 * UsageDashboard — Real-time billing usage dashboard.
 *
 * Three-section layout providing full billing transparency (Decision #25):
 *
 *   1. **Top — Usage Summary:**  Meter gauge (used / total included allowance),
 *      pack balance, overage estimate, and active billing alerts.
 *
 *   2. **Middle — Daily Volume Chart:**  Simple CSS bar chart built from
 *      useDailyVolume data showing total vs billable conversations per day.
 *
 *   3. **Bottom — Conversation List:**  Paginated table of billable
 *      conversations with CSV export.
 *
 * API endpoints consumed:
 *   GET /api/dashboard/usage                — Usage summary (Layer 1)
 *   GET /api/dashboard/usage/daily          — Daily volume (Layer 1)
 *   GET /api/dashboard/conversations        — Paginated conversation list (Layer 2)
 *   GET /api/dashboard/conversations/export — CSV download (Layer 2)
 *
 * Props (from shell):
 *   - tenantContext — authenticated tenant information
 *   - apiFetch     — shell-provided fetch wrapper with auth
 *   - onNotify     — shell toast/banner callback
 *
 * Dependencies:
 *   - ../types  — BaseComponentProps, UsageDashboard, DailyVolume,
 *                  ConversationSummary, PaginatedList
 *   - ../hooks  — useUsageDashboard, useDailyVolume, useConversationList
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { useState, useCallback, useMemo } from 'react';
import { useUsageDashboard, useDailyVolume, useConversationList } from './hooks';
import { HelpTooltip } from './HelpTooltip';
import { tokens } from './theme/styles';
// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------
const PAGE_SIZE = 50;
// Generate billing period options for the dropdown (current + past 5 months)
function getBillingPeriodOptions() {
    const options = [];
    const now = new Date();
    for (let i = 0; i < 6; i++) {
        const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
        const value = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
        const label = d.toLocaleDateString(undefined, { month: 'long', year: 'numeric' });
        options.push({ value, label });
    }
    return options;
}
// ---------------------------------------------------------------------------
// Styles
// ---------------------------------------------------------------------------
const st = {
    container: {
        fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
        color: '#1a1a1a',
    },
    header: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginBottom: 28,
        flexWrap: 'wrap',
        gap: 12,
    },
    title: {
        fontSize: 24,
        fontWeight: 600,
        margin: 0,
    },
    subtitle: {
        fontSize: 13,
        color: '#888',
        margin: '4px 0 0 0',
    },
    periodSelect: {
        padding: '8px 12px',
        fontSize: 14,
        border: '1px solid #d0d0d0',
        borderRadius: 6,
        backgroundColor: '#fff',
        color: '#1a1a1a',
        outline: 'none',
    },
    // -- Section wrappers --
    section: {
        marginBottom: 32,
    },
    sectionTitle: {
        fontSize: 16,
        fontWeight: 600,
        color: '#1a1a1a',
        margin: '0 0 16px 0',
    },
    // -- Summary cards --
    cardsRow: {
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
        gap: 16,
        marginBottom: 20,
    },
    card: {
        padding: '16px 20px',
        backgroundColor: '#fafafa',
        border: '1px solid #e5e5e5',
        borderRadius: 8,
    },
    cardLabel: {
        fontSize: 12,
        fontWeight: 500,
        color: '#888',
        textTransform: 'uppercase',
        letterSpacing: '0.5px',
        margin: '0 0 6px 0',
    },
    cardValue: {
        fontSize: 28,
        fontWeight: 700,
        color: '#1a1a1a',
        margin: 0,
        lineHeight: 1.1,
    },
    cardSub: {
        fontSize: 12,
        color: '#888',
        margin: '4px 0 0 0',
    },
    // -- Meter --
    meterContainer: {
        marginBottom: 20,
        padding: '16px 20px',
        backgroundColor: '#fafafa',
        border: '1px solid #e5e5e5',
        borderRadius: 8,
    },
    meterLabel: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'baseline',
        marginBottom: 8,
    },
    meterTrack: {
        height: 12,
        backgroundColor: '#e5e5e5',
        borderRadius: 6,
        overflow: 'hidden',
        position: 'relative',
    },
    meterFill: (percent, isOverage) => ({
        height: '100%',
        width: `${Math.min(percent, 100)}%`,
        backgroundColor: isOverage ? tokens.brand : percent > 80 ? '#f59e0b' : '#16a34a',
        borderRadius: 6,
        transition: 'width 0.4s ease, background-color 0.3s ease',
    }),
    meterOverflow: (overflowPercent) => ({
        position: 'absolute',
        top: 0,
        right: 0,
        height: '100%',
        width: `${Math.min(overflowPercent, 20)}%`,
        backgroundColor: tokens.brand,
        opacity: 0.3,
        borderRadius: '0 6px 6px 0',
    }),
    // -- Alerts --
    alertsContainer: {
        display: 'flex',
        flexDirection: 'column',
        gap: 8,
    },
    alertItem: {
        display: 'flex',
        alignItems: 'center',
        gap: 8,
        padding: '10px 14px',
        backgroundColor: '#fef3c7',
        border: '1px solid #fde68a',
        borderRadius: 6,
        fontSize: 13,
        color: '#92400e',
    },
    alertIcon: {
        fontSize: 16,
        flexShrink: 0,
    },
    // -- Bar chart --
    chartContainer: {
        overflowX: 'auto',
    },
    chartInner: {
        display: 'flex',
        alignItems: 'flex-end',
        gap: 4,
        minHeight: 160,
        padding: '8px 0 0 0',
    },
    chartColumn: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        flex: '1 0 28px',
        minWidth: 28,
        maxWidth: 48,
    },
    barGroup: {
        display: 'flex',
        gap: 2,
        alignItems: 'flex-end',
        width: '100%',
        justifyContent: 'center',
    },
    bar: (height, color) => ({
        width: 10,
        height: Math.max(height, 2),
        backgroundColor: color,
        borderRadius: '3px 3px 0 0',
        transition: 'height 0.3s ease',
    }),
    chartLabel: {
        fontSize: 10,
        color: '#888',
        marginTop: 6,
        textAlign: 'center',
        whiteSpace: 'nowrap',
    },
    chartLegend: {
        display: 'flex',
        gap: 16,
        marginTop: 12,
        fontSize: 12,
        color: '#666',
    },
    legendDot: (color) => ({
        display: 'inline-block',
        width: 10,
        height: 10,
        borderRadius: '50%',
        backgroundColor: color,
        marginRight: 6,
    }),
    // -- Conversation table --
    tableWrapper: {
        overflowX: 'auto',
        border: '1px solid #e5e5e5',
        borderRadius: 8,
    },
    table: {
        width: '100%',
        borderCollapse: 'collapse',
        fontSize: 13,
    },
    th: {
        textAlign: 'left',
        padding: '10px 12px',
        backgroundColor: '#fafafa',
        borderBottom: '1px solid #e5e5e5',
        fontWeight: 600,
        color: '#555',
        fontSize: 12,
        textTransform: 'uppercase',
        letterSpacing: '0.3px',
        whiteSpace: 'nowrap',
    },
    td: {
        padding: '10px 12px',
        borderBottom: '1px solid #f0f0f0',
        color: '#333',
        whiteSpace: 'nowrap',
    },
    statusBadge: (isBillable) => ({
        display: 'inline-block',
        padding: '2px 8px',
        borderRadius: 4,
        fontSize: 11,
        fontWeight: 600,
        backgroundColor: isBillable ? '#fef2f2' : '#f0fdf4',
        color: isBillable ? '#991b1b' : '#166534',
    }),
    criticBadge: (passed) => ({
        display: 'inline-block',
        padding: '2px 8px',
        borderRadius: 4,
        fontSize: 11,
        fontWeight: 600,
        backgroundColor: passed === null ? '#fafaf9' : passed ? '#f0fdf4' : '#fef2f2',
        color: passed === null ? '#888' : passed ? '#166534' : '#991b1b',
    }),
    // -- Pagination --
    pagination: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginTop: 16,
        flexWrap: 'wrap',
        gap: 12,
    },
    pageInfo: {
        fontSize: 13,
        color: '#888',
    },
    pageButtons: {
        display: 'flex',
        gap: 8,
    },
    pageBtn: (disabled) => ({
        padding: '6px 14px',
        fontSize: 13,
        fontWeight: 500,
        backgroundColor: 'transparent',
        color: disabled ? '#ccc' : '#555',
        border: `1px solid ${disabled ? '#eee' : '#d0d0d0'}`,
        borderRadius: 6,
        cursor: disabled ? 'not-allowed' : 'pointer',
    }),
    // -- Export button --
    exportBtn: {
        padding: '8px 16px',
        fontSize: 13,
        fontWeight: 500,
        backgroundColor: 'transparent',
        color: '#555',
        border: '1px solid #d0d0d0',
        borderRadius: 6,
        cursor: 'pointer',
    },
    // -- States --
    loading: {
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        padding: 64,
        fontSize: 14,
        color: '#888',
    },
    error: {
        padding: '16px 20px',
        backgroundColor: '#fef2f2',
        border: '1px solid #fecaca',
        borderRadius: 8,
        color: '#991b1b',
        fontSize: 14,
        lineHeight: 1.5,
    },
    empty: {
        padding: '32px 20px',
        textAlign: 'center',
        color: '#888',
        fontSize: 14,
    },
    btnSecondary: {
        padding: '8px 20px',
        fontSize: 14,
        fontWeight: 500,
        backgroundColor: 'transparent',
        color: '#555',
        border: '1px solid #d0d0d0',
        borderRadius: 6,
        cursor: 'pointer',
    },
    tableHeaderRow: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 12,
    },
};
// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function formatNumber(n) {
    if (n == null)
        return '0';
    return n.toLocaleString(undefined, { maximumFractionDigits: 0 });
}
function formatCurrency(n) {
    if (n == null)
        return '$0.00';
    return `$${n.toFixed(2)}`;
}
function formatShortDate(iso) {
    try {
        const d = new Date(iso);
        return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
    }
    catch {
        return iso;
    }
}
function formatDateTime(iso) {
    if (!iso)
        return '--';
    try {
        const d = new Date(iso);
        return d.toLocaleDateString(undefined, {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
    }
    catch {
        return iso;
    }
}
const UsageMeter = ({ usage }) => {
    const percent = usage.includedAllowance > 0
        ? (usage.totalConversations / usage.includedAllowance) * 100
        : 0;
    const isOverage = usage.totalConversations > usage.includedAllowance;
    const overflowPercent = isOverage
        ? ((usage.totalConversations - usage.includedAllowance) / usage.includedAllowance) * 100
        : 0;
    return (_jsxs("div", { style: st.meterContainer, children: [_jsxs("div", { style: st.meterLabel, children: [_jsxs("div", { children: [_jsx("span", { style: { fontSize: 14, fontWeight: 600, color: '#1a1a1a' }, children: "Conversations Used" }), _jsxs("span", { style: { fontSize: 13, color: '#888', marginLeft: 8 }, children: [formatNumber(usage.totalConversations), " of", ' ', formatNumber(usage.includedAllowance), " included"] })] }), _jsxs("span", { style: {
                            fontSize: 14,
                            fontWeight: 600,
                            color: isOverage ? tokens.brand : percent > 80 ? '#f59e0b' : '#16a34a',
                        }, children: [(percent ?? 0).toFixed(0), "%"] })] }), _jsxs("div", { style: st.meterTrack, children: [_jsx("div", { style: st.meterFill(percent, isOverage) }), isOverage && _jsx("div", { style: st.meterOverflow(overflowPercent) })] }), isOverage && (_jsxs("div", { style: {
                    fontSize: 12,
                    color: tokens.brand,
                    marginTop: 8,
                    fontWeight: 500,
                }, children: [formatNumber(usage.overageConversations), " overage conversation", usage.overageConversations === 1 ? '' : 's', " \u00B7 Estimated cost: ", formatCurrency(usage.estimatedOverageCost), _jsx(HelpTooltip, { text: "Projected cost for overage conversations at your tier's per-conversation rate.", docLink: "https://agentredcx.com/docs/billing/overview#how-conversations-are-billed" })] }))] }));
};
const SummaryCards = ({ usage }) => (_jsxs("div", { style: st.cardsRow, children: [_jsxs("div", { style: st.card, children: [_jsxs("p", { style: st.cardLabel, children: ["Remaining included", _jsx(HelpTooltip, { text: "Conversations used from your plan's included monthly allowance.", docLink: "https://agentredcx.com/docs/billing/overview#how-conversations-are-billed" })] }), _jsx("p", { style: st.cardValue, children: formatNumber(usage.remainingIncluded) }), _jsxs("p", { style: st.cardSub, children: ["of ", formatNumber(usage.includedAllowance)] })] }), _jsxs("div", { style: st.card, children: [_jsxs("p", { style: st.cardLabel, children: ["Pack balance", _jsx(HelpTooltip, { text: "Remaining pre-purchased conversation credits (FIFO, 90-day validity).", docLink: "https://agentredcx.com/docs/billing/overview#conversation-packs" })] }), _jsx("p", { style: st.cardValue, children: formatNumber(usage.packBalance) }), _jsx("p", { style: st.cardSub, children: "pre-purchased conversations" })] }), _jsxs("div", { style: st.card, children: [_jsxs("p", { style: st.cardLabel, children: ["Overage", _jsx(HelpTooltip, { text: "Conversations beyond your included allowance and pack balance, billed at your tier's overage rate.", docLink: "https://agentredcx.com/docs/billing/overview#how-conversations-are-billed" })] }), _jsx("p", { style: {
                        ...st.cardValue,
                        color: usage.overageConversations > 0 ? tokens.brand : '#1a1a1a',
                    }, children: formatNumber(usage.overageConversations) }), _jsx("p", { style: st.cardSub, children: usage.overageConversations > 0
                        ? formatCurrency(usage.estimatedOverageCost)
                        : 'no overage' })] }), _jsxs("div", { style: st.card, children: [_jsx("p", { style: st.cardLabel, children: "Overage reported" }), _jsx("p", { style: st.cardValue, children: formatNumber(usage.overageReported) }), _jsx("p", { style: st.cardSub, children: "reported to billing" })] })] }));
const AlertsPanel = ({ alerts }) => {
    if (alerts.length === 0)
        return null;
    return (_jsx("div", { style: st.alertsContainer, children: alerts.map((alert, idx) => (_jsxs("div", { style: st.alertItem, children: [_jsx("span", { style: st.alertIcon, role: "img", "aria-label": "Warning", children: "!" }), alert] }, idx))) }));
};
const DailyChart = ({ days }) => {
    const maxValue = useMemo(() => {
        let max = 1;
        for (const d of days) {
            if (d.total > max)
                max = d.total;
        }
        return max;
    }, [days]);
    const chartHeight = 140;
    if (days.length === 0) {
        return _jsx("div", { style: st.empty, children: "No daily volume data available." });
    }
    return (_jsxs("div", { children: [_jsx("div", { style: st.chartContainer, children: _jsx("div", { style: st.chartInner, children: days.map((day) => {
                        const totalH = (day.total / maxValue) * chartHeight;
                        const billableH = (day.billable / maxValue) * chartHeight;
                        return (_jsxs("div", { style: st.chartColumn, children: [_jsxs("div", { style: st.barGroup, children: [_jsx("div", { style: st.bar(totalH, '#d0d0d0'), title: `Total: ${day.total}` }), _jsx("div", { style: st.bar(billableH, tokens.brand), title: `Billable: ${day.billable}` })] }), _jsx("div", { style: st.chartLabel, children: formatShortDate(day.date) })] }, day.date));
                    }) }) }), _jsxs("div", { style: st.chartLegend, children: [_jsxs("span", { children: [_jsx("span", { style: st.legendDot('#d0d0d0') }), "Total"] }), _jsxs("span", { children: [_jsx("span", { style: st.legendDot(tokens.brand) }), "Billable"] })] })] }));
};
const ConversationTable = ({ conversations, totalCount, offset, pageSize, onPageChange, loading, }) => {
    if (!loading && conversations.length === 0) {
        return _jsx("div", { style: st.empty, children: "No conversations found for this period." });
    }
    const currentPage = Math.floor(offset / pageSize) + 1;
    const totalPages = Math.max(1, Math.ceil(totalCount / pageSize));
    const hasPrev = offset > 0;
    const hasNext = offset + pageSize < totalCount;
    return (_jsxs("div", { children: [_jsx("div", { style: st.tableWrapper, children: _jsxs("table", { style: st.table, children: [_jsx("thead", { children: _jsxs("tr", { children: [_jsx("th", { style: st.th, children: "ID" }), _jsx("th", { style: st.th, children: "Status" }), _jsx("th", { style: st.th, children: "Customer" }), _jsx("th", { style: st.th, children: "Billable" }), _jsx("th", { style: st.th, children: "Messages" }), _jsx("th", { style: st.th, children: "Turns" }), _jsx("th", { style: st.th, children: "Started" }), _jsx("th", { style: st.th, children: "Ended" }), _jsx("th", { style: st.th, children: "Model" }), _jsx("th", { style: st.th, children: "Critic" })] }) }), _jsx("tbody", { children: loading ? (_jsx("tr", { children: _jsx("td", { style: st.td, colSpan: 10, children: _jsx("div", { style: { textAlign: 'center', padding: 16, color: '#888' }, children: "Loading conversations..." }) }) })) : (conversations.map((conv) => (_jsxs("tr", { children: [_jsxs("td", { style: {
                                            ...st.td,
                                            fontFamily: "'JetBrains Mono', monospace",
                                            fontSize: 12,
                                            maxWidth: 120,
                                            overflow: 'hidden',
                                            textOverflow: 'ellipsis',
                                        }, title: conv.conversationId, children: [conv.conversationId.slice(0, 12), "..."] }), _jsx("td", { style: st.td, children: conv.status ?? '--' }), _jsx("td", { style: {
                                            ...st.td,
                                            maxWidth: 100,
                                            overflow: 'hidden',
                                            textOverflow: 'ellipsis',
                                        }, title: conv.customerId ?? undefined, children: conv.customerId ?? '--' }), _jsx("td", { style: st.td, children: _jsx("span", { style: st.statusBadge(conv.isBillable), children: conv.isBillable ? 'Yes' : 'No' }) }), _jsx("td", { style: st.td, children: conv.messageCount }), _jsx("td", { style: st.td, children: conv.turnCount }), _jsx("td", { style: st.td, children: formatDateTime(conv.startedAt) }), _jsx("td", { style: st.td, children: formatDateTime(conv.endedAt) }), _jsx("td", { style: { ...st.td, fontSize: 12 }, children: conv.modelUsed ?? '--' }), _jsx("td", { style: st.td, children: _jsx("span", { style: st.criticBadge(conv.criticPassed), children: conv.criticPassed === null
                                                ? 'N/A'
                                                : conv.criticPassed
                                                    ? 'Pass'
                                                    : 'Fail' }) })] }, conv.conversationId)))) })] }) }), _jsxs("div", { style: st.pagination, children: [_jsxs("span", { style: st.pageInfo, children: ["Showing ", offset + 1, "--", Math.min(offset + pageSize, totalCount), " of", ' ', formatNumber(totalCount), " conversations"] }), _jsxs("div", { style: st.pageButtons, children: [_jsx("button", { style: st.pageBtn(!hasPrev), disabled: !hasPrev, onClick: () => onPageChange(Math.max(0, offset - pageSize)), children: "Previous" }), _jsxs("span", { style: {
                                    padding: '6px 10px',
                                    fontSize: 13,
                                    color: '#555',
                                    alignSelf: 'center',
                                }, children: ["Page ", currentPage, " of ", totalPages] }), _jsx("button", { style: st.pageBtn(!hasNext), disabled: !hasNext, onClick: () => onPageChange(offset + pageSize), children: "Next" })] })] })] }));
};
// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------
export const UsageDashboard = ({ tenantContext, apiFetch, onNotify, }) => {
    // ---- state ----
    const [billingPeriod, setBillingPeriod] = useState(undefined);
    const [convOffset, setConvOffset] = useState(0);
    const [exporting, setExporting] = useState(false);
    // ---- hooks ----
    const { data: usageData, loading: usageLoading, error: usageError, refetch: refetchUsage, } = useUsageDashboard(apiFetch, billingPeriod);
    const { data: dailyData, loading: dailyLoading, error: dailyError, } = useDailyVolume(apiFetch, billingPeriod);
    const { data: convData, loading: convLoading, error: convError, } = useConversationList(apiFetch, billingPeriod, convOffset, PAGE_SIZE);
    // ---- period options ----
    const periodOptions = useMemo(() => getBillingPeriodOptions(), []);
    // ---- handlers ----
    const handlePeriodChange = useCallback((e) => {
        const val = e.target.value;
        setBillingPeriod(val || undefined);
        setConvOffset(0);
    }, []);
    const handleExportCsv = useCallback(async () => {
        if (exporting)
            return;
        setExporting(true);
        try {
            const params = new URLSearchParams();
            if (billingPeriod)
                params.set('billing_period', billingPeriod);
            const path = `/api/dashboard/conversations/export?${params}`;
            const resp = await apiFetch(path);
            if (!resp.ok) {
                const body = await resp.text().catch(() => '');
                throw new Error(`${resp.status}: ${body}`);
            }
            const blob = await resp.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `conversations-${billingPeriod ?? 'current'}.csv`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            onNotify('CSV export downloaded.', 'success');
        }
        catch (err) {
            const msg = err instanceof Error ? err.message : 'Export failed';
            onNotify(`Export failed: ${msg}`, 'error');
        }
        finally {
            setExporting(false);
        }
    }, [exporting, billingPeriod, apiFetch, onNotify]);
    const handlePageChange = useCallback((newOffset) => {
        setConvOffset(newOffset);
    }, []);
    // ---- loading state (initial) ----
    if (usageLoading && !usageData) {
        return (_jsx("div", { style: st.container, children: _jsx("div", { style: st.loading, children: "Loading usage dashboard..." }) }));
    }
    // ---- error state ----
    if (usageError && !usageData) {
        return (_jsx("div", { style: st.container, children: _jsxs("div", { style: st.error, children: [_jsx("strong", { children: "Failed to load usage dashboard." }), _jsx("br", {}), usageError, _jsx("br", {}), _jsx("button", { style: { ...st.btnSecondary, marginTop: 12 }, onClick: refetchUsage, children: "Retry" })] }) }));
    }
    // Derive data
    const usage = usageData;
    const days = dailyData?.days ?? [];
    const conversations = convData?.items ?? [];
    const convTotalCount = convData?.totalCount ?? 0;
    return (_jsxs("div", { style: st.container, children: [_jsxs("div", { style: st.header, children: [_jsxs("div", { children: [_jsx("h2", { style: st.title, children: "Usage dashboard" }), _jsxs("p", { style: st.subtitle, children: [tenantContext.tier, " tier \u00B7", ' ', usage?.billingPeriod ?? 'current period'] })] }), _jsxs("select", { style: st.periodSelect, value: billingPeriod ?? '', onChange: handlePeriodChange, children: [_jsx("option", { value: "", children: "Current period" }), periodOptions.map((opt) => (_jsx("option", { value: opt.value, children: opt.label }, opt.value)))] })] }), _jsxs("div", { style: st.section, children: [_jsx("h3", { style: st.sectionTitle, children: "Usage summary" }), usage ? (_jsxs(_Fragment, { children: [_jsx(UsageMeter, { usage: usage }), _jsx(SummaryCards, { usage: usage }), (usage.activeAlerts ?? []).length > 0 && (_jsx(AlertsPanel, { alerts: usage.activeAlerts ?? [] }))] })) : (_jsx("div", { style: st.empty, children: "No usage data available." }))] }), _jsxs("div", { style: st.section, children: [_jsxs("h3", { style: st.sectionTitle, children: ["Daily volume", _jsx(HelpTooltip, { text: "Total and billable conversations per day for the selected billing period.", docLink: "https://agentredcx.com/docs/billing/overview#usage-dashboard" })] }), dailyLoading && days.length === 0 ? (_jsx("div", { style: { padding: 24, textAlign: 'center', color: '#888', fontSize: 14 }, children: "Loading chart data..." })) : dailyError ? (_jsxs("div", { style: st.error, children: ["Failed to load daily volume: ", dailyError] })) : (_jsx(DailyChart, { days: days }))] }), _jsxs("div", { style: st.section, children: [_jsxs("div", { style: st.tableHeaderRow, children: [_jsxs("h3", { style: st.sectionTitle, children: ["Conversations", _jsx(HelpTooltip, { text: "Conversations where the AI produced at least one response. Non-billable: test, admin, health-check, and system conversations.", docLink: "https://agentredcx.com/docs/billing/billable-conversation-spec" })] }), _jsx("button", { style: {
                                    ...st.exportBtn,
                                    ...(exporting ? { opacity: 0.6, cursor: 'not-allowed' } : {}),
                                }, onClick: handleExportCsv, disabled: exporting, children: exporting ? 'Exporting...' : 'Export CSV' })] }), convError ? (_jsxs("div", { style: st.error, children: ["Failed to load conversations: ", convError] })) : (_jsx(ConversationTable, { conversations: conversations, totalCount: convTotalCount, offset: convOffset, pageSize: PAGE_SIZE, onPageChange: handlePageChange, loading: convLoading }))] })] }));
};
export default UsageDashboard;
//# sourceMappingURL=UsageDashboard.js.map