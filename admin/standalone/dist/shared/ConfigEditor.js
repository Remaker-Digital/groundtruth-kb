import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
/**
 * ConfigEditor — Full tenant configuration editor with version history.
 *
 * Provides a comprehensive configuration management interface with:
 *   - Tabbed/grouped layout matching the 9 onboarding groups
 *   - Collapsible sections within each group
 *   - Inline form field editing (same field types as OnboardingWizard)
 *   - Unsaved changes indicator with save/discard actions
 *   - Version history panel (right sidebar or bottom section)
 *   - Diff view between any two versions
 *   - Rollback to a previous version
 *   - Reset to tier defaults
 *
 * API endpoints consumed:
 *   GET    /api/config            — Current resolved config (active or draft)
 *   PUT    /api/config            — Save changes to draft (not live until activated)
 *   GET    /api/config/versions   — Version history list
 *   POST   /api/config/rollback   — Create draft from historical version
 *   POST   /api/config/reset      — Create draft from tier defaults
 *   GET    /api/config/diff       — Diff current overrides vs defaults
 *   GET    /api/config/named      — List named configurations
 *   POST   /api/config/named      — Save current config as named snapshot
 *   POST   /api/config/named/{name}/activate — Load named config as draft
 *   DELETE /api/config/named/{name}          — Delete a named config
 *
 * Props (from shell):
 *   - tenantContext — authenticated tenant information
 *   - apiFetch     — shell-provided fetch wrapper with auth
 *   - onNotify     — shell toast/banner callback
 *
 * Dependencies:
 *   - ../types  — BaseComponentProps, ConfigField, ConfigVersion, ConfigDiff, etc.
 *   - ../hooks  — useConfig, useUpdateConfig, useConfigVersions, useConfigSchema
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { useState, useCallback, useEffect, useMemo } from 'react';
import { useConfig, useUpdateConfig, useConfigVersions, useConfigSchema, } from './hooks';
import { tokens } from './theme/styles';
const CONFIG_GROUPS = [
    {
        key: 'brand_and_tone',
        label: 'Brand & Tone',
        description: 'Brand name, voice personality, and communication style.',
    },
    {
        key: 'ai_behavior',
        label: 'AI behavior',
        description: 'Response formality, length limits, and model behavior.',
    },
    {
        key: 'escalation',
        label: 'Escalation rules',
        description: 'When and how conversations are escalated to human agents.',
    },
    {
        key: 'integrations',
        label: 'Integrations',
        description: 'Shopify, Zendesk, Mailchimp, and third-party service connections.',
    },
    {
        key: 'knowledge_base',
        label: 'Knowledge base',
        description: 'FAQs, product information, and policy documents.',
    },
    {
        key: 'response_policies',
        label: 'Response policies',
        description: 'Business policies, return windows, support hours.',
    },
    {
        key: 'customer_memory',
        label: 'Customer memory',
        description: 'How the AI remembers customers across conversations.',
    },
    {
        key: 'notifications',
        label: 'Notifications',
        description: 'Alert thresholds and notification preferences.',
    },
    {
        key: 'widget_appearance',
        label: 'Widget appearance',
        description: 'Chat widget colors, position, and storefront behavior.',
    },
];
// ---------------------------------------------------------------------------
// Styles
// ---------------------------------------------------------------------------
const s = {
    container: {
        display: 'flex',
        flexDirection: 'column',
        fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
        color: '#1a1a1a',
        height: '100%',
    },
    header: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginBottom: 24,
        flexWrap: 'wrap',
        gap: 12,
    },
    title: {
        fontSize: 24,
        fontWeight: 600,
        margin: 0,
    },
    headerActions: {
        display: 'flex',
        gap: 8,
        flexWrap: 'wrap',
        alignItems: 'center',
    },
    unsavedBadge: {
        display: 'inline-flex',
        alignItems: 'center',
        gap: 6,
        padding: '5px 12px',
        backgroundColor: '#fef3c7',
        color: '#92400e',
        borderRadius: 6,
        fontSize: 13,
        fontWeight: 500,
    },
    layout: {
        display: 'flex',
        gap: 24,
        flexGrow: 1,
        minHeight: 0,
    },
    mainPanel: {
        flex: 1,
        minWidth: 0,
        overflowY: 'auto',
    },
    sidebar: {
        width: 320,
        flexShrink: 0,
        overflowY: 'auto',
        borderLeft: '1px solid #e5e5e5',
        paddingLeft: 24,
    },
    // Tabs
    tabBar: {
        display: 'flex',
        flexWrap: 'wrap',
        gap: 2,
        marginBottom: 24,
        borderBottom: '1px solid #e5e5e5',
        paddingBottom: 0,
    },
    tab: (active) => ({
        padding: '8px 16px',
        fontSize: 13,
        fontWeight: active ? 600 : 400,
        color: active ? tokens.action : '#555',
        backgroundColor: 'transparent',
        border: 'none',
        borderBottom: active ? `2px solid ${tokens.action}` : '2px solid transparent',
        cursor: 'pointer',
        whiteSpace: 'nowrap',
        marginBottom: -1,
        transition: 'color 0.15s ease, border-color 0.15s ease',
    }),
    // Field sections
    sectionHeader: (collapsed) => ({
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '12px 0',
        cursor: 'pointer',
        userSelect: 'none',
        borderBottom: collapsed ? 'none' : '1px solid #f0f0f0',
    }),
    sectionTitle: {
        fontSize: 16,
        fontWeight: 600,
        color: '#1a1a1a',
        margin: 0,
    },
    sectionDescription: {
        fontSize: 13,
        color: '#777',
        margin: '4px 0 0 0',
    },
    chevron: (collapsed) => ({
        fontSize: 12,
        color: '#999',
        transform: collapsed ? 'rotate(-90deg)' : 'rotate(0deg)',
        transition: 'transform 0.15s ease',
    }),
    fieldsContainer: {
        display: 'flex',
        flexDirection: 'column',
        gap: 18,
        padding: '16px 0 24px 0',
    },
    fieldGroup: {
        display: 'flex',
        flexDirection: 'column',
        gap: 5,
    },
    label: {
        fontSize: 14,
        fontWeight: 500,
        color: '#333',
    },
    description: {
        fontSize: 12,
        color: '#888',
        margin: 0,
        lineHeight: 1.4,
    },
    input: {
        padding: '8px 12px',
        fontSize: 14,
        border: '1px solid #d0d0d0',
        borderRadius: 6,
        outline: 'none',
        backgroundColor: '#fff',
        color: '#1a1a1a',
        width: '100%',
        boxSizing: 'border-box',
    },
    textarea: {
        padding: '8px 12px',
        fontSize: 14,
        border: '1px solid #d0d0d0',
        borderRadius: 6,
        outline: 'none',
        backgroundColor: '#fff',
        color: '#1a1a1a',
        minHeight: 72,
        resize: 'vertical',
        width: '100%',
        boxSizing: 'border-box',
        fontFamily: 'inherit',
    },
    select: {
        padding: '8px 12px',
        fontSize: 14,
        border: '1px solid #d0d0d0',
        borderRadius: 6,
        outline: 'none',
        backgroundColor: '#fff',
        color: '#1a1a1a',
        width: '100%',
        boxSizing: 'border-box',
    },
    checkboxRow: {
        display: 'flex',
        alignItems: 'center',
        gap: 10,
        cursor: 'pointer',
    },
    checkbox: {
        width: 18,
        height: 18,
        accentColor: tokens.action,
        cursor: 'pointer',
    },
    colorRow: {
        display: 'flex',
        alignItems: 'center',
        gap: 12,
    },
    colorSwatch: {
        width: 36,
        height: 36,
        border: '1px solid #d0d0d0',
        borderRadius: 6,
        padding: 2,
        cursor: 'pointer',
        backgroundColor: '#fff',
    },
    tierBadge: {
        display: 'inline-block',
        fontSize: 10,
        fontWeight: 600,
        textTransform: 'uppercase',
        padding: '2px 6px',
        borderRadius: 4,
        backgroundColor: '#f0f0f0',
        color: '#888',
        marginLeft: 8,
    },
    // Buttons
    btnPrimary: {
        padding: '8px 20px',
        fontSize: 14,
        fontWeight: 600,
        backgroundColor: tokens.action,
        color: tokens.white,
        border: 'none',
        borderRadius: 6,
        cursor: 'pointer',
    },
    btnSecondary: {
        padding: '8px 20px',
        fontSize: 14,
        fontWeight: 500,
        backgroundColor: 'transparent',
        color: '#555',
        border: '1px solid #d0d0d0',
        borderRadius: 6,
        cursor: 'pointer',
    },
    btnDanger: {
        padding: '8px 16px',
        fontSize: 13,
        fontWeight: 500,
        backgroundColor: '#fef2f2',
        color: '#991b1b',
        border: '1px solid #fecaca',
        borderRadius: 6,
        cursor: 'pointer',
    },
    btnSmall: {
        padding: '4px 10px',
        fontSize: 12,
        fontWeight: 500,
        backgroundColor: 'transparent',
        color: '#555',
        border: '1px solid #d0d0d0',
        borderRadius: 4,
        cursor: 'pointer',
    },
    disabled: {
        opacity: 0.6,
        cursor: 'not-allowed',
    },
    // Version history sidebar
    sidebarTitle: {
        fontSize: 16,
        fontWeight: 600,
        marginBottom: 16,
        color: '#1a1a1a',
    },
    versionItem: (selected) => ({
        padding: '10px 12px',
        borderRadius: 6,
        backgroundColor: selected ? '#fef2f2' : 'transparent',
        border: selected ? '1px solid #fecaca' : '1px solid transparent',
        cursor: 'pointer',
        marginBottom: 6,
        transition: 'background-color 0.15s ease',
    }),
    versionNumber: {
        fontSize: 14,
        fontWeight: 600,
        color: '#1a1a1a',
    },
    versionMeta: {
        fontSize: 12,
        color: '#888',
        margin: '2px 0 0 0',
    },
    diffContainer: {
        marginTop: 16,
        padding: 16,
        backgroundColor: '#fafafa',
        borderRadius: 8,
        border: '1px solid #e5e5e5',
    },
    diffTitle: {
        fontSize: 14,
        fontWeight: 600,
        marginBottom: 12,
        color: '#1a1a1a',
    },
    diffRow: {
        display: 'flex',
        flexDirection: 'column',
        gap: 2,
        padding: '8px 0',
        borderBottom: '1px solid #eee',
    },
    diffField: {
        fontSize: 13,
        fontWeight: 600,
        color: '#333',
    },
    diffBefore: {
        fontSize: 12,
        color: '#991b1b',
        fontFamily: "'JetBrains Mono', monospace",
        backgroundColor: '#fef2f2',
        padding: '2px 6px',
        borderRadius: 3,
        wordBreak: 'break-all',
    },
    diffAfter: {
        fontSize: 12,
        color: '#166534',
        fontFamily: "'JetBrains Mono', monospace",
        backgroundColor: '#f0fdf4',
        padding: '2px 6px',
        borderRadius: 3,
        wordBreak: 'break-all',
    },
    loading: {
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        padding: 64,
        fontSize: 14,
        color: '#888',
    },
    error: {
        padding: '16px 20px',
        backgroundColor: '#fef2f2',
        border: '1px solid #fecaca',
        borderRadius: 8,
        color: '#991b1b',
        fontSize: 14,
        lineHeight: 1.5,
    },
    empty: {
        padding: '32px 20px',
        textAlign: 'center',
        color: '#888',
        fontSize: 14,
    },
    changedDot: {
        display: 'inline-block',
        width: 6,
        height: 6,
        borderRadius: '50%',
        backgroundColor: '#f59e0b',
        marginLeft: 6,
    },
};
// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function formatValue(v) {
    if (v === null || v === undefined)
        return '(empty)';
    if (typeof v === 'boolean')
        return v ? 'true' : 'false';
    if (typeof v === 'object')
        return JSON.stringify(v);
    return String(v);
}
function formatDate(iso) {
    try {
        const d = new Date(iso);
        return d.toLocaleDateString(undefined, {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
    }
    catch {
        return iso;
    }
}
const FieldEditor = ({ field, value, originalValue, onChange, disabled, tenantTier, }) => {
    const tierOrder = ['trial', 'starter', 'professional', 'enterprise'];
    const tenantIdx = tierOrder.indexOf(tenantTier);
    const fieldIdx = field.tierGate ? tierOrder.indexOf(field.tierGate) : 0;
    const isLocked = fieldIdx > tenantIdx;
    const effectiveDisabled = disabled || isLocked;
    const isChanged = JSON.stringify(value) !== JSON.stringify(originalValue);
    const handleChange = useCallback((newVal) => {
        if (!effectiveDisabled)
            onChange(field.key, newVal);
    }, [field.key, onChange, effectiveDisabled]);
    const renderControl = () => {
        const ft = field.type;
        switch (ft) {
            case 'boolean':
                return (_jsxs("label", { style: s.checkboxRow, children: [_jsx("input", { type: "checkbox", style: s.checkbox, checked: Boolean(value), onChange: (e) => handleChange(e.target.checked), disabled: effectiveDisabled }), _jsx("span", { style: { fontSize: 14, color: effectiveDisabled ? '#aaa' : '#333' }, children: Boolean(value) ? 'Enabled' : 'Disabled' })] }));
            case 'select':
                return (_jsxs("select", { style: {
                        ...s.select,
                        ...(effectiveDisabled ? s.disabled : {}),
                    }, value: String(value ?? ''), onChange: (e) => handleChange(e.target.value), disabled: effectiveDisabled, children: [_jsx("option", { value: "", children: "-- Select --" }), (field.options ?? []).map((opt) => (_jsx("option", { value: opt.value, children: opt.label }, opt.value)))] }));
            case 'color':
                return (_jsxs("div", { style: s.colorRow, children: [_jsx("input", { type: "color", style: s.colorSwatch, value: String(value ?? '#000000'), onChange: (e) => handleChange(e.target.value), disabled: effectiveDisabled }), _jsx("span", { style: {
                                fontSize: 13,
                                fontFamily: "'JetBrains Mono', monospace",
                                color: '#555',
                            }, children: String(value ?? '#000000') })] }));
            case 'textarea':
                return (_jsx("textarea", { style: {
                        ...s.textarea,
                        ...(effectiveDisabled ? s.disabled : {}),
                    }, value: String(value ?? ''), onChange: (e) => handleChange(e.target.value), disabled: effectiveDisabled, rows: 4 }));
            case 'number':
            case 'integer':
            case 'float':
                return (_jsx("input", { type: "number", style: {
                        ...s.input,
                        ...(effectiveDisabled ? s.disabled : {}),
                    }, value: value !== undefined && value !== null ? String(value) : '', onChange: (e) => handleChange(e.target.value === '' ? null : Number(e.target.value)), step: field.type === 'float' ? '0.1' : '1', disabled: effectiveDisabled }));
            case 'json':
            case 'object':
                return (_jsx("textarea", { style: {
                        ...s.textarea,
                        fontFamily: "'JetBrains Mono', monospace",
                        fontSize: 13,
                        ...(effectiveDisabled ? s.disabled : {}),
                    }, value: typeof value === 'string'
                        ? value
                        : value != null
                            ? JSON.stringify(value, null, 2)
                            : '', onChange: (e) => {
                        try {
                            handleChange(JSON.parse(e.target.value));
                        }
                        catch {
                            handleChange(e.target.value);
                        }
                    }, disabled: effectiveDisabled, rows: 5 }));
            case 'string':
            default:
                return (_jsx("input", { type: "text", style: {
                        ...s.input,
                        ...(effectiveDisabled ? s.disabled : {}),
                    }, value: String(value ?? ''), onChange: (e) => handleChange(e.target.value), disabled: effectiveDisabled }));
        }
    };
    return (_jsxs("div", { style: s.fieldGroup, children: [_jsxs("label", { style: s.label, children: [field.label, field.validation?.required && (_jsx("span", { style: { color: '#d73a49', marginLeft: 2 }, title: "Required", children: "*" })), isLocked && field.tierGate && (_jsxs("span", { style: s.tierBadge, children: [field.tierGate, "+"] })), isChanged && _jsx("span", { style: s.changedDot, title: "Modified" })] }), field.description && _jsx("p", { style: s.description, children: field.description }), renderControl()] }));
};
// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------
export const ConfigEditor = ({ tenantContext, apiFetch, onNotify, }) => {
    // ---- state ----
    const [activeTab, setActiveTab] = useState(CONFIG_GROUPS[0].key);
    const [collapsedSections, setCollapsedSections] = useState(new Set());
    const [editedValues, setEditedValues] = useState({});
    const [originalValues, setOriginalValues] = useState({});
    const [saving, setSaving] = useState(false);
    const [resetting, setResetting] = useState(false);
    const [selectedVersion, setSelectedVersion] = useState(null);
    const [diffData, setDiffData] = useState(null);
    const [diffLoading, setDiffLoading] = useState(false);
    const [rollingBack, setRollingBack] = useState(false);
    // ---- hooks ----
    const { data: configData, loading: configLoading, error: configError, refetch: refetchConfig } = useConfig(apiFetch);
    const { updateConfig, loading: updateLoading, error: updateError } = useUpdateConfig(apiFetch);
    const { data: schemaData, loading: schemaLoading } = useConfigSchema(apiFetch);
    const { data: versionsData, loading: versionsLoading, refetch: refetchVersions, } = useConfigVersions(apiFetch);
    // ---- derive all fields from schema ----
    const allFields = useMemo(() => {
        if (!schemaData?.fields)
            return [];
        return schemaData.fields.map((raw) => ({
            key: String(raw.key ?? raw.field_name ?? ''),
            label: String(raw.label ?? raw.field_name ?? ''),
            description: String(raw.description ?? raw.tooltip ?? ''),
            type: (raw.type ?? raw.field_type ?? 'string'),
            defaultValue: raw.default_value ?? raw.defaultValue ?? null,
            currentValue: raw.current_value ?? raw.currentValue ?? null,
            options: Array.isArray(raw.options)
                ? raw.options.map((o) => {
                    if (typeof o === 'object' && o !== null && 'value' in o) {
                        return o;
                    }
                    return { value: String(o), label: String(o) };
                })
                : undefined,
            tierGate: (raw.tier_gate ?? raw.tierGate ?? undefined),
            stepOrder: Number(raw.step_order ?? raw.stepOrder ?? 0),
            group: String(raw.group ?? raw.onboarding_step ?? 'other'),
        }));
    }, [schemaData]);
    // Group fields by config group
    const fieldsByGroup = useMemo(() => {
        const map = {};
        for (const g of CONFIG_GROUPS) {
            map[g.key] = [];
        }
        for (const f of allFields) {
            const groupKey = f.group;
            if (map[groupKey]) {
                map[groupKey].push(f);
            }
            else {
                // Fields that don't match a known group — assign to closest match
                // or default to the first group
                const match = CONFIG_GROUPS.find((g) => groupKey.includes(g.key) || g.key.includes(groupKey));
                const target = match ? match.key : CONFIG_GROUPS[0].key;
                if (!map[target])
                    map[target] = [];
                map[target].push(f);
            }
        }
        // Sort each group by stepOrder
        for (const key of Object.keys(map)) {
            map[key].sort((a, b) => a.stepOrder - b.stepOrder);
        }
        return map;
    }, [allFields]);
    // ---- initialise edited values from config ----
    useEffect(() => {
        if (!configData?.config)
            return;
        const values = {};
        // Merge config data with field defaults
        for (const f of allFields) {
            values[f.key] =
                configData.config[f.key] !== undefined
                    ? configData.config[f.key]
                    : f.currentValue ?? f.defaultValue;
        }
        setEditedValues(values);
        setOriginalValues({ ...values });
    }, [configData, allFields]);
    // ---- derive versions list ----
    const versions = useMemo(() => {
        if (!versionsData?.versions)
            return [];
        return versionsData.versions.map((v) => ({
            version: Number(v.version ?? 0),
            createdAt: String(v.created_at ?? v.createdAt ?? ''),
            actor: String(v.actor ?? 'system'),
            changeCount: Number(v.change_count ?? v.changeCount ?? 0),
        }));
    }, [versionsData]);
    // ---- unsaved changes ----
    const changedKeys = useMemo(() => {
        const keys = [];
        for (const key of Object.keys(editedValues)) {
            if (JSON.stringify(editedValues[key]) !== JSON.stringify(originalValues[key])) {
                keys.push(key);
            }
        }
        return keys;
    }, [editedValues, originalValues]);
    const hasUnsavedChanges = changedKeys.length > 0;
    // ---- handlers ----
    const handleFieldChange = useCallback((key, value) => {
        setEditedValues((prev) => ({ ...prev, [key]: value }));
    }, []);
    const handleSave = useCallback(async () => {
        if (saving || updateLoading || !hasUnsavedChanges)
            return;
        setSaving(true);
        // Build partial update with only changed fields
        const changes = {};
        for (const key of changedKeys) {
            changes[key] = editedValues[key];
        }
        try {
            const result = await updateConfig(changes);
            if (result?.success) {
                onNotify(`Changes saved to draft (${result.changes?.length ?? changedKeys.length} field${changedKeys.length === 1 ? '' : 's'}) — activate to go live.`, 'success');
                setOriginalValues({ ...editedValues });
                refetchConfig();
                refetchVersions();
            }
            else {
                onNotify(result?.error || result?.message || 'Failed to save configuration.', 'error');
            }
        }
        catch {
            onNotify('An unexpected error occurred while saving.', 'error');
        }
        finally {
            setSaving(false);
        }
    }, [
        saving,
        updateLoading,
        hasUnsavedChanges,
        changedKeys,
        editedValues,
        updateConfig,
        onNotify,
        refetchConfig,
        refetchVersions,
    ]);
    const handleDiscard = useCallback(() => {
        setEditedValues({ ...originalValues });
    }, [originalValues]);
    const handleReset = useCallback(async () => {
        if (resetting)
            return;
        const confirmed = window.confirm('Reset all configuration to tier defaults? This will discard all custom overrides and cannot be undone.');
        if (!confirmed)
            return;
        setResetting(true);
        try {
            const resp = await apiFetch('/api/config/reset', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({}),
            });
            if (!resp.ok) {
                const body = await resp.text().catch(() => '');
                throw new Error(`${resp.status}: ${body}`);
            }
            onNotify('Draft reset to tier defaults — activate to go live.', 'success');
            refetchConfig();
            refetchVersions();
        }
        catch (err) {
            const msg = err instanceof Error ? err.message : 'Reset failed';
            onNotify(`Reset failed: ${msg}`, 'error');
        }
        finally {
            setResetting(false);
        }
    }, [resetting, apiFetch, onNotify, refetchConfig, refetchVersions]);
    const handleSelectVersion = useCallback(async (version) => {
        if (selectedVersion === version) {
            setSelectedVersion(null);
            setDiffData(null);
            return;
        }
        setSelectedVersion(version);
        setDiffLoading(true);
        setDiffData(null);
        try {
            const resp = await apiFetch(`/api/config/diff?version=${version}`);
            if (!resp.ok) {
                throw new Error(`${resp.status}`);
            }
            const data = await resp.json();
            const diffs = Array.isArray(data.diffs ?? data.changes)
                ? (data.diffs ?? data.changes).map((d) => ({
                    field: String(d.field ?? d.key ?? ''),
                    before: d.before ?? d.old_value ?? null,
                    after: d.after ?? d.new_value ?? null,
                }))
                : [];
            setDiffData(diffs);
        }
        catch {
            setDiffData([]);
        }
        finally {
            setDiffLoading(false);
        }
    }, [selectedVersion, apiFetch]);
    const handleRollback = useCallback(async () => {
        if (rollingBack || selectedVersion === null)
            return;
        const confirmed = window.confirm(`Roll back configuration to version ${selectedVersion}? This creates a new version with those settings.`);
        if (!confirmed)
            return;
        setRollingBack(true);
        try {
            const resp = await apiFetch('/api/config/rollback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ version: selectedVersion }),
            });
            if (!resp.ok) {
                const body = await resp.text().catch(() => '');
                throw new Error(`${resp.status}: ${body}`);
            }
            onNotify(`Draft set to version ${selectedVersion} — activate to go live.`, 'success');
            setSelectedVersion(null);
            setDiffData(null);
            refetchConfig();
            refetchVersions();
        }
        catch (err) {
            const msg = err instanceof Error ? err.message : 'Rollback failed';
            onNotify(`Rollback failed: ${msg}`, 'error');
        }
        finally {
            setRollingBack(false);
        }
    }, [rollingBack, selectedVersion, apiFetch, onNotify, refetchConfig, refetchVersions]);
    const toggleSection = useCallback((groupKey) => {
        setCollapsedSections((prev) => {
            const next = new Set(prev);
            if (next.has(groupKey)) {
                next.delete(groupKey);
            }
            else {
                next.add(groupKey);
            }
            return next;
        });
    }, []);
    // ---- loading state ----
    if ((configLoading || schemaLoading) && !configData) {
        return (_jsx("div", { style: s.container, children: _jsx("div", { style: s.loading, children: "Loading configuration..." }) }));
    }
    // ---- error state ----
    if (configError) {
        return (_jsx("div", { style: s.container, children: _jsxs("div", { style: s.error, children: [_jsx("strong", { children: "Failed to load configuration." }), _jsx("br", {}), configError, _jsx("br", {}), _jsx("button", { style: { ...s.btnSecondary, marginTop: 12 }, onClick: refetchConfig, children: "Retry" })] }) }));
    }
    // Active tab fields
    const activeFields = fieldsByGroup[activeTab] ?? [];
    return (_jsxs("div", { style: s.container, children: [_jsxs("div", { style: s.header, children: [_jsxs("div", { children: [_jsxs("h2", { style: s.title, children: ["Agent configuration", configData && configData.fromCache === false && (_jsx("span", { style: {
                                            display: 'inline-block',
                                            marginLeft: 10,
                                            padding: '2px 8px',
                                            fontSize: 11,
                                            fontWeight: 600,
                                            color: '#f59e0b',
                                            backgroundColor: '#fef3c7',
                                            borderRadius: 4,
                                            verticalAlign: 'middle',
                                        }, children: "DRAFT" }))] }), configData && (_jsxs("p", { style: { fontSize: 13, color: '#888', margin: '4px 0 0 0' }, children: ["Version ", configData.version, " \u00B7 ", tenantContext.tier, " tier"] }))] }), _jsxs("div", { style: s.headerActions, children: [hasUnsavedChanges && (_jsxs("span", { style: s.unsavedBadge, children: [changedKeys.length, " unsaved change", changedKeys.length === 1 ? '' : 's'] })), hasUnsavedChanges && (_jsx("button", { style: s.btnSecondary, onClick: handleDiscard, disabled: saving, children: "Discard" })), _jsx("button", { style: {
                                    ...s.btnPrimary,
                                    ...(saving || !hasUnsavedChanges ? s.disabled : {}),
                                }, onClick: handleSave, disabled: saving || updateLoading || !hasUnsavedChanges, children: saving ? 'Saving...' : 'Save changes' }), _jsx("button", { style: {
                                    ...s.btnDanger,
                                    ...(resetting ? s.disabled : {}),
                                }, onClick: handleReset, disabled: resetting, children: resetting ? 'Resetting...' : 'Reset to Defaults' })] })] }), updateError && (_jsxs("div", { style: { ...s.error, marginBottom: 16 }, children: ["Save failed: ", updateError] })), _jsxs("div", { style: s.layout, children: [_jsxs("div", { style: s.mainPanel, children: [_jsx("div", { style: s.tabBar, children: CONFIG_GROUPS.map((g) => {
                                    const groupFields = fieldsByGroup[g.key] ?? [];
                                    const hasChanges = groupFields.some((f) => JSON.stringify(editedValues[f.key]) !==
                                        JSON.stringify(originalValues[f.key]));
                                    return (_jsxs("button", { style: s.tab(activeTab === g.key), onClick: () => setActiveTab(g.key), children: [g.label, hasChanges && _jsx("span", { style: s.changedDot })] }, g.key));
                                }) }), activeFields.length === 0 ? (_jsxs("div", { style: s.empty, children: ["No configurable fields in this group for the", ' ', _jsx("strong", { children: tenantContext.tier }), " tier."] })) : (_jsx("div", { children: (() => {
                                    const group = CONFIG_GROUPS.find((g) => g.key === activeTab);
                                    const collapsed = collapsedSections.has(activeTab);
                                    return (_jsxs(_Fragment, { children: [_jsxs("div", { style: s.sectionHeader(collapsed), onClick: () => toggleSection(activeTab), role: "button", tabIndex: 0, onKeyDown: (e) => {
                                                    if (e.key === 'Enter' || e.key === ' ')
                                                        toggleSection(activeTab);
                                                }, children: [_jsxs("div", { children: [_jsx("h3", { style: s.sectionTitle, children: group?.label ?? activeTab }), _jsx("p", { style: s.sectionDescription, children: group?.description ?? '' })] }), _jsx("span", { style: s.chevron(collapsed), children: collapsed ? '\u25B6' : '\u25BC' })] }), !collapsed && (_jsx("div", { style: s.fieldsContainer, children: activeFields.map((field) => (_jsx(FieldEditor, { field: field, value: editedValues[field.key], originalValue: originalValues[field.key], onChange: handleFieldChange, disabled: saving || updateLoading, tenantTier: tenantContext.tier }, field.key))) }))] }));
                                })() }))] }), _jsxs("div", { style: s.sidebar, children: [_jsx("h3", { style: s.sidebarTitle, children: "Version history" }), versionsLoading ? (_jsx("div", { style: { fontSize: 13, color: '#888' }, children: "Loading versions..." })) : versions.length === 0 ? (_jsx("div", { style: { fontSize: 13, color: '#888' }, children: "No version history available." })) : (_jsx("div", { children: versions.map((v) => (_jsxs("div", { style: s.versionItem(selectedVersion === v.version), onClick: () => handleSelectVersion(v.version), role: "button", tabIndex: 0, onKeyDown: (e) => {
                                        if (e.key === 'Enter' || e.key === ' ')
                                            handleSelectVersion(v.version);
                                    }, children: [_jsxs("div", { style: s.versionNumber, children: ["v", v.version] }), _jsxs("p", { style: s.versionMeta, children: [formatDate(v.createdAt), " \u00B7 ", v.actor, " \u00B7", ' ', v.changeCount, " change", v.changeCount === 1 ? '' : 's'] })] }, v.version))) })), selectedVersion !== null && (_jsxs("div", { style: s.diffContainer, children: [_jsxs("div", { style: s.diffTitle, children: ["Changes in v", selectedVersion] }), diffLoading ? (_jsx("div", { style: { fontSize: 13, color: '#888' }, children: "Loading diff..." })) : !diffData || diffData.length === 0 ? (_jsx("div", { style: { fontSize: 13, color: '#888' }, children: "No differences found." })) : (_jsx("div", { children: diffData.map((d, idx) => (_jsxs("div", { style: s.diffRow, children: [_jsx("span", { style: s.diffField, children: d.field }), _jsxs("span", { style: s.diffBefore, children: ["- ", formatValue(d.before)] }), _jsxs("span", { style: s.diffAfter, children: ["+ ", formatValue(d.after)] })] }, idx))) })), _jsx("button", { style: {
                                            ...s.btnDanger,
                                            marginTop: 12,
                                            width: '100%',
                                            ...(rollingBack ? s.disabled : {}),
                                        }, onClick: handleRollback, disabled: rollingBack, children: rollingBack
                                            ? 'Rolling back...'
                                            : `Rollback to v${selectedVersion}` })] }))] })] })] }));
};
export default ConfigEditor;
//# sourceMappingURL=ConfigEditor.js.map