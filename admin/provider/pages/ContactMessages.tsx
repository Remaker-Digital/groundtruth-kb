// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * ContactMessages — Provider Console page for contact message management.
 *
 * Displays persisted Contact Us form submissions from merchant admins.
 * Supports filtering by topic/status/tenant, status lifecycle management,
 * operator notes, and CSV export (SPEC-1589, SPEC-1590, SPEC-1592).
 *
 * API: GET    /api/superadmin/contact-messages
 *      GET    /api/superadmin/contact-messages/{id}
 *      PATCH  /api/superadmin/contact-messages/{id}
 *      GET    /api/superadmin/contact-messages/export
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useEffect, useState, useCallback } from 'react';
import {
  ActionIcon,
  Badge,
  Button,
  Group,
  Modal,
  Pagination,
  Paper,
  Select,
  Stack,
  Table,
  Text,
  Textarea,
  Title,
  Tooltip,
} from '@mantine/core';
import { useProviderContext } from '../layouts/ProviderLayout';
import { LoadingState } from '../../shared/LoadingState';
import { TenantName } from '../components/TenantName';
import { tokens } from '../../shared/theme/styles';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface ContactMessage {
  id: string;
  tenantId: string;
  topic: string;
  subject: string;
  message: string;
  memberEmail: string | null;
  memberRole: string | null;
  memberId: string | null;
  tier: string | null;
  status: string;
  notes: string;
  createdAt: string;
  updatedAt: string;
}

