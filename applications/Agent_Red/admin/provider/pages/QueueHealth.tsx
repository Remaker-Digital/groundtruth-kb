// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * QueueHealth — NATS JetStream queue depth monitoring.
 *
 * Per-tenant message backlog, byte usage, and consumer counts.
 * Health badges: green <100 msgs, orange 100-1000, red >1000.
 *
 * API: GET /api/superadmin/queues
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useEffect, useState } from 'react';
import {
  Badge,
  Card,
  Collapse,
  Group,
  Paper,
  SimpleGrid,
  Stack,
  Table,
  Text,
  Title,
  UnstyledButton,
} from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { useProviderContext } from '../layouts/ProviderLayout';
import { LoadingState } from '../../shared/LoadingState';
import { TenantName } from '../components/TenantName';
import { tokens } from '../../shared/theme/styles';

// ---------------------------------------------------------------------------
// Types (camelCase — matches CamelCaseModel API serialization)
// ---------------------------------------------------------------------------

interface TenantQueueInfo {
  tenantId: string;
  streamName: string;
  messages: number;
  bytes: number;
  consumerCount: number;
}

interface QueueDepthResponse {
  natsDeployed: boolean;
  totalTenants: number;
  totalMessages: number;
  totalBytes: number;
  tenants: TenantQueueInfo[];
  errors: Array<{ tenantId: string; message: string }>;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB'];
  const i = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
  const val = bytes / Math.pow(1024, i);
  return `${val < 10 ? val.toFixed(1) : Math.round(val)} ${units[i]}`;
}

function queueHealthColor(messages: number): string {
  if (messages < 100) return 'green';
  if (messages <= 1000) return 'orange';
  return 'red';
}

function queueHealthLabel(messages: number): string {
  if (messages < 100) return 'Healthy';
  if (messages <= 1000) return 'Elevated';
  return 'Critical';
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function QueueHealthPage() {
  const { apiFetch, onNotify, getTenantDisplay } = useProviderContext();
  const [data, setData] = useState<QueueDepthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [errorsOpened, { toggle: toggleErrors }] = useDisclosure(false);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await apiFetch('/api/superadmin/queues');
        if (res.ok && !cancelled) {
          setData(await res.json());
        } else if (!cancelled) {
          onNotify('Failed to load queue health', 'error');
        }
      } catch {
        if (!cancelled) onNotify('Network error loading queue health', 'error');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [apiFetch, onNotify]);

  if (loading) {
    return <LoadingState text="Loading queue health" />;
  }

  if (!data) {
    return (
      <Text c="dimmed" ta="center" mt="xl">
        Unable to load queue health data.
      </Text>
    );
  }

  if (!data.natsDeployed) {
    return (
      <Stack gap="lg">
        <Title order={3} c={tokens.textPrimary}>Queue Health</Title>
        <Paper withBorder radius="md" bg={tokens.surface} p="xl">
          <Stack align="center" gap="sm">
            <Badge variant="light" color="gray" size="lg">Not Deployed</Badge>
            <Text c="dimmed" size="sm" ta="center">
              NATS JetStream is not deployed in this environment.
              Queue health monitoring will be available when NATS is configured.
            </Text>
          </Stack>
        </Paper>
      </Stack>
    );
  }

  return (
    <Stack gap="lg">
      <Title order={3} c={tokens.textPrimary}>Queue Health</Title>

      {/* Summary cards */}
      <SimpleGrid cols={{ base: 1, sm: 3 }} spacing="md">
        <Card withBorder padding="lg" radius="md" bg={tokens.surface}>
          <Text c="dimmed" size="xs" tt="uppercase" fw={600}>Total Tenants</Text>
          <Text fw={700} size="xl" c={tokens.textPrimary} mt={4}>{data.totalTenants}</Text>
        </Card>
        <Card withBorder padding="lg" radius="md" bg={tokens.surface}>
          <Text c="dimmed" size="xs" tt="uppercase" fw={600}>Total Messages</Text>
          <Text
            fw={700}
            size="xl"
            c={data.totalMessages > 1000 ? tokens.danger : data.totalMessages > 100 ? tokens.warning : tokens.success}
            mt={4}
          >
            {data.totalMessages.toLocaleString()}
          </Text>
        </Card>
        <Card withBorder padding="lg" radius="md" bg={tokens.surface}>
          <Text c="dimmed" size="xs" tt="uppercase" fw={600}>Total Bytes</Text>
          <Text fw={700} size="xl" c={tokens.textPrimary} mt={4}>{formatBytes(data.totalBytes)}</Text>
        </Card>
      </SimpleGrid>

      {/* Per-tenant table */}
      <Paper withBorder radius="md" bg={tokens.surface} style={{ overflow: 'auto' }}>
        <Table striped highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Tenant ID</Table.Th>
              <Table.Th>Stream</Table.Th>
              <Table.Th>Messages</Table.Th>
              <Table.Th>Bytes</Table.Th>
              <Table.Th>Consumers</Table.Th>
              <Table.Th>Health</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {data.tenants.length === 0 ? (
              <Table.Tr>
                <Table.Td colSpan={6}>
                  <Text c="dimmed" ta="center" py="md">No queue data available</Text>
                </Table.Td>
              </Table.Tr>
            ) : (
              data.tenants.map((t) => (
                <Table.Tr key={t.tenantId}>
                  <Table.Td>
                    <TenantName tenantId={t.tenantId} info={getTenantDisplay(t.tenantId)} />
                  </Table.Td>
                  <Table.Td>
                    <Text size="xs" ff="monospace" c={tokens.textMuted}>{t.streamName}</Text>
                  </Table.Td>
                  <Table.Td>
                    <Text size="xs" fw={500} c={tokens.textSecondary}>
                      {t.messages.toLocaleString()}
                    </Text>
                  </Table.Td>
                  <Table.Td>
                    <Text size="xs" c={tokens.textMuted}>{formatBytes(t.bytes)}</Text>
                  </Table.Td>
                  <Table.Td>
                    <Text size="xs" c={tokens.textMuted}>{t.consumerCount}</Text>
                  </Table.Td>
                  <Table.Td>
                    <Badge
                      variant="light"
                      color={queueHealthColor(t.messages)}
                      size="sm"
                    >
                      {queueHealthLabel(t.messages)}
                    </Badge>
                  </Table.Td>
                </Table.Tr>
              ))
            )}
          </Table.Tbody>
        </Table>
      </Paper>

      {/* Errors section (collapsible) */}
      {data.errors.length > 0 && (
        <Paper withBorder radius="md" bg={tokens.surface} p="md">
          <UnstyledButton onClick={toggleErrors}>
            <Group gap="xs">
              <Badge variant="filled" color="red" size="sm">
                {data.errors.length} Error{data.errors.length !== 1 ? 's' : ''}
              </Badge>
              <Text size="xs" c="dimmed">
                {errorsOpened ? 'Hide details' : 'Show details'}
              </Text>
            </Group>
          </UnstyledButton>
          <Collapse in={errorsOpened}>
            <Stack gap="xs" mt="sm">
              {data.errors.map((err, i) => (
                <Group key={i} gap="xs">
                  <TenantName tenantId={err.tenantId} info={getTenantDisplay(err.tenantId)} />
                  <Text size="xs" c={tokens.textMuted}>{err.message}</Text>
                </Group>
              ))}
            </Stack>
          </Collapse>
        </Paper>
      )}
    </Stack>
  );
}
