import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
import { useMemo, useState } from 'react';
import { Paper, Group, Stack, Text, Badge, SimpleGrid, Title, Box, Skeleton, Table, Progress, SegmentedControl, Divider, Alert, List, ThemeIcon, useComputedColorScheme, } from '@mantine/core';
import { AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer, } from 'recharts';
import { useAppContext } from '../layouts/StandaloneLayout';
import { useAnalyticsSummary, useDailyVolume, useInboxConversations, useIntentBreakdown, useKnowledgeGaps, } from '../../shared/hooks/index';
import { useConfig } from '../../shared/hooks/useConfig';
import { HelpTooltip } from '../../shared/HelpTooltip';
import { agentDisplayLabel } from '../../shared/AnalyticsOverview';
import { tokens } from '../../shared/theme/styles';
const BRAND_RED = tokens.brand;
const statusColorMap = {
    active: 'blue',
    idle: 'yellow',
    ended: 'green',
    escalated: 'red',
};
function StatCard({ label, value, detail, loading }) {
    return (_jsxs(Paper, { p: "lg", radius: "md", withBorder: true, children: [_jsx(Text, { size: "xs", c: "dimmed", fw: 600, mb: 4, children: label }), loading ? (_jsx(Skeleton, { height: 28, width: "60%" })) : (_jsx(Text, { size: "xl", fw: 700, lh: 1, children: value })), detail && !loading && (_jsx(Text, { size: "xs", c: "dimmed", mt: 6, children: detail }))] }));
}
// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function formatChartDate(dateStr) {
    const d = new Date(dateStr);
    return `${d.getMonth() + 1}/${d.getDate()}`;
}
function formatResponseTime(ms) {
    if (ms == null)
        return '--';
    return `${ms}s`;
}
function formatSatisfaction(val) {
    if (val == null)
        return '--';
    return `${val}/5`;
}
function formatLastSeen(dateStr) {
    try {
        const d = new Date(dateStr);
        if (isNaN(d.getTime()))
            return dateStr;
        return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
    }
    catch {
        return dateStr;
    }
}
// ---------------------------------------------------------------------------
// Setup Checklist (WI #288) — shows incomplete setup steps
// ---------------------------------------------------------------------------
function SetupChecklist({ config, activationStatus }) {
    if (!config || !activationStatus)
        return null;
    // Active tenants have completed setup by definition — activation requires
    // configuration.  Showing an incomplete checklist on an active system is
    // contradictory and erodes merchant trust.  (S103 fix)
    if (activationStatus.is_active)
        return null;
    const checks = [
        { label: 'Brand name configured', done: Boolean(config.brand_name && config.brand_name !== 'My Store') },
        { label: 'AI instructions or category selected', done: Boolean(config.custom_instructions || config.brand_voice) },
        // Widget appearance: any customization counts — color change, position,
        // gradient toggle, launcher icon, etc.  Not just color !== default.
        { label: 'Widget appearance customized', done: Boolean((config.widget_primary_color && config.widget_primary_color !== '#ff3621')
                || (config.widget_position && config.widget_position !== 'bottom-right')
                || config.widget_header_gradient_enabled === true
                || (config.widget_launcher_icon && config.widget_launcher_icon !== 'chat')
                || (config.widget_background_color && config.widget_background_color !== '#ffffff')) },
        { label: 'System activated', done: Boolean(activationStatus.is_active) },
    ];
    const doneCount = checks.filter((c) => c.done).length;
    if (doneCount >= checks.length)
        return null;
    return (_jsx(Alert, { variant: "light", color: "blue", title: `Setup progress: ${doneCount}/${checks.length} complete`, children: _jsx(List, { size: "sm", spacing: 4, children: checks.map((c) => (_jsx(List.Item, { icon: _jsx(ThemeIcon, { color: c.done ? 'teal' : 'gray', size: 18, radius: "xl", variant: "light", children: _jsx(Text, { size: "xs", children: c.done ? '\u2713' : '\u2013' }) }), children: _jsx(Text, { size: "sm", c: c.done ? 'dimmed' : undefined, td: c.done ? 'line-through' : undefined, children: c.label }) }, c.label))) }) }));
}
// ---------------------------------------------------------------------------
// DashboardPage — combined overview + analytics
// ---------------------------------------------------------------------------
const DOCS_BASE = 'https://agentredcx.com/docs/admin-guide';
export function DashboardPage() {
    const { apiFetch, tenantContext, activationStatus: activationStatusFromCtx } = useAppContext();
    // Analytics filters
    const [period, setPeriod] = useState('30d');
    // Data hooks
    const summary = useAnalyticsSummary(apiFetch);
    const dailyVolume = useDailyVolume(apiFetch);
    const conversations = useInboxConversations(apiFetch);
    const intents = useIntentBreakdown(apiFetch);
    const gaps = useKnowledgeGaps(apiFetch);
    const configResult = useConfig(apiFetch);
    const computedColorScheme = useComputedColorScheme('dark');
    const isDark = computedColorScheme === 'dark';
    // Dark-mode-aware chart colors — Mazel design revision (2026-02-03 mockup)
    const gridStroke = isDark ? 'rgba(255,255,255,0.06)' : '#e9ecef';
    const axisTickFill = isDark ? tokens.textTertiary : '#868e96';
    const axisLineStroke = isDark ? tokens.border : '#dee2e6';
    const tooltipBg = isDark ? tokens.surface : '#fff';
    const tooltipBorder = isDark ? tokens.border : '#dee2e6';
    const tooltipColor = isDark ? tokens.textSecondary : undefined;
    const intentBarBg = isDark ? 'rgba(255,255,255,0.06)' : '#f1f3f5';
    const cardBorder = isDark ? tokens.border : 'var(--mantine-color-gray-2)';
    // SPEC-1599: Recent conversations must exclude non-billable
    const recentConversations = (conversations.data?.conversations ?? [])
        .filter((c) => c.isBillable !== false)
        .slice(0, 5);
    const intentList = intents.data?.intents ?? [];
    const rawChartData = dailyVolume.data?.days ?? [];
    const gapList = gaps.data?.gaps ?? [];
    // Generate full date range for chart, merging actual data (D7+D8 fix)
    const chartData = useMemo(() => {
        const periodDays = period === '7d' ? 7 : period === '14d' ? 14 : period === '90d' ? 90 : 30;
        const dataByDate = {};
        for (const d of rawChartData)
            dataByDate[d.date] = d;
        const result = [];
        const today = new Date();
        for (let i = periodDays - 1; i >= 0; i--) {
            const dt = new Date(today);
            dt.setDate(dt.getDate() - i);
            const dateStr = dt.toISOString().slice(0, 10);
            result.push(dataByDate[dateStr] ?? { date: dateStr, total: 0, billable: 0 });
        }
        return result;
    }, [rawChartData, period]);
    const summaryLoading = summary.loading;
    const s = summary.data;
    return (_jsxs(Stack, { gap: "lg", children: [_jsxs(Group, { justify: "space-between", align: "flex-end", children: [_jsxs("div", { children: [(() => {
                                const storeName = tenantContext?.shopDomain
                                    ? tenantContext.shopDomain.replace('.myshopify.com', '')
                                    : configResult.data?.config?.brand_name
                                        ? String(configResult.data.config.brand_name)
                                        : null;
                                return storeName ? (_jsx(Text, { size: "lg", fw: 600, c: "dimmed", mb: 4, children: storeName })) : null;
                            })(), _jsx(Title, { order: 2, children: "Dashboard" }), _jsx(Text, { c: "dimmed", size: "sm", children: "Overview of your customer experience performance" })] }), _jsx(Group, { gap: "md", children: _jsx(SegmentedControl, { value: period, onChange: setPeriod, data: [
                                { label: '7d', value: '7d' },
                                { label: '14d', value: '14d' },
                                { label: '30d', value: '30d' },
                                { label: '90d', value: '90d' },
                            ], size: "sm" }) })] }), _jsx(SetupChecklist, { config: configResult.data?.config, activationStatus: activationStatusFromCtx ?? undefined }), _jsxs(SimpleGrid, { cols: { base: 1, xs: 2, md: 3 }, spacing: "md", children: [_jsx(StatCard, { label: _jsxs(_Fragment, { children: ["Total conversations ", _jsx(HelpTooltip, { text: "Billable customer conversations in the selected period. Internal and admin conversations are excluded.", docLink: `${DOCS_BASE}/analytics#total-conversations` })] }), value: (s?.totalConversations ?? 0).toLocaleString(), loading: summaryLoading }), _jsx(StatCard, { label: _jsxs(_Fragment, { children: ["Avg response time ", _jsx(HelpTooltip, { text: "Average time for the AI to generate a complete response, measured from message received to response delivered.", docLink: `${DOCS_BASE}/analytics#average-response-time` })] }), value: formatResponseTime(s?.avgResponseTime), loading: summaryLoading }), _jsx(StatCard, { label: _jsxs(_Fragment, { children: ["Resolution rate ", _jsx(HelpTooltip, { text: "Percentage of conversations resolved by the AI without human escalation.", docLink: `${DOCS_BASE}/analytics#resolution-rate` })] }), value: s?.resolutionRate != null ? `${(s.resolutionRate * 100).toFixed(1)}%` : '--', detail: s != null
                            ? `${Math.round(s.totalConversations * (s.resolutionRate ?? 0)).toLocaleString()} resolved`
                            : undefined, loading: summaryLoading }), _jsx(StatCard, { label: _jsxs(_Fragment, { children: ["Customer satisfaction ", _jsx(HelpTooltip, { text: "Average customer rating on a 1-5 scale, collected via post-conversation feedback.", docLink: `${DOCS_BASE}/analytics#customer-satisfaction` })] }), value: formatSatisfaction(s?.customerSatisfaction), loading: summaryLoading }), _jsx(StatCard, { label: _jsxs(_Fragment, { children: ["Escalation rate ", _jsx(HelpTooltip, { text: "Percentage of conversations handed off to a human team member.", docLink: `${DOCS_BASE}/analytics#escalation-rate` })] }), value: s?.escalationRate != null ? `${(s.escalationRate * 100).toFixed(1)}%` : '--', detail: s != null
                            ? `${(s.escalationCount ?? 0).toLocaleString()} escalated`
                            : undefined, loading: summaryLoading })] }), _jsxs(Paper, { p: "lg", radius: "md", withBorder: true, children: [_jsxs(Group, { justify: "space-between", mb: "md", children: [_jsxs(Text, { fw: 600, children: ["Daily usage ", _jsx(HelpTooltip, { text: "Daily conversation volume (total vs. billable) over the selected time period. Helps identify usage trends and peak periods.", docLink: `${DOCS_BASE}/analytics#daily-usage-chart` })] }), _jsx(Text, { size: "xs", c: "dimmed", children: period === '7d'
                                    ? 'Last 7 days'
                                    : period === '14d'
                                        ? 'Last 14 days'
                                        : period === '90d'
                                            ? 'Last 90 days'
                                            : 'Last 30 days' })] }), dailyVolume.loading ? (_jsx(Skeleton, { height: 320 })) : chartData.length > 0 ? (_jsxs(_Fragment, { children: [_jsx(ResponsiveContainer, { width: "100%", height: 320, children: _jsxs(AreaChart, { data: chartData, margin: { top: 8, right: 8, left: -10, bottom: 0 }, children: [_jsxs("defs", { children: [_jsxs("linearGradient", { id: "gradTotal", x1: "0", y1: "0", x2: "0", y2: "1", children: [_jsx("stop", { offset: "5%", stopColor: BRAND_RED, stopOpacity: 0.15 }), _jsx("stop", { offset: "95%", stopColor: BRAND_RED, stopOpacity: 0 })] }), _jsxs("linearGradient", { id: "gradBillable", x1: "0", y1: "0", x2: "0", y2: "1", children: [_jsx("stop", { offset: "5%", stopColor: tokens.actionHover, stopOpacity: 0.12 }), _jsx("stop", { offset: "95%", stopColor: tokens.actionHover, stopOpacity: 0 })] })] }), _jsx(CartesianGrid, { strokeDasharray: "3 3", stroke: gridStroke }), _jsx(XAxis, { dataKey: "date", tickFormatter: formatChartDate, tick: { fontSize: 11, fill: axisTickFill }, axisLine: { stroke: axisLineStroke }, tickLine: false }), _jsx(YAxis, { tick: { fontSize: 11, fill: axisTickFill }, axisLine: { stroke: axisLineStroke }, tickLine: false }), _jsx(Tooltip, { contentStyle: {
                                                borderRadius: 8,
                                                border: `1px solid ${tooltipBorder}`,
                                                fontSize: 12,
                                                background: tooltipBg,
                                                color: tooltipColor,
                                            }, labelFormatter: (label) => `Date: ${label}` }), _jsx(Area, { type: "monotone", dataKey: "total", stroke: BRAND_RED, strokeWidth: 2, fill: "url(#gradTotal)", name: "Total" }), _jsx(Area, { type: "monotone", dataKey: "billable", stroke: tokens.actionHover, strokeWidth: 1.5, fill: "url(#gradBillable)", name: "Billable" })] }) }), _jsx(Group, { gap: "lg", mt: "xs", justify: "center", children: [
                                    { color: BRAND_RED, label: 'Total' },
                                    { color: tokens.actionHover, label: 'Billable' },
                                ].map((item) => (_jsxs(Group, { gap: 6, children: [_jsx(Box, { style: {
                                                width: 10,
                                                height: 10,
                                                borderRadius: 2,
                                                backgroundColor: item.color,
                                            } }), _jsx(Text, { size: "xs", c: "dimmed", children: item.label })] }, item.label))) })] })) : (_jsx(Group, { justify: "center", py: "xl", children: _jsx(Text, { size: "sm", c: "dimmed", children: "No volume data available" }) }))] }), _jsxs(SimpleGrid, { cols: { base: 1, md: 2 }, spacing: "md", children: [_jsxs(Paper, { p: "lg", radius: "md", withBorder: true, children: [_jsxs(Text, { fw: 600, mb: "md", children: ["Recent conversations ", _jsx(HelpTooltip, { text: "The 5 most recent customer conversations with status and assignment info.", docLink: `${DOCS_BASE}/conversations#conversation-list` })] }), conversations.loading ? (_jsx(Stack, { gap: "xs", children: [1, 2, 3, 4, 5].map((i) => (_jsx(Skeleton, { height: 60, radius: "sm" }, i))) })) : recentConversations.length === 0 ? (_jsx(Text, { size: "sm", c: "dimmed", ta: "center", py: "xl", children: "No conversations yet" })) : (_jsx(Stack, { gap: "xs", children: recentConversations.map((conv) => (_jsxs(Paper, { p: "sm", radius: "sm", style: {
                                        border: `1px solid ${cardBorder}`,
                                    }, children: [_jsxs(Group, { justify: "space-between", mb: 4, children: [_jsx(Text, { size: "sm", fw: 600, lineClamp: 1, style: { flex: 1 }, children: conv.customerName ?? 'Unknown Customer' }), _jsx(Badge, { size: "xs", variant: "light", color: statusColorMap[conv.status ?? ''] || 'gray', children: conv.status })] }), _jsxs(Text, { size: "xs", c: "dimmed", lineClamp: 1, children: [conv.messageCount ?? 0, " messages"] }), _jsxs(Group, { justify: "space-between", mt: 4, children: [_jsx(Text, { size: "xs", c: "dimmed", children: conv.status === 'escalated'
                                                        ? 'Escalated'
                                                        : conv.assignedTo
                                                            ? `Assigned: ${conv.assignedTo}`
                                                            : 'Unassigned' }), _jsx(Text, { size: "xs", c: "dimmed", children: conv.lastActivityAt != null
                                                        ? new Date(conv.lastActivityAt).toLocaleTimeString([], {
                                                            hour: '2-digit',
                                                            minute: '2-digit',
                                                        })
                                                        : '--' })] })] }, conv.conversationId))) }))] }), _jsxs(Paper, { p: "lg", radius: "md", withBorder: true, children: [_jsxs(Text, { fw: 600, mb: "md", children: ["Top topics ", _jsx(HelpTooltip, { text: "Most frequent query categories, ranked by conversation count.", docLink: `${DOCS_BASE}/analytics#topic-breakdown` })] }), intents.loading ? (_jsx(Stack, { gap: "xs", children: [1, 2, 3, 4, 5].map((i) => (_jsx(Skeleton, { height: 48, radius: "sm" }, i))) })) : intentList.length === 0 ? (_jsx(Text, { size: "sm", c: "dimmed", ta: "center", py: "xl", children: "No topic data available" })) : (_jsx(Stack, { gap: "xs", children: intentList.map((intent) => (_jsx(Group, { justify: "space-between", p: "sm", style: {
                                        border: `1px solid ${cardBorder}`,
                                        borderRadius: 6,
                                    }, children: _jsxs("div", { style: { flex: 1, minWidth: 0 }, children: [_jsxs(Group, { justify: "space-between", mb: 4, children: [_jsx(Text, { size: "sm", fw: 500, children: agentDisplayLabel(intent.agent) }), _jsx(Text, { size: "xs", c: "dimmed", children: (intent.invocationCount ?? 0).toLocaleString() })] }), _jsx(Box, { style: {
                                                    height: 6,
                                                    borderRadius: 3,
                                                    backgroundColor: intentBarBg,
                                                    overflow: 'hidden',
                                                }, children: _jsx(Box, { style: {
                                                        height: '100%',
                                                        width: `${intent.percentage ?? 0}%`,
                                                        borderRadius: 3,
                                                        backgroundColor: BRAND_RED,
                                                        opacity: 0.7 + ((intent.percentage ?? 0) / 100) * 0.3,
                                                    } }) })] }) }, intent.agent))) }))] })] }), _jsx(Divider, { label: "Detailed analytics", labelPosition: "center" }), _jsxs(Paper, { p: "lg", radius: "md", withBorder: true, children: [_jsxs(Text, { fw: 600, mb: "md", children: ["Topic breakdown ", _jsx(HelpTooltip, { text: "Query categories detected across your conversations, with count and distribution.", docLink: `${DOCS_BASE}/analytics#topic-breakdown` })] }), intentList.length > 0 ? (_jsxs(Table, { striped: true, highlightOnHover: true, children: [_jsx(Table.Thead, { children: _jsxs(Table.Tr, { children: [_jsx(Table.Th, { children: "Topic" }), _jsx(Table.Th, { style: { width: 80 }, children: "Count" }), _jsx(Table.Th, { style: { width: 200 }, children: "Distribution" })] }) }), _jsx(Table.Tbody, { children: intentList.map((intent) => (_jsxs(Table.Tr, { children: [_jsx(Table.Td, { children: _jsx(Text, { size: "sm", fw: 500, children: agentDisplayLabel(intent.agent) }) }), _jsx(Table.Td, { children: _jsx(Text, { size: "sm", children: (intent.invocationCount ?? 0).toLocaleString() }) }), _jsx(Table.Td, { children: _jsxs(Group, { gap: "xs", wrap: "nowrap", children: [_jsx(Progress, { value: intent.percentage ?? 0, color: BRAND_RED, size: "sm", style: { flex: 1 }, radius: "xl" }), _jsxs(Text, { size: "xs", c: "dimmed", w: 36, ta: "right", children: [intent.percentage ?? 0, "%"] })] }) })] }, intent.agent))) })] })) : (_jsx(Text, { size: "sm", c: "dimmed", ta: "center", py: "md", children: intents.loading ? 'Loading topic data...' : 'No topic data available' }))] }), _jsxs(Paper, { p: "lg", radius: "md", withBorder: true, children: [_jsxs(Group, { justify: "space-between", mb: "md", children: [_jsxs("div", { children: [_jsxs(Text, { fw: 600, children: ["Knowledge gaps ", _jsx(HelpTooltip, { text: "Conversations where the AI lacked sufficient knowledge to fully resolve the query. Add KB entries to address these gaps.", docLink: `${DOCS_BASE}/analytics#knowledge-gaps` })] }), _jsx(Text, { size: "xs", c: "dimmed", children: "Conversations where the AI could not fully resolve the customer query" })] }), gapList.length > 0 && (_jsxs(Badge, { size: "sm", variant: "light", color: "orange", children: [gapList.length, " ", gapList.length === 1 ? 'gap' : 'gaps'] }))] }), gapList.length > 0 ? (_jsxs(Table, { striped: true, highlightOnHover: true, children: [_jsx(Table.Thead, { children: _jsxs(Table.Tr, { children: [_jsx(Table.Th, { children: "Conversation" }), _jsx(Table.Th, { style: { width: 100 }, children: "Status" }), _jsx(Table.Th, { style: { width: 80 }, children: "Turns" }), _jsx(Table.Th, { style: { width: 80 }, children: "Messages" }), _jsx(Table.Th, { style: { width: 120 }, children: "Started" })] }) }), _jsx(Table.Tbody, { children: gapList.map((gap, idx) => (_jsxs(Table.Tr, { children: [_jsxs(Table.Td, { children: [_jsx(Text, { size: "sm", fw: 500, lineClamp: 1, children: gap.conversationId }), gap.customerId && (_jsx(Text, { size: "xs", c: "dimmed", children: gap.customerId }))] }), _jsx(Table.Td, { children: _jsx(Badge, { size: "xs", variant: "light", color: gap.status === 'escalated' ? 'red' :
                                                    gap.status === 'ended' ? 'green' :
                                                        gap.status === 'active' ? 'blue' : 'gray', children: gap.status ?? 'unknown' }) }), _jsx(Table.Td, { children: _jsx(Text, { size: "sm", children: gap.turnCount ?? 0 }) }), _jsx(Table.Td, { children: _jsx(Text, { size: "sm", children: gap.messageCount ?? 0 }) }), _jsx(Table.Td, { children: _jsx(Text, { size: "xs", c: "dimmed", children: gap.startedAt ? formatLastSeen(gap.startedAt) : '--' }) })] }, `gap-${idx}`))) })] })) : (_jsx(Text, { size: "sm", c: "dimmed", ta: "center", py: "md", children: gaps.loading ? 'Loading knowledge gaps...' : 'No knowledge gaps detected' }))] })] }));
}
//# sourceMappingURL=Dashboard.js.map