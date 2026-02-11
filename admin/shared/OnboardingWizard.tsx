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
  IntegrationSummary,
  ValidationRule,
} from './types';
import {
  useOnboardingSteps,
  useUpdateConfig,
  useConfigSchema,
  useIntegrations,
  useActivateIntegration,
  useDeactivateIntegration,
  useConfig,
  useTestModeStatus,
  useActivateTestMode,
  useDeactivateTestMode,
} from './hooks';
import type { TestModeStatus } from './hooks';
import { HelpTooltip } from './HelpTooltip';

// ---------------------------------------------------------------------------
// Step metadata — display labels for each onboarding step
// ---------------------------------------------------------------------------

/** Wizard mode — C16 conditional step 0 determines this. */
type WizardMode = 'production' | 'test';

/** AI-behaviour fields that remain editable during active Test Mode (C14). */
const AI_BEHAVIOR_FIELD_KEYS: ReadonlySet<string> = new Set([
  'brand_voice',
  'response_length',
  'formality_level',
  'escalation_threshold',
  'escalation_keywords',
  'custom_instructions',
  'memory_enabled',
  'retrieval_top_k',
  'retrieval_vector_weight',
  'retrieval_bm25_weight',
  'retrieval_min_score',
  'intent_source_mapping',
  'cite_sources_in_response',
]);

