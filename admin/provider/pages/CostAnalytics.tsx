/**
 * CostAnalytics — Per-tenant cost attribution and unit economics.
 *
 * Shows platform-wide cost overview with per-tenant breakdown by:
 * AI tokens, Cosmos DB RU, storage, and compute share.
 *
 * API: GET /api/superadmin/costs?days=N
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useEffect, useState } from 'react';
import {
  Badge,
  Card,
  Group,
  Paper,
  Select,
  SimpleGrid,
  Stack,
  Table,
  Text,
  Title,
} from '@mantine/core';
import { useProviderContext } from '../layouts/ProviderLayout';
import { LoadingState } from '../../shared/LoadingState';
import { tokens } from '../../shared/theme/styles';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface CostBreakdown {
  aiTokens: number;
  cosmosDb: number;
  storage: number;
  compute: number;
  total: number;
}

interface TenantCostProfile {
  tenantId: string;
  tier: string | null;
  periodStart: string;
  periodEnd: string;
  conversationCount: number;
  totalInputTokens: number;
  totalOutputTokens: number;
  articleCount: number;
  costBreakdown: CostBreakdown;
  costPerConversation: number;
  costSharePct: number;
}

interface CostOverview {
  periodStart: string;
  periodEnd: string;
  totalPlatformCost: number;
  totalConversations: number;
  totalTenants: number;
  avgCostPerTenant: number;
  avgCostPerConversation: number;
  tenants: TenantCostProfile[];
  costByTier: Record<string, number>;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatCost(value: number): string {
  return `$${value.toFixed(4)}`;
}

function formatTokens(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return String(n);
}

const PERIOD_OPTIONS = [
  { value: '7', label: 'Last 7 days' },
  { value: '30', label: 'Last 30 days' },
  { value: '90', label: 'Last 90 days' },
  { value: '365', label: 'Last year' },
];

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function CostAnalyticsPage() {
  const { apiFetch, onNotify } = useProviderContext();
  const [data, setData] = useState<CostOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState('30');

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    (async () => {
      try {
        const res = await apiFetch(`/api/superadmin/costs?days=${days}`);
        if (res.ok && !cancelled) {
          setData(await res.json());
        } else if (!cancelled) {
          onNotify('Failed to load cost analytics', 'error');
        }
      } catch {
        if (!cancelled) onNotify('Network error loading cost analytics', 'error');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [apiFetch, onNotify, days]);

  if (loading) {
    return <LoadingState text="Loading cost analytics" />;
  }

  if (!data) {
    return (
      <Text c="dimmed" ta="center" mt="xl">
        Unable to load cost analytics data.
      </Text>
    );
  }

  return (
    <Stack gap="lg">
      <Group justify="space-between" align="baseline">
        <Title order={3} c={tokens.textPrimary}>Cost Analytics</Title>
        <Select
          size="xs"
          data={PERIOD_OPTIONS}
          value={days}
          onChange={(v) => v && setDays(v)}
          w={160}
        />
      </Group>

      {/* Summary cards */}
      <SimpleGrid cols={{ base: 1, sm: 2, md: 4 }} spacing="md">
        <Card withBorder padding="lg" radius="md" bg={tokens.surface}>
          <Text c="dimmed" size="xs" tt="uppercase" fw={600}>Platform Cost</Text>
          <Text fw={700} size="xl" c={tokens.textPrimary} mt={4}>
            {formatCost(data.totalPlatformCost)}
          </Text>
        </Card>
        <Card withBorder padding="lg" radius="md" bg={tokens.surface}>
          <Text c="dimmed" size="xs" tt="uppercase" fw={600}>Total Conversations</Text>
          <Text fw={700} size="xl" c={tokens.textPrimary} mt={4}>
            {data.totalConversations.toLocaleString()}
          </Text>
        </Card>
        <Card withBorder padding="lg" radius="md" bg={tokens.surface}>
          <Text c="dimmed" size="xs" tt="uppercase" fw={600}>Avg / Tenant</Text>
          <Text fw={700} size="xl" c={tokens.textPrimary} mt={4}>
            {formatCost(data.avgCostPerTenant)}
          </Text>
        </Card>
        <Card withBorder padding="lg" radius="md" bg={tokens.surface}>
          <Text c="dimmed" size="xs" tt="uppercase" fw={600}>Avg / Conversation</Text>
          <Text fw={700} size="xl" c={tokens.textPrimary} mt={4}>
            {formatCost(data.avgCostPerConversation)}
          </Text>
        </Card>
      </SimpleGrid>

      {/* Tier breakdown */}
      {Object.keys(data.costByTier ?? {}).length > 0 && (
        <SimpleGrid cols={{ base: 1, sm: 3 }} spacing="md">
          {Object.entries(data.costByTier ?? {}).map(([tier, cost]) => (
            <Card key={tier} withBorder padding="md" radius="md" bg={tokens.surface}>
              <Group justify="space-between">
                <Text c="dimmed" size="xs" tt="uppercase" fw={600}>{tier}</Text>
                <Badge variant="light" color="blue" size="sm">{tier}</Badge>
              </Group>
              <Text fw={700} size="lg" c={tokens.textPrimary} mt={4}>{formatCost(cost)}</Text>
            </Card>
          ))}
        </SimpleGrid>
      )}

      {/* Per-tenant table */}
      <Paper withBorder radius="md" bg={tokens.surface} style={{ overflow: 'auto' }}>
        <Table striped highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Tenant</Table.Th>
              <Table.Th>Tier</Table.Th>
              <Table.Th ta="right">Conversations</Table.Th>
              <Table.Th ta="right">Input Tokens</Table.Th>
              <Table.Th ta="right">Output Tokens</Table.Th>
              <Table.Th ta="right">Articles</Table.Th>
              <Table.Th ta="right">AI Cost</Table.Th>
              <Table.Th ta="right">DB Cost</Table.Th>
              <Table.Th ta="right">Total</Table.Th>
              <Table.Th ta="right">Per Conv.</Table.Th>
              <Table.Th ta="right">Share</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {data.tenants.length === 0 ? (
              <Table.Tr>
                <Table.Td colSpan={11}>
                  <Text c="dimmed" ta="center" py="md">No tenant cost data available</Text>
                </Table.Td>
              </Table.Tr>
            ) : (
              data.tenants.map((t) => (
                <Table.Tr key={t.tenantId}>
                  <Table.Td>
                    <Text size="xs" ff="monospace" c={tokens.textSecondary}>{t.tenantId}</Text>
                  </Table.Td>
                  <Table.Td>
                    <Text size="xs" c={tokens.textMuted}>{t.tier ?? '—'}</Text>
                  </Table.Td>
                  <Table.Td ta="right">
                    <Text size="xs" c={tokens.textSecondary}>{t.conversationCount.toLocaleString()}</Text>
                  </Table.Td>
                  <Table.Td ta="right">
                    <Text size="xs" c={tokens.textMuted}>{formatTokens(t.totalInputTokens)}</Text>
                  </Table.Td>
                  <Table.Td ta="right">
                    <Text size="xs" c={tokens.textMuted}>{formatTokens(t.totalOutputTokens)}</Text>
                  </Table.Td>
                  <Table.Td ta="right">
                    <Text size="xs" c={tokens.textMuted}>{t.articleCount}</Text>
                  </Table.Td>
                  <Table.Td ta="right">
                    <Text size="xs" c={tokens.textSecondary}>{formatCost(t.costBreakdown.aiTokens)}</Text>
                  </Table.Td>
                  <Table.Td ta="right">
                    <Text size="xs" c={tokens.textSecondary}>{formatCost(t.costBreakdown.cosmosDb)}</Text>
                  </Table.Td>
                  <Table.Td ta="right">
                    <Text size="xs" fw={600} c={tokens.textPrimary}>{formatCost(t.costBreakdown.total)}</Text>
                  </Table.Td>
                  <Table.Td ta="right">
                    <Text size="xs" c={tokens.textMuted}>{formatCost(t.costPerConversation)}</Text>
                  </Table.Td>
                  <Table.Td ta="right">
                    <Text size="xs" c={tokens.textMuted}>{t.costSharePct.toFixed(1)}%</Text>
                  </Table.Td>
                </Table.Tr>
              ))
            )}
          </Table.Tbody>
        </Table>
      </Paper>
    </Stack>
  );
}
