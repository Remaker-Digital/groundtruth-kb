// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

import React, { useState, useMemo } from 'react';
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
  Alert,
  Table,
  Badge,
  Switch,
  Divider,
  Grid,
  Box,
} from '@mantine/core';
import {
  DEFAULT_TENANT_CONFIG,
  TenantConfig,
  CONFIG_ROLLOUTS,
  ConfigRollout,
} from '../../data/mockData';

const BRAND_RED = '#C41E2A';

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

// Icons as inline SVGs
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

const AlertTriangleIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
    <line x1="12" y1="9" x2="12" y2="13" />
    <line x1="12" y1="17" x2="12.01" y2="17" />
  </svg>
);

const RocketIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z" />
    <path d="M12 15l-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z" />
    <path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0" />
    <path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5" />
  </svg>
);

function getPreviewResponse(formality: string, responseLength: string, brandName: string): string {
  const styles: Record<string, Record<string, string>> = {
    casual: {
      concise: `Hey! Your ${brandName} order ships in 2-3 days. Need anything else?`,
      moderate: `Hey there! Great news - your ${brandName} order is being prepared and will ship within 2-3 business days. You'll get a tracking email as soon as it's on its way. Let me know if there's anything else I can help with!`,
      detailed: `Hey there! Thanks for reaching out about your order. Here's what's happening: your ${brandName} order is currently being packed up by our team and should ship within 2-3 business days. Once it ships, you'll get a tracking email with all the details so you can follow along. Standard delivery usually takes about 5-7 business days after that. If you need it faster, I can look into express options for you. Anything else on your mind?`,
    },
    professional: {
      concise: `Your ${brandName} order will ship within 2-3 business days. You'll receive tracking via email.`,
      moderate: `Thank you for your inquiry. Your ${brandName} order is being processed and will ship within 2-3 business days. You will receive a tracking confirmation email once the shipment is dispatched. Please don't hesitate to reach out if you need any further assistance.`,
      detailed: `Thank you for contacting ${brandName} support. I'd be happy to help with your order status.\n\nYour order is currently in our processing queue and will ship within 2-3 business days. Once dispatched, you will receive a tracking confirmation email with carrier details and an estimated delivery date. Standard delivery typically takes 5-7 business days.\n\nIf you require expedited shipping, I can explore available options for your location. Is there anything else I can assist you with?`,
    },
    formal: {
      concise: `Your ${brandName} order is scheduled for dispatch within 2-3 business days. Tracking details will be provided via email.`,
      moderate: `We appreciate your inquiry regarding your ${brandName} order. We are pleased to confirm that your order is currently being prepared for dispatch and will be shipped within 2-3 business days. A tracking confirmation will be sent to your registered email address upon dispatch. Should you require any additional assistance, please do not hesitate to contact us.`,
      detailed: `Dear valued customer,\n\nThank you for contacting ${brandName} customer support. We appreciate your patience and are pleased to provide the following update regarding your order.\n\nYour order is currently in the fulfillment stage of our processing workflow and is scheduled for dispatch within 2-3 business days. Upon dispatch, a comprehensive tracking confirmation, including carrier information and estimated delivery timeline, will be forwarded to your registered email address.\n\nStandard delivery is estimated at 5-7 business days from the date of dispatch. Should you wish to explore expedited shipping arrangements, we would be happy to present the available options.\n\nPlease do not hesitate to contact us should you require any further assistance.`,
    },
  };

  return styles[formality]?.[responseLength] || styles.professional.moderate;
}