const BASE_STEP_ORDER: OnboardingStep[] = [
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

const STEP_LABELS: Record<string, string> = {
  mode_selection: 'Mode selection',
  brand_and_tone: 'Brand & tone',
  ai_behavior: 'AI behavior',
  escalation: 'Escalation rules',
  integrations: 'Integrations',
  knowledge_base: 'Knowledge base',
  response_policies: 'Response policies',
  customer_memory: 'Customer memory',
  notifications: 'Notifications',
  widget_appearance: 'Widget appearance',
  review_and_launch: 'Review & launch',
};

const STEP_DESCRIPTIONS: Record<string, string> = {
  mode_selection:
    'Choose whether to modify your live Production config or create a Test Mode variant for controlled rollout.',
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
  review_and_launch:
    'Review your configuration and activate your AI assistant.',
};

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

export interface OnboardingWizardProps extends BaseComponentProps {
  /** Called when the merchant finishes (or explicitly skips) the entire wizard. */
  onComplete: () => void;
  /** Navigation callback — used to link to full Integrations page from wizard. */
  onNavigate?: (path: string) => void;
  /** Whether a production config already exists (enables C16 mode selector). */
  hasProductionConfig?: boolean;
  /** External test mode state from layout context (C1). */
  testModeStatus?: TestModeStatus | null;
  /** Callback to refetch test mode status after activation/deactivation. */
  onTestModeChange?: () => void;
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
    backgroundColor: completed ? '#ff3621' : active ? '#e8939a' : '#e0e0e0',
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
    accentColor: '#ff3621',
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
    backgroundColor: '#ff3621',
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

  requiredStar: {
    color: '#ff3621',
    marginLeft: 3,
    fontWeight: 700,
    fontSize: 14,
  } as React.CSSProperties,

  labelRow: {
    display: 'flex',
    alignItems: 'center',
    flexWrap: 'wrap' as const,
  } as React.CSSProperties,

  validationError: {
    fontSize: 12,
    color: '#D32F2F',
    marginTop: 4,
    lineHeight: 1.4,
  } as React.CSSProperties,

  inputError: {
    borderColor: '#D32F2F',
  } as React.CSSProperties,
} as const;

// ---------------------------------------------------------------------------
// Validation helper
// ---------------------------------------------------------------------------

/**
 * Validates a field value against its ValidationRule constraints.
 * Returns an error message string, or null if valid.
 */
function validateField(field: ConfigField, value: unknown): string | null {
  const rules = field.validation;
  if (!rules) return null;

  const strValue = value != null ? String(value) : '';

  // Required check
  if (rules.required) {
    if (value === null || value === undefined || strValue.trim() === '') {
      return `${field.label} is required.`;
    }
  }

  // Skip further validation if the field is empty and not required
  if (!strValue || strValue.trim() === '') return null;

  // String length constraints
  if (rules.minLength != null && strValue.length < rules.minLength) {
    return `Must be at least ${rules.minLength} characters.`;
  }
  if (rules.maxLength != null && strValue.length > rules.maxLength) {
    return `Must be at most ${rules.maxLength} characters.`;
  }

  // Numeric range constraints
  if ((field.type === 'number' || field.type === 'integer' || field.type === 'float') && value != null) {
    const numValue = Number(value);
    if (!isNaN(numValue)) {
      if (rules.minValue != null && numValue < rules.minValue) {
        return `Must be at least ${rules.minValue}.`;
      }
      if (rules.maxValue != null && numValue > rules.maxValue) {
        return `Must be at most ${rules.maxValue}.`;
      }
    }
  }

  // Pattern constraint
  if (rules.pattern && typeof value === 'string') {
    try {
      const regex = new RegExp(rules.pattern);
      if (!regex.test(value)) {
        return `Invalid format.`;
      }
    } catch {
      // Invalid regex in schema — skip pattern validation
    }
  }

  return null;
}

/**
 * Validates all fields in a step. Returns a map of field key -> error message.
 */
function validateAllFields(fields: ConfigField[], values: Record<string, unknown>): Record<string, string> {
  const errors: Record<string, string> = {};
  for (const field of fields) {
    const err = validateField(field, values[field.key]);
    if (err) {
      errors[field.key] = err;
    }
  }
  return errors;
}

// ---------------------------------------------------------------------------
// Field renderer
// ---------------------------------------------------------------------------

interface FieldRendererProps {
  field: ConfigField;
  value: unknown;
  onChange: (key: string, value: unknown) => void;
  onBlur: (key: string) => void;
  disabled: boolean;
  tenantTier: string;
  error?: string;
}

const FieldRenderer: React.FC<FieldRendererProps> = ({
  field,
  value,
  onChange,
  onBlur,
  disabled,
  tenantTier,
  error,
}) => {
  // Tier gate: if field requires a higher tier, show it as locked
  const tierOrder = ['trial', 'starter', 'professional', 'enterprise'];
  const tenantTierIndex = tierOrder.indexOf(tenantTier);
  const fieldTierIndex = field.tierGate ? tierOrder.indexOf(field.tierGate) : 0;
  const isLocked = fieldTierIndex > tenantTierIndex;

  const effectiveDisabled = disabled || isLocked;
  const isRequired = field.validation?.required === true;
  const hasError = !!error;

  const handleChange = useCallback(
    (newValue: unknown) => {
      if (!effectiveDisabled) {
        onChange(field.key, newValue);
      }
    },
    [field.key, onChange, effectiveDisabled],
  );

  const handleBlur = useCallback(() => {
    onBlur(field.key);
  }, [field.key, onBlur]);

  // Error border style for inputs
  const errorBorderStyle = hasError ? styles.inputError : {};

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
              ...errorBorderStyle,
            }}
            value={String(value ?? '')}
            onChange={(e) => handleChange(e.target.value)}
            onBlur={handleBlur}
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
              ...errorBorderStyle,
            }}
            value={String(value ?? '')}
            onChange={(e) => handleChange(e.target.value)}
            onBlur={handleBlur}
            disabled={effectiveDisabled}
            rows={4}
          />
        );

      case 'number':
      case 'integer':
      case 'float':
        return (
          <input
            type="number"
            style={{
              ...styles.input,
              ...(effectiveDisabled ? { opacity: 0.6, cursor: 'not-allowed' } : {}),
              ...errorBorderStyle,
            }}
            value={value !== undefined && value !== null ? String(value) : ''}
            onChange={(e) => handleChange(e.target.value === '' ? null : Number(e.target.value))}
            onBlur={handleBlur}
            disabled={effectiveDisabled}
            min={field.validation?.minValue ?? undefined}
            max={field.validation?.maxValue ?? undefined}
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
              ...errorBorderStyle,
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
            onBlur={handleBlur}
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
              ...errorBorderStyle,
            }}
            value={String(value ?? '')}
            onChange={(e) => handleChange(e.target.value)}
            onBlur={handleBlur}
            onKeyDown={(e) => {
              // Prevent Enter from triggering implicit form submission / page crash
              if (e.key === 'Enter') {
                e.preventDefault();
              }
            }}
            disabled={effectiveDisabled}
            maxLength={field.validation?.maxLength ?? undefined}
          />
        );
    }
  };

  return (
    <div style={styles.fieldGroup}>
      <div style={styles.labelRow}>
        <label style={styles.label}>
          {field.label}
          {isRequired && <span style={styles.requiredStar}>*</span>}
        </label>
        {isLocked && field.tierGate && (
          <span style={styles.tierBadge}>{field.tierGate}+</span>
        )}
        {field.tooltip && (
          <HelpTooltip text={field.tooltip} docLink={field.docLink} />
        )}
      </div>
      {field.description && <p style={styles.description}>{field.description}</p>}
      {renderInput()}
      {hasError && <p style={styles.validationError}>{error}</p>}
    </div>
  );
};

// ---------------------------------------------------------------------------
// Integration step — custom card-based UI (C11)
// ---------------------------------------------------------------------------

const INTEGRATION_ICONS: Record<string, string> = {
  shopify: '\uD83D\uDED2',       // shopping cart
  zendesk: '\uD83C\uDFAB',       // ticket
  mailchimp: '\uD83D\uDCE7',     // email
  google_analytics: '\uD83D\uDCCA', // chart
};

