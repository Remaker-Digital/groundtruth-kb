/**
 * BillingHealth — Cross-tenant billing reconciliation dashboard.
 *
 * Shows per-tenant billing health with color-coded status indicators,
 * discrepancy percentages, and overall webhook success rate.
 *
 * API: GET /api/superadmin/billing/health
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useEffect, useState } from 'react';
import {
  Badge,
  Card,
  Group,
  Paper,
  Progress,
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
// Types (camelCase — matches CamelCaseModel API serialization)
// ---------------------------------------------------------------------------

interface TenantBillingHealth {
  tenantId: string;
  tier: string | null;
  status: string;
  reconciliationStatus: string;
  lastReconciliation: string | null;
  discrepancyPercent: number | null;
  needsReview: boolean;
}

interface BillingHealthResponse {
  timestamp: string;
  tenants: TenantBillingHealth[];
  totalTenants: number;
  tenantsNeedingReview: number;
  webhookSuccessRate: number | null;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const STATUS_COLORS: Record<string, string> = {
  healthy: 'green',
  review_needed: 'orange',
  unknown: 'gray',
};

const RECONCILIATION_LABELS: Record<string, string> = {
  not_available: 'N/A',
  reconciled: 'Reconciled',
  check_failed: 'Check Failed',
};

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function BillingHealthPage() {
  const { apiFetch, onNotify } = useProviderContext();
  const [data, setData] = useState<BillingHealthResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await apiFetch('/api/superadmin/billing/health');
        if (res.ok && !cancelled) {
          setData(await res.json());
        } else if (!cancelled) {
          onNotify('Failed to load billing health', 'error');
        }
      } catch {
        if (!cancelled) onNotify('Network error loading billing health', 'error');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [apiFetch, onNotify]);

  if (loading) {
    return <LoadingState text="Loading billing health" />;
  }

  if (!data) {
    return (
      <Text c="dimmed" ta="center" mt="xl">
        Unable to load billing health data.
      </Text>
    );
  }

  const webhookPct = data.webhookSuccessRate != null
    ? Math.round(data.webhookSuccessRate * 100)
    : null;

  return (
    <Stack gap="lg">
      <Group justify="space-between" align="baseline">
        <Title order={3} c={tokens.textPrimary}>Billing Health</Title>
        <Text c="dimmed" size="xs">
          Updated {new Date(data.timestamp).toLocaleString()}
        </Text>
      </Group>

      {/* Summary cards */}
      <SimpleGrid cols={{ base: 1, sm: 3 }} spacing="md">
        <Card withBorder padding="lg" radius="md" bg={tokens.surface}>
          <Text c="dimmed" size="xs" tt="uppercase" fw={600}>Total Tenants</Text>
          <Text fw={700} size="xl" c={tokens.textPrimary} mt={4}>{data.totalTenants}</Text>
        </Card>
        <Card withBorder padding="lg" radius="md" bg={tokens.surface}>
          <Text c="dimmed" size="xs" tt="uppercase" fw={600}>Needing Review</Text>
          <Text
            fw={700}
            size="xl"
            c={data.tenantsNeedingReview > 0 ? tokens.warning : tokens.success}
            mt={4}
          >
            {data.tenantsNeedingReview}
          </Text>
        </Card>
        <Card withBorder padding="lg" radius="md" bg={tokens.surface}>
          <Text c="dimmed" size="xs" tt="uppercase" fw={600}>Webhook Success Rate</Text>
          {webhookPct != null ? (
            <>
              <Text fw={700} size="xl" c={tokens.textPrimary} mt={4}>{webhookPct}%</Text>
              <Progress
                value={webhookPct}
                color={webhookPct >= 99 ? 'green' : webhookPct >= 95 ? 'yellow' : 'red'}
                size="sm"
                mt="xs"
              />
            </>
          ) : (
            <Text c="dimmed" size="sm" mt={4}>Not available</Text>
          )}
        </Card>
      </SimpleGrid>

      {/* Tenant billing table */}
      <Paper withBorder radius="md" bg={tokens.surface} style={{ overflow: 'auto' }}>
        <Table striped highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Tenant ID</Table.Th>
              <Table.Th>Tier</Table.Th>
              <Table.Th>Status</Table.Th>
              <Table.Th>Reconciliation</Table.Th>
              <Table.Th>Discrepancy</Table.Th>
              <Table.Th>Last Check</Table.Th>
              <Table.Th>Review</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {data.tenants.length === 0 ? (
              <Table.Tr>
                <Table.Td colSpan={7}>
                  <Text c="dimmed" ta="center" py="md">No billing data available</Text>
                </Table.Td>
              </Table.Tr>
            ) : (
              data.tenants.map((t) => (
                <Table.Tr key={t.tenantId}>
                  <Table.Td>
                    <Text size="xs" ff="monospace" style={{ color: tokens.textPrimary }}>{t.tenantId}</Text>
                  </Table.Td>
                  <Table.Td>
                    <Text size="xs" c={tokens.textMuted}>{t.tier ?? '—'}</Text>
                  </Table.Td>
                  <Table.Td>
                    <Badge
                      variant="light"
                      color={STATUS_COLORS[t.status] ?? 'gray'}
                      size="sm"
                    >
                      {t.status}
                    </Badge>
                  </Table.Td>
                  <Table.Td>
                    <Text size="xs" c={tokens.textMuted}>
                      {RECONCILIATION_LABELS[t.reconciliationStatus] ?? t.reconciliationStatus}
                    </Text>
                  </Table.Td>
                  <Table.Td>
                    {t.discrepancyPercent != null ? (
                      <Text
                        size="xs"
                        fw={500}
                        c={Math.abs(t.discrepancyPercent) > 5 ? tokens.warning : tokens.success}
                      >
                        {t.discrepancyPercent.toFixed(1)}%
                      </Text>
                    ) : (
                      <Text size="xs" c="dimmed">—</Text>
                    )}
                  </Table.Td>
                  <Table.Td>
                    <Text size="xs" c="dimmed">
                      {t.lastReconciliation
                        ? new Date(t.lastReconciliation).toLocaleDateString()
                        : '—'}
                    </Text>
                  </Table.Td>
                  <Table.Td>
                    {t.needsReview && (
                      <Badge variant="filled" color="orange" size="xs">
                        Review
                      </Badge>
                    )}
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
