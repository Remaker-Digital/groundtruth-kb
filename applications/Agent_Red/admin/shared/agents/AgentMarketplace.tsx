// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * AgentMarketplace — browse and install/uninstall peer agents (SPEC-1865).
 *
 * Card-based layout with category filter. Each card shows agent details,
 * skill count, tier gate, and an Install/Uninstall button. Actions are
 * best-effort with user feedback via onNotify.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useState, useMemo, useCallback } from 'react';
import {
  Badge,
  Button,
  Card,
  Group,
  Select,
  SimpleGrid,
  Stack,
  Text,
  TextInput,
  Title,
} from '@mantine/core';
import type { BaseComponentProps } from '../types';
import {
  useMarketplace,
  useInstallAgent,
  useUninstallAgent,
} from '../hooks/useMarketplace';
import type { MarketplaceAgent } from '../hooks/useMarketplace';
import { getAgentLogo } from '../icons/agent-logos';
import { tokens } from '../theme/styles';

interface AgentMarketplaceProps extends BaseComponentProps {}

const TIER_COLORS: Record<string, string> = {
  free: 'green',
  starter: 'blue',
  professional: 'violet',
  enterprise: 'orange',
};

export const AgentMarketplace: React.FC<AgentMarketplaceProps> = ({
  tenantContext,
  apiFetch,
  onNotify,
}) => {
  const [categoryFilter, setCategoryFilter] = useState<string | null>(null);
  const [search, setSearch] = useState('');

  const { data, loading, error, refetch } = useMarketplace(
    apiFetch,
    categoryFilter || undefined,
  );
  const { install, loading: installing } = useInstallAgent(apiFetch);
  const { uninstall, loading: uninstalling } = useUninstallAgent(apiFetch);

  const agents = data?.agents ?? [];

  // Derive category options from agent data
  const categories = useMemo(() => {
    const cats = new Set(agents.map((a) => a.category));
    return Array.from(cats)
      .sort()
      .map((c) => ({ value: c, label: c.charAt(0).toUpperCase() + c.slice(1) }));
  }, [agents]);

  // Client-side search filter
  const filtered = useMemo(() => {
    if (!search.trim()) return agents;
    const q = search.toLowerCase();
    return agents.filter(
      (a) =>
        a.displayName.toLowerCase().includes(q) ||
        a.description.toLowerCase().includes(q) ||
        a.agentId.toLowerCase().includes(q),
    );
  }, [agents, search]);

  const handleInstall = useCallback(
    async (agentId: string) => {
      try {
        const result = await install(agentId);
        onNotify(
          `Installed ${agentId}: ${result.bindingsCreated} skill bindings created` +
            (result.bindingsFailed > 0
              ? ` (${result.bindingsFailed} failed)`
              : ''),
          result.bindingsFailed > 0 ? 'warning' : 'success',
        );
        refetch();
      } catch (err: unknown) {
        onNotify(
          `Install failed: ${err instanceof Error ? err.message : 'Unknown error'}`,
          'error',
        );
      }
    },
    [install, onNotify, refetch],
  );

  const handleUninstall = useCallback(
    async (agentId: string) => {
      try {
        await uninstall(agentId);
        onNotify(`Uninstalled ${agentId}`, 'success');
        refetch();
      } catch (err: unknown) {
        onNotify(
          `Uninstall failed: ${err instanceof Error ? err.message : 'Unknown error'}`,
          'error',
        );
      }
    },
    [uninstall, onNotify, refetch],
  );

  return (
    <Stack gap="md" p="md">
      <Group justify="space-between" align="flex-end">
        <Title order={3}>Agent Marketplace</Title>
        <Group gap="sm">
          <TextInput
            placeholder="Search agents..."
            value={search}
            onChange={(e) => setSearch(e.currentTarget.value)}
            style={{ width: 220 }}
          />
          <Select
            placeholder="All categories"
            data={categories}
            value={categoryFilter}
            onChange={setCategoryFilter}
            clearable
            style={{ width: 180 }}
          />
        </Group>
      </Group>

      {error && (
        <Text c="red" size="sm">
          {error}
        </Text>
      )}

      {loading && <Text size="sm">Loading marketplace...</Text>}

      <SimpleGrid cols={{ base: 1, sm: 2, lg: 3 }} spacing="md">
        {filtered.map((agent) => (
          <AgentCard
            key={agent.agentId}
            agent={agent}
            onInstall={handleInstall}
            onUninstall={handleUninstall}
            actionLoading={installing || uninstalling}
          />
        ))}
      </SimpleGrid>

      {!loading && filtered.length === 0 && (
        <Text c="dimmed" ta="center" mt="xl">
          No agents available{categoryFilter ? ` in "${categoryFilter}"` : ''}.
        </Text>
      )}
    </Stack>
  );
};

// ---------------------------------------------------------------------------
// AgentCard
// ---------------------------------------------------------------------------

interface AgentCardProps {
  agent: MarketplaceAgent;
  onInstall: (agentId: string) => void;
  onUninstall: (agentId: string) => void;
  actionLoading: boolean;
}

const AgentCard: React.FC<AgentCardProps> = ({
  agent,
  onInstall,
  onUninstall,
  actionLoading,
}) => {
  const Logo = getAgentLogo(agent.agentId);

  return (
    <Card
      shadow="sm"
      padding="lg"
      radius="md"
      withBorder
      style={{
        borderColor: agent.installed ? tokens.brand : undefined,
      }}
    >
      <Group justify="space-between" mb="xs">
        <Group gap="sm">
          {Logo && (
            <div style={{ width: 28, height: 28 }}>
              <Logo />
            </div>
          )}
          <Text fw={600} size="sm" lineClamp={1}>
            {agent.displayName}
          </Text>
        </Group>
        <Badge
          color={TIER_COLORS[agent.tierGate] || 'gray'}
          variant="light"
          size="sm"
        >
          {agent.tierGate}
        </Badge>
      </Group>

      <Text size="xs" c="dimmed" lineClamp={2} mb="sm">
        {agent.description}
      </Text>

      <Group justify="space-between" align="center">
        <Group gap="xs">
          <Badge variant="outline" size="xs">
            {agent.category}
          </Badge>
          <Text size="xs" c="dimmed">
            {agent.skillCount} skill{agent.skillCount !== 1 ? 's' : ''}
          </Text>
        </Group>

        {agent.installed ? (
          <Button
            size="xs"
            variant="outline"
            color="red"
            onClick={() => onUninstall(agent.agentId)}
            loading={actionLoading}
          >
            Uninstall
          </Button>
        ) : (
          <Button
            size="xs"
            variant="filled"
            color={tokens.brand}
            onClick={() => onInstall(agent.agentId)}
            loading={actionLoading}
          >
            Install
          </Button>
        )}
      </Group>
    </Card>
  );
};
