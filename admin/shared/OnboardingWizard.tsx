/**
 * OnboardingWizard — 9-step merchant onboarding wizard.
 *
 * Guides new merchants through initial configuration with a step-by-step
 * interface.  Each step fetches its field definitions from the backend schema
 * endpoint, renders appropriate form controls, and saves changes via PUT
 * /api/config.
 *
 * Steps:
 *   1. Brand & Tone            5. Business Policies     9. Widget Appearance
 *   2. Languages                6. Escalation Rules
 *   3. Response Style           7. Integrations
 *   4. Knowledge Base           8. Memory & Privacy
 *
 * Props (from shell):
 *   - tenantContext — authenticated tenant information
 *   - apiFetch     — shell-provided fetch wrapper with auth
 *   - onNotify     — shell toast/banner callback
 *   - onComplete   — called when merchant finishes onboarding
 *
 * Dependencies:
 *   - ../types   — BaseComponentProps, OnboardingStep, OnboardingStepConfig, ConfigField
 *   - ../hooks   — useOnboardingSteps, useUpdateConfig, useConfigSchema
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useState, useCallback, useEffect, useMemo } from 'react';
import type {
  BaseComponentProps,
  OnboardingStep,
  OnboardingStepConfig,
  ConfigField,
  ConfigFieldType,
} from '../types';
import { useOnboardingSteps, useUpdateConfig, useConfigSchema } from '../hooks';

// ---------------------------------------------------------------------------
// Step metadata — display labels for each onboarding step
// ---------------------------------------------------------------------------

const STEP_ORDER: OnboardingStep[] = [
  'brand_and_tone',
  'ai_behavior',
  'escalation',
  'integrations',
  'knowledge_base',
  'response_policies',
  'customer_memory',
  'notifications',
  'widget_appearance',
];

const STEP_LABELS: Record<OnboardingStep, string> = {
  brand_and_tone: 'Brand & Tone',
  ai_behavior: 'AI Behavior',
  escalation: 'Escalation Rules',
  integrations: 'Integrations',
  knowledge_base: 'Knowledge Base',
  response_policies: 'Response Policies',
  customer_memory: 'Customer Memory',
  notifications: 'Notifications',
  widget_appearance: 'Widget Appearance',
};

const STEP_DESCRIPTIONS: Record<OnboardingStep, string> = {
  brand_and_tone:
    'Set your brand name, voice, and personality so the AI represents your business authentically.',
  ai_behavior:
    'Configure how the AI responds: formality, response length, and model behavior.',
  escalation:
    'Define when and how conversations are escalated to human agents.',
  integrations:
    'Connect your Shopify store, Zendesk, Mailchimp, and other services.',
  knowledge_base:
    'Upload FAQs, product information, and policies for the AI to reference.',
  response_policies:
    'Set business policies like return windows, shipping info, and support hours.',
  customer_memory:
    'Configure how the AI remembers customers across conversations.',
  notifications:
    'Set up alert thresholds and notification preferences.',
  widget_appearance:
    'Customize the chat widget colors, position, and behavior on your storefront.',
};

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

export interface OnboardingWizardProps extends BaseComponentProps {
  /** Called when the merchant finishes (or explicitly skips) the entire wizard. */
  onComplete: () => void;
}

// ---------------------------------------------------------------------------
// Styles (inline, framework-agnostic)
// ---------------------------------------------------------------------------

