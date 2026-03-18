// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

/**
 * A/B Testing page — Standalone admin (SPEC-0621, SPEC-0623, SPEC-0624, SPEC-0625, SPEC-0626).
 *
 * Multi-tab layout:
 *   1. Experiments — list + create wizard (SPEC-0623)
 *   2. KPI Dashboard — per-experiment metrics comparison (SPEC-0624)
 *   3. Review — merchant approval / rejection flow (SPEC-0626)
 *
 * Wizard steps (SPEC-0623): Audience → Schedule → Variant Config → Review & Launch.
 * "I'm Feeling Lucky" button calls AI suggestion endpoint (SPEC-0625).
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  Paper,
  Tabs,
  Table,
  Button,
  Group,
  Stack,
  Title,
  Text,
  Badge,
  Alert,
  Modal,
  Stepper,
  TextInput,
  Textarea,
  Select,
  Slider,
  NumberInput,
  JsonInput,
  ActionIcon,
  Tooltip,
  Progress,
  Card,
  SimpleGrid,
  ThemeIcon,
} from '@mantine/core';
import { useAppContext } from '../layouts/StandaloneLayout';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface VariantConfig {
  name: string;
  description: string;
  configOverrides: Record<string, unknown>;
}

interface Experiment {
  experimentId: string;
  tenantId: string;
  name: string;
  description: string;
  hypothesis: string;
  status: string;
  controlRatio: number;
  treatmentRatio: number;
  audienceMode: string;
  startDate: string | null;
  endDate: string | null;
  createdAt: string;
  concludedAt: string | null;
  metricKeys: string[];
  aiRationale: string;
  conclusionRecommendation: string | null;
}

interface KPIMetric {
  metricKey: string;
  controlValue: number;
  treatmentValue: number;
  statResult: {
    testName: string;
    statistic: number;
    pValue: number;
    effectSize: number;
    ciLower: number;
    ciUpper: number;
    significant: boolean;
    sampleSizeControl: number;
    sampleSizeTreatment: number;
  } | null;
}

// ---------------------------------------------------------------------------
// Status badge helper
// ---------------------------------------------------------------------------

const STATUS_COLORS: Record<string, string> = {
  draft: 'gray',
  pending_review: 'yellow',
  active: 'green',
  pending_conclusion: 'orange',
  concluded_promote: 'teal',
  concluded_rollback: 'red',
};

function StatusBadge({ status }: { status: string }) {
  return (
    <Badge color={STATUS_COLORS[status] || 'gray'} variant="light">
      {status.replace(/_/g, ' ')}
    </Badge>
  );
}

// ---------------------------------------------------------------------------
// Significance indicator
// ---------------------------------------------------------------------------

function SignificanceBadge({ pValue }: { pValue: number | null }) {
  if (pValue === null) return <Badge color="gray">No data</Badge>;
  if (pValue < 0.01) return <Badge color="green">Highly significant</Badge>;
  if (pValue < 0.05) return <Badge color="teal">Significant</Badge>;
  if (pValue < 0.10) return <Badge color="yellow">Marginal</Badge>;
  return <Badge color="gray">Not significant</Badge>;
}

// ---------------------------------------------------------------------------
// Main page component
// ---------------------------------------------------------------------------

export function ABTestingPage() {
  const { apiFetch, onNotify } = useAppContext();
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [loading, setLoading] = useState(false);
  const [wizardOpen, setWizardOpen] = useState(false);
  const [selectedExp, setSelectedExp] = useState<Experiment | null>(null);
  const [kpis, setKpis] = useState<KPIMetric[]>([]);

  // Wizard state (SPEC-0623: 4 steps)
  const [wizardStep, setWizardStep] = useState(0);
  const [wizardData, setWizardData] = useState({
    name: '',
    description: '',
    hypothesis: '',
    audienceMode: 'all',
    audiencePercentage: 100,
    startDate: '',
    endDate: '',
    controlName: 'Current Config',
    controlOverrides: '{}',
    treatmentName: 'Test Variant',
    treatmentOverrides: '{"quality_threshold": 4.0}',
    controlRatio: 80,
  });

  // -----------------------------------------------------------------------
  // API calls
  // -----------------------------------------------------------------------

  const fetchExperiments = useCallback(async () => {
    setLoading(true);
    try {
      const res = await apiFetch('/api/superadmin/experiments');
      if (res.ok) {
        setExperiments(await res.json());
      }
    } catch (e) {
      console.error('Failed to fetch experiments', e);
    } finally {
      setLoading(false);
    }
  }, [apiFetch]);

  useEffect(() => {
    fetchExperiments();
  }, [fetchExperiments]);

  const fetchKPIs = useCallback(async (expId: string) => {
    try {
      const res = await apiFetch(`/api/superadmin/experiments/${expId}/kpis`);
      if (res.ok) {
        const data = await res.json();
        setKpis(data.metrics || []);
      }
    } catch (e) {
      console.error('Failed to fetch KPIs', e);
    }
  }, [apiFetch]);

  // -----------------------------------------------------------------------
  // Wizard actions
  // -----------------------------------------------------------------------

  const createExperiment = async () => {
    try {
      const body = {
        name: wizardData.name,
        description: wizardData.description,
        hypothesis: wizardData.hypothesis,
        audienceMode: wizardData.audienceMode,
        audiencePercentage: wizardData.audiencePercentage,
        endDate: wizardData.endDate || null,
        controlRatio: wizardData.controlRatio / 100,
        control: {
          name: wizardData.controlName,
          description: 'Current production configuration',
          configOverrides: JSON.parse(wizardData.controlOverrides || '{}'),
        },
        treatment: {
          name: wizardData.treatmentName,
          description: wizardData.description,
          configOverrides: JSON.parse(wizardData.treatmentOverrides || '{}'),
        },
      };
      const res = await apiFetch('/api/superadmin/experiments', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (res.ok) {
        onNotify?.('Experiment created', 'success');
        setWizardOpen(false);
        setWizardStep(0);
        fetchExperiments();
      } else {
        const err = await res.json();
        onNotify?.(`Failed: ${err.detail || 'Unknown error'}`, 'error');
      }
    } catch (e) {
      onNotify?.('Failed to create experiment', 'error');
    }
  };

  // SPEC-0625: "I'm Feeling Lucky" — AI suggestion
  const suggestVariant = async () => {
    try {
      const res = await apiFetch('/api/superadmin/experiments/suggest-variant', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          currentConfig: JSON.parse(wizardData.controlOverrides || '{}'),
          commentary: wizardData.hypothesis,
        }),
      });
      if (res.ok) {
        const suggestion = await res.json();
        setWizardData(prev => ({
          ...prev,
          treatmentName: 'AI Suggested Variant',
          treatmentOverrides: JSON.stringify(suggestion.suggestedConfig || {}, null, 2),
        }));
        onNotify?.('AI suggestion applied!', 'success');
      } else {
        onNotify?.('Suggestion unavailable — try again later', 'warning');
      }
    } catch {
      onNotify?.('AI suggestion failed', 'error');
    }
  };

  // SPEC-0626: Lifecycle actions
  const performAction = async (expId: string, action: string) => {
    try {
      const res = await apiFetch(`/api/superadmin/experiments/${expId}/${action}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: action === 'finalize' ? JSON.stringify({ action: 'promote' }) : '{}',
      });
      if (res.ok) {
        onNotify?.(`Action "${action}" succeeded`, 'success');
        fetchExperiments();
      } else {
        const err = await res.json();
        onNotify?.(`Failed: ${err.detail}`, 'error');
      }
    } catch {
      onNotify?.(`Action "${action}" failed`, 'error');
    }
  };

  // -----------------------------------------------------------------------
  // Render
  // -----------------------------------------------------------------------

  return (
    <Stack gap="lg">
      <Group justify="space-between">
        <Title order={2}>A/B Testing</Title>
        <Button onClick={() => setWizardOpen(true)}>New Experiment</Button>
      </Group>

      <Tabs defaultValue="experiments">
        <Tabs.List>
          <Tabs.Tab value="experiments">Experiments</Tabs.Tab>
          <Tabs.Tab value="kpis">KPI Dashboard</Tabs.Tab>
          <Tabs.Tab value="review">Review &amp; Approve</Tabs.Tab>
        </Tabs.List>

        {/* Tab 1: Experiment List */}
        <Tabs.Panel value="experiments" pt="md">
          <Paper p="md" withBorder>
            <Table striped highlightOnHover>
              <Table.Thead>
                <Table.Tr>
                  <Table.Th>Name</Table.Th>
                  <Table.Th>Status</Table.Th>
                  <Table.Th>Split</Table.Th>
                  <Table.Th>Created</Table.Th>
                  <Table.Th>Actions</Table.Th>
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {experiments.map(exp => (
                  <Table.Tr key={exp.experimentId}>
                    <Table.Td>
                      <Text fw={500}>{exp.name}</Text>
                      <Text size="xs" c="dimmed">{exp.hypothesis}</Text>
                    </Table.Td>
                    <Table.Td><StatusBadge status={exp.status} /></Table.Td>
                    <Table.Td>{Math.round(exp.controlRatio * 100)}/{Math.round(exp.treatmentRatio * 100)}</Table.Td>
                    <Table.Td>{exp.createdAt ? new Date(exp.createdAt).toLocaleDateString() : '—'}</Table.Td>
                    <Table.Td>
                      <Group gap="xs">
                        <Button
                          size="xs"
                          variant="light"
                          onClick={() => {
                            setSelectedExp(exp);
                            fetchKPIs(exp.experimentId);
                          }}
                        >
                          View KPIs
                        </Button>
                      </Group>
                    </Table.Td>
                  </Table.Tr>
                ))}
                {experiments.length === 0 && (
                  <Table.Tr>
                    <Table.Td colSpan={5}>
                      <Text ta="center" c="dimmed" py="lg">
                        No experiments yet. Click "New Experiment" to get started.
                      </Text>
                    </Table.Td>
                  </Table.Tr>
                )}
              </Table.Tbody>
            </Table>
          </Paper>
        </Tabs.Panel>

        {/* Tab 2: KPI Dashboard (SPEC-0624) */}
        <Tabs.Panel value="kpis" pt="md">
          {selectedExp ? (
            <Stack gap="md">
              <Group justify="space-between">
                <div>
                  <Title order={3}>{selectedExp.name}</Title>
                  <Text c="dimmed">{selectedExp.hypothesis}</Text>
                </div>
                <StatusBadge status={selectedExp.status} />
              </Group>

              <SimpleGrid cols={3}>
                {kpis.map(kpi => (
                  <Card key={kpi.metricKey} withBorder padding="md">
                    <Text fw={500} tt="capitalize">
                      {kpi.metricKey.replace(/_/g, ' ')}
                    </Text>
                    <Group justify="space-between" mt="sm">
                      <div>
                        <Text size="xs" c="dimmed">Control</Text>
                        <Text size="lg" fw={700}>{kpi.controlValue.toFixed(2)}</Text>
                      </div>
                      <div>
                        <Text size="xs" c="dimmed">Treatment</Text>
                        <Text size="lg" fw={700}>{kpi.treatmentValue.toFixed(2)}</Text>
                      </div>
                    </Group>
                    <SignificanceBadge
                      pValue={kpi.statResult?.pValue ?? null}
                    />
                  </Card>
                ))}
              </SimpleGrid>

              {kpis.length === 0 && (
                <Alert color="blue">
                  No KPI data available yet. Metrics will appear once conversations
                  are processed with this experiment active.
                </Alert>
              )}
            </Stack>
          ) : (
            <Alert color="gray">
              Select an experiment from the Experiments tab to view KPIs.
            </Alert>
          )}
        </Tabs.Panel>

        {/* Tab 3: Review & Approve (SPEC-0626) */}
        <Tabs.Panel value="review" pt="md">
          <Stack gap="md">
            {experiments
              .filter(e => ['pending_review', 'pending_conclusion'].includes(e.status))
              .map(exp => (
                <Paper key={exp.experimentId} p="md" withBorder>
                  <Group justify="space-between">
                    <div>
                      <Title order={4}>{exp.name}</Title>
                      <Text size="sm" c="dimmed">{exp.description}</Text>
                      <StatusBadge status={exp.status} />
                    </div>
                    <Group>
                      {exp.status === 'pending_review' && (
                        <>
                          <Button
                            color="green"
                            onClick={() => performAction(exp.experimentId, 'approve')}
                          >
                            Approve &amp; Launch
                          </Button>
                          <Button
                            color="red"
                            variant="outline"
                            onClick={() => performAction(exp.experimentId, 'reject')}
                          >
                            Reject
                          </Button>
                        </>
                      )}
                      {exp.status === 'pending_conclusion' && (
                        <>
                          {exp.conclusionRecommendation && (
                            <Alert color="blue" mr="md">
                              AI recommends: {exp.conclusionRecommendation}
                            </Alert>
                          )}
                          <Button
                            color="teal"
                            onClick={() => performAction(exp.experimentId, 'finalize')}
                          >
                            Accept &amp; Promote
                          </Button>
                          <Button
                            color="red"
                            variant="outline"
                            onClick={() => performAction(exp.experimentId, 'reject')}
                          >
                            Continue Experiment
                          </Button>
                        </>
                      )}
                    </Group>
                  </Group>
                </Paper>
              ))}
            {experiments.filter(e =>
              ['pending_review', 'pending_conclusion'].includes(e.status)
            ).length === 0 && (
              <Alert color="gray">
                No experiments awaiting your review.
              </Alert>
            )}
          </Stack>
        </Tabs.Panel>
      </Tabs>

      {/* Wizard Modal (SPEC-0623: 4 steps) */}
      <Modal
        opened={wizardOpen}
        onClose={() => { setWizardOpen(false); setWizardStep(0); }}
        title="Create A/B Experiment"
        size="lg"
      >
        <Stepper active={wizardStep} onStepClick={setWizardStep}>
          {/* Step 1: Audience */}
          <Stepper.Step label="Audience" description="Who to include">
            <Stack gap="md" mt="md">
              <Select
                label="Audience Selection"
                data={[
                  { value: 'all', label: 'All customers' },
                  { value: 'percentage', label: 'Random percentage' },
                  { value: 'segment', label: 'Customer segment' },
                ]}
                value={wizardData.audienceMode}
                onChange={(v) => setWizardData(d => ({ ...d, audienceMode: v || 'all' }))}
              />
              {wizardData.audienceMode === 'percentage' && (
                <Slider
                  label="Percentage of customers"
                  min={1}
                  max={100}
                  value={wizardData.audiencePercentage}
                  onChange={(v) => setWizardData(d => ({ ...d, audiencePercentage: v }))}
                  marks={[{ value: 25, label: '25%' }, { value: 50, label: '50%' }, { value: 75, label: '75%' }]}
                />
              )}
            </Stack>
          </Stepper.Step>

          {/* Step 2: Schedule */}
          <Stepper.Step label="Schedule" description="When to run">
            <Stack gap="md" mt="md">
              <TextInput
                label="Start Date"
                type="date"
                value={wizardData.startDate}
                onChange={(e) => setWizardData(d => ({ ...d, startDate: e.target.value }))}
              />
              <TextInput
                label="End Date (optional)"
                type="date"
                value={wizardData.endDate}
                onChange={(e) => setWizardData(d => ({ ...d, endDate: e.target.value }))}
              />
              <Text size="xs" c="dimmed">
                Leave end date empty for manual conclusion.
              </Text>
            </Stack>
          </Stepper.Step>

          {/* Step 3: Variant Config */}
          <Stepper.Step label="Variants" description="What to test">
            <Stack gap="md" mt="md">
              <Slider
                label={`Traffic split: ${wizardData.controlRatio}% control / ${100 - wizardData.controlRatio}% treatment`}
                min={5}
                max={95}
                step={5}
                value={wizardData.controlRatio}
                onChange={(v) => setWizardData(d => ({ ...d, controlRatio: v }))}
              />
              <TextInput
                label="Control Variant Name"
                value={wizardData.controlName}
                onChange={(e) => setWizardData(d => ({ ...d, controlName: e.target.value }))}
              />
              <JsonInput
                label="Control Config Overrides"
                value={wizardData.controlOverrides}
                onChange={(v) => setWizardData(d => ({ ...d, controlOverrides: v }))}
                minRows={3}
              />
              <TextInput
                label="Treatment Variant Name"
                value={wizardData.treatmentName}
                onChange={(e) => setWizardData(d => ({ ...d, treatmentName: e.target.value }))}
              />
              <JsonInput
                label="Treatment Config Overrides"
                value={wizardData.treatmentOverrides}
                onChange={(v) => setWizardData(d => ({ ...d, treatmentOverrides: v }))}
                minRows={3}
              />
              {/* SPEC-0625: I'm Feeling Lucky */}
              <Button
                variant="gradient"
                gradient={{ from: 'orange', to: 'red' }}
                onClick={suggestVariant}
              >
                I&apos;m Feeling Lucky — AI Suggest
              </Button>
            </Stack>
          </Stepper.Step>

          {/* Step 4: Review & Launch */}
          <Stepper.Step label="Review" description="Confirm & launch">
            <Stack gap="md" mt="md">
              <TextInput
                label="Experiment Name"
                value={wizardData.name}
                onChange={(e) => setWizardData(d => ({ ...d, name: e.target.value }))}
                required
              />
              <Textarea
                label="Description"
                value={wizardData.description}
                onChange={(e) => setWizardData(d => ({ ...d, description: e.target.value }))}
              />
              <Textarea
                label="Hypothesis"
                placeholder="What do you expect this experiment to prove?"
                value={wizardData.hypothesis}
                onChange={(e) => setWizardData(d => ({ ...d, hypothesis: e.target.value }))}
              />

              <Paper p="sm" withBorder>
                <Text fw={500}>Summary</Text>
                <Text size="sm">Audience: {wizardData.audienceMode}</Text>
                <Text size="sm">Split: {wizardData.controlRatio}% / {100 - wizardData.controlRatio}%</Text>
                <Text size="sm">Control: {wizardData.controlName}</Text>
                <Text size="sm">Treatment: {wizardData.treatmentName}</Text>
                {wizardData.endDate && <Text size="sm">End: {wizardData.endDate}</Text>}
              </Paper>

              <Button
                size="lg"
                color="green"
                onClick={createExperiment}
                fullWidth
              >
                Create Experiment
              </Button>
            </Stack>
          </Stepper.Step>
        </Stepper>

        <Group justify="space-between" mt="xl">
          <Button
            variant="default"
            onClick={() => setWizardStep(s => Math.max(0, s - 1))}
            disabled={wizardStep === 0}
          >
            Back
          </Button>
          <Button
            onClick={() => setWizardStep(s => Math.min(3, s + 1))}
            disabled={wizardStep === 3}
          >
            Next
          </Button>
        </Group>
      </Modal>
    </Stack>
  );
}