const integrationStyles = {
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
    gap: 16,
    marginBottom: 32,
  } as React.CSSProperties,

  card: (enabled: boolean): React.CSSProperties => ({
    border: `1px solid ${enabled ? '#ff3621' : '#272727'}`,
    borderRadius: 10,
    padding: 20,
    backgroundColor: '#1f1f1f',
    transition: 'border-color 0.2s ease',
  }),

  cardHeader: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 8,
  } as React.CSSProperties,

  cardNameRow: {
    display: 'flex',
    alignItems: 'center',
    gap: 10,
  } as React.CSSProperties,

  cardIcon: {
    fontSize: 22,
  } as React.CSSProperties,

  cardName: {
    fontSize: 15,
    fontWeight: 600,
    color: '#F5F5F5',
  } as React.CSSProperties,

  cardDescription: {
    fontSize: 13,
    color: '#787878',
    lineHeight: 1.5,
    margin: '0 0 14px 0',
  } as React.CSSProperties,

  statusBadge: (status: string | null): React.CSSProperties => ({
    display: 'inline-flex',
    alignItems: 'center',
    gap: 5,
    fontSize: 11,
    fontWeight: 600,
    textTransform: 'uppercase' as const,
    padding: '3px 10px',
    borderRadius: 12,
    backgroundColor:
      status === 'connected' ? 'rgba(13,124,62,0.15)'
      : status === 'error' ? 'rgba(211,47,47,0.15)'
      : 'rgba(120,120,120,0.15)',
    color:
      status === 'connected' ? '#0D7C3E'
      : status === 'error' ? '#D32F2F'
      : '#787878',
  }),

  statusDot: (status: string | null): React.CSSProperties => ({
    width: 6,
    height: 6,
    borderRadius: '50%',
    backgroundColor:
      status === 'connected' ? '#0D7C3E'
      : status === 'error' ? '#D32F2F'
      : '#787878',
  }),

  cardFooter: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginTop: 4,
  } as React.CSSProperties,

  toggleBtn: (enabled: boolean): React.CSSProperties => ({
    padding: '6px 16px',
    fontSize: 13,
    fontWeight: 500,
    borderRadius: 6,
    border: 'none',
    cursor: 'pointer',
    backgroundColor: enabled ? 'rgba(211,47,47,0.12)' : 'rgba(13,124,62,0.12)',
    color: enabled ? '#D32F2F' : '#0D7C3E',
    transition: 'background-color 0.15s ease',
  }),

  tierLock: {
    fontSize: 12,
    color: '#787878',
    fontStyle: 'italic' as const,
  } as React.CSSProperties,

  configureLink: {
    fontSize: 12,
    color: '#ff3621',
    textDecoration: 'none',
    cursor: 'pointer',
    border: 'none',
    background: 'none',
    padding: 0,
    fontWeight: 500,
  } as React.CSSProperties,
} as const;

interface IntegrationStepProps {
  apiFetch: (path: string, init?: RequestInit) => Promise<Response>;
  tenantTier: string;
  onNotify: (message: string, type: 'success' | 'error' | 'warning' | 'info') => void;
  onNavigate?: (path: string) => void;
}

const IntegrationStep: React.FC<IntegrationStepProps> = ({
  apiFetch,
  tenantTier,
  onNotify,
  onNavigate,
}) => {
  const { data: integrations, loading, error, refetch } = useIntegrations(apiFetch);
  const { activate, loading: activating } = useActivateIntegration(apiFetch);
  const { deactivate, loading: deactivating } = useDeactivateIntegration(apiFetch);

  const handleToggle = useCallback(async (type: string, currentlyEnabled: boolean) => {
    try {
      if (currentlyEnabled) {
        await deactivate(type);
        onNotify(`Integration deactivated.`, 'info');
      } else {
        await activate(type);
        onNotify(`Integration activated.`, 'success');
      }
      refetch();
    } catch {
      onNotify('Failed to update integration.', 'error');
    }
  }, [activate, deactivate, onNotify, refetch]);

  if (loading && !integrations) {
    return <div style={styles.loading}>Loading integrations...</div>;
  }

  if (error) {
    return (
      <div style={styles.error}>
        Failed to load integrations: {error}
        <br />
        <button style={{ ...styles.buttonSecondary, marginTop: 12 }} onClick={refetch}>
          Retry
        </button>
      </div>
    );
  }

  const items: IntegrationSummary[] = integrations ?? [];

  return (
    <div style={integrationStyles.grid}>
      {items.map((integ) => {
        const icon = INTEGRATION_ICONS[integ.type] ?? '\u{1F517}';

        return (
          <div key={integ.type} style={integrationStyles.card(integ.enabled)}>
            <div style={integrationStyles.cardHeader}>
              <div style={integrationStyles.cardNameRow}>
                <span style={integrationStyles.cardIcon}>{icon}</span>
                <span style={integrationStyles.cardName}>{integ.name}</span>
              </div>
              <span style={integrationStyles.statusBadge(integ.status)}>
                <span style={integrationStyles.statusDot(integ.status)} />
                {integ.status ?? 'Not configured'}
              </span>
            </div>

            <p style={integrationStyles.cardDescription}>{integ.description}</p>

            <div style={integrationStyles.cardFooter}>
              {!integ.tierMet ? (
                <span style={integrationStyles.tierLock}>
                  {integ.tierGate}+ tier required
                </span>
              ) : (
                <button
                  style={integrationStyles.toggleBtn(integ.enabled)}
                  onClick={() => handleToggle(integ.type, integ.enabled)}
                  disabled={activating || deactivating}
                >
                  {integ.enabled ? 'Disable' : 'Enable'}
                </button>
              )}

              {onNavigate && (
                <button
                  style={integrationStyles.configureLink}
                  onClick={() => onNavigate('/integrations')}
                >
                  Configure {String.fromCodePoint(0x2192)}
                </button>
              )}
            </div>
          </div>
        );
      })}

      {items.length === 0 && (
        <div style={styles.emptyStep}>
          No integrations available. Check back later!
        </div>
      )}
    </div>
  );
};

