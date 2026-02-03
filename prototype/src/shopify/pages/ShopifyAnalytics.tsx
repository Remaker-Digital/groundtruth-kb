// (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

import React, { useState, useCallback } from 'react';
import {
  Page,
  Layout,
  LegacyCard,
  Text,
  Badge,
  DataTable,
  Tabs,
  Banner,
  Button,
  Box,
  InlineStack,
  BlockStack,
} from '@shopify/polaris';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from 'recharts';
import {
  ANALYTICS_SUMMARY,
  DAILY_VOLUMES,
  INTENT_BREAKDOWN,
} from '../../data/mockData';
import type { DailyVolume } from '../../data/mockData';

const BRAND_RED = '#C41E2A';

// For response time and escalation rate, a DECREASE is an improvement
function isDeltaPositive(key: string, delta: number): boolean {
  const inverseMetrics = ['avgResponseTime', 'escalationRate'];
  if (inverseMetrics.includes(key)) {
    return delta < 0;
  }
  return delta > 0;
}

function formatDelta(delta: number, suffix: string = '%'): string {
  const sign = delta > 0 ? '+' : '';
  return `${sign}${delta}${suffix}`;
}

function formatChartDate(dateStr: string): string {
  const d = new Date(dateStr);
  return `${d.getMonth() + 1}/${d.getDate()}`;
}

// Filter daily volumes by period
function filterByPeriod(data: DailyVolume[], days: number): DailyVolume[] {
  return data.slice(-days);
}

// Scale analytics summary based on selected period (simulates period change)
function scaleForPeriod(days: number): number {
  switch (days) {
    case 7: return 0.23;
    case 14: return 0.47;
    case 30: return 1.0;
    case 90: return 3.1;
    default: return 1.0;
  }
}

function trendArrow(trend: 'up' | 'down' | 'stable'): string {
  if (trend === 'up') return '\u2191 Up';
  if (trend === 'down') return '\u2193 Down';
  return '\u2192 Stable';
}

interface MetricCardProps {
  title: string;
  value: string;
  delta: number;
  deltaKey: string;
  deltaSuffix?: string;
  detail?: string;
}

function MetricCard({ title, value, delta, deltaKey, deltaSuffix = '%', detail }: MetricCardProps) {
  const positive = isDeltaPositive(deltaKey, delta);
  return (
    <LegacyCard sectioned>
      <BlockStack gap="200">
        <Text as="p" variant="bodySm" tone="subdued">
          {title}
        </Text>
        <InlineStack align="space-between" blockAlign="end">
          <Text as="p" variant="headingXl" fontWeight="bold">
            {value}
          </Text>
          <Badge tone={positive ? 'success' : 'critical'}>
            {formatDelta(delta, deltaSuffix)}
          </Badge>
        </InlineStack>
        {detail && (
          <Text as="p" variant="bodySm" tone="subdued">
            {detail}
          </Text>
        )}
      </BlockStack>
    </LegacyCard>
  );
}

// Knowledge gap suggestions based on low-confidence or trending intents
const KNOWLEDGE_GAPS = [
  {
    id: 'gap-1',
    title: 'International Return Process',
    reason: 'High volume "Return/Exchange" queries from international customers lack specific guidance',
    intent: 'Return/Exchange',
    priority: 'high' as const,
    estimatedImpact: '+4% resolution rate',
  },
  {
    id: 'gap-2',
    title: 'Bulk Order Customization Options',
    reason: '"Bulk/Corporate" intent has lowest confidence (0.85) and is trending up',
    intent: 'Bulk/Corporate',
    priority: 'high' as const,
    estimatedImpact: '+8% confidence',
  },
  {
    id: 'gap-3',
    title: 'Account Recovery Self-Service',
    reason: '"Account Issues" intent has 0.89 confidence -- most escalations come from password reset flow',
    intent: 'Account Issues',
    priority: 'medium' as const,
    estimatedImpact: '-3% escalation rate',
  },
  {
    id: 'gap-4',
    title: 'Holiday Shipping Deadlines FAQ',
    reason: 'Seasonal spike in "Shipping Inquiry" expected; proactive article reduces volume',
    intent: 'Shipping Inquiry',
    priority: 'low' as const,
    estimatedImpact: '-12% shipping queries',
  },
];

const priorityToneMap: Record<string, 'critical' | 'attention' | 'info'> = {
  high: 'critical',
  medium: 'attention',
  low: 'info',
};

const PERIOD_TABS = [
  { id: '7', content: '7 days' },
  { id: '14', content: '14 days' },
  { id: '30', content: '30 days' },
  { id: '90', content: '90 days' },
];

