// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * StatusPage — Incident management and public status page.
 *
 * Create, update, and resolve incidents. Manage affected services.
 * Timeline view of incident updates. Resolved incidents collapsible.
 *
 * API: GET/POST /api/superadmin/incidents
 *      POST .../update, POST .../resolve
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useCallback, useEffect, useState } from 'react';
import {
  ActionIcon,
  Badge,
  Button,
  Card,
  Collapse,
  Group,
  Modal,
  MultiSelect,
  Select,
  Stack,
  Text,
  Textarea,
  TextInput,
  Timeline,
  Title,
} from '@mantine/core';
import { useProviderContext } from '../layouts/ProviderLayout';
import { LoadingState } from '../../shared/LoadingState';
import { HelpTooltip } from '../../shared/HelpTooltip';
import { tokens, modalStyles, modalInputStyles } from '../../shared/theme/styles';

// ---------------------------------------------------------------------------
// Types (matches camelCase serialization)
// ---------------------------------------------------------------------------

interface IncidentUpdate {
  timestamp: string;
  status: string;
  message: string;
  author: string;
}

interface Incident {
  incidentId: string;
  title: string;
  description: string;
  status: string;
  severity: string;
  affectedServices: string[];
  updates: IncidentUpdate[];
  createdAt: string;
  updatedAt: string;
  resolvedAt: string | null;
  createdBy: string;
}

interface IncidentListResponse {
  incidents: Incident[];
  total: number;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const SEVERITY_COLORS: Record<string, string> = {
  critical: 'red',
  major: 'orange',
  minor: 'yellow',
};

const STATUS_COLORS: Record<string, string> = {
  investigating: 'red',
  identified: 'orange',
  monitoring: 'blue',
  resolved: 'green',
  scheduled: 'grape',
};

const SERVICES = [
  'API', 'Widget', 'NATS', 'Key Vault', 'MCP', 'Admin Console', 'Cosmos DB',
];

const STATUS_OPTIONS = [
  { value: 'investigating', label: 'Investigating' },
  { value: 'identified', label: 'Identified' },
  { value: 'monitoring', label: 'Monitoring' },
  { value: 'resolved', label: 'Resolved' },
];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatDate(iso: string): string {
  if (!iso) return '\u2014';
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function StatusPageManagement() {
  const { apiFetch, onNotify } = useProviderContext();
  const [data, setData] = useState<IncidentListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [showResolved, setShowResolved] = useState(false);

  // Create modal
  const [createOpen, setCreateOpen] = useState(false);
  const [createTitle, setCreateTitle] = useState('');
  const [createDesc, setCreateDesc] = useState('');
  const [createSeverity, setCreateSeverity] = useState<string | null>('minor');
  const [createServices, setCreateServices] = useState<string[]>([]);
  const [creating, setCreating] = useState(false);

  // Update modal
  const [updateOpen, setUpdateOpen] = useState(false);
  const [updateIncidentId, setUpdateIncidentId] = useState('');
  const [updateStatus, setUpdateStatus] = useState<string | null>('monitoring');
  const [updateMessage, setUpdateMessage] = useState('');
  const [updating, setUpdating] = useState(false);

  const fetchData = useCallback(async () => {
    try {
      const res = await apiFetch('/api/superadmin/incidents?limit=100');
      if (res.ok) {
        setData(await res.json());
      } else {
        onNotify('Failed to load incidents', 'error');
      }
    } catch {
      onNotify('Network error loading incidents', 'error');
    } finally {
      setLoading(false);
    }
  }, [apiFetch, onNotify]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleCreate = async () => {
    setCreating(true);
    try {
      const res = await apiFetch('/api/superadmin/incidents', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: createTitle,
          description: createDesc,
          severity: createSeverity || 'minor',
          affectedServices: createServices,
        }),
      });
      if (res.ok) {
        onNotify('Incident created', 'success');
        setCreateOpen(false);
        setCreateTitle('');
        setCreateDesc('');
        setCreateSeverity('minor');
        setCreateServices([]);
        await fetchData();
      } else {
        onNotify('Failed to create incident', 'error');
      }
    } catch {
      onNotify('Network error', 'error');
    } finally {
      setCreating(false);
    }
  };

