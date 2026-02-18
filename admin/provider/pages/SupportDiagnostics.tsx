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
      <Title order={3} c="#F5F5F5">Support Diagnostics</Title>

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
            <Paper withBorder radius="md" p="md" bg="#2a1a1a">
              <Text c="#E5A100" fw={600} size="sm" mb="xs">Partial data — collection errors:</Text>
              {data.collectionErrors.map((e, i) => (
                <Text key={i} c="#E5A100" size="xs">{e}</Text>
              ))}
            </Paper>
          )}

          {/* Summary cards */}
          <SimpleGrid cols={{ base: 1, sm: 2, md: 4 }} spacing="md">
            <Card withBorder padding="md" radius="md" bg="#1f1f1f">
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
            <Card withBorder padding="md" radius="md" bg="#1f1f1f">
              <Text c="dimmed" size="xs" tt="uppercase" fw={600}>Tier</Text>
              <Text fw={700} size="lg" c="#F5F5F5" mt={4}>{data.tier ?? '—'}</Text>
            </Card>
            <Card withBorder padding="md" radius="md" bg="#1f1f1f">
              <Text c="dimmed" size="xs" tt="uppercase" fw={600}>Billing Channel</Text>
              <Text fw={700} size="lg" c="#F5F5F5" mt={4}>{data.billingChannel ?? '—'}</Text>
            </Card>
            <Card withBorder padding="md" radius="md" bg="#1f1f1f">
              <Text c="dimmed" size="xs" tt="uppercase" fw={600}>Created</Text>
              <Text fw={500} size="sm" c="#F5F5F5" mt={4}>
                {data.createdAt ? new Date(data.createdAt).toLocaleDateString() : '—'}
              </Text>
            </Card>
          </SimpleGrid>

          {/* Config state + AI config */}
          <SimpleGrid cols={{ base: 1, sm: 2 }} spacing="md">
            <Card withBorder padding="md" radius="md" bg="#1f1f1f">
              <Text c="dimmed" size="xs" tt="uppercase" fw={600} mb="sm">Configuration State</Text>
              <Stack gap="xs">
                <Group justify="space-between">
                  <Text size="sm" c="#A0A0A0">Active</Text>
                  <BoolBadge value={data.configState.isActive} />
                </Group>
                <Group justify="space-between">
                  <Text size="sm" c="#A0A0A0">Configured</Text>
                  <BoolBadge value={data.configState.isConfigured} />
                </Group>
                <Group justify="space-between">
                  <Text size="sm" c="#A0A0A0">Pending Changes</Text>
                  <BoolBadge value={data.configState.hasPendingChanges} trueLabel="Yes" falseLabel="None" />
                </Group>
                <Group justify="space-between">
                  <Text size="sm" c="#A0A0A0">Active Version</Text>
                  <Text size="sm" c="#F5F5F5">{data.configState.activeVersion ?? '—'}</Text>
                </Group>
              </Stack>
            </Card>

            <Card withBorder padding="md" radius="md" bg="#1f1f1f">
              <Text c="dimmed" size="xs" tt="uppercase" fw={600} mb="sm">AI Configuration</Text>
              <Stack gap="xs">
                <Group justify="space-between">
                  <Text size="sm" c="#A0A0A0">Model</Text>
                  <Text size="sm" c="#F5F5F5">{data.aiConfig.model ?? '—'}</Text>
                </Group>
                <Group justify="space-between">
                  <Text size="sm" c="#A0A0A0">Brand Name</Text>
                  <BoolBadge value={data.aiConfig.brandNamePresent} trueLabel="Set" falseLabel="Missing" />
                </Group>
                <Group justify="space-between">
                  <Text size="sm" c="#A0A0A0">Brand Voice</Text>
                  <BoolBadge value={data.aiConfig.brandVoicePresent} trueLabel="Set" falseLabel="Missing" />
                </Group>
              </Stack>
            </Card>
          </SimpleGrid>

          {/* Knowledge Base + Team + Conversations */}
          <SimpleGrid cols={{ base: 1, sm: 3 }} spacing="md">
            <Card withBorder padding="md" radius="md" bg="#1f1f1f">
              <Text c="dimmed" size="xs" tt="uppercase" fw={600} mb="sm">Knowledge Base</Text>
              <Stack gap="xs">
                <Group justify="space-between">
                  <Text size="sm" c="#A0A0A0">Total Articles</Text>
                  <Text size="sm" fw={600} c="#F5F5F5">{data.knowledgeBase.totalArticles}</Text>
                </Group>
                <Group justify="space-between">
                  <Text size="sm" c="#A0A0A0">Active</Text>
                  <Text size="sm" c="#0D7C3E">{data.knowledgeBase.activeCount}</Text>
                </Group>
                <Group justify="space-between">
                  <Text size="sm" c="#A0A0A0">Draft</Text>
                  <Text size="sm" c="#E5A100">{data.knowledgeBase.draftCount}</Text>
                </Group>
              </Stack>
            </Card>

            <Card withBorder padding="md" radius="md" bg="#1f1f1f">
              <Text c="dimmed" size="xs" tt="uppercase" fw={600} mb="sm">Team</Text>
              <Stack gap="xs">
                <Group justify="space-between">
                  <Text size="sm" c="#A0A0A0">Members</Text>
                  <Text size="sm" fw={600} c="#F5F5F5">{data.team.memberCount}</Text>
                </Group>
                {Object.entries(data.team.rolesBreakdown).map(([role, count]) => (
                  <Group key={role} justify="space-between">
                    <Text size="xs" c="#A0A0A0">{role}</Text>
                    <Text size="xs" c="#E0E0E0">{count}</Text>
                  </Group>
                ))}
              </Stack>
            </Card>

            <Card withBorder padding="md" radius="md" bg="#1f1f1f">
              <Text c="dimmed" size="xs" tt="uppercase" fw={600} mb="sm">Conversations</Text>
              <Stack gap="xs">
                <Group justify="space-between">
                  <Text size="sm" c="#A0A0A0">Last 24h</Text>
                  <Text size="sm" fw={600} c="#F5F5F5">{data.conversations.last24hCount}</Text>
                </Group>
                <Group justify="space-between">
                  <Text size="sm" c="#A0A0A0">Last 7d</Text>
                  <Text size="sm" c="#F5F5F5">{data.conversations.last7dCount}</Text>
                </Group>
              </Stack>
            </Card>
          </SimpleGrid>

          {/* Integrations + Widget */}
          <SimpleGrid cols={{ base: 1, sm: 2 }} spacing="md">
            <Card withBorder padding="md" radius="md" bg="#1f1f1f">
              <Text c="dimmed" size="xs" tt="uppercase" fw={600} mb="sm">Integrations</Text>
              <Stack gap="xs">
                <Group justify="space-between">
                  <Text size="sm" c="#A0A0A0">Shopify</Text>
                  <BoolBadge value={data.integrations.shopifyConnected} trueLabel="Connected" falseLabel="Disconnected" />
                </Group>
                <Group justify="space-between">
                  <Text size="sm" c="#A0A0A0">Stripe</Text>
                  <BoolBadge value={data.integrations.stripeConnected} trueLabel="Connected" falseLabel="Disconnected" />
                </Group>
                <Group justify="space-between">
                  <Text size="sm" c="#A0A0A0">NATS</Text>
                  <BoolBadge value={data.integrations.natsConnected} trueLabel="Connected" falseLabel="Disconnected" />
                </Group>
              </Stack>
            </Card>

            <Card withBorder padding="md" radius="md" bg="#1f1f1f">
              <Text c="dimmed" size="xs" tt="uppercase" fw={600} mb="sm">Widget Deployment</Text>
              <Stack gap="xs">
                <Group justify="space-between">
                  <Text size="sm" c="#A0A0A0">Widget Key</Text>
                  <BoolBadge value={data.widget.widgetKeyPresent} trueLabel="Present" falseLabel="Missing" />
                </Group>
                <Group justify="space-between">
                  <Text size="sm" c="#A0A0A0">Origin Configured</Text>
                  <BoolBadge value={data.widget.originConfigured} trueLabel="Yes" falseLabel="No" />
                </Group>
              </Stack>
            </Card>
          </SimpleGrid>

          {/* Errors section */}
          <Group justify="space-between" align="baseline" mt="md">
            <Title order={4} c="#F5F5F5">Recent Errors</Title>
            <Button variant="light" size="xs" onClick={handleFetchErrors} loading={errorsLoading}>
              Load Errors
            </Button>
          </Group>

          {errors && (
            <Paper withBorder radius="md" bg="#1f1f1f" style={{ overflow: 'auto' }}>
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
                          <Text size="xs" c="#A0A0A0">
                            {new Date(entry.timestamp).toLocaleString()}
                          </Text>
                        </Table.Td>
                        <Table.Td>
                          <Text size="xs" c="#A0A0A0">{entry.actor}</Text>
                        </Table.Td>
                        <Table.Td>
                          <Text size="xs" ff="monospace" c="#E0E0E0">
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
