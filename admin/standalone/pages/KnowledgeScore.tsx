// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

/**
 * Knowledge Score page — composite quality score + gap review (SPEC-1873).
 *
 * Displays:
 *   1. Composite knowledge score (0-100) with ring progress
 *   2. Four factor breakdown bars (coverage, relevance, escalation, freshness)
 *   3. Trend badge vs previous 30-day window
 *   4. Stats row (total conversations, unanswered, KB entries, fresh entries)
 *   5. Gap review table — clustered unanswered questions sorted by priority
 *
 * Professional+ tier required. Lower tiers see an upgrade prompt.
 * Admin role required via ProtectedRoute (wired in index.tsx).
 */

import React, { useMemo, useState } from 'react';
import {
  Paper,
  Group,
  Stack,
  Text,
  SimpleGrid,
  Title,
  Table,
  Progress,
  SegmentedControl,
  Badge,
  Loader,
  RingProgress,
  Collapse,
  ActionIcon,
  Tooltip,
  Alert,
} from '@mantine/core';
import { useAppContext } from '../layouts/StandaloneLayout';
import { useKnowledgeScore, useGapReview } from '../../shared/hooks/index';
import type { GapCluster } from '../../shared/hooks/index';
import { tokens } from '../../shared/theme/styles';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const BRAND_RED = tokens.brand;
const PROFESSIONAL_TIER = 'professional';
const TIER_ORDER: Record<string, number> = { free: 0, starter: 1, professional: 2, enterprise: 3 };

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function scoreColor(score: number): string {
  if (score >= 80) return '#40c057';  // green
  if (score >= 60) return '#fab005';  // yellow
  if (score >= 40) return '#fd7e14';  // orange
  return '#fa5252';                    // red
}

function trendBadge(trend: { direction?: string; delta?: number }): React.ReactNode {
  if (!trend.direction || trend.direction === '=') {
    return <Badge variant="light" color="gray" size="sm">Stable</Badge>;
  }
  if (trend.direction === 'up') {
    return (
      <Badge variant="light" color="green" size="sm">
        +{trend.delta?.toFixed(1) ?? '?'}
      </Badge>
    );
  }
  return (
    <Badge variant="light" color="red" size="sm">
      {trend.delta?.toFixed(1) ?? '?'}
    </Badge>
  );
}

function formatDate(iso: string): string {
  try {
    const d = new Date(iso);
    if (isNaN(d.getTime())) return iso;
    return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
  } catch {
    return iso;
  }
}

function factorLabel(key: string): string {
  switch (key) {
    case 'coverage': return 'Coverage';
    case 'relevance': return 'Relevance';
    case 'escalationRate': return 'Escalation rate';
    case 'freshness': return 'Freshness';
    default: return key;
  }
}

function factorDescription(key: string): string {
  switch (key) {
    case 'coverage': return 'Fraction of queries answered without escalation';
    case 'relevance': return 'Average knowledge retrieval relevance score';
    case 'escalationRate': return 'Rate of escalated/error conversations (lower is better)';
    case 'freshness': return 'Fraction of KB entries updated within 30 days';
    default: return '';
  }
}

/** For escalation rate, invert the display (lower = better). */
function factorValue(key: string, value: number): number {
  if (key === 'escalationRate') return 1 - value;
  return value;
}

function factorColor(key: string, value: number): string {
  const v = factorValue(key, value);
  if (v >= 0.8) return 'green';
  if (v >= 0.6) return 'yellow';
  if (v >= 0.4) return 'orange';
  return 'red';
}

// ---------------------------------------------------------------------------
// Period to ISO since date
// ---------------------------------------------------------------------------

function periodToSince(period: string): string | undefined {
  const days = parseInt(period.replace('d', ''), 10);
  if (isNaN(days)) return undefined;
  const d = new Date(Date.now() - days * 24 * 60 * 60 * 1000);
  return d.toISOString();
}

// ---------------------------------------------------------------------------
// StatCard (matches Analytics page pattern)
// ---------------------------------------------------------------------------

interface StatCardProps {
  label: string;
  value: string;
  detail?: string;
}

function StatCard({ label, value, detail }: StatCardProps) {
  return (
    <Paper p="lg" radius="md" withBorder>
      <Text size="xs" c="dimmed" fw={600} mb={4}>
        {label}
      </Text>
      <Text size="xl" fw={700} lh={1}>
        {value}
      </Text>
      {detail && (
        <Text size="xs" c="dimmed" mt={6}>
          {detail}
        </Text>
      )}
    </Paper>
  );
}