// ---------------------------------------------------------------------------
// Review & Launch step — C13 read-only config summary + activation
// ---------------------------------------------------------------------------

/** Styles for the Review & Launch step. */
const reviewStyles = {
  section: {
    marginBottom: 24,
    border: '1px solid #272727',
    borderRadius: 8,
    overflow: 'hidden',
  } as React.CSSProperties,

  sectionHeader: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '10px 16px',
    backgroundColor: '#1a1a1a',
    cursor: 'pointer',
    userSelect: 'none' as const,
  } as React.CSSProperties,

  sectionTitle: {
    fontSize: 14,
    fontWeight: 600,
    color: '#F5F5F5',
  } as React.CSSProperties,

  sectionBody: {
    padding: '12px 16px',
    display: 'flex',
    flexDirection: 'column' as const,
    gap: 8,
  } as React.CSSProperties,

  fieldRow: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    fontSize: 13,
    lineHeight: 1.5,
  } as React.CSSProperties,

  fieldLabel: {
    color: '#888',
    minWidth: 140,
    flexShrink: 0,
  } as React.CSSProperties,

  fieldValue: {
    color: '#E0E0E0',
    textAlign: 'right' as const,
    wordBreak: 'break-word' as const,
    maxWidth: '60%',
  } as React.CSSProperties,

  testPercentageRow: {
    display: 'flex',
    alignItems: 'center',
    gap: 12,
    marginBottom: 20,
    padding: '14px 16px',
    border: '1px solid #f59e0b',
    borderRadius: 8,
    backgroundColor: 'rgba(245, 158, 11, 0.04)',
  } as React.CSSProperties,

  percentageInput: {
    width: 70,
    padding: '6px 10px',
    fontSize: 14,
    border: '1px solid #d0d0d0',
    borderRadius: 6,
    textAlign: 'center' as const,
    backgroundColor: '#fff',
    color: '#1a1a1a',
  } as React.CSSProperties,

  activateBtn: (variant: 'production' | 'test'): React.CSSProperties => ({
    padding: '12px 28px',
    fontSize: 15,
    fontWeight: 600,
    border: 'none',
    borderRadius: 8,
    cursor: 'pointer',
    color: '#fff',
    backgroundColor: variant === 'test' ? '#f59e0b' : '#ff3621',
    width: '100%',
    marginTop: 8,
    transition: 'opacity 0.15s ease',
  }),

  destructiveBtn: {
    padding: '8px 20px',
    fontSize: 13,
    fontWeight: 500,
    border: '1px solid #d0d0d0',
    borderRadius: 6,
    cursor: 'pointer',
    backgroundColor: 'transparent',
    color: '#D32F2F',
    transition: 'opacity 0.15s ease',
  } as React.CSSProperties,

  activeTestBanner: {
    padding: '12px 16px',
    backgroundColor: 'rgba(245, 158, 11, 0.08)',
    border: '1px solid #f59e0b',
    borderRadius: 8,
    marginBottom: 20,
    fontSize: 14,
    color: '#f59e0b',
    display: 'flex',
    alignItems: 'center',
    gap: 10,
  } as React.CSSProperties,

  actionRow: {
    display: 'flex',
    gap: 12,
    marginTop: 16,
  } as React.CSSProperties,
} as const;

/**
 * Group config fields by wizard step for the review summary.
 * Returns an array of { step, label, fields: [{key, value}] }.
 */
function groupConfigForReview(
  config: Record<string, unknown>,
): Array<{ step: string; label: string; fields: Array<{ key: string; value: string }> }> {
  // Map config keys to their most likely step based on field prefixes / known groups
  const stepFieldPrefixes: Record<string, string[]> = {
    brand_and_tone: ['brand_', 'persona_', 'company_name'],
    ai_behavior: ['response_', 'formality_', 'model_', 'ai_'],
    escalation: ['escalation_'],
    knowledge_base: ['kb_', 'knowledge_'],
    response_policies: ['policy_', 'return_', 'shipping_', 'refund_', 'support_hours'],
    customer_memory: ['memory_', 'consent_'],
    notifications: ['notification_', 'alert_'],
    widget_appearance: ['widget_'],
  };

  const grouped: Record<string, Array<{ key: string; value: string }>> = {};
  const assignedKeys = new Set<string>();

  // First pass: assign by prefix
  for (const [step, prefixes] of Object.entries(stepFieldPrefixes)) {
    for (const [key, val] of Object.entries(config)) {
      if (assignedKeys.has(key)) continue;
      if (key.startsWith('test_mode_')) continue; // Exclude test mode internal fields
      for (const prefix of prefixes) {
        if (key.startsWith(prefix) || key === prefix) {
          if (!grouped[step]) grouped[step] = [];
          grouped[step].push({ key, value: formatConfigValue(val) });
          assignedKeys.add(key);
          break;
        }
      }
    }
  }

  // AI-behaviour fields that didn't match above
  for (const key of AI_BEHAVIOR_FIELD_KEYS) {
    if (assignedKeys.has(key) || !(key in config)) continue;
    if (!grouped['ai_behavior']) grouped['ai_behavior'] = [];
    grouped['ai_behavior'].push({ key, value: formatConfigValue(config[key]) });
    assignedKeys.add(key);
  }

  // Remaining unassigned keys go into a "General" section
  for (const [key, val] of Object.entries(config)) {
    if (assignedKeys.has(key)) continue;
    if (key.startsWith('test_mode_')) continue;
    if (!grouped['general']) grouped['general'] = [];
    grouped['general'].push({ key, value: formatConfigValue(val) });
  }

  // Build output in step order
  const result: Array<{ step: string; label: string; fields: Array<{ key: string; value: string }> }> = [];
  const displayOrder = [...BASE_STEP_ORDER, 'general'];
  for (const step of displayOrder) {
    if (grouped[step] && grouped[step].length > 0) {
      const label = step === 'general' ? 'General' : (STEP_LABELS[step] ?? step);
      result.push({ step, label, fields: grouped[step] });
    }
  }

  return result;
}

