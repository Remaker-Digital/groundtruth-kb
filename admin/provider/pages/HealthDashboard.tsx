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
  Loader,
  Paper,
  SimpleGrid,
  Stack,
  Text,
  Title,
} from '@mantine/core';
import { useProviderContext } from '../layouts/ProviderLayout';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface DashboardData {
  timestamp: string;
  system_health: {
    nats: { connected: boolean };
    circuit_breakers: Record<string, unknown>;
    key_vault: { healthy: boolean };
    version: { api: string; product: string };
  };
  tenant_summary: {
    total_tenants: number;
    by_status: Record<string, number>;
    by_tier: Record<string, number>;
    by_billing_channel: Record<string, number>;
  } | null;
  sla_summary: Record<string, unknown>;
  usage_summary: Record<string, unknown>;
  recent_deployments: Array<{
    event_type: string;
    timestamp: string;
    actor: string;
    payload: Record<string, unknown>;
  }>;
  recent_alerts: unknown[];
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
    return (
      <Stack align="center" mt="xl">
        <Loader color="red" />
        <Text c="dimmed" size="sm">Loading dashboard...</Text>
      </Stack>
    );
  }

  if (!data) {
    return (
      <Text c="dimmed" ta="center" mt="xl">
        Unable to load dashboard data.
      </Text>
    );
  }

  const health = data.system_health;
  const tenants = data.tenant_summary;

  return (
    <Stack gap="lg">
      <Group justify="space-between" align="baseline">
        <Title order={3} c="#F5F5F5">Platform Dashboard</Title>
        <Text c="dimmed" size="xs">
          Updated {new Date(data.timestamp).toLocaleString()}
        </Text>
      </Group>

      {/* System Health Cards */}
      <SimpleGrid cols={{ base: 1, sm: 2, md: 4 }} spacing="md">
        <HealthCard
          label="NATS"
          status={health.nats?.connected ? 'healthy' : 'down'}
          detail={health.nats?.connected ? 'Connected' : 'Disconnected'}
        />
        <HealthCard
          label="Key Vault"
          status={health.key_vault?.healthy ? 'healthy' : 'degraded'}
          detail={health.key_vault?.healthy ? 'Healthy' : 'Degraded'}
        />
        <HealthCard
          label="API Version"
          status="info"
          detail={`v${health.version?.product ?? '?'}`}
        />
        <HealthCard
          label="Circuit Breakers"
          status={health.circuit_breakers ? 'healthy' : 'unknown'}
          detail={health.circuit_breakers ? 'Operational' : 'Unknown'}
        />
      </SimpleGrid>

      {/* Tenant Distribution */}
      {tenants && (
        <>
          <Title order={4} c="#E0E0E0">Tenant Distribution</Title>
          <Grid>
            <Grid.Col span={{ base: 12, md: 4 }}>
              <Card withBorder padding="lg" radius="md" bg="#1f1f1f">
                <Text c="dimmed" size="xs" tt="uppercase" fw={600}>Total Tenants</Text>
                <Text fw={700} size="xl" c="#F5F5F5" mt={4}>{tenants.total_tenants}</Text>
              </Card>
            </Grid.Col>
            <Grid.Col span={{ base: 12, md: 4 }}>
              <Card withBorder padding="lg" radius="md" bg="#1f1f1f">
                <Text c="dimmed" size="xs" tt="uppercase" fw={600}>By Status</Text>
                <Group gap="xs" mt="sm">
                  {Object.entries(tenants.by_status).map(([k, v]) => (
                    <Badge key={k} variant="light" color={k === 'active' ? 'green' : 'gray'} size="sm">
                      {k}: {v}
                    </Badge>
                  ))}
                </Group>
              </Card>
            </Grid.Col>
            <Grid.Col span={{ base: 12, md: 4 }}>
              <Card withBorder padding="lg" radius="md" bg="#1f1f1f">
                <Text c="dimmed" size="xs" tt="uppercase" fw={600}>By Tier</Text>
                <Group gap="xs" mt="sm">
                  {Object.entries(tenants.by_tier).map(([k, v]) => (
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
      {data.recent_deployments.length > 0 && (
        <>
          <Title order={4} c="#E0E0E0">Recent Deployments</Title>
          <Paper withBorder p="md" radius="md" bg="#1f1f1f">
            <Stack gap="xs">
              {data.recent_deployments.map((evt, i) => (
                <Group key={i} justify="space-between">
                  <Group gap="xs">
                    <Badge
                      variant="light"
                      color={evt.event_type === 'MODEL_DEPLOYED' ? 'green' : 'orange'}
                      size="sm"
                    >
                      {evt.event_type === 'MODEL_DEPLOYED' ? 'Deploy' : 'Rollback'}
                    </Badge>
                    <Text size="sm" c="#E0E0E0">
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
    healthy: '#0D7C3E',
    down: '#D32F2F',
    degraded: '#E5A100',
    info: '#1E3A5F',
    unknown: '#5C5C5C',
  };
  const dotColor = colorMap[status] ?? '#5C5C5C';

  return (
    <Card withBorder padding="lg" radius="md" bg="#1f1f1f">
      <Group gap="xs" mb={4}>
        <div style={{
          width: 8, height: 8, borderRadius: '50%',
          backgroundColor: dotColor,
        }} />
        <Text c="dimmed" size="xs" tt="uppercase" fw={600}>{label}</Text>
      </Group>
      <Text fw={600} size="sm" c="#E0E0E0">{detail}</Text>
    </Card>
  );
}
