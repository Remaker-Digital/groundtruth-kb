// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * BlocklistConfig — Allow/block list management + value checking.
 *
 * 4 list types: ip, email_domain, tenant, user_agent.
 * Each list has entries with block/allow actions, prefix/suffix matching.
 * Includes a "Check Value" tool for testing entries against lists.
 *
 * API: GET  /api/superadmin/blocklists
 *      GET  /api/superadmin/blocklists/{list_type}
 *      PUT  /api/superadmin/blocklists/{list_type}
 *      POST /api/superadmin/blocklists/{list_type}/check
 *
 * WI-1425 / SPEC-1820
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useCallback, useEffect, useState } from 'react';
import {
  Badge,
  Button,
  Code,
  Group,
  Loader,
  Modal,
  Select,
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

interface BlocklistEntry {
  value: string;
  action: string;
  reason: string;
  addedBy: string;
  addedAt: string;
}

interface BlocklistResponse {
  listType: string;
  entries: BlocklistEntry[];
  defaultAction: string;
  version: number;
  updatedAt: string | null;
  updatedBy: string | null;
}

interface CheckResult {
  listType: string;
  value: string;
  action: string;
  matchedEntry: string | null;
  reason: string;
}

const LIST_TYPES = ['email_domain', 'ip', 'tenant', 'user_agent'];

const LIST_TYPE_LABELS: Record<string, string> = {
  ip: 'IP Addresses',
  email_domain: 'Email Domains',
  tenant: 'Tenants',
  user_agent: 'User Agents',
};

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export const BlocklistConfigPage: React.FC = () => {
  const { apiFetch, onNotify } = useProviderContext();
  const [lists, setLists] = useState<BlocklistResponse[]>([]);
  const [loading, setLoading] = useState(true);

  // Edit modal state
  const [editList, setEditList] = useState<BlocklistResponse | null>(null);
  const [editEntries, setEditEntries] = useState<BlocklistEntry[]>([]);
  const [editDefaultAction, setEditDefaultAction] = useState<string>('allow');
  const [newValue, setNewValue] = useState('');
  const [newAction, setNewAction] = useState<string | null>('block');
  const [newReason, setNewReason] = useState('');
  const [saving, setSaving] = useState(false);

  // Check modal state
  const [checkListType, setCheckListType] = useState<string | null>(null);
  const [checkValue, setCheckValue] = useState('');
  const [checkResult, setCheckResult] = useState<CheckResult | null>(null);
  const [checking, setChecking] = useState(false);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const res = await apiFetch('/api/superadmin/blocklists');
      if (res.ok) {
        const data = await res.json();
        setLists(data.lists || []);
      }
    } catch {
      onNotify('Failed to load blocklists', 'error');
    } finally {
      setLoading(false);
    }
  }, [apiFetch, onNotify]);

  useEffect(() => { loadData(); }, [loadData]);

  const handleEdit = useCallback((list: BlocklistResponse) => {
    setEditList(list);
    setEditEntries([...list.entries]);
    setEditDefaultAction(list.defaultAction);
    setNewValue('');
    setNewAction('block');
    setNewReason('');
  }, []);

  const handleAddEntry = useCallback(() => {
    if (!newValue.trim()) return;
    setEditEntries(prev => [...prev, {
      value: newValue.trim(),
      action: newAction || 'block',
      reason: newReason,
      addedBy: 'spa-console',
      addedAt: '',
    }]);
    setNewValue('');
    setNewReason('');
  }, [newValue, newAction, newReason]);

  const handleRemoveEntry = useCallback((index: number) => {
    setEditEntries(prev => prev.filter((_, i) => i !== index));
  }, []);

  const handleSave = useCallback(async () => {
    if (!editList) return;
    setSaving(true);
    try {
      const res = await apiFetch(`/api/superadmin/blocklists/${editList.listType}`, {
        method: 'PUT',
        body: JSON.stringify({
          entries: editEntries.map(e => ({
            value: e.value,
            action: e.action,
            reason: e.reason,
            addedBy: e.addedBy,
            addedAt: e.addedAt,
          })),
          defaultAction: editDefaultAction,
        }),
      });
      if (res.ok) {
        onNotify(`Updated ${editList.listType} blocklist`, 'success');
        setEditList(null);
        loadData();
      } else {
        const err = await res.json();
        onNotify(err.detail || 'Save failed', 'error');
      }
    } catch {
      onNotify('Network error saving blocklist', 'error');
    } finally {
      setSaving(false);
    }
  }, [editList, editEntries, editDefaultAction, apiFetch, onNotify, loadData]);

  const handleCheck = useCallback(async () => {
    if (!checkListType || !checkValue.trim()) return;
    setChecking(true);
    try {
      const res = await apiFetch(`/api/superadmin/blocklists/${checkListType}/check`, {
        method: 'POST',
        body: JSON.stringify({ value: checkValue.trim() }),
      });
      if (res.ok) {
        setCheckResult(await res.json());
      } else {
        onNotify('Check failed', 'error');
      }
    } catch {
      onNotify('Network error', 'error');
    } finally {
      setChecking(false);
    }
  }, [checkListType, checkValue, apiFetch, onNotify]);

  if (loading) return <Loader size="lg" />;

  return (
    <Stack gap="md">
      <Title order={2}>Allow/Block Lists</Title>
      <Text c="dimmed" size="sm">Manage IP, email domain, tenant, and user agent block/allow lists (SPEC-1820)</Text>

      <Tabs defaultValue="lists">
        <Tabs.List>
          <Tabs.Tab value="lists">Lists ({lists.length})</Tabs.Tab>
          <Tabs.Tab value="check">Check Value</Tabs.Tab>
        </Tabs.List>

        <Tabs.Panel value="lists" pt="md">
          <Table striped highlightOnHover>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>List Type</Table.Th>
                <Table.Th>Entries</Table.Th>
                <Table.Th>Default Action</Table.Th>
                <Table.Th>Version</Table.Th>
                <Table.Th>Updated</Table.Th>
                <Table.Th>Actions</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {lists.map(list => (
                <Table.Tr key={list.listType}>
                  <Table.Td><Code>{LIST_TYPE_LABELS[list.listType] || list.listType}</Code></Table.Td>
                  <Table.Td><Badge size="sm">{list.entries.length}</Badge></Table.Td>
                  <Table.Td>
                    <Badge color={list.defaultAction === 'block' ? 'red' : 'green'} size="sm">
                      {list.defaultAction}
                    </Badge>
                  </Table.Td>
                  <Table.Td>v{list.version}</Table.Td>
                  <Table.Td>{list.updatedAt ? new Date(list.updatedAt).toLocaleString() : '—'}</Table.Td>
                  <Table.Td>
                    <Button size="xs" variant="light" onClick={() => handleEdit(list)}>Edit</Button>
                  </Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        </Tabs.Panel>

        <Tabs.Panel value="check" pt="md">
          <Stack gap="md" maw={500}>
            <Select
              label="List Type"
              data={LIST_TYPES.map(t => ({ value: t, label: LIST_TYPE_LABELS[t] || t }))}
              value={checkListType}
              onChange={setCheckListType}
            />
            <TextInput
              label="Value to Check"
              placeholder="e.g. 192.168.1.1 or spam.example.com"
              value={checkValue}
              onChange={e => setCheckValue(e.currentTarget.value)}
            />
            <Button onClick={handleCheck} loading={checking} disabled={!checkListType || !checkValue.trim()}>
              Check
            </Button>
            {checkResult && (
              <Stack gap="xs">
                <Group>
                  <Text size="sm" fw={500}>Result:</Text>
                  <Badge color={checkResult.action === 'block' ? 'red' : 'green'} size="lg">
                    {checkResult.action.toUpperCase()}
                  </Badge>
                </Group>
                {checkResult.matchedEntry && (
                  <Text size="sm">Matched: <Code>{checkResult.matchedEntry}</Code></Text>
                )}
                {checkResult.reason && (
                  <Text size="sm" c="dimmed">Reason: {checkResult.reason}</Text>
                )}
              </Stack>
            )}
          </Stack>
        </Tabs.Panel>
      </Tabs>

      {/* Edit Modal */}
      <Modal
        opened={!!editList}
        onClose={() => setEditList(null)}
        title={`Edit ${LIST_TYPE_LABELS[editList?.listType || ''] || editList?.listType} List`}
        size="lg"
      >
        <Stack gap="md">
          <Select
            label="Default Action"
            data={[
              { value: 'allow', label: 'Allow (block listed entries)' },
              { value: 'block', label: 'Block (allow listed entries)' },
            ]}
            value={editDefaultAction}
            onChange={v => setEditDefaultAction(v || 'allow')}
          />

          <Text size="sm" fw={500}>Current Entries ({editEntries.length})</Text>
          {editEntries.length > 0 && (
            <Table striped>
              <Table.Thead>
                <Table.Tr>
                  <Table.Th>Value</Table.Th>
                  <Table.Th>Action</Table.Th>
                  <Table.Th>Reason</Table.Th>
                  <Table.Th />
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {editEntries.map((entry, i) => (
                  <Table.Tr key={i}>
                    <Table.Td><Code>{entry.value}</Code></Table.Td>
                    <Table.Td>
                      <Badge color={entry.action === 'block' ? 'red' : 'green'} size="sm">
                        {entry.action}
                      </Badge>
                    </Table.Td>
                    <Table.Td><Text size="xs" lineClamp={1}>{entry.reason || '—'}</Text></Table.Td>
                    <Table.Td>
                      <Button size="xs" variant="subtle" color="red" onClick={() => handleRemoveEntry(i)}>
                        Remove
                      </Button>
                    </Table.Td>
                  </Table.Tr>
                ))}
              </Table.Tbody>
            </Table>
          )}

          <Text size="sm" fw={500}>Add Entry</Text>
          <Group grow>
            <TextInput
              placeholder="Value (IP, domain, etc.)"
              value={newValue}
              onChange={e => setNewValue(e.currentTarget.value)}
            />
            <Select
              data={[{ value: 'block', label: 'Block' }, { value: 'allow', label: 'Allow' }]}
              value={newAction}
              onChange={setNewAction}
            />
          </Group>
          <Group>
            <TextInput
              placeholder="Reason (optional)"
              value={newReason}
              onChange={e => setNewReason(e.currentTarget.value)}
              style={{ flex: 1 }}
            />
            <Button variant="light" onClick={handleAddEntry} disabled={!newValue.trim()}>Add</Button>
          </Group>

          <Group justify="flex-end">
            <Button variant="default" onClick={() => setEditList(null)}>Cancel</Button>
            <Button onClick={handleSave} loading={saving}>Save</Button>
          </Group>
        </Stack>
      </Modal>
    </Stack>
  );
};
