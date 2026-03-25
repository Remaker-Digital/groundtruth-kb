import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * AnalyticsOverview - Analytics dashboard with summary cards, topic breakdown,
 * and knowledge gaps table.
 *
 * Summary cards: total conversations, avg response time, resolution rate,
 *   escalation rate, CSAT.
 * Topic breakdown: horizontal bar chart of top query categories by count.
 * Knowledge gaps: table of unresolved queries with frequency and last-seen date.
 *
 * Framework-agnostic React component — no Polaris, no Tailwind, pure inline styles.
 * Receives auth, API fetch, and notification callbacks from the shell.
 *
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { useMemo, useState } from 'react';
import { useAnalyticsSummary, useIntentBreakdown, useKnowledgeGaps } from './hooks';
import { HelpTooltip } from './HelpTooltip';
import { tokens } from './theme/styles';
// ---------------------------------------------------------------------------
// Style constants
// ---------------------------------------------------------------------------
const BRAND_PRIMARY = tokens.brand; // accent only — spinner, summary card accent
const ACTION_BLUE = tokens.action;
const COLOR_SUCCESS = '#22863a';
const COLOR_DANGER = '#d73a49';
const COLOR_GRAY = '#6a737d';
const COLOR_LIGHT_GRAY = '#f6f8fa';
const COLOR_BORDER = '#e1e4e8';
const COLOR_WHITE = '#ffffff';
const COLOR_TEXT = '#24292e';
const COLOR_TEXT_SECONDARY = '#586069';
const COLOR_WARNING = '#e36209';
const FONT_FAMILY = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif";
const FONT_MONO = "'JetBrains Mono', 'SFMono-Regular', Consolas, monospace";
const BORDER_RADIUS = '6px';
const DOCS_BASE = 'https://agentredcx.com/docs/admin-guide';
// Map internal agent names to user-facing labels
const AGENT_LABEL_MAP = {
    'intent-classifier': 'Question routing',
    'knowledge-retrieval': 'Knowledge lookup',
    'response-generator': 'Response generation',
    'critic-supervisor': 'Quality review',
};
/** Returns a user-facing label for an agent name, falling back to title-case. */
export function agentDisplayLabel(agent) {
    return AGENT_LABEL_MAP[agent] ?? agent.replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}
// Bar chart color palette — 8 distinct hues for topic bars
const BAR_COLORS = [
    '#3b82f6',
    '#10b981',
    '#f59e0b',
    '#ef4444',
    '#8b5cf6',
    '#ec4899',
    '#06b6d4',
    '#84cc16',
];
// ---------------------------------------------------------------------------
// Utilities
// ---------------------------------------------------------------------------
function formatMs(ms) {
    if (ms == null)
        return '--';
    if (ms < 1000)
        return `${Math.round(ms)}ms`;
    const sec = ms / 1000;
    if (sec < 60)
        return `${sec.toFixed(1)}s`;
    const min = Math.floor(sec / 60);
    const remSec = Math.round(sec % 60);
    return `${min}m ${remSec}s`;
}
function formatPercent(value) {
    if (value == null)
        return '--';
    return `${(value * 100).toFixed(1)}%`;
}
function formatNumber(value) {
    if (value == null)
        return '0';
    if (value >= 1000000)
        return `${(value / 1000000).toFixed(1)}M`;
    if (value >= 1000)
        return `${(value / 1000).toFixed(1)}K`;
    return value.toLocaleString();
}
function formatDate(iso) {
    const d = new Date(iso);
    return d.toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' });
}
function formatRelativeDate(iso) {
    const d = new Date(iso);
    const now = Date.now();
    const diffMs = now - d.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    if (diffDays === 0)
        return 'Today';
    if (diffDays === 1)
        return 'Yesterday';
    if (diffDays < 7)
        return `${diffDays}d ago`;
    if (diffDays < 30)
        return `${Math.floor(diffDays / 7)}w ago`;
    return formatDate(iso);
}
// ---------------------------------------------------------------------------
// Sub-components: shared loading / error / empty
// ---------------------------------------------------------------------------
const LoadingSpinner = ({ text = 'Loading...' }) => (_jsxs("div", { style: {
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
                animation: 'analyticsSpin 0.8s linear infinite',
                marginBottom: '12px',
            } }), _jsx("span", { style: { fontSize: '14px' }, children: text }), _jsx("style", { children: `@keyframes analyticsSpin { to { transform: rotate(360deg); } }` })] }));
