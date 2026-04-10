// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * ComplianceDashboard — Cross-tenant compliance overview.
 *
 * PII scrubbing adoption, grace period tracking, DSAR request counts.
 * PII adoption progress bar, grace period rows highlighted.
 *
 * API: GET /api/superadmin/compliance
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
import { HelpTooltip } from '../../shared/HelpTooltip';
import { TenantName } from '../components/TenantName';
import { tokens } from '../../shared/theme/styles';

// ---------------------------------------------------------------------------
// Types (matches ComplianceSummaryResponse camelCase serialization)
// ---------------------------------------------------------------------------

interface TenantComplianceInfo {
  tenantId: string;
  tier: string | null;
  gracePeriodEndsAt: string | null;
  gracePeriodActive: boolean;
  piiScrubbingEnabled: boolean;
  dsarRequestCount: number;
  lastDsarRequest: string | null;
}

interface ComplianceSummaryResponse {
  totalTenants: number;
  tenantsWithPiiScrubbing: number;
  tenantsInGracePeriod: number;
  totalDsarRequests: number;
  tenants: TenantComplianceInfo[];
  errors: Array<{ tenantId: string; message: string }>;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function ComplianceDashboardPage() {
  const { apiFetch, onNotify, getTenantDisplay } = useProviderContext();
  const [data, setData] = useState<ComplianceSummaryResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await apiFetch('/api/superadmin/compliance');
        if (res.ok && !cancelled) {
          setData(await res.json());
        } else if (!cancelled) {
          onNotify('Failed to load compliance data', 'error');
        }
      } catch {
        if (!cancelled) onNotify('Network error loading compliance data', 'error');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [apiFetch, onNotify]);

  if (loading) {
    return <LoadingState text="Loading compliance data" />;
  }

  if (!data) {
    return (
      <Text c="dimmed" ta="center" mt="xl">
        Unable to load compliance data.
      </Text>
    );
  }

  const piiAdoptionPct = data.totalTenants > 0
    ? Math.round((data.tenantsWithPiiScrubbing / data.totalTenants) * 100)
    : 0;