const styles = {
  container: {
    maxWidth: 780,
    margin: '0 auto',
    fontFamily:
      "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    color: '#1a1a1a',
  } as React.CSSProperties,

  header: {
    marginBottom: 32,
  } as React.CSSProperties,

  title: {
    fontSize: 24,
    fontWeight: 600,
    marginBottom: 4,
    color: '#1a1a1a',
  } as React.CSSProperties,

  subtitle: {
    fontSize: 14,
    color: '#666',
    marginTop: 0,
  } as React.CSSProperties,

  progressBar: {
    display: 'flex',
    gap: 4,
    marginBottom: 32,
  } as React.CSSProperties,

  progressSegment: (active: boolean, completed: boolean): React.CSSProperties => ({
    flex: 1,
    height: 6,
    borderRadius: 3,
    backgroundColor: completed ? '#C41E2A' : active ? '#e8939a' : '#e0e0e0',
    transition: 'background-color 0.25s ease',
  }),

  stepIndicator: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 24,
  } as React.CSSProperties,

  stepCount: {
    fontSize: 13,
    color: '#888',
    fontWeight: 500,
  } as React.CSSProperties,

  stepLabel: {
    fontSize: 18,
    fontWeight: 600,
    color: '#1a1a1a',
    margin: '0 0 6px 0',
  } as React.CSSProperties,

  stepDescription: {
    fontSize: 14,
    color: '#555',
    lineHeight: 1.5,
    margin: '0 0 24px 0',
  } as React.CSSProperties,

  fieldsContainer: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: 20,
    marginBottom: 32,
  } as React.CSSProperties,

  fieldGroup: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: 6,
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
    transition: 'border-color 0.15s ease',
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
    minHeight: 80,
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
    accentColor: '#C41E2A',
    cursor: 'pointer',
  } as React.CSSProperties,

  colorRow: {
    display: 'flex',
    alignItems: 'center',
    gap: 12,
  } as React.CSSProperties,

  colorSwatch: {
    width: 40,
    height: 40,
    border: '1px solid #d0d0d0',
    borderRadius: 6,
    padding: 2,
    cursor: 'pointer',
    backgroundColor: '#fff',
  } as React.CSSProperties,

  colorHex: {
    fontSize: 13,
    fontFamily: "'JetBrains Mono', monospace",
    color: '#555',
  } as React.CSSProperties,

  buttonRow: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: 16,
    borderTop: '1px solid #eee',
  } as React.CSSProperties,

  buttonPrimary: {
    padding: '10px 24px',
    fontSize: 14,
    fontWeight: 600,
    backgroundColor: '#C41E2A',
    color: '#fff',
    border: 'none',
    borderRadius: 6,
    cursor: 'pointer',
    transition: 'opacity 0.15s ease',
  } as React.CSSProperties,

  buttonSecondary: {
    padding: '10px 24px',
    fontSize: 14,
    fontWeight: 500,
    backgroundColor: 'transparent',
    color: '#555',
    border: '1px solid #d0d0d0',
    borderRadius: 6,
    cursor: 'pointer',
  } as React.CSSProperties,

  buttonSkip: {
    padding: '10px 16px',
    fontSize: 13,
    fontWeight: 400,
    backgroundColor: 'transparent',
    color: '#888',
    border: 'none',
    cursor: 'pointer',
    textDecoration: 'underline' as const,
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

  emptyStep: {
    padding: '40px 20px',
    textAlign: 'center' as const,
    color: '#888',
    fontSize: 14,
  } as React.CSSProperties,

  tierBadge: {
    display: 'inline-block',
    fontSize: 11,
    fontWeight: 600,
    textTransform: 'uppercase' as const,
    padding: '2px 8px',
    borderRadius: 4,
    backgroundColor: '#f0f0f0',
    color: '#888',
    marginLeft: 8,
  } as React.CSSProperties,

  completedDot: {
    display: 'inline-block',
    width: 8,
    height: 8,
    borderRadius: '50%',
    backgroundColor: '#16a34a',
    marginRight: 6,
  } as React.CSSProperties,
} as const;

// ---------------------------------------------------------------------------
// Field renderer
// ---------------------------------------------------------------------------

interface FieldRendererProps {
  field: ConfigField;
  value: unknown;
  onChange: (key: string, value: unknown) => void;
  disabled: boolean;
  tenantTier: string;
}

