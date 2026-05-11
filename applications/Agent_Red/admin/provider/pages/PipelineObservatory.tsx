// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * PipelineObservatory -- Pipeline Observatory page (SPEC-1585..1587, SPEC-1786).
 *
 * Four tabs: Infrastructure, Traffic Flow, Agent Metrics, Tenant Comparison.
 * Visualizes the full system topology, 7-agent pipeline health, and performance.
 *
 * APIs:
 *   GET /api/superadmin/pipeline/topology
 *   GET /api/superadmin/pipeline/infrastructure
 *   GET /api/superadmin/pipeline/agents/{agent}/metrics
 *   GET /api/superadmin/pipeline/tenants
 *   GET /api/superadmin/pipeline/tenants/{id}/metrics
 *   GET /api/superadmin/pipeline/database
 *
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useCallback, useEffect, useState } from 'react';
import {
  Badge,
  Card,
  Group,
  Paper,
  Progress,
  Select,
  SimpleGrid,
  Stack,
  Table,
  Tabs,
  Text,
  Title,
  Tooltip,
} from '@mantine/core';
import { useProviderContext } from '../layouts/ProviderLayout';
import { LoadingState } from '../../shared/LoadingState';
import { HelpTooltip } from '../../shared/HelpTooltip';
import { tokens } from '../../shared/theme/styles';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface NodeMetrics {
  agent: string;
  invocationCount: number;
  avgLatencyMs: number;
  p50LatencyMs: number;
  p95LatencyMs: number;
  p99LatencyMs: number;
  errorRate: number;
  avgTokensIn: number;
  avgTokensOut: number;
  avgCost: number;
}

interface EdgeMetrics {
  source: string;
  target: string;
  volume: number;
  avgTransitionLatencyMs: number;
  dropOffRate: number;
}

interface TopologyResponse {
  nodes: NodeMetrics[];
  edges: EdgeMetrics[];
  totalConversations: number;
  period: string;
}

interface TenantSummary {
  tenantId: string;
  displayName: string;
  tier: string | null;
  totalConversations: number;
  billableConversations: number;
  avgLatencyMs: number;
  errorRate: number;
  escalationRate: number;
  tokenConsumption: number;
  cost: number;
  estimatedRu: number;
  resolutionRate: number;
}

interface TenantComparisonResponse {
  tenants: TenantSummary[];
  total: number;
  sortBy: string;
  sortOrder: string;
}

// Infrastructure Topology types (SPEC-1786)
interface InfraNode {
  nodeId: string;
  label: string;
  category: string; // "agent" | "azure" | "ingress" | "egress"
  nodeType: string;
  status: string;
  metrics: Record<string, number>;
  position: { x: number; y: number };
}

interface InfraEdge {
  source: string;
  target: string;
  label: string;
  volume: number;
  avgLatencyMs: number;
  errorRate: number;
  protocol: string;
}

