/**
 * Service Messages — compose and send bulk notifications to tenant superadmins.
 *
 * Provides a UI for the service provider to compose service messages,
 * filter recipients by tenant status and tier, preview the recipient list,
 * and send via BCC email.
 *
 * Specifications: SPEC-1646, SPEC-1647, SPEC-1648.
 * Work items: WI-0999.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { useState, useCallback } from 'react';
import {
  Box,
  Button,
  Group,
  Modal,
  MultiSelect,
  Paper,
  Stack,
  Table,
  Text,
  TextInput,
  Textarea,
  Title,
  Badge,
  Alert,
  Pagination,
} from '@mantine/core';
import { useProviderContext } from '../layouts/ProviderLayout';
import { tokens } from '../../shared/theme/styles';

/* ------------------------------------------------------------------ */
/* Types                                                               */
/* ------------------------------------------------------------------ */

interface Recipient {
  tenantId: string;
  email: string;
  tier: string | null;
  status: string | null;
}

interface SendResult {
  totalRecipients: number;
  sentCount: number;
  failedCount: number;
  errors: string[];
  success: boolean;
}

/* ------------------------------------------------------------------ */
/* Filter options                                                      */
/* ------------------------------------------------------------------ */

const STATUS_OPTIONS = [
  { value: 'active', label: 'Active' },
  { value: 'initialized', label: 'Initialized' },
  { value: 'trial', label: 'Trial' },
  { value: 'deactivated', label: 'Deactivated' },
  { value: 'suspended', label: 'Suspended' },
];

const TIER_OPTIONS = [
  { value: 'starter', label: 'Starter' },
  { value: 'professional', label: 'Professional' },
  { value: 'enterprise', label: 'Enterprise' },
  { value: 'trial', label: 'Trial' },
];

/* ------------------------------------------------------------------ */
/* Component                                                           */
/* ------------------------------------------------------------------ */

