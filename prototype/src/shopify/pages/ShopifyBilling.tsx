// (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

import React from 'react';
import {
  Page,
  Layout,
  LegacyCard,
  DataTable,
  Badge,
  Button,
  Text,
  Banner,
  Box,
  InlineStack,
  BlockStack,
  Divider,
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
import { USAGE_DASHBOARD, INVOICES } from '../../data/mockData';

const BRAND_RED = '#C41E2A';

function formatChartDate(dateStr: string): string {
  const d = new Date(dateStr);
  return `${d.getMonth() + 1}/${d.getDate()}`;
}

function ProgressBar({ value, max, color }: { value: number; max: number; color: string }) {
  const pct = Math.min((value / max) * 100, 100);
  return (
    <div
      style={{
        width: '100%',
        height: 8,
        borderRadius: 4,
        background: '#e4e5e7',
        overflow: 'hidden',
      }}
    >
      <div
        style={{
          width: `${pct}%`,
          height: '100%',
          borderRadius: 4,
          background: color,
          transition: 'width 0.3s ease',
        }}
      />
    </div>
  );
}

interface PackCardProps {
  conversations: string;
  price: string;
  rate: string;
}

function PackCard({ conversations, price, rate }: PackCardProps) {
  return (
    <div style={{ flex: '1 1 30%', minWidth: 180 }}>
      <LegacyCard sectioned>
        <BlockStack gap="300">
          <Text as="p" variant="headingMd" fontWeight="bold" alignment="center">
            {conversations}
          </Text>
          <Text as="p" variant="bodySm" tone="subdued" alignment="center">
            conversations
          </Text>
          <Divider />
          <Text as="p" variant="headingLg" fontWeight="bold" alignment="center">
            {price}
          </Text>
          <Text as="p" variant="bodySm" tone="subdued" alignment="center">
            {rate}/conv
          </Text>
          <Button fullWidth>Purchase</Button>
          <Text as="p" variant="bodySm" tone="subdued" alignment="center">
            Valid for 90 days
          </Text>
        </BlockStack>
      </LegacyCard>
    </div>
  );
}

export function ShopifyBilling() {
  const usage = USAGE_DASHBOARD;

  const statusBadgeMap: Record<string, 'success' | 'attention' | 'critical'> = {
    paid: 'success',
    pending: 'attention',
    failed: 'critical',
  };

  // Build invoice table rows
  const invoiceRows = INVOICES.map((inv) => [
    inv.date,
    inv.description,
    `$${inv.amount.toFixed(2)}`,
    <Badge key={inv.id} tone={statusBadgeMap[inv.status] || 'attention'}>
      {inv.status.charAt(0).toUpperCase() + inv.status.slice(1)}
    </Badge>,
    <Button key={`dl-${inv.id}`} variant="plain" url={inv.pdfUrl}>
      Download
    </Button>,
  ]);

  return (
    <Page title="Billing & Usage">
      <Layout>
        {/* Plan Info */}
        <Layout.Section>
          <LegacyCard sectioned>
            <BlockStack gap="400">
              <InlineStack align="space-between" blockAlign="center" wrap={true}>
                <InlineStack gap="300" blockAlign="center">
                  <Text as="span" variant="headingLg" fontWeight="bold">
                    {usage.billing.plan} Plan
                  </Text>
                  <Badge tone="success">Active</Badge>
                </InlineStack>
                <InlineStack gap="200">
                  <Button>Manage Subscription</Button>
                  <Button variant="plain">Change Plan</Button>
                </InlineStack>
              </InlineStack>

              <InlineStack gap="400" wrap={true}>
                <Text as="span" variant="headingXl" fontWeight="bold">
                  ${usage.billing.monthlyBase}/mo
                </Text>
                <Text as="span" variant="bodyMd" tone="subdued">
                  Next invoice: {new Date(usage.billing.nextInvoice).toLocaleDateString('en-US', {
                    month: 'long',
                    day: 'numeric',
                    year: 'numeric',
                  })}
                </Text>
              </InlineStack>

              <Banner tone="info">
                In Shopify embedded apps, subscription management is handled through the Shopify Billing API.
                Plan changes and payment updates are managed via your Shopify admin.
              </Banner>
            </BlockStack>
          </LegacyCard>
        </Layout.Section>

        {/* Usage Metrics: 4 cards in a row */}
        <Layout.Section>
          <InlineStack gap="400" wrap={true}>
            {/* Conversations */}
            <div style={{ flex: '1 1 22%', minWidth: 180 }}>
              <LegacyCard sectioned>
                <BlockStack gap="200">
                  <Text as="p" variant="bodySm" tone="subdued">
                    Conversations
                  </Text>
                  <Text as="p" variant="headingXl" fontWeight="bold">
                    {usage.currentPeriod.used.toLocaleString()}
                  </Text>
                  <Text as="p" variant="bodySm" tone="subdued">
                    of {usage.currentPeriod.included.toLocaleString()} included
                  </Text>
                  <ProgressBar
                    value={usage.currentPeriod.used}
                    max={usage.currentPeriod.included}
                    color={usage.currentPeriod.percentUsed > 90 ? '#D72C0D' : usage.currentPeriod.percentUsed > 75 ? '#FFC453' : BRAND_RED}
                  />
                  <Text as="p" variant="bodySm" tone="subdued">
                    {usage.currentPeriod.percentUsed}% used
                  </Text>
                </BlockStack>
              </LegacyCard>
            </div>

            {/* Pack Balance */}
            <div style={{ flex: '1 1 22%', minWidth: 180 }}>
              <LegacyCard sectioned>
                <BlockStack gap="200">
                  <Text as="p" variant="bodySm" tone="subdued">
                    Pack Balance
                  </Text>
                  <Text as="p" variant="headingXl" fontWeight="bold">
                    {usage.currentPeriod.packBalance.toLocaleString()}
                  </Text>
                  <Text as="p" variant="bodySm" tone="subdued">
                    conversations remaining
                  </Text>
                </BlockStack>
              </LegacyCard>
            </div>

            {/* Overage */}
            <div style={{ flex: '1 1 22%', minWidth: 180 }}>
              <LegacyCard sectioned>
                <BlockStack gap="200">
                  <Text as="p" variant="bodySm" tone="subdued">
                    Overage
                  </Text>
                  <Text as="p" variant="headingXl" fontWeight="bold">
                    ${usage.currentPeriod.overage.toFixed(2)}
                  </Text>
                  <Text as="p" variant="bodySm" tone="subdued">
                    this billing period
                  </Text>
                </BlockStack>
              </LegacyCard>
            </div>

            {/* Estimated Invoice */}
            <div style={{ flex: '1 1 22%', minWidth: 180 }}>
              <LegacyCard sectioned>
                <BlockStack gap="200">
                  <Text as="p" variant="bodySm" tone="subdued">
                    Estimated Invoice
                  </Text>
                  <Text as="p" variant="headingXl" fontWeight="bold">
                    ${(usage.billing.monthlyBase + usage.billing.currentOverage).toFixed(2)}
                  </Text>
                  <Text as="p" variant="bodySm" tone="subdued">
                    base + overage
                  </Text>
                </BlockStack>
              </LegacyCard>
            </div>
          </InlineStack>
        </Layout.Section>

        {/* Daily Usage Chart */}
        <Layout.Section>
          <LegacyCard title="Daily Usage (30 days)" sectioned>
            <div style={{ width: '100%', height: 300 }}>
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart
                  data={usage.dailyUsage}
                  margin={{ top: 8, right: 8, left: -10, bottom: 0 }}
                >
                  <defs>
                    <linearGradient id="billingGradTotal" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={BRAND_RED} stopOpacity={0.15} />
                      <stop offset="95%" stopColor={BRAND_RED} stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="billingGradBillable" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#2563EB" stopOpacity={0.12} />
                      <stop offset="95%" stopColor="#2563EB" stopOpacity={0} />
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
                    fill="url(#billingGradTotal)"
                    name="Total Conversations"
                  />
                  <Area
                    type="monotone"
                    dataKey="billable"
                    stroke="#2563EB"
                    strokeWidth={1.5}
                    fill="url(#billingGradBillable)"
                    name="Billable"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
            <div style={{ display: 'flex', justifyContent: 'center', gap: 20, marginTop: 8 }}>
              {[
                { color: BRAND_RED, label: 'Total' },
                { color: '#2563EB', label: 'Billable' },
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

        {/* Conversation Packs */}
        <Layout.Section>
          <Box paddingBlockEnd="200">
            <Text as="h2" variant="headingMd" fontWeight="bold">
              Conversation Packs
            </Text>
            <Text as="p" variant="bodySm" tone="subdued">
              Pre-purchase conversations at a discount. Packs are consumed before overage billing.
            </Text>
          </Box>
          <InlineStack gap="400" wrap={true}>
            <PackCard conversations="1,000" price="$29" rate="$0.029" />
            <PackCard conversations="5,000" price="$99" rate="$0.020" />
            <PackCard conversations="20,000" price="$249" rate="$0.012" />
          </InlineStack>
        </Layout.Section>

        {/* Invoice History */}
        <Layout.Section>
          <LegacyCard title="Invoice History">
            <DataTable
              columnContentTypes={['text', 'text', 'numeric', 'text', 'text']}
              headings={['Date', 'Description', 'Amount', 'Status', '']}
              rows={invoiceRows}
              sortable={[true, false, true, false, false]}
              defaultSortDirection="descending"
              initialSortColumnIndex={0}
            />
          </LegacyCard>
        </Layout.Section>
      </Layout>
    </Page>
  );
}
