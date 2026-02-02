/**
 * WidgetConfigurator — Visual editor for the 24 widget customization fields.
 *
 * Provides a tabbed form (Visual / Behavior / Content) alongside a live preview
 * panel that renders a mini-widget mockup reflecting the merchant's current
 * settings in real time.
 *
 * The 24 fields map to the widget_* columns in PreferencesDocument and are
 * defined in tenant_config_schema.py (OnboardingStep.WIDGET_APPEARANCE).
 *
 * Props:
 *   - BaseComponentProps (tenantContext, apiFetch, onNotify, onNavigate)
 *
 * Data hooks:
 *   - useConfig: reads the current tenant configuration
 *   - useUpdateConfig: saves changed widget fields via PUT /api/config
 *
 * Architecture references:
 *   - Decision UI-2: Widget delivery (Theme App Extension + JS snippet)
 *   - Decision UI-3: Shadow DOM + iframe isolation
 *   - tenant_config_schema.py step 9: Widget Appearance (24 fields)
 *   - cosmos_schema.py: PreferencesDocument widget_* fields
 *
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useState, useCallback, useMemo, useEffect } from 'react';
import type { BaseComponentProps } from './types';
import { useConfig, useUpdateConfig } from './hooks';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type Tab = 'visual' | 'behavior' | 'content';

interface WidgetConfig {
  // Visual (12)
  widget_primary_color: string;
  widget_background_color: string;
  widget_position: 'bottom-right' | 'bottom-left';
  widget_offset_x: number;
  widget_offset_y: number;
  widget_agent_avatar_url: string;
  widget_agent_display_name: string;
  widget_agent_title: string;
  widget_logo_url: string;
  widget_show_branding: boolean;
  widget_mobile_enabled: boolean;
  widget_dark_mode: boolean;
  // Behavior (9)
  widget_offline_message: string;
  widget_auto_open: boolean;
  widget_auto_open_delay: number;
  widget_operating_hours: Record<string, unknown> | null;
  widget_offline_behavior: 'ai_only' | 'show_form' | 'hide_widget';
  widget_prechat_form: Record<string, unknown> | null;
  widget_chat_rating_enabled: boolean;
  widget_sound_enabled: boolean;
  widget_file_upload_enabled: boolean;
  // Content / Targeting (3)
  widget_header_text: string;
  widget_input_placeholder: string;
  widget_page_rules: string[];
}

const DEFAULT_CONFIG: WidgetConfig = {
  widget_primary_color: '#C41E2A',
  widget_background_color: '#FFFFFF',
  widget_position: 'bottom-right',
  widget_offset_x: 20,
  widget_offset_y: 20,
  widget_agent_avatar_url: '',
  widget_agent_display_name: '',
  widget_agent_title: '',
  widget_logo_url: '',
  widget_show_branding: true,
  widget_mobile_enabled: true,
  widget_dark_mode: false,
  widget_offline_message: '',
  widget_auto_open: false,
  widget_auto_open_delay: 5,
  widget_operating_hours: null,
  widget_offline_behavior: 'ai_only',
  widget_prechat_form: null,
  widget_chat_rating_enabled: false,
  widget_sound_enabled: true,
  widget_file_upload_enabled: true,
  widget_header_text: '',
  widget_input_placeholder: '',
  widget_page_rules: [],
};

// ---------------------------------------------------------------------------
// Styles
// ---------------------------------------------------------------------------

const s = {
  container: {
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    display: 'flex',
    gap: 24,
    maxWidth: 1200,
    margin: '0 auto',
  } as React.CSSProperties,

  formPanel: {
    flex: 1,
    minWidth: 0,
  } as React.CSSProperties,

  previewPanel: {
    width: 340,
    flexShrink: 0,
    position: 'sticky' as const,
    top: 16,
    alignSelf: 'flex-start' as const,
  } as React.CSSProperties,

  card: {
    background: '#FFFFFF',
    border: '1px solid #E5E7EB',
    borderRadius: 8,
    padding: 24,
    marginBottom: 24,
  } as React.CSSProperties,

  tabs: {
    display: 'flex',
    borderBottom: '2px solid #E5E7EB',
    marginBottom: 24,
    gap: 0,
  } as React.CSSProperties,

  tab: (active: boolean): React.CSSProperties => ({
    padding: '10px 20px',
    fontSize: 14,
    fontWeight: active ? 600 : 500,
    color: active ? '#C41E2A' : '#6B7280',
    background: 'transparent',
    border: 'none',
    borderBottom: active ? '2px solid #C41E2A' : '2px solid transparent',
    marginBottom: -2,
    cursor: 'pointer',
    transition: 'color 0.15s ease',
  }),

  sectionTitle: {
    fontSize: 16,
    fontWeight: 600,
    color: '#111827',
    margin: '24px 0 16px 0',
    padding: 0,
  } as React.CSSProperties,

  fieldGroup: {
    marginBottom: 20,
  } as React.CSSProperties,

  label: {
    display: 'block',
    fontSize: 13,
    fontWeight: 600,
    color: '#374151',
    marginBottom: 4,
  } as React.CSSProperties,

  description: {
    display: 'block',
    fontSize: 12,
    color: '#6B7280',
    marginBottom: 8,
    lineHeight: 1.4,
  } as React.CSSProperties,

  input: {
    width: '100%',
    padding: '8px 12px',
    fontSize: 14,
    border: '1px solid #D1D5DB',
    borderRadius: 6,
    color: '#111827',
    background: '#FFFFFF',
    outline: 'none',
    boxSizing: 'border-box' as const,
  } as React.CSSProperties,

  textarea: {
    width: '100%',
    padding: '8px 12px',
    fontSize: 14,
    border: '1px solid #D1D5DB',
    borderRadius: 6,
    color: '#111827',
    background: '#FFFFFF',
    outline: 'none',
    boxSizing: 'border-box' as const,
    resize: 'vertical' as const,
    minHeight: 80,
    fontFamily: 'inherit',
  } as React.CSSProperties,

  select: {
    width: '100%',
    padding: '8px 12px',
    fontSize: 14,
    border: '1px solid #D1D5DB',
    borderRadius: 6,
    color: '#111827',
    background: '#FFFFFF',
    outline: 'none',
    boxSizing: 'border-box' as const,
    cursor: 'pointer',
  } as React.CSSProperties,

  numberInput: {
    width: 120,
    padding: '8px 12px',
    fontSize: 14,
    border: '1px solid #D1D5DB',
    borderRadius: 6,
    color: '#111827',
    background: '#FFFFFF',
    outline: 'none',
    boxSizing: 'border-box' as const,
  } as React.CSSProperties,

  colorRow: {
    display: 'flex',
    alignItems: 'center',
    gap: 12,
  } as React.CSSProperties,

  colorSwatch: (color: string): React.CSSProperties => ({
    width: 36,
    height: 36,
    borderRadius: 6,
    border: '2px solid #D1D5DB',
    background: color,
    cursor: 'pointer',
    flexShrink: 0,
  }),

  colorInput: {
    width: 0,
    height: 0,
    padding: 0,
    border: 'none',
    position: 'absolute' as const,
    opacity: 0,
  } as React.CSSProperties,

  toggle: {
    display: 'flex',
    alignItems: 'center',
    gap: 10,
    cursor: 'pointer',
  } as React.CSSProperties,

  toggleTrack: (on: boolean): React.CSSProperties => ({
    width: 40,
    height: 22,
    borderRadius: 11,
    background: on ? '#C41E2A' : '#D1D5DB',
    position: 'relative' as const,
    transition: 'background 0.2s ease',
    flexShrink: 0,
  }),

  toggleKnob: (on: boolean): React.CSSProperties => ({
    width: 18,
    height: 18,
    borderRadius: '50%',
    background: '#FFFFFF',
    position: 'absolute' as const,
    top: 2,
    left: on ? 20 : 2,
    transition: 'left 0.2s ease',
    boxShadow: '0 1px 2px rgba(0,0,0,0.2)',
  }),

  jsonEditor: {
    width: '100%',
    padding: '8px 12px',
    fontSize: 13,
    fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
    border: '1px solid #D1D5DB',
    borderRadius: 6,
    color: '#111827',
    background: '#F9FAFB',
    outline: 'none',
    boxSizing: 'border-box' as const,
    resize: 'vertical' as const,
    minHeight: 100,
    lineHeight: 1.5,
  } as React.CSSProperties,

  pageRuleRow: {
    display: 'flex',
    alignItems: 'center',
    gap: 8,
    marginBottom: 8,
  } as React.CSSProperties,

  removeButton: {
    width: 28,
    height: 28,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    border: '1px solid #D1D5DB',
    borderRadius: 4,
    background: '#FFFFFF',
    color: '#DC2626',
    fontSize: 16,
    cursor: 'pointer',
    flexShrink: 0,
    lineHeight: 1,
  } as React.CSSProperties,

  addButton: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: 4,
    padding: '6px 12px',
    fontSize: 13,
    fontWeight: 500,
    color: '#374151',
    background: '#F3F4F6',
    border: '1px solid #D1D5DB',
    borderRadius: 4,
    cursor: 'pointer',
  } as React.CSSProperties,

  saveBar: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '12px 24px',
    background: '#111827',
    borderRadius: 8,
    marginBottom: 16,
    color: '#FFFFFF',
    fontSize: 14,
  } as React.CSSProperties,

  saveButton: {
    padding: '8px 24px',
    background: '#C41E2A',
    color: '#FFFFFF',
    border: 'none',
    borderRadius: 6,
    fontSize: 14,
    fontWeight: 600,
    cursor: 'pointer',
  } as React.CSSProperties,

  discardButton: {
    padding: '8px 16px',
    background: 'transparent',
    color: '#9CA3AF',
    border: '1px solid #4B5563',
    borderRadius: 6,
    fontSize: 14,
    fontWeight: 500,
    cursor: 'pointer',
    marginRight: 8,
  } as React.CSSProperties,

  loadingContainer: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 48,
    color: '#6B7280',
    fontSize: 14,
  } as React.CSSProperties,

  errorContainer: {
    padding: 24,
    background: '#FEF2F2',
    border: '1px solid #FECACA',
    borderRadius: 8,
    color: '#991B1B',
    fontSize: 14,
    textAlign: 'center' as const,
  } as React.CSSProperties,

  retryButton: {
    marginTop: 12,
    padding: '6px 16px',
    background: '#DC2626',
    color: '#FFFFFF',
    border: 'none',
    borderRadius: 4,
    fontSize: 13,
    fontWeight: 600,
    cursor: 'pointer',
  } as React.CSSProperties,

  // Preview styles
  previewTitle: {
    fontSize: 14,
    fontWeight: 600,
    color: '#111827',
    margin: '0 0 12px 0',
  } as React.CSSProperties,

  previewFrame: (darkMode: boolean): React.CSSProperties => ({
    background: darkMode ? '#1F2937' : '#F3F4F6',
    borderRadius: 12,
    padding: 24,
    minHeight: 480,
    position: 'relative' as const,
    overflow: 'hidden',
    border: '1px solid #E5E7EB',
  }),
};

// ---------------------------------------------------------------------------
// Sub-components: Form fields
// ---------------------------------------------------------------------------

interface FieldProps {
  label: string;
  description?: string;
  children: React.ReactNode;
}

const Field: React.FC<FieldProps> = ({ label, description, children }) => (
  <div style={s.fieldGroup}>
    <label style={s.label}>{label}</label>
    {description && <span style={s.description}>{description}</span>}
    {children}
  </div>
);

interface ColorPickerFieldProps {
  label: string;
  description?: string;
  value: string;
  onChange: (val: string) => void;
}

const ColorPickerField: React.FC<ColorPickerFieldProps> = ({ label, description, value, onChange }) => {
  const inputRef = React.useRef<HTMLInputElement>(null);

  return (
    <Field label={label} description={description}>
      <div style={s.colorRow}>
        <div
          style={s.colorSwatch(value || '#FFFFFF')}
          onClick={() => inputRef.current?.click()}
          role="button"
          tabIndex={0}
          aria-label={`Pick ${label}`}
        />
        <input
          ref={inputRef}
          type="color"
          value={value || '#FFFFFF'}
          onChange={(e) => onChange(e.target.value)}
          style={s.colorInput}
        />
        <input
          type="text"
          value={value}
          onChange={(e) => {
            const val = e.target.value;
            if (/^#[0-9a-fA-F]{0,6}$/.test(val) || val === '') {
              onChange(val);
            }
          }}
          placeholder="#RRGGBB"
          maxLength={7}
          style={{ ...s.input, width: 120 }}
        />
      </div>
    </Field>
  );
};

interface ToggleFieldProps {
  label: string;
  description?: string;
  value: boolean;
  onChange: (val: boolean) => void;
}

const ToggleField: React.FC<ToggleFieldProps> = ({ label, description, value, onChange }) => (
  <Field label={label} description={description}>
    <div
      style={s.toggle}
      onClick={() => onChange(!value)}
      role="switch"
      aria-checked={value}
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onChange(!value);
        }
      }}
    >
      <div style={s.toggleTrack(value)}>
        <div style={s.toggleKnob(value)} />
      </div>
      <span style={{ fontSize: 13, color: value ? '#111827' : '#6B7280' }}>
        {value ? 'Enabled' : 'Disabled'}
      </span>
    </div>
  </Field>
);

// ---------------------------------------------------------------------------
// Sub-component: Live Preview
// ---------------------------------------------------------------------------

interface PreviewProps {
  config: WidgetConfig;
}

const WidgetPreview: React.FC<PreviewProps> = ({ config }) => {
  const isDark = config.widget_dark_mode;
  const primaryColor = config.widget_primary_color || '#C41E2A';
  const bgColor = isDark ? '#1A1A2E' : (config.widget_background_color || '#FFFFFF');
  const textColor = isDark ? '#E5E7EB' : '#111827';
  const subtextColor = isDark ? '#9CA3AF' : '#6B7280';
  const agentBubbleBg = isDark ? '#374151' : '#F3F4F6';
  const headerText = config.widget_header_text || 'Chat with us';
  const agentName = config.widget_agent_display_name || 'Support';
  const agentTitle = config.widget_agent_title || 'AI Assistant';
  const placeholder = config.widget_input_placeholder || 'Type a message...';
  const position = config.widget_position || 'bottom-right';

  // Contrast check: compute luminance for text readability
  const hexToLum = (hex: string): number => {
    const c = hex.replace('#', '');
    if (c.length !== 6) return 0.5;
    const r = parseInt(c.substring(0, 2), 16) / 255;
    const g = parseInt(c.substring(2, 4), 16) / 255;
    const b = parseInt(c.substring(4, 6), 16) / 255;
    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
  };
  const headerTextColor = hexToLum(primaryColor) > 0.5 ? '#111827' : '#FFFFFF';

  return (
    <div>
      <p style={s.previewTitle}>Live Preview</p>
      <div style={s.previewFrame(isDark)}>
        {/* Mini widget panel */}
        <div style={{
          width: '100%',
          borderRadius: 12,
          overflow: 'hidden',
          boxShadow: '0 4px 24px rgba(0,0,0,0.12)',
          background: bgColor,
          display: 'flex',
          flexDirection: 'column',
          height: 400,
        }}>
          {/* Header */}
          <div style={{
            background: primaryColor,
            padding: '16px',
            display: 'flex',
            alignItems: 'center',
            gap: 10,
          }}>
            {/* Avatar */}
            <div style={{
              width: 36,
              height: 36,
              borderRadius: '50%',
              background: 'rgba(255,255,255,0.2)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 14,
              color: headerTextColor,
              fontWeight: 600,
              overflow: 'hidden',
              flexShrink: 0,
            }}>
              {config.widget_agent_avatar_url ? (
                <img
                  src={config.widget_agent_avatar_url}
                  alt=""
                  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                />
              ) : (
                agentName.charAt(0).toUpperCase()
              )}
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{
                fontSize: 14,
                fontWeight: 600,
                color: headerTextColor,
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
              }}>
                {headerText}
              </div>
              <div style={{
                fontSize: 11,
                color: headerTextColor,
                opacity: 0.8,
              }}>
                {agentName} &middot; {agentTitle}
              </div>
            </div>
            {/* Close icon */}
            <div style={{
              width: 28,
              height: 28,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: headerTextColor,
              opacity: 0.7,
              fontSize: 18,
              cursor: 'default',
            }}>
              &#10005;
            </div>
          </div>

          {/* Message area */}
          <div style={{
            flex: 1,
            padding: 12,
            overflowY: 'auto',
            display: 'flex',
            flexDirection: 'column',
            gap: 8,
          }}>
            {/* Agent greeting */}
            <div style={{ display: 'flex', gap: 8, alignItems: 'flex-end' }}>
              <div style={{
                width: 24,
                height: 24,
                borderRadius: '50%',
                background: primaryColor,
                flexShrink: 0,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 10,
                color: headerTextColor,
                fontWeight: 600,
              }}>
                {agentName.charAt(0).toUpperCase()}
              </div>
              <div style={{
                background: agentBubbleBg,
                borderRadius: '12px 12px 12px 4px',
                padding: '8px 12px',
                fontSize: 13,
                color: textColor,
                maxWidth: '75%',
                lineHeight: 1.4,
              }}>
                Hi there! How can I help you today?
              </div>
            </div>

            {/* Customer message */}
            <div style={{
              display: 'flex',
              justifyContent: 'flex-end',
            }}>
              <div style={{
                background: primaryColor,
                borderRadius: '12px 12px 4px 12px',
                padding: '8px 12px',
                fontSize: 13,
                color: headerTextColor,
                maxWidth: '75%',
                lineHeight: 1.4,
              }}>
                I have a question about my order
              </div>
            </div>

            {/* Agent reply */}
            <div style={{ display: 'flex', gap: 8, alignItems: 'flex-end' }}>
              <div style={{
                width: 24,
                height: 24,
                borderRadius: '50%',
                background: primaryColor,
                flexShrink: 0,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 10,
                color: headerTextColor,
                fontWeight: 600,
              }}>
                {agentName.charAt(0).toUpperCase()}
              </div>
              <div style={{
                background: agentBubbleBg,
                borderRadius: '12px 12px 12px 4px',
                padding: '8px 12px',
                fontSize: 13,
                color: textColor,
                maxWidth: '75%',
                lineHeight: 1.4,
              }}>
                Of course! I'd be happy to help. Could you share your order number?
              </div>
            </div>
          </div>

          {/* Input bar */}
          <div style={{
            padding: '8px 12px',
            borderTop: `1px solid ${isDark ? '#374151' : '#E5E7EB'}`,
            display: 'flex',
            alignItems: 'center',
            gap: 8,
          }}>
            {config.widget_file_upload_enabled && (
              <div style={{
                width: 28,
                height: 28,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: subtextColor,
                fontSize: 16,
                cursor: 'default',
              }}>
                &#128206;
              </div>
            )}
            <div style={{
              flex: 1,
              padding: '8px 12px',
              borderRadius: 20,
              background: isDark ? '#374151' : '#F3F4F6',
              fontSize: 13,
              color: subtextColor,
            }}>
              {placeholder}
            </div>
            <div style={{
              width: 32,
              height: 32,
              borderRadius: '50%',
              background: primaryColor,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: headerTextColor,
              fontSize: 14,
              cursor: 'default',
            }}>
              &#9654;
            </div>
          </div>

          {/* Branding */}
          {config.widget_show_branding && (
            <div style={{
              textAlign: 'center',
              padding: '4px 0 6px 0',
              fontSize: 10,
              color: subtextColor,
            }}>
              Powered by Agent Red
            </div>
          )}
        </div>

        {/* Launcher button preview */}
        <div style={{
          marginTop: 16,
          display: 'flex',
          justifyContent: position === 'bottom-right' ? 'flex-end' : 'flex-start',
        }}>
          <div style={{
            width: 52,
            height: 52,
            borderRadius: '50%',
            background: primaryColor,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 4px 12px rgba(0,0,0,0.2)',
            cursor: 'default',
          }}>
            <span style={{ fontSize: 22, color: headerTextColor }}>&#128172;</span>
          </div>
        </div>

        {/* Position indicator */}
        <div style={{
          marginTop: 8,
          textAlign: 'center',
          fontSize: 11,
          color: isDark ? '#9CA3AF' : '#6B7280',
        }}>
          Position: {position} &middot; Offset: {config.widget_offset_x}px / {config.widget_offset_y}px
        </div>
      </div>
    </div>
  );
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function extractWidgetConfig(raw: Record<string, unknown>): WidgetConfig {
  const cfg: WidgetConfig = { ...DEFAULT_CONFIG };
  for (const key of Object.keys(DEFAULT_CONFIG) as Array<keyof WidgetConfig>) {
    if (raw[key] !== undefined && raw[key] !== null) {
      (cfg as unknown as Record<string, unknown>)[key] = raw[key];
    }
  }
  return cfg;
}

