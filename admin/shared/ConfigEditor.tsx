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

import React, { useState, useCallback, useEffect, useMemo } from 'react';
import type {
  BaseComponentProps,
  ConfigField,
  ConfigFieldType,
  ConfigVersion,
  ConfigDiff,
} from './types';
import {
  useConfig,
  useUpdateConfig,
  useConfigVersions,
  useConfigSchema,
  useNamedConfigs,
  useSaveNamedConfig,
  useActivateNamedConfig,
  useDeleteNamedConfig,
} from './hooks';
import type { NamedConfigSummary } from './hooks';

// ---------------------------------------------------------------------------
// Group definitions
// ---------------------------------------------------------------------------

interface ConfigGroup {
  key: string;
  label: string;
  description: string;
}

const CONFIG_GROUPS: ConfigGroup[] = [
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
    flexDirection: 'column' as const,
    fontFamily:
      "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    color: '#1a1a1a',
    height: '100%',
  } as React.CSSProperties,

  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 24,
    flexWrap: 'wrap' as const,
    gap: 12,
  } as React.CSSProperties,

  title: {
    fontSize: 24,
    fontWeight: 600,
    margin: 0,
  } as React.CSSProperties,

  headerActions: {
    display: 'flex',
    gap: 8,
    flexWrap: 'wrap' as const,
    alignItems: 'center',
  } as React.CSSProperties,

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
  } as React.CSSProperties,

  layout: {
    display: 'flex',
    gap: 24,
    flexGrow: 1,
    minHeight: 0,
  } as React.CSSProperties,

  mainPanel: {
    flex: 1,
    minWidth: 0,
    overflowY: 'auto' as const,
  } as React.CSSProperties,

  sidebar: {
    width: 320,
    flexShrink: 0,
    overflowY: 'auto' as const,
    borderLeft: '1px solid #e5e5e5',
    paddingLeft: 24,
  } as React.CSSProperties,

  // Tabs
  tabBar: {
    display: 'flex',
    flexWrap: 'wrap' as const,
    gap: 2,
    marginBottom: 24,
    borderBottom: '1px solid #e5e5e5',
    paddingBottom: 0,
  } as React.CSSProperties,

  tab: (active: boolean): React.CSSProperties => ({
    padding: '8px 16px',
    fontSize: 13,
    fontWeight: active ? 600 : 400,
    color: active ? '#ff3621' : '#555',
    backgroundColor: 'transparent',
    border: 'none',
    borderBottom: active ? '2px solid #ff3621' : '2px solid transparent',
    cursor: 'pointer',
    whiteSpace: 'nowrap',
    marginBottom: -1,
    transition: 'color 0.15s ease, border-color 0.15s ease',
  }),

  // Field sections
  sectionHeader: (collapsed: boolean): React.CSSProperties => ({
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
  } as React.CSSProperties,

  sectionDescription: {
    fontSize: 13,
    color: '#777',
    margin: '4px 0 0 0',
  } as React.CSSProperties,

  chevron: (collapsed: boolean): React.CSSProperties => ({
    fontSize: 12,
    color: '#999',
    transform: collapsed ? 'rotate(-90deg)' : 'rotate(0deg)',
    transition: 'transform 0.15s ease',
  }),

  fieldsContainer: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: 18,
    padding: '16px 0 24px 0',
  } as React.CSSProperties,

  fieldGroup: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: 5,
  } as React.CSSProperties,

  label: {
    fontSize: 14,
    fontWeight: 500,
    color: '#333',
  } as React.CSSProperties,

  description: {
    fontSize: 12,
    color: '#888',
    margin: 0,
    lineHeight: 1.4,
  } as React.CSSProperties,

  input: {
    padding: '8px 12px',
    fontSize: 14,
    border: '1px solid #d0d0d0',
    borderRadius: 6,
    outline: 'none',
    backgroundColor: '#fff',
    color: '#1a1a1a',
    width: '100%',
    boxSizing: 'border-box' as const,
  } as React.CSSProperties,

  textarea: {
    padding: '8px 12px',
    fontSize: 14,
    border: '1px solid #d0d0d0',
    borderRadius: 6,
    outline: 'none',
    backgroundColor: '#fff',
    color: '#1a1a1a',
    minHeight: 72,
    resize: 'vertical' as const,
    width: '100%',
    boxSizing: 'border-box' as const,
    fontFamily: 'inherit',
  } as React.CSSProperties,

  select: {
    padding: '8px 12px',
    fontSize: 14,
    border: '1px solid #d0d0d0',
    borderRadius: 6,
    outline: 'none',
    backgroundColor: '#fff',
    color: '#1a1a1a',
    width: '100%',
    boxSizing: 'border-box' as const,
  } as React.CSSProperties,

  checkboxRow: {
    display: 'flex',
    alignItems: 'center',
    gap: 10,
    cursor: 'pointer',
  } as React.CSSProperties,

  checkbox: {
    width: 18,
    height: 18,
    accentColor: '#ff3621',
    cursor: 'pointer',
  } as React.CSSProperties,

  colorRow: {
    display: 'flex',
    alignItems: 'center',
    gap: 12,
  } as React.CSSProperties,

  colorSwatch: {
    width: 36,
    height: 36,
    border: '1px solid #d0d0d0',
    borderRadius: 6,
    padding: 2,
    cursor: 'pointer',
    backgroundColor: '#fff',
  } as React.CSSProperties,

  tierBadge: {
    display: 'inline-block',
    fontSize: 10,
    fontWeight: 600,
    textTransform: 'uppercase' as const,
    padding: '2px 6px',
    borderRadius: 4,
    backgroundColor: '#f0f0f0',
    color: '#888',
    marginLeft: 8,
  } as React.CSSProperties,

  // Buttons
  btnPrimary: {
    padding: '8px 20px',
    fontSize: 14,
    fontWeight: 600,
    backgroundColor: '#ff3621',
    color: '#fff',
    border: 'none',
    borderRadius: 6,
    cursor: 'pointer',
  } as React.CSSProperties,

  btnSecondary: {
    padding: '8px 20px',
    fontSize: 14,
    fontWeight: 500,
    backgroundColor: 'transparent',
    color: '#555',
    border: '1px solid #d0d0d0',
    borderRadius: 6,
    cursor: 'pointer',
  } as React.CSSProperties,

  btnDanger: {
    padding: '8px 16px',
    fontSize: 13,
    fontWeight: 500,
    backgroundColor: '#fef2f2',
    color: '#991b1b',
    border: '1px solid #fecaca',
    borderRadius: 6,
    cursor: 'pointer',
  } as React.CSSProperties,

  btnSmall: {
    padding: '4px 10px',
    fontSize: 12,
    fontWeight: 500,
    backgroundColor: 'transparent',
    color: '#555',
    border: '1px solid #d0d0d0',
    borderRadius: 4,
    cursor: 'pointer',
  } as React.CSSProperties,

  disabled: {
    opacity: 0.6,
    cursor: 'not-allowed',
  } as React.CSSProperties,

  // Version history sidebar
  sidebarTitle: {
    fontSize: 16,
    fontWeight: 600,
    marginBottom: 16,
    color: '#1a1a1a',
  } as React.CSSProperties,

  versionItem: (selected: boolean): React.CSSProperties => ({
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
  } as React.CSSProperties,

  versionMeta: {
    fontSize: 12,
    color: '#888',
    margin: '2px 0 0 0',
  } as React.CSSProperties,

  diffContainer: {
    marginTop: 16,
    padding: 16,
    backgroundColor: '#fafafa',
    borderRadius: 8,
    border: '1px solid #e5e5e5',
  } as React.CSSProperties,

  diffTitle: {
    fontSize: 14,
    fontWeight: 600,
    marginBottom: 12,
    color: '#1a1a1a',
  } as React.CSSProperties,

  diffRow: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: 2,
    padding: '8px 0',
    borderBottom: '1px solid #eee',
  } as React.CSSProperties,

  diffField: {
    fontSize: 13,
    fontWeight: 600,
    color: '#333',
  } as React.CSSProperties,

  diffBefore: {
    fontSize: 12,
    color: '#991b1b',
    fontFamily: "'JetBrains Mono', monospace",
    backgroundColor: '#fef2f2',
    padding: '2px 6px',
    borderRadius: 3,
    wordBreak: 'break-all' as const,
  } as React.CSSProperties,

  diffAfter: {
    fontSize: 12,
    color: '#166534',
    fontFamily: "'JetBrains Mono', monospace",
    backgroundColor: '#f0fdf4',
    padding: '2px 6px',
    borderRadius: 3,
    wordBreak: 'break-all' as const,
  } as React.CSSProperties,

  loading: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 64,
    fontSize: 14,
    color: '#888',
  } as React.CSSProperties,

  error: {
    padding: '16px 20px',
    backgroundColor: '#fef2f2',
    border: '1px solid #fecaca',
    borderRadius: 8,
    color: '#991b1b',
    fontSize: 14,
    lineHeight: 1.5,
  } as React.CSSProperties,

  empty: {
    padding: '32px 20px',
    textAlign: 'center' as const,
    color: '#888',
    fontSize: 14,
  } as React.CSSProperties,

  changedDot: {
    display: 'inline-block',
    width: 6,
    height: 6,
    borderRadius: '50%',
    backgroundColor: '#f59e0b',
    marginLeft: 6,
  } as React.CSSProperties,

  // Named config bar
  namedConfigBar: {
    display: 'flex',
    alignItems: 'center',
    gap: 12,
    padding: '10px 16px',
    backgroundColor: '#f9fafb',
    borderRadius: 8,
    border: '1px solid #e5e5e5',
    marginBottom: 20,
    flexWrap: 'wrap' as const,
  } as React.CSSProperties,

  namedConfigLabel: {
    fontSize: 13,
    fontWeight: 600,
    color: '#555',
    whiteSpace: 'nowrap' as const,
  } as React.CSSProperties,

  namedConfigName: {
    fontSize: 14,
    fontWeight: 700,
    color: '#1a1a1a',
    padding: '2px 10px',
    backgroundColor: '#fff',
    border: '1px solid #d0d0d0',
    borderRadius: 4,
  } as React.CSSProperties,

  namedConfigSelect: {
    padding: '5px 10px',
    fontSize: 13,
    border: '1px solid #d0d0d0',
    borderRadius: 6,
    backgroundColor: '#fff',
    color: '#333',
    cursor: 'pointer',
  } as React.CSSProperties,

  // Modal overlay
  modalOverlay: {
    position: 'fixed' as const,
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 10000,
  } as React.CSSProperties,

  modalContent: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: '24px 28px',
    width: 400,
    maxWidth: '90vw',
    boxShadow: '0 20px 60px rgba(0, 0, 0, 0.2)',
  } as React.CSSProperties,

  modalTitle: {
    fontSize: 18,
    fontWeight: 600,
    margin: '0 0 16px 0',
    color: '#1a1a1a',
  } as React.CSSProperties,

  modalActions: {
    display: 'flex',
    justifyContent: 'flex-end',
    gap: 8,
    marginTop: 20,
  } as React.CSSProperties,
} as const;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatValue(v: unknown): string {
  if (v === null || v === undefined) return '(empty)';
  if (typeof v === 'boolean') return v ? 'true' : 'false';
  if (typeof v === 'object') return JSON.stringify(v);
  return String(v);
}

