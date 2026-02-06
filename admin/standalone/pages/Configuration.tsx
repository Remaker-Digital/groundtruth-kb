// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

/**
 * Configuration page — Standalone admin.
 *
 * Two-column Mantine v7 layout adapted from the prototype ConfigurationPage.
 * Left column: 5 form sections (Brand & Persona, Policies, Escalation,
 * Custom Instructions, Language).
 * Right column: Preview card showing sample AI response.
 *
 * Data flows through useConfig / useUpdateConfig hooks instead of mock data.
 * Defensive Rollout section removed (no rollout API at launch).
 */

import React, { useState, useMemo, useEffect, useRef } from 'react';
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
  Grid,
  Box,
  Loader,
  Alert,
  useComputedColorScheme,
} from '@mantine/core';
import { useAppContext } from '../layouts/StandaloneLayout';
import { useConfig, useUpdateConfig } from '../../shared/hooks/index';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const BRAND_RED = '#ff3621';

const ESCALATION_TOPICS = [
  'refund-dispute',
  'legal-complaint',
  'safety-concern',
  'billing-issue',
  'account-deletion',
  'harassment',
  'fraud',
];

const LANGUAGES = [
  { value: 'en', label: 'English' },
  { value: 'es', label: 'Spanish' },
  { value: 'fr', label: 'French' },
  { value: 'de', label: 'German' },
  { value: 'pt', label: 'Portuguese' },
  { value: 'ja', label: 'Japanese' },
  { value: 'zh', label: 'Chinese' },
  { value: 'ko', label: 'Korean' },
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
  autoEscalateTopics: string[];
  idleTimeoutMinutes: number;
  maxTurns: number;
  customInstructions: string;
  primaryLanguage: string;
  supportedLanguages: string[];
}

