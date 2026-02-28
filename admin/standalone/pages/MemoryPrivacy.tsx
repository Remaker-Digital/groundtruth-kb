// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

/**
 * Memory & Privacy page — Standalone admin (WI #290).
 *
 * Provides configuration for:
 *   - Customer memory layer settings (Layers 1-4)
 *   - Data retention policies
 *   - GDPR consent management
 *   - PII scrubbing rules
 *
 * Uses the config API to read/write tenant configuration values.
 */

import React, { useState, useCallback, useEffect } from 'react';
import {
  Paper,
  Stack,
  Title,
  Text,
  Switch,
  Select,
  Slider,
  Button,
  Group,
  Accordion,
  Alert,
  Badge,
  SegmentedControl,
} from '@mantine/core';
import { useAppContext } from '../layouts/StandaloneLayout';
import { useConfig, useUpdateConfig } from '../../shared/hooks/index';
import { HelpTooltip } from '../../shared/HelpTooltip';
import { LoadingState } from '../../shared/LoadingState';
import { tokens } from '../../shared/theme/styles';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const ACTION_BLUE = tokens.action;

const RETENTION_OPTIONS = [
  { value: '30', label: '30 days' },
  { value: '90', label: '90 days' },
  { value: '180', label: '180 days' },
  { value: '365', label: '1 year' },
  { value: '730', label: '2 years' },
];

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export const MemoryPrivacyPage: React.FC = () => {
  const { apiFetch, onNotify, tenantContext, refreshActivationStatus } = useAppContext();
  const { data: fullConfig, loading, error } = useConfig(apiFetch);
  const { updateConfig, loading: saving } = useUpdateConfig(apiFetch);

  const config = fullConfig?.config ?? {};

  // Local state for form values
  const [memoryEnabled, setMemoryEnabled] = useState(false);
  const [conversationMemory, setConversationMemory] = useState(true);
  const [crossSessionLearning, setCrossSessionLearning] = useState(false);
  const [retentionDays, setRetentionDays] = useState('90');
  const [piiScrubbing, setPiiScrubbing] = useState(true);
  const [consentRequired, setConsentRequired] = useState(true);
  const [autoDeleteOnRequest, setAutoDeleteOnRequest] = useState(true);
  const [patternDecayDays, setPatternDecayDays] = useState(90);
  const [identificationMode, setIdentificationMode] = useState('standard');

  // Sync from config when loaded (field names match backend config registry)
  useEffect(() => {
    if (config) {
      setMemoryEnabled(config.memory_enabled === true);
      setConversationMemory(config.conversation_memory !== false);
      setCrossSessionLearning(config.pattern_learning_enabled === true);
      setRetentionDays(String(config.data_retention_days ?? '90'));
      setPiiScrubbing(config.pii_scrubbing !== false);
      setConsentRequired(config.consent_collection_enabled !== false);
      setAutoDeleteOnRequest(config.auto_delete_on_request !== false);
      setPatternDecayDays(Number(config.pattern_decay_days ?? 90));
      setIdentificationMode(String(config.customer_identification_mode ?? 'standard'));
    }
  }, [config]);

  const tier = tenantContext?.tier ?? 'starter';
  const isProOrHigher = tier === 'professional' || tier === 'enterprise';
  const isEnterprise = tier === 'enterprise';

  const handleSave = useCallback(async () => {
    // Field names must match backend config field registry.
    // Only include tier-gated fields when the tenant meets the gate.
    const updates: Record<string, unknown> = {
      memory_enabled: memoryEnabled,
      data_retention_days: parseInt(retentionDays, 10),
      pii_scrubbing: piiScrubbing,
      consent_collection_enabled: consentRequired,
      customer_identification_mode: identificationMode,
    };

    // Pro+ fields — only send when the tenant tier allows it
    if (isProOrHigher) {
      updates.pattern_learning_enabled = crossSessionLearning;
    }

    const result = await updateConfig(updates);
    if (result?.success) {
      onNotify('Draft memory & privacy settings saved.', 'success');
      refreshActivationStatus();
    } else {
      // Surface the actual validation error from the hook, not a generic fallback
      const detail = result?.message
        || error
        || 'Failed to save settings. Please check your plan tier and try again.';
      onNotify(detail, 'error');
    }
  }, [
    memoryEnabled, conversationMemory, crossSessionLearning, retentionDays,
    piiScrubbing, consentRequired, autoDeleteOnRequest, patternDecayDays,
    identificationMode, isProOrHigher, updateConfig, error, onNotify,
    refreshActivationStatus,
  ]);

  // Loading state
  if (loading && !fullConfig) {
    return <LoadingState text="Loading memory settings" />;
  }

  // Error state
  if (error && !fullConfig) {
    return (
      <Stack gap="lg">
        <Title order={2}>Memory & privacy</Title>
        <Alert color="red" title="Failed to load settings">
          {error}
        </Alert>
      </Stack>
    );
  }

  return (
    <Stack gap="lg">
      {/* Page header */}
      <div>
        <Title order={2}>Memory & privacy</Title>
        <Text c="dimmed" size="sm">
          Configure how your AI remembers customers and handles their data
        </Text>
      </div>

      {/* Upgrade banner for sub-Professional tiers */}
      {!isProOrHigher && (
        <Alert color="blue" variant="light" title="Unlock advanced memory features">
          <Text size="sm">
            Cross-session learning and dedicated model training are available on the Professional plan and above.
            Upgrade your plan to enable AI that learns and adapts to each customer over time.
          </Text>
        </Alert>
      )}

      {/* Layer 1: Customer context */}
      <Paper radius="md" withBorder p="lg">
        <Group justify="space-between" mb="md">
          <Group gap="xs">
            <Text fw={600} size="md">Customer context</Text>
            <Badge variant="light" color="green" size="xs">All tiers</Badge>
          </Group>
          <Switch
            checked={memoryEnabled}
            onChange={(e) => setMemoryEnabled(e.currentTarget.checked)}
            color={ACTION_BLUE}
            label={memoryEnabled ? 'Enabled' : 'Disabled'}
            labelPosition="left"
          />
        </Group>
        <Text c="dimmed" size="sm" mb="xs">
          Structured customer profiles (preferences, account state, interaction history)
          are injected into every conversation.
        </Text>
        <HelpTooltip text="Customer context provides the AI with information about each customer's previous interactions, preferences, and account status. This enables personalized responses without customers having to repeat themselves." docLink="https://agentredcx.com/docs/admin-guide/customer-memory#how-the-layers-work" />
      </Paper>

      {/* Layer 2: Conversation memory */}
      <Paper radius="md" withBorder p="lg">
        <Group justify="space-between" mb="md">
          <Group gap="xs">
            <Text fw={600} size="md">Conversation memory</Text>
            <Badge variant="light" color="green" size="xs">All tiers</Badge>
          </Group>
          <Switch
            checked={conversationMemory}
            onChange={(e) => setConversationMemory(e.currentTarget.checked)}
            color={ACTION_BLUE}
            label={conversationMemory ? 'Enabled' : 'Disabled'}
            labelPosition="left"
            disabled={!memoryEnabled}
          />
        </Group>
        <Text c="dimmed" size="sm" mb="xs">
          Vectorized conversation transcripts enable semantic search across a customer's
          full interaction history.
        </Text>
        <HelpTooltip text="Conversation memory stores previous chat transcripts as vector embeddings, allowing the AI to find and reference relevant past conversations. This helps provide consistent support across sessions." docLink="https://agentredcx.com/docs/admin-guide/customer-memory#memory-enabled" />
      </Paper>

      {/* Layer 3: Cross-session learning */}
      <Paper radius="md" withBorder p="lg">
        <Group justify="space-between" mb="md">
          <Group gap="xs">
            <Text fw={600} size="md">Cross-session learning</Text>
            {isProOrHigher ? (
              <Badge variant="light" color="blue" size="xs">Professional+</Badge>
            ) : (
              <Badge variant="light" color="gray" size="xs">Professional+ required</Badge>
            )}
          </Group>
          <Switch
            checked={crossSessionLearning}
            onChange={(e) => setCrossSessionLearning(e.currentTarget.checked)}
            color={ACTION_BLUE}
            label={crossSessionLearning ? 'Enabled' : 'Disabled'}
            labelPosition="left"
            disabled={!memoryEnabled || !isProOrHigher}
          />
        </Group>
        <Text c="dimmed" size="sm" mb="xs">
          The AI extracts and persists behavioral patterns, communication preferences,
          and interaction styles across sessions.
        </Text>
        <HelpTooltip text="Cross-session learning observes how each customer communicates over time — tone, vocabulary, topic patterns — and adapts future responses to match. Learned patterns decay gradually so the AI stays responsive to changing behavior." docLink="https://agentredcx.com/docs/admin-guide/customer-memory#pattern-learning" />
        {isProOrHigher && crossSessionLearning && (
          <div style={{ marginTop: 12 }}>
            <Text size="sm" fw={500} mb={4}>Pattern decay (days)</Text>
            <Slider
              value={patternDecayDays}
              onChange={setPatternDecayDays}
              min={30}
              max={365}
              step={30}
              marks={[
                { value: 30, label: '30' },
                { value: 90, label: '90' },
                { value: 180, label: '180' },
                { value: 365, label: '365' },
              ]}
              color={ACTION_BLUE}
              mb="md"
              disabled={!memoryEnabled}
            />
            <HelpTooltip text="How long learned patterns remain active before decaying. Shorter values keep the AI more responsive to behavior changes; longer values provide more stable personalization." docLink="https://agentredcx.com/docs/admin-guide/customer-memory#pattern-learning" />
          </div>
        )}
      </Paper>

      {/* Layer 4: Dedicated model training (SPEC-1523) */}
      <Paper radius="md" withBorder p="lg">
        <Group justify="space-between" mb="md">
          <Group gap="xs">
            <Text fw={600} size="md">Dedicated model training</Text>
            {isEnterprise ? (
              <Badge variant="light" color="grape" size="xs">Enterprise add-on</Badge>
            ) : (
              <Badge variant="light" color="gray" size="xs">Enterprise required</Badge>
            )}
          </Group>
          {isEnterprise && (
            <Switch
              label="Enable fine-tuning"
              checked={config?.fineTuningEnabled ?? false}
              onChange={(e) => handleConfigChange('fineTuningEnabled', e.currentTarget.checked)}
              color={ACTION_BLUE}
            />
          )}
        </Group>
        <Text c="dimmed" size="sm" mb="xs">
          Per-customer AI fine-tuning on 1,000+ historical interactions for maximum
          personalization. Available as an Enterprise add-on ($299/month).
        </Text>
        <HelpTooltip text="Dedicated model training creates a custom AI model for each customer using their historical interactions. This provides the highest level of personalization but requires a large conversation history (1,000+ interactions) and is billed as a separate Enterprise add-on." docLink="https://agentredcx.com/docs/admin-guide/customer-memory#dedicated-model-training" />
        {!isEnterprise && (
          <Alert color="blue" variant="light" mt="md">
            <Text size="sm">Upgrade to Enterprise tier to access dedicated model training.</Text>
          </Alert>
        )}
        {isEnterprise && config?.fineTuningEnabled && (
          <Stack mt="md" gap="md">
            <SegmentedControl
              value={config?.fineTuningSchedule ?? 'monthly'}
              onChange={(val) => handleConfigChange('fineTuningSchedule', val)}
              fullWidth
              data={[
                { value: 'monthly', label: 'Monthly' },
                { value: 'weekly', label: 'Weekly' },
                { value: 'manual', label: 'Manual only' },
              ]}
              color={ACTION_BLUE}
            />
            <Text size="xs" c="dimmed">Training schedule — how often the pipeline runs automatically.</Text>
            <NumberInput
              label="Minimum conversations"
              description="Minimum conversation count before training is eligible"
              value={config?.fineTuningMinConversations ?? 1000}
              onChange={(val) => handleConfigChange('fineTuningMinConversations', val)}
              min={100}
              max={10000}
              step={100}
            />
            <Button
              variant="light"
              color={ACTION_BLUE}
              onClick={() => {
                fetch('/api/admin/fine-tuning/trigger', { method: 'POST', headers: { 'Authorization': `Bearer ${apiKey}` } })
                  .then(r => r.json())
                  .then(() => notifications.show({ title: 'Training triggered', message: 'Fine-tuning pipeline started', color: 'green' }))
                  .catch(() => notifications.show({ title: 'Error', message: 'Failed to trigger training', color: 'red' }));
              }}
            >
              Trigger training now
            </Button>
            {config?.fineTuningActiveModelId && (
              <Alert color="green" variant="light">
                <Text size="sm">Active model: {config.fineTuningActiveModelId} (v{config.fineTuningActiveModelVersion})</Text>
              </Alert>
            )}
          </Stack>
        )}
      </Paper>

      {/* KA-8: Customer identification mode */}
      <Paper radius="md" withBorder p="lg">
        <Group justify="space-between" mb="md">
          <Group gap="xs">
            <Text fw={600} size="md">Customer identification</Text>
            <Badge variant="light" color="green" size="xs">All tiers</Badge>
          </Group>
        </Group>
        <Text c="dimmed" size="sm" mb="md">
          Controls how aggressively the AI prompts anonymous visitors to identify
          themselves (log in or provide an email). Identified customers get richer
          memory and personalization.
        </Text>
        <SegmentedControl
          value={identificationMode}
          onChange={setIdentificationMode}
          fullWidth
          data={[
            { value: 'off', label: 'Off' },
            { value: 'gentle', label: 'Gentle' },
            { value: 'standard', label: 'Standard' },
            { value: 'aggressive', label: 'Aggressive' },
          ]}
          color={ACTION_BLUE}
          mb="sm"
          disabled={!memoryEnabled}
        />
        <Text size="xs" c="dimmed">
          {identificationMode === 'off' && 'No identification prompt. The AI will not ask visitors to log in or provide contact information.'}
          {identificationMode === 'gentle' && 'Casual mention. The AI may casually note that logging in helps with personalization, but will not push.'}
          {identificationMode === 'standard' && 'Standard prompt. The AI\'s first response suggests logging in or providing an email to access order history and personalized support.'}
          {identificationMode === 'aggressive' && 'Strong prompt. The AI\'s first response includes a clear authentication suggestion and asks probing questions about interests and recent orders.'}
        </Text>
        {!memoryEnabled && (
          <Alert color="yellow" variant="light" mt="sm">
            <Text size="xs">Enable customer context above to use identification prompts.</Text>
          </Alert>
        )}
        <HelpTooltip text="Customer identification helps your AI build richer memory profiles. When customers identify themselves, the AI can access their order history, preferences, and past interactions — enabling more personalized and effective support." docLink="https://agentredcx.com/docs/admin-guide/customer-memory#identification" />
      </Paper>

      {/* Privacy & data retention */}
      <Accordion variant="separated" radius="md" defaultValue="privacy">
        <Accordion.Item value="privacy">
          <Accordion.Control>
            <Group gap="xs">
              <Text fw={600} size="md">Data retention & privacy</Text>
              <HelpTooltip text="Controls how long customer conversation data is stored, whether personally identifiable information is automatically redacted, and how GDPR data requests are handled. These settings apply to all customers on your account." docLink="https://agentredcx.com/docs/admin-guide/data-retention" />
            </Group>
          </Accordion.Control>
          <Accordion.Panel>
            <Stack gap="md">
              <Select
                label="Data retention period"
                description="How long conversation data is retained before automatic deletion."
                value={retentionDays}
                onChange={(val) => setRetentionDays(val ?? '90')}
                data={RETENTION_OPTIONS}
                allowDeselect={false}
              />

              <Switch
                label="PII scrubbing"
                description="Automatically detect and redact personally identifiable information (emails, phone numbers, addresses) from stored conversations."
                checked={piiScrubbing}
                onChange={(e) => setPiiScrubbing(e.currentTarget.checked)}
                color={ACTION_BLUE}
              />

              <Switch
                label="Consent required"
                description="Require explicit customer consent before storing conversation data. A consent prompt appears at the start of each conversation."
                checked={consentRequired}
                onChange={(e) => setConsentRequired(e.currentTarget.checked)}
                color={ACTION_BLUE}
              />

              <Switch
                label="Automatic deletion on request"
                description="Automatically delete all customer data when a GDPR deletion request is received."
                checked={autoDeleteOnRequest}
                onChange={(e) => setAutoDeleteOnRequest(e.currentTarget.checked)}
                color={ACTION_BLUE}
              />
            </Stack>
          </Accordion.Panel>
        </Accordion.Item>
      </Accordion>

      {/* Save draft inputs — persists field edits to draft state */}
      <Group justify="flex-end">
        <Button
          color={ACTION_BLUE}
          onClick={handleSave}
          loading={saving}
        >
          Save draft inputs
        </Button>
      </Group>
    </Stack>
  );
};