function formatDate(iso: string): string {
  try {
    const d = new Date(iso);
    return d.toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return iso;
  }
}

// ---------------------------------------------------------------------------
// Field editor (shared logic — same types as OnboardingWizard)
// ---------------------------------------------------------------------------

interface FieldEditorProps {
  field: ConfigField;
  value: unknown;
  originalValue: unknown;
  onChange: (key: string, value: unknown) => void;
  disabled: boolean;
  tenantTier: string;
}

const FieldEditor: React.FC<FieldEditorProps> = ({
  field,
  value,
  originalValue,
  onChange,
  disabled,
  tenantTier,
}) => {
  const tierOrder = ['trial', 'starter', 'professional', 'enterprise'];
  const tenantIdx = tierOrder.indexOf(tenantTier);
  const fieldIdx = field.tierGate ? tierOrder.indexOf(field.tierGate) : 0;
  const isLocked = fieldIdx > tenantIdx;
  const effectiveDisabled = disabled || isLocked;
  const isChanged = JSON.stringify(value) !== JSON.stringify(originalValue);

  const handleChange = useCallback(
    (newVal: unknown) => {
      if (!effectiveDisabled) onChange(field.key, newVal);
    },
    [field.key, onChange, effectiveDisabled],
  );

  const renderControl = (): React.ReactNode => {
    const ft: ConfigFieldType = field.type;

    switch (ft) {
      case 'boolean':
        return (
          <label style={s.checkboxRow}>
            <input
              type="checkbox"
              style={s.checkbox}
              checked={Boolean(value)}
              onChange={(e) => handleChange(e.target.checked)}
              disabled={effectiveDisabled}
            />
            <span style={{ fontSize: 14, color: effectiveDisabled ? '#aaa' : '#333' }}>
              {Boolean(value) ? 'Enabled' : 'Disabled'}
            </span>
          </label>
        );

      case 'select':
        return (
          <select
            style={{
              ...s.select,
              ...(effectiveDisabled ? s.disabled : {}),
            }}
            value={String(value ?? '')}
            onChange={(e) => handleChange(e.target.value)}
            disabled={effectiveDisabled}
          >
            <option value="">-- Select --</option>
            {(field.options ?? []).map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        );

      case 'color':
        return (
          <div style={s.colorRow}>
            <input
              type="color"
              style={s.colorSwatch}
              value={String(value ?? '#000000')}
              onChange={(e) => handleChange(e.target.value)}
              disabled={effectiveDisabled}
            />
            <span
              style={{
                fontSize: 13,
                fontFamily: "'JetBrains Mono', monospace",
                color: '#555',
              }}
            >
              {String(value ?? '#000000')}
            </span>
          </div>
        );

      case 'textarea':
        return (
          <textarea
            style={{
              ...s.textarea,
              ...(effectiveDisabled ? s.disabled : {}),
            }}
            value={String(value ?? '')}
            onChange={(e) => handleChange(e.target.value)}
            disabled={effectiveDisabled}
            rows={4}
          />
        );

      case 'number':
      case 'integer':
      case 'float':
        return (
          <input
            type="number"
            style={{
              ...s.input,
              ...(effectiveDisabled ? s.disabled : {}),
            }}
            value={value !== undefined && value !== null ? String(value) : ''}
            onChange={(e) =>
              handleChange(e.target.value === '' ? null : Number(e.target.value))
            }
            step={field.type === 'float' ? '0.1' : '1'}
            disabled={effectiveDisabled}
          />
        );

      case 'json':
      case 'object':
        return (
          <textarea
            style={{
              ...s.textarea,
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: 13,
              ...(effectiveDisabled ? s.disabled : {}),
            }}
            value={
              typeof value === 'string'
                ? value
                : value != null
                  ? JSON.stringify(value, null, 2)
                  : ''
            }
            onChange={(e) => {
              try {
                handleChange(JSON.parse(e.target.value));
              } catch {
                handleChange(e.target.value);
              }
            }}
            disabled={effectiveDisabled}
            rows={5}
          />
        );

      case 'string':
      default:
        return (
          <input
            type="text"
            style={{
              ...s.input,
              ...(effectiveDisabled ? s.disabled : {}),
            }}
            value={String(value ?? '')}
            onChange={(e) => handleChange(e.target.value)}
            disabled={effectiveDisabled}
          />
        );
    }
  };

  return (
    <div style={s.fieldGroup}>
      <label style={s.label}>
        {field.label}
        {isLocked && field.tierGate && (
          <span style={s.tierBadge}>{field.tierGate}+</span>
        )}
        {isChanged && <span style={s.changedDot} title="Modified" />}
      </label>
      {field.description && <p style={s.description}>{field.description}</p>}
      {renderControl()}
    </div>
  );
};

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export const ConfigEditor: React.FC<BaseComponentProps> = ({
  tenantContext,
  apiFetch,
  onNotify,
}) => {
  // ---- state ----
  const [activeTab, setActiveTab] = useState<string>(CONFIG_GROUPS[0].key);
  const [collapsedSections, setCollapsedSections] = useState<Set<string>>(new Set());
  const [editedValues, setEditedValues] = useState<Record<string, unknown>>({});
  const [originalValues, setOriginalValues] = useState<Record<string, unknown>>({});
  const [saving, setSaving] = useState(false);
  const [resetting, setResetting] = useState(false);
  const [selectedVersion, setSelectedVersion] = useState<number | null>(null);
  const [diffData, setDiffData] = useState<ConfigDiff[] | null>(null);
  const [diffLoading, setDiffLoading] = useState(false);
  const [rollingBack, setRollingBack] = useState(false);

  // Named config state
  const [showSaveAsModal, setShowSaveAsModal] = useState(false);
  const [saveAsName, setSaveAsName] = useState('');

  // ---- hooks ----
  const { data: configData, loading: configLoading, error: configError, refetch: refetchConfig } =
    useConfig(apiFetch);

  const { updateConfig, loading: updateLoading, error: updateError } = useUpdateConfig(apiFetch);

  const { data: schemaData, loading: schemaLoading } = useConfigSchema(apiFetch);

  const {
    data: versionsData,
    loading: versionsLoading,
    refetch: refetchVersions,
  } = useConfigVersions(apiFetch);

  // Named config hooks
  const {
    data: namedConfigsData,
    loading: namedConfigsLoading,
    refetch: refetchNamedConfigs,
  } = useNamedConfigs(apiFetch);

  const { saveNamed, loading: savingNamed } = useSaveNamedConfig(apiFetch);
  const { activateNamed, loading: activatingNamed } = useActivateNamedConfig(apiFetch);
  const { deleteNamed, loading: deletingNamed } = useDeleteNamedConfig(apiFetch);

  // Derived named config data
  const namedConfigs: NamedConfigSummary[] = useMemo(() => {
    return namedConfigsData?.configs ?? [];
  }, [namedConfigsData]);

  const activeConfigName: string = useMemo(() => {
    const active = namedConfigs.find((c) => c.isActive);
    return active?.name ?? 'Default';
  }, [namedConfigs]);

  // ---- derive all fields from schema ----
  const allFields: ConfigField[] = useMemo(() => {
    if (!schemaData?.fields) return [];
    return schemaData.fields.map((raw: Record<string, unknown>) => ({
      key: String(raw.key ?? raw.field_name ?? ''),
      label: String(raw.label ?? raw.field_name ?? ''),
      description: String(raw.description ?? raw.tooltip ?? ''),
      type: (raw.type ?? raw.field_type ?? 'string') as ConfigFieldType,
      defaultValue: raw.default_value ?? raw.defaultValue ?? null,
      currentValue: raw.current_value ?? raw.currentValue ?? null,
      options: Array.isArray(raw.options)
        ? raw.options.map((o: unknown) => {
            if (typeof o === 'object' && o !== null && 'value' in o) {
              return o as { value: string; label: string };
            }
            return { value: String(o), label: String(o) };
          })
        : undefined,
      tierGate: (raw.tier_gate ?? raw.tierGate ?? undefined) as string | undefined,
      stepOrder: Number(raw.step_order ?? raw.stepOrder ?? 0),
      group: String(raw.group ?? raw.onboarding_step ?? 'other'),
    })) as ConfigField[];
  }, [schemaData]);

  // Group fields by config group
  const fieldsByGroup: Record<string, ConfigField[]> = useMemo(() => {
    const map: Record<string, ConfigField[]> = {};
    for (const g of CONFIG_GROUPS) {
      map[g.key] = [];
    }
    for (const f of allFields) {
      const groupKey = f.group;
      if (map[groupKey]) {
        map[groupKey].push(f);
      } else {
        // Fields that don't match a known group — assign to closest match
        // or default to the first group
        const match = CONFIG_GROUPS.find((g) => groupKey.includes(g.key) || g.key.includes(groupKey));
        const target = match ? match.key : CONFIG_GROUPS[0].key;
        if (!map[target]) map[target] = [];
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
    if (!configData?.config) return;
    const values: Record<string, unknown> = {};
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
  const versions: ConfigVersion[] = useMemo(() => {
    if (!versionsData?.versions) return [];
    return versionsData.versions.map((v: Record<string, unknown>) => ({
      version: Number(v.version ?? 0),
      createdAt: String(v.created_at ?? v.createdAt ?? ''),
      actor: String(v.actor ?? 'system'),
      changeCount: Number(v.change_count ?? v.changeCount ?? 0),
    }));
  }, [versionsData]);

  // ---- unsaved changes ----
  const changedKeys = useMemo(() => {
    const keys: string[] = [];
    for (const key of Object.keys(editedValues)) {
      if (JSON.stringify(editedValues[key]) !== JSON.stringify(originalValues[key])) {
        keys.push(key);
      }
    }
    return keys;
  }, [editedValues, originalValues]);

  const hasUnsavedChanges = changedKeys.length > 0;

  // ---- handlers ----
  const handleFieldChange = useCallback((key: string, value: unknown) => {
    setEditedValues((prev) => ({ ...prev, [key]: value }));
  }, []);

  const handleSave = useCallback(async () => {
    if (saving || updateLoading || !hasUnsavedChanges) return;
    setSaving(true);

    // Build partial update with only changed fields
    const changes: Record<string, unknown> = {};
    for (const key of changedKeys) {
      changes[key] = editedValues[key];
    }

    try {
      const result = await updateConfig(changes);
      if (result?.success) {
        onNotify(
          `Changes saved to draft (${result.changes?.length ?? changedKeys.length} field${changedKeys.length === 1 ? '' : 's'}) — activate to go live.`,
          'success',
        );
        setOriginalValues({ ...editedValues });
        refetchConfig();
        refetchVersions();
      } else {
        onNotify(result?.message ?? 'Failed to save configuration.', 'error');
      }
    } catch {
      onNotify('An unexpected error occurred while saving.', 'error');
    } finally {
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
    if (resetting) return;

    const confirmed = window.confirm(
      'Reset all configuration to tier defaults? This will discard all custom overrides and cannot be undone.',
    );
    if (!confirmed) return;

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
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Reset failed';
      onNotify(`Reset failed: ${msg}`, 'error');
    } finally {
      setResetting(false);
    }
  }, [resetting, apiFetch, onNotify, refetchConfig, refetchVersions]);

  const handleSelectVersion = useCallback(
    async (version: number) => {
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
        const diffs: ConfigDiff[] = Array.isArray(data.diffs ?? data.changes)
          ? (data.diffs ?? data.changes).map((d: Record<string, unknown>) => ({
              field: String(d.field ?? d.key ?? ''),
              before: d.before ?? d.old_value ?? null,
              after: d.after ?? d.new_value ?? null,
            }))
          : [];
        setDiffData(diffs);
      } catch {
        setDiffData([]);
      } finally {
        setDiffLoading(false);
      }
    },
    [selectedVersion, apiFetch],
  );

  const handleRollback = useCallback(async () => {
    if (rollingBack || selectedVersion === null) return;

    const confirmed = window.confirm(
      `Roll back configuration to version ${selectedVersion}? This creates a new version with those settings.`,
    );
    if (!confirmed) return;

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
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Rollback failed';
      onNotify(`Rollback failed: ${msg}`, 'error');
    } finally {
      setRollingBack(false);
    }
  }, [rollingBack, selectedVersion, apiFetch, onNotify, refetchConfig, refetchVersions]);

  // ---- Named config handlers ----
  const handleSaveAs = useCallback(async () => {
    const name = saveAsName.trim();
    if (!name || savingNamed) return;

    try {
      const result = await saveNamed(name);
      if (result) {
        onNotify(`Configuration saved as "${name}".`, 'success');
        setShowSaveAsModal(false);
        setSaveAsName('');
        refetchNamedConfigs();
        refetchConfig();
        refetchVersions();
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Save failed';
      onNotify(`Failed to save configuration: ${msg}`, 'error');
    }
  }, [saveAsName, savingNamed, saveNamed, onNotify, refetchNamedConfigs, refetchConfig, refetchVersions]);

  const handleActivateConfig = useCallback(
    async (name: string) => {
      if (activatingNamed) return;

      try {
        const result = await activateNamed(name);
        if (result) {
          onNotify(`Configuration "${name}" activated.`, 'success');
          refetchNamedConfigs();
          refetchConfig();
          refetchVersions();
        }
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Activation failed';
        onNotify(`Failed to activate configuration: ${msg}`, 'error');
      }
    },
    [activatingNamed, activateNamed, onNotify, refetchNamedConfigs, refetchConfig, refetchVersions],
  );

  const handleDeleteConfig = useCallback(
    async (name: string) => {
      if (deletingNamed) return;

      const confirmed = window.confirm(
        `Delete configuration "${name}"? This removes the name label from the version. The version history itself is preserved.`,
      );
      if (!confirmed) return;

      try {
        const result = await deleteNamed(name);
        if (result) {
          onNotify(`Configuration "${name}" deleted.`, 'success');
          refetchNamedConfigs();
        }
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Delete failed';
        onNotify(`Failed to delete configuration: ${msg}`, 'error');
      }
    },
    [deletingNamed, deleteNamed, onNotify, refetchNamedConfigs],
  );

  const handleRestoreDefault = useCallback(async () => {
    await handleActivateConfig('Default');
  }, [handleActivateConfig]);

  const toggleSection = useCallback((groupKey: string) => {
    setCollapsedSections((prev) => {
      const next = new Set(prev);
      if (next.has(groupKey)) {
        next.delete(groupKey);
      } else {
        next.add(groupKey);
      }
      return next;
    });
  }, []);

  // ---- loading state ----
  if ((configLoading || schemaLoading) && !configData) {
    return (
      <div style={s.container}>
        <div style={s.loading}>Loading configuration...</div>
      </div>
    );
  }

  // ---- error state ----
  if (configError) {
    return (
      <div style={s.container}>
        <div style={s.error}>
          <strong>Failed to load configuration.</strong>
          <br />
          {configError}
          <br />
          <button style={{ ...s.btnSecondary, marginTop: 12 }} onClick={refetchConfig}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  // Active tab fields
  const activeFields = fieldsByGroup[activeTab] ?? [];

  return (
    <div style={s.container}>
      {/* Header */}
      <div style={s.header}>
        <div>
          <h2 style={s.title}>
            Agent configuration
            {configData && configData.fromCache === false && (
              <span style={{
                display: 'inline-block',
                marginLeft: 10,
                padding: '2px 8px',
                fontSize: 11,
                fontWeight: 600,
                color: '#f59e0b',
                backgroundColor: '#fef3c7',
                borderRadius: 4,
                verticalAlign: 'middle',
              }}>
                DRAFT
              </span>
            )}
          </h2>
          {configData && (
            <p style={{ fontSize: 13, color: '#888', margin: '4px 0 0 0' }}>
              Version {configData.version} &middot; {tenantContext.tier} tier
            </p>
          )}
        </div>

        <div style={s.headerActions}>
          {hasUnsavedChanges && (
            <span style={s.unsavedBadge}>
              {changedKeys.length} unsaved change{changedKeys.length === 1 ? '' : 's'}
            </span>
          )}

          {hasUnsavedChanges && (
            <button style={s.btnSecondary} onClick={handleDiscard} disabled={saving}>
              Discard
            </button>
          )}

          <button
            style={{
              ...s.btnPrimary,
              ...(saving || !hasUnsavedChanges ? s.disabled : {}),
            }}
            onClick={handleSave}
            disabled={saving || updateLoading || !hasUnsavedChanges}
          >
            {saving ? 'Saving...' : 'Save changes'}
          </button>

          <button
            style={{
              ...s.btnDanger,
              ...(resetting ? s.disabled : {}),
            }}
            onClick={handleReset}
            disabled={resetting}
          >
            {resetting ? 'Resetting...' : 'Reset to Defaults'}
          </button>
        </div>
      </div>

      {/* Named configuration bar */}
      <div style={s.namedConfigBar}>
        <span style={s.namedConfigLabel}>Active configuration:</span>
        <span style={s.namedConfigName}>{activeConfigName}</span>

        {/* Config selector dropdown */}
        {namedConfigs.length > 0 && (
          <select
            style={s.namedConfigSelect}
            value=""
            onChange={(e) => {
              const name = e.target.value;
              if (name) handleActivateConfig(name);
            }}
            disabled={activatingNamed}
          >
            <option value="">Switch configuration...</option>
            {namedConfigs
              .filter((c) => !c.isActive)
              .map((c) => (
                <option key={c.name} value={c.name}>
                  {c.name} (v{c.version})
                </option>
              ))}
          </select>
        )}

        <button
          style={s.btnSecondary}
          onClick={() => {
            setSaveAsName('');
            setShowSaveAsModal(true);
          }}
        >
          Save As...
        </button>

        {activeConfigName !== 'Default' && (
          <button
            style={s.btnSmall}
            onClick={handleRestoreDefault}
            disabled={activatingNamed}
          >
            Restore to Default
          </button>
        )}

        {/* Delete non-Default configs */}
        {namedConfigs.filter((c) => !c.isDefault && !c.isActive).length > 0 && (
          <select
            style={{ ...s.namedConfigSelect, color: '#991b1b' }}
            value=""
            onChange={(e) => {
              const name = e.target.value;
              if (name) handleDeleteConfig(name);
            }}
            disabled={deletingNamed}
          >
            <option value="">Delete config...</option>
            {namedConfigs
              .filter((c) => !c.isDefault)
              .map((c) => (
                <option key={c.name} value={c.name}>
                  {c.name}
                </option>
              ))}
          </select>
        )}

        {namedConfigsLoading && (
          <span style={{ fontSize: 12, color: '#888' }}>Loading...</span>
        )}
      </div>

      {/* Update error */}
      {updateError && (
        <div style={{ ...s.error, marginBottom: 16 }}>Save failed: {updateError}</div>
      )}

      {/* Main layout: fields + sidebar */}
      <div style={s.layout}>
        {/* Main panel */}
        <div style={s.mainPanel}>
          {/* Tab bar */}
          <div style={s.tabBar}>
            {CONFIG_GROUPS.map((g) => {
              const groupFields = fieldsByGroup[g.key] ?? [];
              const hasChanges = groupFields.some(
                (f) =>
                  JSON.stringify(editedValues[f.key]) !==
                  JSON.stringify(originalValues[f.key]),
              );
              return (
                <button
                  key={g.key}
                  style={s.tab(activeTab === g.key)}
                  onClick={() => setActiveTab(g.key)}
                >
                  {g.label}
                  {hasChanges && <span style={s.changedDot} />}
                </button>
              );
            })}
          </div>

          {/* Active group content */}
          {activeFields.length === 0 ? (
            <div style={s.empty}>
              No configurable fields in this group for the{' '}
              <strong>{tenantContext.tier}</strong> tier.
            </div>
          ) : (
            <div>
              {/* Section header (collapsible) */}
              {(() => {
                const group = CONFIG_GROUPS.find((g) => g.key === activeTab);
                const collapsed = collapsedSections.has(activeTab);
                return (
                  <>
                    <div
                      style={s.sectionHeader(collapsed)}
                      onClick={() => toggleSection(activeTab)}
                      role="button"
                      tabIndex={0}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' || e.key === ' ') toggleSection(activeTab);
                      }}
                    >
                      <div>
                        <h3 style={s.sectionTitle}>{group?.label ?? activeTab}</h3>
                        <p style={s.sectionDescription}>
                          {group?.description ?? ''}
                        </p>
                      </div>
                      <span style={s.chevron(collapsed)}>
                        {collapsed ? '\u25B6' : '\u25BC'}
                      </span>
                    </div>

                    {!collapsed && (
                      <div style={s.fieldsContainer}>
                        {activeFields.map((field) => (
                          <FieldEditor
                            key={field.key}
                            field={field}
                            value={editedValues[field.key]}
                            originalValue={originalValues[field.key]}
                            onChange={handleFieldChange}
                            disabled={saving || updateLoading}
                            tenantTier={tenantContext.tier}
                          />
                        ))}
                      </div>
                    )}
                  </>
                );
              })()}
            </div>
          )}
        </div>

        {/* Version history sidebar */}
        <div style={s.sidebar}>
          <h3 style={s.sidebarTitle}>Version history</h3>

          {versionsLoading ? (
            <div style={{ fontSize: 13, color: '#888' }}>Loading versions...</div>
          ) : versions.length === 0 ? (
            <div style={{ fontSize: 13, color: '#888' }}>No version history available.</div>
          ) : (
            <div>
              {versions.map((v) => (
                <div
                  key={v.version}
                  style={s.versionItem(selectedVersion === v.version)}
                  onClick={() => handleSelectVersion(v.version)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ')
                      handleSelectVersion(v.version);
                  }}
                >
                  <div style={s.versionNumber}>v{v.version}</div>
                  <p style={s.versionMeta}>
                    {formatDate(v.createdAt)} &middot; {v.actor} &middot;{' '}
                    {v.changeCount} change{v.changeCount === 1 ? '' : 's'}
                  </p>
                </div>
              ))}
            </div>
          )}

          {/* Diff view */}
          {selectedVersion !== null && (
            <div style={s.diffContainer}>
              <div style={s.diffTitle}>
                Changes in v{selectedVersion}
              </div>

              {diffLoading ? (
                <div style={{ fontSize: 13, color: '#888' }}>Loading diff...</div>
              ) : !diffData || diffData.length === 0 ? (
                <div style={{ fontSize: 13, color: '#888' }}>No differences found.</div>
              ) : (
                <div>
                  {diffData.map((d, idx) => (
                    <div key={idx} style={s.diffRow}>
                      <span style={s.diffField}>{d.field}</span>
                      <span style={s.diffBefore}>- {formatValue(d.before)}</span>
                      <span style={s.diffAfter}>+ {formatValue(d.after)}</span>
                    </div>
                  ))}
                </div>
              )}

              {/* Rollback button */}
              <button
                style={{
                  ...s.btnDanger,
                  marginTop: 12,
                  width: '100%',
                  ...(rollingBack ? s.disabled : {}),
                }}
                onClick={handleRollback}
                disabled={rollingBack}
              >
                {rollingBack
                  ? 'Rolling back...'
                  : `Rollback to v${selectedVersion}`}
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Save As modal */}
      {showSaveAsModal && (
        <div
          style={s.modalOverlay}
          onClick={(e) => {
            if (e.target === e.currentTarget) setShowSaveAsModal(false);
          }}
        >
          <div style={s.modalContent}>
            <h3 style={s.modalTitle}>Save configuration as</h3>
            <p style={{ fontSize: 13, color: '#666', margin: '0 0 16px 0' }}>
              Save the current configuration as a named snapshot. You can switch between
              saved configurations at any time.
            </p>
            <input
              type="text"
              style={s.input}
              placeholder="e.g. Holiday Mode, Sale Config, Test Variant A"
              value={saveAsName}
              onChange={(e) => setSaveAsName(e.target.value)}
              maxLength={64}
              autoFocus
              onKeyDown={(e) => {
                if (e.key === 'Enter' && saveAsName.trim()) handleSaveAs();
                if (e.key === 'Escape') setShowSaveAsModal(false);
              }}
            />
            {saveAsName.trim().toLowerCase() === 'default' && (
              <p style={{ fontSize: 12, color: '#991b1b', margin: '8px 0 0 0' }}>
                "Default" is reserved. Choose a different name.
              </p>
            )}
            <div style={s.modalActions}>
              <button
                style={s.btnSecondary}
                onClick={() => setShowSaveAsModal(false)}
              >
                Cancel
              </button>
              <button
                style={{
                  ...s.btnPrimary,
                  ...(!saveAsName.trim() ||
                  saveAsName.trim().toLowerCase() === 'default' ||
                  savingNamed
                    ? s.disabled
                    : {}),
                }}
                onClick={handleSaveAs}
                disabled={
                  !saveAsName.trim() ||
                  saveAsName.trim().toLowerCase() === 'default' ||
                  savingNamed
                }
              >
                {savingNamed ? 'Saving...' : 'Save configuration'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ConfigEditor;