function safeJsonStringify(val: unknown): string {
  if (val === null || val === undefined) return '';
  try {
    return JSON.stringify(val, null, 2);
  } catch {
    return '';
  }
}

function safeJsonParse(str: string): Record<string, unknown> | null {
  if (!str.trim()) return null;
  try {
    return JSON.parse(str);
  } catch {
    return null;
  }
}

function diffConfig(
  original: WidgetConfig,
  current: WidgetConfig,
): Record<string, unknown> {
  const changes: Record<string, unknown> = {};
  for (const key of Object.keys(DEFAULT_CONFIG) as Array<keyof WidgetConfig>) {
    const origVal = JSON.stringify(original[key]);
    const currVal = JSON.stringify(current[key]);
    if (origVal !== currVal) {
      changes[key] = current[key];
    }
  }
  return changes;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export const WidgetConfigurator: React.FC<BaseComponentProps> = ({
  tenantContext,
  apiFetch,
  onNotify,
}) => {
  const [activeTab, setActiveTab] = useState<Tab>('visual');
  const [localConfig, setLocalConfig] = useState<WidgetConfig>(DEFAULT_CONFIG);
  const [savedConfig, setSavedConfig] = useState<WidgetConfig>(DEFAULT_CONFIG);
  const [jsonErrors, setJsonErrors] = useState<Record<string, string>>({});

  // Data hooks
  const config = useConfig(apiFetch);
  const { updateConfig, loading: saving, error: saveError } = useUpdateConfig(apiFetch);

  // Sync remote config to local state
  useEffect(() => {
    if (config.data?.config) {
      const extracted = extractWidgetConfig(config.data.config);
      setLocalConfig(extracted);
      setSavedConfig(extracted);
    }
  }, [config.data]);

  // Change tracking
  const pendingChanges = useMemo(
    () => diffConfig(savedConfig, localConfig),
    [savedConfig, localConfig],
  );
  const hasChanges = Object.keys(pendingChanges).length > 0;
  const changeCount = Object.keys(pendingChanges).length;

  // Field updater
  const updateField = useCallback(<K extends keyof WidgetConfig>(
    key: K,
    value: WidgetConfig[K],
  ) => {
    setLocalConfig((prev) => ({ ...prev, [key]: value }));
  }, []);

  // Save handler
  const handleSave = useCallback(async () => {
    if (!hasChanges) return;

    // Validate JSON fields have no errors
    const jsonFieldErrors = Object.entries(jsonErrors).filter(([, err]) => err);
    if (jsonFieldErrors.length > 0) {
      onNotify(
        `Please fix JSON errors before saving: ${jsonFieldErrors.map(([k]) => k).join(', ')}`,
        'error',
      );
      return;
    }

    const result = await updateConfig(pendingChanges);
    if (result?.success) {
      setSavedConfig(localConfig);
      onNotify(`Saved ${changeCount} widget setting${changeCount > 1 ? 's' : ''} successfully.`, 'success');
    } else {
      onNotify(saveError || 'Failed to save widget settings.', 'error');
    }
  }, [hasChanges, pendingChanges, localConfig, changeCount, updateConfig, onNotify, saveError, jsonErrors]);

  // Discard handler
  const handleDiscard = useCallback(() => {
    setLocalConfig(savedConfig);
    setJsonErrors({});
    onNotify('Changes discarded.', 'info');
  }, [savedConfig, onNotify]);

  // JSON field handler
  const handleJsonField = useCallback((key: keyof WidgetConfig, raw: string) => {
    if (!raw.trim()) {
      updateField(key, null as never);
      setJsonErrors((prev) => {
        const next = { ...prev };
        delete next[key];
        return next;
      });
      return;
    }
    const parsed = safeJsonParse(raw);
    if (parsed !== null) {
      updateField(key, parsed as never);
      setJsonErrors((prev) => {
        const next = { ...prev };
        delete next[key];
        return next;
      });
    } else {
      setJsonErrors((prev) => ({ ...prev, [key]: 'Invalid JSON' }));
    }
  }, [updateField]);

  // Page rules handlers
  const addPageRule = useCallback(() => {
    updateField('widget_page_rules', [...localConfig.widget_page_rules, '']);
  }, [localConfig.widget_page_rules, updateField]);

  const updatePageRule = useCallback((index: number, value: string) => {
    const rules = [...localConfig.widget_page_rules];
    rules[index] = value;
    updateField('widget_page_rules', rules);
  }, [localConfig.widget_page_rules, updateField]);

  const removePageRule = useCallback((index: number) => {
    const rules = localConfig.widget_page_rules.filter((_, i) => i !== index);
    updateField('widget_page_rules', rules);
  }, [localConfig.widget_page_rules, updateField]);

  // -------------------------------------------------------------------------
  // Loading state
  // -------------------------------------------------------------------------

  if (config.loading && !config.data) {
    return (
      <div style={s.container}>
        <div style={s.loadingContainer}>Loading widget configuration...</div>
      </div>
    );
  }

  // -------------------------------------------------------------------------
  // Error state
  // -------------------------------------------------------------------------

  if (config.error && !config.data) {
    return (
      <div style={s.container}>
        <div style={s.errorContainer}>
          <div>Failed to load configuration: {config.error}</div>
          <button style={s.retryButton} onClick={config.refetch}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  // -------------------------------------------------------------------------
  // Render
  // -------------------------------------------------------------------------

  return (
    <div style={s.container}>
      {/* Form panel */}
      <div style={s.formPanel}>
        {/* Save bar */}
        {hasChanges && (
          <div style={s.saveBar}>
            <span>{changeCount} unsaved change{changeCount > 1 ? 's' : ''}</span>
            <div>
              <button style={s.discardButton} onClick={handleDiscard} disabled={saving}>
                Discard
              </button>
              <button style={s.saveButton} onClick={handleSave} disabled={saving}>
                {saving ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </div>
        )}

        {/* Tabs */}
        <div style={s.tabs}>
          {(['visual', 'behavior', 'content'] as Tab[]).map((tab) => (
            <button
              key={tab}
              style={s.tab(activeTab === tab)}
              onClick={() => setActiveTab(tab)}
            >
              {tab === 'visual' ? 'Visual' : tab === 'behavior' ? 'Behavior' : 'Content & Targeting'}
            </button>
          ))}
        </div>

        {/* ============================================================ */}
        {/* VISUAL TAB                                                   */}
        {/* ============================================================ */}
        {activeTab === 'visual' && (
          <div style={s.card}>
            <h4 style={s.sectionTitle}>Colors</h4>
            <ColorPickerField
              label="Widget Primary Color"
              description="Header background, send button, and customer message bubbles."
              value={localConfig.widget_primary_color}
              onChange={(v) => updateField('widget_primary_color', v)}
            />
            <ColorPickerField
              label="Chat Background Color"
              description="Background of the conversation panel. White is recommended."
              value={localConfig.widget_background_color}
              onChange={(v) => updateField('widget_background_color', v)}
            />
            <ToggleField
              label="Dark Mode"
              description="Use a dark color scheme. Your primary color is still used for accents."
              value={localConfig.widget_dark_mode}
              onChange={(v) => updateField('widget_dark_mode', v)}
            />

            <h4 style={s.sectionTitle}>Position & Layout</h4>
            <Field
              label="Widget Position"
              description="Which corner of the screen the launcher appears in."
            >
              <select
                style={s.select}
                value={localConfig.widget_position}
                onChange={(e) => updateField('widget_position', e.target.value as 'bottom-right' | 'bottom-left')}
              >
                <option value="bottom-right">Bottom Right</option>
                <option value="bottom-left">Bottom Left</option>
              </select>
            </Field>
            <div style={{ display: 'flex', gap: 16 }}>
              <Field label="Horizontal Offset (px)" description="Distance from screen edge.">
                <input
                  type="number"
                  style={s.numberInput}
                  value={localConfig.widget_offset_x}
                  min={0}
                  max={100}
                  onChange={(e) => updateField('widget_offset_x', Math.max(0, Math.min(100, Number(e.target.value))))}
                />
              </Field>
              <Field label="Vertical Offset (px)" description="Distance from bottom edge.">
                <input
                  type="number"
                  style={s.numberInput}
                  value={localConfig.widget_offset_y}
                  min={0}
                  max={100}
                  onChange={(e) => updateField('widget_offset_y', Math.max(0, Math.min(100, Number(e.target.value))))}
                />
              </Field>
            </div>

            <h4 style={s.sectionTitle}>Agent Identity</h4>
            <Field
              label="Agent Display Name"
              description="Name shown in the widget header and message bubbles."
            >
              <input
                type="text"
                style={s.input}
                value={localConfig.widget_agent_display_name}
                placeholder="e.g. Support, Amy, Help Desk"
                maxLength={100}
                onChange={(e) => updateField('widget_agent_display_name', e.target.value)}
              />
            </Field>
            <Field
              label="Agent Title"
              description="Subtitle under the agent name (e.g. Customer Support)."
            >
              <input
                type="text"
                style={s.input}
                value={localConfig.widget_agent_title}
                placeholder="e.g. Customer Support, AI Assistant"
                maxLength={100}
                onChange={(e) => updateField('widget_agent_title', e.target.value)}
              />
            </Field>
            <Field
              label="Agent Avatar URL"
              description="URL of a square image (200x200px recommended). PNG, JPG, or WebP."
            >
              <input
                type="text"
                style={s.input}
                value={localConfig.widget_agent_avatar_url}
                placeholder="https://example.com/avatar.png"
                maxLength={500}
                onChange={(e) => updateField('widget_agent_avatar_url', e.target.value)}
              />
            </Field>
            <Field
              label="Widget Logo URL"
              description="Company logo in the header (120x40px landscape recommended)."
            >
              <input
                type="text"
                style={s.input}
                value={localConfig.widget_logo_url}
                placeholder="https://example.com/logo.png"
                maxLength={500}
                onChange={(e) => updateField('widget_logo_url', e.target.value)}
              />
            </Field>

            <h4 style={s.sectionTitle}>Display Options</h4>
            <ToggleField
              label="Show 'Powered by Agent Red'"
              description="Professional and Enterprise tiers can remove branding. Starter always shows."
              value={localConfig.widget_show_branding}
              onChange={(v) => {
                if (!v && (tenantContext.tier === 'starter' || tenantContext.tier === 'trial')) {
                  onNotify('Branding removal requires Professional tier or above.', 'warning');
                  return;
                }
                updateField('widget_show_branding', v);
              }}
            />
            <ToggleField
              label="Show on Mobile"
              description="Hide widget on screens narrower than 768px when disabled."
              value={localConfig.widget_mobile_enabled}
              onChange={(v) => updateField('widget_mobile_enabled', v)}
            />
          </div>
        )}

        {/* ============================================================ */}
        {/* BEHAVIOR TAB                                                 */}
        {/* ============================================================ */}
        {activeTab === 'behavior' && (
          <div style={s.card}>
            <h4 style={s.sectionTitle}>Auto-Open</h4>
            <ToggleField
              label="Auto-Open Widget"
              description="Open the widget automatically after a delay. Use sparingly."
              value={localConfig.widget_auto_open}
              onChange={(v) => updateField('widget_auto_open', v)}
            />
            {localConfig.widget_auto_open && (
              <Field
                label="Auto-Open Delay (seconds)"
                description="How long to wait before auto-opening (1-120 seconds)."
              >
                <input
                  type="number"
                  style={s.numberInput}
                  value={localConfig.widget_auto_open_delay}
                  min={1}
                  max={120}
                  onChange={(e) => updateField('widget_auto_open_delay', Math.max(1, Math.min(120, Number(e.target.value))))}
                />
              </Field>
            )}

            <h4 style={s.sectionTitle}>Offline Settings</h4>
            <Field
              label="Offline Behavior"
              description="What happens when your team is offline."
            >
              <select
                style={s.select}
                value={localConfig.widget_offline_behavior}
                onChange={(e) => updateField('widget_offline_behavior', e.target.value as 'ai_only' | 'show_form' | 'hide_widget')}
              >
                <option value="ai_only">AI Only (recommended)</option>
                <option value="show_form">Show Leave-a-Message Form</option>
                <option value="hide_widget">Hide Widget</option>
              </select>
            </Field>
            <Field
              label="Offline Message"
              description="Displayed when human agents are offline. AI remains available 24/7."
            >
              <textarea
                style={s.textarea}
                value={localConfig.widget_offline_message}
                placeholder="Our team is offline, but our AI assistant is here to help!"
                maxLength={500}
                onChange={(e) => updateField('widget_offline_message', e.target.value)}
              />
            </Field>

            <h4 style={s.sectionTitle}>Notifications & Attachments</h4>
            <ToggleField
              label="Notification Sound"
              description="Play a subtle sound when new messages arrive and widget is minimized."
              value={localConfig.widget_sound_enabled}
              onChange={(v) => updateField('widget_sound_enabled', v)}
            />
            <ToggleField
              label="File Uploads"
              description="Allow visitors to attach images and files (PNG, JPG, PDF, up to 10MB)."
              value={localConfig.widget_file_upload_enabled}
              onChange={(v) => updateField('widget_file_upload_enabled', v)}
            />
            <ToggleField
              label="Post-Chat Rating"
              description="Show thumbs up/down prompt after conversations end. Tracked in Analytics."
              value={localConfig.widget_chat_rating_enabled}
              onChange={(v) => updateField('widget_chat_rating_enabled', v)}
            />

            <h4 style={s.sectionTitle}>Pre-Chat Form</h4>
            <Field
              label="Pre-Chat Form Configuration (JSON)"
              description='Collect visitor information before chat starts. Format: {"enabled": true, "fields": [{"name": "email", "label": "Email", "type": "email", "required": true}]}'
            >
              <textarea
                style={{
                  ...s.jsonEditor,
                  borderColor: jsonErrors['widget_prechat_form'] ? '#DC2626' : '#D1D5DB',
                }}
                value={safeJsonStringify(localConfig.widget_prechat_form)}
                placeholder='{"enabled": true, "fields": [...]}'
                onChange={(e) => handleJsonField('widget_prechat_form', e.target.value)}
              />
              {jsonErrors['widget_prechat_form'] && (
                <span style={{ fontSize: 12, color: '#DC2626', marginTop: 4, display: 'block' }}>
                  {jsonErrors['widget_prechat_form']}
                </span>
              )}
            </Field>

            <h4 style={s.sectionTitle}>Operating Hours</h4>
            <Field
              label="Operating Hours (JSON)"
              description='Schedule with timezone and per-day ranges. Format: {"timezone": "America/New_York", "schedule": {"monday": [{"start": "09:00", "end": "17:00"}]}}'
            >
              <textarea
                style={{
                  ...s.jsonEditor,
                  borderColor: jsonErrors['widget_operating_hours'] ? '#DC2626' : '#D1D5DB',
                }}
                value={safeJsonStringify(localConfig.widget_operating_hours)}
                placeholder='{"timezone": "America/New_York", "schedule": {...}}'
                onChange={(e) => handleJsonField('widget_operating_hours', e.target.value)}
              />
              {jsonErrors['widget_operating_hours'] && (
                <span style={{ fontSize: 12, color: '#DC2626', marginTop: 4, display: 'block' }}>
                  {jsonErrors['widget_operating_hours']}
                </span>
              )}
            </Field>
          </div>
        )}

        {/* ============================================================ */}
        {/* CONTENT & TARGETING TAB                                      */}
        {/* ============================================================ */}
        {activeTab === 'content' && (
          <div style={s.card}>
            <h4 style={s.sectionTitle}>Header & Input Text</h4>
            <Field
              label="Widget Header Text"
              description="Custom title at the top of the widget. Defaults to 'Chat with us'."
            >
              <input
                type="text"
                style={s.input}
                value={localConfig.widget_header_text}
                placeholder="Chat with us"
                maxLength={100}
                onChange={(e) => updateField('widget_header_text', e.target.value)}
              />
            </Field>
            <Field
              label="Input Placeholder"
              description="Grey hint text in the message input box."
            >
              <input
                type="text"
                style={s.input}
                value={localConfig.widget_input_placeholder}
                placeholder="Type a message..."
                maxLength={200}
                onChange={(e) => updateField('widget_input_placeholder', e.target.value)}
              />
            </Field>

            <h4 style={s.sectionTitle}>Page Visibility Rules</h4>
            <p style={{
              fontSize: 12,
              color: '#6B7280',
              margin: '0 0 12px 0',
              lineHeight: 1.5,
            }}>
              Control which pages show the widget. Prefix with + to include or - to exclude.
              Examples: +/products/*, -/checkout, -/admin/*. If empty, the widget appears on all pages.
            </p>

            {localConfig.widget_page_rules.map((rule, idx) => (
              <div key={idx} style={s.pageRuleRow}>
                <input
                  type="text"
                  style={{ ...s.input, flex: 1 }}
                  value={rule}
                  placeholder="+/products/* or -/checkout"
                  maxLength={500}
                  onChange={(e) => updatePageRule(idx, e.target.value)}
                />
                <button
                  style={s.removeButton}
                  onClick={() => removePageRule(idx)}
                  title="Remove rule"
                >
                  &#10005;
                </button>
              </div>
            ))}

            {localConfig.widget_page_rules.length < 20 && (
              <button style={s.addButton} onClick={addPageRule}>
                + Add Rule
              </button>
            )}

            {localConfig.widget_page_rules.length === 0 && (
              <div style={{
                padding: 16,
                background: '#F9FAFB',
                borderRadius: 6,
                border: '1px dashed #D1D5DB',
                textAlign: 'center',
                fontSize: 13,
                color: '#6B7280',
                marginTop: 8,
              }}>
                No page rules configured. The widget will appear on all pages.
              </div>
            )}
          </div>
        )}
      </div>

      {/* Preview panel */}
      <div style={s.previewPanel}>
        <WidgetPreview config={localConfig} />
      </div>
    </div>
  );
};

export default WidgetConfigurator;