const EmptyState = ({ icon, title, subtitle }) => (_jsxs("div", { style: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '32px 16px',
        color: COLOR_TEXT_SECONDARY,
    }, children: [_jsx("span", { style: { fontSize: '36px', marginBottom: '10px' }, children: icon }), _jsx("span", { style: { fontSize: '14px', fontWeight: 600, color: COLOR_TEXT, marginBottom: '4px' }, children: title }), subtitle && _jsx("span", { style: { fontSize: '12px' }, children: subtitle })] }));
const ErrorBanner = ({ message, onRetry }) => (_jsxs("div", { style: {
        padding: '12px 16px',
        backgroundColor: '#ffeef0',
        border: `1px solid ${COLOR_DANGER}33`,
        borderRadius: BORDER_RADIUS,
        margin: '16px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '12px',
    }, children: [_jsx("span", { style: { fontSize: '13px', color: COLOR_DANGER }, children: message }), onRetry && (_jsx("button", { onClick: onRetry, style: {
                padding: '4px 12px',
                border: `1px solid ${COLOR_DANGER}`,
                borderRadius: BORDER_RADIUS,
                backgroundColor: 'transparent',
                color: COLOR_DANGER,
                fontSize: '12px',
                fontFamily: FONT_FAMILY,
                cursor: 'pointer',
                whiteSpace: 'nowrap',
            }, children: "Retry" }))] }));
// ---------------------------------------------------------------------------
// Section header
// ---------------------------------------------------------------------------
const SectionHeader = ({ title, subtitle, tooltip, docLink }) => (_jsxs("div", { style: { marginBottom: '16px' }, children: [_jsxs("h3", { style: { margin: 0, fontSize: '16px', fontWeight: 600, color: COLOR_TEXT, display: 'inline-flex', alignItems: 'center', gap: '6px' }, children: [title, tooltip && _jsx(HelpTooltip, { text: tooltip, docLink: docLink })] }), subtitle && (_jsx("span", { style: { fontSize: '13px', color: COLOR_TEXT_SECONDARY, display: 'block' }, children: subtitle }))] }));
const SummaryCard = ({ label, value, subtext, accentColor = BRAND_PRIMARY, tooltip, docLink }) => (_jsxs("div", { style: {
        flex: '1 1 180px',
        minWidth: '160px',
        backgroundColor: COLOR_WHITE,
        border: `1px solid ${COLOR_BORDER}`,
        borderRadius: BORDER_RADIUS,
        padding: '16px 20px',
        borderTop: `3px solid ${accentColor}`,
    }, children: [_jsxs("div", { style: { fontSize: '12px', fontWeight: 600, color: COLOR_TEXT_SECONDARY, textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '8px', display: 'inline-flex', alignItems: 'center', gap: '6px' }, children: [label, tooltip && _jsx(HelpTooltip, { text: tooltip, docLink: docLink })] }), _jsx("div", { style: { fontSize: '28px', fontWeight: 700, color: COLOR_TEXT, lineHeight: 1.1, fontFamily: FONT_MONO }, children: value }), subtext && (_jsx("div", { style: { fontSize: '12px', color: COLOR_TEXT_SECONDARY, marginTop: '4px' }, children: subtext }))] }));
