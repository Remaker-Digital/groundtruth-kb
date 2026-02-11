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

import React, { useState, useCallback, useEffect } from 'react';
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
  Code,
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

  // Assignment modal
  const [assignModalOpen, setAssignModalOpen] = useState(false);
  const [assignPageType, setAssignPageType] = useState<string | null>('all');
  const [assignSlot1, setAssignSlot1] = useState<string | null>(null);
  const [assignSlot2, setAssignSlot2] = useState<string | null>(null);
  const [savingAssign, setSavingAssign] = useState(false);

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

  // ---- Assignment CRUD -----------------------------------------------------

  const openCreateAssignment = useCallback(() => {
    setAssignPageType('all');
    setAssignSlot1(null);
    setAssignSlot2(null);
    setAssignModalOpen(true);
  }, []);

  const openEditAssignment = useCallback((assignment: PageAssignment) => {
    setAssignPageType(assignment.pageType);
    setAssignSlot1(assignment.slot1ActionId);
    setAssignSlot2(assignment.slot2ActionId);
    setAssignModalOpen(true);
  }, []);

  const closeAssignModal = useCallback(() => {
    setAssignModalOpen(false);
  }, []);

  const handleSaveAssignment = useCallback(async () => {
    if (!assignPageType) return;
    setSavingAssign(true);
    try {
      const resp = await apiFetch('/api/admin/quick-actions/assignments', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          page_type: assignPageType,
          page_handle: null,
          slot_1_action_id: assignSlot1,
          slot_2_action_id: assignSlot2,
        }),
      });
      if (!resp.ok) {
        const errText = await resp.text().catch(() => '');
        throw new Error(`Save failed: ${resp.status} ${errText}`);
      }
      onNotify(`Assignment for "${assignPageType}" saved`, 'success');
      closeAssignModal();
      await fetchAssignments();
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Save failed';
      onNotify(msg, 'error');
    } finally {
      setSavingAssign(false);
    }
  }, [assignPageType, assignSlot1, assignSlot2, apiFetch, onNotify, closeAssignModal, fetchAssignments]);

  const handleDeleteAssignment = useCallback(async (pageType: string) => {
    try {
      const resp = await apiFetch(`/api/admin/quick-actions/assignments/${pageType}`, {
        method: 'DELETE',
      });
      if (!resp.ok) throw new Error(`Delete failed: ${resp.status}`);
      onNotify(`Assignment for "${pageType}" removed`, 'success');
      await fetchAssignments();
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Delete failed';
      onNotify(msg, 'error');
    }
  }, [apiFetch, onNotify, fetchAssignments]);

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
          <Tabs.Tab value="assignments">Page assignments ({assignments.length})</Tabs.Tab>
          <Tabs.Tab value="variables">Template variables</Tabs.Tab>
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
                          <Text ta="center" c="dimmed" py="xl" size="sm">
                            No quick actions yet. Create your first prompt button to get started.
                          </Text>
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
        {/* TAB: Page Assignments                                             */}
        {/* ================================================================= */}

        <Tabs.Panel value="assignments" pt="md">
          <Stack gap="md">
            <Alert color="blue" variant="light" title="How page assignments work">
              <Text size="sm">
                Each page type can have up to 2 quick action buttons (slot 1 and slot 2).
                The "All pages" assignment serves as a fallback when no specific page type
                assignment is configured. Specific page types (product, collection, etc.)
                take priority over "All pages".
              </Text>
            </Alert>

            <Group justify="flex-end">
              <Button color={BRAND_RED} onClick={openCreateAssignment}>
                Add page assignment
              </Button>
            </Group>

            <Paper radius="md" withBorder>
              <Table.ScrollContainer minWidth={500}>
                <Table verticalSpacing="sm" horizontalSpacing="md">
                  <Table.Thead>
                    <Table.Tr>
                      <Table.Th>Page type</Table.Th>
                      <Table.Th>Slot 1</Table.Th>
                      <Table.Th>Slot 2</Table.Th>
                      <Table.Th w={100} ta="right">Actions</Table.Th>
                    </Table.Tr>
                  </Table.Thead>
                  <Table.Tbody>
                    {assignments.length === 0 && (
                      <Table.Tr>
                        <Table.Td colSpan={4}>
                          <Text ta="center" c="dimmed" py="xl" size="sm">
                            No page assignments yet. Add an assignment to control which quick actions
                            appear on each page type.
                          </Text>
                        </Table.Td>
                      </Table.Tr>
                    )}
                    {assignments.map((assign) => (
                      <Table.Tr key={assign.pageType}>
                        <Table.Td>
                          <Badge
                            variant="light"
                            color={assign.pageType === 'all' ? 'blue' : 'gray'}
                            size="sm"
                            tt="capitalize"
                          >
                            {assign.pageType === 'all' ? 'All pages (fallback)' : assign.pageType}
                          </Badge>
                        </Table.Td>
                        <Table.Td>
                          {assign.slot1Action ? (
                            <Text size="sm">
                              {assign.slot1Action.icon ? `${assign.slot1Action.icon} ` : ''}
                              {assign.slot1Action.label}
                            </Text>
                          ) : (
                            <Text size="sm" c="dimmed">Empty</Text>
                          )}
                        </Table.Td>
                        <Table.Td>
                          {assign.slot2Action ? (
                            <Text size="sm">
                              {assign.slot2Action.icon ? `${assign.slot2Action.icon} ` : ''}
                              {assign.slot2Action.label}
                            </Text>
                          ) : (
                            <Text size="sm" c="dimmed">Empty</Text>
                          )}
                        </Table.Td>
                        <Table.Td>
                          <Group gap="xs" justify="flex-end">
                            <Tooltip label="Edit" position="left">
                              <ActionIcon
                                variant="subtle"
                                color="gray"
                                size="sm"
                                onClick={() => openEditAssignment(assign)}
                              >
                                <EditIcon />
                              </ActionIcon>
                            </Tooltip>
                            <Tooltip label="Remove" position="left">
                              <ActionIcon
                                variant="subtle"
                                color="red"
                                size="sm"
                                onClick={() => handleDeleteAssignment(assign.pageType)}
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
        {/* TAB: Template Variables                                           */}
        {/* ================================================================= */}

        <Tabs.Panel value="variables" pt="md">
          <Stack gap="md">
            <Alert color="blue" variant="light" title="Template variable substitution">
              <Text size="sm">
                Use double-curly-brace placeholders in your prompt templates.
                These are replaced with page context values when the customer
                clicks a quick action button.
              </Text>
            </Alert>

            <Paper radius="md" withBorder>
              <Table verticalSpacing="sm" horizontalSpacing="md">
                <Table.Thead>
                  <Table.Tr>
                    <Table.Th w={220}>Variable</Table.Th>
                    <Table.Th>Description</Table.Th>
                  </Table.Tr>
                </Table.Thead>
                <Table.Tbody>
                  {TEMPLATE_VARS.map((tv) => (
                    <Table.Tr key={tv.var}>
                      <Table.Td>
                        <Code>{tv.var}</Code>
                      </Table.Td>
                      <Table.Td>
                        <Text size="sm">{tv.desc}</Text>
                      </Table.Td>
                    </Table.Tr>
                  ))}
                </Table.Tbody>
              </Table>
            </Paper>

            <Text size="sm" c="dimmed">
              Example: "Tell me about {'{{product_title}}'}" becomes
              "Tell me about Classic Running Shoes" on a product page.
              Unresolved variables are left as-is.
            </Text>
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
          <Textarea
            label="Prompt template"
            description="Hidden prompt sent to AI when clicked. Use {{variable}} for page context."
            placeholder="e.g. Tell me about {{product_title}} and its key features"
            required
            maxLength={2000}
            minRows={3}
            maxRows={8}
            value={formPrompt}
            onChange={(e) => setFormPrompt(e.currentTarget.value)}
          />
          <Group grow>
            <TextInput
              label="Icon (optional)"
              description="Emoji or icon identifier"
              placeholder="e.g. 🚀"
              maxLength={50}
              value={formIcon}
              onChange={(e) => setFormIcon(e.currentTarget.value)}
            />
            <NumberInput
              label="Sort order"
              description="Lower numbers appear first"
              min={0}
              max={999}
              value={formSortOrder}
              onChange={(val) => setFormSortOrder(typeof val === 'number' ? val : 0)}
            />
          </Group>
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
                border: '1px solid #272727',
                background: '#1f1f1f',
                fontSize: 13,
                color: '#E0E0E0',
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
      {/* Assignment Modal                                                  */}
      {/* ================================================================= */}

      <Modal
        opened={assignModalOpen}
        onClose={closeAssignModal}
        title={
          <Text fw={600} size="lg">
            Page assignment
          </Text>
        }
        centered
        size="md"
      >
        <Stack gap="md">
          <Select
            label="Page type"
            description="Which page type this assignment applies to"
            data={PAGE_TYPES}
            value={assignPageType}
            onChange={setAssignPageType}
            allowDeselect={false}
          />
          <Select
            label="Slot 1 — Quick action"
            description="First quick action button"
            placeholder="Select a quick action..."
            data={actionSelectData}
            value={assignSlot1}
            onChange={setAssignSlot1}
            clearable
          />
          <Select
            label="Slot 2 — Quick action"
            description="Second quick action button"
            placeholder="Select a quick action..."
            data={actionSelectData}
            value={assignSlot2}
            onChange={setAssignSlot2}
            clearable
          />
          <Group justify="flex-end" mt="sm">
            <Button variant="default" onClick={closeAssignModal}>
              Cancel
            </Button>
            <Button
              color={BRAND_RED}
              onClick={handleSaveAssignment}
              disabled={!assignPageType}
              loading={savingAssign}
            >
              Save assignment
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