export function ServiceMessagesPage() {
  const { apiFetch, onNotify } = useProviderContext();

  // Form state
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [filterStatus, setFilterStatus] = useState<string[]>([]);
  const [filterTier, setFilterTier] = useState<string[]>([]);

  // Preview state
  const [recipients, setRecipients] = useState<Recipient[]>([]);
  const [previewLoaded, setPreviewLoaded] = useState(false);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [previewPage, setPreviewPage] = useState(1);

  // Send state
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [sending, setSending] = useState(false);
  const [sendResult, setSendResult] = useState<SendResult | null>(null);

  /* ---- Preview recipients ---- */
  const handlePreview = useCallback(async () => {
    setPreviewLoading(true);
    setPreviewLoaded(false);
    try {
      const params = new URLSearchParams();
      filterStatus.forEach(s => params.append('filter_status', s));
      filterTier.forEach(t => params.append('filter_tier', t));
      const res = await apiFetch(
        `/api/superadmin/service-messages/preview?${params.toString()}`,
        { method: 'POST' },
      );
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail || `HTTP ${res.status}`);
      }
      const data = await res.json();
      setRecipients(data.recipients || []);
      setPreviewLoaded(true);
      setPreviewPage(1);
    } catch (e: any) {
      onNotify(e.message || 'Failed to load recipients', 'error');
    } finally {
      setPreviewLoading(false);
    }
  }, [apiFetch, onNotify, filterStatus, filterTier]);

  /* ---- Send message ---- */
  const handleSend = useCallback(async () => {
    if (!subject.trim() || !body.trim()) {
      onNotify('Subject and body are required', 'warning');
      return;
    }
    setSending(true);
    try {
      const payload = {
        subject: subject.trim(),
        body: body.trim(),
        filterStatus: filterStatus.length > 0 ? filterStatus : null,
        filterTier: filterTier.length > 0 ? filterTier : null,
      };
      const res = await apiFetch('/api/superadmin/service-messages/send', {
        method: 'POST',
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail || `HTTP ${res.status}`);
      }
      const result: SendResult = await res.json();
      setSendResult(result);
      if (result.success) {
        onNotify(
          `Service message sent to ${result.sentCount} recipient(s)`,
          'success',
        );
      } else {
        onNotify(
          `Sent ${result.sentCount}/${result.totalRecipients} — ${result.failedCount} failed`,
          'warning',
        );
      }
    } catch (e: any) {
      onNotify(e.message || 'Failed to send service message', 'error');
    } finally {
      setSending(false);
      setConfirmOpen(false);
    }
  }, [apiFetch, onNotify, subject, body, filterStatus, filterTier]);

  /* ---- Reset form ---- */
  const handleReset = useCallback(() => {
    setSubject('');
    setBody('');
    setFilterStatus([]);
    setFilterTier([]);
    setRecipients([]);
    setPreviewLoaded(false);
    setSendResult(null);
  }, []);

  /* ---- Pagination ---- */
  const pageSize = 20;
  const totalPages = Math.ceil(recipients.length / pageSize);
  const pagedRecipients = recipients.slice(
    (previewPage - 1) * pageSize,
    previewPage * pageSize,
  );

  /* ---- Unique email count (de-duplicated) ---- */
  const uniqueEmails = new Set(recipients.map(r => r.email));

  return (
    <Box>
      <Title order={2} mb="lg" style={{ color: tokens.textPrimary }}>
        Service Messages
      </Title>
      <Text size="sm" mb="xl" style={{ color: tokens.textSecondary }}>
        Send bulk notifications to tenant superadmins. Recipients are BCC — email
        addresses are not disclosed to each other.
      </Text>

      {/* ---- Send result banner ---- */}
      {sendResult && (
        <Alert
          color={sendResult.success ? 'green' : 'yellow'}
          mb="lg"
          withCloseButton
          onClose={() => setSendResult(null)}
          title={sendResult.success ? 'Message sent' : 'Partial delivery'}
        >
          Sent to {sendResult.sentCount} of {sendResult.totalRecipients} recipient(s).
          {sendResult.errors.length > 0 && (
            <Text size="xs" mt="xs" style={{ color: tokens.textSecondary }}>
              {sendResult.errors.join('; ')}
            </Text>
          )}
        </Alert>
      )}

      {/* ---- Compose form ---- */}
      <Paper p="lg" mb="lg" style={{ background: tokens.surface }}>
        <Title order={4} mb="md" style={{ color: tokens.textPrimary }}>
          Compose
        </Title>
        <Stack gap="md">
          <TextInput
            label="Subject"
            placeholder="e.g. Platform update — v1.66.0 released"
            value={subject}
            onChange={e => setSubject(e.currentTarget.value)}
            maxLength={200}
            required
          />
          <Textarea
            label="Message body (HTML supported)"
            placeholder="Write the service message content..."
            value={body}
            onChange={e => setBody(e.currentTarget.value)}
            minRows={6}
            maxRows={12}
            maxLength={10000}
            required
          />
        </Stack>
      </Paper>

      {/* ---- Recipient filters ---- */}
      <Paper p="lg" mb="lg" style={{ background: tokens.surface }}>
        <Title order={4} mb="md" style={{ color: tokens.textPrimary }}>
          Recipient Filters
        </Title>
        <Text size="sm" mb="md" style={{ color: tokens.textSecondary }}>
          Leave empty to send to all tenants with a registered superadmin email.
        </Text>
        <Group grow mb="md">
          <MultiSelect
            label="Tenant status"
            placeholder="All statuses"
            data={STATUS_OPTIONS}
            value={filterStatus}
            onChange={setFilterStatus}
            clearable
          />
          <MultiSelect
            label="Subscription tier"
            placeholder="All tiers"
            data={TIER_OPTIONS}
            value={filterTier}
            onChange={setFilterTier}
            clearable
          />
        </Group>
        <Group>
          <Button
            variant="light"
            onClick={handlePreview}
            loading={previewLoading}
          >
            Preview Recipients
          </Button>
          {previewLoaded && (
            <Text size="sm" style={{ color: tokens.textSecondary }}>
              {recipients.length} tenant(s) — {uniqueEmails.size} unique email(s)
            </Text>
          )}
        </Group>
      </Paper>

      {/* ---- Recipient preview table ---- */}
      {previewLoaded && recipients.length > 0 && (
        <Paper p="lg" mb="lg" style={{ background: tokens.surface }}>
          <Title order={4} mb="md" style={{ color: tokens.textPrimary }}>
            Recipients ({recipients.length})
          </Title>
          <Table striped highlightOnHover>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Tenant ID</Table.Th>
                <Table.Th>Email</Table.Th>
                <Table.Th>Tier</Table.Th>
                <Table.Th>Status</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {pagedRecipients.map((r, i) => (
                <Table.Tr key={`${r.tenantId}-${i}`}>
                  <Table.Td>
                    <Text size="xs" ff="monospace">
                      {r.tenantId.length > 20
                        ? `${r.tenantId.slice(0, 20)}...`
                        : r.tenantId}
                    </Text>
                  </Table.Td>
                  <Table.Td>{r.email}</Table.Td>
                  <Table.Td>
                    {r.tier && (
                      <Badge size="sm" variant="light" color="blue">
                        {r.tier}
                      </Badge>
                    )}
                  </Table.Td>
                  <Table.Td>
                    {r.status && (
                      <Badge
                        size="sm"
                        variant="light"
                        color={r.status === 'active' ? 'green' : 'gray'}
                      >
                        {r.status}
                      </Badge>
                    )}
                  </Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
          {totalPages > 1 && (
            <Group justify="center" mt="md">
              <Pagination
                total={totalPages}
                value={previewPage}
                onChange={setPreviewPage}
                size="sm"
              />
            </Group>
          )}
        </Paper>
      )}

      {previewLoaded && recipients.length === 0 && (
        <Alert color="yellow" mb="lg">
          No tenants match the selected filters or have a registered email address.
        </Alert>
      )}

      {/* ---- Action buttons ---- */}
      <Group>
        <Button
          onClick={() => setConfirmOpen(true)}
          disabled={
            !subject.trim() || !body.trim() || !previewLoaded || recipients.length === 0
          }
          color="red"
        >
          Send Service Message
        </Button>
        <Button variant="subtle" onClick={handleReset}>
          Reset
        </Button>
      </Group>

      {/* ---- Confirmation modal ---- */}
      <Modal
        opened={confirmOpen}
        onClose={() => setConfirmOpen(false)}
        title="Confirm Service Message"
        centered
      >
        <Stack gap="md">
          <Text size="sm">
            You are about to send a service message to{' '}
            <strong>{uniqueEmails.size}</strong> unique recipient(s) across{' '}
            <strong>{recipients.length}</strong> tenant(s).
          </Text>
          <Paper p="sm" style={{ background: tokens.page }}>
            <Text size="sm" fw={600}>Subject:</Text>
            <Text size="sm">{subject}</Text>
          </Paper>
          <Text size="xs" style={{ color: tokens.textSecondary }}>
            Recipients will receive this as a BCC email from "Agent Red Service
            Administrator". Email addresses will not be disclosed to each other.
          </Text>
          <Group justify="flex-end">
            <Button
              variant="subtle"
              onClick={() => setConfirmOpen(false)}
              disabled={sending}
            >
              Cancel
            </Button>
            <Button
              color="red"
              onClick={handleSend}
              loading={sending}
            >
              Confirm &amp; Send
            </Button>
          </Group>
        </Stack>
      </Modal>
    </Box>
  );
}