interface ContactMessageListResponse {
  messages: ContactMessage[];
  total: number;
  skip: number;
  limit: number;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const PAGE_SIZE = 25;

const STATUS_COLORS: Record<string, string> = {
  new: 'blue',
  read: 'yellow',
  resolved: 'green',
  archived: 'gray',
};

const TOPIC_LABELS: Record<string, string> = {
  support: 'Support',
  feature_request: 'Feature Request',
  billing: 'Billing',
  bug_report: 'Bug Report',
  general: 'General',
};

const TOPIC_COLORS: Record<string, string> = {
  support: 'orange',
  feature_request: 'violet',
  billing: 'cyan',
  bug_report: 'red',
  general: 'gray',
};

const STATUS_OPTIONS = [
  { value: '', label: 'All Statuses' },
  { value: 'new', label: 'New' },
  { value: 'read', label: 'Read' },
  { value: 'resolved', label: 'Resolved' },
  { value: 'archived', label: 'Archived' },
];

const TOPIC_OPTIONS = [
  { value: '', label: 'All Topics' },
  { value: 'support', label: 'Support' },
  { value: 'feature_request', label: 'Feature Request' },
  { value: 'billing', label: 'Billing' },
  { value: 'bug_report', label: 'Bug Report' },
  { value: 'general', label: 'General' },
];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatDate(iso: string): string {
  if (!iso) return '—';
  try {
    return new Date(iso).toLocaleString(undefined, {
      dateStyle: 'medium',
      timeStyle: 'short',
    });
  } catch {
    return iso;
  }
}

function truncate(text: string, maxLen: number): string {
  if (text.length <= maxLen) return text;
  return text.slice(0, maxLen) + '...';
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function ContactMessagesPage() {
  const { apiFetch, onNotify, getTenantDisplay } = useProviderContext();
  const [messages, setMessages] = useState<ContactMessage[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);

  // Filters
  const [topicFilter, setTopicFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  // Detail modal
  const [selected, setSelected] = useState<ContactMessage | null>(null);
  const [detailOpen, setDetailOpen] = useState(false);
  const [editStatus, setEditStatus] = useState('');
  const [editNotes, setEditNotes] = useState('');
  const [saving, setSaving] = useState(false);

  // ── Fetch messages ─────────────────────────────────────────
  const fetchMessages = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      params.set('skip', String((page - 1) * PAGE_SIZE));
      params.set('limit', String(PAGE_SIZE));
      if (topicFilter) params.set('topic', topicFilter);
      if (statusFilter) params.set('status', statusFilter);

      const res = await apiFetch(`/api/superadmin/contact-messages?${params}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data: ContactMessageListResponse = await res.json();
      setMessages(data.messages);
      setTotal(data.total);
    } catch (err) {
      onNotify(`Failed to load contact messages: ${err}`, 'error');
    } finally {
      setLoading(false);
    }
  }, [apiFetch, onNotify, page, topicFilter, statusFilter]);

  useEffect(() => {
    fetchMessages();
  }, [fetchMessages]);

  // ── Open detail modal ──────────────────────────────────────
  const openDetail = (msg: ContactMessage) => {
    setSelected(msg);
    setEditStatus(msg.status);
    setEditNotes(msg.notes);
    setDetailOpen(true);
  };

  // ── Save status/notes ──────────────────────────────────────
  const handleSave = async () => {
    if (!selected) return;
    setSaving(true);
    try {
      const body: Record<string, string> = {};
      if (editStatus !== selected.status) body.status = editStatus;
      if (editNotes !== selected.notes) body.notes = editNotes;

      if (Object.keys(body).length === 0) {
        onNotify('No changes to save', 'info');
        setSaving(false);
        return;
      }

      const res = await apiFetch(`/api/superadmin/contact-messages/${selected.id}`, {
        method: 'PATCH',
        body: JSON.stringify(body),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      onNotify('Message updated', 'success');
      setDetailOpen(false);
      fetchMessages();
    } catch (err) {
      onNotify(`Failed to update: ${err}`, 'error');
    } finally {
      setSaving(false);
    }
  };

  // ── CSV export ─────────────────────────────────────────────
  const handleExport = async () => {
    try {
      const params = new URLSearchParams();
      if (topicFilter) params.set('topic', topicFilter);
      if (statusFilter) params.set('status', statusFilter);

      const res = await apiFetch(`/api/superadmin/contact-messages/export?${params}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'contact-messages.csv';
      a.click();
      URL.revokeObjectURL(url);
      onNotify('CSV exported', 'success');
    } catch (err) {
      onNotify(`Export failed: ${err}`, 'error');
    }
  };

  // ── Render ─────────────────────────────────────────────────
  const totalPages = Math.ceil(total / PAGE_SIZE);

  return (
    <Stack gap="md">
      <Group justify="space-between">
        <Title order={2}>Contact Messages</Title>
        <Button variant="light" size="xs" onClick={handleExport}>
          Export CSV
        </Button>
      </Group>

      {/* Filters */}
      <Paper p="sm" withBorder>
        <Group gap="sm">
          <Select
            size="xs"
            w={160}
            data={TOPIC_OPTIONS}
            value={topicFilter}
            onChange={(v) => { setTopicFilter(v || ''); setPage(1); }}
            placeholder="Topic"
          />
          <Select
            size="xs"
            w={160}
            data={STATUS_OPTIONS}
            value={statusFilter}
            onChange={(v) => { setStatusFilter(v || ''); setPage(1); }}
            placeholder="Status"
          />
          <Text size="xs" c="dimmed">{total} messages</Text>
        </Group>
      </Paper>

      {/* Table */}
      {loading ? (
        <LoadingState text="Loading contact messages..." />
      ) : messages.length === 0 ? (
        <Paper p="xl" withBorder>
          <Text ta="center" c="dimmed">No contact messages found.</Text>
        </Paper>
      ) : (
        <Paper withBorder>
          <Table striped highlightOnHover>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Date</Table.Th>
                <Table.Th>Tenant</Table.Th>
                <Table.Th>Topic</Table.Th>
                <Table.Th>Subject</Table.Th>
                <Table.Th>Status</Table.Th>
                <Table.Th>From</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {messages.map((msg) => (
                <Table.Tr
                  key={msg.id}
                  style={{ cursor: 'pointer' }}
                  onClick={() => openDetail(msg)}
                >
                  <Table.Td>
                    <Text size="xs">{formatDate(msg.createdAt)}</Text>
                  </Table.Td>
                  <Table.Td>
                    <TenantName tenantId={msg.tenantId} info={getTenantDisplay(msg.tenantId)} />
                  </Table.Td>
                  <Table.Td>
                    <Badge size="xs" color={TOPIC_COLORS[msg.topic] || 'gray'}>
                      {TOPIC_LABELS[msg.topic] || msg.topic}
                    </Badge>
                  </Table.Td>
                  <Table.Td>
                    <Text size="sm" lineClamp={1}>{msg.subject}</Text>
                  </Table.Td>
                  <Table.Td>
                    <Badge size="xs" color={STATUS_COLORS[msg.status] || 'gray'}>
                      {msg.status}
                    </Badge>
                  </Table.Td>
                  <Table.Td>
                    <Text size="xs">{msg.memberEmail || '—'}</Text>
                  </Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        </Paper>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <Group justify="center">
          <Pagination total={totalPages} value={page} onChange={setPage} size="sm" />
        </Group>
      )}

      {/* Detail Modal */}
      <Modal
        opened={detailOpen}
        onClose={() => setDetailOpen(false)}
        title="Contact Message Detail"
        size="lg"
      >
        {selected && (
          <Stack gap="md">
            {/* Header info */}
            <Group gap="sm">
              <Badge color={TOPIC_COLORS[selected.topic] || 'gray'}>
                {TOPIC_LABELS[selected.topic] || selected.topic}
              </Badge>
              <Badge color={STATUS_COLORS[selected.status] || 'gray'}>
                {selected.status}
              </Badge>
              <Text size="xs" c="dimmed">{formatDate(selected.createdAt)}</Text>
            </Group>

            {/* Tenant context */}
            <Paper p="sm" withBorder style={{ background: tokens.surface }}>
              <Stack gap={4}>
                <Group gap="xs">
                  <Text size="xs" fw={600} w={100}>Tenant</Text>
                  <TenantName tenantId={selected.tenantId} info={getTenantDisplay(selected.tenantId)} />
                </Group>
                <Group gap="xs">
                  <Text size="xs" fw={600} w={100}>Tier</Text>
                  <Text size="xs">{selected.tier || '—'}</Text>
                </Group>
                <Group gap="xs">
                  <Text size="xs" fw={600} w={100}>Email</Text>
                  <Text size="xs">{selected.memberEmail || '—'}</Text>
                </Group>
                <Group gap="xs">
                  <Text size="xs" fw={600} w={100}>Role</Text>
                  <Text size="xs">{selected.memberRole || '—'}</Text>
                </Group>
              </Stack>
            </Paper>

            {/* Subject and message */}
            <Stack gap={4}>
              <Text fw={600}>{selected.subject}</Text>
              <Paper p="sm" withBorder style={{ whiteSpace: 'pre-wrap', lineHeight: 1.6 }}>
                <Text size="sm">{selected.message}</Text>
              </Paper>
            </Stack>

            {/* Status update */}
            <Select
              label="Status"
              size="sm"
              data={[
                { value: 'new', label: 'New' },
                { value: 'read', label: 'Read' },
                { value: 'resolved', label: 'Resolved' },
                { value: 'archived', label: 'Archived' },
              ]}
              value={editStatus}
              onChange={(v) => setEditStatus(v || 'new')}
            />

            {/* Notes */}
            <Textarea
              label="Operator Notes"
              size="sm"
              minRows={3}
              maxRows={6}
              value={editNotes}
              onChange={(e) => setEditNotes(e.currentTarget.value)}
              placeholder="Add internal notes..."
            />

            {/* Actions */}
            <Group justify="flex-end">
              <Button variant="subtle" onClick={() => setDetailOpen(false)}>
                Cancel
              </Button>
              <Button loading={saving} onClick={handleSave}>
                Save Changes
              </Button>
            </Group>
          </Stack>
        )}
      </Modal>
    </Stack>
  );
}