// ---------------------------------------------------------------------------
// GapRow — expandable row showing conversation IDs
// ---------------------------------------------------------------------------

function GapRow({ cluster }: { cluster: GapCluster }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <>
      <Table.Tr
        style={{ cursor: cluster.conversationIds.length > 0 ? 'pointer' : undefined }}
        onClick={() => cluster.conversationIds.length > 0 && setExpanded(!expanded)}
      >
        <Table.Td>
          <Badge variant="light" color="blue" size="sm">{cluster.intent}</Badge>
        </Table.Td>
        <Table.Td style={{ maxWidth: 300 }}>
          <Text size="sm" lineClamp={2}>{cluster.sampleQuestion}</Text>
        </Table.Td>
        <Table.Td>
          <Text size="sm" fw={600}>{cluster.frequency}</Text>
        </Table.Td>
        <Table.Td>
          <Text size="sm">{formatDate(cluster.lastOccurrence)}</Text>
        </Table.Td>
        <Table.Td>
          <Text size="sm">{cluster.suggestedAction}</Text>
        </Table.Td>
        <Table.Td>
          <Badge
            variant="filled"
            color={cluster.priorityScore >= 0.7 ? 'red' : cluster.priorityScore >= 0.4 ? 'orange' : 'gray'}
            size="sm"
          >
            {(cluster.priorityScore * 100).toFixed(0)}
          </Badge>
        </Table.Td>
        <Table.Td>
          {cluster.conversationIds.length > 0 && (
            <ActionIcon variant="subtle" size="sm">
              <Text size="xs">{expanded ? '▲' : '▼'}</Text>
            </ActionIcon>
          )}
        </Table.Td>
      </Table.Tr>
      {cluster.conversationIds.length > 0 && (
        <Table.Tr>
          <Table.Td colSpan={7} p={0}>
            <Collapse in={expanded}>
              <Paper p="sm" bg="var(--mantine-color-dark-8)" radius={0}>
                <Text size="xs" c="dimmed" mb={4}>Conversation IDs ({cluster.conversationIds.length})</Text>
                <Text size="xs" style={{ fontFamily: 'monospace', wordBreak: 'break-all' }}>
                  {cluster.conversationIds.join(', ')}
                </Text>
              </Paper>
            </Collapse>
          </Table.Td>
        </Table.Tr>
      )}
    </>
  );
}

// ---------------------------------------------------------------------------
// KnowledgeScorePage
// ---------------------------------------------------------------------------

