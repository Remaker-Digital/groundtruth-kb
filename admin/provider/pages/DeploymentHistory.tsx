/**
 * DeploymentHistory — Timeline of production deploy and rollback events.
 *
 * Shows current version, total events, and a chronological list of
 * deployment events with type badges, actor, timestamp, and payload details.
 *
 * API: GET /api/superadmin/deployments
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useEffect, useState } from 'react';
import {
  Badge,
  Card,
  Code,
  Group,
  Paper,
  Select,
  SimpleGrid,
  Stack,
  Text,
  Title,
} from '@mantine/core';
import { useProviderContext } from '../layouts/ProviderLayout';
import { LoadingState } from '../../shared/LoadingState';
import { tokens } from '../../shared/theme/styles';

// ---------------------------------------------------------------------------
// Types (camelCase — matches CamelCaseModel API serialization)
// ---------------------------------------------------------------------------

interface DeploymentEvent {
  eventType: string;
  timestamp: string;
  actor: string;
  payload: Record<string, unknown>;
}

interface DeploymentResponse {
  events: DeploymentEvent[];
  total: number;
  currentVersion: string | null;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function DeploymentHistoryPage() {
  const { apiFetch, onNotify } = useProviderContext();
  const [data, setData] = useState<DeploymentResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [limit, setLimit] = useState<string>('20');

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      try {
        const res = await apiFetch(`/api/superadmin/deployments?limit=${limit}`);
        if (res.ok && !cancelled) {
          setData(await res.json());
        } else if (!cancelled) {
          onNotify('Failed to load deployment history', 'error');
        }
      } catch {
        if (!cancelled) onNotify('Network error loading deployments', 'error');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [apiFetch, onNotify, limit]);

  if (loading) {
    return <LoadingState text="Loading deployment history" />;
  }

  if (!data) {
    return (
      <Text c="dimmed" ta="center" mt="xl">
        Unable to load deployment history.
      </Text>
    );
  }

  return (
    <Stack gap="lg">
      <Group justify="space-between" align="baseline">
        <Title order={3} c={tokens.textPrimary}>Deployment History</Title>
        <Select
          value={limit}
          onChange={(v) => v && setLimit(v)}
          data={[
            { value: '10', label: 'Last 10' },
            { value: '20', label: 'Last 20' },
            { value: '50', label: 'Last 50' },
            { value: '100', label: 'Last 100' },
          ]}
          size="xs"
          w={120}
        />
      </Group>

      {/* Summary */}
      <SimpleGrid cols={{ base: 1, sm: 2 }} spacing="md">
        <Card withBorder padding="lg" radius="md" bg={tokens.surface}>
          <Text c="dimmed" size="xs" tt="uppercase" fw={600}>Current Version</Text>
          <Text fw={700} size="xl" c={tokens.textPrimary} mt={4}>
            {data.currentVersion ? `v${data.currentVersion}` : 'Unknown'}
          </Text>
        </Card>
        <Card withBorder padding="lg" radius="md" bg={tokens.surface}>
          <Text c="dimmed" size="xs" tt="uppercase" fw={600}>Total Events</Text>
          <Text fw={700} size="xl" c={tokens.textPrimary} mt={4}>{data.total}</Text>
        </Card>
      </SimpleGrid>

      {/* Event timeline */}
      {data.events.length === 0 ? (
        <Paper withBorder p="xl" radius="md" bg={tokens.surface}>
          <Text c="dimmed" ta="center">No deployment events found</Text>
        </Paper>
      ) : (
        <Stack gap="sm">
          {data.events.map((evt, i) => {
            const isDeploy = evt.eventType === 'MODEL_DEPLOYED';
            return (
              <Paper key={i} withBorder p="md" radius="md" bg={tokens.surface}>
                <Group justify="space-between" mb="xs">
                  <Group gap="sm">
                    <Badge
                      variant="light"
                      color={isDeploy ? 'green' : 'orange'}
                      size="md"
                    >
                      {isDeploy ? 'Deploy' : 'Rollback'}
                    </Badge>
                    <Text size="sm" fw={500} c={tokens.textSecondary}>
                      {evt.actor || 'system'}
                    </Text>
                  </Group>
                  <Text size="xs" c="dimmed">
                    {new Date(evt.timestamp).toLocaleString()}
                  </Text>
                </Group>

                {/* Payload details */}
                {Object.keys(evt.payload ?? {}).length > 0 && (
                  <Code
                    block
                    style={{
                      backgroundColor: tokens.page,
                      color: tokens.textMuted,
                      fontSize: '12px',
                      maxHeight: '120px',
                      overflow: 'auto',
                    }}
                  >
                    {JSON.stringify(evt.payload, null, 2)}
                  </Code>
                )}
              </Paper>
            );
          })}
        </Stack>
      )}
    </Stack>
  );
}