function RolloutCard({ rollout }: { rollout: ConfigRollout }) {
  const isActive = rollout.status === 'active';
  const isReverted = rollout.status === 'reverted';
  const metricsA = rollout.metrics.groupA;
  const metricsB = rollout.metrics.groupB;

  return (
    <Paper p="md" radius="md" withBorder>
      <Group justify="space-between" mb="sm">
        <Group gap="sm">
          <Text fw={600} size="sm">{rollout.name}</Text>
          <Badge
            size="sm"
            variant="light"
            color={isActive ? 'blue' : isReverted ? 'red' : rollout.status === 'completed' ? 'green' : 'gray'}
          >
            {rollout.status}
          </Badge>
        </Group>
        <Text size="xs" c="dimmed">
          {rollout.startedAt
            ? new Date(rollout.startedAt).toLocaleDateString()
            : 'Not started'}
        </Text>
      </Group>

      {/* Traffic split and selection */}
      <Group gap="lg" mb="sm">
        <div>
          <Text size="xs" c="dimmed">Traffic to Group B</Text>
          <Text size="sm" fw={600}>{rollout.trafficSplit}%</Text>
        </div>
        <div>
          <Text size="xs" c="dimmed">Selection</Text>
          <Text size="sm" fw={600}>{rollout.selectionMethod}</Text>
        </div>
      </Group>

      {/* Changes being tested */}
      <Text size="xs" c="dimmed" mb={4}>Changes being tested:</Text>
      <Stack gap={4} mb="sm">
        {rollout.changes.map((change, i) => (
          <Group key={i} gap="xs">
            <Badge size="xs" variant="outline" color="gray">{change.field}</Badge>
            <Text size="xs" c="dimmed">
              {String(change.currentValue)} {'\u2192'} {String(change.newValue)}
            </Text>
          </Group>
        ))}
      </Stack>

      {/* Metrics comparison table */}
      <Table striped withTableBorder withColumnBorders mb="sm" fz="xs">
        <Table.Thead>
          <Table.Tr>
            <Table.Th>Metric</Table.Th>
            <Table.Th style={{ textAlign: 'right' }}>
              Group A ({100 - rollout.trafficSplit}%)
            </Table.Th>
            <Table.Th style={{ textAlign: 'right' }}>
              Group B ({rollout.trafficSplit}%)
            </Table.Th>
            <Table.Th style={{ textAlign: 'right' }}>Diff</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {[
            { label: 'Conversations', a: metricsA.conversations, b: metricsB.conversations, fmt: (v: number) => v.toLocaleString(), pct: false },
            { label: 'Satisfaction', a: metricsA.satisfaction, b: metricsB.satisfaction, fmt: (v: number) => v.toFixed(1), pct: false },
            { label: 'Resolution Rate', a: metricsA.resolutionRate, b: metricsB.resolutionRate, fmt: (v: number) => `${v}%`, pct: true },
            { label: 'Escalation Rate', a: metricsA.escalationRate, b: metricsB.escalationRate, fmt: (v: number) => `${v}%`, pct: true },
          ].map((row) => {
            const diff = row.b - row.a;
            // For escalation rate, lower is better
            const isImprovement =
              row.label === 'Escalation Rate' ? diff < 0 : diff > 0;
            return (
              <Table.Tr key={row.label}>
                <Table.Td>{row.label}</Table.Td>
                <Table.Td style={{ textAlign: 'right' }}>{row.fmt(row.a)}</Table.Td>
                <Table.Td style={{ textAlign: 'right' }}>{row.fmt(row.b)}</Table.Td>
                <Table.Td style={{ textAlign: 'right' }}>
                  <Text
                    size="xs"
                    fw={600}
                    c={Math.abs(diff) < 0.01 ? 'dimmed' : isImprovement ? 'green' : 'red'}
                  >
                    {diff > 0 ? '+' : ''}{row.pct ? `${diff.toFixed(1)}pp` : diff.toFixed(1)}
                  </Text>
                </Table.Td>
              </Table.Tr>
            );
          })}
        </Table.Tbody>
      </Table>

      {/* Auto-revert status */}
      <Group gap="xs" mb={isReverted ? 'sm' : 0}>
        <Text size="xs" c="dimmed">Auto-revert:</Text>
        <Badge size="xs" variant="light" color={rollout.autoRevert.enabled ? 'green' : 'gray'}>
          {rollout.autoRevert.enabled ? 'Enabled' : 'Disabled'}
        </Badge>
      </Group>

      {/* Revert reason alert */}
      {isReverted && rollout.autoRevert.revertReason && (
        <Alert
          color="red"
          variant="light"
          title="Auto-reverted"
          icon={<AlertTriangleIcon />}
          mt="sm"
        >
          <Text size="xs">{rollout.autoRevert.revertReason}</Text>
        </Alert>
      )}
    </Paper>
  );
}

