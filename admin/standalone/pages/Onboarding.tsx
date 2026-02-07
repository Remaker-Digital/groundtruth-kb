// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

import React, { useState, useCallback, useMemo } from 'react';
import {
  Paper,
  Stepper,
  TextInput,
  Textarea,
  Select,
  Switch,
  Chip,
  NumberInput,
  ColorInput,
  ColorPicker,
  Slider as MantineSlider,
  SegmentedControl,
  Button,
  Progress,
  Group,
  Stack,
  Title,
  Text,
  Badge,
  Alert,
  Divider,
  Box,
  Skeleton,
  Loader,
  ActionIcon,
  Collapse,
  Tooltip,
  useComputedColorScheme,
} from '@mantine/core';
import { useAppContext } from '../layouts/StandaloneLayout';
import { useOnboardingSteps, useUpdateConfig } from '../../shared/hooks/index';
import type { ConfigFieldType } from '../../shared/types/index';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const BRAND_RED = '#ff3621';

// ---------------------------------------------------------------------------
// Escalation categories (same definitions as Configuration.tsx)
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
    label: 'Technical Assistance',
    description: 'Integration issues, API questions, advanced configuration',
    defaultKeywords: ['api', 'integration', 'webhook', 'developer', 'sdk', 'technical', 'configuration', 'setup'],
  },
  {
    id: 'general',
    label: 'General Inquiry',
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
    result[cat.id] = { enabled: true, email: '', keywords: [...cat.defaultKeywords] };
  }
  return result;
}

// ---------------------------------------------------------------------------
// SVG mini-icons for escalation UI
// ---------------------------------------------------------------------------

const ChevronDownSmall = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="6 9 12 15 18 9" /></svg>
);
const ChevronUpSmall = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="18 15 12 9 6 15" /></svg>
);
const XSmall = () => (
  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" /></svg>
);
const ResetSmall = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="1 4 1 10 7 10" /><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10" /></svg>
);

// ---------------------------------------------------------------------------
// Widget preview defaults for the wizard Widget Appearance step
// ---------------------------------------------------------------------------

const WIDGET_PRESET_COLORS = [
  '#ff3621', '#e53e3e', '#dd6b20', '#d69e2e', '#38a169',
  '#319795', '#3182ce', '#5a67d8', '#805ad5', '#d53f8c',
  '#1a1a2e', '#2d3748', '#4a5568', '#000000',
];

const WIDGET_POSITION_OPTIONS = [
  { value: 'bottom-right', label: 'Bottom Right' },
  { value: 'bottom-left', label: 'Bottom Left' },
];

// ---------------------------------------------------------------------------
// Field type mapping: API ConfigFieldType → renderer type
// ---------------------------------------------------------------------------

function mapFieldType(apiType: ConfigFieldType): string {
  switch (apiType) {
    case 'string':
      return 'text';
    case 'json':
      return 'textarea';
    case 'boolean':
      return 'switch';
    default:
      // 'textarea', 'select', 'number', 'color' pass through
      return apiType;
  }
}

// ---------------------------------------------------------------------------
// Local step shape (adapted from prototype OnboardingStep)
// ---------------------------------------------------------------------------

interface LocalField {
  key: string;
  label: string;
  type: string;
  value: unknown;
  placeholder?: string;
  options?: Array<{ value: string; label: string }>;
}

interface LocalStep {
  id: number;
  step: string;
  title: string;
  description: string;
  completed: boolean;
  fields: LocalField[];
}

// ---------------------------------------------------------------------------
// Deep clone helper
// ---------------------------------------------------------------------------

function deepCloneSteps(steps: LocalStep[]): LocalStep[] {
  return steps.map((s) => ({
    ...s,
    fields: s.fields.map((f) => ({ ...f })),
  }));
}

// ---------------------------------------------------------------------------
// Go Live step factory (appended as the last step)
// ---------------------------------------------------------------------------

function makeGoLiveStep(nextId: number): LocalStep {
  return {
    id: nextId,
    step: 'go_live',
    title: 'Go Live',
    description: 'Review your setup and activate your AI agent',
    completed: false,
    fields: [],
  };
}

// ---------------------------------------------------------------------------
// OnboardingPage
// ---------------------------------------------------------------------------