const DEFAULTS: ConfigFormState = {
  brandName: '',
  brandVoice: '',
  formality: 'professional',
  responseLength: 'moderate',
  returnWindow: 30,
  refundPolicy: '',
  shippingPolicy: '',
  escalationThreshold: 0.7,
  autoEscalateTopics: ['refund-dispute', 'legal-complaint', 'safety-concern'],
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

// ---------------------------------------------------------------------------
// Preview response generator
// ---------------------------------------------------------------------------

function getPreviewResponse(formality: string, responseLength: string, brandName: string): string {
  const name = brandName || 'Your Store';
  const styles: Record<string, Record<string, string>> = {
    casual: {
      concise: `Hey! Your ${name} order ships in 2-3 days. Need anything else?`,
      moderate: `Hey there! Great news - your ${name} order is being prepared and will ship within 2-3 business days. You'll get a tracking email as soon as it's on its way. Let me know if there's anything else I can help with!`,
      detailed: `Hey there! Thanks for reaching out about your order. Here's what's happening: your ${name} order is currently being packed up by our team and should ship within 2-3 business days. Once it ships, you'll get a tracking email with all the details so you can follow along. Standard delivery usually takes about 5-7 business days after that. If you need it faster, I can look into express options for you. Anything else on your mind?`,
    },
    professional: {
      concise: `Your ${name} order will ship within 2-3 business days. You'll receive tracking via email.`,
      moderate: `Thank you for your inquiry. Your ${name} order is being processed and will ship within 2-3 business days. You will receive a tracking confirmation email once the shipment is dispatched. Please don't hesitate to reach out if you need any further assistance.`,
      detailed: `Thank you for contacting ${name} support. I'd be happy to help with your order status.\n\nYour order is currently in our processing queue and will ship within 2-3 business days. Once dispatched, you will receive a tracking confirmation email with carrier details and an estimated delivery date. Standard delivery typically takes 5-7 business days.\n\nIf you require expedited shipping, I can explore available options for your location. Is there anything else I can assist you with?`,
    },
    formal: {
      concise: `Your ${name} order is scheduled for dispatch within 2-3 business days. Tracking details will be provided via email.`,
      moderate: `We appreciate your inquiry regarding your ${name} order. We are pleased to confirm that your order is currently being prepared for dispatch and will be shipped within 2-3 business days. A tracking confirmation will be sent to your registered email address upon dispatch. Should you require any additional assistance, please do not hesitate to contact us.`,
      detailed: `Dear valued customer,\n\nThank you for contacting ${name} customer support. We appreciate your patience and are pleased to provide the following update regarding your order.\n\nYour order is currently in the fulfillment stage of our processing workflow and is scheduled for dispatch within 2-3 business days. Upon dispatch, a comprehensive tracking confirmation, including carrier information and estimated delivery timeline, will be forwarded to your registered email address.\n\nStandard delivery is estimated at 5-7 business days from the date of dispatch. Should you wish to explore expedited shipping arrangements, we would be happy to present the available options.\n\nPlease do not hesitate to contact us should you require any further assistance.`,
    },
  };

  return styles[formality]?.[responseLength] || styles.professional.moderate;
}

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

/** Build form state from the raw config record. */
function configToForm(cfg: Record<string, unknown> | undefined | null): ConfigFormState {
  if (!cfg) return { ...DEFAULTS };
  return {
    brandName: str(cfg.brandName, DEFAULTS.brandName),
    brandVoice: str(cfg.brandVoice, DEFAULTS.brandVoice),
    formality: str(cfg.formality, DEFAULTS.formality),
    responseLength: str(cfg.responseLength, DEFAULTS.responseLength),
    returnWindow: num(cfg.returnWindow, DEFAULTS.returnWindow),
    refundPolicy: str(cfg.refundPolicy, DEFAULTS.refundPolicy),
    shippingPolicy: str(cfg.shippingPolicy, DEFAULTS.shippingPolicy),
    escalationThreshold: num(cfg.escalationThreshold, DEFAULTS.escalationThreshold),
    autoEscalateTopics: strArr(cfg.autoEscalateTopics, DEFAULTS.autoEscalateTopics),
    idleTimeoutMinutes: num(cfg.idleTimeoutMinutes, DEFAULTS.idleTimeoutMinutes),
    maxTurns: num(cfg.maxTurns, DEFAULTS.maxTurns),
    customInstructions: str(cfg.customInstructions, DEFAULTS.customInstructions),
    primaryLanguage: str(cfg.primaryLanguage, DEFAULTS.primaryLanguage),
    supportedLanguages: strArr(cfg.supportedLanguages, DEFAULTS.supportedLanguages),
  };
}

/** Compute fields that differ between two form states. */
function diffForm(
  original: ConfigFormState,
  current: ConfigFormState,
): Record<string, unknown> {
  const changes: Record<string, unknown> = {};
  for (const key of Object.keys(current) as Array<keyof ConfigFormState>) {
    const origVal = original[key];
    const curVal = current[key];
    if (Array.isArray(origVal) && Array.isArray(curVal)) {
      if (origVal.length !== curVal.length || origVal.some((v, i) => v !== curVal[i])) {
        changes[key] = curVal;
      }
    } else if (origVal !== curVal) {
      changes[key] = curVal;
    }
  }
  return changes;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export const ConfigurationPage: React.FC = () => {
  const { apiFetch, onNotify } = useAppContext();
  const configResult = useConfig(apiFetch);
  const { updateConfig: saveConfig, loading: saving, error: saveError } = useUpdateConfig(apiFetch);

  const computedColorScheme = useComputedColorScheme('dark');
  const isDark = computedColorScheme === 'dark';
  const previewBg = isDark ? 'rgba(255,255,255,0.04)' : '#f8f9fa';

  // Form state
  const [form, setForm] = useState<ConfigFormState>({ ...DEFAULTS });
  const [hasChanges, setHasChanges] = useState(false);

  // Snapshot of the server state (used for discard and diff)
  const serverFormRef = useRef<ConfigFormState>({ ...DEFAULTS });

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

  const handleDiscard = () => {
    setForm({ ...serverFormRef.current });
    setHasChanges(false);
  };

  const handleSave = async () => {
    const changes = diffForm(serverFormRef.current, form);
    if (Object.keys(changes).length === 0) return;

    const result = await saveConfig(changes);
    if (result) {
      onNotify('Configuration saved successfully.', 'success');
      // Update server snapshot so discard reflects new saved state
      serverFormRef.current = { ...form };
      setHasChanges(false);
      configResult.refetch();
    } else {
      onNotify(saveError || 'Failed to save configuration.', 'error');
    }
  };

  // Preview text
  const previewText = useMemo(
    () => getPreviewResponse(form.formality, form.responseLength, form.brandName),
    [form.formality, form.responseLength, form.brandName],
  );

  // Loading state
  if (configResult.loading && !configResult.data) {
    return (
      <Stack align="center" justify="center" gap="md" py="xl">
        <Loader color={BRAND_RED} size="md" />
        <Text c="dimmed" size="sm">Loading configuration...</Text>
      </Stack>
    );
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
      <Group justify="space-between" align="flex-start" wrap="wrap">
        <div>
          <Title order={2}>Configuration</Title>
          <Text c="dimmed" size="sm">
            Fine-tune your AI agent's behavior
          </Text>
        </div>
        <Group gap="sm">
          <Button
            variant="default"
            leftSection={<UndoIcon />}
            disabled={!hasChanges || saving}
            onClick={handleDiscard}
          >
            Discard
          </Button>
          <Button
            color={BRAND_RED}
            leftSection={<SaveIcon />}
            disabled={!hasChanges}
            loading={saving}
            onClick={handleSave}
          >
            Save Changes
          </Button>
        </Group>
      </Group>

      {/* Save error banner */}
      {saveError && (
        <Alert color="red" variant="light" title="Save failed" withCloseButton onClose={() => {}}>
          <Text size="sm">{saveError}</Text>
        </Alert>
      )}

      {/* Two-column layout */}
      <Grid gutter="lg">
        {/* Left column: Configuration form */}
        <Grid.Col span={{ base: 12, lg: 7 }}>
          <Stack gap="lg">
            {/* Brand & Persona */}
            <Paper p="lg" radius="md" withBorder>
              <Text fw={600} mb="md">Brand & Persona</Text>
              <Stack gap="md">
                <TextInput
                  label="Brand Name"
                  placeholder="Your store or brand name"
                  value={form.brandName}
                  onChange={(e) => updateField('brandName', e.currentTarget.value)}
                />
                <Textarea
                  label="Brand Voice"
                  placeholder="Describe the personality and tone of your AI agent..."
                  value={form.brandVoice}
                  onChange={(e) => updateField('brandVoice', e.currentTarget.value)}
                  minRows={3}
                  autosize
                />
                <Group grow>
                  <Select
                    label="Formality"
                    data={[
                      { value: 'casual', label: 'Casual' },
                      { value: 'professional', label: 'Professional' },
                      { value: 'formal', label: 'Formal' },
                    ]}
                    value={form.formality}
                    onChange={(val) => updateField('formality', val || 'professional')}
                  />
                  <Select
                    label="Response Length"
                    data={[
                      { value: 'concise', label: 'Concise' },
                      { value: 'moderate', label: 'Moderate' },
                      { value: 'detailed', label: 'Detailed' },
                    ]}
                    value={form.responseLength}
                    onChange={(val) => updateField('responseLength', val || 'moderate')}
                  />
                </Group>
              </Stack>
            </Paper>

            {/* Policies */}
            <Paper p="lg" radius="md" withBorder>
              <Text fw={600} mb="md">Policies</Text>
              <Stack gap="md">
                <NumberInput
                  label="Return Window"
                  suffix=" days"
                  value={form.returnWindow}
                  onChange={(val) => updateField('returnWindow', Number(val) || 30)}
                  min={0}
                  max={365}
                />
                <Textarea
                  label="Refund Policy"
                  placeholder="Describe your refund policy..."
                  value={form.refundPolicy}
                  onChange={(e) => updateField('refundPolicy', e.currentTarget.value)}
                  minRows={3}
                  autosize
                />
                <Textarea
                  label="Shipping Policy"
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
              <Text fw={600} mb="md">Escalation</Text>
              <Stack gap="md">
                <div>
                  <Text size="sm" fw={500} mb={8}>
                    Escalation Threshold
                  </Text>
                  <Slider
                    value={form.escalationThreshold}
                    onChange={(val) => updateField('escalationThreshold', val)}
                    min={0}
                    max={1}
                    step={0.05}
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
                <div>
                  <Text size="sm" fw={500} mb={8}>
                    Auto-Escalate Topics
                  </Text>
                  <Chip.Group
                    multiple
                    value={form.autoEscalateTopics}
                    onChange={(val) => updateField('autoEscalateTopics', val)}
                  >
                    <Group gap="xs" wrap="wrap">
                      {ESCALATION_TOPICS.map((topic) => (
                        <Chip key={topic} value={topic} size="sm" color={BRAND_RED}>
                          {topic}
                        </Chip>
                      ))}
                    </Group>
                  </Chip.Group>
                </div>
                <Group grow>
                  <NumberInput
                    label="Idle Timeout"
                    suffix=" minutes"
                    value={form.idleTimeoutMinutes}
                    onChange={(val) => updateField('idleTimeoutMinutes', Number(val) || 30)}
                    min={1}
                    max={120}
                  />
                  <NumberInput
                    label="Max Turns"
                    value={form.maxTurns}
                    onChange={(val) => updateField('maxTurns', Number(val) || 50)}
                    min={5}
                    max={200}
                  />
                </Group>
              </Stack>
            </Paper>

            {/* Custom Instructions */}
            <Paper p="lg" radius="md" withBorder>
              <Text fw={600} mb="md">Custom Instructions</Text>
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
              <Text fw={600} mb="md">Language</Text>
              <Stack gap="md">
                <Select
                  label="Primary Language"
                  data={LANGUAGES}
                  value={form.primaryLanguage}
                  onChange={(val) => updateField('primaryLanguage', val || 'en')}
                />
                <div>
                  <Text size="sm" fw={500} mb={8}>
                    Supported Languages
                  </Text>
                  <Chip.Group
                    multiple
                    value={form.supportedLanguages}
                    onChange={(val) => updateField('supportedLanguages', val)}
                  >
                    <Group gap="xs" wrap="wrap">
                      {LANGUAGES.map((lang) => (
                        <Chip key={lang.value} value={lang.value} size="sm" color={BRAND_RED}>
                          {lang.label}
                        </Chip>
                      ))}
                    </Group>
                  </Chip.Group>
                </div>
              </Stack>
            </Paper>
          </Stack>
        </Grid.Col>

        {/* Right column: Preview */}
        <Grid.Col span={{ base: 12, lg: 5 }}>
          <Paper p="lg" radius="md" withBorder>
            <Text fw={600} mb="xs">Preview</Text>
            <Text size="xs" c="dimmed" mb="md">
              How your AI will respond based on current settings
            </Text>
            <Paper
              p="sm"
              radius="md"
              style={{
                backgroundColor: previewBg,
                borderLeft: `3px solid ${BRAND_RED}`,
              }}
            >
              <Group gap="xs" mb={8}>
                <Box
                  style={{
                    width: 24,
                    height: 24,
                    borderRadius: '50%',
                    background: BRAND_RED,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#fff',
                    fontSize: 10,
                    fontWeight: 700,
                  }}
                >
                  AR
                </Box>
                <Text size="xs" fw={600}>Agent Red AI</Text>
                <Badge size="xs" variant="light" color="gray">
                  {form.formality} / {form.responseLength}
                </Badge>
              </Group>
              <Text size="sm" style={{ whiteSpace: 'pre-wrap', lineHeight: 1.6 }}>
                {previewText}
              </Text>
            </Paper>
            <Text size="xs" c="dimmed" mt="sm" ta="center">
              Sample response to: "When will my order ship?"
            </Text>
          </Paper>
        </Grid.Col>
      </Grid>
    </Stack>
  );
};
