/**
 * SupportDiagnostics — Per-tenant diagnostic snapshot for support.
 *
 * Provides a comprehensive diagnostic view of a selected tenant including
 * config state, AI config, knowledge base stats, team info, conversations,
 * integrations, widget deployment, and recent errors.
 *
 * API: GET /api/superadmin/diagnostics/{tenant_id}
 *      GET /api/superadmin/diagnostics/{tenant_id}/errors
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
  SimpleGrid,
  Stack,
  Table,
  Text,
  TextInput,
  Title,
} from '@mantine/core';
import { useProviderContext } from '../layouts/ProviderLayout';
import { LoadingState } from '../../shared/LoadingState';
import { tokens } from '../../shared/theme/styles';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface ConfigStateSummary {
  isActive: boolean;
  isConfigured: boolean;
  hasPendingChanges: boolean;
  activeVersion: number | null;
  activatedAt: string | null;
}

interface AIConfigSummary {
  model: string | null;
  brandNamePresent: boolean;
  brandVoicePresent: boolean;
}

interface KnowledgeBaseStats {
  totalArticles: number;
  draftCount: number;
  activeCount: number;
}

interface TeamInfo {
  memberCount: number;
  rolesBreakdown: Record<string, number>;
}

interface ConversationStats {
  last24hCount: number;
  last7dCount: number;
  statusBreakdown: Record<string, number>;
}

interface IntegrationHealth {
  shopifyConnected: boolean;
  stripeConnected: boolean;
  natsDeployed: boolean;
  natsConnected: boolean;
}

interface WidgetDeployment {
  widgetKeyPresent: boolean;
  originConfigured: boolean;
}

interface DiagnosticSnapshot {
  tenantId: string;
  status: string;
  tier: string | null;
  billingChannel: string | null;
  createdAt: string | null;
  configState: ConfigStateSummary;
  aiConfig: AIConfigSummary;
  knowledgeBase: KnowledgeBaseStats;
  team: TeamInfo;
  conversations: ConversationStats;
  integrations: IntegrationHealth;
  widget: WidgetDeployment;
  lastActivityAt: string | null;
  collectionErrors: string[];
  generatedAt: string;
}

interface ErrorEntry {
  eventType: string;
  timestamp: string;
  actor: string;
  payload: Record<string, unknown>;
  conversationId: string | null;
}

interface ErrorsResponse {
  tenantId: string;
  entries: ErrorEntry[];
  total: number;
  generatedAt: string;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function BoolBadge({ value, trueLabel, falseLabel }: {
  value: boolean;
  trueLabel?: string;
  falseLabel?: string;
}) {
  return (
    <Badge variant="light" color={value ? 'green' : 'red'} size="sm">
      {value ? (trueLabel ?? 'Yes') : (falseLabel ?? 'No')}
    </Badge>
  );
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function SupportDiagnosticsPage() {
  const { apiFetch, onNotify } = useProviderContext();
  const [tenantId, setTenantId] = useState('');
  const [data, setData] = useState<DiagnosticSnapshot | null>(null);
  const [errors, setErrors] = useState<ErrorsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [errorsLoading, setErrorsLoading] = useState(false);

  const handleFetch = async () => {
    if (!tenantId.trim()) {
      onNotify('Please enter a tenant ID', 'warning');
      return;
    }
    setLoading(true);
    setData(null);
    setErrors(null);
    try {
      const res = await apiFetch(`/api/superadmin/diagnostics/${encodeURIComponent(tenantId.trim())}`);
      if (res.ok) {
        setData(await res.json());
      } else if (res.status === 404) {
        onNotify('Tenant not found', 'warning');
      } else {
        onNotify('Failed to load diagnostics', 'error');
      }
    } catch {
      onNotify('Network error loading diagnostics', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleFetchErrors = async () => {
    if (!tenantId.trim()) return;
    setErrorsLoading(true);
    try {
      const res = await apiFetch(`/api/superadmin/diagnostics/${encodeURIComponent(tenantId.trim())}/errors`);
      if (res.ok) {
        setErrors(await res.json());
      } else {
        onNotify('Failed to load errors', 'error');
      }
    } catch {
      onNotify('Network error loading errors', 'error');
    } finally {
      setErrorsLoading(false);
    }
  };

  return (
    <Stack gap="lg">
      <Title order={3} c={tokens.textPrimary}>Support Diagnostics</Title>

      {/* Tenant lookup */}
      <Group>
        <TextInput
          placeholder="Enter tenant ID..."
          value={tenantId}
          onChange={(e) => setTenantId(e.currentTarget.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleFetch()}
          style={{ flex: 1 }}
        />
        <Button onClick={handleFetch} loading={loading}>
          Run Diagnostics
        </Button>
      </Group>

      {loading && <LoadingState text="Collecting diagnostic snapshot" />}

      {data && (
        <>
          {/* Collection errors warning */}
          {data.collectionErrors.length > 0 && (
            <Paper withBorder radius="md" p="md" bg={tokens.page}>
              <Text c={tokens.warning} fw={600} size="sm" mb="xs">Partial data — collection errors:</Text>
              {data.collectionErrors.map((e, i) => (
                <Text key={i} c={tokens.warning} size="xs">{e}</Text>
              ))}
            </Paper>
          )}

          {/* Summary cards */}
          <SimpleGrid cols={{ base: 1, sm: 2, md: 4 }} spacing="md">
            <Card withBorder padding="md" radius="md" bg={tokens.surface}>
              <Text c="dimmed" size="xs" tt="uppercase" fw={600}>Status</Text>
              <Badge
                variant="filled"
                color={data.status === 'active' ? 'green' : data.status === 'trial' ? 'blue' : 'red'}
                size="lg"
                mt={4}
              >
                {data.status}
              </Badge>
            </Card>
            <Card withBorder padding="md" radius="md" bg={tokens.surface}>
              <Text c="dimmed" size="xs" tt="uppercase" fw={600}>Tier</Text>
              <Text fw={700} size="lg" c={tokens.textPrimary} mt={4}>{data.tier ?? '—'}</Text>
            </Card>
            <Card withBorder padding="md" radius="md" bg={tokens.surface}>
              <Text c="dimmed" size="xs" tt="uppercase" fw={600}>Billing Channel</Text>
              <Text fw={700} size="lg" c={tokens.textPrimary} mt={4}>{data.billingChannel ?? '—'}</Text>
            </Card>
            <Card withBorder padding="md" radius="md" bg={tokens.surface}>
              <Text c="dimmed" size="xs" tt="uppercase" fw={600}>Created</Text>
              <Text fw={500} size="sm" c={tokens.textPrimary} mt={4}>
                {data.createdAt ? new Date(data.createdAt).toLocaleDateString() : '—'}
              </Text>
            </Card>
          </SimpleGrid>

          {/* Config state + AI config */}
          <SimpleGrid cols={{ base: 1, sm: 2 }} spacing="md">
            <Card withBorder padding="md" radius="md" bg={tokens.surface}>
              <Text c="dimmed" size="xs" tt="uppercase" fw={600} mb="sm">Configuration State</Text>
              <Stack gap="xs">
                <Group justify="space-between">
                  <Text size="sm" c={tokens.textMuted}>Active</Text>
                  <BoolBadge value={data.configState.isActive} />
                </Group>
                <Group justify="space-between">
                  <Text size="sm" c={tokens.textMuted}>Configured</Text>
                  <BoolBadge value={data.configState.isConfigured} />
                </Group>
                <Group justify="space-between">
                  <Text size="sm" c={tokens.textMuted}>Pending Changes</Text>
                  <BoolBadge value={data.configState.hasPendingChanges} trueLabel="Yes" falseLabel="None" />
                </Group>
                <Group justify="space-between">
                  <Text size="sm" c={tokens.textMuted}>Active Version</Text>
                  <Text size="sm" c={tokens.textPrimary}>{data.configState.activeVersion ?? '—'}</Text>
                </Group>
              </Stack>
            </Card>

            <Card withBorder padding="md" radius="md" bg={tokens.surface}>
              <Text c="dimmed" size="xs" tt="uppercase" fw={600} mb="sm">AI Configuration</Text>
              <Stack gap="xs">
                <Group justify="space-between">
                  <Text size="sm" c={tokens.textMuted}>Model</Text>
                  <Text size="sm" c={tokens.textPrimary}>{data.aiConfig.model ?? '—'}</Text>
                </Group>
                <Group justify="space-between">
                  <Text size="sm" c={tokens.textMuted}>Brand Name</Text>
                  <BoolBadge value={data.aiConfig.brandNamePresent} trueLabel="Set" falseLabel="Missing" />
                </Group>
                <Group justify="space-between">
                  <Text size="sm" c={tokens.textMuted}>Brand Voice</Text>
                  <BoolBadge value={data.aiConfig.brandVoicePresent} trueLabel="Set" falseLabel="Missing" />
                </Group>
              </Stack>
            </Card>
          </SimpleGrid>

          {/* Knowledge Base + Team + Conversations */}
          <SimpleGrid cols={{ base: 1, sm: 3 }} spacing="md">
            <Card withBorder padding="md" radius="md" bg={tokens.surface}>
              <Text c="dimmed" size="xs" tt="uppercase" fw={600} mb="sm">Knowledge Base</Text>
              <Stack gap="xs">
                <Group justify="space-between">
                  <Text size="sm" c={tokens.textMuted}>Total Articles</Text>
                  <Text size="sm" fw={600} c={tokens.textPrimary}>{data.knowledgeBase.totalArticles}</Text>
                </Group>
                <Group justify="space-between">
                  <Text size="sm" c={tokens.textMuted}>Active</Text>
                  <Text size="sm" c={tokens.success}>{data.knowledgeBase.activeCount}</Text>
                </Group>
                <Group justify="space-between">
                  <Text size="sm" c={tokens.textMuted}>Draft</Text>
                  <Text size="sm" c={tokens.warning}>{data.knowledgeBase.draftCount}</Text>
                </Group>
              </Stack>
            </Card>

            <Card withBorder padding="md" radius="md" bg={tokens.surface}>
              <Text c="dimmed" size="xs" tt="uppercase" fw={600} mb="sm">Team</Text>
              <Stack gap="xs">
                <Group justify="space-between">
                  <Text size="sm" c={tokens.textMuted}>Members</Text>
                  <Text size="sm" fw={600} c={tokens.textPrimary}>{data.team?.memberCount ?? 0}</Text>
                </Group>
                {Object.entries(data.team?.rolesBreakdown ?? {}).map(([role, count]) => (
                  <Group key={role} justify="space-between">
                    <Text size="xs" c={tokens.textMuted}>{role}</Text>
                    <Text size="xs" c={tokens.textSecondary}>{count}</Text>
                  </Group>
                ))}
              </Stack>
            </Card>

            <Card withBorder padding="md" radius="md" bg={tokens.surface}>
              <Text c="dimmed" size="xs" tt="uppercase" fw={600} mb="sm">Conversations</Text>
              <Stack gap="xs">
                <Group justify="space-between">
                  <Text size="sm" c={tokens.textMuted}>Last 24h</Text>
                  <Text size="sm" fw={600} c={tokens.textPrimary}>{data.conversations.last24hCount}</Text>
                </Group>
                <Group justify="space-between">
                  <Text size="sm" c={tokens.textMuted}>Last 7d</Text>
                  <Text size="sm" c={tokens.textPrimary}>{data.conversations.last7dCount}</Text>
                </Group>
              </Stack>
            </Card>
          </SimpleGrid>

          {/* Integrations + Widget */}
          <SimpleGrid cols={{ base: 1, sm: 2 }} spacing="md">
            <Card withBorder padding="md" radius="md" bg={tokens.surface}>
              <Text c="dimmed" size="xs" tt="uppercase" fw={600} mb="sm">Integrations</Text>
              <Stack gap="xs">
                <Group justify="space-between">
                  <Text size="sm" c={tokens.textMuted}>Shopify</Text>
                  <BoolBadge value={data.integrations.shopifyConnected} trueLabel="Connected" falseLabel="Disconnected" />
                </Group>
                <Group justify="space-between">
                  <Text size="sm" c={tokens.textMuted}>Stripe</Text>
                  <BoolBadge value={data.integrations.stripeConnected} trueLabel="Connected" falseLabel="Disconnected" />
                </Group>
                <Group justify="space-between">
                  <Text size="sm" c={tokens.textMuted}>NATS</Text>
                  {data.integrations.natsDeployed ? (
                    <BoolBadge value={data.integrations.natsConnected} trueLabel="Connected" falseLabel="Disconnected" />
                  ) : (
                    <Badge variant="light" color="gray" size="sm">Not Deployed</Badge>
                  )}
                </Group>
              </Stack>
            </Card>

            <Card withBorder padding="md" radius="md" bg={tokens.surface}>
              <Text c="dimmed" size="xs" tt="uppercase" fw={600} mb="sm">Widget Deployment</Text>
              <Stack gap="xs">
                <Group justify="space-between">
                  <Text size="sm" c={tokens.textMuted}>Widget Key</Text>
                  <BoolBadge value={data.widget.widgetKeyPresent} trueLabel="Present" falseLabel="Missing" />
                </Group>
                <Group justify="space-between">
                  <Text size="sm" c={tokens.textMuted}>Origin Configured</Text>
                  <BoolBadge value={data.widget.originConfigured} trueLabel="Yes" falseLabel="No" />
                </Group>
              </Stack>
            </Card>
          </SimpleGrid>

          {/* Errors section */}
          <Group justify="space-between" align="baseline" mt="md">
            <Title order={4} c={tokens.textPrimary}>Recent Errors</Title>
            <Button variant="light" size="xs" onClick={handleFetchErrors} loading={errorsLoading}>
              Load Errors
            </Button>
          </Group>

          {errors && (
            <Paper withBorder radius="md" bg={tokens.surface} style={{ overflow: 'auto' }}>
              <Table striped highlightOnHover>
                <Table.Thead>
                  <Table.Tr>
                    <Table.Th>Event Type</Table.Th>
                    <Table.Th>Timestamp</Table.Th>
                    <Table.Th>Actor</Table.Th>
                    <Table.Th>Conversation</Table.Th>
                  </Table.Tr>
                </Table.Thead>
                <Table.Tbody>
                  {errors.entries.length === 0 ? (
                    <Table.Tr>
                      <Table.Td colSpan={4}>
                        <Text c="dimmed" ta="center" py="md">No recent errors</Text>
                      </Table.Td>
                    </Table.Tr>
                  ) : (
                    errors.entries.map((entry, i) => (
                      <Table.Tr key={i}>
                        <Table.Td>
                          <Badge variant="light" color="red" size="sm">{entry.eventType}</Badge>
                        </Table.Td>
                        <Table.Td>
                          <Text size="xs" c={tokens.textMuted}>
                            {new Date(entry.timestamp).toLocaleString()}
                          </Text>
                        </Table.Td>
                        <Table.Td>
                          <Text size="xs" c={tokens.textMuted}>{entry.actor}</Text>
                        </Table.Td>
                        <Table.Td>
                          <Text size="xs" ff="monospace" c={tokens.textSecondary}>
                            {entry.conversationId ?? '—'}
                          </Text>
                        </Table.Td>
                      </Table.Tr>
                    ))
                  )}
                </Table.Tbody>
              </Table>
              {errors.total > errors.entries.length && (
                <Text c="dimmed" size="xs" ta="center" py="xs">
                  Showing {errors.entries.length} of {errors.total} errors
                </Text>
              )}
            </Paper>
          )}

          {/* Metadata */}
          <Text c="dimmed" size="xs" ta="right">
            Generated {new Date(data.generatedAt).toLocaleString()}
          </Text>
        </>
      )}
    </Stack>
  );
}