export function OnboardingPage() {
  const { apiFetch, onNotify } = useAppContext();
  const stepsResult = useOnboardingSteps(apiFetch);
  const { updateConfig, loading: saving } = useUpdateConfig(apiFetch);

  const computedColorScheme = useComputedColorScheme('dark');
  const isDark = computedColorScheme === 'dark';

  const [activeStep, setActiveStep] = useState(0);
  const [localValues, setLocalValues] = useState<Record<string, Record<string, unknown>>>({});
  const [completedOverrides, setCompletedOverrides] = useState<Record<string, boolean>>({});

  // Escalation categories state (for the escalation_rules step)
  const [escalationCats, setEscalationCats] = useState<EscalationCategoriesState>(defaultEscalationCategories());
  const [expandedCats, setExpandedCats] = useState<Record<string, boolean>>({});
  const [kwInputs, setKwInputs] = useState<Record<string, string>>({});
  const [escalationThreshold, setEscalationThreshold] = useState(0.7);

  // Widget config state (for the widget_appearance step)
  const [widgetConfig, setWidgetConfig] = useState({
    widgetColor: '#ff3621',
    widgetBackground: '#ffffff',
    widgetPosition: 'bottom-right',
    offsetX: 20,
    offsetY: 20,
    borderRadius: 16,
    agentAvatar: '',
    agentDisplayName: 'AI Assistant',
    agentTitle: 'Here to help',
    greetingMessage: 'Hi there! How can I help you today?',
    colorMode: 'auto',
    showBranding: true,
  });

  // ---- Map API steps to local format + append Go Live step ----------------

  const steps: LocalStep[] = useMemo(() => {
    const apiSteps = stepsResult.data?.steps ?? [];
    const mapped: LocalStep[] = apiSteps.map((s, i) => ({
      id: i + 1,
      step: s.step,
      title: s.label,
      description: s.description,
      completed: completedOverrides[s.step] ?? s.isComplete,
      fields: (s.fields ?? []).map((f) => {
        // Use locally-edited value if present, else API currentValue, else defaultValue
        const localStepValues = localValues[s.step];
        const localVal = localStepValues != null ? localStepValues[f.key] : undefined;
        return {
          key: f.key,
          label: f.label,
          type: mapFieldType(f.type),
          value: localVal !== undefined ? localVal : (f.currentValue ?? f.defaultValue),
          placeholder: f.description,
          options: f.options,
        };
      }),
    }));

    // Append Go Live review step
    mapped.push(makeGoLiveStep(mapped.length + 1));
    return mapped;
  }, [stepsResult.data, localValues, completedOverrides]);

  const totalSteps = steps.length;
  const completedCount = steps.filter((s) => s.completed).length;
  const progressPercent = totalSteps > 0 ? Math.round((completedCount / totalSteps) * 100) : 0;
  const currentStep = steps[activeStep] ?? null;
  const allComplete = steps.filter((s) => s.step !== 'go_live').every((s) => s.completed);
  const isGoLive = currentStep?.step === 'go_live';

  // ---- Field value updates (local state) ----------------------------------

  const updateFieldValue = useCallback(
    (fieldIndex: number, value: unknown) => {
      if (!currentStep) return;
      const field = currentStep.fields[fieldIndex];
      if (!field) return;

      setLocalValues((prev) => ({
        ...prev,
        [currentStep.step]: {
          ...(prev[currentStep.step] || {}),
          [field.key]: value,
        },
      }));
    },
    [currentStep],
  );

  // ---- Complete step: save via API ----------------------------------------

  const handleCompleteStep = useCallback(async () => {
    if (!currentStep || isGoLive) return;

    // Collect field key-value pairs — custom state for special steps
    const changes: Record<string, unknown> = {};

    if (currentStep.step === 'escalation_rules') {
      changes.escalationThreshold = escalationThreshold;
      changes.escalationCategories = escalationCats;
    } else if (currentStep.step === 'widget_appearance') {
      Object.assign(changes, widgetConfig);
    } else {
      for (const field of currentStep.fields) {
        changes[field.key] = field.value;
      }
    }

    const result = await updateConfig(changes);
    if (result) {
      setCompletedOverrides((prev) => ({ ...prev, [currentStep.step]: true }));
      onNotify(`"${currentStep.title}" has been saved successfully.`, 'success');
      if (activeStep < totalSteps - 1) {
        setActiveStep(activeStep + 1);
      }
    } else {
      onNotify('Failed to save step. Please try again.', 'error');
    }
  }, [currentStep, isGoLive, updateConfig, onNotify, activeStep, totalSteps, escalationThreshold, escalationCats, widgetConfig]);

  // ---- Navigation ---------------------------------------------------------

  const handleBack = useCallback(() => {
    if (activeStep > 0) setActiveStep(activeStep - 1);
  }, [activeStep]);

  const handleNext = useCallback(() => {
    if (activeStep < totalSteps - 1) setActiveStep(activeStep + 1);
  }, [activeStep, totalSteps]);

  // ---- Dynamic field renderer ---------------------------------------------

  const renderField = (field: LocalField, fieldIndex: number) => {
    switch (field.type) {
      case 'text':
        return (
          <TextInput
            key={field.key}
            label={field.label}
            placeholder={field.placeholder || ''}
            value={String(field.value ?? '')}
            onChange={(e) => updateFieldValue(fieldIndex, e.currentTarget.value)}
          />
        );
      case 'textarea':
        return (
          <Textarea
            key={field.key}
            label={field.label}
            placeholder={field.placeholder || ''}
            value={String(field.value ?? '')}
            onChange={(e) => updateFieldValue(fieldIndex, e.currentTarget.value)}
            minRows={3}
            autosize
          />
        );
      case 'url':
        return (
          <TextInput
            key={field.key}
            label={field.label}
            placeholder={field.placeholder || 'https://'}
            value={String(field.value ?? '')}
            onChange={(e) => updateFieldValue(fieldIndex, e.currentTarget.value)}
            type="url"
          />
        );
      case 'select':
        return (
          <Select
            key={field.key}
            label={field.label}
            placeholder="Select..."
            value={field.value != null ? String(field.value) : null}
            data={field.options ?? []}
            onChange={(val) => updateFieldValue(fieldIndex, val)}
            allowDeselect={false}
          />
        );
      case 'multiselect':
        return (
          <div key={field.key}>
            <Text size="sm" fw={500} mb={6}>
              {field.label}
            </Text>
            <Chip.Group
              multiple
              value={Array.isArray(field.value) ? (field.value as string[]) : []}
              onChange={(val) => updateFieldValue(fieldIndex, val)}
            >
              <Group gap="xs">
                {(field.options ?? []).map((opt) => (
                  <Chip key={opt.value} value={opt.value} size="sm" variant="outline" color={BRAND_RED}>
                    {opt.label}
                  </Chip>
                ))}
              </Group>
            </Chip.Group>
          </div>
        );
      case 'switch':
        return (
          <Switch
            key={field.key}
            label={field.label}
            description={field.placeholder}
            checked={Boolean(field.value)}
            onChange={(e) => updateFieldValue(fieldIndex, e.currentTarget.checked)}
            color={BRAND_RED}
          />
        );
      case 'number':
        return (
          <NumberInput
            key={field.key}
            label={field.label}
            value={typeof field.value === 'number' ? field.value : 0}
            onChange={(val) => updateFieldValue(fieldIndex, val)}
            min={0}
          />
        );
      case 'email':
        return (
          <TextInput
            key={field.key}
            label={field.label}
            placeholder={field.placeholder || 'email@example.com'}
            value={String(field.value ?? '')}
            onChange={(e) => updateFieldValue(fieldIndex, e.currentTarget.value)}
            type="email"
          />
        );
      case 'color':
        return (
          <ColorInput
            key={field.key}
            label={field.label}
            value={String(field.value ?? BRAND_RED)}
            onChange={(val) => updateFieldValue(fieldIndex, val)}
            format="hex"
          />
        );
      default:
        return (
          <TextInput
            key={field.key}
            label={field.label}
            value={String(field.value ?? '')}
            onChange={(e) => updateFieldValue(fieldIndex, e.currentTarget.value)}
          />
        );
    }
  };

  // ---- Escalation category helpers -----------------------------------------

  const updateCatField = (catId: string, field: keyof EscalationCategoryConfig, value: unknown) => {
    setEscalationCats((prev) => {
      const next = { ...prev };
      next[catId] = { ...next[catId], [field]: value };
      return next;
    });
  };

  const addKw = (catId: string, keyword: string) => {
    const kw = keyword.trim().toLowerCase();
    if (!kw) return;
    if (escalationCats[catId]?.keywords.includes(kw)) return;
    for (const [otherId, otherCfg] of Object.entries(escalationCats)) {
      if (otherId !== catId && otherCfg.keywords.includes(kw)) return;
    }
    const current = escalationCats[catId]?.keywords || [];
    updateCatField(catId, 'keywords', [...current, kw]);
  };

  const removeKw = (catId: string, keyword: string) => {
    const current = escalationCats[catId]?.keywords || [];
    updateCatField(catId, 'keywords', current.filter((k) => k !== keyword));
  };

  const resetKw = (catId: string) => {
    const cat = ESCALATION_CATEGORIES.find((c) => c.id === catId);
    if (cat) updateCatField(catId, 'keywords', [...cat.defaultKeywords]);
  };

  // ---- Custom step: Escalation Rules -------------------------------------

  const renderEscalationStep = () => (
    <Stack gap="md">
      {/* Threshold slider */}
      <div>
        <Text size="sm" fw={500} mb={8}>Escalation Threshold</Text>
        <MantineSlider
          value={escalationThreshold}
          onChange={setEscalationThreshold}
          min={0} max={1} step={0.05}
          marks={[
            { value: 0, label: 'Conservative' },
            { value: 0.5, label: '0.5' },
            { value: 1, label: 'Aggressive' },
          ]}
          label={(val) => val.toFixed(2)}
          color={BRAND_RED}
          mb="lg"
        />
      </div>

      {/* Per-category cards */}
      {ESCALATION_CATEGORIES.map((cat) => {
        const cfg = escalationCats[cat.id] || { enabled: true, email: '', keywords: [...cat.defaultKeywords] };
        const isExp = !!expandedCats[cat.id];
        return (
          <Paper
            key={cat.id}
            p="sm"
            radius="sm"
            style={{
              backgroundColor: isDark ? '#141414' : '#f8f9fa',
              border: `1px solid ${isDark ? '#272727' : '#dee2e6'}`,
              opacity: cfg.enabled ? 1 : 0.6,
            }}
          >
            <Group justify="space-between" wrap="nowrap">
              <Group gap="sm" wrap="nowrap" style={{ flex: 1, minWidth: 0, cursor: 'pointer' }} onClick={() => setExpandedCats((p) => ({ ...p, [cat.id]: !p[cat.id] }))}>
                <Switch
                  size="sm"
                  color={BRAND_RED}
                  checked={cfg.enabled}
                  onChange={(e) => { e.stopPropagation(); updateCatField(cat.id, 'enabled', e.currentTarget.checked); }}
                />
                <div style={{ minWidth: 0 }}>
                  <Group gap={6} wrap="nowrap">
                    <Text size="sm" fw={600}>{cat.label}</Text>
                    <Badge size="xs" variant="light" color="gray">{cfg.keywords.length} keywords</Badge>
                    {cfg.email && <Badge size="xs" variant="light" color={BRAND_RED}>{String.fromCodePoint(0x2709)}</Badge>}
                  </Group>
                  <Text size="xs" c="dimmed" truncate>{cat.description}</Text>
                </div>
              </Group>
              <ActionIcon variant="subtle" size="sm" onClick={() => setExpandedCats((p) => ({ ...p, [cat.id]: !p[cat.id] }))} color="gray">
                {isExp ? <ChevronUpSmall /> : <ChevronDownSmall />}
              </ActionIcon>
            </Group>

            <Collapse in={isExp}>
              <Stack gap="sm" mt="sm">
                <TextInput
                  label="Notification Email"
                  placeholder={`${cat.id}@yourcompany.com`}
                  size="sm"
                  value={cfg.email}
                  onChange={(e) => updateCatField(cat.id, 'email', e.currentTarget.value)}
                  disabled={!cfg.enabled}
                />
                <div>
                  <Group justify="space-between" mb={6}>
                    <Text size="sm" fw={500}>Keywords</Text>
                    <Tooltip label="Reset to defaults">
                      <ActionIcon variant="subtle" size="xs" color="gray" onClick={() => resetKw(cat.id)} disabled={!cfg.enabled}>
                        <ResetSmall />
                      </ActionIcon>
                    </Tooltip>
                  </Group>
                  <Group gap={4} wrap="wrap" mb={8}>
                    {cfg.keywords.map((kw) => (
                      <Badge
                        key={kw}
                        size="sm"
                        variant="light"
                        color={isDark ? 'gray' : 'dark'}
                        rightSection={
                          cfg.enabled ? (
                            <ActionIcon size="xs" variant="transparent" color="gray" onClick={() => removeKw(cat.id, kw)} style={{ marginLeft: 2 }}>
                              <XSmall />
                            </ActionIcon>
                          ) : null
                        }
                      >
                        {kw}
                      </Badge>
                    ))}
                  </Group>
                  <TextInput
                    size="xs"
                    placeholder="Add keyword and press Enter..."
                    value={kwInputs[cat.id] || ''}
                    onChange={(e) => setKwInputs((p) => ({ ...p, [cat.id]: e.currentTarget.value }))}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault();
                        addKw(cat.id, kwInputs[cat.id] || '');
                        setKwInputs((p) => ({ ...p, [cat.id]: '' }));
                      }
                    }}
                    disabled={!cfg.enabled}
                  />
                </div>
              </Stack>
            </Collapse>
          </Paper>
        );
      })}
    </Stack>
  );

  // ---- Custom step: Widget Appearance (full configurator) -----------------

  const updateWidget = (key: string, value: unknown) => {
    setWidgetConfig((prev) => ({ ...prev, [key]: value }));
  };

  const renderWidgetAppearanceStep = () => {
    const dk = isDark;
    // Preview token colors
    const panelBg = dk ? '#1f1f1f' : (widgetConfig.widgetBackground || '#ffffff');
    const headerBg = widgetConfig.widgetColor || BRAND_RED;
    const msgAreaBg = dk ? '#141414' : '#f8f9fa';
    const agentBubbleBg = dk ? '#1f1f1f' : '#f0f0f0';
    const agentBubbleText = dk ? '#E0E0E0' : '#1f2937';
    const borderColor = dk ? '#272727' : '#dee2e6';

    return (
      <Stack gap="lg">
        {/* Two-column: controls left, preview right */}
        <div style={{ display: 'flex', gap: 24, alignItems: 'flex-start', flexWrap: 'wrap' }}>
          {/* Controls */}
          <div style={{ flex: 1, minWidth: 280 }}>
            <Stack gap="md">
              {/* Primary Color */}
              <div>
                <Text size="sm" fw={500} mb={6}>Widget Color</Text>
                <ColorPicker
                  value={widgetConfig.widgetColor}
                  onChange={(val) => updateWidget('widgetColor', val)}
                  format="hex"
                  size="sm"
                  swatches={WIDGET_PRESET_COLORS}
                  fullWidth
                />
                <TextInput
                  size="xs"
                  value={widgetConfig.widgetColor}
                  onChange={(e) => updateWidget('widgetColor', e.currentTarget.value)}
                  mt={6}
                  styles={{ input: { fontFamily: 'monospace' } }}
                />
              </div>

              {/* Background Color */}
              <div>
                <Text size="sm" fw={500} mb={6}>Widget Background</Text>
                <ColorPicker
                  value={widgetConfig.widgetBackground}
                  onChange={(val) => updateWidget('widgetBackground', val)}
                  format="hex"
                  size="sm"
                  swatches={['#ffffff', '#f8f9fa', '#f0f0f0', '#1f1f1f', '#141414', '#0a0a0a']}
                  fullWidth
                />
                <TextInput
                  size="xs"
                  value={widgetConfig.widgetBackground}
                  onChange={(e) => updateWidget('widgetBackground', e.currentTarget.value)}
                  mt={6}
                  styles={{ input: { fontFamily: 'monospace' } }}
                />
              </div>

              {/* Position */}
              <div>
                <Text size="sm" fw={500} mb={6}>Position</Text>
                <SegmentedControl
                  data={WIDGET_POSITION_OPTIONS}
                  value={widgetConfig.widgetPosition}
                  onChange={(val) => updateWidget('widgetPosition', val)}
                  color={BRAND_RED}
                  fullWidth
                  size="xs"
                />
              </div>

              {/* Offset X/Y */}
              <Group grow>
                <NumberInput
                  label="Offset X"
                  suffix="px"
                  value={widgetConfig.offsetX}
                  onChange={(val) => updateWidget('offsetX', Number(val) || 20)}
                  min={0} max={100} size="sm"
                />
                <NumberInput
                  label="Offset Y"
                  suffix="px"
                  value={widgetConfig.offsetY}
                  onChange={(val) => updateWidget('offsetY', Number(val) || 20)}
                  min={0} max={100} size="sm"
                />
              </Group>

              {/* Border Radius */}
              <div>
                <Text size="sm" fw={500} mb={6}>Border Radius: {widgetConfig.borderRadius}px</Text>
                <MantineSlider
                  value={widgetConfig.borderRadius}
                  onChange={(val) => updateWidget('borderRadius', val)}
                  min={0} max={32} step={1}
                  color={BRAND_RED}
                  marks={[{ value: 0, label: '0' }, { value: 16, label: '16' }, { value: 32, label: '32' }]}
                />
              </div>

              {/* Color Mode */}
              <div>
                <Text size="sm" fw={500} mb={6}>Color Mode</Text>
                <SegmentedControl
                  data={[
                    { value: 'light', label: 'Light' },
                    { value: 'dark', label: 'Dark' },
                    { value: 'auto', label: 'Auto' },
                  ]}
                  value={widgetConfig.colorMode}
                  onChange={(val) => updateWidget('colorMode', val)}
                  color={BRAND_RED}
                  fullWidth
                  size="xs"
                />
              </div>

              {/* Agent info */}
              <TextInput
                label="Agent Display Name"
                value={widgetConfig.agentDisplayName}
                onChange={(e) => updateWidget('agentDisplayName', e.currentTarget.value)}
                size="sm"
              />
              <TextInput
                label="Agent Title"
                value={widgetConfig.agentTitle}
                onChange={(e) => updateWidget('agentTitle', e.currentTarget.value)}
                size="sm"
              />
              <Textarea
                label="Greeting Message"
                value={widgetConfig.greetingMessage}
                onChange={(e) => updateWidget('greetingMessage', e.currentTarget.value)}
                size="sm"
                minRows={2}
                autosize
              />

              {/* Branding toggle */}
              <Switch
                label="Show 'Powered by Agent Red' branding"
                checked={widgetConfig.showBranding}
                onChange={(e) => updateWidget('showBranding', e.currentTarget.checked)}
                color={BRAND_RED}
                size="sm"
              />
            </Stack>
          </div>

          {/* Live Preview */}
          <div style={{ width: 320, flexShrink: 0 }}>
            <Text size="xs" fw={500} c="dimmed" mb={8}>Live Preview</Text>
            <Paper
              radius={widgetConfig.borderRadius}
              style={{
                width: 320,
                height: 460,
                overflow: 'hidden',
                border: `1px solid ${borderColor}`,
                display: 'flex',
                flexDirection: 'column',
                backgroundColor: panelBg,
              }}
            >
              {/* Header */}
              <div
                style={{
                  background: headerBg,
                  padding: '14px 16px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 10,
                }}
              >
                <div
                  style={{
                    width: 36,
                    height: 36,
                    borderRadius: '50%',
                    background: 'rgba(255,255,255,0.2)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#fff',
                    fontWeight: 700,
                    fontSize: 14,
                  }}
                >
                  AR
                </div>
                <div>
                  <div style={{ color: '#fff', fontSize: 14, fontWeight: 600 }}>
                    {widgetConfig.agentDisplayName || 'AI Assistant'}
                  </div>
                  <div style={{ color: 'rgba(255,255,255,0.8)', fontSize: 11 }}>
                    {widgetConfig.agentTitle || 'Here to help'}
                  </div>
                </div>
              </div>

              {/* Message area */}
              <div style={{ flex: 1, padding: 16, backgroundColor: msgAreaBg, overflowY: 'auto' }}>
                <div
                  style={{
                    backgroundColor: agentBubbleBg,
                    borderRadius: '12px 12px 12px 2px',
                    padding: '10px 14px',
                    maxWidth: '85%',
                    fontSize: 13,
                    lineHeight: 1.5,
                    color: agentBubbleText,
                  }}
                >
                  {widgetConfig.greetingMessage || 'Hi there! How can I help you today?'}
                </div>
              </div>

              {/* Input bar */}
              <div
                style={{
                  borderTop: `1px solid ${borderColor}`,
                  padding: '10px 12px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  backgroundColor: panelBg,
                }}
              >
                <div
                  style={{
                    flex: 1,
                    backgroundColor: msgAreaBg,
                    borderRadius: 20,
                    padding: '8px 14px',
                    fontSize: 13,
                    color: dk ? '#5C5C5C' : '#9ca3af',
                  }}
                >
                  Type a message...
                </div>
                <div
                  style={{
                    width: 32,
                    height: 32,
                    borderRadius: '50%',
                    background: headerBg,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="22" y1="2" x2="11" y2="13" /><polygon points="22 2 15 22 11 13 2 9 22 2" />
                  </svg>
                </div>
              </div>

              {/* Branding */}
              {widgetConfig.showBranding && (
                <div style={{ textAlign: 'center', padding: '4px 0 6px', fontSize: 10, color: dk ? '#5C5C5C' : '#9ca3af' }}>
                  Powered by Agent Red
                </div>
              )}
            </Paper>
          </div>
        </div>
      </Stack>
    );
  };

  // ---- Go Live review page ------------------------------------------------

  const renderGoLivePage = () => {
    const configSteps = steps.filter((s) => s.step !== 'go_live');
    const completedSteps = configSteps.filter((s) => s.completed);
    const incompleteSteps = configSteps.filter((s) => !s.completed);

    return (
      <Stack gap="lg">
        <Text fw={600} size="lg">
          Review & Activate
        </Text>
        <Text size="sm" c="dimmed">
          Review your setup before activating your AI agent.
        </Text>

        <Divider />

        {/* Completed steps */}
        {completedSteps.length > 0 && (
          <Stack gap="xs">
            <Text size="sm" fw={500} c="green">
              Completed Steps
            </Text>
            {completedSteps.map((step) => (
              <Group key={step.id} gap="sm">
                <Box
                  style={{
                    width: 20,
                    height: 20,
                    borderRadius: '50%',
                    backgroundColor: '#059669',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0,
                  }}
                >
                  <svg
                    width="12"
                    height="12"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="#fff"
                    strokeWidth="3"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                </Box>
                <Text size="sm">
                  {step.title} — {step.description}
                </Text>
              </Group>
            ))}
          </Stack>
        )}

        {/* Incomplete steps */}
        {incompleteSteps.length > 0 && (
          <Stack gap="xs">
            <Text size="sm" fw={500} c="yellow.8">
              Incomplete Steps
            </Text>
            {incompleteSteps.map((step) => (
              <Group key={step.id} gap="sm">
                <Box
                  style={{
                    width: 20,
                    height: 20,
                    borderRadius: '50%',
                    backgroundColor: '#D97706',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0,
                  }}
                >
                  <svg
                    width="12"
                    height="12"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="#fff"
                    strokeWidth="3"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <line x1="12" y1="9" x2="12" y2="13" />
                    <circle cx="12" cy="17" r="0.5" fill="#fff" />
                  </svg>
                </Box>
                <Text size="sm">
                  {step.title} — {step.description}
                </Text>
              </Group>
            ))}
          </Stack>
        )}

        <Divider />

        {!allComplete && (
          <Alert color="yellow" variant="light" title="Not ready yet">
            Complete all steps above before activating your AI agent. You can click any step in the
            sidebar to return to it.
          </Alert>
        )}

        <Text size="xs" c="dimmed">
          Your AI agent will start responding to customers immediately after activation.
        </Text>

        <Button
          color={BRAND_RED}
          size="lg"
          disabled={!allComplete}
          fullWidth
          onClick={() =>
            onNotify('Your AI agent is now live and responding to customers.', 'success')
          }
        >
          Activate AI Agent
        </Button>
      </Stack>
    );
  };

  // ---- Loading state ------------------------------------------------------

  if (stepsResult.loading) {
    return (
      <Stack gap="lg">
        <div>
          <Title order={2}>Setup Wizard</Title>
          <Text c="dimmed" size="sm">
            Complete these steps to get your AI agent ready
          </Text>
        </div>
        <Paper p="xl" radius="md" withBorder>
          <Stack gap="md" align="center" py="xl">
            <Loader size="sm" color={BRAND_RED} />
            <Text size="sm" c="dimmed">
              Loading onboarding steps...
            </Text>
          </Stack>
        </Paper>
      </Stack>
    );
  }

  // ---- Error state --------------------------------------------------------

  if (stepsResult.error) {
    return (
      <Stack gap="lg">
        <div>
          <Title order={2}>Setup Wizard</Title>
          <Text c="dimmed" size="sm">
            Complete these steps to get your AI agent ready
          </Text>
        </div>
        <Alert color="red" variant="light" title="Failed to load onboarding steps">
          {stepsResult.error}
        </Alert>
        <Button variant="light" color={BRAND_RED} onClick={stepsResult.refetch}>
          Retry
        </Button>
      </Stack>
    );
  }

  // ---- No steps available -------------------------------------------------

  if (steps.length <= 1) {
    // Only the Go Live step exists (no API steps returned)
    return (
      <Stack gap="lg">
        <div>
          <Title order={2}>Setup Wizard</Title>
          <Text c="dimmed" size="sm">
            Complete these steps to get your AI agent ready
          </Text>
        </div>
        <Alert color="blue" variant="light" title="No onboarding steps available">
          Your configuration may already be complete, or the onboarding API is not yet configured.
        </Alert>
      </Stack>
    );
  }

  // ---- Main render --------------------------------------------------------

  return (
    <Stack gap="lg">
      {/* Page header */}
      <div>
        <Title order={2}>Setup Wizard</Title>
        <Text c="dimmed" size="sm">
          Complete these steps to get your AI agent ready
        </Text>
      </div>

      {/* Overall progress */}
      <Paper p="md" radius="md" withBorder>
        <Group justify="space-between" mb={8}>
          <Text size="sm" fw={500}>
            {completedCount} of {totalSteps} steps completed
          </Text>
          <Badge variant="light" color={allComplete ? 'green' : 'blue'} size="sm">
            {progressPercent}%
          </Badge>
        </Group>
        <Progress
          value={progressPercent}
          size="sm"
          radius="xl"
          color={allComplete ? 'green' : BRAND_RED}
        />
      </Paper>

      {/* Main layout: Stepper (left) + Content (right) */}
      <div style={{ display: 'flex', gap: 24, alignItems: 'flex-start' }}>
        {/* Stepper sidebar */}
        <Paper
          p="md"
          radius="md"
          withBorder
          style={{ width: 280, flexShrink: 0 }}
        >
          <Stepper
            active={activeStep}
            onStepClick={setActiveStep}
            orientation="vertical"
            size="sm"
            color={BRAND_RED}
            styles={{
              step: { cursor: 'pointer' },
              stepIcon: { cursor: 'pointer' },
              stepLabel: { cursor: 'pointer' },
            }}
          >
            {steps.map((step, index) => (
              <Stepper.Step
                key={step.id}
                label={step.title}
                description={step.completed ? 'Completed' : step.description}
                completedIcon={
                  <svg
                    width="14"
                    height="14"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="3"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                }
                color={step.completed ? 'green' : index === activeStep ? BRAND_RED : 'gray'}
              />
            ))}
          </Stepper>
        </Paper>

        {/* Content area */}
        <Paper p="lg" radius="md" withBorder style={{ flex: 1, minWidth: 0 }}>
          {currentStep == null ? (
            <Text size="sm" c="dimmed">
              Select a step to begin.
            </Text>
          ) : isGoLive ? (
            renderGoLivePage()
          ) : (
            <Stack gap="lg">
              <div>
                <Group gap="sm" mb={4}>
                  <Text fw={600} size="lg">
                    {currentStep.title}
                  </Text>
                  {currentStep.completed && (
                    <Badge variant="light" color="green" size="xs">
                      Completed
                    </Badge>
                  )}
                </Group>
                <Text size="sm" c="dimmed">
                  {currentStep.description}
                </Text>
              </div>

              <Divider />

              {/* Form fields — custom renderers for escalation and widget steps */}
              {currentStep.step === 'escalation_rules' ? (
                renderEscalationStep()
              ) : currentStep.step === 'widget_appearance' ? (
                renderWidgetAppearanceStep()
              ) : (
                <Stack gap="md">
                  {(currentStep.fields ?? []).map((field, i) => renderField(field, i))}
                </Stack>
              )}

              {/* Navigation */}
              <Divider />
              <Group justify="space-between">
                <Button
                  variant="default"
                  onClick={handleBack}
                  disabled={activeStep === 0}
                >
                  Back
                </Button>
                <Group gap="sm">
                  {!currentStep.completed && (
                    <Button
                      color={BRAND_RED}
                      onClick={handleCompleteStep}
                      loading={saving}
                    >
                      Complete Step
                    </Button>
                  )}
                  {activeStep < totalSteps - 1 && (
                    <Button
                      variant={currentStep.completed ? 'filled' : 'light'}
                      color={BRAND_RED}
                      onClick={handleNext}
                    >
                      Next
                    </Button>
                  )}
                </Group>
              </Group>
            </Stack>
          )}
        </Paper>
      </div>
    </Stack>
  );
}
