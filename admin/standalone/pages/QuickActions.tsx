// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

/**
 * Quick Actions page — Standalone admin.
 *
 * CRUD interface for managing contextual quick action prompt buttons
 * and page assignments. Quick actions appear as clickable pill buttons
 * in the chat widget greeting area, sending a hidden prompt to the AI.
 *
 * API endpoints (admin_quick_action_api.py):
 *   GET/POST          /api/admin/quick-actions
 *   GET/PUT/DELETE     /api/admin/quick-actions/{id}
 *   GET/PUT            /api/admin/quick-actions/assignments
 *   DELETE             /api/admin/quick-actions/assignments/{type}
 *
 * Architecture: WI #226-229
 */

import React, { useState, useCallback, useEffect, useRef } from 'react';
import {
  Paper,
  Table,
  Badge,
  Button,
  Modal,
  TextInput,
  Textarea,
  Select,
  Switch,
  NumberInput,
  Group,
  Stack,
  Title,
  Text,
  ActionIcon,
  Tooltip,
  Loader,
  Alert,
  Tabs,
  useComputedColorScheme,
} from '@mantine/core';
import { useAppContext } from '../layouts/StandaloneLayout';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const BRAND_RED = '#ff3621';

const PAGE_TYPES = [
  { value: 'all', label: 'All pages (fallback)' },
  { value: 'home', label: 'Home' },
  { value: 'product', label: 'Product' },
  { value: 'collection', label: 'Collection' },
  { value: 'cart', label: 'Cart' },
  { value: 'search', label: 'Search' },
  { value: 'blog', label: 'Blog' },
  { value: 'page', label: 'Page' },
  { value: 'other', label: 'Other' },
];

const STARTER_EXAMPLES = [
  { icon: '📦', label: 'Track my order', prompt: 'I want to track my recent order. Can you help me find the status?' },
  { icon: '🔄', label: 'Return policy', prompt: 'What is your return and exchange policy? How do I start a return?' },
  { icon: '💡', label: 'Product recommendations', prompt: 'Can you recommend products based on what I\'m looking at? {{product_title}}' },
  { icon: '❓', label: 'Help with my order', prompt: 'I need help with an issue related to my order. Can you assist?' },
];

const TEMPLATE_VARS = [
  { var: '{{page_type}}', desc: 'Current page type (home, product, etc.)' },
  { var: '{{page_handle}}', desc: 'URL slug or Shopify handle' },
  { var: '{{page_title}}', desc: 'Document title' },
  { var: '{{page_url}}', desc: 'Full page URL' },
  { var: '{{product_title}}', desc: 'Product title (product pages only)' },
  { var: '{{collection_title}}', desc: 'Collection title (collection pages only)' },
];

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface QuickAction {
  id: string;
  label: string;
  promptTemplate: string;
  icon: string | null;
  isActive: boolean;
  sortOrder: number;
  createdAt: string;
  updatedAt: string;
}

interface PageAssignment {
  pageType: string;
  pageHandle: string | null;
  slot1ActionId: string | null;
  slot2ActionId: string | null;
  slot1Action: QuickAction | null;
  slot2Action: QuickAction | null;
  autoOpen?: boolean;
  autoOpenDelayMs?: number;
}

// ---------------------------------------------------------------------------
// Delete icon SVG
// ---------------------------------------------------------------------------

const TrashIcon: React.FC = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="3 6 5 6 21 6" />
    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
  </svg>
);