export function ConfigurationPage() {
  const [config, setConfig] = useState<TenantConfig>({ ...DEFAULT_TENANT_CONFIG });
  const [hasChanges, setHasChanges] = useState(false);

  // Track changes
  const updateConfig = <K extends keyof TenantConfig>(key: K, value: TenantConfig[K]) => {
    setConfig((prev) => ({ ...prev, [key]: value }));
    setHasChanges(true);
  };

  const handleDiscard = () => {
    setConfig({ ...DEFAULT_TENANT_CONFIG });
    setHasChanges(false);
  };

  const handleSave = () => {
    // In a real app, this would POST to /api/config
    setHasChanges(false);
  };

  // Preview text
  const previewText = useMemo(
    () => getPreviewResponse(config.formality, config.responseLength, config.brandName),
    [config.formality, config.responseLength, config.brandName]
  );

  // Rollout data
  const activeRollout = CONFIG_ROLLOUTS.find((r) => r.status === 'active');
  const revertedRollout = CONFIG_ROLLOUTS.find((r) => r.status === 'reverted');

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
            disabled={!hasChanges}
            onClick={handleDiscard}
          >
            Discard
          </Button>
          <Button
            color={BRAND_RED}
            leftSection={<SaveIcon />}
            disabled={!hasChanges}
            onClick={handleSave}
          >
            Save Changes
          </Button>
        </Group>
      </Group>

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
                  value={config.brandName}
                  onChange={(e) => updateConfig('brandName', e.currentTarget.value)}
                />
                <Textarea
                  label="Brand Voice"
                  placeholder="Describe the personality and tone of your AI agent..."
                  value={config.brandVoice}
                  onChange={(e) => updateConfig('brandVoice', e.currentTarget.value)}
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
                    value={config.formality}
                    onChange={(val) =>
                      updateConfig('formality', (val || 'professional') as TenantConfig['formality'])
                    }
                  />
                  <Select
                    label="Response Length"
                    data={[
                      { value: 'concise', label: 'Concise' },
                      { value: 'moderate', label: 'Moderate' },
                      { value: 'detailed', label: 'Detailed' },
                    ]}
                    value={config.responseLength}
                    onChange={(val) =>
                      updateConfig('responseLength', (val || 'moderate') as TenantConfig['responseLength'])
                    }
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
                  value={config.returnWindow}
                  onChange={(val) => updateConfig('returnWindow', Number(val) || 30)}
                  min={0}
                  max={365}
                />
                <Textarea
                  label="Refund Policy"
                  placeholder="Describe your refund policy..."
                  value={config.refundPolicy}
                  onChange={(e) => updateConfig('refundPolicy', e.currentTarget.value)}
                  minRows={3}
                  autosize
                />
                <Textarea
                  label="Shipping Policy"
                  placeholder="Describe your shipping policy..."
                  value={config.shippingPolicy}
                  onChange={(e) => updateConfig('shippingPolicy', e.currentTarget.value)}
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
                    value={config.escalationThreshold}
                    onChange={(val) => updateConfig('escalationThreshold', val)}
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
                    value={config.autoEscalateTopics}
                    onChange={(val) => updateConfig('autoEscalateTopics', val)}
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
                    value={config.idleTimeoutMinutes}
                    onChange={(val) => updateConfig('idleTimeoutMinutes', Number(val) || 30)}
                    min={1}
                    max={120}
                  />
                  <NumberInput
                    label="Max Turns"
                    value={config.maxTurns}
                    onChange={(val) => updateConfig('maxTurns', Number(val) || 50)}
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
                value={config.customInstructions}
                onChange={(e) =>
                  updateConfig('customInstructions', e.currentTarget.value)
                }
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
                  value={config.primaryLanguage}
                  onChange={(val) => updateConfig('primaryLanguage', val || 'en')}
                />
                <div>
                  <Text size="sm" fw={500} mb={8}>
                    Supported Languages
                  </Text>
                  <Chip.Group
                    multiple
                    value={config.supportedLanguages}
                    onChange={(val) => updateConfig('supportedLanguages', val)}
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

        {/* Right column: Preview + Defensive Rollout */}
        <Grid.Col span={{ base: 12, lg: 5 }}>
          <Stack gap="lg">
            {/* Preview card */}
            <Paper p="lg" radius="md" withBorder>
              <Text fw={600} mb="xs">Preview</Text>
              <Text size="xs" c="dimmed" mb="md">
                How your AI will respond based on current settings
              </Text>
              <Paper
                p="sm"
                radius="md"
                style={{
                  backgroundColor: '#f8f9fa',
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
                    {config.formality} / {config.responseLength}
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

            {/* Defensive Rollout card */}
            <Paper p="lg" radius="md" withBorder>
              <Group justify="space-between" mb="md">
                <Group gap="xs">
                  <RocketIcon />
                  <Text fw={600}>Defensive Rollout</Text>
                </Group>
                <Button size="xs" variant="light" color={BRAND_RED}>
                  New Rollout
                </Button>
              </Group>

              <Text size="xs" c="dimmed" mb="md">
                Test configuration changes on a small percentage of traffic before
                rolling out to all customers.
              </Text>

              <Stack gap="md">
                {activeRollout && (
                  <div>
                    <Text size="xs" fw={600} c="dimmed" tt="uppercase" mb="xs">
                      Active
                    </Text>
                    <RolloutCard rollout={activeRollout} />
                  </div>
                )}

                {revertedRollout && (
                  <div>
                    <Divider my="xs" />
                    <Text size="xs" fw={600} c="dimmed" tt="uppercase" mb="xs">
                      Recent
                    </Text>
                    <RolloutCard rollout={revertedRollout} />
                  </div>
                )}
              </Stack>
            </Paper>
          </Stack>
        </Grid.Col>
      </Grid>
    </Stack>
  );
}
