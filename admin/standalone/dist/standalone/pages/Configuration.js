import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * Configuration page — Standalone admin.
 *
 * Mantine v7 layout with 5 form sections (Brand & Persona, Policies,
 * Escalation, Custom Instructions, Language).
 *
 * Data flows through useConfig / useUpdateConfig hooks. Save creates a
 * draft; the Activate/Discard/Roll-back controls live in the sidebar.
 */
import { useState, useEffect, useRef } from 'react';
import { Paper, TextInput, Textarea, Select, Slider, Chip, NumberInput, Button, Group, Stack, Title, Text, Badge, Alert, Switch, ActionIcon, Collapse, Tooltip, Modal, Table, useComputedColorScheme, } from '@mantine/core';
import { useAppContext } from '../layouts/StandaloneLayout';
import { useConfig, useUpdateConfig, useConfigSuggestions, useNamedConfigs, useSaveNamedConfig, useActivateNamedConfig, useDeleteNamedConfig, useAutoSaveDraft, } from '../../shared/hooks/index';
import { AutoSaveIndicator } from '../../shared/components/AutoSaveIndicator';
import { HelpTooltip } from '../../shared/HelpTooltip';
import { LabelWithSuggestion } from '../../shared/components/SuggestionBadge';
import { LoadingState } from '../../shared/LoadingState';
import { tokens } from '../../shared/theme/styles';
const DOCS_BASE = 'https://agentredcx.com/docs/admin-guide';
// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------
const BRAND_RED = tokens.brand; // accent only — email badge indicator
const ACTION_BLUE = tokens.action;
const ESCALATION_CATEGORIES = [
    {
        id: 'sales',
        label: 'Sales',
        description: 'Purchase decisions, pricing questions, product comparisons',
        defaultKeywords: ['pricing', 'discount', 'bulk order', 'quote', 'negotiate', 'wholesale', 'purchase order'],
    },
    {
        id: 'support',
        label: 'Support',
        description: 'Product issues, troubleshooting, how-to questions',
        defaultKeywords: ['not working', 'broken', 'defective', 'help me', 'issue', 'problem', 'error', 'bug'],
    },
    {
        id: 'service',
        label: 'Service',
        description: 'Returns, refunds, exchanges, order modifications',
        defaultKeywords: ['refund', 'return', 'exchange', 'cancel order', 'wrong item', 'missing item', 'damaged'],
    },
    {
        id: 'account',
        label: 'Account',
        description: 'Account access, billing, subscription management',
        defaultKeywords: ['my account', 'password', 'login', 'subscription', 'billing', 'charge', 'invoice', 'cancel subscription'],
    },
    {
        id: 'technical',
        label: 'Technical assistance',
        description: 'Integration issues, API questions, advanced configuration',
        defaultKeywords: ['api', 'integration', 'webhook', 'developer', 'sdk', 'technical', 'configuration', 'setup'],
    },
    {
        id: 'general',
        label: 'General inquiry',
        description: 'Complaints, legal, safety, or anything not matching other categories',
        defaultKeywords: ['complaint', 'manager', 'supervisor', 'lawyer', 'legal', 'sue', 'safety', 'harassment', 'fraud'],
    },
];
function defaultEscalationCategories() {
    const result = {};
    for (const cat of ESCALATION_CATEGORIES) {
        result[cat.id] = {
            enabled: true,
            email: '',
            keywords: [...cat.defaultKeywords],
        };
    }
    return result;
}
/** Primary language options — only languages with full support. */
const PRIMARY_LANGUAGES = [
    { value: 'en', label: 'English' },
];
/** Supported languages — English (available), Spanish/French (coming soon). */
const LANGUAGES = [
    { value: 'en', label: 'English', disabled: false },
    { value: 'es', label: 'Spanish (coming soon)', disabled: true },
    { value: 'fr', label: 'French (coming soon)', disabled: true },
];
const DEFAULTS = {
    brandName: '',
    brandVoice: '',
    formality: 'balanced',
    responseLength: 'standard',
    returnWindow: 30,
    refundPolicy: '',
    shippingPolicy: '',
    escalationThreshold: 0.7,
    escalationCategories: defaultEscalationCategories(),
    idleTimeoutMinutes: 30,
    maxTurns: 50,
    customInstructions: '',
    primaryLanguage: 'en',
    supportedLanguages: ['en'],
};
// ---------------------------------------------------------------------------
// SVG Icons
// ---------------------------------------------------------------------------
const SaveIcon = () => (_jsxs("svg", { width: "16", height: "16", viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: "2", strokeLinecap: "round", strokeLinejoin: "round", children: [_jsx("path", { d: "M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z" }), _jsx("polyline", { points: "17 21 17 13 7 13 7 21" }), _jsx("polyline", { points: "7 3 7 8 15 8" })] }));
const UndoIcon = () => (_jsxs("svg", { width: "16", height: "16", viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: "2", strokeLinecap: "round", strokeLinejoin: "round", children: [_jsx("polyline", { points: "1 4 1 10 7 10" }), _jsx("path", { d: "M3.51 15a9 9 0 1 0 2.13-9.36L1 10" })] }));
const ChevronDownIcon = () => (_jsx("svg", { width: "16", height: "16", viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: "2", strokeLinecap: "round", strokeLinejoin: "round", children: _jsx("polyline", { points: "6 9 12 15 18 9" }) }));
const ChevronUpIcon = () => (_jsx("svg", { width: "16", height: "16", viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: "2", strokeLinecap: "round", strokeLinejoin: "round", children: _jsx("polyline", { points: "18 15 12 9 6 15" }) }));
const XIcon = () => (_jsxs("svg", { width: "12", height: "12", viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: "2", strokeLinecap: "round", strokeLinejoin: "round", children: [_jsx("line", { x1: "18", y1: "6", x2: "6", y2: "18" }), _jsx("line", { x1: "6", y1: "6", x2: "18", y2: "18" })] }));
const ResetIcon = () => (_jsxs("svg", { width: "14", height: "14", viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: "2", strokeLinecap: "round", strokeLinejoin: "round", children: [_jsx("polyline", { points: "1 4 1 10 7 10" }), _jsx("path", { d: "M3.51 15a9 9 0 1 0 2.13-9.36L1 10" })] }));
// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
/** Safely cast a config record value to string. */
function str(val, fallback = '') {
    if (typeof val === 'string')
        return val;
    return fallback;
}
/** Safely cast a config record value to number. */
function num(val, fallback) {
    if (typeof val === 'number')
        return val;
    if (typeof val === 'string') {
        const n = Number(val);
        if (!Number.isNaN(n))
            return n;
    }
    return fallback;
}
/** Safely cast a config record value to string array. */
function strArr(val, fallback) {
    if (Array.isArray(val))
        return val.map(String);
    return fallback;
}
/** Parse escalation categories from raw config. */
function parseEscalationCategories(raw) {
    const defaults = defaultEscalationCategories();
    if (!raw || typeof raw !== 'object')
        return defaults;
    const obj = raw;
    for (const cat of ESCALATION_CATEGORIES) {
        const entry = obj[cat.id];
        if (entry && typeof entry === 'object') {
            const e = entry;
            defaults[cat.id] = {
                enabled: typeof e.enabled === 'boolean' ? e.enabled : true,
                email: typeof e.email === 'string' ? e.email : '',
                keywords: Array.isArray(e.keywords) ? e.keywords.map(String) : [...cat.defaultKeywords],
            };
        }
    }
    return defaults;
}
/** Read a config value trying snake_case first, then camelCase fallback. */
function cfgVal(cfg, snake, camel) {
    return cfg[snake] !== undefined ? cfg[snake] : cfg[camel];
}
/** Build form state from the raw config record. */
function configToForm(cfg) {
    if (!cfg)
        return { ...DEFAULTS, escalationCategories: defaultEscalationCategories() };
    return {
        brandName: str(cfgVal(cfg, 'brand_name', 'brandName'), DEFAULTS.brandName),
        brandVoice: str(cfgVal(cfg, 'brand_voice', 'brandVoice'), DEFAULTS.brandVoice),
        formality: str(cfgVal(cfg, 'formality_level', 'formality'), DEFAULTS.formality),
        responseLength: str(cfgVal(cfg, 'response_length', 'responseLength'), DEFAULTS.responseLength),
        returnWindow: num(cfgVal(cfg, 'return_window', 'returnWindow'), DEFAULTS.returnWindow),
        refundPolicy: str(cfgVal(cfg, 'return_policy', 'refundPolicy'), DEFAULTS.refundPolicy),
        shippingPolicy: str(cfgVal(cfg, 'shipping_info', 'shippingPolicy'), DEFAULTS.shippingPolicy),
        escalationThreshold: num(cfgVal(cfg, 'escalation_threshold', 'escalationThreshold'), DEFAULTS.escalationThreshold),
        escalationCategories: parseEscalationCategories(cfg.escalation_categories ?? cfg.escalationCategories),
        idleTimeoutMinutes: num(cfgVal(cfg, 'idle_timeout_minutes', 'idleTimeoutMinutes'), DEFAULTS.idleTimeoutMinutes),
        maxTurns: num(cfgVal(cfg, 'max_ai_turns_before_escalation', 'maxTurns'), DEFAULTS.maxTurns),
        customInstructions: str(cfgVal(cfg, 'custom_instructions', 'customInstructions'), DEFAULTS.customInstructions),
        primaryLanguage: str(cfgVal(cfg, 'primary_language', 'primaryLanguage'), DEFAULTS.primaryLanguage),
        supportedLanguages: strArr(cfgVal(cfg, 'additional_languages', 'supportedLanguages'), DEFAULTS.supportedLanguages),
    };
}
/** Deep compare two escalation categories state objects. */
function escalationCategoriesEqual(a, b) {
    const keysA = Object.keys(a);
    const keysB = Object.keys(b);
    if (keysA.length !== keysB.length)
        return false;
    for (const k of keysA) {
        const ca = a[k];
        const cb = b[k];
        if (!ca || !cb)
            return false;
        if (ca.enabled !== cb.enabled)
            return false;
        if (ca.email !== cb.email)
            return false;
        if (ca.keywords.length !== cb.keywords.length)
            return false;
        if (ca.keywords.some((kw, i) => kw !== cb.keywords[i]))
            return false;
    }
    return true;
}
/** Compute fields that differ between two form states. */
/** Map camelCase form keys to snake_case backend field names. */
const FORM_TO_BACKEND = {
    brandName: 'brand_name',
    brandVoice: 'brand_voice',
    formality: 'formality_level',
    responseLength: 'response_length',
    returnWindow: 'return_window',
    refundPolicy: 'return_policy',
    shippingPolicy: 'shipping_info',
    escalationThreshold: 'escalation_threshold',
    escalationCategories: 'escalation_categories',
    idleTimeoutMinutes: 'idle_timeout_minutes',
    maxTurns: 'max_ai_turns_before_escalation',
    customInstructions: 'custom_instructions',
    primaryLanguage: 'primary_language',
    supportedLanguages: 'additional_languages',
};
function diffForm(original, current) {
    const changes = {};
    for (const key of Object.keys(current)) {
        const backendKey = FORM_TO_BACKEND[key] || key;
        if (key === 'escalationCategories') {
            if (!escalationCategoriesEqual(original.escalationCategories, current.escalationCategories)) {
                changes[backendKey] = current.escalationCategories;
            }
            continue;
        }
        const origVal = original[key];
        const curVal = current[key];
        if (Array.isArray(origVal) && Array.isArray(curVal)) {
            if (origVal.length !== curVal.length || origVal.some((v, i) => v !== curVal[i])) {
                changes[backendKey] = curVal;
            }
        }
        else if (origVal !== curVal) {
            changes[backendKey] = curVal;
        }
    }
    return changes;
}
// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------
export const ConfigurationPage = () => {
    const { apiFetch, onNotify, refreshActivationStatus, configRefreshKey } = useAppContext();
    const configResult = useConfig(apiFetch);
    const { updateConfig: saveConfig, loading: saving, error: saveError, clearError: clearSaveError } = useUpdateConfig(apiFetch);
    // KA-7: Config field suggestions from KB analysis
    const suggestionsResult = useConfigSuggestions(apiFetch);
    const suggestions = suggestionsResult.data ?? {};
    // Named configurations (C3) — WI #266 delete + WI #267 timestamps
    const namedResult = useNamedConfigs(apiFetch);
    const { saveNamed, loading: savingNamed } = useSaveNamedConfig(apiFetch);
    const { activateNamed, loading: activatingNamed } = useActivateNamedConfig(apiFetch);
    const { deleteNamed, loading: deletingNamed } = useDeleteNamedConfig(apiFetch);
    const [showSaveModal, setShowSaveModal] = useState(false);
    const [saveAsName, setSaveAsName] = useState('');
    const computedColorScheme = useComputedColorScheme('dark');
    const isDark = computedColorScheme === 'dark';
    // Form state
    const [form, setForm] = useState({ ...DEFAULTS });
    const [hasChanges, setHasChanges] = useState(false);
    // Snapshot of the server state (used for discard and diff)
    const serverFormRef = useRef({ ...DEFAULTS });
    // Config-vs-KB conflict warnings (SPEC-1715)
    const [configConflicts, setConfigConflicts] = useState([]);
    // Escalation category expand/collapse state
    const [expandedCategories, setExpandedCategories] = useState({});
    // Keyword input buffers (one per category)
    const [keywordInputs, setKeywordInputs] = useState({});
    // Re-fetch config when sidebar Discard triggers a configRefreshKey change (D50)
    useEffect(() => {
        if (configRefreshKey > 0)
            configResult.refetch();
    }, [configRefreshKey]); // eslint-disable-line react-hooks/exhaustive-deps
    // Initialize form from loaded config
    useEffect(() => {
        if (configResult.data?.config) {
            const loaded = configToForm(configResult.data.config);
            setForm(loaded);
            serverFormRef.current = loaded;
            setHasChanges(false);
        }
    }, [configResult.data]);
    // Track changes
    const updateField = (key, value) => {
        setForm((prev) => {
            const next = { ...prev, [key]: value };
            // Check if anything differs from server state
            const diff = diffForm(serverFormRef.current, next);
            setHasChanges(Object.keys(diff).length > 0);
            return next;
        });
    };
    /** Update a single field within one escalation category. */
    const updateCategory = (catId, field, value) => {
        setForm((prev) => {
            const cats = { ...prev.escalationCategories };
            cats[catId] = { ...cats[catId], [field]: value };
            const next = { ...prev, escalationCategories: cats };
            const diff = diffForm(serverFormRef.current, next);
            setHasChanges(Object.keys(diff).length > 0);
            return next;
        });
    };
    /** Add a keyword to a category (no duplicates, no overlap with other categories). */
    const addKeyword = (catId, keyword) => {
        const kw = keyword.trim().toLowerCase();
        if (!kw)
            return;
        // Check if keyword already exists in this category
        if (form.escalationCategories[catId]?.keywords.includes(kw))
            return;
        // Check overlap with other categories
        for (const [otherId, otherCfg] of Object.entries(form.escalationCategories)) {
            if (otherId !== catId && otherCfg.keywords.includes(kw)) {
                // Silently skip — keyword belongs to another category
                return;
            }
        }
        const current = form.escalationCategories[catId]?.keywords || [];
        updateCategory(catId, 'keywords', [...current, kw]);
    };
    /** Remove a keyword from a category. */
    const removeKeyword = (catId, keyword) => {
        const current = form.escalationCategories[catId]?.keywords || [];
        updateCategory(catId, 'keywords', current.filter((k) => k !== keyword));
    };
    /** Reset keywords for a category to its defaults. */
    const resetCategoryKeywords = (catId) => {
        const cat = ESCALATION_CATEGORIES.find((c) => c.id === catId);
        if (cat) {
            updateCategory(catId, 'keywords', [...cat.defaultKeywords]);
        }
    };
    /** Toggle a category expand/collapse. */
    const toggleCategory = (catId) => {
        setExpandedCategories((prev) => ({ ...prev, [catId]: !prev[catId] }));
    };
    const handleDiscard = () => {
        setForm({ ...serverFormRef.current });
        setHasChanges(false);
    };
    const handleSave = async () => {
        const changes = diffForm(serverFormRef.current, form);
        if (Object.keys(changes).length === 0)
            return false;
        const result = await saveConfig(changes);
        if (result?.success) {
            // Update server snapshot so discard reflects new saved state
            serverFormRef.current = { ...form };
            setHasChanges(false);
            configResult.refetch();
            refreshActivationStatus();
            // SPEC-1715: Check for config-vs-KB conflicts after save
            // Fire-and-forget — don't block save on this check
            const policyFields = {
                returnPolicy: form.refundPolicy,
                shippingInfo: form.shippingPolicy,
                brandVoice: form.brandVoice,
            };
            if (Object.values(policyFields).some((v) => v)) {
                apiFetch('/api/admin/knowledge/scan/config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(policyFields),
                })
                    .then((r) => r.ok ? r.json() : null)
                    .then((data) => {
                    if (data?.conflicts?.length) {
                        setConfigConflicts(data.conflicts.map((c) => ({
                            configField: c.configField,
                            configValue: c.configValue,
                            articleTitle: c.articleTitle,
                            conflictingFacts: c.conflictingFacts || [],
                        })));
                    }
                    else {
                        setConfigConflicts([]);
                    }
                })
                    .catch(() => { });
            }
            return true;
        }
        else {
            const detail = result?.error || saveError || 'Failed to save configuration.';
            onNotify(`Failed to save: ${detail}`, 'error');
            return false;
        }
    };
    const { onBlur: autoSaveOnBlur, saveCount } = useAutoSaveDraft({ save: handleSave });
    // Named configuration handlers (WI #266, #267)
    const handleSaveNamed = async () => {
        const name = saveAsName.trim();
        if (!name)
            return;
        const result = await saveNamed(name);
        if (result) {
            setShowSaveModal(false);
            setSaveAsName('');
            onNotify(`Configuration "${name}" saved.`, 'success');
            namedResult.refetch();
        }
        else {
            onNotify('Failed to save named configuration.', 'error');
        }
    };
    const handleActivateNamed = async (name) => {
        const result = await activateNamed(name);
        if (result) {
            onNotify(`Configuration "${name}" activated.`, 'success');
            namedResult.refetch();
            configResult.refetch();
            refreshActivationStatus();
        }
        else {
            onNotify(`Failed to activate configuration "${name}".`, 'error');
        }
    };
    const handleDeleteNamed = async (name) => {
        const ok = await deleteNamed(name);
        if (ok) {
            onNotify(`Configuration "${name}" deleted.`, 'success');
            namedResult.refetch();
        }
        else {
            onNotify(`Failed to delete configuration "${name}".`, 'error');
        }
    };
    /** Format ISO date to readable relative/absolute string. */
    const formatDate = (iso) => {
        try {
            const d = new Date(iso);
            const now = new Date();
            const diffMs = now.getTime() - d.getTime();
            const diffMins = Math.floor(diffMs / 60000);
            if (diffMins < 1)
                return 'Just now';
            if (diffMins < 60)
                return `${diffMins}m ago`;
            const diffHrs = Math.floor(diffMins / 60);
            if (diffHrs < 24)
                return `${diffHrs}h ago`;
            const diffDays = Math.floor(diffHrs / 24);
            if (diffDays < 7)
                return `${diffDays}d ago`;
            return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: d.getFullYear() !== now.getFullYear() ? 'numeric' : undefined });
        }
        catch {
            return iso;
        }
    };
    // Loading state
    if (configResult.loading && !configResult.data) {
        return _jsx(LoadingState, { text: "Loading configuration" });
    }
    // Error state
    if (configResult.error && !configResult.data) {
        return (_jsxs(Alert, { color: "red", variant: "light", title: "Failed to load configuration", children: [_jsx(Text, { size: "sm", children: configResult.error }), _jsx(Button, { mt: "sm", size: "xs", variant: "light", onClick: configResult.refetch, children: "Retry" })] }));
    }
    return (_jsxs(Stack, { gap: "lg", children: [_jsxs("div", { children: [_jsxs(Group, { justify: "space-between", align: "center", children: [_jsx(Title, { order: 2, children: "Agent configuration" }), _jsx(AutoSaveIndicator, { saveCount: saveCount })] }), _jsx(Text, { c: "dimmed", size: "sm", children: "Fine-tune your AI agent's behavior" })] }), saveError && (_jsx(Alert, { color: "red", variant: "light", title: "Save failed", withCloseButton: true, onClose: clearSaveError, children: _jsx(Text, { size: "sm", children: saveError }) })), configConflicts.length > 0 && (_jsxs(Alert, { color: "yellow", variant: "light", title: "Configuration conflicts with knowledge base", withCloseButton: true, onClose: () => setConfigConflicts([]), children: [_jsx(Text, { size: "sm", mb: "xs", children: "The following configuration fields conflict with knowledge base articles. Configuration values take priority, but you may want to update the articles." }), configConflicts.map((c, i) => (_jsxs(Text, { size: "sm", c: "dimmed", mb: 2, children: [_jsx(Text, { span: true, fw: 600, c: "dark", children: c.configField }), " conflicts with article \"", c.articleTitle, "\"", c.conflictingFacts.length > 0 && ` — ${c.conflictingFacts[0]}`] }, i)))] })), (() => {
                const configs = namedResult.data?.configs ?? [];
                if (namedResult.loading && !namedResult.data)
                    return null;
                const activeConfig = configs.find((c) => c.isActive);
                return (_jsxs(Paper, { p: "lg", radius: "md", withBorder: true, children: [_jsxs(Group, { justify: "space-between", mb: configs.length > 0 ? 'md' : 0, children: [_jsxs(Text, { fw: 600, children: ["Saved configurations", _jsx(HelpTooltip, { text: "Save snapshots of your current configuration and switch between them. The active configuration is applied to your AI agent.", docLink: `${DOCS_BASE}/named-configs` })] }), _jsx(Button, { size: "xs", variant: "light", color: ACTION_BLUE, onClick: () => { setSaveAsName(''); setShowSaveModal(true); }, disabled: savingNamed, children: "Save current as\u2026" })] }), configs.length === 0 ? (_jsx(Text, { size: "sm", c: "dimmed", children: "No saved configurations yet. Click \"Save current as\u2026\" to create a reusable snapshot." })) : (_jsxs(Table, { verticalSpacing: "xs", highlightOnHover: true, children: [_jsx(Table.Thead, { children: _jsxs(Table.Tr, { children: [_jsx(Table.Th, { children: "Name" }), _jsx(Table.Th, { children: "Saved" }), _jsx(Table.Th, { children: "Fields" }), _jsx(Table.Th, { style: { width: 140, textAlign: 'right' }, children: "Actions" })] }) }), _jsx(Table.Tbody, { children: configs.map((c) => (_jsxs(Table.Tr, { children: [_jsx(Table.Td, { children: _jsxs(Group, { gap: 8, wrap: "nowrap", children: [_jsx(Text, { size: "sm", fw: c.isActive ? 600 : 400, children: c.name }), c.isActive && _jsx(Badge, { size: "xs", color: "teal", variant: "light", children: "Active" }), c.isDefault && _jsx(Badge, { size: "xs", color: "gray", variant: "light", children: "Default" })] }) }), _jsx(Table.Td, { children: _jsx(Tooltip, { label: new Date(c.createdAt).toLocaleString(), withArrow: true, children: _jsx(Text, { size: "sm", c: "dimmed", children: formatDate(c.createdAt) }) }) }), _jsx(Table.Td, { children: _jsxs(Badge, { size: "sm", variant: "light", color: "gray", children: [c.fieldCount, " fields"] }) }), _jsx(Table.Td, { children: _jsxs(Group, { gap: 4, justify: "flex-end", wrap: "nowrap", children: [!c.isActive && (_jsx(Button, { size: "compact-xs", variant: "light", color: ACTION_BLUE, onClick: () => handleActivateNamed(c.name), loading: activatingNamed, children: "Activate" })), !c.isDefault && !c.isActive && (_jsx(Button, { size: "compact-xs", variant: "light", color: "red", onClick: () => handleDeleteNamed(c.name), loading: deletingNamed, children: "Delete" }))] }) })] }, c.name))) })] })), activeConfig && (_jsxs(Text, { size: "xs", c: "dimmed", mt: "sm", children: ["Active: ", _jsx("strong", { children: activeConfig.name }), " (v", activeConfig.version, ", last saved ", formatDate(activeConfig.createdAt), ")"] }))] }));
            })(), _jsx(Modal, { opened: showSaveModal, onClose: () => setShowSaveModal(false), title: "Save configuration as", size: "sm", centered: true, children: _jsxs(Stack, { gap: "md", children: [_jsx(TextInput, { label: "Configuration name", placeholder: 'e.g. "Holiday", "Black Friday", "Default v2"', value: saveAsName, onChange: (e) => setSaveAsName(e.currentTarget.value), maxLength: 64, "data-autofocus": true, onKeyDown: (e) => {
                                if (e.key === 'Enter' && saveAsName.trim())
                                    handleSaveNamed();
                            } }), saveAsName.trim().toLowerCase() === 'default' && (_jsx(Text, { size: "xs", c: "yellow", children: "This will overwrite the Default configuration snapshot." })), _jsxs(Group, { justify: "flex-end", children: [_jsx(Button, { variant: "default", onClick: () => setShowSaveModal(false), children: "Cancel" }), _jsx(Button, { color: ACTION_BLUE, onClick: handleSaveNamed, disabled: !saveAsName.trim(), loading: savingNamed, children: "Save configuration" })] })] }) }), _jsxs(Stack, { gap: "lg", onBlur: autoSaveOnBlur, children: [_jsxs(Paper, { p: "lg", radius: "md", withBorder: true, children: [_jsxs(Text, { fw: 600, mb: "xs", children: ["Escalation ", _jsx(HelpTooltip, { text: "Configure when and how conversations are handed off to human team members.", docLink: `${DOCS_BASE}/escalation-rules` })] }), _jsx(Text, { size: "xs", c: "dimmed", mb: "md", children: "Configure escalation categories, trigger keywords, and optional notification emails. Each category routes to a different team member with its own keyword set." }), _jsxs(Stack, { gap: "md", children: [_jsxs("div", { children: [_jsx(Text, { size: "sm", fw: 500, mb: 8, children: "Escalation threshold" }), _jsx(Slider, { value: form.escalationThreshold, onChange: (val) => updateField('escalationThreshold', val), min: 0, max: 1, step: 0.05, marks: [
                                                    { value: 0, label: _jsx("span", { style: { position: 'relative', left: '50%' }, children: "Conservative" }) },
                                                    { value: 0.5, label: '0.5' },
                                                    { value: 1, label: _jsx("span", { style: { position: 'relative', right: '50%' }, children: "Aggressive" }) },
                                                ], label: (val) => val.toFixed(2), color: ACTION_BLUE, mb: "lg" })] }), ESCALATION_CATEGORIES.map((cat) => {
                                        const catConfig = form.escalationCategories[cat.id] || {
                                            enabled: true,
                                            email: '',
                                            keywords: [...cat.defaultKeywords],
                                        };
                                        const isExpanded = !!expandedCategories[cat.id];
                                        const kwCount = catConfig.keywords.length;
                                        return (_jsxs(Paper, { p: "sm", radius: "sm", style: {
                                                backgroundColor: isDark ? tokens.page : '#f8f9fa',
                                                border: `1px solid ${isDark ? tokens.border : '#dee2e6'}`,
                                                opacity: catConfig.enabled ? 1 : 0.6,
                                            }, children: [_jsxs(Group, { justify: "space-between", wrap: "nowrap", children: [_jsxs(Group, { gap: "sm", wrap: "nowrap", style: { flex: 1, minWidth: 0, cursor: 'pointer' }, onClick: () => toggleCategory(cat.id), children: [_jsx(Switch, { size: "sm", color: ACTION_BLUE, checked: catConfig.enabled, onChange: (e) => {
                                                                        e.stopPropagation();
                                                                        updateCategory(cat.id, 'enabled', e.currentTarget.checked);
                                                                    } }), _jsxs("div", { style: { minWidth: 0 }, children: [_jsxs(Group, { gap: 6, wrap: "nowrap", children: [_jsx(Text, { size: "sm", fw: 600, children: cat.label }), _jsxs(Badge, { size: "xs", variant: "light", color: "gray", children: [kwCount, " keywords"] }), catConfig.email && _jsx(Badge, { size: "xs", variant: "light", color: BRAND_RED, children: String.fromCodePoint(0x2709) })] }), _jsx(Text, { size: "xs", c: "dimmed", truncate: true, children: cat.description })] })] }), _jsx(ActionIcon, { variant: "subtle", size: "sm", onClick: () => toggleCategory(cat.id), color: "gray", children: isExpanded ? _jsx(ChevronUpIcon, {}) : _jsx(ChevronDownIcon, {}) })] }), _jsx(Collapse, { in: isExpanded, children: _jsxs(Stack, { gap: "sm", mt: "sm", children: [_jsx(TextInput, { label: "Notification email (optional)", placeholder: `${cat.id}@yourcompany.com`, size: "sm", value: catConfig.email, onChange: (e) => updateCategory(cat.id, 'email', e.currentTarget.value), disabled: !catConfig.enabled }), _jsxs("div", { children: [_jsxs(Group, { justify: "space-between", mb: 6, children: [_jsx(Text, { size: "sm", fw: 500, children: "Keywords" }), _jsx(Tooltip, { label: "Reset to default keywords", children: _jsx(ActionIcon, { variant: "subtle", size: "xs", color: "gray", onClick: () => resetCategoryKeywords(cat.id), disabled: !catConfig.enabled, children: _jsx(ResetIcon, {}) }) })] }), _jsx(Group, { gap: 4, wrap: "wrap", mb: 8, children: catConfig.keywords.map((kw) => (_jsx(Badge, { size: "sm", variant: "light", color: isDark ? 'gray' : 'dark', rightSection: catConfig.enabled ? (_jsx(ActionIcon, { size: "xs", variant: "transparent", color: "gray", onClick: () => removeKeyword(cat.id, kw), style: { marginLeft: 2 }, children: _jsx(XIcon, {}) })) : null, children: kw }, kw))) }), _jsx(TextInput, { size: "xs", placeholder: "Add keyword and press Enter...", value: keywordInputs[cat.id] || '', onChange: (e) => setKeywordInputs((prev) => ({ ...prev, [cat.id]: e.currentTarget.value })), onKeyDown: (e) => {
                                                                            if (e.key === 'Enter') {
                                                                                e.preventDefault();
                                                                                addKeyword(cat.id, keywordInputs[cat.id] || '');
                                                                                setKeywordInputs((prev) => ({ ...prev, [cat.id]: '' }));
                                                                            }
                                                                        }, disabled: !catConfig.enabled })] })] }) })] }, cat.id));
                                    }), _jsxs(Group, { grow: true, children: [_jsx(NumberInput, { label: _jsxs(_Fragment, { children: ["Idle timeout ", _jsx(HelpTooltip, { text: "Minutes of customer inactivity before the conversation is automatically ended and marked as resolved.", docLink: `${DOCS_BASE}/escalation-settings` })] }), suffix: " minutes", value: form.idleTimeoutMinutes, onChange: (val) => updateField('idleTimeoutMinutes', Number(val) || 30), min: 1, max: 120 }), _jsx(NumberInput, { label: _jsxs(_Fragment, { children: ["Max turns ", _jsx(HelpTooltip, { text: "Maximum number of back-and-forth exchanges before the conversation is automatically ended and marked as resolved.", docLink: `${DOCS_BASE}/escalation-settings` })] }), value: form.maxTurns, onChange: (val) => updateField('maxTurns', Number(val) || 50), min: 1, max: 50 })] })] })] }), _jsxs(Paper, { p: "lg", radius: "md", withBorder: true, children: [_jsxs(Text, { fw: 600, mb: "md", children: ["Agent identity ", _jsx(HelpTooltip, { text: "Define who your AI agent is \u2014 brand name, personality, tone, and special instructions.", docLink: `${DOCS_BASE}/brand-and-tone` })] }), _jsxs(Stack, { gap: "lg", children: [_jsxs("div", { children: [_jsx(Text, { fw: 500, size: "sm", mb: "sm", c: "dimmed", children: "Brand & persona" }), _jsxs(Stack, { gap: "md", children: [_jsx(TextInput, { label: _jsx(LabelWithSuggestion, { label: "Brand name", suggestion: suggestions.brand_name, currentValue: form.brandName, onApply: (v) => updateField('brandName', String(v)) }), placeholder: "Your store or brand name", value: form.brandName, onChange: (e) => updateField('brandName', e.currentTarget.value), required: true }), _jsx(Textarea, { label: _jsx(LabelWithSuggestion, { label: "Brand voice", suggestion: suggestions.brand_voice, currentValue: form.brandVoice, onApply: (v) => updateField('brandVoice', String(v)) }), placeholder: "Describe the personality and tone of your AI agent...", value: form.brandVoice, onChange: (e) => updateField('brandVoice', e.currentTarget.value), minRows: 3, autosize: true, required: true }), _jsxs(Group, { grow: true, children: [_jsx(Select, { label: "Formality", data: [
                                                                    { value: 'casual', label: 'Casual' },
                                                                    { value: 'balanced', label: 'Professional' },
                                                                    { value: 'formal', label: 'Formal' },
                                                                ], value: form.formality, onChange: (val) => updateField('formality', val || 'balanced') }), _jsx(Select, { label: "Response length", data: [
                                                                    { value: 'concise', label: 'Concise' },
                                                                    { value: 'standard', label: 'Moderate' },
                                                                    { value: 'detailed', label: 'Detailed' },
                                                                ], value: form.responseLength, onChange: (val) => updateField('responseLength', val || 'standard') })] })] })] }), _jsxs("div", { children: [_jsx(Text, { fw: 500, size: "sm", mb: "sm", c: "dimmed", children: "Custom instructions" }), _jsx(Textarea, { placeholder: "Provide advisory instructions for the AI agent...", value: form.customInstructions, onChange: (e) => updateField('customInstructions', e.currentTarget.value), minRows: 5, autosize: true, maxRows: 12 }), _jsx(Text, { size: "xs", c: "dimmed", mt: 8, children: "Advisory instructions for the AI agent. Safety rules always take precedence." })] })] })] }), _jsxs(Paper, { p: "lg", radius: "md", withBorder: true, children: [_jsxs(Text, { fw: 600, mb: "md", children: ["Language ", _jsx(HelpTooltip, { text: "Set the primary response language and additional supported languages for multilingual customers.", docLink: `${DOCS_BASE}/languages` })] }), _jsxs(Stack, { gap: "md", children: [_jsx(Select, { label: "Primary language", data: PRIMARY_LANGUAGES, value: form.primaryLanguage, onChange: (val) => updateField('primaryLanguage', val || 'en') }), _jsxs("div", { children: [_jsx(Text, { size: "sm", fw: 500, mb: 8, children: "Supported languages" }), _jsx(Chip.Group, { multiple: true, value: form.supportedLanguages, onChange: (val) => updateField('supportedLanguages', val), children: _jsx(Group, { gap: "xs", wrap: "wrap", children: LANGUAGES.map((lang) => (_jsx(Chip, { value: lang.value, size: "sm", color: ACTION_BLUE, disabled: lang.disabled, styles: lang.disabled ? { label: { opacity: 0.5, cursor: 'not-allowed' } } : undefined, children: lang.label }, lang.value))) }) })] })] })] })] })] }));
};
//# sourceMappingURL=Configuration.js.map