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
} from '@mantine/core';
import { useAppContext } from '../layouts/StandaloneLayout';
import { useOnboardingSteps, useUpdateConfig } from '../../shared/hooks/index';
import type { ConfigFieldType } from '../../shared/types/index';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const BRAND_RED = '#ff3621';

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

  const [activeStep, setActiveStep] = useState(0);
  const [localValues, setLocalValues] = useState<Record<string, Record<string, unknown>>>({});
  const [completedOverrides, setCompletedOverrides] = useState<Record<string, boolean>>({});

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

    // Collect field key-value pairs
    const changes: Record<string, unknown> = {};
    for (const field of currentStep.fields) {
      changes[field.key] = field.value;
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
  }, [currentStep, isGoLive, updateConfig, onNotify, activeStep, totalSteps]);

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

              {/* Form fields */}
              <Stack gap="md">
                {(currentStep.fields ?? []).map((field, i) => renderField(field, i))}
              </Stack>

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
