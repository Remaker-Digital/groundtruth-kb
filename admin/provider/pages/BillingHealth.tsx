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

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface TenantBillingHealth {
  tenant_id: string;
  tier: string | null;
  status: string;
  reconciliation_status: string;
  last_reconciliation: string | null;
  discrepancy_percent: number | null;
  needs_review: boolean;
}

interface BillingHealthResponse {
  timestamp: string;
  tenants: TenantBillingHealth[];
  total_tenants: number;
  tenants_needing_review: number;
  webhook_success_rate: number | null;
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

  const webhookPct = data.webhook_success_rate != null
    ? Math.round(data.webhook_success_rate * 100)
    : null;

  return (
    <Stack gap="lg">
      <Group justify="space-between" align="baseline">
        <Title order={3} c="#fafaf9">Billing Health</Title>
        <Text c="dimmed" size="xs">
          Updated {new Date(data.timestamp).toLocaleString()}
        </Text>
      </Group>

      {/* Summary cards */}
      <SimpleGrid cols={{ base: 1, sm: 3 }} spacing="md">
        <Card withBorder padding="lg" radius="md" bg="#292524">
          <Text c="dimmed" size="xs" tt="uppercase" fw={600}>Total Tenants</Text>
          <Text fw={700} size="xl" c="#fafaf9" mt={4}>{data.total_tenants}</Text>
        </Card>
        <Card withBorder padding="lg" radius="md" bg="#292524">
          <Text c="dimmed" size="xs" tt="uppercase" fw={600}>Needing Review</Text>
          <Text
            fw={700}
            size="xl"
            c={data.tenants_needing_review > 0 ? '#E5A100' : '#0D7C3E'}
            mt={4}
          >
            {data.tenants_needing_review}
          </Text>
        </Card>
        <Card withBorder padding="lg" radius="md" bg="#292524">
          <Text c="dimmed" size="xs" tt="uppercase" fw={600}>Webhook Success Rate</Text>
          {webhookPct != null ? (
            <>
              <Text fw={700} size="xl" c="#fafaf9" mt={4}>{webhookPct}%</Text>
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
      <Paper withBorder radius="md" bg="#292524" style={{ overflow: 'auto' }}>
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
                <Table.Tr key={t.tenant_id}>
                  <Table.Td>
                    <Text size="xs" ff="monospace" c="#E0E0E0">{t.tenant_id}</Text>
                  </Table.Td>
                  <Table.Td>
                    <Text size="xs" c="#A0A0A0">{t.tier ?? '—'}</Text>
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
                    <Text size="xs" c="#A0A0A0">
                      {RECONCILIATION_LABELS[t.reconciliation_status] ?? t.reconciliation_status}
                    </Text>
                  </Table.Td>
                  <Table.Td>
                    {t.discrepancy_percent != null ? (
                      <Text
                        size="xs"
                        fw={500}
                        c={Math.abs(t.discrepancy_percent) > 5 ? '#E5A100' : '#0D7C3E'}
                      >
                        {t.discrepancy_percent.toFixed(1)}%
                      </Text>
                    ) : (
                      <Text size="xs" c="dimmed">—</Text>
                    )}
                  </Table.Td>
                  <Table.Td>
                    <Text size="xs" c="dimmed">
                      {t.last_reconciliation
                        ? new Date(t.last_reconciliation).toLocaleDateString()
                        : '—'}
                    </Text>
                  </Table.Td>
                  <Table.Td>
                    {t.needs_review && (
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
