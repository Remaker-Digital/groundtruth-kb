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
  Loader,
  Badge,
} from '@mantine/core';
import { useAppContext } from '../layouts/StandaloneLayout';
import { useConfig, useUpdateConfig } from '../../shared/hooks/index';
import { HelpTooltip } from '../../shared/HelpTooltip';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const BRAND_RED = '#ff3621';

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
    }
  }, [config]);

  const tier = tenantContext?.tier ?? 'starter';
  const isProOrHigher = tier === 'professional' || tier === 'enterprise';
  const isEnterprise = tier === 'enterprise';

  const handleSave = useCallback(async () => {
    // Field names must match backend config field registry
    const updates: Record<string, unknown> = {
      memory_enabled: memoryEnabled,
      pattern_learning_enabled: crossSessionLearning,
      data_retention_days: parseInt(retentionDays, 10),
      consent_collection_enabled: consentRequired,
    };

    const result = await updateConfig(updates);
    if (result?.success) {
      onNotify('Memory & privacy settings saved.', 'success');
      refreshActivationStatus();
    } else {
      onNotify(result?.message ?? 'Failed to save settings.', 'error');
    }
  }, [
    memoryEnabled, conversationMemory, crossSessionLearning, retentionDays,
    piiScrubbing, consentRequired, autoDeleteOnRequest, patternDecayDays,
    updateConfig, onNotify, refreshActivationStatus,
  ]);

  // Loading state
  if (loading && !fullConfig) {
    return (
      <Stack gap="lg" align="center" py="xl">
        <Loader size="md" color={BRAND_RED} />
        <Text c="dimmed" size="sm">Loading memory settings...</Text>
      </Stack>
    );
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
            color={BRAND_RED}
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
            color={BRAND_RED}
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
            color={BRAND_RED}
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
              color={BRAND_RED}
              mb="md"
              disabled={!memoryEnabled}
            />
            <HelpTooltip text="How long learned patterns remain active before decaying. Shorter values keep the AI more responsive to behavior changes; longer values provide more stable personalization." docLink="https://agentredcx.com/docs/admin-guide/customer-memory#pattern-learning" />
          </div>
        )}
      </Paper>

      {/* Layer 4: Dedicated model training */}
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
                color={BRAND_RED}
              />

              <Switch
                label="Consent required"
                description="Require explicit customer consent before storing conversation data. A consent prompt appears at the start of each conversation."
                checked={consentRequired}
                onChange={(e) => setConsentRequired(e.currentTarget.checked)}
                color={BRAND_RED}
              />

              <Switch
                label="Automatic deletion on request"
                description="Automatically delete all customer data when a GDPR deletion request is received."
                checked={autoDeleteOnRequest}
                onChange={(e) => setAutoDeleteOnRequest(e.currentTarget.checked)}
                color={BRAND_RED}
              />
            </Stack>
          </Accordion.Panel>
        </Accordion.Item>
      </Accordion>

      {/* Save draft inputs — persists field edits to draft state */}
      <Group justify="flex-end">
        <Button
          color={BRAND_RED}
          onClick={handleSave}
          loading={saving}
        >
          Save draft inputs
        </Button>
      </Group>
    </Stack>
  );
};
