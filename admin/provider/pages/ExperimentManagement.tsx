/**
 * ExperimentManagement — Cross-tenant A/B experiment management (SPEC-0621 / WI-1526).
 *
 * Superadmin view of all experiments across tenants. Shows status, metrics
 * summary, and lifecycle actions (submit, approve, conclude).
 *
 * API: GET  /api/superadmin/experiments
 *      POST /api/superadmin/experiments/{id}/{action}
 *      GET  /api/superadmin/experiments/{id}/kpis
 *
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useCallback, useEffect, useState } from 'react';
import {
  Badge,
  Button,
  Group,
  Loader,
  Stack,
  Table,
  Tabs,
  Text,
  Title,
  Card,
  SimpleGrid,
  Alert,
  Select,
} from '@mantine/core';
import { useProviderContext } from '../layouts/ProviderLayout';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface Experiment {
  experimentId: string;
  tenantId: string;
  name: string;
  description: string;
  hypothesis: string;
  status: string;
  controlRatio: number;
  treatmentRatio: number;
  audienceMode: string;
  startDate: string | null;
  endDate: string | null;
  createdAt: string;
  concludedAt: string | null;
  metricKeys: string[];
  aiRationale: string;
  conclusionRecommendation: string | null;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const STATUS_COLORS: Record<string, string> = {
  draft: 'gray',
  pending_review: 'yellow',
  active: 'green',
  pending_conclusion: 'orange',
  concluded_promote: 'teal',
  concluded_rollback: 'red',
};

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function ExperimentManagementPage() {
  const { apiFetch, onNotify } = useProviderContext();
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [loading, setLoading] = useState(false);
  const [statusFilter, setStatusFilter] = useState<string | null>(null);

  const fetchExperiments = useCallback(async () => {
    setLoading(true);
    try {
      const url = statusFilter
        ? `/api/superadmin/experiments?status=${statusFilter}`
        : '/api/superadmin/experiments';
      const res = await apiFetch(url);
      if (res.ok) {
        setExperiments(await res.json());
      }
    } catch (e) {
      console.error('Failed to fetch experiments', e);
    } finally {
      setLoading(false);
    }
  }, [apiFetch, statusFilter]);

  useEffect(() => {
    fetchExperiments();
  }, [fetchExperiments]);

  const performAction = async (expId: string, action: string, body?: object) => {
    try {
      const res = await apiFetch(`/api/superadmin/experiments/${expId}/${action}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body || {}),
      });
      if (res.ok) {
        onNotify?.(`${action} succeeded`, 'success');
        fetchExperiments();
      } else {
        const err = await res.json();
        onNotify?.(`Failed: ${err.detail}`, 'error');
      }
    } catch {
      onNotify?.(`${action} failed`, 'error');
    }
  };

  return (
    <Stack gap="lg">
      <Group justify="space-between">
        <Title order={2}>Experiment Management</Title>
        <Select
          placeholder="Filter by status"
          clearable
          data={[
            { value: 'draft', label: 'Draft' },
            { value: 'pending_review', label: 'Pending Review' },
            { value: 'active', label: 'Active' },
            { value: 'pending_conclusion', label: 'Pending Conclusion' },
            { value: 'concluded_promote', label: 'Promoted' },
            { value: 'concluded_rollback', label: 'Rolled Back' },
          ]}
          value={statusFilter}
          onChange={setStatusFilter}
          w={200}
        />
      </Group>

      {loading ? (
        <Loader />
      ) : (
        <Table striped highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Tenant</Table.Th>
              <Table.Th>Experiment</Table.Th>
              <Table.Th>Status</Table.Th>
              <Table.Th>Split</Table.Th>
              <Table.Th>Created</Table.Th>
              <Table.Th>Actions</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {experiments.map(exp => (
              <Table.Tr key={exp.experimentId}>
                <Table.Td>
                  <Text size="sm" c="dimmed">{exp.tenantId}</Text>
                </Table.Td>
                <Table.Td>
                  <Text fw={500}>{exp.name}</Text>
                  <Text size="xs" c="dimmed">{exp.hypothesis}</Text>
                </Table.Td>
                <Table.Td>
                  <Badge color={STATUS_COLORS[exp.status] || 'gray'} variant="light">
                    {exp.status.replace(/_/g, ' ')}
                  </Badge>
                </Table.Td>
                <Table.Td>
                  {Math.round(exp.controlRatio * 100)}/{Math.round(exp.treatmentRatio * 100)}
                </Table.Td>
                <Table.Td>
                  {exp.createdAt ? new Date(exp.createdAt).toLocaleDateString() : '—'}
                </Table.Td>
                <Table.Td>
                  <Group gap="xs">
                    {exp.status === 'draft' && (
                      <Button size="xs" variant="light" color="yellow"
                        onClick={() => performAction(exp.experimentId, 'submit')}>
                        Submit
                      </Button>
                    )}
                    {exp.status === 'pending_review' && (
                      <>
                        <Button size="xs" color="green"
                          onClick={() => performAction(exp.experimentId, 'approve')}>
                          Approve
                        </Button>
                        <Button size="xs" color="red" variant="outline"
                          onClick={() => performAction(exp.experimentId, 'reject')}>
                          Reject
                        </Button>
                      </>
                    )}
                    {exp.status === 'active' && (
                      <Button size="xs" variant="light" color="orange"
                        onClick={() => performAction(exp.experimentId, 'conclude')}>
                        Conclude
                      </Button>
                    )}
                    {exp.status === 'pending_conclusion' && (
                      <>
                        <Button size="xs" color="teal"
                          onClick={() => performAction(exp.experimentId, 'finalize', { action: 'promote' })}>
                          Promote
                        </Button>
                        <Button size="xs" color="red" variant="outline"
                          onClick={() => performAction(exp.experimentId, 'finalize', { action: 'rollback' })}>
                          Rollback
                        </Button>
                      </>
                    )}
                  </Group>
                </Table.Td>
              </Table.Tr>
            ))}
            {experiments.length === 0 && (
              <Table.Tr>
                <Table.Td colSpan={6}>
                  <Text ta="center" c="dimmed" py="lg">
                    {statusFilter ? 'No experiments match the selected filter.' : 'No experiments found.'}
                  </Text>
                </Table.Td>
              </Table.Tr>
            )}
          </Table.Tbody>
        </Table>
      )}
    </Stack>
  );
}