  return (
    <Stack gap="lg">
      <Title order={3} c={tokens.textPrimary}>Compliance Dashboard</Title><HelpTooltip text="Cross-tenant compliance posture including PII scrubbing adoption and DSAR request tracking." />

      {/* Summary cards */}
      <SimpleGrid cols={{ base: 1, sm: 2, md: 4 }} spacing="md">
        <Card withBorder padding="lg" radius="md" bg={tokens.surface}>
          <Text c="dimmed" size="xs" tt="uppercase" fw={600}>Total Tenants</Text>
          <Text fw={700} size="xl" c={tokens.textPrimary} mt={4}>{data.totalTenants}</Text>
        </Card>
        <Card withBorder padding="lg" radius="md" bg={tokens.surface}>
          <Text c="dimmed" size="xs" tt="uppercase" fw={600}>PII Scrubbing Enabled</Text>
          <Text fw={700} size="xl" c={tokens.success} mt={4}>
            {data.tenantsWithPiiScrubbing}
          </Text>
          <Text c="dimmed" size="xs">{piiAdoptionPct}% adoption</Text>
        </Card>
        <Card withBorder padding="lg" radius="md" bg={tokens.surface}>
          <Text c="dimmed" size="xs" tt="uppercase" fw={600}>Grace Period Active</Text>
          <Text
            fw={700}
            size="xl"
            c={data.tenantsInGracePeriod > 0 ? tokens.warning : tokens.success}
            mt={4}
          >
            {data.tenantsInGracePeriod}
          </Text>
        </Card>
        <Card withBorder padding="lg" radius="md" bg={tokens.surface}>
          <Text c="dimmed" size="xs" tt="uppercase" fw={600}>Total DSAR Requests</Text>
          <Text fw={700} size="xl" c={tokens.textPrimary} mt={4}>{data.totalDsarRequests}</Text>
        </Card>
      </SimpleGrid>

      {/* PII adoption progress */}
      <Paper withBorder radius="md" bg={tokens.surface} p="md">
        <Group justify="space-between" mb="xs">
          <Text size="sm" fw={500} c={tokens.textSecondary}>PII Scrubbing Adoption</Text>
          <Text size="sm" fw={600} c={tokens.textPrimary}>{piiAdoptionPct}%</Text>
        </Group>
        <Progress
          value={piiAdoptionPct}
          color={piiAdoptionPct >= 80 ? 'green' : piiAdoptionPct >= 50 ? 'yellow' : 'red'}
          size="lg"
          radius="md"
        />
      </Paper>

      {/* Compliance matrix table */}
      <Paper withBorder radius="md" bg={tokens.surface} style={{ overflow: 'auto' }}>
        <Table striped highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Tenant ID</Table.Th>
              <Table.Th>Tier</Table.Th>
              <Table.Th>Grace Period<HelpTooltip text="New tenants receive a 30-day grace period before PII scrubbing enforcement begins." /></Table.Th>
              <Table.Th>PII Scrubbing</Table.Th>
              <Table.Th>DSAR Requests<HelpTooltip text="Data Subject Access Requests — formal requests from customers to access or delete their personal data under GDPR/CCPA." /></Table.Th>
              <Table.Th>Last DSAR</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {data.tenants.length === 0 ? (
              <Table.Tr>
                <Table.Td colSpan={6}>
                  <Text c="dimmed" ta="center" py="md">No compliance data available</Text>
                </Table.Td>
              </Table.Tr>
            ) : (
              data.tenants.map((t) => (
                <Table.Tr
                  key={t.tenantId}
                  style={t.gracePeriodActive ? { backgroundColor: 'rgba(229, 161, 0, 0.06)' } : undefined}
                >
                  <Table.Td>
                    <TenantName tenantId={t.tenantId} info={getTenantDisplay(t.tenantId)} />
                  </Table.Td>
                  <Table.Td>
                    <Text size="xs" c={tokens.textMuted}>{t.tier ?? '\u2014'}</Text>
                  </Table.Td>
                  <Table.Td>
                    {t.gracePeriodActive ? (
                      <Badge variant="light" color="orange" size="sm">Active</Badge>
                    ) : (
                      <Badge variant="light" color="gray" size="sm">Expired</Badge>
                    )}
                  </Table.Td>
                  <Table.Td>
                    <Badge
                      variant="light"
                      color={t.piiScrubbingEnabled ? 'green' : 'red'}
                      size="sm"
                    >
                      {t.piiScrubbingEnabled ? 'Enabled' : 'Disabled'}
                    </Badge>
                  </Table.Td>
                  <Table.Td>
                    <Text size="xs" fw={500} c={tokens.textSecondary}>{t.dsarRequestCount}</Text>
                  </Table.Td>
                  <Table.Td>
                    <Text size="xs" c="dimmed">
                      {t.lastDsarRequest
                        ? new Date(t.lastDsarRequest).toLocaleDateString()
                        : '\u2014'}
                    </Text>
                  </Table.Td>
                </Table.Tr>
              ))
            )}
          </Table.Tbody>
        </Table>
      </Paper>

      {/* Errors section */}
      {data.errors.length > 0 && (
        <Paper withBorder radius="md" bg={tokens.surface} p="md">
          <Group gap="xs" mb="sm">
            <Badge variant="filled" color="red" size="sm">
              {data.errors.length} Error{data.errors.length !== 1 ? 's' : ''}
            </Badge>
          </Group>
          <Stack gap="xs">
            {data.errors.map((err, i) => (
              <Group key={i} gap="xs">
                <TenantName tenantId={err.tenantId} info={getTenantDisplay(err.tenantId)} />
                <Text size="xs" c={tokens.textMuted}>{err.message}</Text>
              </Group>
            ))}
          </Stack>
        </Paper>
      )}
    </Stack>
  );
}
