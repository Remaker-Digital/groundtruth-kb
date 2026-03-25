import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * Analytics page — Standalone admin.
 *
 * Adapted from prototype AnalyticsPage with API hooks replacing mock data.
 * Mantine v7 dark mode design with Recharts area chart.
 *
 * Changes from prototype:
 *   - Mock data replaced with useAnalyticsSummary, useDailyVolume,
 *     useIntentBreakdown, useKnowledgeGaps hooks.
 *   - StatCard delta badges removed (API AnalyticsSummary has no delta fields).
 *   - "AI Handled" StatCard removed (no aiHandledRate in API).
 *   - Period selector retained as visual placeholder (API does not support
 *     period filtering yet); no data scaling applied.
 *   - Chart simplified from 4 series to 2 (API DailyVolume: total + billable).
 *   - Intent table: avgConfidence and trend columns removed.
 *   - Knowledge Gaps section uses API data (query, frequency, lastSeen)
 *     instead of prototype inline constant (title, reason, priority, impact).
 *   - Null-safety guards on all API data access.
 */
import { useState } from 'react';
import { Paper, Group, Stack, Text, SimpleGrid, Title, Table, Progress, SegmentedControl, Box, Badge, Loader, useComputedColorScheme, } from '@mantine/core';
import { AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer, } from 'recharts';
import { useAppContext } from '../layouts/StandaloneLayout';
import { useAnalyticsSummary, useDailyVolume, useIntentBreakdown, useKnowledgeGaps, } from '../../shared/hooks/index';
import { agentDisplayLabel } from '../../shared/AnalyticsOverview';
import { tokens } from '../../shared/theme/styles';
// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------
const BRAND_RED = tokens.brand;
function StatCard({ label, value, detail }) {
    return (_jsxs(Paper, { p: "lg", radius: "md", withBorder: true, children: [_jsx(Text, { size: "xs", c: "dimmed", fw: 600, mb: 4, children: label }), _jsx(Text, { size: "xl", fw: 700, lh: 1, children: value }), detail && (_jsx(Text, { size: "xs", c: "dimmed", mt: 6, children: detail }))] }));
}
// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function formatChartDate(dateStr) {
    const d = new Date(dateStr);
    return `${d.getMonth() + 1}/${d.getDate()}`;
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
// AnalyticsPage
// ---------------------------------------------------------------------------
export const AnalyticsPage = () => {
    const { apiFetch } = useAppContext();
    const [period, setPeriod] = useState('30d');
    // API hooks
    const summary = useAnalyticsSummary(apiFetch);
    const dailyVolume = useDailyVolume(apiFetch);
    const intents = useIntentBreakdown(apiFetch);
    const gaps = useKnowledgeGaps(apiFetch);
    // Dark mode chart colors — Mazel design revision (2026-02-03 mockup)
    const computedColorScheme = useComputedColorScheme('dark');
    const isDark = computedColorScheme === 'dark';
    const gridStroke = isDark ? 'rgba(255,255,255,0.06)' : '#e9ecef';
    const axisTickFill = isDark ? tokens.textTertiary : '#868e96';
    const axisLineStroke = isDark ? tokens.border : '#dee2e6';
    const tooltipBg = isDark ? tokens.surface : '#fff';
    const tooltipBorder = isDark ? tokens.border : '#dee2e6';
    const tooltipColor = isDark ? tokens.textSecondary : undefined;
    const cardBorder = isDark ? tokens.border : 'var(--mantine-color-gray-2)';
    // Null-safe data extraction
    const s = summary.data;
    const chartData = dailyVolume.data?.days ?? [];
    const intentList = intents.data?.intents ?? [];
    const gapList = gaps.data?.gaps ?? [];
    // Loading state
    const isLoading = summary.loading && !s;
    return (_jsxs(Stack, { gap: "lg", children: [_jsxs(Group, { justify: "space-between", align: "flex-end", children: [_jsxs("div", { children: [_jsx(Title, { order: 2, children: "Analytics" }), _jsx(Text, { c: "dimmed", size: "sm", children: "Performance metrics and intent analysis" })] }), _jsx(Group, { gap: "md", children: _jsx(SegmentedControl, { value: period, onChange: setPeriod, data: [
                                { label: '7d', value: '7d' },
                                { label: '14d', value: '14d' },
                                { label: '30d', value: '30d' },
                                { label: '90d', value: '90d' },
                            ], size: "sm" }) })] }), isLoading && (_jsxs(Group, { justify: "center", py: "xl", children: [_jsx(Loader, { size: "sm" }), _jsx(Text, { size: "sm", c: "dimmed", children: "Loading analytics..." })] })), summary.error && (_jsx(Paper, { p: "md", radius: "md", withBorder: true, children: _jsxs(Text, { c: "red", size: "sm", children: ["Failed to load analytics: ", summary.error] }) })), _jsxs(SimpleGrid, { cols: { base: 1, xs: 2, md: 3 }, spacing: "md", children: [_jsx(StatCard, { label: "Total conversations", value: (s?.totalConversations ?? 0).toLocaleString(), detail: s ? `Billable: ${(s.billableConversations ?? 0).toLocaleString()}` : undefined }), _jsx(StatCard, { label: "Avg response time", value: s?.avgResponseTime != null ? `${s.avgResponseTime}s` : '--' }), _jsx(StatCard, { label: "Resolution rate", value: s?.resolutionRate != null ? `${(s.resolutionRate * 100).toFixed(1)}%` : '--', detail: s != null
                            ? `${Math.round(s.totalConversations * (s.resolutionRate ?? 0)).toLocaleString()} resolved`
                            : undefined }), _jsx(StatCard, { label: "Customer satisfaction", value: s?.customerSatisfaction != null ? `${s.customerSatisfaction}/5` : '--' }), _jsx(StatCard, { label: "Escalation rate", value: s != null ? `${(s.escalationRate * 100).toFixed(1)}%` : '--', detail: s != null
                            ? `${(s.escalationCount ?? 0).toLocaleString()} escalated`
                            : undefined })] }), _jsxs(Paper, { p: "lg", radius: "md", withBorder: true, children: [_jsxs(Group, { justify: "space-between", mb: "md", children: [_jsx(Text, { fw: 600, children: "Conversation volume" }), _jsx(Text, { size: "xs", c: "dimmed", children: period === '7d'
                                    ? 'Last 7 days'
                                    : period === '14d'
                                        ? 'Last 14 days'
                                        : period === '90d'
                                            ? 'Last 90 days'
                                            : 'Last 30 days' })] }), chartData.length > 0 ? (_jsxs(_Fragment, { children: [_jsx(ResponsiveContainer, { width: "100%", height: 340, children: _jsxs(AreaChart, { data: chartData, margin: { top: 8, right: 8, left: -10, bottom: 0 }, children: [_jsxs("defs", { children: [_jsxs("linearGradient", { id: "aGradTotal", x1: "0", y1: "0", x2: "0", y2: "1", children: [_jsx("stop", { offset: "5%", stopColor: BRAND_RED, stopOpacity: 0.15 }), _jsx("stop", { offset: "95%", stopColor: BRAND_RED, stopOpacity: 0 })] }), _jsxs("linearGradient", { id: "aGradBillable", x1: "0", y1: "0", x2: "0", y2: "1", children: [_jsx("stop", { offset: "5%", stopColor: tokens.actionHover, stopOpacity: 0.12 }), _jsx("stop", { offset: "95%", stopColor: tokens.actionHover, stopOpacity: 0 })] })] }), _jsx(CartesianGrid, { strokeDasharray: "3 3", stroke: gridStroke }), _jsx(XAxis, { dataKey: "date", tickFormatter: formatChartDate, tick: { fontSize: 11, fill: axisTickFill }, axisLine: { stroke: axisLineStroke }, tickLine: false }), _jsx(YAxis, { tick: { fontSize: 11, fill: axisTickFill }, axisLine: { stroke: axisLineStroke }, tickLine: false }), _jsx(Tooltip, { contentStyle: {
                                                borderRadius: 8,
                                                border: `1px solid ${tooltipBorder}`,
                                                fontSize: 12,
                                                background: tooltipBg,
                                                color: tooltipColor,
                                            }, labelFormatter: (label) => `Date: ${label}` }), _jsx(Area, { type: "monotone", dataKey: "total", stroke: BRAND_RED, strokeWidth: 2, fill: "url(#aGradTotal)", name: "Total" }), _jsx(Area, { type: "monotone", dataKey: "billable", stroke: tokens.actionHover, strokeWidth: 1.5, fill: "url(#aGradBillable)", name: "Billable" })] }) }), _jsx(Group, { gap: "lg", mt: "xs", justify: "center", children: [
                                    { color: BRAND_RED, label: 'Total' },
                                    { color: tokens.actionHover, label: 'Billable' },
                                ].map((item) => (_jsxs(Group, { gap: 6, children: [_jsx(Box, { style: {
                                                width: 10,
                                                height: 10,
                                                borderRadius: 2,
                                                backgroundColor: item.color,
                                            } }), _jsx(Text, { size: "xs", c: "dimmed", children: item.label })] }, item.label))) })] })) : (_jsx(Group, { justify: "center", py: "xl", children: _jsx(Text, { size: "sm", c: "dimmed", children: dailyVolume.loading ? 'Loading chart data...' : 'No volume data available' }) }))] }), _jsxs(Paper, { p: "lg", radius: "md", withBorder: true, children: [_jsx(Text, { fw: 600, mb: "md", children: "Topic breakdown" }), intentList.length > 0 ? (_jsxs(Table, { striped: true, highlightOnHover: true, children: [_jsx(Table.Thead, { children: _jsxs(Table.Tr, { children: [_jsx(Table.Th, { children: "Topic" }), _jsx(Table.Th, { style: { width: 80 }, children: "Count" }), _jsx(Table.Th, { style: { width: 200 }, children: "Distribution" })] }) }), _jsx(Table.Tbody, { children: intentList.map((intent) => (_jsxs(Table.Tr, { children: [_jsx(Table.Td, { children: _jsx(Text, { size: "sm", fw: 500, children: agentDisplayLabel(intent.agent) }) }), _jsx(Table.Td, { children: _jsx(Text, { size: "sm", children: (intent.invocationCount ?? 0).toLocaleString() }) }), _jsx(Table.Td, { children: _jsxs(Group, { gap: "xs", wrap: "nowrap", children: [_jsx(Progress, { value: intent.percentage ?? 0, color: BRAND_RED, size: "sm", style: { flex: 1 }, radius: "xl" }), _jsxs(Text, { size: "xs", c: "dimmed", w: 36, ta: "right", children: [intent.percentage ?? 0, "%"] })] }) })] }, intent.agent))) })] })) : (_jsx(Text, { size: "sm", c: "dimmed", ta: "center", py: "md", children: intents.loading ? 'Loading topic data...' : 'No topic data available' }))] }), _jsxs(Paper, { p: "lg", radius: "md", withBorder: true, children: [_jsxs(Group, { justify: "space-between", mb: "md", children: [_jsxs("div", { children: [_jsx(Text, { fw: 600, children: "Knowledge gaps" }), _jsx(Text, { size: "xs", c: "dimmed", children: "Conversations where the AI could not fully resolve the customer query" })] }), gapList.length > 0 && (_jsxs(Badge, { size: "sm", variant: "light", color: "orange", children: [gapList.length, " ", gapList.length === 1 ? 'gap' : 'gaps'] }))] }), gapList.length > 0 ? (_jsxs(Table, { striped: true, highlightOnHover: true, children: [_jsx(Table.Thead, { children: _jsxs(Table.Tr, { children: [_jsx(Table.Th, { children: "Conversation" }), _jsx(Table.Th, { style: { width: 100 }, children: "Status" }), _jsx(Table.Th, { style: { width: 80 }, children: "Turns" }), _jsx(Table.Th, { style: { width: 80 }, children: "Messages" }), _jsx(Table.Th, { style: { width: 120 }, children: "Started" })] }) }), _jsx(Table.Tbody, { children: gapList.map((gap, idx) => (_jsxs(Table.Tr, { children: [_jsxs(Table.Td, { children: [_jsx(Text, { size: "sm", fw: 500, lineClamp: 1, children: gap.conversationId }), gap.customerId && (_jsx(Text, { size: "xs", c: "dimmed", children: gap.customerId }))] }), _jsx(Table.Td, { children: _jsx(Badge, { size: "xs", variant: "light", color: gap.status === 'escalated' ? 'red' :
                                                    gap.status === 'ended' ? 'green' :
                                                        gap.status === 'active' ? 'blue' : 'gray', children: gap.status ?? 'unknown' }) }), _jsx(Table.Td, { children: _jsx(Text, { size: "sm", children: gap.turnCount ?? 0 }) }), _jsx(Table.Td, { children: _jsx(Text, { size: "sm", children: gap.messageCount ?? 0 }) }), _jsx(Table.Td, { children: _jsx(Text, { size: "xs", c: "dimmed", children: gap.startedAt ? formatLastSeen(gap.startedAt) : '--' }) })] }, `gap-${idx}`))) })] })) : (_jsx(Text, { size: "sm", c: "dimmed", ta: "center", py: "md", children: gaps.loading ? 'Loading knowledge gaps...' : 'No knowledge gaps detected' }))] })] }));
};
//# sourceMappingURL=Analytics.js.map