interface InfraTopologyResponse {
  nodes: InfraNode[];
  edges: InfraEdge[];
  period: string;
  totalRequests: number;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const AGENT_LABELS: Record<string, string> = {
  'intent-classifier': 'Intent Classifier',
  'knowledge-retrieval': 'Knowledge Retrieval',
  'response-generator': 'Response Generator',
  'escalation-handler': 'Escalation Handler',
  'analytics-collector': 'Analytics Collector',
  'critic-supervisor': 'Critic Supervisor',
  'co-pilot': 'Co-Pilot',
};

const AGENT_COLORS: Record<string, string> = {
  'intent-classifier': 'blue',
  'knowledge-retrieval': 'cyan',
  'response-generator': 'green',
  'escalation-handler': 'orange',
  'analytics-collector': 'violet',
  'critic-supervisor': 'red',
  'co-pilot': 'pink',
};

function healthColor(errorRate: number): string {
  if (errorRate > 0.05) return tokens.danger;
  if (errorRate > 0.01) return tokens.warning;
  return tokens.success;
}

function formatLatency(ms: number): string {
  if (ms < 1) return '<1ms';
  if (ms >= 1000) return `${(ms / 1000).toFixed(1)}s`;
  return `${Math.round(ms)}ms`;
}

// ---------------------------------------------------------------------------
// Traffic Flow Tab (SPEC-1585)
// ---------------------------------------------------------------------------

function TrafficFlowTab() {
  const { apiFetch, onNotify } = useProviderContext();
  const [data, setData] = useState<TopologyResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState('24h');

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const res = await apiFetch(`/api/superadmin/pipeline/topology?period=${period}`);
      if (res.ok) setData(await res.json());
      else onNotify('Failed to load topology', 'error');
    } catch {
      onNotify('Network error loading topology', 'error');
    } finally {
      setLoading(false);
    }
  }, [apiFetch, onNotify, period]);

  useEffect(() => { loadData(); }, [loadData]);

  if (loading) return <LoadingState text="Loading pipeline topology" />;
  if (!data) return <Text c="dimmed" ta="center">Unable to load topology</Text>;

  return (
    <Stack gap="lg">
      {/* Period selector */}
      <Group gap="md">
        <Select
          label="Time Range"
          data={[
            { value: '1h', label: 'Last Hour' },
            { value: '24h', label: 'Last 24 Hours' },
            { value: '7d', label: 'Last 7 Days' },
            { value: '30d', label: 'Last 30 Days' },
          ]}
          value={period}
          onChange={(val) => setPeriod(val || '24h')}
          style={{ width: 180 }}
        />
        <Card withBorder padding="sm" radius="md" bg={tokens.surface} mt="auto">
          <Text size="xs" c="dimmed" tt="uppercase" fw={600}>Total Conversations</Text>
          <Text fw={700} size="lg" c={tokens.textPrimary}>{data.totalConversations}</Text>
        </Card>
      </Group>

      {/* Agent nodes as cards */}
      <Text size="sm" fw={500} c={tokens.textSecondary}>Pipeline Agents</Text>
      <SimpleGrid cols={{ base: 1, sm: 2, md: 3, lg: 4 }} spacing="md">
        {data.nodes.map((node) => {
          const color = healthColor(node.errorRate);
          return (
            <Card key={node.agent} withBorder padding="md" radius="md" bg={tokens.surface}>
              <Group gap="xs" mb="sm">
                <Badge
                  variant="filled"
                  color={AGENT_COLORS[node.agent] ?? 'gray'}
                  size="sm"
                >
                  {AGENT_LABELS[node.agent] ?? node.agent}
                </Badge>
                <Tooltip label={`Error rate: ${(node.errorRate * 100).toFixed(1)}%`}>
                  <div style={{
                    width: 10,
                    height: 10,
                    borderRadius: '50%',
                    backgroundColor: color,
                  }} />
                </Tooltip>
              </Group>
              <SimpleGrid cols={2} spacing="xs">
                <div>
                  <Text size="xs" c="dimmed">Invocations</Text>
                  <Text size="sm" fw={600} c={tokens.textPrimary}>{node.invocationCount}</Text>
                </div>
                <div>
                  <Text size="xs" c="dimmed">Avg Latency</Text>
                  <Text size="sm" fw={600} c={tokens.textPrimary}>
                    {formatLatency(node.avgLatencyMs)}
                  </Text>
                </div>
                <div>
                  <Text size="xs" c="dimmed">Tokens In</Text>
                  <Text size="sm" c={tokens.textSecondary}>{Math.round(node.avgTokensIn)}</Text>
                </div>
                <div>
                  <Text size="xs" c="dimmed">Avg Cost</Text>
                  <Text size="sm" c={tokens.textSecondary}>
                    ${node.avgCost.toFixed(4)}
                  </Text>
                </div>
              </SimpleGrid>
            </Card>
          );
        })}
      </SimpleGrid>

      {/* Edge flow table */}
      <Paper withBorder radius="md" bg={tokens.surface} style={{ overflow: 'auto' }}>
        <Text size="sm" fw={500} c={tokens.textSecondary} p="md" pb={0}>
          Agent-to-Agent Transitions
        </Text>
        <Table striped highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Source</Table.Th>
              <Table.Th>Target</Table.Th>
              <Table.Th>Volume</Table.Th>
              <Table.Th>Avg Latency</Table.Th>
              <Table.Th>Drop-off</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {data.edges.map((edge, i) => (
              <Table.Tr key={i}>
                <Table.Td>
                  <Badge variant="light" color={AGENT_COLORS[edge.source] ?? 'gray'} size="xs">
                    {AGENT_LABELS[edge.source] ?? edge.source}
                  </Badge>
                </Table.Td>
                <Table.Td>
                  <Badge variant="light" color={AGENT_COLORS[edge.target] ?? 'gray'} size="xs">
                    {AGENT_LABELS[edge.target] ?? edge.target}
                  </Badge>
                </Table.Td>
                <Table.Td>
                  <Text size="xs" fw={500} c={tokens.textSecondary}>{edge.volume}</Text>
                </Table.Td>
                <Table.Td>
                  <Text size="xs" c={tokens.textSecondary}>
                    {formatLatency(edge.avgTransitionLatencyMs)}
                  </Text>
                </Table.Td>
                <Table.Td>
                  <Text size="xs" c={edge.dropOffRate > 0.1 ? tokens.danger : tokens.textMuted}>
                    {(edge.dropOffRate * 100).toFixed(1)}%
                  </Text>
                </Table.Td>
              </Table.Tr>
            ))}
          </Table.Tbody>
        </Table>
      </Paper>
    </Stack>
  );
}

