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
  ActionIcon,
  Alert,
  Badge,
  Button,
  Card,
  CopyButton,
  Group,
  Modal,
  Pagination,
  Paper,
  Select,
  SimpleGrid,
  Stack,
  Table,
  Text,
  TextInput,
  Title,
  Tooltip,
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

/** Response from POST /api/superadmin/tenants (P0-PROV-1). */
interface CreateTenantResponse {
  tenantId: string;
  status: string;
  tier: string;
  superadminEmail: string;
  superadminApiKey: string | null;
  widgetKey: string | null;
  warnings: string[];
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

const TIER_OPTIONS = [
  { value: 'trial', label: 'Trial' },
  { value: 'starter', label: 'Starter' },
  { value: 'professional', label: 'Professional' },
  { value: 'enterprise', label: 'Enterprise' },
];

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

  // Create Tenant modal state (P0-PROV-1)
  const [createOpen, setCreateOpen] = useState(false);
  const [createLoading, setCreateLoading] = useState(false);
  const [createResult, setCreateResult] = useState<CreateTenantResponse | null>(null);
  const [createForm, setCreateForm] = useState({
    merchantName: '',
    merchantUrl: '',
    superadminEmail: '',
    tier: 'starter',
  });

  const resetCreateForm = useCallback(() => {
    setCreateForm({ merchantName: '', merchantUrl: '', superadminEmail: '', tier: 'starter' });
    setCreateResult(null);
    setCreateLoading(false);
  }, []);

  const handleCreateSubmit = useCallback(async () => {
    if (!createForm.merchantName.trim() || !createForm.superadminEmail.trim()) {
      onNotify('Merchant Name and Superadmin Email are required', 'error');
      return;
    }
    setCreateLoading(true);
    try {
      const res = await apiFetch('/api/superadmin/tenants', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          merchantName: createForm.merchantName.trim(),
          merchantUrl: createForm.merchantUrl.trim() || null,
          superadminEmail: createForm.superadminEmail.trim(),
          tier: createForm.tier,
        }),
      });

