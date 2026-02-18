/**
 * SecretPosture — Cross-tenant secret inventory and posture.
 *
 * Per-tenant secret counts, type breakdown, integration coverage
 * (Shopify/Stripe/API Key). Disabled secrets flagged red.
 *
 * API: GET /api/superadmin/secrets/posture
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useEffect, useState } from 'react';
import {
  Badge,
  Card,
  Group,
  Paper,
  SimpleGrid,
  Stack,
  Table,
  Text,
  Title,
} from '@mantine/core';
import { useProviderContext } from '../layouts/ProviderLayout';
import { LoadingState } from '../../shared/LoadingState';
import { HelpTooltip } from '../../shared/HelpTooltip';

// ---------------------------------------------------------------------------
// Types (matches SecretPostureResponse camelCase serialization)
// ---------------------------------------------------------------------------

interface TenantSecretInfo {
  tenantId: string;
  tier: string | null;
  secretCount: number;
  secretsByType: Record<string, number>;
  hasShopify: boolean;
  hasStripe: boolean;
  hasApiKey: boolean;
  oldestSecret: string | null;
  newestSecret: string | null;
  disabledSecrets: number;
}

interface SecretPostureResponse {
  totalTenants: number;
  totalSecrets: number;
  secretsByTypeGlobal: Record<string, number>;
  tenantsWithShopify: number;
  tenantsWithStripe: number;
  tenantsWithApiKey: number;
  tenants: TenantSecretInfo[];
  errors: Array<{ tenantId: string; message: string }>;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const TYPE_COLORS: Record<string, string> = {
  shopify_access_token: 'green',
  stripe_restricted_key: 'violet',
  api_key: 'blue',
  openai_api_key: 'cyan',
  webhook_secret: 'orange',
  totp_seed: 'pink',
};

function typeBadgeColor(type: string): string {
  return TYPE_COLORS[type] ?? 'gray';
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function SecretPosturePage() {
  const { apiFetch, onNotify } = useProviderContext();
  const [data, setData] = useState<SecretPostureResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await apiFetch('/api/superadmin/secrets/posture');
        if (res.ok && !cancelled) {
          setData(await res.json());
        } else if (!cancelled) {
          onNotify('Failed to load secret posture', 'error');
        }
      } catch {
        if (!cancelled) onNotify('Network error loading secret posture', 'error');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [apiFetch, onNotify]);

  if (loading) {
    return <LoadingState text="Loading secret posture" />;
  }

  if (!data) {
    return (
      <Text c="dimmed" ta="center" mt="xl">
        Unable to load secret posture data.
      </Text>
    );
  }

  return (
    <Stack gap="lg">
      <Title order={3} c="#F5F5F5">Secret Posture</Title><HelpTooltip text="Cross-tenant inventory of secrets stored in Azure Key Vault. Disabled secrets and missing integrations are flagged." />

      {/* Summary cards */}
      <SimpleGrid cols={{ base: 1, sm: 2, md: 4 }} spacing="md">
        <Card withBorder padding="lg" radius="md" bg="#1f1f1f">
          <Text c="dimmed" size="xs" tt="uppercase" fw={600}>Total Secrets</Text>
          <Text fw={700} size="xl" c="#F5F5F5" mt={4}>{data.totalSecrets}</Text>
        </Card>
        <Card withBorder padding="lg" radius="md" bg="#1f1f1f">
          <Text c="dimmed" size="xs" tt="uppercase" fw={600}>Tenants w/ Shopify</Text>
          <Text fw={700} size="xl" c="#0D7C3E" mt={4}>{data.tenantsWithShopify}</Text>
        </Card>
        <Card withBorder padding="lg" radius="md" bg="#1f1f1f">
          <Text c="dimmed" size="xs" tt="uppercase" fw={600}>Tenants w/ Stripe</Text>
          <Text fw={700} size="xl" c="#7C3AED" mt={4}>{data.tenantsWithStripe}</Text>
        </Card>
        <Card withBorder padding="lg" radius="md" bg="#1f1f1f">
          <Text c="dimmed" size="xs" tt="uppercase" fw={600}>Tenants w/ API Key</Text>
          <Text fw={700} size="xl" c="#1E88E5" mt={4}>{data.tenantsWithApiKey}</Text>
        </Card>
      </SimpleGrid>

      {/* Global type breakdown */}
      {Object.keys(data.secretsByTypeGlobal).length > 0 && (
        <Paper withBorder radius="md" bg="#1f1f1f" p="md">
          <Text size="sm" fw={500} c="#E0E0E0" mb="sm">Secret Types (Global)</Text>
          <Group gap="sm">
            {Object.entries(data.secretsByTypeGlobal).map(([type, count]) => (
              <Badge
                key={type}
                variant="light"
                color={typeBadgeColor(type)}
                size="lg"
              >
                {type.replace(/_/g, ' ')}: {count}
              </Badge>
            ))}
          </Group>
        </Paper>
      )}

      {/* Per-tenant table */}
      <Paper withBorder radius="md" bg="#1f1f1f" style={{ overflow: 'auto' }}>
        <Table striped highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Tenant ID</Table.Th>
              <Table.Th>Tier</Table.Th>
              <Table.Th>Secrets</Table.Th>
              <Table.Th>Shopify</Table.Th>
              <Table.Th>Stripe</Table.Th>
              <Table.Th>API Key</Table.Th>
              <Table.Th>Disabled<HelpTooltip text="Secrets that have been revoked or expired. These should be rotated or removed." /></Table.Th>
              <Table.Th>Oldest</Table.Th>
              <Table.Th>Newest</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {data.tenants.length === 0 ? (
              <Table.Tr>
                <Table.Td colSpan={9}>
                  <Text c="dimmed" ta="center" py="md">No secret data available</Text>
                </Table.Td>
              </Table.Tr>
            ) : (
              data.tenants.map((t) => (
                <Table.Tr key={t.tenantId}>
                  <Table.Td>
                    <Text size="xs" ff="monospace" c="#E0E0E0">{t.tenantId}</Text>
                  </Table.Td>
                  <Table.Td>
                    <Text size="xs" c="#A0A0A0">{t.tier ?? '\u2014'}</Text>
                  </Table.Td>
                  <Table.Td>
                    <Text size="xs" fw={500} c="#E0E0E0">{t.secretCount}</Text>
                  </Table.Td>
                  <Table.Td>
                    <Text size="xs" c={t.hasShopify ? '#0D7C3E' : '#5C5C5C'}>
                      {t.hasShopify ? '\u2713' : '\u2014'}
                    </Text>
                  </Table.Td>
                  <Table.Td>
                    <Text size="xs" c={t.hasStripe ? '#7C3AED' : '#5C5C5C'}>
                      {t.hasStripe ? '\u2713' : '\u2014'}
                    </Text>
                  </Table.Td>
                  <Table.Td>
                    <Text size="xs" c={t.hasApiKey ? '#1E88E5' : '#5C5C5C'}>
                      {t.hasApiKey ? '\u2713' : '\u2014'}
                    </Text>
                  </Table.Td>
                  <Table.Td>
                    <Text size="xs" fw={500} c={t.disabledSecrets > 0 ? '#D32F2F' : '#A0A0A0'}>
                      {t.disabledSecrets}
                    </Text>
                  </Table.Td>
                  <Table.Td>
                    <Text size="xs" c="dimmed">
                      {t.oldestSecret ? new Date(t.oldestSecret).toLocaleDateString() : '\u2014'}
                    </Text>
                  </Table.Td>
                  <Table.Td>
                    <Text size="xs" c="dimmed">
                      {t.newestSecret ? new Date(t.newestSecret).toLocaleDateString() : '\u2014'}
                    </Text>
                  </Table.Td>
                </Table.Tr>
              ))
            )}
          </Table.Tbody>
        </Table>
      </Paper>

      {/* Errors section */}
      {data.errors.length > 0 && (
        <Paper withBorder radius="md" bg="#1f1f1f" p="md">
          <Group gap="xs" mb="sm">
            <Badge variant="filled" color="red" size="sm">
              {data.errors.length} Error{data.errors.length !== 1 ? 's' : ''}
            </Badge>
          </Group>
          <Stack gap="xs">
            {data.errors.map((err, i) => (
              <Group key={i} gap="xs">
                <Text size="xs" ff="monospace" c="#E5A100">{err.tenantId}</Text>
                <Text size="xs" c="#A0A0A0">{err.message}</Text>
              </Group>
            ))}
          </Stack>
        </Paper>
      )}
    </Stack>
  );
}
