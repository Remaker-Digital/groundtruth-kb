/**
 * EntitlementConfig — View and edit tier entitlement configuration.
 *
 * Lists all entitlement documents (tier configs, pricing, gates, etc.).
 * Edit with version history and diff view against frozen fallback.
 *
 * API: GET/PUT /api/superadmin/entitlements
 *      GET /api/superadmin/entitlements/diff
 *      GET /api/superadmin/entitlements/history
 *
 * WI-1424 / SPEC-1819
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useCallback, useEffect, useState } from 'react';
import {
  Badge,
  Button,
  Card,
  Code,
  Group,
  JsonInput,
  Loader,
  Modal,
  Stack,
  Table,
  Tabs,
  Text,
  TextInput,
  Title,
} from '@mantine/core';
import { useProviderContext } from '../layouts/ProviderLayout';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface EntitlementDocument {
  configType: string;
  configKey: string;
  value: Record<string, unknown>;
  version: number;
  updatedAt: string;
  updatedBy: string | null;
}

interface DiffEntry {
  configKey: string;
  hasLiveDoc: boolean;
  frozenKeys: string[];
  liveKeys: string[];
  differences: string[];
}

interface HistoryEntry {
  id: string;
  action: string;
  configKey: string;
  actor: string;
  timestamp: string;
  previousVersion: number;
  newVersion: number;
  changeReason: string;
  diffSummary: string[];
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export const EntitlementConfigPage: React.FC = () => {
  const { apiFetch, onNotify } = useProviderContext();
  const [documents, setDocuments] = useState<EntitlementDocument[]>([]);
  const [diffs, setDiffs] = useState<DiffEntry[]>([]);
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [editDoc, setEditDoc] = useState<EntitlementDocument | null>(null);
  const [editValue, setEditValue] = useState('');
  const [changeReason, setChangeReason] = useState('');
  const [saving, setSaving] = useState(false);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [docsRes, diffRes, histRes] = await Promise.all([
        apiFetch('/api/superadmin/entitlements'),
        apiFetch('/api/superadmin/entitlements/diff'),
        apiFetch('/api/superadmin/entitlements/history'),
      ]);
      if (docsRes.ok) {
        const data = await docsRes.json();
        setDocuments(data.documents || []);
      }
      if (diffRes.ok) {
        const data = await diffRes.json();
        setDiffs(data.entries || []);
      }
      if (histRes.ok) {
        const data = await histRes.json();
        setHistory(data.entries || []);
      }
    } catch {
      onNotify('Failed to load entitlement data', 'error');
    } finally {
      setLoading(false);
    }
  }, [apiFetch, onNotify]);

  useEffect(() => { loadData(); }, [loadData]);

  const handleEdit = useCallback((doc: EntitlementDocument) => {
    setEditDoc(doc);
    setEditValue(JSON.stringify(doc.value, null, 2));
    setChangeReason('');
  }, []);

  const handleSave = useCallback(async () => {
    if (!editDoc) return;
    setSaving(true);
    try {
      const parsed = JSON.parse(editValue);
      const res = await apiFetch(`/api/superadmin/entitlements/${editDoc.configKey}`, {
        method: 'PUT',
        body: JSON.stringify({ value: parsed, changeReason }),
      });
      if (res.ok) {
        onNotify(`Updated ${editDoc.configKey}`, 'success');
        setEditDoc(null);
        loadData();
      } else {
        const err = await res.json();
        onNotify(err.detail || 'Save failed', 'error');
      }
    } catch (e: any) {
      onNotify(e.message || 'Invalid JSON', 'error');
    } finally {
      setSaving(false);
    }
  }, [editDoc, editValue, changeReason, apiFetch, onNotify, loadData]);

  if (loading) return <Loader size="lg" />;

  return (
    <Stack gap="md">
      <Title order={2}>Entitlement Configuration</Title>
      <Text c="dimmed" size="sm">Manage tier configs, pricing, gates, and SLA targets (SPEC-1819)</Text>

      <Tabs defaultValue="documents">
        <Tabs.List>
          <Tabs.Tab value="documents">Documents ({documents.length})</Tabs.Tab>
          <Tabs.Tab value="drift">Drift Check ({diffs.filter(d => d.differences.length > 0).length})</Tabs.Tab>
          <Tabs.Tab value="history">History ({history.length})</Tabs.Tab>
        </Tabs.List>

        <Tabs.Panel value="documents" pt="md">
          <Table striped highlightOnHover>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Config Key</Table.Th>
                <Table.Th>Type</Table.Th>
                <Table.Th>Version</Table.Th>
                <Table.Th>Updated</Table.Th>
                <Table.Th>Actions</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {documents.map(doc => (
                <Table.Tr key={doc.configKey}>
                  <Table.Td><Code>{doc.configKey}</Code></Table.Td>
                  <Table.Td>{doc.configType}</Table.Td>
                  <Table.Td><Badge size="sm">v{doc.version}</Badge></Table.Td>
                  <Table.Td>{doc.updatedAt ? new Date(doc.updatedAt).toLocaleString() : '—'}</Table.Td>
                  <Table.Td>
                    <Button size="xs" variant="light" onClick={() => handleEdit(doc)}>Edit</Button>
                  </Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        </Tabs.Panel>

        <Tabs.Panel value="drift" pt="md">
          <Table striped>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Config Key</Table.Th>
                <Table.Th>Live Doc</Table.Th>
                <Table.Th>Differences</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {diffs.map(d => (
                <Table.Tr key={d.configKey}>
                  <Table.Td><Code>{d.configKey}</Code></Table.Td>
                  <Table.Td>
                    <Badge color={d.hasLiveDoc ? 'green' : 'red'} size="sm">
                      {d.hasLiveDoc ? 'Yes' : 'Missing'}
                    </Badge>
                  </Table.Td>
                  <Table.Td>
                    {d.differences.length === 0
                      ? <Text c="dimmed" size="sm">No drift</Text>
                      : d.differences.map((diff, i) => <Text key={i} size="sm">{diff}</Text>)}
                  </Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        </Tabs.Panel>

        <Tabs.Panel value="history" pt="md">
          <Table striped>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Time</Table.Th>
                <Table.Th>Key</Table.Th>
                <Table.Th>Version</Table.Th>
                <Table.Th>Actor</Table.Th>
                <Table.Th>Reason</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {history.map(h => (
                <Table.Tr key={h.id}>
                  <Table.Td>{new Date(h.timestamp).toLocaleString()}</Table.Td>
                  <Table.Td><Code>{h.configKey}</Code></Table.Td>
                  <Table.Td>v{h.previousVersion} → v{h.newVersion}</Table.Td>
                  <Table.Td>{h.actor}</Table.Td>
                  <Table.Td>{h.changeReason || '—'}</Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        </Tabs.Panel>
      </Tabs>

      {/* Edit Modal */}
      <Modal opened={!!editDoc} onClose={() => setEditDoc(null)} title={`Edit ${editDoc?.configKey}`} size="lg">
        <Stack gap="md">
          <JsonInput
            label="Configuration Value (JSON)"
            value={editValue}
            onChange={setEditValue}
            minRows={12}
            autosize
            formatOnBlur
            validationError="Invalid JSON"
          />
          <TextInput
            label="Change Reason"
            placeholder="Why are you making this change?"
            value={changeReason}
            onChange={e => setChangeReason(e.currentTarget.value)}
          />
          <Group justify="flex-end">
            <Button variant="default" onClick={() => setEditDoc(null)}>Cancel</Button>
            <Button onClick={handleSave} loading={saving}>Save</Button>
          </Group>
        </Stack>
      </Modal>
    </Stack>
  );
};