export function ShopifyAnalytics() {
  const [selectedTab, setSelectedTab] = useState(2); // Default to 30 days
  const handleTabChange = useCallback((index: number) => setSelectedTab(index), []);

  const days = parseInt(PERIOD_TABS[selectedTab].id, 10);
  const summary = ANALYTICS_SUMMARY;
  const scale = scaleForPeriod(days);
  const chartData = filterByPeriod(DAILY_VOLUMES, days);

  // Scale total conversations for period, keep rates unchanged
  const scaledTotal = Math.round(summary.totalConversations * scale);

  // Build DataTable rows for intent breakdown
  const intentRows = INTENT_BREAKDOWN.map((intent) => [
    intent.intent,
    intent.count,
    `${intent.percentage}%`,
    `${(intent.avgConfidence * 100).toFixed(0)}%`,
    trendArrow(intent.trend),
  ]);

  const periodLabel =
    days === 7 ? 'Last 7 days' :
    days === 14 ? 'Last 14 days' :
    days === 90 ? 'Last 90 days' :
    'Last 30 days';

  return (
    <Page title="Analytics">
      <Layout>
        {/* Info banner */}
        <Layout.Section>
          <Banner tone="info">
            Analytics data is updated every 15 minutes.
          </Banner>
        </Layout.Section>

        {/* Period tabs */}
        <Layout.Section>
          <Tabs tabs={PERIOD_TABS} selected={selectedTab} onSelect={handleTabChange} />
        </Layout.Section>

        {/* Metric cards - 3x2 grid */}
        <Layout.Section>
          <InlineStack gap="400" wrap={true}>
            <div style={{ flex: '1 1 30%', minWidth: 220 }}>
              <MetricCard
                title="Total Conversations"
                value={scaledTotal.toLocaleString()}
                delta={summary.totalConversationsDelta}
                deltaKey="totalConversations"
                detail={`${Math.round(scaledTotal * 0.85).toLocaleString()} billable`}
              />
            </div>
            <div style={{ flex: '1 1 30%', minWidth: 220 }}>
              <MetricCard
                title="Avg Response Time"
                value={`${summary.avgResponseTime}s`}
                delta={summary.avgResponseTimeDelta}
                deltaKey="avgResponseTime"
                detail="P50: 1.2s | P95: 1.9s | P99: 3.8s"
              />
            </div>
            <div style={{ flex: '1 1 30%', minWidth: 220 }}>
              <MetricCard
                title="Resolution Rate"
                value={`${summary.resolutionRate}%`}
                delta={summary.resolutionRateDelta}
                deltaKey="resolutionRate"
                detail={`${Math.round(scaledTotal * summary.resolutionRate / 100).toLocaleString()} resolved`}
              />
            </div>
          </InlineStack>
        </Layout.Section>

        <Layout.Section>
          <InlineStack gap="400" wrap={true}>
            <div style={{ flex: '1 1 30%', minWidth: 220 }}>
              <MetricCard
                title="Customer Satisfaction"
                value={`${summary.customerSatisfaction}/5`}
                delta={summary.customerSatisfactionDelta}
                deltaKey="customerSatisfaction"
                deltaSuffix=""
                detail="Based on 847 ratings"
              />
            </div>
            <div style={{ flex: '1 1 30%', minWidth: 220 }}>
              <MetricCard
                title="AI Handled"
                value={`${summary.aiHandledRate}%`}
                delta={summary.aiHandledRateDelta}
                deltaKey="aiHandledRate"
                detail={`${Math.round(scaledTotal * summary.aiHandledRate / 100).toLocaleString()} conversations`}
              />
            </div>
            <div style={{ flex: '1 1 30%', minWidth: 220 }}>
              <MetricCard
                title="Escalation Rate"
                value={`${summary.escalationRate}%`}
                delta={summary.escalationRateDelta}
                deltaKey="escalationRate"
                detail={`${Math.round(scaledTotal * summary.escalationRate / 100).toLocaleString()} escalated`}
              />
            </div>
          </InlineStack>
        </Layout.Section>

        {/* Full-width conversation volume chart */}
        <Layout.Section>
          <LegacyCard sectioned>
            <InlineStack align="space-between" blockAlign="center">
              <Text as="h2" variant="headingMd" fontWeight="semibold">
                Conversation Volume
              </Text>
              <Text as="span" variant="bodySm" tone="subdued">
                {periodLabel}
              </Text>
            </InlineStack>
            <Box paddingBlockStart="400">
              <div style={{ width: '100%', height: 340 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart
                    data={chartData}
                    margin={{ top: 8, right: 8, left: -10, bottom: 0 }}
                  >
                    <defs>
                      <linearGradient id="shopAnalGradTotal" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor={BRAND_RED} stopOpacity={0.15} />
                        <stop offset="95%" stopColor={BRAND_RED} stopOpacity={0} />
                      </linearGradient>
                      <linearGradient id="shopAnalGradBillable" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#2563EB" stopOpacity={0.12} />
                        <stop offset="95%" stopColor="#2563EB" stopOpacity={0} />
                      </linearGradient>
                      <linearGradient id="shopAnalGradAI" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#059669" stopOpacity={0.12} />
                        <stop offset="95%" stopColor="#059669" stopOpacity={0} />
                      </linearGradient>
                      <linearGradient id="shopAnalGradEscalated" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#D97706" stopOpacity={0.12} />
                        <stop offset="95%" stopColor="#D97706" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e1e3e5" />
                    <XAxis
                      dataKey="date"
                      tickFormatter={formatChartDate}
                      tick={{ fontSize: 11, fill: '#6d7175' }}
                      axisLine={{ stroke: '#c9cccf' }}
                      tickLine={false}
                    />
                    <YAxis
                      tick={{ fontSize: 11, fill: '#6d7175' }}
                      axisLine={{ stroke: '#c9cccf' }}
                      tickLine={false}
                    />
                    <Tooltip
                      contentStyle={{
                        borderRadius: 8,
                        border: '1px solid #c9cccf',
                        fontSize: 12,
                        fontFamily: '-apple-system, BlinkMacSystemFont, "San Francisco", "Segoe UI", Roboto, sans-serif',
                      }}
                      labelFormatter={(label) => `Date: ${label}`}
                    />
                    <Area
                      type="monotone"
                      dataKey="total"
                      stroke={BRAND_RED}
                      strokeWidth={2}
                      fill="url(#shopAnalGradTotal)"
                      name="Total"
                    />
                    <Area
                      type="monotone"
                      dataKey="billable"
                      stroke="#2563EB"
                      strokeWidth={1.5}
                      fill="url(#shopAnalGradBillable)"
                      name="Billable"
                    />
                    <Area
                      type="monotone"
                      dataKey="aiResolved"
                      stroke="#059669"
                      strokeWidth={1.5}
                      fill="url(#shopAnalGradAI)"
                      name="AI Resolved"
                    />
                    <Area
                      type="monotone"
                      dataKey="escalated"
                      stroke="#D97706"
                      strokeWidth={1.5}
                      fill="url(#shopAnalGradEscalated)"
                      name="Escalated"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
              <div style={{ display: 'flex', justifyContent: 'center', gap: 20, marginTop: 8 }}>
                {[
                  { color: BRAND_RED, label: 'Total' },
                  { color: '#2563EB', label: 'Billable' },
                  { color: '#059669', label: 'AI Resolved' },
                  { color: '#D97706', label: 'Escalated' },
                ].map((item) => (
                  <InlineStack gap="100" key={item.label} blockAlign="center">
                    <div
                      style={{
                        width: 10,
                        height: 10,
                        borderRadius: 2,
                        backgroundColor: item.color,
                      }}
                    />
                    <Text as="span" variant="bodySm" tone="subdued">
                      {item.label}
                    </Text>
                  </InlineStack>
                ))}
              </div>
            </Box>
          </LegacyCard>
        </Layout.Section>

        {/* Intent Breakdown DataTable */}
        <Layout.Section>
          <LegacyCard title="Intent Breakdown">
            <DataTable
              columnContentTypes={['text', 'numeric', 'text', 'text', 'text']}
              headings={['Intent', 'Count', '% of Total', 'Avg Confidence', 'Trend']}
              rows={intentRows}
              sortable={[true, true, true, true, false]}
              defaultSortDirection="descending"
              initialSortColumnIndex={1}
            />
          </LegacyCard>
        </Layout.Section>

        {/* Knowledge Gaps */}
        <Layout.Section>
          <LegacyCard
            title="Knowledge Gaps"
            actions={[
              {
                content: `${KNOWLEDGE_GAPS.length} suggestions`,
              },
            ]}
          >
            <LegacyCard.Section>
              <Text as="p" variant="bodySm" tone="subdued">
                Suggested articles to create based on unresolved intents and low confidence areas
              </Text>
            </LegacyCard.Section>
            {KNOWLEDGE_GAPS.map((gap) => (
              <LegacyCard.Section key={gap.id}>
                <BlockStack gap="200">
                  <InlineStack align="space-between" blockAlign="center" wrap={false}>
                    <InlineStack gap="200" blockAlign="center">
                      <Text as="span" variant="bodyMd" fontWeight="semibold">
                        {gap.title}
                      </Text>
                      <Badge tone={priorityToneMap[gap.priority]}>
                        {gap.priority}
                      </Badge>
                      <Badge tone="info">
                        {gap.intent}
                      </Badge>
                    </InlineStack>
                    <Button onClick={() => {}}>
                      Create Article
                    </Button>
                  </InlineStack>
                  <Text as="p" variant="bodySm" tone="subdued">
                    {gap.reason}
                  </Text>
                  <Text as="p" variant="bodySm" tone="success">
                    Estimated impact: {gap.estimatedImpact}
                  </Text>
                </BlockStack>
              </LegacyCard.Section>
            ))}
          </LegacyCard>
        </Layout.Section>
      </Layout>
    </Page>
  );
}
