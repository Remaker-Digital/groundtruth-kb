// (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

import React from 'react';
import {
  Page,
  Layout,
  LegacyCard,
  Text,
  Badge,
  DataTable,
  ResourceList,
  ResourceItem,
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
  CONVERSATIONS,
  INTENT_BREAKDOWN,
} from '../../data/mockData';

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

const statusBadgeMap: Record<string, 'success' | 'attention' | 'info' | 'critical'> = {
  active: 'info',
  waiting: 'attention',
  resolved: 'success',
  escalated: 'critical',
};

interface MetricCardProps {
  title: string;
  value: string;
  delta: number;
  deltaKey: string;
  deltaSuffix?: string;
}

function MetricCard({ title, value, delta, deltaKey, deltaSuffix = '%' }: MetricCardProps) {
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
      </BlockStack>
    </LegacyCard>
  );
}

export function ShopifyDashboard() {
  const summary = ANALYTICS_SUMMARY;
  const recentConversations = CONVERSATIONS.slice(0, 5);

  // Build DataTable rows for intent breakdown
  const intentRows = INTENT_BREAKDOWN.map((intent) => [
    intent.intent,
    intent.count,
    `${(intent.avgConfidence * 100).toFixed(0)}%`,
  ]);

  return (
    <Page
      title="Dashboard"
      subtitle="Overview of your AI customer experience"
    >
      <Layout>
        {/* Top row: 3 key metric cards */}
        <Layout.Section>
          <InlineStack gap="400" wrap={true}>
            <div style={{ flex: '1 1 30%', minWidth: 220 }}>
              <MetricCard
                title="Total Conversations"
                value={summary.totalConversations.toLocaleString()}
                delta={summary.totalConversationsDelta}
                deltaKey="totalConversations"
              />
            </div>
            <div style={{ flex: '1 1 30%', minWidth: 220 }}>
              <MetricCard
                title="AI Handled"
                value={`${summary.aiHandledRate}%`}
                delta={summary.aiHandledRateDelta}
                deltaKey="aiHandledRate"
              />
            </div>
            <div style={{ flex: '1 1 30%', minWidth: 220 }}>
              <MetricCard
                title="Satisfaction"
                value={`${summary.customerSatisfaction}/5`}
                delta={summary.customerSatisfactionDelta}
                deltaKey="customerSatisfaction"
                deltaSuffix=""
              />
            </div>
          </InlineStack>
        </Layout.Section>

        {/* Second row: 3 more metric cards */}
        <Layout.Section>
          <InlineStack gap="400" wrap={true}>
            <div style={{ flex: '1 1 30%', minWidth: 220 }}>
              <MetricCard
                title="Resolution Rate"
                value={`${summary.resolutionRate}%`}
                delta={summary.resolutionRateDelta}
                deltaKey="resolutionRate"
              />
            </div>
            <div style={{ flex: '1 1 30%', minWidth: 220 }}>
              <MetricCard
                title="Avg Response"
                value={`${summary.avgResponseTime}s`}
                delta={summary.avgResponseTimeDelta}
                deltaKey="avgResponseTime"
              />
            </div>
            <div style={{ flex: '1 1 30%', minWidth: 220 }}>
              <MetricCard
                title="Escalation Rate"
                value={`${summary.escalationRate}%`}
                delta={summary.escalationRateDelta}
                deltaKey="escalationRate"
              />
            </div>
          </InlineStack>
        </Layout.Section>

        {/* Full-width conversation volume chart */}
        <Layout.Section>
          <LegacyCard title="Daily Conversation Volume (30 days)" sectioned>
            <div style={{ width: '100%', height: 320 }}>
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart
                  data={DAILY_VOLUMES}
                  margin={{ top: 8, right: 8, left: -10, bottom: 0 }}
                >
                  <defs>
                    <linearGradient id="shopDashGradTotal" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={BRAND_RED} stopOpacity={0.15} />
                      <stop offset="95%" stopColor={BRAND_RED} stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="shopDashGradBillable" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#2563EB" stopOpacity={0.12} />
                      <stop offset="95%" stopColor="#2563EB" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="shopDashGradAI" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#059669" stopOpacity={0.12} />
                      <stop offset="95%" stopColor="#059669" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="shopDashGradEscalated" x1="0" y1="0" x2="0" y2="1">
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
                    fill="url(#shopDashGradTotal)"
                    name="Total"
                  />
                  <Area
                    type="monotone"
                    dataKey="billable"
                    stroke="#2563EB"
                    strokeWidth={1.5}
                    fill="url(#shopDashGradBillable)"
                    name="Billable"
                  />
                  <Area
                    type="monotone"
                    dataKey="aiResolved"
                    stroke="#059669"
                    strokeWidth={1.5}
                    fill="url(#shopDashGradAI)"
                    name="AI Resolved"
                  />
                  <Area
                    type="monotone"
                    dataKey="escalated"
                    stroke="#D97706"
                    strokeWidth={1.5}
                    fill="url(#shopDashGradEscalated)"
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
          </LegacyCard>
        </Layout.Section>

        {/* Bottom section: Recent conversations (left) + Intent breakdown (right) */}
        <Layout.Section variant="oneThird">
          <LegacyCard title="Recent Conversations">
            <ResourceList
              resourceName={{ singular: 'conversation', plural: 'conversations' }}
              items={recentConversations}
              renderItem={(item) => {
                const { id, customerName, subject, status, updatedAt } = item;
                const timeStr = new Date(updatedAt).toLocaleTimeString([], {
                  hour: '2-digit',
                  minute: '2-digit',
                });
                return (
                  <ResourceItem
                    id={id}
                    onClick={() => {}}
                    accessibilityLabel={`View conversation with ${customerName}`}
                  >
                    <InlineStack align="space-between" blockAlign="start" wrap={false}>
                      <BlockStack gap="100">
                        <Text as="span" variant="bodyMd" fontWeight="semibold">
                          {customerName}
                        </Text>
                        <Text as="span" variant="bodySm" tone="subdued" truncate>
                          {subject}
                        </Text>
                      </BlockStack>
                      <BlockStack gap="100" align="end">
                        <Badge tone={statusBadgeMap[status] || 'info'}>
                          {status}
                        </Badge>
                        <Text as="span" variant="bodySm" tone="subdued">
                          {timeStr}
                        </Text>
                      </BlockStack>
                    </InlineStack>
                  </ResourceItem>
                );
              }}
            />
          </LegacyCard>
        </Layout.Section>

        <Layout.Section>
          <LegacyCard title="Intent Breakdown">
            <DataTable
              columnContentTypes={['text', 'numeric', 'text']}
              headings={['Intent', 'Count', 'Confidence']}
              rows={intentRows}
              sortable={[true, true, true]}
              defaultSortDirection="descending"
              initialSortColumnIndex={1}
            />
          </LegacyCard>
        </Layout.Section>
      </Layout>
    </Page>
  );
}