const FieldRenderer: React.FC<FieldRendererProps> = ({
  field,
  value,
  onChange,
  disabled,
  tenantTier,
}) => {
  // Tier gate: if field requires a higher tier, show it as locked
  const tierOrder = ['trial', 'starter', 'professional', 'enterprise'];
  const tenantTierIndex = tierOrder.indexOf(tenantTier);
  const fieldTierIndex = field.tierGate ? tierOrder.indexOf(field.tierGate) : 0;
  const isLocked = fieldTierIndex > tenantTierIndex;

  const effectiveDisabled = disabled || isLocked;

  const handleChange = useCallback(
    (newValue: unknown) => {
      if (!effectiveDisabled) {
        onChange(field.key, newValue);
      }
    },
    [field.key, onChange, effectiveDisabled],
  );

  const renderInput = (): React.ReactNode => {
    const fieldType: ConfigFieldType = field.type;

    switch (fieldType) {
      case 'boolean':
        return (
          <label style={styles.checkboxRow}>
            <input
              type="checkbox"
              style={styles.checkbox}
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
              ...styles.select,
              ...(effectiveDisabled ? { opacity: 0.6, cursor: 'not-allowed' } : {}),
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
          <div style={styles.colorRow}>
            <input
              type="color"
              style={styles.colorSwatch}
              value={String(value ?? '#000000')}
              onChange={(e) => handleChange(e.target.value)}
              disabled={effectiveDisabled}
            />
            <span style={styles.colorHex}>{String(value ?? '#000000')}</span>
          </div>
        );

      case 'textarea':
        return (
          <textarea
            style={{
              ...styles.textarea,
              ...(effectiveDisabled ? { opacity: 0.6, cursor: 'not-allowed' } : {}),
            }}
            value={String(value ?? '')}
            onChange={(e) => handleChange(e.target.value)}
            disabled={effectiveDisabled}
            rows={4}
          />
        );

      case 'number':
        return (
          <input
            type="number"
            style={{
              ...styles.input,
              ...(effectiveDisabled ? { opacity: 0.6, cursor: 'not-allowed' } : {}),
            }}
            value={value !== undefined && value !== null ? String(value) : ''}
            onChange={(e) => handleChange(e.target.value === '' ? null : Number(e.target.value))}
            disabled={effectiveDisabled}
          />
        );

      case 'json':
        return (
          <textarea
            style={{
              ...styles.textarea,
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: 13,
              ...(effectiveDisabled ? { opacity: 0.6, cursor: 'not-allowed' } : {}),
            }}
            value={
              typeof value === 'string'
                ? value
                : value !== undefined && value !== null
                  ? JSON.stringify(value, null, 2)
                  : ''
            }
            onChange={(e) => {
              try {
                handleChange(JSON.parse(e.target.value));
              } catch {
                // Allow intermediate invalid JSON while typing
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
              ...styles.input,
              ...(effectiveDisabled ? { opacity: 0.6, cursor: 'not-allowed' } : {}),
            }}
            value={String(value ?? '')}
            onChange={(e) => handleChange(e.target.value)}
            disabled={effectiveDisabled}
          />
        );
    }
  };

  return (
    <div style={styles.fieldGroup}>
      <label style={styles.label}>
        {field.label}
        {isLocked && field.tierGate && (
          <span style={styles.tierBadge}>{field.tierGate}+</span>
        )}
      </label>
      {field.description && <p style={styles.description}>{field.description}</p>}
      {renderInput()}
    </div>
  );
};

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export const OnboardingWizard: React.FC<OnboardingWizardProps> = ({
  tenantContext,
  apiFetch,
  onNotify,
  onComplete,
}) => {
  // ---- state ----
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [fieldValues, setFieldValues] = useState<Record<string, unknown>>({});
  const [saving, setSaving] = useState(false);
  const [completedSteps, setCompletedSteps] = useState<Set<number>>(new Set());

  // ---- hooks ----
  const {
    data: onboardingData,
    loading: stepsLoading,
    error: stepsError,
    refetch: refetchSteps,
  } = useOnboardingSteps(apiFetch);

  const { updateConfig, loading: updateLoading, error: updateError } = useUpdateConfig(apiFetch);

  // Current step key
  const currentStepKey = STEP_ORDER[currentStepIndex];

  // Fetch schema for the current step (step numbers are 1-indexed on the backend).
  // Map our step key to the backend step number.  The backend uses integer step
  // numbers matching the OnboardingStep enum.  We map by finding the step in the
  // onboarding response or falling back to index + 1.
  const backendStepNumber = useMemo(() => {
    if (!onboardingData?.steps) return currentStepIndex + 1;
    const match = onboardingData.steps.find((s) => s.step === currentStepKey);
    if (match) {
      // The backend step number is derived from the OnboardingStepConfig.
      // If the step config includes a numeric identifier we use it; otherwise
      // fall back to position.
      return currentStepIndex + 1;
    }
    return currentStepIndex + 1;
  }, [onboardingData, currentStepKey, currentStepIndex]);

  const {
    data: schemaData,
    loading: schemaLoading,
    error: schemaError,
  } = useConfigSchema(apiFetch, String(backendStepNumber));

  // ---- derive fields for current step ----
  const currentFields: ConfigField[] = useMemo(() => {
    // Prefer the onboarding endpoint's per-step field list
    if (onboardingData?.steps) {
      const stepConfig = onboardingData.steps.find((s) => s.step === currentStepKey);
      if (stepConfig && stepConfig.fields.length > 0) {
        return stepConfig.fields;
      }
    }

    // Fallback: use the schema endpoint response
    if (schemaData?.fields) {
      return schemaData.fields.map((raw: Record<string, unknown>) => ({
        key: String(raw.key ?? raw.field_name ?? ''),
        label: String(raw.label ?? raw.field_name ?? ''),
        description: String(raw.description ?? raw.tooltip ?? ''),
        type: (raw.type ?? raw.field_type ?? 'string') as ConfigFieldType,
        defaultValue: raw.default_value ?? raw.defaultValue ?? null,
        currentValue: raw.current_value ?? raw.currentValue ?? raw.default_value ?? null,
        options: Array.isArray(raw.options)
          ? raw.options.map((o: unknown) => {
              if (typeof o === 'object' && o !== null && 'value' in o) {
                return o as { value: string; label: string };
              }
              return { value: String(o), label: String(o) };
            })
          : undefined,
        tierGate: raw.tier_gate ?? raw.tierGate ?? undefined,
        stepOrder: Number(raw.step_order ?? raw.stepOrder ?? 0),
        group: String(raw.group ?? currentStepKey),
      })) as ConfigField[];
    }

    return [];
  }, [onboardingData, schemaData, currentStepKey]);

  // ---- initialise field values when step fields load ----
  useEffect(() => {
    if (currentFields.length === 0) return;

    const initial: Record<string, unknown> = {};
    for (const field of currentFields) {
      // Prefer currentValue (from the existing config) over defaultValue
      initial[field.key] =
        field.currentValue !== undefined && field.currentValue !== null
          ? field.currentValue
          : field.defaultValue;
    }
    setFieldValues(initial);
  }, [currentFields]);

  // ---- mark steps already completed from onboarding data ----
  useEffect(() => {
    if (!onboardingData?.steps) return;
    const done = new Set<number>();
    STEP_ORDER.forEach((stepKey, idx) => {
      const stepConfig = onboardingData.steps.find((s) => s.step === stepKey);
      if (stepConfig?.isComplete) {
        done.add(idx);
      }
    });
    setCompletedSteps(done);
  }, [onboardingData]);

  // ---- handlers ----
  const handleFieldChange = useCallback((key: string, value: unknown) => {
    setFieldValues((prev) => ({ ...prev, [key]: value }));
  }, []);

  const handleSave = useCallback(async () => {
    if (saving || updateLoading) return;
    setSaving(true);

    try {
      const result = await updateConfig(fieldValues);
      if (result?.success) {
        onNotify(`${STEP_LABELS[currentStepKey]} saved successfully.`, 'success');
        setCompletedSteps((prev) => new Set(prev).add(currentStepIndex));

        // Advance to next step or finish
        if (currentStepIndex < STEP_ORDER.length - 1) {
          setCurrentStepIndex((i) => i + 1);
        } else {
          onNotify('Onboarding complete! Your AI assistant is ready.', 'success');
          onComplete();
        }
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
    updateConfig,
    fieldValues,
    onNotify,
    currentStepKey,
    currentStepIndex,
    onComplete,
  ]);

  const handlePrev = useCallback(() => {
    if (currentStepIndex > 0) {
      setCurrentStepIndex((i) => i - 1);
    }
  }, [currentStepIndex]);

  const handleSkip = useCallback(() => {
    if (currentStepIndex < STEP_ORDER.length - 1) {
      setCurrentStepIndex((i) => i + 1);
    } else {
      onComplete();
    }
  }, [currentStepIndex, onComplete]);

  // ---- loading state ----
  if (stepsLoading && !onboardingData) {
    return (
      <div style={styles.container}>
        <div style={styles.loading}>Loading onboarding steps...</div>
      </div>
    );
  }

  // ---- error state ----
  if (stepsError) {
    return (
      <div style={styles.container}>
        <div style={styles.error}>
          <strong>Failed to load onboarding steps.</strong>
          <br />
          {stepsError}
          <br />
          <button
            style={{ ...styles.buttonSecondary, marginTop: 12 }}
            onClick={refetchSteps}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const isFirstStep = currentStepIndex === 0;
  const isLastStep = currentStepIndex === STEP_ORDER.length - 1;
  const fieldsLoading = schemaLoading && currentFields.length === 0;
  const fieldsError = schemaError;

  return (
    <div style={styles.container}>
      {/* Header */}
      <div style={styles.header}>
        <h2 style={styles.title}>Set Up Your AI Assistant</h2>
        <p style={styles.subtitle}>
          Complete these steps to configure how your AI assistant interacts with
          customers. You can always change these settings later.
        </p>
      </div>

      {/* Progress bar */}
      <div style={styles.progressBar}>
        {STEP_ORDER.map((_, idx) => (
          <div
            key={idx}
            style={styles.progressSegment(
              idx === currentStepIndex,
              completedSteps.has(idx) || idx < currentStepIndex,
            )}
          />
        ))}
      </div>

      {/* Step indicator */}
      <div style={styles.stepIndicator}>
        <span style={styles.stepCount}>
          Step {currentStepIndex + 1} of {STEP_ORDER.length}
        </span>
        {completedSteps.has(currentStepIndex) && (
          <span style={{ fontSize: 12, color: '#16a34a', fontWeight: 500 }}>
            <span style={styles.completedDot} />
            Completed
          </span>
        )}
      </div>

      {/* Step content */}
      <h3 style={styles.stepLabel}>{STEP_LABELS[currentStepKey]}</h3>
      <p style={styles.stepDescription}>{STEP_DESCRIPTIONS[currentStepKey]}</p>

      {/* Fields */}
      {fieldsLoading ? (
        <div style={styles.loading}>Loading fields...</div>
      ) : fieldsError ? (
        <div style={styles.error}>
          Failed to load fields for this step: {fieldsError}
        </div>
      ) : currentFields.length === 0 ? (
        <div style={styles.emptyStep}>
          No configurable fields for this step at the{' '}
          <strong>{tenantContext.tier}</strong> tier.
        </div>
      ) : (
        <div style={styles.fieldsContainer}>
          {currentFields.map((field) => (
            <FieldRenderer
              key={field.key}
              field={field}
              value={fieldValues[field.key]}
              onChange={handleFieldChange}
              disabled={saving || updateLoading}
              tenantTier={tenantContext.tier}
            />
          ))}
        </div>
      )}

      {/* Update error */}
      {updateError && (
        <div style={{ ...styles.error, marginBottom: 16 }}>
          Save failed: {updateError}
        </div>
      )}

      {/* Navigation */}
      <div style={styles.buttonRow}>
        <div style={{ display: 'flex', gap: 8 }}>
          {!isFirstStep && (
            <button
              style={styles.buttonSecondary}
              onClick={handlePrev}
              disabled={saving}
            >
              Previous
            </button>
          )}
          <button
            style={styles.buttonSkip}
            onClick={handleSkip}
            disabled={saving}
          >
            {isLastStep ? 'Skip & Finish' : 'Skip'}
          </button>
        </div>

        <button
          style={{
            ...styles.buttonPrimary,
            ...(saving || updateLoading
              ? { opacity: 0.6, cursor: 'not-allowed' }
              : {}),
          }}
          onClick={handleSave}
          disabled={saving || updateLoading || currentFields.length === 0}
        >
          {saving || updateLoading
            ? 'Saving...'
            : isLastStep
              ? 'Finish Setup'
              : 'Save & Continue'}
        </button>
      </div>
    </div>
  );
};

export default OnboardingWizard;