const IntentBarChart = ({ intents }) => {
    const maxCount = useMemo(() => {
        if (intents.length === 0)
            return 1;
        return Math.max(...intents.map((i) => i.invocationCount ?? 0), 1);
    }, [intents]);
    if (intents.length === 0) {
        return (_jsx(EmptyState, { icon: String.fromCodePoint(0x1F4CA), title: "No topic data", subtitle: "Topic breakdown will appear once conversations are processed." }));
    }
    return (_jsx("div", { style: { display: 'flex', flexDirection: 'column', gap: '8px' }, children: intents.map((intent, idx) => {
            const barWidth = Math.max(((intent.invocationCount ?? 0) / maxCount) * 100, 2);
            const color = BAR_COLORS[idx % BAR_COLORS.length];
            return (_jsxs("div", { style: { display: 'flex', alignItems: 'center', gap: '12px' }, children: [_jsx("div", { style: {
                            width: '180px',
                            minWidth: '120px',
                            fontSize: '13px',
                            color: COLOR_TEXT,
                            fontWeight: 500,
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                        }, title: agentDisplayLabel(intent.agent), children: agentDisplayLabel(intent.agent) }), _jsxs("div", { style: { flex: 1, display: 'flex', alignItems: 'center', gap: '8px' }, children: [_jsx("div", { style: {
                                    flex: 1,
                                    height: '24px',
                                    backgroundColor: COLOR_LIGHT_GRAY,
                                    borderRadius: '4px',
                                    overflow: 'hidden',
                                    position: 'relative',
                                }, children: _jsx("div", { style: {
                                        width: `${barWidth}%`,
                                        height: '100%',
                                        backgroundColor: color,
                                        borderRadius: '4px',
                                        transition: 'width 0.4s ease-out',
                                        minWidth: '4px',
                                    } }) }), _jsxs("div", { style: {
                                    width: '70px',
                                    textAlign: 'right',
                                    fontSize: '12px',
                                    fontFamily: FONT_MONO,
                                    color: COLOR_TEXT_SECONDARY,
                                    flexShrink: 0,
                                }, children: [formatNumber(intent.invocationCount), ' ', _jsxs("span", { style: { fontSize: '11px', color: COLOR_GRAY }, children: ["(", (intent.percentage ?? 0).toFixed(1), "%)"] })] })] })] }, intent.agent));
        }) }));
};
const KnowledgeGapsTable = ({ gaps }) => {
    if (gaps.length === 0) {
        return (_jsx(EmptyState, { icon: String.fromCodePoint(0x2705), title: "No knowledge gaps detected", subtitle: "Your knowledge base is covering all customer queries." }));
    }
    const thStyle = {
        padding: '10px 16px',
        textAlign: 'left',
        fontSize: '12px',
        fontWeight: 600,
        color: COLOR_TEXT_SECONDARY,
        borderBottom: `1px solid ${COLOR_BORDER}`,
        textTransform: 'uppercase',
        letterSpacing: '0.5px',
    };
    return (_jsx("div", { style: { overflowX: 'auto' }, children: _jsxs("table", { style: { width: '100%', borderCollapse: 'collapse', fontSize: '14px' }, children: [_jsx("thead", { children: _jsxs("tr", { style: { backgroundColor: COLOR_LIGHT_GRAY }, children: [_jsx("th", { style: thStyle, children: "Conversation" }), _jsx("th", { style: { ...thStyle, width: '100px' }, children: "Status" }), _jsx("th", { style: { ...thStyle, width: '80px', textAlign: 'right' }, children: "Turns" }), _jsx("th", { style: { ...thStyle, width: '80px', textAlign: 'right' }, children: "Messages" }), _jsx("th", { style: { ...thStyle, width: '120px', textAlign: 'right' }, children: "Started" })] }) }), _jsx("tbody", { children: gaps.map((gap, idx) => (_jsxs("tr", { style: { backgroundColor: idx % 2 === 0 ? COLOR_WHITE : COLOR_LIGHT_GRAY }, children: [_jsxs("td", { style: {
                                    padding: '10px 16px',
                                    borderBottom: `1px solid ${COLOR_BORDER}`,
                                    color: COLOR_TEXT,
                                    fontSize: '13px',
                                }, children: [_jsx("div", { children: gap.conversationId }), gap.customerId && (_jsx("div", { style: { fontSize: '11px', color: COLOR_TEXT_SECONDARY }, children: gap.customerId }))] }), _jsx("td", { style: {
                                    padding: '10px 16px',
                                    borderBottom: `1px solid ${COLOR_BORDER}`,
                                    fontSize: '12px',
                                    color: gap.status === 'escalated' ? COLOR_DANGER : COLOR_TEXT,
                                    fontWeight: gap.status === 'escalated' ? 600 : 400,
                                }, children: gap.status ?? 'unknown' }), _jsx("td", { style: {
                                    padding: '10px 16px',
                                    borderBottom: `1px solid ${COLOR_BORDER}`,
                                    textAlign: 'right',
                                    fontFamily: FONT_MONO,
                                    fontSize: '13px',
                                }, children: gap.turnCount ?? 0 }), _jsx("td", { style: {
                                    padding: '10px 16px',
                                    borderBottom: `1px solid ${COLOR_BORDER}`,
                                    textAlign: 'right',
                                    fontFamily: FONT_MONO,
                                    fontSize: '13px',
                                }, children: gap.messageCount ?? 0 }), _jsx("td", { style: {
                                    padding: '10px 16px',
                                    borderBottom: `1px solid ${COLOR_BORDER}`,
                                    textAlign: 'right',
                                    fontSize: '12px',
                                    color: COLOR_TEXT_SECONDARY,
                                }, children: gap.startedAt ? formatRelativeDate(gap.startedAt) : '--' })] }, `${gap.conversationId}-${idx}`))) })] }) }));
};
// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------
const PERIOD_OPTIONS = [
    { value: '7d', label: '7 days' },
    { value: '14d', label: '14 days' },
    { value: '30d', label: '30 days' },
    { value: '90d', label: '90 days' },
];
export const AnalyticsOverview = ({ tenantContext, apiFetch, onNotify, }) => {
    const [period, setPeriod] = useState('30d');
    // Data hooks — period filter only (test mode removed S157)
    const { data: summary, loading: summaryLoading, error: summaryError, refetch: refetchSummary, } = useAnalyticsSummary(apiFetch, undefined, period);
    const { data: intentData, loading: intentsLoading, error: intentsError, refetch: refetchIntents, } = useIntentBreakdown(apiFetch, undefined, period);
    const intents = intentData?.intents ?? [];
    const { data: gapsData, loading: gapsLoading, error: gapsError, refetch: refetchGaps, } = useKnowledgeGaps(apiFetch, undefined, period);
    const gaps = gapsData?.gaps ?? [];
    // Determine overall loading state for the initial load
    const isInitialLoad = summaryLoading && !summary;
    if (isInitialLoad) {
        return (_jsx("div", { style: {
                fontFamily: FONT_FAMILY,
                border: `1px solid ${COLOR_BORDER}`,
                borderRadius: BORDER_RADIUS,
                backgroundColor: COLOR_WHITE,
                minHeight: '500px',
            }, children: _jsx(LoadingSpinner, { text: "Loading analytics..." }) }));
    }
    // Determine rating color for CSAT
    function csatColor(score) {
        if (score == null)
            return COLOR_GRAY;
        if (score >= 4.0)
            return COLOR_SUCCESS;
        if (score >= 3.0)
            return COLOR_WARNING;
        return COLOR_DANGER;
    }
    // Determine rating color for escalation rate
    function escalationColor(rate) {
        if (rate <= 0.05)
            return COLOR_SUCCESS;
        if (rate <= 0.15)
            return COLOR_WARNING;
        return COLOR_DANGER;
    }
    return (_jsxs("div", { style: {
            fontFamily: FONT_FAMILY,
            border: `1px solid ${COLOR_BORDER}`,
            borderRadius: BORDER_RADIUS,
            backgroundColor: COLOR_WHITE,
            minHeight: '500px',
        }, children: [_jsxs("div", { style: {
                    padding: '16px 20px',
                    borderBottom: `1px solid ${COLOR_BORDER}`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                }, children: [_jsxs("div", { children: [_jsx("h2", { style: { margin: 0, fontSize: '18px', fontWeight: 600, color: COLOR_TEXT }, children: "Analytics Overview" }), summary?.since && summary?.until && (_jsxs("span", { style: { fontSize: '13px', color: COLOR_TEXT_SECONDARY }, children: [formatDate(summary.since), " \u2013 ", formatDate(summary.until)] }))] }), _jsxs("div", { style: { display: 'flex', alignItems: 'center', gap: '8px' }, children: [_jsx("div", { style: {
                                    display: 'inline-flex',
                                    border: `1px solid ${COLOR_BORDER}`,
                                    borderRadius: BORDER_RADIUS,
                                    overflow: 'hidden',
                                }, role: "group", "aria-label": "Analytics date range", children: PERIOD_OPTIONS.map((opt) => (_jsx("button", { onClick: () => setPeriod(opt.value), "aria-pressed": period === opt.value, style: {
                                        padding: '5px 10px',
                                        border: 'none',
                                        borderRight: `1px solid ${COLOR_BORDER}`,
                                        backgroundColor: period === opt.value ? ACTION_BLUE : COLOR_WHITE,
                                        color: period === opt.value ? COLOR_WHITE : COLOR_TEXT,
                                        fontSize: '12px',
                                        fontFamily: FONT_FAMILY,
                                        cursor: 'pointer',
                                        fontWeight: period === opt.value ? 600 : 400,
                                        transition: 'background-color 0.15s, color 0.15s',
                                    }, children: opt.label }, opt.value))) }), _jsx("button", { onClick: () => {
                                    refetchSummary();
                                    refetchIntents();
                                    refetchGaps();
                                }, style: {
                                    padding: '6px 14px',
                                    border: `1px solid ${COLOR_BORDER}`,
                                    borderRadius: BORDER_RADIUS,
                                    backgroundColor: COLOR_WHITE,
                                    color: COLOR_TEXT,
                                    fontSize: '12px',
                                    fontFamily: FONT_FAMILY,
                                    cursor: 'pointer',
                                    fontWeight: 500,
                                }, children: "Refresh" })] })] }), _jsxs("div", { style: { padding: '20px' }, children: [summaryError && (_jsx(ErrorBanner, { message: summaryError, onRetry: refetchSummary })), summary && (_jsxs("div", { style: {
                            display: 'flex',
                            gap: '16px',
                            flexWrap: 'wrap',
                            marginBottom: '32px',
                        }, children: [_jsx(SummaryCard, { label: "Total conversations", value: formatNumber(summary.totalConversations), accentColor: tokens.action, tooltip: "All conversations (billable and non-billable) in the selected period.", docLink: `${DOCS_BASE}/analytics#total-conversations` }), _jsx(SummaryCard, { label: "Avg response time", value: formatMs(summary.avgResponseTime), subtext: summary.avgResponseTime != null ? (summary.avgResponseTime <= 2000 ? 'Within SLA' : 'Above P95 target') : undefined, accentColor: summary.avgResponseTime != null ? (summary.avgResponseTime <= 2000 ? COLOR_SUCCESS : COLOR_WARNING) : COLOR_GRAY, tooltip: "Average time from customer message to AI response (P50).", docLink: `${DOCS_BASE}/analytics#average-response-time` }), _jsx(SummaryCard, { label: "Resolution rate", value: formatPercent(summary.resolutionRate), accentColor: summary.resolutionRate != null ? (summary.resolutionRate >= 0.8 ? COLOR_SUCCESS : COLOR_WARNING) : COLOR_GRAY, tooltip: "Percentage of conversations resolved without escalation to a human agent.", docLink: `${DOCS_BASE}/analytics#resolution-rate` }), _jsx(SummaryCard, { label: "Escalation rate", value: formatPercent(summary.escalationRate), accentColor: escalationColor(summary.escalationRate), tooltip: "Percentage of conversations escalated to human agents.", docLink: `${DOCS_BASE}/analytics#escalation-rate` }), _jsx(SummaryCard, { label: "CSAT", value: summary.customerSatisfaction != null ? summary.customerSatisfaction.toFixed(1) : '--', subtext: summary.customerSatisfaction != null ? 'out of 5.0' : 'No ratings yet', accentColor: csatColor(summary.customerSatisfaction), tooltip: "Customer satisfaction score based on thumbs up/down ratings.", docLink: `${DOCS_BASE}/analytics#customer-satisfaction` })] })), _jsxs("div", { style: {
                            marginBottom: '32px',
                            padding: '20px',
                            backgroundColor: COLOR_LIGHT_GRAY,
                            borderRadius: BORDER_RADIUS,
                            border: `1px solid ${COLOR_BORDER}`,
                        }, children: [_jsx(SectionHeader, { title: "Topic breakdown", subtitle: "Top query categories by conversation count", tooltip: "Distribution of customer query categories across your conversations.", docLink: `${DOCS_BASE}/analytics#topic-breakdown` }), intentsError && (_jsx(ErrorBanner, { message: intentsError, onRetry: refetchIntents })), intentsLoading && intents.length === 0 && (_jsx(LoadingSpinner, { text: "Loading intents..." })), !intentsLoading && !intentsError && (_jsx(IntentBarChart, { intents: intents }))] }), _jsxs("div", { style: {
                            padding: '20px',
                            backgroundColor: COLOR_LIGHT_GRAY,
                            borderRadius: BORDER_RADIUS,
                            border: `1px solid ${COLOR_BORDER}`,
                        }, children: [_jsx(SectionHeader, { title: "Knowledge gaps", subtitle: "Queries the AI could not resolve \u2014 consider adding KB articles for these topics", tooltip: "Conversations where the AI could not find a confident answer in the Knowledge Base.", docLink: `${DOCS_BASE}/analytics#knowledge-gaps` }), gapsError && (_jsx(ErrorBanner, { message: gapsError, onRetry: refetchGaps })), gapsLoading && gaps.length === 0 && (_jsx(LoadingSpinner, { text: "Loading knowledge gaps..." })), !gapsLoading && !gapsError && (_jsx(KnowledgeGapsTable, { gaps: gaps }))] })] })] }));
};
export default AnalyticsOverview;
//# sourceMappingURL=AnalyticsOverview.js.map