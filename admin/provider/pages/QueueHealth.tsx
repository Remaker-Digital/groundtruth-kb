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
  Loader,
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

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface TenantQueueInfo {
  tenant_id: string;
  stream_name: string;
  messages: number;
  bytes: number;
  consumer_count: number;
}

interface QueueDepthResponse {
  total_tenants: number;
  total_messages: number;
  total_bytes: number;
  tenants: TenantQueueInfo[];
  errors: Array<{ tenant_id: string; message: string }>;
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
  const { apiFetch, onNotify } = useProviderContext();
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
    return (
      <Stack align="center" mt="xl">
        <Loader color="red" />
        <Text c="dimmed" size="sm">Loading queue health...</Text>
      </Stack>
    );
  }

  if (!data) {
    return (
      <Text c="dimmed" ta="center" mt="xl">
        Unable to load queue health data.
      </Text>
    );
  }

  return (
    <Stack gap="lg">
      <Title order={3} c="#F5F5F5">Queue Health</Title>

      {/* Summary cards */}
      <SimpleGrid cols={{ base: 1, sm: 3 }} spacing="md">
        <Card withBorder padding="lg" radius="md" bg="#1f1f1f">
          <Text c="dimmed" size="xs" tt="uppercase" fw={600}>Total Tenants</Text>
          <Text fw={700} size="xl" c="#F5F5F5" mt={4}>{data.total_tenants}</Text>
        </Card>
        <Card withBorder padding="lg" radius="md" bg="#1f1f1f">
          <Text c="dimmed" size="xs" tt="uppercase" fw={600}>Total Messages</Text>
          <Text
            fw={700}
            size="xl"
            c={data.total_messages > 1000 ? '#D32F2F' : data.total_messages > 100 ? '#E5A100' : '#0D7C3E'}
            mt={4}
          >
            {data.total_messages.toLocaleString()}
          </Text>
        </Card>
        <Card withBorder padding="lg" radius="md" bg="#1f1f1f">
          <Text c="dimmed" size="xs" tt="uppercase" fw={600}>Total Bytes</Text>
          <Text fw={700} size="xl" c="#F5F5F5" mt={4}>{formatBytes(data.total_bytes)}</Text>
        </Card>
      </SimpleGrid>

      {/* Per-tenant table */}
      <Paper withBorder radius="md" bg="#1f1f1f" style={{ overflow: 'auto' }}>
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
                <Table.Tr key={t.tenant_id}>
                  <Table.Td>
                    <Text size="xs" ff="monospace" c="#E0E0E0">{t.tenant_id}</Text>
                  </Table.Td>
                  <Table.Td>
                    <Text size="xs" ff="monospace" c="#A0A0A0">{t.stream_name}</Text>
                  </Table.Td>
                  <Table.Td>
                    <Text size="xs" fw={500} c="#E0E0E0">
                      {t.messages.toLocaleString()}
                    </Text>
                  </Table.Td>
                  <Table.Td>
                    <Text size="xs" c="#A0A0A0">{formatBytes(t.bytes)}</Text>
                  </Table.Td>
                  <Table.Td>
                    <Text size="xs" c="#A0A0A0">{t.consumer_count}</Text>
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
        <Paper withBorder radius="md" bg="#1f1f1f" p="md">
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
                  <Text size="xs" ff="monospace" c="#E5A100">{err.tenant_id}</Text>
                  <Text size="xs" c="#A0A0A0">{err.message}</Text>
                </Group>
              ))}
            </Stack>
          </Collapse>
        </Paper>
      )}
    </Stack>
  );
}