// ---------------------------------------------------------------------------
// Agent Metrics Tab (SPEC-1586)
// ---------------------------------------------------------------------------

function AgentMetricsTab() {
  const { apiFetch, onNotify } = useProviderContext();
  const [data, setData] = useState<TopologyResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await apiFetch('/api/superadmin/pipeline/topology?period=24h');
        if (res.ok && !cancelled) setData(await res.json());
      } catch {
        if (!cancelled) onNotify('Failed to load agent metrics', 'error');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [apiFetch, onNotify]);

  if (loading) return <LoadingState text="Loading agent metrics" />;
  if (!data) return <Text c="dimmed" ta="center">Unable to load agent metrics</Text>;

  return (
    <Stack gap="md">
      <SimpleGrid cols={{ base: 1, sm: 2, lg: 3 }} spacing="md">
        {data.nodes.map((node) => {
          const color = healthColor(node.errorRate);
          const agentColor = AGENT_COLORS[node.agent] ?? 'gray';
          return (
            <Card key={node.agent} withBorder padding="md" radius="md" bg={tokens.surface}>
              <Group gap="xs" mb="md">
                <Badge variant="filled" color={agentColor} size="md">
                  {AGENT_LABELS[node.agent] ?? node.agent}
                </Badge>
                <Badge variant="outline" color={color === tokens.success ? 'green' : color === tokens.warning ? 'yellow' : 'red'} size="xs">
                  {(node.errorRate * 100).toFixed(1)}% errors
                </Badge>
              </Group>

              {/* Key metrics */}
              <Stack gap="xs">
                <Group gap="lg">
                  <div>
                    <Text size="xs" c="dimmed">Invocations</Text>
                    <Text size="lg" fw={700} c={tokens.textPrimary}>{node.invocationCount}</Text>
                  </div>
                  <div>
                    <Text size="xs" c="dimmed">Avg Cost</Text>
                    <Text size="lg" fw={700} c={tokens.textPrimary}>${node.avgCost.toFixed(4)}</Text>
                  </div>
                </Group>

                {/* Latency percentiles */}
                <Paper withBorder radius="sm" p="xs" bg={tokens.surface}>
                  <Text size="xs" c="dimmed" mb={4}>Latency Percentiles</Text>
                  <Group gap="md">
                    <div>
                      <Text size="xs" fw={600} c={tokens.chartBlue}>P50</Text>
                      <Text size="xs">{formatLatency(node.p50LatencyMs)}</Text>
                    </div>
                    <div>
                      <Text size="xs" fw={600} c={tokens.warning}>P95</Text>
                      <Text size="xs">{formatLatency(node.p95LatencyMs)}</Text>
                    </div>
                    <div>
                      <Text size="xs" fw={600} c={tokens.danger}>P99</Text>
                      <Text size="xs">{formatLatency(node.p99LatencyMs)}</Text>
                    </div>
                  </Group>
                </Paper>

                {/* Token usage */}
                <Group gap="md">
                  <div>
                    <Text size="xs" c="dimmed">Avg Tokens In</Text>
                    <Text size="sm" c={tokens.textSecondary}>{Math.round(node.avgTokensIn)}</Text>
                  </div>
                  <div>
                    <Text size="xs" c="dimmed">Avg Tokens Out</Text>
                    <Text size="sm" c={tokens.textSecondary}>{Math.round(node.avgTokensOut)}</Text>
                  </div>
                </Group>
              </Stack>
            </Card>
          );
        })}
      </SimpleGrid>
    </Stack>
  );
}

// ---------------------------------------------------------------------------
// Tenant Comparison Tab (SPEC-1587)
// ---------------------------------------------------------------------------