const EditIcon: React.FC = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
  </svg>
);

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export const QuickActionsPage: React.FC = () => {
  const { apiFetch, onNotify } = useAppContext();
  const computedColorScheme = useComputedColorScheme('dark');
  const isDark = computedColorScheme === 'dark';

  // ---- State ---------------------------------------------------------------

  const [actions, setActions] = useState<QuickAction[]>([]);
  const [assignments, setAssignments] = useState<PageAssignment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Action modal
  const [actionModalOpen, setActionModalOpen] = useState(false);
  const [editingAction, setEditingAction] = useState<QuickAction | null>(null);
  const [formLabel, setFormLabel] = useState('');
  const [formPrompt, setFormPrompt] = useState('');
  const [formIcon, setFormIcon] = useState('');
  const [formActive, setFormActive] = useState(true);
  const [formSortOrder, setFormSortOrder] = useState<number>(0);
  const [saving, setSaving] = useState(false);

  // Prompt textarea ref (for cursor-position variable insertion)
  const promptRef = useRef<HTMLTextAreaElement>(null);

  // Confirm delete
  const [confirmDelete, setConfirmDelete] = useState<{ id: string; label: string } | null>(null);

  // ---- Data fetching -------------------------------------------------------

  const fetchActions = useCallback(async () => {
    try {
      const resp = await apiFetch('/api/admin/quick-actions');
      if (!resp.ok) throw new Error(`Failed to load quick actions: ${resp.status}`);
      const data = await resp.json();
      setActions(data.actions || []);
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Failed to load';
      setError(msg);
    }
  }, [apiFetch]);

  const fetchAssignments = useCallback(async () => {
    try {
      const resp = await apiFetch('/api/admin/quick-actions/assignments');
      if (!resp.ok) throw new Error(`Failed to load assignments: ${resp.status}`);
      const data = await resp.json();
      setAssignments(data.assignments || []);
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Failed to load';
      setError(msg);
    }
  }, [apiFetch]);

  useEffect(() => {
    async function loadAll() {
      setLoading(true);
      await Promise.all([fetchActions(), fetchAssignments()]);
      setLoading(false);
    }
    loadAll();
  }, [fetchActions, fetchAssignments]);

  // ---- Action CRUD ---------------------------------------------------------

  const openCreateAction = useCallback(() => {
    setEditingAction(null);
    setFormLabel('');
    setFormPrompt('');
    setFormIcon('');
    setFormActive(true);
    setFormSortOrder(actions.length);
    setActionModalOpen(true);
  }, [actions.length]);

  const openEditAction = useCallback((action: QuickAction) => {
    setEditingAction(action);
    setFormLabel(action.label);
    setFormPrompt(action.promptTemplate);
    setFormIcon(action.icon || '');
    setFormActive(action.isActive);
    setFormSortOrder(action.sortOrder);
    setActionModalOpen(true);
  }, []);

  const closeActionModal = useCallback(() => {
    setActionModalOpen(false);
    setEditingAction(null);
  }, []);

  const handleSaveAction = useCallback(async () => {
    if (!formLabel.trim() || !formPrompt.trim()) return;
    setSaving(true);
    try {
      const body: Record<string, unknown> = {
        label: formLabel.trim(),
        prompt_template: formPrompt.trim(),
        icon: formIcon.trim() || null,
        is_active: formActive,
        sort_order: formSortOrder,
      };

      if (editingAction) {
        // Update
        const resp = await apiFetch(`/api/admin/quick-actions/${editingAction.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        });
        if (!resp.ok) {
          const errText = await resp.text().catch(() => '');
          throw new Error(`Update failed: ${resp.status} ${errText}`);
        }
        onNotify(`Updated "${formLabel.trim()}"`, 'success');
      } else {
        // Create
        const resp = await apiFetch('/api/admin/quick-actions', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        });
        if (!resp.ok) {
          const errText = await resp.text().catch(() => '');
          throw new Error(`Create failed: ${resp.status} ${errText}`);
        }
        onNotify(`Created "${formLabel.trim()}"`, 'success');
      }

      closeActionModal();
      await fetchActions();
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Save failed';
      onNotify(msg, 'error');
    } finally {
      setSaving(false);
    }
  }, [formLabel, formPrompt, formIcon, formActive, formSortOrder, editingAction, apiFetch, onNotify, closeActionModal, fetchActions]);

  const handleDeleteAction = useCallback(async (id: string) => {
    try {
      const resp = await apiFetch(`/api/admin/quick-actions/${id}`, { method: 'DELETE' });
      if (!resp.ok) throw new Error(`Delete failed: ${resp.status}`);
      onNotify('Quick action deleted', 'success');
      setConfirmDelete(null);
      await Promise.all([fetchActions(), fetchAssignments()]);
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Delete failed';
      onNotify(msg, 'error');
    }
  }, [apiFetch, onNotify, fetchActions, fetchAssignments]);

  // ---- Create from starter example -------------------------------------------

  const handleCreateStarter = useCallback(async (starter: { icon: string; label: string; prompt: string }, index: number) => {
    try {
      const resp = await apiFetch('/api/admin/quick-actions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          label: starter.label,
          prompt_template: starter.prompt,
          icon: starter.icon,
          is_active: true,
          sort_order: index,
        }),
      });
      if (!resp.ok) throw new Error(`Create failed: ${resp.status}`);
      onNotify(`Created "${starter.label}"`, 'success');
      await fetchActions();
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Create failed';
      onNotify(msg, 'error');
    }
  }, [apiFetch, onNotify, fetchActions]);

  // ---- Assignment inline save -----------------------------------------------

  const handleInlineAssignmentSave = useCallback(async (
    pageType: string,
    slot: 'slot1' | 'slot2',
    actionId: string | null,
  ) => {
    // Find existing assignment for this page type
    const existing = assignments.find((a) => a.pageType === pageType);
    const slot1 = slot === 'slot1' ? actionId : (existing?.slot1ActionId ?? null);
    const slot2 = slot === 'slot2' ? actionId : (existing?.slot2ActionId ?? null);

    // If both slots are now empty, delete the assignment
    if (!slot1 && !slot2) {
      try {
        const resp = await apiFetch(`/api/admin/quick-actions/assignments/${pageType}`, {
          method: 'DELETE',
        });
        if (!resp.ok && resp.status !== 404) throw new Error(`Delete failed: ${resp.status}`);
        await fetchAssignments();
      } catch (err) {
        const msg = err instanceof Error ? err.message : 'Save failed';
        onNotify(msg, 'error');
      }
      return;
    }

    try {
      const resp = await apiFetch('/api/admin/quick-actions/assignments', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          page_type: pageType,
          page_handle: null,
          slot_1_action_id: slot1,
          slot_2_action_id: slot2,
        }),
      });
      if (!resp.ok) {
        const errText = await resp.text().catch(() => '');
        throw new Error(`Save failed: ${resp.status} ${errText}`);
      }
      await fetchAssignments();
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Save failed';
      onNotify(msg, 'error');
    }
  }, [assignments, apiFetch, onNotify, fetchAssignments]);

  // ---- Auto-open toggle per page (WI #254) ----------------------------------

  const handleAutoOpenToggle = useCallback(async (
    pageType: string,
    autoOpen: boolean,
  ) => {
    const existing = assignments.find((a) => a.pageType === pageType);
    try {
      const resp = await apiFetch('/api/admin/quick-actions/assignments', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          page_type: pageType,
          page_handle: null,
          slot_1_action_id: existing?.slot1ActionId ?? null,
          slot_2_action_id: existing?.slot2ActionId ?? null,
          auto_open: autoOpen,
          auto_open_delay_ms: existing?.autoOpenDelayMs ?? 3000,
        }),
      });
      if (!resp.ok) throw new Error(`Save failed: ${resp.status}`);
      await fetchAssignments();
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Save failed';
      onNotify(msg, 'error');
    }
  }, [assignments, apiFetch, onNotify, fetchAssignments]);

  // ---- Insert template variable at cursor ----------------------------------

  const insertTemplateVar = useCallback((token: string) => {
    const ta = promptRef.current;
    if (!ta) {
      // Fallback: append to end
      const needsSpace = formPrompt.length > 0 && !formPrompt.endsWith(' ');
      setFormPrompt(formPrompt + (needsSpace ? ' ' : '') + token);
      return;
    }
    const start = ta.selectionStart ?? formPrompt.length;
    const end = ta.selectionEnd ?? start;
    const before = formPrompt.slice(0, start);
    const after = formPrompt.slice(end);
    const needsSpace = before.length > 0 && !before.endsWith(' ') && !before.endsWith('\n');
    const newValue = before + (needsSpace ? ' ' : '') + token + after;
    setFormPrompt(newValue);
    // Restore cursor after the inserted token
    requestAnimationFrame(() => {
      const pos = before.length + (needsSpace ? 1 : 0) + token.length;
      ta.focus();
      ta.setSelectionRange(pos, pos);
    });
  }, [formPrompt]);

  // ---- Action select data --------------------------------------------------

  const actionSelectData = actions.map((a) => ({
    value: a.id,
    label: `${a.icon ? a.icon + ' ' : ''}${a.label}${!a.isActive ? ' (inactive)' : ''}`,
  }));

  // ---- Loading state -------------------------------------------------------

  if (loading) {
    return (
      <Stack gap="lg" align="center" py="xl">
        <Loader size="md" color={BRAND_RED} />
        <Text c="dimmed" size="sm">Loading quick actions...</Text>
      </Stack>
    );
  }

  if (error && !actions.length) {
    return (
      <Stack gap="lg">
        <Title order={2}>Quick actions</Title>
        <Alert color="red" title="Failed to load">
          {error}
          <br />
          <Button
            variant="light"
            color="red"
            size="xs"
            mt="sm"
            onClick={() => {
              setError(null);
              setLoading(true);
              Promise.all([fetchActions(), fetchAssignments()]).then(() => setLoading(false));
            }}
          >
            Retry
          </Button>
        </Alert>
      </Stack>
    );
  }

  // ---- Render ---------------------------------------------------------------

  return (
    <Stack gap="lg">
      {/* Page header */}
      <div>
        <Title order={2}>Quick actions</Title>
        <Text c="dimmed" size="sm">
          Manage contextual prompt buttons that appear in the chat widget
        </Text>
      </div>

      <Tabs defaultValue="prompts" variant="outline">
        <Tabs.List>
          <Tabs.Tab value="prompts">Prompt library ({actions.length})</Tabs.Tab>
          <Tabs.Tab value="assignments">Page assignments</Tabs.Tab>
        </Tabs.List>

        {/* ================================================================= */}
        {/* TAB: Prompt Library                                               */}
        {/* ================================================================= */}

        <Tabs.Panel value="prompts" pt="md">
          <Stack gap="md">
            <Group justify="flex-end">
              <Button color={BRAND_RED} onClick={openCreateAction}>
                Create quick action
              </Button>
            </Group>

            <Paper radius="md" withBorder>
              <Table.ScrollContainer minWidth={640}>
                <Table verticalSpacing="sm" horizontalSpacing="md">
                  <Table.Thead>
                    <Table.Tr>
                      <Table.Th w={40}>Order</Table.Th>
                      <Table.Th w={50}>Icon</Table.Th>
                      <Table.Th>Label</Table.Th>
                      <Table.Th>Prompt template</Table.Th>
                      <Table.Th w={80}>Status</Table.Th>
                      <Table.Th w={100} ta="right">Actions</Table.Th>
                    </Table.Tr>
                  </Table.Thead>
                  <Table.Tbody>
                    {actions.length === 0 && (
                      <Table.Tr>
                        <Table.Td colSpan={6}>
                          <Stack gap="md" py="lg" px="md" align="center">
                            <Text ta="center" c="dimmed" size="sm">
                              No quick actions yet. Start with one of these examples or create your own.
                            </Text>
                            <Group gap="sm" wrap="wrap" justify="center">
                              {STARTER_EXAMPLES.map((starter, idx) => (
                                <Button
                                  key={starter.label}
                                  variant="light"
                                  color="gray"
                                  size="sm"
                                  leftSection={<span>{starter.icon}</span>}
                                  onClick={() => handleCreateStarter(starter, idx)}
                                >
                                  {starter.label}
                                </Button>
                              ))}
                            </Group>
                            <Text ta="center" c="dimmed" size="xs">
                              Click any example to add it, then customize the prompt template
                            </Text>
                          </Stack>
                        </Table.Td>
                      </Table.Tr>
                    )}
                    {actions.map((action) => (
                      <Table.Tr key={action.id}>
                        <Table.Td>
                          <Text size="sm" c="dimmed">{action.sortOrder}</Text>
                        </Table.Td>
                        <Table.Td>
                          <Text size="lg">{action.icon || '—'}</Text>
                        </Table.Td>
                        <Table.Td>
                          <Text size="sm" fw={500}>{action.label}</Text>
                        </Table.Td>
                        <Table.Td>
                          <Text
                            size="xs"
                            c="dimmed"
                            lineClamp={2}
                            style={{ maxWidth: 300 }}
                          >
                            {action.promptTemplate}
                          </Text>
                        </Table.Td>
                        <Table.Td>
                          <Badge
                            variant={action.isActive ? 'filled' : 'outline'}
                            color={action.isActive ? 'green' : 'gray'}
                            size="sm"
                          >
                            {action.isActive ? 'Active' : 'Inactive'}
                          </Badge>
                        </Table.Td>
                        <Table.Td>
                          <Group gap="xs" justify="flex-end">
                            <Tooltip label="Edit" position="left">
                              <ActionIcon
                                variant="subtle"
                                color="gray"
                                size="sm"
                                onClick={() => openEditAction(action)}
                              >
                                <EditIcon />
                              </ActionIcon>
                            </Tooltip>
                            <Tooltip label="Delete" position="left">
                              <ActionIcon
                                variant="subtle"
                                color="red"
                                size="sm"
                                onClick={() => setConfirmDelete({ id: action.id, label: action.label })}
                              >
                                <TrashIcon />
                              </ActionIcon>
                            </Tooltip>
                          </Group>
                        </Table.Td>
                      </Table.Tr>
                    ))}
                  </Table.Tbody>
                </Table>
              </Table.ScrollContainer>
            </Paper>
          </Stack>
        </Tabs.Panel>

        {/* ================================================================= */}
        {/* TAB: Page Assignments — inline list of all page types            */}
        {/* ================================================================= */}

        <Tabs.Panel value="assignments" pt="md">
          <Stack gap="md">
            <Alert color="blue" variant="light" title="How page assignments work">
              <Text size="sm">
                Each page type can have up to 2 quick action buttons (slot 1 and slot 2).
                The "All pages" row serves as a fallback when no specific page type
                assignment is configured. Specific page types take priority.
              </Text>
            </Alert>

            <Paper radius="md" withBorder>
              <Table.ScrollContainer minWidth={680}>
                <Table verticalSpacing="sm" horizontalSpacing="md">
                  <Table.Thead>
                    <Table.Tr>
                      <Table.Th w={180}>Page type</Table.Th>
                      <Table.Th>Slot 1</Table.Th>
                      <Table.Th>Slot 2</Table.Th>
                      <Table.Th w={100}>
                        <Tooltip label="Auto-open the widget on this page type" position="top">
                          <Text component="span" size="sm" fw={600} style={{ cursor: 'help' }}>
                            Auto-open
                          </Text>
                        </Tooltip>
                      </Table.Th>
                    </Table.Tr>
                  </Table.Thead>
                  <Table.Tbody>
                    {PAGE_TYPES.map((pt) => {
                      const assign = assignments.find((a) => a.pageType === pt.value);
                      return (
                        <Table.Tr key={pt.value}>
                          <Table.Td>
                            <Badge
                              variant="light"
                              color={pt.value === 'all' ? 'blue' : 'gray'}
                              size="sm"
                            >
                              {pt.label}
                            </Badge>
                          </Table.Td>
                          <Table.Td>
                            <Select
                              size="xs"
                              placeholder="None"
                              data={actionSelectData}
                              value={assign?.slot1ActionId ?? null}
                              onChange={(val) => handleInlineAssignmentSave(pt.value, 'slot1', val)}
                              clearable
                              styles={{ input: { minHeight: 30, fontSize: 13 } }}
                            />
                          </Table.Td>
                          <Table.Td>
                            <Select
                              size="xs"
                              placeholder="None"
                              data={actionSelectData}
                              value={assign?.slot2ActionId ?? null}
                              onChange={(val) => handleInlineAssignmentSave(pt.value, 'slot2', val)}
                              clearable
                              styles={{ input: { minHeight: 30, fontSize: 13 } }}
                            />
                          </Table.Td>
                          <Table.Td>
                            <Switch
                              size="xs"
                              color={BRAND_RED}
                              checked={assign?.autoOpen ?? false}
                              onChange={(e) => handleAutoOpenToggle(pt.value, e.currentTarget.checked)}
                              aria-label={`Auto-open on ${pt.label}`}
                            />
                          </Table.Td>
                        </Table.Tr>
                      );
                    })}
                  </Table.Tbody>
                </Table>
              </Table.ScrollContainer>
            </Paper>
          </Stack>
        </Tabs.Panel>

      </Tabs>

      {/* ================================================================= */}
      {/* Create / Edit Action Modal                                        */}
      {/* ================================================================= */}

      <Modal
        opened={actionModalOpen}
        onClose={closeActionModal}
        title={
          <Text fw={600} size="lg">
            {editingAction ? 'Edit quick action' : 'Create quick action'}
          </Text>
        }
        centered
        size="lg"
      >
        <Stack gap="md">
          <TextInput
            label="Button label"
            description="Text shown on the quick action button"
            placeholder="e.g. What can you do?"
            required
            maxLength={100}
            value={formLabel}
            onChange={(e) => setFormLabel(e.currentTarget.value)}
          />
          <div>
            <Textarea
              ref={promptRef}
              label="Prompt template"
              description="Hidden prompt sent to AI when clicked. Click a variable below to insert it."
              placeholder="e.g. Tell me about {{product_title}} and its key features"
              required
              maxLength={2000}
              minRows={3}
              maxRows={8}
              value={formPrompt}
              onChange={(e) => setFormPrompt(e.currentTarget.value)}
            />
            <Group gap={6} mt={6} wrap="wrap">
              {TEMPLATE_VARS.map((tv) => (
                <Button
                  key={tv.var}
                  size="compact-xs"
                  variant="light"
                  color="gray"
                  style={{ fontSize: 11, fontFamily: "'JetBrains Mono', monospace" }}
                  title={tv.desc}
                  onClick={() => insertTemplateVar(tv.var)}
                >
                  {tv.var}
                </Button>
              ))}
            </Group>
          </div>
          <div>
            <TextInput
              label="Icon (optional)"
              description="Single emoji displayed before the button label. Click one below or paste your own."
              placeholder="e.g. 📦"
              maxLength={50}
              value={formIcon}
              onChange={(e) => setFormIcon(e.currentTarget.value)}
            />
            <Group gap={4} mt={6} wrap="wrap">
              {['📦', '🔄', '💡', '❓', '🛒', '💬', '🏷️', '🚚', '⭐', '🔍', '💰', '🎁'].map((emoji) => (
                <Button
                  key={emoji}
                  size="compact-xs"
                  variant={formIcon === emoji ? 'filled' : 'light'}
                  color={formIcon === emoji ? 'red' : 'gray'}
                  style={{ fontSize: 16, padding: '2px 6px', minWidth: 32 }}
                  onClick={() => setFormIcon(emoji)}
                >
                  {emoji}
                </Button>
              ))}
            </Group>
          </div>
          <Switch
            label="Active"
            description="Inactive quick actions won't appear in the widget"
            checked={formActive}
            onChange={(e) => setFormActive(e.currentTarget.checked)}
            color={BRAND_RED}
          />

          {/* Preview */}
          {formLabel.trim() && (
            <div>
              <Text size="sm" fw={500} mb={4}>Preview</Text>
              <div style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 6,
                padding: '6px 14px',
                borderRadius: 20,
                border: `1px solid ${isDark ? '#272727' : '#dee2e6'}`,
                background: isDark ? '#1f1f1f' : '#f1f3f5',
                fontSize: 13,
                color: isDark ? '#E0E0E0' : '#1f2937',
              }}>
                {formIcon.trim() && <span>{formIcon.trim()}</span>}
                <span>{formLabel.trim()}</span>
              </div>
            </div>
          )}

          <Group justify="flex-end" mt="sm">
            <Button variant="default" onClick={closeActionModal}>
              Cancel
            </Button>
            <Button
              color={BRAND_RED}
              onClick={handleSaveAction}
              disabled={!formLabel.trim() || !formPrompt.trim()}
              loading={saving}
            >
              {editingAction ? 'Save changes' : 'Create'}
            </Button>
          </Group>
        </Stack>
      </Modal>

      {/* ================================================================= */}
      {/* Confirm Delete Modal                                              */}
      {/* ================================================================= */}

      <Modal
        opened={!!confirmDelete}
        onClose={() => setConfirmDelete(null)}
        title={
          <Text fw={600} size="lg">
            Delete quick action
          </Text>
        }
        centered
        size="sm"
      >
        <Stack gap="md">
          <Text size="sm">
            Are you sure you want to delete{' '}
            <Text component="span" fw={600}>"{confirmDelete?.label}"</Text>?
            This will also remove it from any page assignments.
          </Text>
          <Group justify="flex-end" mt="sm">
            <Button variant="default" onClick={() => setConfirmDelete(null)}>
              Cancel
            </Button>
            <Button
              color="red"
              onClick={() => {
                if (confirmDelete) handleDeleteAction(confirmDelete.id);
              }}
            >
              Delete
            </Button>
          </Group>
        </Stack>
      </Modal>
    </Stack>
  );
};