  const handleUpdate = async () => {
    setUpdating(true);
    try {
      const res = await apiFetch(`/api/superadmin/incidents/${updateIncidentId}/update`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          status: updateStatus || 'monitoring',
          message: updateMessage,
        }),
      });
      if (res.ok) {
        onNotify('Incident updated', 'success');
        setUpdateOpen(false);
        setUpdateMessage('');
        await fetchData();
      } else {
        onNotify('Failed to update incident', 'error');
      }
    } catch {
      onNotify('Network error', 'error');
    } finally {
      setUpdating(false);
    }
  };

  const handleResolve = async (incidentId: string) => {
    try {
      const res = await apiFetch(`/api/superadmin/incidents/${incidentId}/resolve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: 'Incident resolved' }),
      });
      if (res.ok) {
        onNotify('Incident resolved', 'success');
        await fetchData();
      } else {
        onNotify('Failed to resolve incident', 'error');
      }
    } catch {
      onNotify('Network error', 'error');
    }
  };

  if (loading) {
    return <LoadingState text="Loading incidents" />;
  }

  const activeIncidents = (data?.incidents ?? []).filter((i) => i.status !== 'resolved');
  const resolvedIncidents = (data?.incidents ?? []).filter((i) => i.status === 'resolved');

  return (
    <Stack gap="lg">
      <Group justify="space-between" align="baseline">
        <Title order={3} c={tokens.textPrimary}>Status Page</Title><HelpTooltip text="Manage incidents visible on the public status page at /api/status. Active incidents affect the overall system status." />
        <Button color="action" size="sm" onClick={() => setCreateOpen(true)}>
          Create Incident
        </Button>
      </Group>

      {/* Active incidents */}
      {activeIncidents.length === 0 ? (
        <Card withBorder padding="lg" radius="md" bg={tokens.surface}>
          <Group gap="sm">
            <Badge variant="filled" color="green" size="lg">All Systems Operational</Badge><HelpTooltip text="Status is operational when there are no active (non-resolved) incidents." />
          </Group>
          <Text c="dimmed" size="sm" mt="sm">No active incidents.</Text>
        </Card>
      ) : (
        activeIncidents.map((inc) => (
          <Card key={inc.incidentId} withBorder padding="lg" radius="md" bg={tokens.surface}>
            <Group justify="space-between" mb="sm">
              <Group gap="sm">
                <Text fw={600} size="md" c={tokens.textPrimary}>{inc.title}</Text>
                <Badge variant="light" color={SEVERITY_COLORS[inc.severity] ?? 'gray'} size="sm">
                  {inc.severity}
                </Badge>
                <Badge variant="light" color={STATUS_COLORS[inc.status] ?? 'gray'} size="sm">
                  {inc.status}
                </Badge>
              </Group>
              <Group gap="xs">
                <Button
                  variant="light"
                  color="blue"
                  size="xs"
                  onClick={() => {
                    setUpdateIncidentId(inc.incidentId);
                    setUpdateStatus(inc.status);
                    setUpdateOpen(true);
                  }}
                >
                  Add Update
                </Button>
                <Button
                  variant="light"
                  color="green"
                  size="xs"
                  onClick={() => handleResolve(inc.incidentId)}
                >
                  Resolve
                </Button>
              </Group>
            </Group>

            {inc.description && (
              <Text size="sm" c={tokens.textMuted} mb="sm">{inc.description}</Text>
            )}

            {inc.affectedServices.length > 0 && (
              <Group gap="xs" mb="sm">
                <Text size="xs" c="dimmed">Affected:</Text>
                {inc.affectedServices.map((svc) => (
                  <Badge key={svc} variant="outline" color="red" size="xs">{svc}</Badge>
                ))}
              </Group>
            )}

            {inc.updates.length > 0 && (
              <Timeline active={inc.updates.length - 1} bulletSize={16} lineWidth={2} mt="sm">
                {inc.updates.map((upd, i) => (
                  <Timeline.Item
                    key={i}
                    title={
                      <Group gap="xs">
                        <Badge
                          variant="light"
                          color={STATUS_COLORS[upd.status] ?? 'gray'}
                          size="xs"
                        >
                          {upd.status}
                        </Badge>
                        <Text size="xs" c="dimmed">{formatDate(upd.timestamp)}</Text>
                      </Group>
                    }
                  >
                    <Text size="sm" c={tokens.textSecondary}>{upd.message}</Text>
                    <Text size="xs" c="dimmed">by {upd.author}</Text>
                  </Timeline.Item>
                ))}
              </Timeline>
            )}

            <Text size="xs" c="dimmed" mt="sm">
              Created {formatDate(inc.createdAt)} by {inc.createdBy}
            </Text>
          </Card>
        ))
      )}

      {/* Resolved incidents (collapsible) */}
      {resolvedIncidents.length > 0 && (
        <>
          <Button
            variant="subtle"
            color="gray"
            size="sm"
            onClick={() => setShowResolved(!showResolved)}
          >
            {showResolved ? 'Hide' : 'Show'} {resolvedIncidents.length} Resolved Incident{resolvedIncidents.length !== 1 ? 's' : ''}
          </Button>
          <Collapse in={showResolved}>
            <Stack gap="md">
              {resolvedIncidents.map((inc) => (
                <Card key={inc.incidentId} withBorder padding="md" radius="md" bg={tokens.page}>
                  <Group justify="space-between" mb="xs">
                    <Group gap="sm">
                      <Text fw={500} size="sm" c={tokens.textMuted}>{inc.title}</Text>
                      <Badge variant="light" color="green" size="xs">resolved</Badge>
                      <Badge variant="light" color={SEVERITY_COLORS[inc.severity] ?? 'gray'} size="xs">
                        {inc.severity}
                      </Badge>
                    </Group>
                    <Text size="xs" c="dimmed">Resolved {formatDate(inc.resolvedAt ?? '')}</Text>
                  </Group>
                  {inc.updates.length > 0 && (
                    <Text size="xs" c="dimmed">
                      {inc.updates.length} update{inc.updates.length !== 1 ? 's' : ''} — last: {inc.updates[inc.updates.length - 1].message}
                    </Text>
                  )}
                </Card>
              ))}
            </Stack>
          </Collapse>
        </>
      )}

      {/* Create Incident Modal */}
      <Modal
        opened={createOpen}
        onClose={() => setCreateOpen(false)}
        title="Create Incident"
        size="md"
        styles={modalStyles}
      >
        <Stack gap="md">
          <TextInput
            label="Title"
            placeholder="Brief incident title"
            value={createTitle}
            onChange={(e) => setCreateTitle(e.currentTarget.value)}
            required
            styles={modalInputStyles}
          />
          <Textarea
            label="Description"
            placeholder="Detailed description (optional)"
            value={createDesc}
            onChange={(e) => setCreateDesc(e.currentTarget.value)}
            minRows={3}
            styles={modalInputStyles}
          />
          <Select
            label="Severity"
            data={[
              { value: 'minor', label: 'Minor' },
              { value: 'major', label: 'Major' },
              { value: 'critical', label: 'Critical' },
            ]}
            value={createSeverity}
            onChange={setCreateSeverity}
            styles={modalInputStyles}
          />
          <MultiSelect
            label="Affected Services"
            data={SERVICES}
            value={createServices}
            onChange={setCreateServices}
            placeholder="Select affected services"
            styles={modalInputStyles}
          />
          <Group justify="flex-end">
            <Button variant="subtle" onClick={() => setCreateOpen(false)}>Cancel</Button>
            <Button
              color="action"
              loading={creating}
              disabled={!createTitle.trim()}
              onClick={handleCreate}
            >
              Create Incident
            </Button>
          </Group>
        </Stack>
      </Modal>

      {/* Add Update Modal */}
      <Modal
        opened={updateOpen}
        onClose={() => setUpdateOpen(false)}
        title="Add Incident Update"
        size="md"
        styles={modalStyles}
      >
        <Stack gap="md">
          <Select
            label="Status"
            data={STATUS_OPTIONS}
            value={updateStatus}
            onChange={setUpdateStatus}
            styles={modalInputStyles}
          />
          <Textarea
            label="Update Message"
            placeholder="Describe what changed"
            value={updateMessage}
            onChange={(e) => setUpdateMessage(e.currentTarget.value)}
            minRows={3}
            required
            styles={modalInputStyles}
          />
          <Group justify="flex-end">
            <Button variant="subtle" onClick={() => setUpdateOpen(false)}>Cancel</Button>
            <Button
              color="blue"
              loading={updating}
              disabled={!updateMessage.trim()}
              onClick={handleUpdate}
            >
              Post Update
            </Button>
          </Group>
        </Stack>
      </Modal>
    </Stack>
  );
}
