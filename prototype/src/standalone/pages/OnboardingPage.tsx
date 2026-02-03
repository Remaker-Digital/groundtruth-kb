// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

import React, { useState } from 'react';
import {
  Paper,
  Stepper,
  TextInput,
  Textarea,
  Select,
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
} from '@mantine/core';
import { notifications } from '@mantine/notifications';
import { ONBOARDING_STEPS, OnboardingStep } from '../../data/mockData';

const BRAND_RED = '#C41E2A';

function deepCloneSteps(steps: OnboardingStep[]): OnboardingStep[] {
  return steps.map((s) => ({
    ...s,
    fields: s.fields.map((f) => ({ ...f, value: f.value })),
  }));
}

export function OnboardingPage() {
  const [activeStep, setActiveStep] = useState(3); // zero-indexed: step 4 = Escalation
  const [steps, setSteps] = useState<OnboardingStep[]>(() => deepCloneSteps(ONBOARDING_STEPS));

  const completedCount = steps.filter((s) => s.completed).length;
  const totalSteps = steps.length;
  const progressPercent = Math.round((completedCount / totalSteps) * 100);
  const currentStep = steps[activeStep];

  const updateFieldValue = (fieldIndex: number, value: any) => {
    setSteps((prev) => {
      const updated = deepCloneSteps(prev);
      updated[activeStep].fields[fieldIndex].value = value;
      return updated;
    });
  };

  const handleCompleteStep = () => {
    setSteps((prev) => {
      const updated = deepCloneSteps(prev);
      updated[activeStep].completed = true;
      return updated;
    });
    notifications.show({
      title: 'Step completed',
      message: `"${currentStep.title}" has been saved successfully.`,
      color: 'green',
      autoClose: 3000,
    });
    if (activeStep < totalSteps - 1) {
      setActiveStep(activeStep + 1);
    }
  };

  const handleBack = () => {
    if (activeStep > 0) {
      setActiveStep(activeStep - 1);
    }
  };

  const handleNext = () => {
    if (activeStep < totalSteps - 1) {
      setActiveStep(activeStep + 1);
    }
  };

  const allComplete = steps.every((s) => s.completed);
  const isGoLive = activeStep === totalSteps - 1;

  const renderField = (
    field: { label: string; type: string; value: any; placeholder?: string; options?: string[] },
    fieldIndex: number
  ) => {
    switch (field.type) {
      case 'text':
        return (
          <TextInput
            key={fieldIndex}
            label={field.label}
            placeholder={field.placeholder || ''}
            value={field.value || ''}
            onChange={(e) => updateFieldValue(fieldIndex, e.currentTarget.value)}
          />
        );
      case 'textarea':
        return (
          <Textarea
            key={fieldIndex}
            label={field.label}
            placeholder={field.placeholder || ''}
            value={field.value || ''}
            onChange={(e) => updateFieldValue(fieldIndex, e.currentTarget.value)}
            minRows={3}
            autosize
          />
        );
      case 'url':
        return (
          <TextInput
            key={fieldIndex}
            label={field.label}
            placeholder={field.placeholder || 'https://'}
            value={field.value || ''}
            onChange={(e) => updateFieldValue(fieldIndex, e.currentTarget.value)}
            type="url"
          />
        );
      case 'select':
        return (
          <Select
            key={fieldIndex}
            label={field.label}
            placeholder="Select..."
            value={field.value || null}
            data={(field.options || []).map((opt) => ({
              value: opt,
              label: opt.charAt(0).toUpperCase() + opt.slice(1).replace(/-/g, ' '),
            }))}
            onChange={(val) => updateFieldValue(fieldIndex, val)}
            allowDeselect={false}
          />
        );
      case 'multiselect':
        return (
          <div key={fieldIndex}>
            <Text size="sm" fw={500} mb={6}>
              {field.label}
            </Text>
            <Chip.Group
              multiple
              value={field.value || []}
              onChange={(val) => updateFieldValue(fieldIndex, val)}
            >
              <Group gap="xs">
                {(field.options || []).map((opt) => (
                  <Chip key={opt} value={opt} size="sm" variant="outline" color={BRAND_RED}>
                    {opt.replace(/-/g, ' ')}
                  </Chip>
                ))}
              </Group>
            </Chip.Group>
          </div>
        );
      case 'number':
        return (
          <NumberInput
            key={fieldIndex}
            label={field.label}
            value={field.value ?? 0}
            onChange={(val) => updateFieldValue(fieldIndex, val)}
            min={0}
          />
        );
      case 'email':
        return (
          <TextInput
            key={fieldIndex}
            label={field.label}
            placeholder={field.placeholder || 'email@example.com'}
            value={field.value || ''}
            onChange={(e) => updateFieldValue(fieldIndex, e.currentTarget.value)}
            type="email"
          />
        );
      case 'color':
        return (
          <ColorInput
            key={fieldIndex}
            label={field.label}
            value={field.value || '#C41E2A'}
            onChange={(val) => updateFieldValue(fieldIndex, val)}
            format="hex"
          />
        );
      default:
        return (
          <TextInput
            key={fieldIndex}
            label={field.label}
            value={field.value || ''}
            onChange={(e) => updateFieldValue(fieldIndex, e.currentTarget.value)}
          />
        );
    }
  };

  const renderGoLivePage = () => {
    const completedSteps = steps.filter((s) => s.completed && s.id !== 9);
    const incompleteSteps = steps.filter((s) => !s.completed && s.id !== 9);

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
            notifications.show({
              title: 'AI Agent Activated',
              message: 'Your AI agent is now live and responding to customers.',
              color: 'green',
              autoClose: 5000,
            })
          }
        >
          Activate AI Agent
        </Button>
      </Stack>
    );
  };

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
          {isGoLive ? (
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
                {currentStep.fields.map((field, i) => renderField(field, i))}
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
                    <Button color={BRAND_RED} onClick={handleCompleteStep}>
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
