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

import React, { useState, useEffect, useRef } from 'react';
import {
  Paper,
  TextInput,
  Textarea,
  Select,
  Slider,
  Chip,
  NumberInput,
  Button,
  Group,
  Stack,
  Title,
  Text,
  Badge,
  Alert,
  Switch,
  ActionIcon,
  Collapse,
  Tooltip,
  Modal,
  Table,
  useComputedColorScheme,
} from '@mantine/core';
import { useAppContext } from '../layouts/StandaloneLayout';
import {
  useConfig,
  useUpdateConfig,
  useConfigSuggestions,
  useNamedConfigs,
  useSaveNamedConfig,
  useActivateNamedConfig,
  useDeleteNamedConfig,
} from '../../shared/hooks/index';
import { HelpTooltip } from '../../shared/HelpTooltip';
import { LabelWithSuggestion } from '../../shared/components/SuggestionBadge';
import { LoadingState } from '../../shared/LoadingState';
import { tokens } from '../../shared/theme/styles';
import type { SuggestionMap } from '../../shared/hooks/useSuggestions';

const DOCS_BASE = 'https://agentredcx.com/docs/admin-guide';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const BRAND_RED = tokens.brand; // accent only — email badge indicator
const ACTION_BLUE = tokens.action;

// ---------------------------------------------------------------------------
// Escalation categories — each has its own email + keyword set
// ---------------------------------------------------------------------------

interface EscalationCategory {
  id: string;
  label: string;
  description: string;
  defaultKeywords: string[];
}

const ESCALATION_CATEGORIES: EscalationCategory[] = [
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

interface EscalationCategoryConfig {
  enabled: boolean;
  email: string;
  keywords: string[];
}

type EscalationCategoriesState = Record<string, EscalationCategoryConfig>;

function defaultEscalationCategories(): EscalationCategoriesState {
  const result: EscalationCategoriesState = {};
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

// ---------------------------------------------------------------------------
// Form state interface
// ---------------------------------------------------------------------------

interface ConfigFormState {
  brandName: string;
  brandVoice: string;
  formality: string;
  responseLength: string;
  returnWindow: number;
  refundPolicy: string;
  shippingPolicy: string;
  escalationThreshold: number;
  escalationCategories: EscalationCategoriesState;
  idleTimeoutMinutes: number;
  maxTurns: number;
  customInstructions: string;
  primaryLanguage: string;
  supportedLanguages: string[];
}

const DEFAULTS: ConfigFormState = {
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

const SaveIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z" />
    <polyline points="17 21 17 13 7 13 7 21" />
    <polyline points="7 3 7 8 15 8" />
  </svg>
);

const UndoIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="1 4 1 10 7 10" />
    <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10" />
  </svg>
);

const ChevronDownIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="6 9 12 15 18 9" />
  </svg>
);

const ChevronUpIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="18 15 12 9 6 15" />
  </svg>
);

const XIcon = () => (
  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
  </svg>
);

const ResetIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="1 4 1 10 7 10" />
    <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10" />
  </svg>
);

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Safely cast a config record value to string. */
function str(val: unknown, fallback = ''): string {
  if (typeof val === 'string') return val;
  return fallback;
}

/** Safely cast a config record value to number. */
function num(val: unknown, fallback: number): number {
  if (typeof val === 'number') return val;
  if (typeof val === 'string') {
    const n = Number(val);
    if (!Number.isNaN(n)) return n;
  }
  return fallback;
}

/** Safely cast a config record value to string array. */
function strArr(val: unknown, fallback: string[]): string[] {
  if (Array.isArray(val)) return val.map(String);
  return fallback;
}

