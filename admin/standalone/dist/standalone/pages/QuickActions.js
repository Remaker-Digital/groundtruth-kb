import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
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
import { useState, useCallback, useEffect, useRef } from 'react';
import { Paper, Table, Badge, Button, Modal, TextInput, Textarea, Select, Switch, NumberInput, Group, Stack, Title, Text, ActionIcon, Tooltip, Alert, Tabs, useComputedColorScheme, } from '@mantine/core';
import { useAppContext } from '../layouts/StandaloneLayout';
import { LoadingState } from '../../shared/LoadingState';
import { tokens } from '../../shared/theme/styles';
// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------
const ACTION_BLUE = tokens.action;
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
// Delete icon SVG
// ---------------------------------------------------------------------------
const TrashIcon = () => (_jsxs("svg", { width: "14", height: "14", viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: "2", strokeLinecap: "round", strokeLinejoin: "round", children: [_jsx("polyline", { points: "3 6 5 6 21 6" }), _jsx("path", { d: "M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" })] }));
const EditIcon = () => (_jsxs("svg", { width: "14", height: "14", viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: "2", strokeLinecap: "round", strokeLinejoin: "round", children: [_jsx("path", { d: "M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" }), _jsx("path", { d: "M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" })] }));
// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------
export const QuickActionsPage = () => {
    const { apiFetch, onNotify } = useAppContext();
    const computedColorScheme = useComputedColorScheme('dark');
    const isDark = computedColorScheme === 'dark';
    // ---- State ---------------------------------------------------------------
    const [actions, setActions] = useState([]);
    const [assignments, setAssignments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    // Action modal
    const [actionModalOpen, setActionModalOpen] = useState(false);
    const [editingAction, setEditingAction] = useState(null);
    const [formLabel, setFormLabel] = useState('');
    const [formPrompt, setFormPrompt] = useState('');
    const [formIcon, setFormIcon] = useState('');
    const [formActive, setFormActive] = useState(true);
    const [formSortOrder, setFormSortOrder] = useState(0);
    const [saving, setSaving] = useState(false);
    // Prompt textarea ref (for cursor-position variable insertion)
    const promptRef = useRef(null);
    // Confirm delete
    const [confirmDelete, setConfirmDelete] = useState(null);
    // ---- Data fetching -------------------------------------------------------
    const fetchActions = useCallback(async () => {
        try {
            const resp = await apiFetch('/api/admin/quick-actions');
            if (!resp.ok)
                throw new Error(`Failed to load quick actions: ${resp.status}`);
            const data = await resp.json();
            setActions(data.actions || []);
        }
        catch (err) {
            const msg = err instanceof Error ? err.message : 'Failed to load';
            setError(msg);
        }
    }, [apiFetch]);
    const fetchAssignments = useCallback(async () => {
        try {
            const resp = await apiFetch('/api/admin/quick-actions/assignments');
            if (!resp.ok)
                throw new Error(`Failed to load assignments: ${resp.status}`);
            const data = await resp.json();
            setAssignments(data.assignments || []);
        }
        catch (err) {
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
    const openEditAction = useCallback((action) => {
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
        if (!formLabel.trim() || !formPrompt.trim())
            return;
        setSaving(true);
        try {
            const body = {
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
            }
            else {
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
        }
        catch (err) {
            const msg = err instanceof Error ? err.message : 'Save failed';
            onNotify(msg, 'error');
        }
        finally {
            setSaving(false);
        }
    }, [formLabel, formPrompt, formIcon, formActive, formSortOrder, editingAction, apiFetch, onNotify, closeActionModal, fetchActions]);
    const handleDeleteAction = useCallback(async (id) => {
        try {
            const resp = await apiFetch(`/api/admin/quick-actions/${id}`, { method: 'DELETE' });
            if (!resp.ok)
                throw new Error(`Delete failed: ${resp.status}`);
            onNotify('Quick action deleted', 'success');
            setConfirmDelete(null);
            await Promise.all([fetchActions(), fetchAssignments()]);
        }
        catch (err) {
            const msg = err instanceof Error ? err.message : 'Delete failed';
            onNotify(msg, 'error');
        }
    }, [apiFetch, onNotify, fetchActions, fetchAssignments]);
    // ---- Create from starter example -------------------------------------------
    const handleCreateStarter = useCallback(async (starter, index) => {
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
            if (!resp.ok)
                throw new Error(`Create failed: ${resp.status}`);
            onNotify(`Created "${starter.label}"`, 'success');
            await fetchActions();
        }
        catch (err) {
            const msg = err instanceof Error ? err.message : 'Create failed';
            onNotify(msg, 'error');
        }
    }, [apiFetch, onNotify, fetchActions]);
    // ---- Assignment inline save -----------------------------------------------
    const handleInlineAssignmentSave = useCallback(async (pageType, slot, actionId) => {
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
                if (!resp.ok && resp.status !== 404)
                    throw new Error(`Delete failed: ${resp.status}`);
                await fetchAssignments();
            }
            catch (err) {
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
        }
        catch (err) {
            const msg = err instanceof Error ? err.message : 'Save failed';
            onNotify(msg, 'error');
        }
    }, [assignments, apiFetch, onNotify, fetchAssignments]);
    // ---- Auto-open toggle per page (WI #254) ----------------------------------
    const handleAutoOpenToggle = useCallback(async (pageType, autoOpen) => {
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
            if (!resp.ok)
                throw new Error(`Save failed: ${resp.status}`);
            await fetchAssignments();
        }
        catch (err) {
            const msg = err instanceof Error ? err.message : 'Save failed';
            onNotify(msg, 'error');
        }
    }, [assignments, apiFetch, onNotify, fetchAssignments]);
    // ---- Auto-open delay per page (Issue 14b) ---------------------------------
    const handleAutoOpenDelayChange = useCallback(async (pageType, delayMs) => {
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
                    auto_open: existing?.autoOpen ?? false,
                    auto_open_delay_ms: delayMs,
                }),
            });
            if (!resp.ok)
                throw new Error(`Save failed: ${resp.status}`);
            await fetchAssignments();
        }
        catch (err) {
            const msg = err instanceof Error ? err.message : 'Save failed';
            onNotify(msg, 'error');
        }
    }, [assignments, apiFetch, onNotify, fetchAssignments]);
    // ---- Insert template variable at cursor ----------------------------------
    const insertTemplateVar = useCallback((token) => {
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
        return _jsx(LoadingState, { text: "Loading quick actions" });
    }
    if (error && !actions.length) {
        return (_jsxs(Stack, { gap: "lg", children: [_jsx(Title, { order: 2, children: "Quick actions" }), _jsxs(Alert, { color: "red", title: "Failed to load", children: [error, _jsx("br", {}), _jsx(Button, { variant: "light", color: "red", size: "xs", mt: "sm", onClick: () => {
                                setError(null);
                                setLoading(true);
                                Promise.all([fetchActions(), fetchAssignments()]).then(() => setLoading(false));
                            }, children: "Retry" })] })] }));
    }
    // ---- Render ---------------------------------------------------------------
    return (_jsxs(Stack, { gap: "lg", children: [_jsxs("div", { children: [_jsx(Title, { order: 2, children: "Quick actions" }), _jsx(Text, { c: "dimmed", size: "sm", children: "Manage contextual prompt buttons that appear in the chat widget" })] }), _jsxs(Tabs, { defaultValue: "prompts", variant: "outline", children: [_jsxs(Tabs.List, { children: [_jsxs(Tabs.Tab, { value: "prompts", children: ["Prompt library (", actions.length, ")"] }), _jsx(Tabs.Tab, { value: "assignments", children: "Page assignments" })] }), _jsx(Tabs.Panel, { value: "prompts", pt: "md", children: _jsxs(Stack, { gap: "md", children: [_jsx(Group, { justify: "flex-end", children: _jsx(Button, { color: ACTION_BLUE, onClick: openCreateAction, children: "Create quick action" }) }), _jsx(Paper, { radius: "md", withBorder: true, children: _jsx(Table.ScrollContainer, { minWidth: 640, children: _jsxs(Table, { verticalSpacing: "sm", horizontalSpacing: "md", children: [_jsx(Table.Thead, { children: _jsxs(Table.Tr, { children: [_jsx(Table.Th, { w: 50, children: "Icon" }), _jsx(Table.Th, { children: "Label" }), _jsx(Table.Th, { style: { maxWidth: 300 }, children: "Prompt template" }), _jsx(Table.Th, { w: 100, children: "Status" }), _jsx(Table.Th, { w: 100, ta: "right", children: "Actions" })] }) }), _jsxs(Table.Tbody, { children: [actions.length === 0 && (_jsx(Table.Tr, { children: _jsx(Table.Td, { colSpan: 5, children: _jsxs(Stack, { gap: "md", py: "lg", px: "md", align: "center", children: [_jsx(Text, { ta: "center", c: "dimmed", size: "sm", children: "No quick actions yet. Start with one of these examples or create your own." }), _jsx(Group, { gap: "sm", wrap: "wrap", justify: "center", children: STARTER_EXAMPLES.map((starter, idx) => (_jsx(Button, { variant: "light", color: "gray", size: "sm", leftSection: _jsx("span", { children: starter.icon }), onClick: () => handleCreateStarter(starter, idx), children: starter.label }, starter.label))) }), _jsx(Text, { ta: "center", c: "dimmed", size: "xs", children: "Click any example to add it, then customize the prompt template" })] }) }) })), actions.map((action) => (_jsxs(Table.Tr, { children: [_jsx(Table.Td, { children: _jsx(Text, { size: "lg", children: action.icon || '—' }) }), _jsx(Table.Td, { children: _jsx(Text, { size: "sm", fw: 500, children: action.label }) }), _jsx(Table.Td, { children: _jsx(Text, { size: "xs", c: "dimmed", lineClamp: 2, style: { maxWidth: 300 }, children: action.promptTemplate }) }), _jsx(Table.Td, { children: _jsx(Badge, { variant: action.isActive ? 'filled' : 'outline', color: action.isActive ? 'green' : 'gray', size: "sm", children: action.isActive ? 'Active' : 'Inactive' }) }), _jsx(Table.Td, { children: _jsxs(Group, { gap: "xs", justify: "flex-end", children: [_jsx(Tooltip, { label: "Edit", position: "left", children: _jsx(ActionIcon, { variant: "subtle", color: "gray", size: "sm", onClick: () => openEditAction(action), children: _jsx(EditIcon, {}) }) }), _jsx(Tooltip, { label: "Delete", position: "left", children: _jsx(ActionIcon, { variant: "subtle", color: "red", size: "sm", onClick: () => setConfirmDelete({ id: action.id, label: action.label }), children: _jsx(TrashIcon, {}) }) })] }) })] }, action.id)))] })] }) }) })] }) }), _jsx(Tabs.Panel, { value: "assignments", pt: "md", children: _jsxs(Stack, { gap: "md", children: [_jsx(Alert, { color: "blue", variant: "light", title: "How page assignments work", children: _jsx(Text, { size: "sm", children: "Each page type can have up to 2 quick action buttons (slot 1 and slot 2). The \"All pages\" row serves as a fallback when no specific page type assignment is configured. Specific page types take priority." }) }), _jsx(Paper, { radius: "md", withBorder: true, children: _jsx(Table.ScrollContainer, { minWidth: 680, children: _jsxs(Table, { verticalSpacing: "sm", horizontalSpacing: "md", children: [_jsx(Table.Thead, { children: _jsxs(Table.Tr, { children: [_jsx(Table.Th, { w: 180, children: "Page type" }), _jsx(Table.Th, { children: "Slot 1" }), _jsx(Table.Th, { children: "Slot 2" }), _jsx(Table.Th, { w: 100, children: _jsx(Tooltip, { label: "Auto-open the widget on this page type", position: "top", children: _jsx(Text, { component: "span", size: "sm", fw: 600, style: { cursor: 'help' }, children: "Auto-open" }) }) }), _jsx(Table.Th, { w: 120, children: _jsx(Tooltip, { label: "Seconds to wait before auto-opening the widget", position: "top", children: _jsx(Text, { component: "span", size: "sm", fw: 600, style: { cursor: 'help' }, children: "Delay (s)" }) }) })] }) }), _jsx(Table.Tbody, { children: PAGE_TYPES.map((pt) => {
                                                        const assign = assignments.find((a) => a.pageType === pt.value);
                                                        return (_jsxs(Table.Tr, { children: [_jsx(Table.Td, { children: _jsx(Badge, { variant: "light", color: pt.value === 'all' ? 'blue' : 'gray', size: "sm", children: pt.label }) }), _jsx(Table.Td, { children: _jsx(Select, { size: "xs", placeholder: "None", data: actionSelectData, value: assign?.slot1ActionId ?? null, onChange: (val) => handleInlineAssignmentSave(pt.value, 'slot1', val), clearable: true, styles: { input: { minHeight: 30, fontSize: 13 } } }) }), _jsx(Table.Td, { children: _jsx(Select, { size: "xs", placeholder: "None", data: actionSelectData, value: assign?.slot2ActionId ?? null, onChange: (val) => handleInlineAssignmentSave(pt.value, 'slot2', val), clearable: true, styles: { input: { minHeight: 30, fontSize: 13 } } }) }), _jsx(Table.Td, { children: _jsx(Switch, { size: "xs", color: ACTION_BLUE, checked: assign?.autoOpen ?? false, onChange: (e) => handleAutoOpenToggle(pt.value, e.currentTarget.checked), "aria-label": `Auto-open on ${pt.label}` }) }), _jsx(Table.Td, { children: _jsx(NumberInput, { size: "xs", min: 1, max: 60, step: 1, value: Math.round((assign?.autoOpenDelayMs ?? 3000) / 1000), onChange: (val) => handleAutoOpenDelayChange(pt.value, (typeof val === 'number' ? val : 3) * 1000), disabled: !(assign?.autoOpen), styles: { input: { minHeight: 30, fontSize: 13, width: 70 } }, suffix: "s" }) })] }, pt.value));
                                                    }) })] }) }) })] }) })] }), _jsx(Modal, { opened: actionModalOpen, onClose: closeActionModal, title: _jsx(Text, { fw: 600, size: "lg", children: editingAction ? 'Edit quick action' : 'Create quick action' }), centered: true, size: "lg", children: _jsxs(Stack, { gap: "md", children: [_jsx(TextInput, { label: "Button label", description: "Text shown on the quick action button", placeholder: "e.g. What can you do?", required: true, maxLength: 100, value: formLabel, onChange: (e) => setFormLabel(e.currentTarget.value) }), _jsxs("div", { children: [_jsx(Textarea, { ref: promptRef, label: "Prompt template", description: "Hidden prompt sent to AI when clicked. Click a variable below to insert it.", placeholder: "e.g. Tell me about {{product_title}} and its key features", required: true, maxLength: 2000, minRows: 3, maxRows: 8, value: formPrompt, onChange: (e) => setFormPrompt(e.currentTarget.value) }), _jsx(Group, { gap: 6, mt: 6, wrap: "wrap", children: TEMPLATE_VARS.map((tv) => (_jsx(Button, { size: "compact-xs", variant: "light", color: "gray", style: { fontSize: 11, fontFamily: "'JetBrains Mono', monospace" }, title: tv.desc, onClick: () => insertTemplateVar(tv.var), children: tv.var }, tv.var))) })] }), _jsxs("div", { children: [_jsx(TextInput, { label: "Icon (optional)", description: "Single emoji displayed before the button label. Click one below or paste your own.", placeholder: "e.g. \uD83D\uDCE6", maxLength: 50, value: formIcon, onChange: (e) => setFormIcon(e.currentTarget.value) }), _jsx(Group, { gap: 4, mt: 6, wrap: "wrap", children: ['📦', '🔄', '💡', '❓', '🛒', '💬', '🏷️', '🚚', '⭐', '🔍', '💰', '🎁'].map((emoji) => (_jsx(Button, { size: "compact-xs", variant: formIcon === emoji ? 'filled' : 'light', color: formIcon === emoji ? 'red' : 'gray', style: { fontSize: 16, padding: '2px 6px', minWidth: 32 }, onClick: () => setFormIcon(emoji), children: emoji }, emoji))) })] }), _jsx(Switch, { label: "Active", description: "Inactive quick actions won't appear in the widget", checked: formActive, onChange: (e) => setFormActive(e.currentTarget.checked), color: ACTION_BLUE }), formLabel.trim() && (_jsxs("div", { children: [_jsx(Text, { size: "sm", fw: 500, mb: 4, children: "Preview" }), _jsxs("div", { style: {
                                        display: 'inline-flex',
                                        alignItems: 'center',
                                        gap: 6,
                                        padding: '6px 14px',
                                        borderRadius: 20,
                                        border: `1px solid ${isDark ? tokens.border : '#dee2e6'}`,
                                        background: isDark ? tokens.surface : '#f1f3f5',
                                        fontSize: 13,
                                        color: isDark ? tokens.textSecondary : '#1f2937',
                                    }, children: [formIcon.trim() && _jsx("span", { children: formIcon.trim() }), _jsx("span", { children: formLabel.trim() })] })] })), _jsxs(Group, { justify: "flex-end", mt: "sm", children: [_jsx(Button, { variant: "default", onClick: closeActionModal, children: "Cancel" }), _jsx(Button, { color: ACTION_BLUE, onClick: handleSaveAction, disabled: !formLabel.trim() || !formPrompt.trim(), loading: saving, children: editingAction ? 'Save changes' : 'Create' })] })] }) }), _jsx(Modal, { opened: !!confirmDelete, onClose: () => setConfirmDelete(null), title: _jsx(Text, { fw: 600, size: "lg", children: "Delete quick action" }), centered: true, size: "sm", children: _jsxs(Stack, { gap: "md", children: [_jsxs(Text, { size: "sm", children: ["Are you sure you want to delete", ' ', _jsxs(Text, { component: "span", fw: 600, children: ["\"", confirmDelete?.label, "\""] }), "? This will also remove it from any page assignments."] }), _jsxs(Group, { justify: "flex-end", mt: "sm", children: [_jsx(Button, { variant: "default", onClick: () => setConfirmDelete(null), children: "Cancel" }), _jsx(Button, { color: "red", onClick: () => {
                                        if (confirmDelete)
                                            handleDeleteAction(confirmDelete.id);
                                    }, children: "Delete" })] })] }) })] }));
};
//# sourceMappingURL=QuickActions.js.map