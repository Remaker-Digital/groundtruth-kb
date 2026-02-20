/**
 * AbuseDetection — Cross-tenant anomalous usage detection dashboard.
 *
 * Shows abuse signal scan results with severity-colored indicators,
 * risk scores, and ability to flag/unflag tenants.
 *
 * API: GET  /api/superadmin/abuse/signals
 *      GET  /api/superadmin/abuse/tenant/{tenant_id}
 *      POST /api/superadmin/abuse/tenant/{tenant_id}/flag
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useEffect, useState } from 'react';
import {
  Badge,
  Button,
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
import { tokens } from '../../shared/theme/styles';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface AbuseSignal {
  tenantId: string;
  signalType: string;
  severity: string;
  description: string;
  detectedAt: string;
  metricValue: number;
  threshold: number;
}

interface TenantAbuseProfile {
  tenantId: string;
  isFlagged: boolean;
  flaggedAt: string | null;
  flaggedBy: string | null;
  signals: AbuseSignal[];
  riskScore: number;
}

interface AbuseOverview {
  totalTenantsScanned: number;
  flaggedCount: number;
  signalsByType: Record<string, number>;
  highRiskTenants: TenantAbuseProfile[];
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const SEVERITY_COLORS: Record<string, string> = {
  critical: 'red',
  high: 'orange',
  medium: 'yellow',
  low: 'gray',
};

const SIGNAL_LABELS: Record<string, string> = {
  rate_anomaly: 'Rate Anomaly',
  volume_spike: 'Volume Spike',
  widget_abuse: 'Widget Abuse',
  token_exhaustion: 'Token Exhaustion',
  error_rate: 'Error Rate',
};

function riskColor(score: number): string {
  if (score >= 75) return 'red';
  if (score >= 50) return 'orange';
  if (score >= 25) return 'yellow';
  return 'green';
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function AbuseDetectionPage() {
  const { apiFetch, onNotify } = useProviderContext();
  const [data, setData] = useState<AbuseOverview | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    setLoading(true);
    try {
      const res = await apiFetch('/api/superadmin/abuse/signals');
      if (res.ok) {
        setData(await res.json());
      } else {
        onNotify('Failed to load abuse signals', 'error');
      }
    } catch {
      onNotify('Network error loading abuse signals', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [apiFetch]);

  const handleToggleFlag = async (tenantId: string, currentlyFlagged: boolean) => {
    try {
      const res = await apiFetch(`/api/superadmin/abuse/tenant/${encodeURIComponent(tenantId)}/flag`, {
        method: 'POST',
        body: JSON.stringify({ flagged: !currentlyFlagged }),
      });
      if (res.ok) {
        onNotify(
          currentlyFlagged ? `Unflagged ${tenantId}` : `Flagged ${tenantId}`,
          'success',
        );
        // Refresh data
        await fetchData();
      } else {
        onNotify('Failed to update flag', 'error');
      }
    } catch {
      onNotify('Network error updating flag', 'error');
    }
  };

  if (loading) {
    return <LoadingState text="Scanning for abuse signals" />;
  }

  if (!data) {
    return (
      <Text c="dimmed" ta="center" mt="xl">
        Unable to load abuse detection data.
      </Text>
    );
  }

  return (
    <Stack gap="lg">
      <Group justify="space-between" align="baseline">
        <Title order={3} c={tokens.textPrimary}>Abuse Detection</Title>
        <Button variant="light" size="xs" onClick={fetchData}>
          Rescan
        </Button>
      </Group>

      {/* Summary cards */}
      <SimpleGrid cols={{ base: 1, sm: 3 }} spacing="md">
        <Card withBorder padding="lg" radius="md" bg={tokens.surface}>
          <Text c="dimmed" size="xs" tt="uppercase" fw={600}>Tenants Scanned</Text>
          <Text fw={700} size="xl" c={tokens.textPrimary} mt={4}>{data.totalTenantsScanned}</Text>
        </Card>
        <Card withBorder padding="lg" radius="md" bg={tokens.surface}>
          <Text c="dimmed" size="xs" tt="uppercase" fw={600}>Flagged</Text>
          <Text
            fw={700}
            size="xl"
            c={data.flaggedCount > 0 ? tokens.warning : tokens.success}
            mt={4}
          >
            {data.flaggedCount}
          </Text>
        </Card>
        <Card withBorder padding="lg" radius="md" bg={tokens.surface}>
          <Text c="dimmed" size="xs" tt="uppercase" fw={600}>High-Risk Tenants</Text>
          <Text
            fw={700}
            size="xl"
            c={data.highRiskTenants.length > 0 ? tokens.brand : tokens.success}
            mt={4}
          >
            {data.highRiskTenants.length}
          </Text>
        </Card>
      </SimpleGrid>

      {/* Signals by type */}
      {Object.keys(data.signalsByType ?? {}).length > 0 && (
        <SimpleGrid cols={{ base: 2, sm: 5 }} spacing="sm">
          {Object.entries(data.signalsByType ?? {}).map(([type, count]) => (
            <Card key={type} withBorder padding="sm" radius="md" bg={tokens.surface}>
              <Text c="dimmed" size="xs" fw={600}>
                {SIGNAL_LABELS[type] ?? type}
              </Text>
              <Text fw={700} size="lg" c={tokens.textPrimary} mt={2}>{count}</Text>
            </Card>
          ))}
        </SimpleGrid>
      )}

      {/* High-risk tenants table */}
      <Title order={4} c={tokens.textPrimary} mt="sm">High-Risk Tenants</Title>
      <Paper withBorder radius="md" bg={tokens.surface} style={{ overflow: 'auto' }}>
        <Table striped highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Tenant ID</Table.Th>
              <Table.Th>Risk Score</Table.Th>
              <Table.Th>Signals</Table.Th>
              <Table.Th>Flagged</Table.Th>
              <Table.Th>Actions</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {data.highRiskTenants.length === 0 ? (
              <Table.Tr>
                <Table.Td colSpan={5}>
                  <Text c="dimmed" ta="center" py="md">No high-risk tenants detected</Text>
                </Table.Td>
              </Table.Tr>
            ) : (
              data.highRiskTenants.map((t) => (
                <Table.Tr key={t.tenantId}>
                  <Table.Td>
                    <Text size="xs" ff="monospace" c={tokens.textSecondary}>{t.tenantId}</Text>
                  </Table.Td>
                  <Table.Td>
                    <Group gap="xs">
                      <Progress
                        value={t.riskScore}
                        color={riskColor(t.riskScore)}
                        size="sm"
                        w={60}
                      />
                      <Text size="xs" fw={600} c={tokens.textPrimary}>{t.riskScore}</Text>
                    </Group>
                  </Table.Td>
                  <Table.Td>
                    <Group gap={4}>
                      {t.signals.map((s, i) => (
                        <Badge
                          key={i}
                          variant="light"
                          color={SEVERITY_COLORS[s.severity] ?? 'gray'}
                          size="xs"
                        >
                          {SIGNAL_LABELS[s.signalType] ?? s.signalType}
                        </Badge>
                      ))}
                    </Group>
                  </Table.Td>
                  <Table.Td>
                    {t.isFlagged ? (
                      <Badge variant="filled" color="red" size="sm">Flagged</Badge>
                    ) : (
                      <Text size="xs" c="dimmed">—</Text>
                    )}
                  </Table.Td>
                  <Table.Td>
                    <Button
                      variant="light"
                      size="xs"
                      color={t.isFlagged ? 'green' : 'red'}
                      onClick={() => handleToggleFlag(t.tenantId, t.isFlagged)}
                    >
                      {t.isFlagged ? 'Unflag' : 'Flag'}
                    </Button>
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