/** Parse escalation categories from raw config. */
function parseEscalationCategories(raw: unknown): EscalationCategoriesState {
  const defaults = defaultEscalationCategories();
  if (!raw || typeof raw !== 'object') return defaults;
  const obj = raw as Record<string, unknown>;
  for (const cat of ESCALATION_CATEGORIES) {
    const entry = obj[cat.id];
    if (entry && typeof entry === 'object') {
      const e = entry as Record<string, unknown>;
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
function cfgVal(cfg: Record<string, unknown>, snake: string, camel: string): unknown {
  return cfg[snake] !== undefined ? cfg[snake] : cfg[camel];
}

/** Build form state from the raw config record. */
function configToForm(cfg: Record<string, unknown> | undefined | null): ConfigFormState {
  if (!cfg) return { ...DEFAULTS, escalationCategories: defaultEscalationCategories() };
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
function escalationCategoriesEqual(a: EscalationCategoriesState, b: EscalationCategoriesState): boolean {
  const keysA = Object.keys(a);
  const keysB = Object.keys(b);
  if (keysA.length !== keysB.length) return false;
  for (const k of keysA) {
    const ca = a[k];
    const cb = b[k];
    if (!ca || !cb) return false;
    if (ca.enabled !== cb.enabled) return false;
    if (ca.email !== cb.email) return false;
    if (ca.keywords.length !== cb.keywords.length) return false;
    if (ca.keywords.some((kw, i) => kw !== cb.keywords[i])) return false;
  }
  return true;
}

/** Compute fields that differ between two form states. */
/** Map camelCase form keys to snake_case backend field names. */
const FORM_TO_BACKEND: Record<string, string> = {
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

function diffForm(
  original: ConfigFormState,
  current: ConfigFormState,
): Record<string, unknown> {
  const changes: Record<string, unknown> = {};
  for (const key of Object.keys(current) as Array<keyof ConfigFormState>) {
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
    } else if (origVal !== curVal) {
      changes[backendKey] = curVal;
    }
  }
  return changes;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export const ConfigurationPage: React.FC = () => {
  const { apiFetch, onNotify, refreshActivationStatus, configRefreshKey } = useAppContext();
  const configResult = useConfig(apiFetch);
  const { updateConfig: saveConfig, loading: saving, error: saveError, clearError: clearSaveError } = useUpdateConfig(apiFetch);

  // KA-7: Config field suggestions from KB analysis
  const suggestionsResult = useConfigSuggestions(apiFetch);
  const suggestions: SuggestionMap = suggestionsResult.data ?? {};

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
  const [form, setForm] = useState<ConfigFormState>({ ...DEFAULTS });
  const [hasChanges, setHasChanges] = useState(false);

  // Snapshot of the server state (used for discard and diff)
  const serverFormRef = useRef<ConfigFormState>({ ...DEFAULTS });

  // Escalation category expand/collapse state
  const [expandedCategories, setExpandedCategories] = useState<Record<string, boolean>>({});
  // Keyword input buffers (one per category)
  const [keywordInputs, setKeywordInputs] = useState<Record<string, string>>({});

  // Re-fetch config when sidebar Discard triggers a configRefreshKey change (D50)
  useEffect(() => {
    if (configRefreshKey > 0) configResult.refetch();
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
  const updateField = <K extends keyof ConfigFormState>(key: K, value: ConfigFormState[K]) => {
    setForm((prev) => {
      const next = { ...prev, [key]: value };
      // Check if anything differs from server state
      const diff = diffForm(serverFormRef.current, next);
      setHasChanges(Object.keys(diff).length > 0);
      return next;
    });
  };

  /** Update a single field within one escalation category. */
  const updateCategory = (catId: string, field: keyof EscalationCategoryConfig, value: unknown) => {
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
  const addKeyword = (catId: string, keyword: string) => {
    const kw = keyword.trim().toLowerCase();
    if (!kw) return;
    // Check if keyword already exists in this category
    if (form.escalationCategories[catId]?.keywords.includes(kw)) return;
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
  const removeKeyword = (catId: string, keyword: string) => {
    const current = form.escalationCategories[catId]?.keywords || [];
    updateCategory(catId, 'keywords', current.filter((k) => k !== keyword));
  };

  /** Reset keywords for a category to its defaults. */
  const resetCategoryKeywords = (catId: string) => {
    const cat = ESCALATION_CATEGORIES.find((c) => c.id === catId);
    if (cat) {
      updateCategory(catId, 'keywords', [...cat.defaultKeywords]);
    }
  };

  /** Toggle a category expand/collapse. */
  const toggleCategory = (catId: string) => {
    setExpandedCategories((prev) => ({ ...prev, [catId]: !prev[catId] }));
  };

  const handleDiscard = () => {
    setForm({ ...serverFormRef.current });
    setHasChanges(false);
  };

  const handleSave = async () => {
    const changes = diffForm(serverFormRef.current, form);
    if (Object.keys(changes).length === 0) return;

    const result = await saveConfig(changes);
    if (result?.success) {
      onNotify('Draft configuration saved successfully.', 'success');
      // Update server snapshot so discard reflects new saved state
      serverFormRef.current = { ...form };
      setHasChanges(false);
      configResult.refetch();
      refreshActivationStatus();
    } else {
      const detail = (result as any)?.error || saveError || 'Failed to save configuration.';
      onNotify(`Failed to save: ${detail}`, 'error');
    }
  };

  // Named configuration handlers (WI #266, #267)
  const handleSaveNamed = async () => {
    const name = saveAsName.trim();
    if (!name) return;
    const result = await saveNamed(name);
    if (result) {
      setShowSaveModal(false);
      setSaveAsName('');
      onNotify(`Configuration "${name}" saved.`, 'success');
      namedResult.refetch();
    } else {
      onNotify('Failed to save named configuration.', 'error');
    }
  };

  const handleActivateNamed = async (name: string) => {
    const result = await activateNamed(name);
    if (result) {
      onNotify(`Configuration "${name}" activated.`, 'success');
      namedResult.refetch();
      configResult.refetch();
      refreshActivationStatus();
    } else {
      onNotify(`Failed to activate configuration "${name}".`, 'error');
    }
  };

  const handleDeleteNamed = async (name: string) => {
    const ok = await deleteNamed(name);
    if (ok) {
      onNotify(`Configuration "${name}" deleted.`, 'success');
      namedResult.refetch();
    } else {
      onNotify(`Failed to delete configuration "${name}".`, 'error');
    }
  };

  /** Format ISO date to readable relative/absolute string. */
  const formatDate = (iso: string): string => {
    try {
      const d = new Date(iso);
      const now = new Date();
      const diffMs = now.getTime() - d.getTime();
      const diffMins = Math.floor(diffMs / 60000);
      if (diffMins < 1) return 'Just now';
      if (diffMins < 60) return `${diffMins}m ago`;
      const diffHrs = Math.floor(diffMins / 60);
      if (diffHrs < 24) return `${diffHrs}h ago`;
      const diffDays = Math.floor(diffHrs / 24);
      if (diffDays < 7) return `${diffDays}d ago`;
      return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: d.getFullYear() !== now.getFullYear() ? 'numeric' : undefined });
    } catch {
      return iso;
    }
  };

  // Loading state
  if (configResult.loading && !configResult.data) {
    return <LoadingState text="Loading configuration" />;
  }

  // Error state
  if (configResult.error && !configResult.data) {
    return (
      <Alert color="red" variant="light" title="Failed to load configuration">
        <Text size="sm">{configResult.error}</Text>
        <Button mt="sm" size="xs" variant="light" onClick={configResult.refetch}>
          Retry
        </Button>
      </Alert>
    );
  }

  return (
    <Stack gap="lg">
      {/* Page header with action buttons */}
      <div>
        <Title order={2}>Agent configuration</Title>
        <Text c="dimmed" size="sm">
          Fine-tune your AI agent's behavior
        </Text>
      </div>

      {/* Save error banner */}
      {saveError && (
        <Alert color="red" variant="light" title="Save failed" withCloseButton onClose={clearSaveError}>
          <Text size="sm">{saveError}</Text>
        </Alert>
      )}

      {/* Saved Configurations (WI #266 delete, WI #267 timestamps) */}
      {(() => {
        const configs = namedResult.data?.configs ?? [];
        if (namedResult.loading && !namedResult.data) return null;
        const activeConfig = configs.find((c) => c.isActive);
        return (
          <Paper p="lg" radius="md" withBorder>
            <Group justify="space-between" mb={configs.length > 0 ? 'md' : 0}>
              <Text fw={600}>
                Saved configurations
                <HelpTooltip text="Save snapshots of your current configuration and switch between them. The active configuration is applied to your AI agent." docLink={`${DOCS_BASE}/named-configs`} />
              </Text>
              <Button
                size="xs"
                variant="light"
                color={ACTION_BLUE}
                onClick={() => { setSaveAsName(''); setShowSaveModal(true); }}
                disabled={savingNamed}
              >
                Save current as…
              </Button>
            </Group>
            {configs.length === 0 ? (
              <Text size="sm" c="dimmed">
                No saved configurations yet. Click "Save current as…" to create a reusable snapshot.
              </Text>
            ) : (
              <Table verticalSpacing="xs" highlightOnHover>
                <Table.Thead>
                  <Table.Tr>
                    <Table.Th>Name</Table.Th>
                    <Table.Th>Saved</Table.Th>
                    <Table.Th>Fields</Table.Th>
                    <Table.Th style={{ width: 140, textAlign: 'right' }}>Actions</Table.Th>
                  </Table.Tr>
                </Table.Thead>
                <Table.Tbody>
                  {configs.map((c) => (
                    <Table.Tr key={c.name}>
                      <Table.Td>
                        <Group gap={8} wrap="nowrap">
                          <Text size="sm" fw={c.isActive ? 600 : 400}>{c.name}</Text>
                          {c.isActive && <Badge size="xs" color="teal" variant="light">Active</Badge>}
                          {c.isDefault && <Badge size="xs" color="gray" variant="light">Default</Badge>}
                        </Group>
                      </Table.Td>
                      <Table.Td>
                        <Tooltip label={new Date(c.createdAt).toLocaleString()} withArrow>
                          <Text size="sm" c="dimmed">{formatDate(c.createdAt)}</Text>
                        </Tooltip>
                      </Table.Td>
                      <Table.Td>
                        <Badge size="sm" variant="light" color="gray">{c.fieldCount} fields</Badge>
                      </Table.Td>
                      <Table.Td>
                        <Group gap={4} justify="flex-end" wrap="nowrap">
                          {!c.isActive && (
                            <Button
                              size="compact-xs"
                              variant="light"
                              color={ACTION_BLUE}
                              onClick={() => handleActivateNamed(c.name)}
                              loading={activatingNamed}
                            >
                              Activate
                            </Button>
                          )}
                          {!c.isDefault && !c.isActive && (
                            <Button
                              size="compact-xs"
                              variant="light"
                              color="red"
                              onClick={() => handleDeleteNamed(c.name)}
                              loading={deletingNamed}
                            >
                              Delete
                            </Button>
                          )}
                        </Group>
                      </Table.Td>
                    </Table.Tr>
                  ))}
                </Table.Tbody>
              </Table>
            )}
            {activeConfig && (
              <Text size="xs" c="dimmed" mt="sm">
                Active: <strong>{activeConfig.name}</strong> (v{activeConfig.version}, last saved {formatDate(activeConfig.createdAt)})
              </Text>
            )}
          </Paper>
        );
      })()}

      {/* Save Configuration Modal */}
      <Modal
        opened={showSaveModal}
        onClose={() => setShowSaveModal(false)}
        title="Save configuration as"
        size="sm"
        centered
      >
        <Stack gap="md">
          <TextInput
            label="Configuration name"
            placeholder='e.g. "Holiday", "Black Friday", "Default v2"'
            value={saveAsName}
            onChange={(e) => setSaveAsName(e.currentTarget.value)}
            maxLength={64}
            data-autofocus
            onKeyDown={(e) => {
              if (e.key === 'Enter' && saveAsName.trim()) handleSaveNamed();
            }}
          />
          {saveAsName.trim().toLowerCase() === 'default' && (
            <Text size="xs" c="yellow">This will overwrite the Default configuration snapshot.</Text>
          )}
          <Group justify="flex-end">
            <Button variant="default" onClick={() => setShowSaveModal(false)}>Cancel</Button>
            <Button
              color={ACTION_BLUE}
              onClick={handleSaveNamed}
              disabled={!saveAsName.trim()}
              loading={savingNamed}
            >
              Save configuration
            </Button>
          </Group>
        </Stack>
      </Modal>

      {/* Configuration form */}
      <Stack gap="lg">
            {/* Brand & Persona */}
            <Paper p="lg" radius="md" withBorder>
              <Text fw={600} mb="md">Brand & persona <HelpTooltip text="Set your AI agent's name, greeting, personality tone, and formality level." docLink={`${DOCS_BASE}/brand-and-tone`} /></Text>
              <Stack gap="md">
                <TextInput
                  label={
                    <LabelWithSuggestion
                      label="Brand name"
                      suggestion={suggestions.brand_name}
                      currentValue={form.brandName}
                      onApply={(v) => updateField('brandName', String(v))}
                    />
                  }
                  placeholder="Your store or brand name"
                  value={form.brandName}
                  onChange={(e) => updateField('brandName', e.currentTarget.value)}
                  required
                />
                <Textarea
                  label={
                    <LabelWithSuggestion
                      label="Brand voice"
                      suggestion={suggestions.brand_voice}
                      currentValue={form.brandVoice}
                      onApply={(v) => updateField('brandVoice', String(v))}
                    />
                  }
                  placeholder="Describe the personality and tone of your AI agent..."
                  value={form.brandVoice}
                  onChange={(e) => updateField('brandVoice', e.currentTarget.value)}
                  minRows={3}
                  autosize
                  required
                />
                <Group grow>
                  <Select
                    label="Formality"
                    data={[
                      { value: 'casual', label: 'Casual' },
                      { value: 'balanced', label: 'Professional' },
                      { value: 'formal', label: 'Formal' },
                    ]}
                    value={form.formality}
                    onChange={(val) => updateField('formality', val || 'balanced')}
                  />
                  <Select
                    label="Response length"
                    data={[
                      { value: 'concise', label: 'Concise' },
                      { value: 'standard', label: 'Moderate' },
                      { value: 'detailed', label: 'Detailed' },
                    ]}
                    value={form.responseLength}
                    onChange={(val) => updateField('responseLength', val || 'standard')}
                  />
                </Group>
              </Stack>
            </Paper>

            {/* Policies */}
            <Paper p="lg" radius="md" withBorder>
              <Text fw={600} mb="md">Policies <HelpTooltip text="Control how the AI handles refunds, returns, and other business rules." docLink={`${DOCS_BASE}/business-policies`} /></Text>
              <Stack gap="md">
                <NumberInput
                  label="Return window"
                  suffix=" days"
                  value={form.returnWindow}
                  onChange={(val) => updateField('returnWindow', Number(val) || 30)}
                  min={0}
                  max={365}
                />
                <Textarea
                  label={
                    <LabelWithSuggestion
                      label="Refund policy"
                      suggestion={suggestions.return_policy}
                      currentValue={form.refundPolicy}
                      onApply={(v) => updateField('refundPolicy', String(v))}
                    />
                  }
                  placeholder="Describe your refund policy..."
                  value={form.refundPolicy}
                  onChange={(e) => updateField('refundPolicy', e.currentTarget.value)}
                  minRows={3}
                  autosize
                />
                <Textarea
                  label={
                    <LabelWithSuggestion
                      label="Shipping policy"
                      suggestion={suggestions.shipping_info}
                      currentValue={form.shippingPolicy}
                      onApply={(v) => updateField('shippingPolicy', String(v))}
                    />
                  }
                  placeholder="Describe your shipping policy..."
                  value={form.shippingPolicy}
                  onChange={(e) => updateField('shippingPolicy', e.currentTarget.value)}
                  minRows={3}
                  autosize
                />
              </Stack>
            </Paper>

            {/* Escalation */}
            <Paper p="lg" radius="md" withBorder>
              <Text fw={600} mb="xs">Escalation <HelpTooltip text="Configure when and how conversations are handed off to human team members." docLink={`${DOCS_BASE}/escalation-rules`} /></Text>
              <Text size="xs" c="dimmed" mb="md">
                Configure escalation categories, notification emails, and trigger keywords.
                Each category routes to a different team email with its own keyword set.
              </Text>

              <Stack gap="md">
                {/* Global threshold slider */}
                <div>
                  <Text size="sm" fw={500} mb={8}>
                    Escalation threshold
                  </Text>
                  <Slider
                    value={form.escalationThreshold}
                    onChange={(val) => updateField('escalationThreshold', val)}
                    min={0}
                    max={1}
                    step={0.05}
                    marks={[
                      { value: 0, label: <span style={{ position: 'relative', left: '50%' }}>Conservative</span> },
                      { value: 0.5, label: '0.5' },
                      { value: 1, label: <span style={{ position: 'relative', right: '50%' }}>Aggressive</span> },
                    ]}
                    label={(val) => val.toFixed(2)}
                    color={ACTION_BLUE}
                    mb="lg"
                  />
                </div>

                {/* Per-category cards */}
                {ESCALATION_CATEGORIES.map((cat) => {
                  const catConfig = form.escalationCategories[cat.id] || {
                    enabled: true,
                    email: '',
                    keywords: [...cat.defaultKeywords],
                  };
                  const isExpanded = !!expandedCategories[cat.id];
                  const kwCount = catConfig.keywords.length;

                  return (
                    <Paper
                      key={cat.id}
                      p="sm"
                      radius="sm"
                      style={{
                        backgroundColor: isDark ? tokens.page : '#f8f9fa',
                        border: `1px solid ${isDark ? tokens.border : '#dee2e6'}`,
                        opacity: catConfig.enabled ? 1 : 0.6,
                      }}
                    >
                      {/* Category header row */}
                      <Group justify="space-between" wrap="nowrap">
                        <Group gap="sm" wrap="nowrap" style={{ flex: 1, minWidth: 0, cursor: 'pointer' }} onClick={() => toggleCategory(cat.id)}>
                          <Switch
                            size="sm"
                            color={ACTION_BLUE}
                            checked={catConfig.enabled}
                            onChange={(e) => {
                              e.stopPropagation();
                              updateCategory(cat.id, 'enabled', e.currentTarget.checked);
                            }}
                          />
                          <div style={{ minWidth: 0 }}>
                            <Group gap={6} wrap="nowrap">
                              <Text size="sm" fw={600}>{cat.label}</Text>
                              <Badge size="xs" variant="light" color="gray">{kwCount} keywords</Badge>
                              {catConfig.email && <Badge size="xs" variant="light" color={BRAND_RED}>{String.fromCodePoint(0x2709)}</Badge>}
                            </Group>
                            <Text size="xs" c="dimmed" truncate>{cat.description}</Text>
                          </div>
                        </Group>
                        <ActionIcon
                          variant="subtle"
                          size="sm"
                          onClick={() => toggleCategory(cat.id)}
                          color="gray"
                        >
                          {isExpanded ? <ChevronUpIcon /> : <ChevronDownIcon />}
                        </ActionIcon>
                      </Group>

                      {/* Expanded detail */}
                      <Collapse in={isExpanded}>
                        <Stack gap="sm" mt="sm">
                          {/* Notification email */}
                          <TextInput
                            label="Notification email"
                            placeholder={`${cat.id}@yourcompany.com`}
                            size="sm"
                            value={catConfig.email}
                            onChange={(e) => updateCategory(cat.id, 'email', e.currentTarget.value)}
                            disabled={!catConfig.enabled}
                          />

                          {/* Keyword editor */}
                          <div>
                            <Group justify="space-between" mb={6}>
                              <Text size="sm" fw={500}>Keywords</Text>
                              <Tooltip label="Reset to default keywords">
                                <ActionIcon
                                  variant="subtle"
                                  size="xs"
                                  color="gray"
                                  onClick={() => resetCategoryKeywords(cat.id)}
                                  disabled={!catConfig.enabled}
                                >
                                  <ResetIcon />
                                </ActionIcon>
                              </Tooltip>
                            </Group>
                            {/* Keyword chips */}
                            <Group gap={4} wrap="wrap" mb={8}>
                              {catConfig.keywords.map((kw) => (
                                <Badge
                                  key={kw}
                                  size="sm"
                                  variant="light"
                                  color={isDark ? 'gray' : 'dark'}
                                  rightSection={
                                    catConfig.enabled ? (
                                      <ActionIcon
                                        size="xs"
                                        variant="transparent"
                                        color="gray"
                                        onClick={() => removeKeyword(cat.id, kw)}
                                        style={{ marginLeft: 2 }}
                                      >
                                        <XIcon />
                                      </ActionIcon>
                                    ) : null
                                  }
                                >
                                  {kw}
                                </Badge>
                              ))}
                            </Group>
                            {/* Add keyword input */}
                            <TextInput
                              size="xs"
                              placeholder="Add keyword and press Enter..."
                              value={keywordInputs[cat.id] || ''}
                              onChange={(e) =>
                                setKeywordInputs((prev) => ({ ...prev, [cat.id]: e.currentTarget.value }))
                              }
                              onKeyDown={(e) => {
                                if (e.key === 'Enter') {
                                  e.preventDefault();
                                  addKeyword(cat.id, keywordInputs[cat.id] || '');
                                  setKeywordInputs((prev) => ({ ...prev, [cat.id]: '' }));
                                }
                              }}
                              disabled={!catConfig.enabled}
                            />
                          </div>
                        </Stack>
                      </Collapse>
                    </Paper>
                  );
                })}

                {/* Global escalation settings */}
                <Group grow>
                  <NumberInput
                    label={<>Idle timeout <HelpTooltip text="Minutes of customer inactivity before the conversation is automatically ended and marked as resolved." docLink={`${DOCS_BASE}/escalation-settings`} /></>}
                    suffix=" minutes"
                    value={form.idleTimeoutMinutes}
                    onChange={(val) => updateField('idleTimeoutMinutes', Number(val) || 30)}
                    min={1}
                    max={120}
                  />
                  <NumberInput
                    label={<>Max turns <HelpTooltip text="Maximum number of back-and-forth exchanges before the conversation is automatically ended and marked as resolved." docLink={`${DOCS_BASE}/escalation-settings`} /></>}
                    value={form.maxTurns}
                    onChange={(val) => updateField('maxTurns', Number(val) || 50)}
                    min={1}
                    max={50}
                  />
                </Group>
              </Stack>
            </Paper>

            {/* Custom Instructions */}
            <Paper p="lg" radius="md" withBorder>
              <Text fw={600} mb="md">Custom instructions <HelpTooltip text="Free-form instructions injected into every AI response. Use this for brand-specific rules or response guidelines." docLink={`${DOCS_BASE}/custom-instructions`} /></Text>
              <Textarea
                placeholder="Provide advisory instructions for the AI agent..."
                value={form.customInstructions}
                onChange={(e) => updateField('customInstructions', e.currentTarget.value)}
                minRows={5}
                autosize
                maxRows={12}
              />
              <Text size="xs" c="dimmed" mt={8}>
                Advisory instructions for the AI agent. Safety rules always take
                precedence.
              </Text>
            </Paper>

            {/* Language */}
            <Paper p="lg" radius="md" withBorder>
              <Text fw={600} mb="md">Language <HelpTooltip text="Set the primary response language and additional supported languages for multilingual customers." docLink={`${DOCS_BASE}/languages`} /></Text>
              <Stack gap="md">
                <Select
                  label="Primary language"
                  data={PRIMARY_LANGUAGES}
                  value={form.primaryLanguage}
                  onChange={(val) => updateField('primaryLanguage', val || 'en')}
                />
                <div>
                  <Text size="sm" fw={500} mb={8}>
                    Supported languages
                  </Text>
                  <Chip.Group
                    multiple
                    value={form.supportedLanguages}
                    onChange={(val) => updateField('supportedLanguages', val)}
                  >
                    <Group gap="xs" wrap="wrap">
                      {LANGUAGES.map((lang) => (
                        <Chip
                          key={lang.value}
                          value={lang.value}
                          size="sm"
                          color={ACTION_BLUE}
                          disabled={lang.disabled}
                          styles={lang.disabled ? { label: { opacity: 0.5, cursor: 'not-allowed' } } : undefined}
                        >
                          {lang.label}
                        </Chip>
                      ))}
                    </Group>
                  </Chip.Group>
                </div>
              </Stack>
            </Paper>

          </Stack>

          {/* Save draft inputs — persists field edits to draft state */}
          <Group justify="flex-end">
            <Button
              color={ACTION_BLUE}
              leftSection={<SaveIcon />}
              disabled={!hasChanges}
              loading={saving}
              onClick={handleSave}
            >
              Save draft inputs
            </Button>
          </Group>
    </Stack>
  );
};