export const KnowledgeScorePage: React.FC = () => {
  const { apiFetch, tenantContext } = useAppContext();
  const [period, setPeriod] = useState('30d');
  const since = useMemo(() => periodToSince(period), [period]);

  // Tier gate BEFORE hooks — prevents 403 from triggering global logout
  const tier = tenantContext?.tier ?? 'free';
  const hasTier = TIER_ORDER[tier] >= TIER_ORDER[PROFESSIONAL_TIER];

  const score = useKnowledgeScore(apiFetch, since, hasTier);
  const gaps = useGapReview(apiFetch, { since, limit: 50, enabled: hasTier });

  if (!hasTier) {
    return (
      <Stack gap="lg">
        <Title order={2}>Knowledge Score</Title>
        <Alert color="yellow" title="Professional tier required">
          Knowledge Score and gap review require a Professional or Enterprise subscription.
          Upgrade your plan to access quality insights.
        </Alert>
      </Stack>
    );
  }

  const s = score.data;
  const gapList = gaps.data?.clusters ?? [];
  const isLoading = score.loading && !s;

  return (
    <Stack gap="lg">
      {/* Page header */}
      <Group justify="space-between" align="flex-end">
        <div>
          <Title order={2}>Knowledge Score</Title>
          <Text c="dimmed" size="sm">
            Knowledge quality metrics and unanswered question review
          </Text>
        </div>
        <SegmentedControl
          value={period}
          onChange={setPeriod}
          data={[
            { label: '7d', value: '7d' },
            { label: '14d', value: '14d' },
            { label: '30d', value: '30d' },
            { label: '90d', value: '90d' },
          ]}
          size="sm"
        />
      </Group>

      {/* Loading */}
      {isLoading && (
        <Group justify="center" py="xl">
          <Loader size="sm" />
          <Text size="sm" c="dimmed">Loading knowledge score...</Text>
        </Group>
      )}

      {/* Error */}
      {score.error && (
        <Alert color="red" title="Error loading score">
          {score.error}
        </Alert>
      )}

      {/* Score card + factors */}
      {s && (
        <>
          <SimpleGrid cols={{ base: 1, md: 2 }} spacing="lg">
            {/* Composite score ring */}
            <Paper p="xl" radius="md" withBorder>
              <Group gap="xl" align="center">
                <RingProgress
                  size={140}
                  thickness={14}
                  roundCaps
                  sections={[{ value: s.score, color: scoreColor(s.score) }]}
                  label={
                    <Text ta="center" fw={700} size="xl">
                      {s.score.toFixed(0)}
                    </Text>
                  }
                />
                <Stack gap="xs">
                  <Text fw={600} size="lg">Composite Score</Text>
                  <Group gap="xs">
                    {trendBadge(s.trend)}
                    {s.trend.previous != null && (
                      <Text size="xs" c="dimmed">
                        vs {s.trend.previous.toFixed(0)} previous
                      </Text>
                    )}
                  </Group>
                  <Text size="xs" c="dimmed">
                    Based on {s.totalConversations} conversations
                  </Text>
                </Stack>
              </Group>
            </Paper>

            {/* Factor breakdown */}
            <Paper p="xl" radius="md" withBorder>
              <Text fw={600} mb="md">Factor Breakdown</Text>
              <Stack gap="sm">
                {(['coverage', 'relevance', 'escalationRate', 'freshness'] as const).map((key) => {
                  const raw = s.factors[key];
                  const display = factorValue(key, raw);
                  return (
                    <div key={key}>
                      <Group justify="space-between" mb={4}>
                        <Tooltip label={factorDescription(key)}>
                          <Text size="sm">{factorLabel(key)}</Text>
                        </Tooltip>
                        <Text size="sm" fw={600}>{(display * 100).toFixed(0)}%</Text>
                      </Group>
                      <Progress
                        value={display * 100}
                        color={factorColor(key, raw)}
                        size="md"
                        radius="xl"
                      />
                    </div>
                  );
                })}
              </Stack>
            </Paper>
          </SimpleGrid>

          {/* Stats row */}
          <SimpleGrid cols={{ base: 2, md: 4 }} spacing="md">
            <StatCard
              label="Total conversations"
              value={s.totalConversations.toLocaleString()}
            />
            <StatCard
              label="Unanswered"
              value={s.unansweredCount.toLocaleString()}
              detail={s.totalConversations > 0
                ? `${((s.unansweredCount / s.totalConversations) * 100).toFixed(1)}% of total`
                : undefined}
            />
            <StatCard
              label="KB entries"
              value={s.kbEntryCount.toLocaleString()}
            />
            <StatCard
              label="Fresh entries"
              value={s.freshEntryCount.toLocaleString()}
              detail={s.kbEntryCount > 0
                ? `${((s.freshEntryCount / s.kbEntryCount) * 100).toFixed(0)}% updated <30d`
                : undefined}
            />
          </SimpleGrid>
        </>
      )}

      {/* Gap review table */}
      <Paper p="lg" radius="md" withBorder>
        <Group justify="space-between" mb="md">
          <div>
            <Text fw={600}>Unanswered Question Clusters</Text>
            <Text size="xs" c="dimmed">
              Grouped by detected intent, sorted by priority
            </Text>
          </div>
          {gaps.data && (
            <Badge variant="light" color="gray" size="sm">
              {gaps.data.totalGaps} total gaps
            </Badge>
          )}
        </Group>

        {gaps.loading && !gaps.data && (
          <Group justify="center" py="md">
            <Loader size="sm" />
          </Group>
        )}

        {gaps.error && (
          <Alert color="red" title="Error loading gaps" mb="md">
            {gaps.error}
          </Alert>
        )}

        {gapList.length === 0 && !gaps.loading && (
          <Text size="sm" c="dimmed" ta="center" py="xl">
            No unanswered question clusters found for this period.
          </Text>
        )}

        {gapList.length > 0 && (
          <Table striped highlightOnHover>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Intent</Table.Th>
                <Table.Th>Sample question</Table.Th>
                <Table.Th>Freq</Table.Th>
                <Table.Th>Last seen</Table.Th>
                <Table.Th>Suggested action</Table.Th>
                <Table.Th>Priority</Table.Th>
                <Table.Th w={40}></Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {gapList.map((cluster, idx) => (
                <GapRow key={`${cluster.intent}-${idx}`} cluster={cluster} />
              ))}
            </Table.Tbody>
          </Table>
        )}
      </Paper>
    </Stack>
  );
};
