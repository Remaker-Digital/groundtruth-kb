// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * SecretHealth — Aggregate secret health (SPEC-1843 zero-knowledge).
 *
 * Replaces the former per-tenant SecretPosture page.  Shows only aggregate
 * counts: tenants with API keys, widget keys, and tenants missing keys.
 * No per-tenant detail, no PII, no secret values.
 *
 * API: GET /api/superadmin/health/secrets
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useEffect, useState } from 'react';
import {
  Card,
  SimpleGrid,
  Stack,
  Text,
  Title,
} from '@mantine/core';
import { useProviderContext } from '../layouts/ProviderLayout';
import { LoadingState } from '../../shared/LoadingState';
import { HelpTooltip } from '../../shared/HelpTooltip';
import { tokens } from '../../shared/theme/styles';

// ---------------------------------------------------------------------------
// Types (matches SecretHealthResponse camelCase serialization)
// ---------------------------------------------------------------------------

interface SecretHealthResponse {
  tenantsWithApiKey: number;
  tenantsWithWidgetKey: number;
  tenantsMissingKeys: number;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function SecretPosturePage() {
  const { apiFetch, onNotify } = useProviderContext();
  const [data, setData] = useState<SecretHealthResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await apiFetch('/api/superadmin/health/secrets');
        if (res.ok && !cancelled) {
          setData(await res.json());
        } else if (!cancelled) {
          onNotify('Failed to load secret health', 'error');
        }
      } catch {
        if (!cancelled) onNotify('Network error loading secret health', 'error');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [apiFetch, onNotify]);

  if (loading) {
    return <LoadingState text="Loading secret health" />;
  }

  if (!data) {
    return (
      <Text c="dimmed" ta="center" mt="xl">
        Unable to load secret health data.
      </Text>
    );
  }

  return (
    <Stack gap="lg">
      <Title order={3} c={tokens.textPrimary}>
        Secret Health
      </Title>
      <HelpTooltip text="Aggregate key coverage across all tenants. Per-tenant secret detail has been removed for zero-knowledge compliance (SPEC-1843)." />

      <SimpleGrid cols={{ base: 1, sm: 3 }} spacing="md">
        <Card withBorder padding="lg" radius="md" bg={tokens.surface}>
          <Text c="dimmed" size="xs" tt="uppercase" fw={600}>
            Tenants w/ API Key
          </Text>
          <Text fw={700} size="xl" c={tokens.success} mt={4}>
            {data.tenantsWithApiKey}
          </Text>
        </Card>
        <Card withBorder padding="lg" radius="md" bg={tokens.surface}>
          <Text c="dimmed" size="xs" tt="uppercase" fw={600}>
            Tenants w/ Widget Key
          </Text>
          <Text fw={700} size="xl" c={tokens.chartBlue} mt={4}>
            {data.tenantsWithWidgetKey}
          </Text>
        </Card>
        <Card withBorder padding="lg" radius="md" bg={tokens.surface}>
          <Text c="dimmed" size="xs" tt="uppercase" fw={600}>
            Tenants Missing Keys
          </Text>
          <Text fw={700} size="xl" c={data.tenantsMissingKeys > 0 ? tokens.danger : tokens.textMuted} mt={4}>
            {data.tenantsMissingKeys}
          </Text>
        </Card>
      </SimpleGrid>
    </Stack>
  );
}