function TenantComparisonTab() {
  const { apiFetch, onNotify } = useProviderContext();
  const [data, setData] = useState<TenantComparisonResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState('totalConversations');

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const res = await apiFetch(
        `/api/superadmin/pipeline/tenants?sort_by=${sortBy}&sort_order=desc`
      );
      if (res.ok) setData(await res.json());
      else onNotify('Failed to load tenant comparison', 'error');
    } catch {
      onNotify('Network error loading tenant comparison', 'error');
    } finally {
      setLoading(false);
    }
  }, [apiFetch, onNotify, sortBy]);

  useEffect(() => { loadData(); }, [loadData]);

  if (loading) return <LoadingState text="Loading tenant comparison" />;
  if (!data) return <Text c="dimmed" ta="center">Unable to load tenant comparison</Text>;

  return (
    <Stack gap="md">
      <Group gap="md">
        <Select
          label="Sort By"
          data={[
            { value: 'totalConversations', label: 'Conversations' },
            { value: 'avgLatencyMs', label: 'Avg Latency' },
            { value: 'errorRate', label: 'Error Rate' },
            { value: 'cost', label: 'Cost' },
            { value: 'tokenConsumption', label: 'Token Usage' },
          ]}
          value={sortBy}
          onChange={(val) => setSortBy(val || 'totalConversations')}
          style={{ width: 200 }}
        />
        <Card withBorder padding="sm" radius="md" bg={tokens.surface} mt="auto">
          <Text size="xs" c="dimmed" tt="uppercase" fw={600}>Total Tenants</Text>
          <Text fw={700} size="lg" c={tokens.textPrimary}>{data.total}</Text>
        </Card>
      </Group>

      <Paper withBorder radius="md" bg={tokens.surface} style={{ overflow: 'auto' }}>
        <Table striped highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Tenant</Table.Th>
              <Table.Th>Tier</Table.Th>
              <Table.Th>Conversations</Table.Th>
              <Table.Th>Billable</Table.Th>
              <Table.Th>Avg Latency</Table.Th>
              <Table.Th>Error Rate</Table.Th>
              <Table.Th>Escalation</Table.Th>
              <Table.Th>Tokens</Table.Th>
              <Table.Th>Cost</Table.Th>
              <Table.Th>Est. RU</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {(data.tenants ?? []).length === 0 ? (
              <Table.Tr>
                <Table.Td colSpan={10}>
                  <Text c="dimmed" ta="center" py="md">No tenant data available</Text>
                </Table.Td>
              </Table.Tr>
            ) : (
              (data.tenants ?? []).map((t) => (
                <Table.Tr key={t.tenantId}>
                  <Table.Td>
                    <Tooltip label={t.tenantId} position="right" withArrow>
                      <Text size="xs" fw={500} c={tokens.textSecondary} style={{ cursor: 'help' }}>
                        {t.displayName}
                      </Text>
                    </Tooltip>
                  </Table.Td>
                  <Table.Td>
                    <Text size="xs" c={tokens.textMuted}>{t.tier ?? '\u2014'}</Text>
                  </Table.Td>
                  <Table.Td>
                    <Text size="xs" fw={500} c={tokens.textPrimary}>{t.totalConversations}</Text>
                  </Table.Td>
                  <Table.Td>
                    <Text size="xs" c={tokens.textSecondary}>{t.billableConversations}</Text>
                  </Table.Td>
                  <Table.Td>
                    <Text size="xs" c={tokens.textSecondary}>
                      {formatLatency(t.avgLatencyMs)}
                    </Text>
                  </Table.Td>
                  <Table.Td>
                    <Text size="xs" c={t.errorRate > 0.05 ? tokens.danger : tokens.textMuted}>
                      {(t.errorRate * 100).toFixed(1)}%
                    </Text>
                  </Table.Td>
                  <Table.Td>
                    <Text size="xs" c={tokens.textSecondary}>
                      {(t.escalationRate * 100).toFixed(1)}%
                    </Text>
                  </Table.Td>
                  <Table.Td>
                    <Text size="xs" c={tokens.textSecondary}>
                      {t.tokenConsumption.toLocaleString()}
                    </Text>
                  </Table.Td>
                  <Table.Td>
                    <Text size="xs" fw={500} c={tokens.textPrimary}>
                      ${t.cost.toFixed(2)}
                    </Text>
                  </Table.Td>
                  <Table.Td>
                    <Text size="xs" c={tokens.textMuted}>
                      {t.estimatedRu.toFixed(0)}
                    </Text>
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

// ---------------------------------------------------------------------------
// Infrastructure Topology Tab (SPEC-1786)
// ---------------------------------------------------------------------------

const CATEGORY_COLORS: Record<string, string> = {
  agent: 'blue',
  azure: 'cyan',
  ingress: 'green',
  egress: 'orange',
};

const STATUS_INDICATOR: Record<string, string> = {
  healthy: tokens.success,
  degraded: tokens.warning,
  error: tokens.danger,
};

const NODE_TYPE_LABELS: Record<string, string> = {
  'container-app': 'Container App',
  'cosmos-db': 'Cosmos DB',
  redis: 'Redis Cache',
  openai: 'Azure OpenAI',
  nats: 'NATS JetStream',
  'key-vault': 'Key Vault',
  cdn: 'CDN',
  webhook: 'Webhook',
  widget: 'Chat Widget',
  spa: 'SPA Console',
  'embedded-app': 'Embedded App',
};

function InfrastructureTab() {
  const { apiFetch, onNotify } = useProviderContext();
  const [data, setData] = useState<InfraTopologyResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState('24h');

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const res = await apiFetch(
        `/api/superadmin/pipeline/infrastructure?period=${period}`
      );
      if (res.ok) setData(await res.json());
      else onNotify('Failed to load infrastructure topology', 'error');
    } catch {
      onNotify('Network error loading infrastructure', 'error');
    } finally {
      setLoading(false);
    }
  }, [apiFetch, onNotify, period]);

  useEffect(() => { loadData(); }, [loadData]);

  if (loading) return <LoadingState text="Loading infrastructure topology" />;
  if (!data) return <Text c="dimmed" ta="center">Unable to load infrastructure</Text>;

  // Group nodes by layer (y position)
  const layers = new Map<number, InfraNode[]>();
  for (const node of data.nodes) {
    const y = node.position?.y ?? 0;
    if (!layers.has(y)) layers.set(y, []);
    layers.get(y)!.push(node);
  }
  const sortedLayers = [...layers.entries()].sort(([a], [b]) => a - b);

  const layerLabels: Record<number, string> = {
    0: 'Ingress Points',
    1: 'API Gateway',
    2: 'Pipeline Agents (Tier 1)',
    3: 'Pipeline Agents (Tier 2)',
    4: 'Infrastructure Services',
    5: 'Content Delivery',
  };

  return (
    <Stack gap="lg">
      <Group gap="md">
        <Select
          label="Time Range"
          data={[
            { value: '1h', label: 'Last Hour' },
            { value: '24h', label: 'Last 24 Hours' },
            { value: '7d', label: 'Last 7 Days' },
            { value: '30d', label: 'Last 30 Days' },
          ]}
          value={period}
          onChange={(val) => setPeriod(val || '24h')}
          style={{ width: 180 }}
        />
        <Card withBorder padding="sm" radius="md" bg={tokens.surface} mt="auto">
          <Text size="xs" c="dimmed" tt="uppercase" fw={600}>Total Requests</Text>
          <Text fw={700} size="lg" c={tokens.textPrimary}>{data.totalRequests}</Text>
        </Card>
      </Group>

      {/* Topology layers */}
      {sortedLayers.map(([y, layerNodes]) => (
        <div key={y}>
          <Text size="sm" fw={600} c={tokens.textSecondary} mb="xs">
            {layerLabels[y] ?? `Layer ${y}`}
          </Text>
          <SimpleGrid
            cols={{ base: 1, sm: 2, md: Math.min(layerNodes.length, 5) }}
            spacing="sm"
          >
            {layerNodes.map((node) => {
              const statusColor = STATUS_INDICATOR[node.status] ?? tokens.textMuted;
              const catColor = CATEGORY_COLORS[node.category] ?? 'gray';
              return (
                <Card
                  key={node.nodeId}
                  withBorder
                  padding="sm"
                  radius="md"
                  bg={tokens.surface}
                  style={{ borderLeft: `3px solid ${statusColor}` }}
                >
                  <Group gap="xs" mb="xs">
                    <Badge variant="filled" color={catColor} size="xs">
                      {node.category}
                    </Badge>
                    <Text size="sm" fw={600} c={tokens.textPrimary}>
                      {node.label}
                    </Text>
                    <Tooltip label={`Status: ${node.status}`}>
                      <div style={{
                        width: 8,
                        height: 8,
                        borderRadius: '50%',
                        backgroundColor: statusColor,
                      }} />
                    </Tooltip>
                  </Group>
                  <Text size="xs" c="dimmed">
                    {NODE_TYPE_LABELS[node.nodeType] ?? node.nodeType}
                  </Text>
                  {node.metrics && Object.keys(node.metrics).length > 0 && (
                    <Group gap="md" mt="xs">
                      {node.metrics.invocation_count != null && (
                        <div>
                          <Text size="xs" c="dimmed">Invocations</Text>
                          <Text size="xs" fw={500}>{node.metrics.invocation_count}</Text>
                        </div>
                      )}
                      {node.metrics.avg_latency_ms != null && (
                        <div>
                          <Text size="xs" c="dimmed">Avg Latency</Text>
                          <Text size="xs" fw={500}>
                            {formatLatency(node.metrics.avg_latency_ms)}
                          </Text>
                        </div>
                      )}
                      {node.metrics.error_rate != null && (
                        <div>
                          <Text size="xs" c="dimmed">Error Rate</Text>
                          <Text
                            size="xs"
                            fw={500}
                            c={node.metrics.error_rate > 0.05 ? tokens.danger : undefined}
                          >
                            {(node.metrics.error_rate * 100).toFixed(1)}%
                          </Text>
                        </div>
                      )}
                    </Group>
                  )}
                </Card>
              );
            })}
          </SimpleGrid>
        </div>
      ))}

      {/* Edge flow table */}
      <Paper withBorder radius="md" bg={tokens.surface} style={{ overflow: 'auto' }}>
        <Text size="sm" fw={500} c={tokens.textSecondary} p="md" pb={0}>
          Traffic Flow Connections
        </Text>
        <Table striped highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Source</Table.Th>
              <Table.Th>Target</Table.Th>
              <Table.Th>Protocol</Table.Th>
              <Table.Th>Label</Table.Th>
              <Table.Th>Volume</Table.Th>
              <Table.Th>Avg Latency</Table.Th>
              <Table.Th>Error Rate</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {data.edges.map((edge, i) => (
              <Table.Tr key={i}>
                <Table.Td><Text size="xs" c={tokens.textSecondary}>{edge.source}</Text></Table.Td>
                <Table.Td><Text size="xs" c={tokens.textSecondary}>{edge.target}</Text></Table.Td>
                <Table.Td><Badge variant="light" size="xs">{edge.protocol}</Badge></Table.Td>
                <Table.Td><Text size="xs" c="dimmed">{edge.label}</Text></Table.Td>
                <Table.Td>
                  <Text size="xs" fw={500} c={tokens.textPrimary}>
                    {edge.volume > 0 ? edge.volume.toLocaleString() : '\u2014'}
                  </Text>
                </Table.Td>
                <Table.Td>
                  <Text size="xs" c={tokens.textSecondary}>
                    {edge.avgLatencyMs > 0 ? formatLatency(edge.avgLatencyMs) : '\u2014'}
                  </Text>
                </Table.Td>
                <Table.Td>
                  <Text
                    size="xs"
                    c={edge.errorRate > 0.05 ? tokens.danger : tokens.textMuted}
                  >
                    {edge.errorRate > 0 ? `${(edge.errorRate * 100).toFixed(1)}%` : '\u2014'}
                  </Text>
                </Table.Td>
              </Table.Tr>
            ))}
          </Table.Tbody>
        </Table>
      </Paper>
    </Stack>
  );
}

// ---------------------------------------------------------------------------
// Main Page Component
// ---------------------------------------------------------------------------

export function PipelineObservatoryPage() {
  return (
    <Stack gap="lg">
      <Group gap="xs">
        <Title order={3} c={tokens.textPrimary}>Pipeline Observatory</Title>
        <HelpTooltip text="Monitor the full system infrastructure and 7-agent AI pipeline performance across all tenants." />
      </Group>

      <Tabs defaultValue="infrastructure" variant="outline">
        <Tabs.List>
          <Tabs.Tab value="infrastructure">Infrastructure</Tabs.Tab>
          <Tabs.Tab value="traffic">Traffic Flow</Tabs.Tab>
          <Tabs.Tab value="agents">Agent Metrics</Tabs.Tab>
          <Tabs.Tab value="tenants">Tenant Comparison</Tabs.Tab>
        </Tabs.List>

        <Tabs.Panel value="infrastructure" pt="md">
          <InfrastructureTab />
        </Tabs.Panel>
        <Tabs.Panel value="traffic" pt="md">
          <TrafficFlowTab />
        </Tabs.Panel>
        <Tabs.Panel value="agents" pt="md">
          <AgentMetricsTab />
        </Tabs.Panel>
        <Tabs.Panel value="tenants" pt="md">
          <TenantComparisonTab />
        </Tabs.Panel>
      </Tabs>
    </Stack>
  );
}