      if (res.ok) {
        const data: CreateTenantResponse = await res.json();
        setCreateResult(data);
        onNotify(`Tenant ${data.tenantId.slice(0, 8)}... created successfully`, 'success');
        // Trigger a re-fetch by resetting to page 1 (useEffect dependency)
        setPage(1);
      } else {
        const err = await res.json().catch(() => ({ detail: 'Unknown error' }));
        onNotify(`Failed to create tenant: ${err.detail || res.statusText}`, 'error');
      }
    } catch {
      onNotify('Network error creating tenant', 'error');
    } finally {
      setCreateLoading(false);
    }
  }, [apiFetch, createForm, onNotify]);

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
      <Group justify="space-between" align="center">
        <Title order={3} c={tokens.textPrimary}>Tenant Directory</Title>
        <Button color="action" onClick={() => { resetCreateForm(); setCreateOpen(true); }}>
          Create Tenant
        </Button>
      </Group>

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

      {/* Create Tenant Modal (P0-PROV-1) */}
      <Modal
        opened={createOpen}
        onClose={() => { setCreateOpen(false); resetCreateForm(); }}
        title={createResult ? 'Tenant Created' : 'Create New Tenant'}
        size="lg"
        centered
      >
        {createResult ? (
          /* ── Success: show credentials ── */
          <Stack gap="md">
            <Alert
              color={createResult.warnings.length > 0 ? 'orange' : 'green'}
              title={createResult.warnings.length > 0
                ? 'Tenant provisioned with warnings'
                : 'Tenant provisioned successfully'}
            >
              Tenant <Text span fw={600}>{createResult.tenantId.slice(0, 12)}...</Text> has status: {createResult.status}.
              {createResult.warnings.length > 0 && (
                <Text size="sm" c="orange" mt="xs">
                  {createResult.warnings.join('; ')}
                </Text>
              )}
            </Alert>

            <Paper withBorder p="md" radius="md" bg={tokens.surface}>
              <Stack gap="sm">
                <Text size="sm" fw={600} c={tokens.textPrimary}>Credentials — save these now (shown only once)</Text>

                {createResult.superadminApiKey && (
                  <Group gap="xs" align="center">
                    <TextInput
                      label="Superadmin API Key"
                      value={createResult.superadminApiKey}
                      readOnly
                      size="sm"
                      style={{ flex: 1 }}
                      styles={{ input: { fontFamily: 'monospace', fontSize: '12px' } }}
                    />
                    <CopyButton value={createResult.superadminApiKey}>
                      {({ copied, copy }) => (
                        <Tooltip label={copied ? 'Copied' : 'Copy'}>
                          <ActionIcon color={copied ? 'green' : 'action'} onClick={copy} mt={24} variant="subtle">
                            {copied ? '✓' : '📋'}
                          </ActionIcon>
                        </Tooltip>
                      )}
                    </CopyButton>
                  </Group>
                )}

                {createResult.widgetKey && (
                  <Group gap="xs" align="center">
                    <TextInput
                      label="Widget Key"
                      value={createResult.widgetKey}
                      readOnly
                      size="sm"
                      style={{ flex: 1 }}
                      styles={{ input: { fontFamily: 'monospace', fontSize: '12px' } }}
                    />
                    <CopyButton value={createResult.widgetKey}>
                      {({ copied, copy }) => (
                        <Tooltip label={copied ? 'Copied' : 'Copy'}>
                          <ActionIcon color={copied ? 'green' : 'action'} onClick={copy} mt={24} variant="subtle">
                            {copied ? '✓' : '📋'}
                          </ActionIcon>
                        </Tooltip>
                      )}
                    </CopyButton>
                  </Group>
                )}

                <Group gap="xs">
                  <Text size="xs" c="dimmed">Tenant ID:</Text>
                  <Text size="xs" ff="monospace" c={tokens.textMuted}>{createResult.tenantId}</Text>
                </Group>
                <Group gap="xs">
                  <Text size="xs" c="dimmed">Status:</Text>
                  <Badge size="xs" color={createResult.status === 'active' ? 'green' : 'orange'}>{createResult.status}</Badge>
                </Group>
                <Group gap="xs">
                  <Text size="xs" c="dimmed">Tier:</Text>
                  <Badge size="xs" variant="outline">{createResult.tier}</Badge>
                </Group>
              </Stack>
            </Paper>

            <Button
              color="action"
              onClick={() => { setCreateOpen(false); resetCreateForm(); }}
              fullWidth
            >
              Done
            </Button>
          </Stack>
        ) : (
          /* ── Form: create tenant ── */
          <Stack gap="md">
            <TextInput
              label="Merchant Name"
              placeholder="Harrison Corporation"
              required
              value={createForm.merchantName}
              onChange={(e) => setCreateForm(f => ({ ...f, merchantName: e.currentTarget.value }))}
              disabled={createLoading}
            />
            <TextInput
              label="Merchant URL"
              placeholder="harrisoncorp.com (optional)"
              value={createForm.merchantUrl}
              onChange={(e) => setCreateForm(f => ({ ...f, merchantUrl: e.currentTarget.value }))}
              disabled={createLoading}
            />
            <TextInput
              label="Superadmin Email"
              placeholder="admin@merchant.com"
              required
              type="email"
              value={createForm.superadminEmail}
              onChange={(e) => setCreateForm(f => ({ ...f, superadminEmail: e.currentTarget.value }))}
              disabled={createLoading}
            />
            <Select
              label="Tier"
              data={TIER_OPTIONS}
              value={createForm.tier}
              onChange={(v) => setCreateForm(f => ({ ...f, tier: v || 'starter' }))}
              required
              disabled={createLoading}
            />

            <Group justify="flex-end" mt="sm">
              <Button
                variant="subtle"
                onClick={() => { setCreateOpen(false); resetCreateForm(); }}
                disabled={createLoading}
              >
                Cancel
              </Button>
              <Button
                color="action"
                onClick={handleCreateSubmit}
                loading={createLoading}
              >
                Create Tenant
              </Button>
            </Group>
          </Stack>
        )}
      </Modal>
    </Stack>
  );
}
