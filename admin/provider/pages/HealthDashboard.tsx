/**
 * HealthDashboard — Provider console landing page.
 *
 * Shows system health cards, tenant distribution, SLA summary,
 * recent deployments, and usage overview.
 *
 * API: GET /api/superadmin/dashboard
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useEffect, useState } from 'react';
import {
  Badge,
  Card,
  Grid,
  Group,
  Paper,
  SimpleGrid,
  Stack,
  Text,
  Title,
} from '@mantine/core';
import { useProviderContext } from '../layouts/ProviderLayout';
import { LoadingState } from '../../shared/LoadingState';
import { EmptyState } from '../../shared/EmptyState';
import { Icons } from '../../shared/icons';
import { HelpTooltip } from '../../shared/HelpTooltip';
import { tokens } from '../../shared/theme/styles';

// ---------------------------------------------------------------------------
// Types (camelCase — matches CamelCaseModel API serialization)
// ---------------------------------------------------------------------------

interface DashboardData {
  timestamp: string;
  systemHealth: {
    nats: { deployed: boolean; connected: boolean };
    circuitBreakers: Record<string, unknown>;
    keyVault: { healthy: boolean };
    version: { api: string; product: string };
  } | null;
  tenantSummary: {
    totalTenants: number;
    byStatus: Record<string, number>;
    byTier: Record<string, number>;
    byBillingChannel: Record<string, number>;
  } | null;
  slaSummary: Record<string, unknown>;
  usageSummary: Record<string, unknown>;
  recentDeployments: Array<{
    eventType: string;
    timestamp: string;
    actor: string;
    payload: Record<string, unknown>;
  }>;
  recentAlerts: unknown[];
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function HealthDashboardPage() {
  const { apiFetch, onNotify } = useProviderContext();
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await apiFetch('/api/superadmin/dashboard');
        if (res.ok && !cancelled) {
          setData(await res.json());
        } else if (!cancelled) {
          onNotify('Failed to load dashboard', 'error');
        }
      } catch {
        if (!cancelled) onNotify('Network error loading dashboard', 'error');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [apiFetch, onNotify]);

  if (loading) {
    return <LoadingState text="Loading dashboard" />;
  }

  if (!data) {
    return (
      <EmptyState
        icon={<Icons.dashboard size={36} />}
        title="Unable to load dashboard"
        subtitle="Check your connection and try refreshing the page."
      />
    );
  }

  const health = data.systemHealth;
  const tenants = data.tenantSummary;

  return (
    <Stack gap="lg">
      <Group justify="space-between" align="baseline">
        <Title order={3} c={tokens.textPrimary}>Platform Dashboard</Title><HelpTooltip text="Real-time overview of system health, tenant distribution, and recent activity across the platform." />
        <Text c="dimmed" size="xs">
          Updated {new Date(data.timestamp).toLocaleString()}
        </Text>
      </Group>

      {/* System Health Cards */}
      <SimpleGrid cols={{ base: 1, sm: 2, md: 4 }} spacing="md">
        <HealthCard
          label="NATS"
          status={health?.nats?.connected ? 'healthy' : health?.nats?.deployed ? 'down' : 'unknown'}
          detail={health?.nats?.connected ? 'Connected' : health?.nats?.deployed ? 'Disconnected' : 'Not Deployed'}
        />
        <HealthCard
          label="Key Vault"
          status={health?.keyVault?.healthy ? 'healthy' : 'degraded'}
          detail={health?.keyVault?.healthy ? 'Healthy' : 'Degraded'}
        />
        <HealthCard
          label="API Version"
          status="info"
          detail={`v${health?.version?.product ?? '?'}`}
        />
        <HealthCard
          label="Circuit Breakers"
          status={health?.circuitBreakers ? 'healthy' : 'unknown'}
          detail={health?.circuitBreakers ? 'Operational' : 'Unknown'}
        />
      </SimpleGrid>

      {/* Tenant Distribution */}
      {tenants && (
        <>
          <Title order={4} c={tokens.textSecondary}>Tenant Distribution</Title>
          <Grid>
            <Grid.Col span={{ base: 12, md: 4 }}>
              <Card withBorder padding="lg" radius="md" bg={tokens.surface}>
                <Text c="dimmed" size="xs" tt="uppercase" fw={600}>Total Tenants</Text>
                <Text fw={700} size="xl" c={tokens.textPrimary} mt={4}>{tenants.totalTenants}</Text>
              </Card>
            </Grid.Col>
            <Grid.Col span={{ base: 12, md: 4 }}>
              <Card withBorder padding="lg" radius="md" bg={tokens.surface}>
                <Text c="dimmed" size="xs" tt="uppercase" fw={600}>By Status</Text>
                <Group gap="xs" mt="sm">
                  {Object.entries(tenants?.byStatus ?? {}).map(([k, v]) => (
                    <Badge key={k} variant="light" color={k === 'active' ? 'green' : 'gray'} size="sm">
                      {k}: {v}
                    </Badge>
                  ))}
                </Group>
              </Card>
            </Grid.Col>
            <Grid.Col span={{ base: 12, md: 4 }}>
              <Card withBorder padding="lg" radius="md" bg={tokens.surface}>
                <Text c="dimmed" size="xs" tt="uppercase" fw={600}>By Tier</Text>
                <Group gap="xs" mt="sm">
                  {Object.entries(tenants?.byTier ?? {}).map(([k, v]) => (
                    <Badge key={k} variant="light" color="blue" size="sm">
                      {k}: {v}
                    </Badge>
                  ))}
                </Group>
              </Card>
            </Grid.Col>
          </Grid>
        </>
      )}

      {/* Recent Deployments */}
      {(data.recentDeployments?.length ?? 0) > 0 && (
        <>
          <Title order={4} c={tokens.textSecondary}>Recent Deployments</Title>
          <Paper withBorder p="md" radius="md" bg={tokens.surface}>
            <Stack gap="xs">
              {data.recentDeployments.map((evt, i) => (
                <Group key={i} justify="space-between">
                  <Group gap="xs">
                    <Badge
                      variant="light"
                      color={evt.eventType === 'MODEL_DEPLOYED' ? 'green' : 'orange'}
                      size="sm"
                    >
                      {evt.eventType === 'MODEL_DEPLOYED' ? 'Deploy' : 'Rollback'}
                    </Badge>
                    <Text size="sm" c={tokens.textSecondary}>
                      {evt.actor || 'system'}
                    </Text>
                  </Group>
                  <Text size="xs" c="dimmed">
                    {new Date(evt.timestamp).toLocaleString()}
                  </Text>
                </Group>
              ))}
            </Stack>
          </Paper>
        </>
      )}
    </Stack>
  );
}

// ---------------------------------------------------------------------------
// Health card sub-component
// ---------------------------------------------------------------------------

function HealthCard({ label, status, detail }: { label: string; status: string; detail: string }) {
  const colorMap: Record<string, string> = {
    healthy: tokens.success,
    down: tokens.danger,
    degraded: tokens.warning,
    info: tokens.info,
    unknown: tokens.textTertiary,
  };
  const dotColor = colorMap[status] ?? tokens.textTertiary;

  return (
    <Card withBorder padding="lg" radius="md" bg={tokens.surface}>
      <Group gap="xs" mb={4}>
        <div style={{
          width: 8, height: 8, borderRadius: '50%',
          backgroundColor: dotColor,
        }} />
        <Text c="dimmed" size="xs" tt="uppercase" fw={600}>{label}</Text>
      </Group>
      <Text fw={600} size="sm" c={tokens.textSecondary}>{detail}</Text>
    </Card>
  );
}
