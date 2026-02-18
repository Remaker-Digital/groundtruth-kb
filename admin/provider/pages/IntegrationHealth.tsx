/**
 * IntegrationHealth — Cross-service integration reliability dashboard.
 *
 * Circuit breaker states, NATS connectivity, MCP integration status.
 * Overall health banner, per-breaker cards, MCP adoption gauges.
 *
 * API: GET /api/superadmin/integrations/health
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useEffect, useState } from 'react';
import {
  Badge,
  Card,
  Group,
  Paper,
  RingProgress,
  SimpleGrid,
  Stack,
  Text,
  Title,
} from '@mantine/core';
import { useProviderContext } from '../layouts/ProviderLayout';
import { LoadingState } from '../../shared/LoadingState';

// ---------------------------------------------------------------------------
// Types (matches IntegrationHealthResponse camelCase serialization)
// ---------------------------------------------------------------------------

interface CircuitBreakerStatus {
  service: string;
  state: string;
  failures: number;
  successes: number;
}

interface McpIntegrationStatus {
  serverName: string;
  tenantsEnabled: number;
  tenantsConnected: number;
  tenantsErrored: number;
}

interface IntegrationHealthResponse {
  overallHealthy: boolean;
  circuitBreakers: CircuitBreakerStatus[];
  anyBreakerOpen: boolean;
  natsConnected: boolean;
  mcpIntegrations: McpIntegrationStatus[];
  errors: Array<{ tenantId: string; message: string }>;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const BREAKER_STATE_COLORS: Record<string, string> = {
  closed: 'green',
  half_open: 'orange',
  open: 'red',
};

const BREAKER_STATE_LABELS: Record<string, string> = {
  closed: 'Closed',
  half_open: 'Half Open',
  open: 'Open',
};

function formatServiceName(service: string): string {
  return service
    .replace(/-/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function IntegrationHealthPage() {
  const { apiFetch, onNotify } = useProviderContext();
  const [data, setData] = useState<IntegrationHealthResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await apiFetch('/api/superadmin/integrations/health');
        if (res.ok && !cancelled) {
          setData(await res.json());
        } else if (!cancelled) {
          onNotify('Failed to load integration health', 'error');
        }
      } catch {
        if (!cancelled) onNotify('Network error loading integration health', 'error');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [apiFetch, onNotify]);

  if (loading) {
    return <LoadingState text="Loading integration health" />;
  }

  if (!data) {
    return (
      <Text c="dimmed" ta="center" mt="xl">
        Unable to load integration health data.
      </Text>
    );
  }

  return (
    <Stack gap="lg">
      <Group justify="space-between" align="baseline">
        <Title order={3} c="#F5F5F5">Integration Health</Title>
        <Badge
          variant="filled"
          color={data.overallHealthy ? 'green' : 'red'}
          size="lg"
        >
          {data.overallHealthy ? 'All Systems Healthy' : 'Issues Detected'}
        </Badge>
      </Group>

      {/* NATS connectivity */}
      <Paper withBorder radius="md" bg="#1f1f1f" p="md">
        <Group gap="sm">
          <Text size="sm" fw={500} c="#E0E0E0">NATS JetStream</Text>
          <Badge
            variant="light"
            color={data.natsConnected ? 'green' : 'red'}
            size="sm"
          >
            {data.natsConnected ? 'Connected' : 'Disconnected'}
          </Badge>
        </Group>
      </Paper>

      {/* Circuit breaker cards */}
      {data.circuitBreakers.length > 0 && (
        <>
          <Text size="sm" fw={600} c="#A0A0A0" tt="uppercase">Circuit Breakers</Text>
          <SimpleGrid cols={{ base: 1, sm: 2, md: 3 }} spacing="md">
            {data.circuitBreakers.map((cb) => (
              <Card key={cb.service} withBorder padding="lg" radius="md" bg="#1f1f1f">
                <Group justify="space-between" mb="xs">
                  <Text size="sm" fw={500} c="#E0E0E0">
                    {formatServiceName(cb.service)}
                  </Text>
                  <Badge
                    variant="light"
                    color={BREAKER_STATE_COLORS[cb.state] ?? 'gray'}
                    size="sm"
                  >
                    {BREAKER_STATE_LABELS[cb.state] ?? cb.state}
                  </Badge>
                </Group>
                <Group gap="xl">
                  <Stack gap={2}>
                    <Text c="dimmed" size="xs">Failures</Text>
                    <Text
                      fw={600}
                      size="lg"
                      c={cb.failures > 0 ? '#D32F2F' : '#A0A0A0'}
                    >
                      {cb.failures}
                    </Text>
                  </Stack>
                  <Stack gap={2}>
                    <Text c="dimmed" size="xs">Successes</Text>
                    <Text fw={600} size="lg" c="#0D7C3E">{cb.successes}</Text>
                  </Stack>
                </Group>
              </Card>
            ))}
          </SimpleGrid>
        </>
      )}

      {/* MCP integration status */}
      {data.mcpIntegrations.length > 0 && (
        <>
          <Text size="sm" fw={600} c="#A0A0A0" tt="uppercase">MCP Integrations</Text>
          <SimpleGrid cols={{ base: 1, sm: 2 }} spacing="md">
            {data.mcpIntegrations.map((mcp) => {
              const connectedPct = mcp.tenantsEnabled > 0
                ? Math.round((mcp.tenantsConnected / mcp.tenantsEnabled) * 100)
                : 0;
              return (
                <Card key={mcp.serverName} withBorder padding="lg" radius="md" bg="#1f1f1f">
                  <Group justify="space-between" align="flex-start">
                    <Stack gap={4}>
                      <Text size="sm" fw={500} c="#E0E0E0">
                        {formatServiceName(mcp.serverName)}
                      </Text>
                      <Group gap="lg">
                        <Stack gap={0}>
                          <Text c="dimmed" size="xs">Enabled</Text>
                          <Text size="sm" fw={500} c="#E0E0E0">{mcp.tenantsEnabled}</Text>
                        </Stack>
                        <Stack gap={0}>
                          <Text c="dimmed" size="xs">Connected</Text>
                          <Text size="sm" fw={500} c="#0D7C3E">{mcp.tenantsConnected}</Text>
                        </Stack>
                        <Stack gap={0}>
                          <Text c="dimmed" size="xs">Errored</Text>
                          <Text
                            size="sm"
                            fw={500}
                            c={mcp.tenantsErrored > 0 ? '#D32F2F' : '#A0A0A0'}
                          >
                            {mcp.tenantsErrored}
                          </Text>
                        </Stack>
                      </Group>
                    </Stack>
                    <RingProgress
                      size={80}
                      thickness={8}
                      roundCaps
                      sections={[
                        {
                          value: connectedPct,
                          color: connectedPct >= 80
                            ? '#0D7C3E'
                            : connectedPct >= 50
                              ? '#E5A100'
                              : '#D32F2F',
                        },
                      ]}
                      label={
                        <Text ta="center" size="xs" fw={600} c="#F5F5F5">
                          {connectedPct}%
                        </Text>
                      }
                    />
                  </Group>
                </Card>
              );
            })}
          </SimpleGrid>
        </>
      )}

      {/* Errors section */}
      {data.errors.length > 0 && (
        <Paper withBorder radius="md" bg="#1f1f1f" p="md">
          <Group gap="xs" mb="sm">
            <Badge variant="filled" color="red" size="sm">
              {data.errors.length} Error{data.errors.length !== 1 ? 's' : ''}
            </Badge>
          </Group>
          <Stack gap="xs">
            {data.errors.map((err, i) => (
              <Group key={i} gap="xs">
                <Text size="xs" ff="monospace" c="#E5A100">{err.tenantId}</Text>
                <Text size="xs" c="#A0A0A0">{err.message}</Text>
              </Group>
            ))}
          </Stack>
        </Paper>
      )}
    </Stack>
  );
}