/** Format a config value for display in the review summary. */
function formatConfigValue(val: unknown): string {
  if (val === null || val === undefined) return '\u2014'; // em-dash
  if (typeof val === 'boolean') return val ? 'Enabled' : 'Disabled';
  if (typeof val === 'number') return String(val);
  if (typeof val === 'string') return val || '\u2014';
  if (Array.isArray(val)) return val.length === 0 ? '(none)' : val.join(', ');
  if (typeof val === 'object') {
    try { return JSON.stringify(val); } catch { return '(object)'; }
  }
  return String(val);
}

/** Format a config key for human display: snake_case → Title Case. */
function formatFieldLabel(key: string): string {
  return key
    .split('_')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ');
}

interface ReviewAndLaunchStepProps {
  apiFetch: (path: string, init?: RequestInit) => Promise<Response>;
  config: Record<string, unknown>;
  wizardMode: WizardMode;
  testPercentage: number;
  onTestPercentageChange: (pct: number) => void;
  isTestModeActive: boolean;
  activatingTest: boolean;
  deactivatingTest: boolean;
  onActivateTest: () => Promise<void>;
  onRollout: () => Promise<void>;
  onAbandon: () => Promise<void>;
  onFinishProduction: () => void;
}

const ReviewAndLaunchStep: React.FC<ReviewAndLaunchStepProps> = ({
  config,
  wizardMode,
  testPercentage,
  onTestPercentageChange,
  isTestModeActive,
  activatingTest,
  deactivatingTest,
  onActivateTest,
  onRollout,
  onAbandon,
  onFinishProduction,
}) => {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(
    () => new Set(BASE_STEP_ORDER),
  );

  const toggleSection = useCallback((step: string) => {
    setExpandedSections((prev) => {
      const next = new Set(prev);
      if (next.has(step)) next.delete(step);
      else next.add(step);
      return next;
    });
  }, []);

  const grouped = useMemo(() => groupConfigForReview(config), [config]);

  return (
    <div>
      {/* Active Test Mode banner */}
      {isTestModeActive && (
        <div style={reviewStyles.activeTestBanner}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
            <line x1="12" y1="9" x2="12" y2="13" />
            <line x1="12" y1="17" x2="12.01" y2="17" />
          </svg>
          <div>
            <strong>Test Mode is active.</strong> You can roll out (merge to production) or abandon (discard) the test configuration.
          </div>
        </div>
      )}

      {/* Config summary sections */}
      <div style={{ marginBottom: 24 }}>
        <div style={{ fontSize: 14, fontWeight: 500, color: '#888', marginBottom: 12 }}>
          Configuration Summary
        </div>

        {grouped.length === 0 && (
          <div style={styles.emptyStep}>
            No configuration values have been set yet.
          </div>
        )}

        {grouped.map(({ step, label, fields }) => (
          <div key={step} style={reviewStyles.section}>
            <div
              style={reviewStyles.sectionHeader}
              onClick={() => toggleSection(step)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  toggleSection(step);
                }
              }}
            >
              <span style={reviewStyles.sectionTitle}>
                {label}
                <span style={{ color: '#666', fontWeight: 400, marginLeft: 8, fontSize: 12 }}>
                  ({fields.length} {fields.length === 1 ? 'field' : 'fields'})
                </span>
              </span>
              <span style={{ color: '#888', fontSize: 12 }}>
                {expandedSections.has(step) ? '\u25B2' : '\u25BC'}
              </span>
            </div>

            {expandedSections.has(step) && (
              <div style={reviewStyles.sectionBody}>
                {fields.map(({ key, value }) => (
                  <div key={key} style={reviewStyles.fieldRow}>
                    <span style={reviewStyles.fieldLabel}>{formatFieldLabel(key)}</span>
                    <span style={reviewStyles.fieldValue}>{value}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Test Mode controls */}
      {wizardMode === 'test' && !isTestModeActive && (
        <>
          <div style={reviewStyles.testPercentageRow}>
            <label style={{ fontSize: 14, fontWeight: 500, color: '#F5F5F5', flexShrink: 0 }}>
              Test Population:
            </label>
            <input
              type="number"
              style={reviewStyles.percentageInput}
              value={testPercentage}
              min={1}
              max={50}
              onChange={(e) => {
                const val = Math.min(50, Math.max(1, parseInt(e.target.value, 10) || 1));
                onTestPercentageChange(val);
              }}
            />
            <span style={{ fontSize: 14, color: '#888' }}>% of sessions</span>
            <span style={{ fontSize: 12, color: '#666', marginLeft: 'auto' }}>
              (1\u201350%)
            </span>
          </div>

          <button
            style={{
              ...reviewStyles.activateBtn('test'),
              ...(activatingTest ? { opacity: 0.6, cursor: 'not-allowed' } : {}),
            }}
            onClick={onActivateTest}
            disabled={activatingTest}
          >
            {activatingTest ? 'Activating...' : `Activate AI Agent Test (${testPercentage}%)`}
          </button>
        </>
      )}

      {/* Roll-out / Abandon controls when test is already active */}
      {isTestModeActive && (
        <div style={reviewStyles.actionRow}>
          <button
            style={{
              ...reviewStyles.activateBtn('production'),
              flex: 1,
              ...(deactivatingTest ? { opacity: 0.6, cursor: 'not-allowed' } : {}),
            }}
            onClick={onRollout}
            disabled={deactivatingTest}
          >
            {deactivatingTest ? 'Processing...' : 'Roll Out to Production'}
          </button>
          <button
            style={{
              ...reviewStyles.destructiveBtn,
              ...(deactivatingTest ? { opacity: 0.6, cursor: 'not-allowed' } : {}),
            }}
            onClick={onAbandon}
            disabled={deactivatingTest}
          >
            Abandon Test
          </button>
        </div>
      )}

      {/* Production activation */}
      {wizardMode === 'production' && !isTestModeActive && (
        <button
          style={reviewStyles.activateBtn('production')}
          onClick={onFinishProduction}
        >
          Activate AI Agent
        </button>
      )}
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
  onNavigate,
  hasProductionConfig,
  testModeStatus: externalTestMode,
  onTestModeChange,
}) => {
  // ---- BUG-5 fix: persist wizard state across reload ----
  const WIZARD_STORAGE_KEY = `agentred_wizard_${tenantContext?.tenantId || 'default'}`;

  function loadWizardState<T>(key: string, fallback: T): T {
    try {
      const stored = localStorage.getItem(WIZARD_STORAGE_KEY);
      if (!stored) return fallback;
      const parsed = JSON.parse(stored);
      return parsed[key] ?? fallback;
    } catch {
      return fallback;
    }
  }

  // ---- state (with localStorage restoration) ----
  const [currentStepIndex, setCurrentStepIndex] = useState(() => loadWizardState('stepIndex', 0));
  const [fieldValues, setFieldValues] = useState<Record<string, unknown>>(() => loadWizardState('fieldValues', {}));
  const [saving, setSaving] = useState(false);
  const [completedSteps, setCompletedSteps] = useState<Set<number>>(
    () => new Set(loadWizardState<number[]>('completedSteps', [])),
  );
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [touchedFields, setTouchedFields] = useState<Set<string>>(new Set());

  // C16: wizard mode — "production" or "test"
  const [wizardMode, setWizardMode] = useState<WizardMode>(() => loadWizardState('wizardMode', 'production'));

  // C13: test population percentage for Review & Launch
  const [testPercentage, setTestPercentage] = useState(() => loadWizardState('testPercentage', 10));

  // Persist wizard state to localStorage on changes
  useEffect(() => {
    try {
      const state = {
        stepIndex: currentStepIndex,
        fieldValues,
        completedSteps: Array.from(completedSteps),
        wizardMode,
        testPercentage,
      };
      localStorage.setItem(WIZARD_STORAGE_KEY, JSON.stringify(state));
    } catch {
      // localStorage may be unavailable — gracefully degrade
    }
  }, [currentStepIndex, fieldValues, completedSteps, wizardMode, testPercentage, WIZARD_STORAGE_KEY]);

  // ---- hooks ----
  const {
    data: onboardingData,
    loading: stepsLoading,
    error: stepsError,
    refetch: refetchSteps,
  } = useOnboardingSteps(apiFetch);

  const { updateConfig, loading: updateLoading, error: updateError } = useUpdateConfig(apiFetch);

  // C13: load full config for review step
  const { data: fullConfig } = useConfig(apiFetch);

  // C2: test mode hooks for activation from Review step
  const { data: testModeData, refetch: refetchTestMode } = useTestModeStatus(apiFetch);
  const { activate: activateTestMode, loading: activatingTest } = useActivateTestMode(apiFetch);
  const { deactivate: deactivateTestMode, loading: deactivatingTest } = useDeactivateTestMode(apiFetch);

  // Effective test mode state — prefer external context, fall back to local fetch
  const testMode = externalTestMode ?? testModeData;
  const isTestModeActive = testMode?.enabled === true;

  // C16: Compute the dynamic step order
  // mode_selection is step 0 ONLY when: production config exists AND test mode is NOT currently active
  const showModeSelector = hasProductionConfig === true && !isTestModeActive;

  const STEP_ORDER: string[] = useMemo(() => {
    const steps: string[] = [];
    if (showModeSelector) steps.push('mode_selection');
    steps.push(...BASE_STEP_ORDER);
    steps.push('review_and_launch');
    return steps;
  }, [showModeSelector]);

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
      return schemaData.fields.map((raw: Record<string, unknown>) => {
        // Parse validation rule from backend format
        const rawValidation = raw.validation as Record<string, unknown> | undefined;
        const validation: ValidationRule | undefined = rawValidation ? {
          required: rawValidation.required === true,
          minLength: rawValidation.min_length != null ? Number(rawValidation.min_length) : undefined,
          maxLength: rawValidation.max_length != null ? Number(rawValidation.max_length) : undefined,
          minValue: rawValidation.min_value != null ? Number(rawValidation.min_value) : undefined,
          maxValue: rawValidation.max_value != null ? Number(rawValidation.max_value) : undefined,
          pattern: rawValidation.pattern != null ? String(rawValidation.pattern) : undefined,
          allowedValues: Array.isArray(rawValidation.allowed_values) ? rawValidation.allowed_values as string[] : undefined,
          maxItems: rawValidation.max_items != null ? Number(rawValidation.max_items) : undefined,
        } : undefined;

        return {
          key: String(raw.key ?? raw.field_name ?? ''),
          label: String(raw.label ?? raw.display_name ?? raw.field_name ?? ''),
          description: String(raw.description ?? ''),
          tooltip: raw.tooltip != null ? String(raw.tooltip) : undefined,
          docLink: raw.doc_link ?? raw.docLink ?? raw.help_url ?? undefined,
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
          validation,
        };
      }) as ConfigField[];
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
    // Reset validation state when switching steps
    setFieldErrors({});
    setTouchedFields(new Set());
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
    // Clear error for this field on change (re-validates on blur)
    setFieldErrors((prev) => {
      if (prev[key]) {
        const next = { ...prev };
        delete next[key];
        return next;
      }
      return prev;
    });
  }, []);

  const handleFieldBlur = useCallback((key: string) => {
    setTouchedFields((prev) => new Set(prev).add(key));
    // Validate the individual field on blur
    const field = currentFields.find((f) => f.key === key);
    if (field) {
      const err = validateField(field, fieldValues[key]);
      setFieldErrors((prev) => {
        if (err) {
          return { ...prev, [key]: err };
        }
        const next = { ...prev };
        delete next[key];
        return next;
      });
    }
  }, [currentFields, fieldValues]);

  const handleSave = useCallback(async () => {
    if (saving || updateLoading) return;

    // C16: Mode selection — no save, just advance
    if (currentStepKey === 'mode_selection') {
      setCompletedSteps((prev) => new Set(prev).add(currentStepIndex));
      setCurrentStepIndex((i) => i + 1);
      return;
    }

    // C13: Review and Launch — activation handled by ReviewAndLaunchStep buttons,
    // so the primary nav button just advances / finishes.
    if (currentStepKey === 'review_and_launch') {
      // The step's own buttons handle activation. The primary nav button
      // is labelled "Finish Setup" and completes the wizard.
      onNotify('Onboarding complete! Your AI assistant is ready.', 'success');
      onComplete();
      return;
    }

    // C11: Integrations step — no field-level save (managed by IntegrationStep)
    if (currentStepKey === 'integrations') {
      setCompletedSteps((prev) => new Set(prev).add(currentStepIndex));
      if (currentStepIndex < STEP_ORDER.length - 1) {
        setCurrentStepIndex((i) => i + 1);
      }
      return;
    }

    // Standard field-based steps — validate and save
    const errors = validateAllFields(currentFields, fieldValues);
    if (Object.keys(errors).length > 0) {
      setFieldErrors(errors);
      // Mark all fields as touched so errors display
      setTouchedFields(new Set(currentFields.map((f) => f.key)));
      onNotify('Please fix the highlighted errors before continuing.', 'warning');
      return;
    }

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
    currentFields,
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

      {/* C16: Mode Selection step */}
      {currentStepKey === 'mode_selection' ? (
        <div style={styles.fieldsContainer}>
          <div style={{ marginBottom: 16, fontSize: 14, color: '#888' }}>
            A Production configuration already exists. Choose how you want to proceed:
          </div>
          <label style={{ ...styles.checkboxRow, padding: '14px 16px', border: wizardMode === 'production' ? '2px solid #ff3621' : '1px solid #d0d0d0', borderRadius: 8, cursor: 'pointer', background: wizardMode === 'production' ? 'rgba(255, 54, 33, 0.04)' : 'transparent' }}>
            <input type="radio" name="wizard-mode" value="production" checked={wizardMode === 'production'} onChange={() => setWizardMode('production')} style={{ accentColor: '#ff3621', width: 18, height: 18 }} />
            <div>
              <div style={{ fontWeight: 600, fontSize: 15, marginBottom: 2 }}>Production</div>
              <div style={{ fontSize: 13, color: '#888' }}>Modify your live AI configuration directly.</div>
            </div>
          </label>
          <label style={{ ...styles.checkboxRow, padding: '14px 16px', border: wizardMode === 'test' ? '2px solid #f59e0b' : '1px solid #d0d0d0', borderRadius: 8, cursor: 'pointer', marginTop: 8, background: wizardMode === 'test' ? 'rgba(245, 158, 11, 0.04)' : 'transparent' }}>
            <input type="radio" name="wizard-mode" value="test" checked={wizardMode === 'test'} onChange={() => setWizardMode('test')} style={{ accentColor: '#f59e0b', width: 18, height: 18 }} />
            <div>
              <div style={{ fontWeight: 600, fontSize: 15, marginBottom: 2 }}>Test Mode</div>
              <div style={{ fontSize: 13, color: '#888' }}>Create a test variant — route a percentage of sessions to it for controlled testing.</div>
            </div>
          </label>
        </div>

      /* C13: Review and Launch step */
      ) : currentStepKey === 'review_and_launch' ? (
        <ReviewAndLaunchStep
          apiFetch={apiFetch}
          config={fullConfig?.config ?? {}}
          wizardMode={wizardMode}
          testPercentage={testPercentage}
          onTestPercentageChange={setTestPercentage}
          isTestModeActive={isTestModeActive}
          activatingTest={activatingTest}
          deactivatingTest={deactivatingTest}
          onActivateTest={async () => {
            // Collect AI-behaviour field deltas from current config
            const overrides: Record<string, unknown> = {};
            const prefs = fullConfig?.config ?? {};
            for (const key of AI_BEHAVIOR_FIELD_KEYS) {
              if (key in prefs) overrides[key] = (prefs as Record<string, unknown>)[key];
            }
            const ok = await activateTestMode(overrides, testPercentage);
            if (ok) {
              onNotify(`Test Mode activated — ${testPercentage}% of sessions will use the test config.`, 'success');
              refetchTestMode();
              onTestModeChange?.();
            } else {
              onNotify('Failed to activate Test Mode.', 'error');
            }
          }}
          onRollout={async () => {
            const ok = await deactivateTestMode('rollout');
            if (ok) {
              onNotify('Test Mode rolled out — test overrides merged into production.', 'success');
              refetchTestMode();
              onTestModeChange?.();
              onComplete();
            } else {
              onNotify('Failed to roll out test mode.', 'error');
            }
          }}
          onAbandon={async () => {
            const ok = await deactivateTestMode('abandon');
            if (ok) {
              onNotify('Test Mode abandoned — test overrides discarded.', 'success');
              refetchTestMode();
              onTestModeChange?.();
            } else {
              onNotify('Failed to abandon test mode.', 'error');
            }
          }}
          onFinishProduction={() => {
            onNotify('Configuration saved! Your AI assistant is live.', 'success');
            onComplete();
          }}
        />

      /* C11: custom integration step */
      ) : currentStepKey === 'integrations' ? (
        <IntegrationStep
          apiFetch={apiFetch}
          tenantTier={tenantContext.tier}
          onNotify={onNotify}
          onNavigate={onNavigate}
        />
      ) : fieldsLoading ? (
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
          {currentFields.map((field) => {
            // C14: Lock non-AI-behaviour fields when Test Mode is active
            const lockedByTestMode = isTestModeActive && !AI_BEHAVIOR_FIELD_KEYS.has(field.key);

            return (
              <div key={field.key} style={{ position: 'relative' }}>
                {lockedByTestMode && (
                  <div
                    style={{
                      position: 'absolute',
                      inset: 0,
                      background: 'rgba(128, 128, 128, 0.12)',
                      borderRadius: 6,
                      zIndex: 2,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      cursor: 'not-allowed',
                    }}
                    title="This field is locked while Test Mode is active. Only AI behaviour fields can be modified."
                  />
                )}
                <FieldRenderer
                  field={field}
                  value={fieldValues[field.key]}
                  onChange={handleFieldChange}
                  onBlur={handleFieldBlur}
                  disabled={saving || updateLoading || lockedByTestMode}
                  tenantTier={tenantContext.tier}
                  error={touchedFields.has(field.key) ? fieldErrors[field.key] : undefined}
                />
              </div>
            );
          })}
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
          {/* Hide skip on review_and_launch — activation is explicit */}
          {currentStepKey !== 'review_and_launch' && (
            <button
              style={styles.buttonSkip}
              onClick={handleSkip}
              disabled={saving}
            >
              {isLastStep ? 'Skip & Finish' : 'Skip'}
            </button>
          )}
        </div>

        <button
          style={{
            ...styles.buttonPrimary,
            ...(saving || updateLoading
              ? { opacity: 0.6, cursor: 'not-allowed' }
              : {}),
            // Test-mode review uses amber
            ...(currentStepKey === 'review_and_launch' && wizardMode === 'test' && !isTestModeActive
              ? { backgroundColor: '#f59e0b' }
              : {}),
          }}
          onClick={handleSave}
          disabled={
            saving ||
            updateLoading ||
            // Standard field steps require fields; special steps don't
            (currentStepKey !== 'mode_selection' &&
             currentStepKey !== 'review_and_launch' &&
             currentStepKey !== 'integrations' &&
             currentFields.length === 0)
          }
        >
          {saving || updateLoading
            ? 'Saving...'
            : currentStepKey === 'mode_selection'
              ? 'Continue'
              : currentStepKey === 'review_and_launch'
                ? 'Finish Setup'
                : currentStepKey === 'integrations'
                  ? 'Continue'
                  : isLastStep
                    ? 'Finish Setup'
                    : 'Save & Continue'}
        </button>
      </div>
    </div>
  );
};

export default OnboardingWizard;
