/**
 * TenantDirectory — Cross-tenant directory with filtering and pagination.
 *
 * Shows tenant summary cards (total, by status, by tier) and a filterable
 * paginated table of all tenants.
 *
 * API:
 *   GET /api/superadmin/tenants          — paginated, filterable tenant list
 *   GET /api/superadmin/tenants/summary  — distribution aggregates
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useCallback, useEffect, useState } from 'react';
import {
  Badge,
  Card,
  Group,
  Pagination,
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

interface TenantSummary {
  totalTenants: number;
  byStatus: Record<string, number>;
  byTier: Record<string, number>;
  byBillingChannel: Record<string, number>;
}

interface TenantItem {
  tenantId: string;
  status: string;
  tier: string | null;
  billingChannel: string | null;
  customerEmail: string | null;
  shopifyShopDomain: string | null;
  createdAt: string | null;
  updatedAt: string | null;
  deactivatedAt: string | null;
  consentStatus: string | null;
}

interface TenantListResponse {
  tenants: TenantItem[];
  total: number;
  skip: number;
  limit: number;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const PAGE_SIZE = 25;

const STATUS_COLORS: Record<string, string> = {
  active: 'green',
  trial: 'blue',
  suspended: 'orange',
  deactivated: 'red',
  pending: 'yellow',
};

const TIER_COLORS: Record<string, string> = {
  STARTER: 'gray',
  PROFESSIONAL: 'blue',
  ENTERPRISE: 'violet',
};

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function TenantDirectoryPage() {
  const { apiFetch, onNotify } = useProviderContext();

  // Filters
  const [statusFilter, setStatusFilter] = useState<string | null>(null);
  const [tierFilter, setTierFilter] = useState<string | null>(null);
  const [channelFilter, setChannelFilter] = useState<string | null>(null);

  // Data
  const [summary, setSummary] = useState<TenantSummary | null>(null);
  const [tenants, setTenants] = useState<TenantItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);

  // Fetch summary on mount
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await apiFetch('/api/superadmin/tenants/summary');
        if (res.ok && !cancelled) setSummary(await res.json());
      } catch {
        // non-fatal
      }
    })();
    return () => { cancelled = true; };
  }, [apiFetch]);

  // Fetch tenant list on filter/page change
  const fetchTenants = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      params.set('skip', String((page - 1) * PAGE_SIZE));
      params.set('limit', String(PAGE_SIZE));
      if (statusFilter) params.set('status', statusFilter);
      if (tierFilter) params.set('tier', tierFilter);
      if (channelFilter) params.set('billing_channel', channelFilter);

      const res = await apiFetch(`/api/superadmin/tenants?${params.toString()}`);
      if (res.ok) {
        const data: TenantListResponse = await res.json();
        setTenants(data.tenants);
        setTotal(data.total);
      } else {
        onNotify('Failed to load tenants', 'error');
      }
    } catch {
      onNotify('Network error loading tenants', 'error');
    } finally {
      setLoading(false);
    }
  }, [apiFetch, onNotify, page, statusFilter, tierFilter, channelFilter]);

  useEffect(() => { fetchTenants(); }, [fetchTenants]);

  // Reset to page 1 when filters change
  useEffect(() => { setPage(1); }, [statusFilter, tierFilter, channelFilter]);

  const totalPages = Math.ceil(total / PAGE_SIZE);

  return (
    <Stack gap="lg">
      <Title order={3} c={tokens.textPrimary}>Tenant Directory</Title>

      {/* Summary cards */}
      {summary && (
        <SimpleGrid cols={{ base: 1, sm: 2, md: 4 }} spacing="md">
          <Card withBorder padding="lg" radius="md" bg={tokens.surface}>
            <Text c="dimmed" size="xs" tt="uppercase" fw={600}>Total Tenants</Text>
            <Text fw={700} size="xl" c={tokens.textPrimary} mt={4}>{summary.totalTenants}</Text>
          </Card>
          {Object.entries(summary.byStatus ?? {}).map(([status, count]) => (
            <Card key={status} withBorder padding="lg" radius="md" bg={tokens.surface}>
              <Text c="dimmed" size="xs" tt="uppercase" fw={600}>{status}</Text>
              <Text fw={700} size="xl" c={tokens.textPrimary} mt={4}>{count}</Text>
            </Card>
          ))}
        </SimpleGrid>
      )}

      {/* Filters */}
      <Paper withBorder p="md" radius="md" bg={tokens.surface}>
        <Group gap="md">
          <Select
            label="Status"
            placeholder="All statuses"
            clearable
            value={statusFilter}
            onChange={setStatusFilter}
            data={summary ? Object.keys(summary.byStatus ?? {}).map(s => ({ value: s, label: s })) : []}
            size="sm"
            w={180}
          />
          <Select
            label="Tier"
            placeholder="All tiers"
            clearable
            value={tierFilter}
            onChange={setTierFilter}
            data={summary ? Object.keys(summary.byTier ?? {}).map(t => ({ value: t, label: t })) : []}
            size="sm"
            w={180}
          />
          <Select
            label="Billing channel"
            placeholder="All channels"
            clearable
            value={channelFilter}
            onChange={setChannelFilter}
            data={summary ? Object.keys(summary.byBillingChannel ?? {}).map(c => ({ value: c, label: c })) : []}
            size="sm"
            w={180}
          />
          <Text c="dimmed" size="sm" mt="lg">
            {total} tenant{total !== 1 ? 's' : ''} found
          </Text>
        </Group>
      </Paper>

      {/* Table */}
      <Paper withBorder radius="md" bg={tokens.surface} style={{ overflow: 'auto' }}>
        {loading ? (
          <LoadingState text="Loading tenants" size={24} />
        ) : (
          <Table striped highlightOnHover>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Tenant ID</Table.Th>
                <Table.Th>Status</Table.Th>
                <Table.Th>Tier</Table.Th>
                <Table.Th>Channel</Table.Th>
                <Table.Th>Email</Table.Th>
                <Table.Th>Shop Domain</Table.Th>
                <Table.Th>Created</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {tenants.length === 0 ? (
                <Table.Tr>
                  <Table.Td colSpan={7}>
                    <Text c="dimmed" ta="center" py="md">No tenants found</Text>
                  </Table.Td>
                </Table.Tr>
              ) : (
                tenants.map((t) => (
                  <Table.Tr key={t.tenantId}>
                    <Table.Td>
                      <Text size="xs" ff="monospace" style={{ color: tokens.textPrimary }}>{t.tenantId}</Text>
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
                      {t.tier ? (
                        <Badge variant="outline" color={TIER_COLORS[t.tier] ?? 'gray'} size="sm">
                          {t.tier}
                        </Badge>
                      ) : (
                        <Text c="dimmed" size="xs">—</Text>
                      )}
                    </Table.Td>
                    <Table.Td>
                      <Text size="xs" c={tokens.textMuted}>{t.billingChannel ?? '—'}</Text>
                    </Table.Td>
                    <Table.Td>
                      <Text size="xs" c={tokens.textMuted}>{t.customerEmail ?? '—'}</Text>
                    </Table.Td>
                    <Table.Td>
                      <Text size="xs" c={tokens.textMuted}>{t.shopifyShopDomain ?? '—'}</Text>
                    </Table.Td>
                    <Table.Td>
                      <Text size="xs" c="dimmed">
                        {t.createdAt ? new Date(t.createdAt).toLocaleDateString() : '—'}
                      </Text>
                    </Table.Td>
                  </Table.Tr>
                ))
              )}
            </Table.Tbody>
          </Table>
        )}
      </Paper>

      {/* Pagination */}
      {totalPages > 1 && (
        <Group justify="center">
          <Pagination
            total={totalPages}
            value={page}
            onChange={setPage}
            color="action"
            size="sm"
          />
        </Group>
      )}
    </Stack>
  );
}
