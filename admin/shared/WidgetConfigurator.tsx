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
 *   - useWidgetAppearances: GET /api/config/widget-appearances (C4)
 *   - useSaveWidgetAppearance: POST /api/config/widget-appearances (C4)
 *   - useActivateWidgetAppearance: POST /api/config/widget-appearances/{name}/activate (C4, saves as draft)
 *   - useDeleteWidgetAppearance: DELETE /api/config/widget-appearances/{name} (C4)
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
import {
  useConfig,
  useUpdateConfig,
  useWidgetAppearances,
  useSaveWidgetAppearance,
  useActivateWidgetAppearance,
  useDeleteWidgetAppearance,
} from './hooks';
import type { NamedConfigSummary } from './hooks';
import { tokens } from './theme/styles';

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
  widget_mobile_fullscreen: boolean;
  widget_mobile_position: 'bottom-right' | 'bottom-left' | null;
  widget_mobile_offset_x: number | null;
  widget_mobile_offset_y: number | null;
  widget_dark_mode: boolean;
  widget_agent_bubble_color: string;
  widget_agent_bubble_text_color: string;
  widget_customer_bubble_color: string;
  widget_customer_bubble_text_color: string;
  widget_launcher_shape: 'circle' | 'rounded-square' | 'pill';
  widget_launcher_icon: 'chat' | 'headset' | 'help';
  widget_panel_height: 'short' | 'standard' | 'tall';
  widget_locale: 'auto' | 'en' | 'es' | 'fr' | 'de' | 'pt' | 'ja' | 'zh' | 'ko';
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
  // Engagement triggers (WI-0816)
  widget_exit_intent_enabled: boolean;
  widget_scroll_depth_trigger: number | null;
  // Content / Targeting (4)
  widget_greeting_message: string;
  widget_header_text: string;
  widget_input_placeholder: string;
  widget_page_rules: string[];
}

const DEFAULT_CONFIG: WidgetConfig = {
  widget_primary_color: tokens.brand,
  widget_background_color: tokens.white,
  widget_position: 'bottom-right',
  widget_offset_x: 20,
  widget_offset_y: 20,
  widget_agent_avatar_url: '',
  widget_agent_display_name: '',
  widget_agent_title: '',
  widget_logo_url: '',
  widget_show_branding: true,
  widget_mobile_enabled: true,
  widget_mobile_fullscreen: false,
  widget_mobile_position: null,
  widget_mobile_offset_x: null,
  widget_mobile_offset_y: null,
  widget_dark_mode: false,
  widget_agent_bubble_color: '',
  widget_agent_bubble_text_color: '',
  widget_customer_bubble_color: '',
  widget_customer_bubble_text_color: '',
  widget_launcher_shape: 'circle',
  widget_launcher_icon: 'chat',
  widget_panel_height: 'standard',
  widget_locale: 'auto',
  widget_offline_message: '',
  widget_auto_open: false,
  widget_auto_open_delay: 5,
  widget_operating_hours: null,
  widget_offline_behavior: 'ai_only',
  widget_prechat_form: null,
  widget_chat_rating_enabled: false,
  widget_sound_enabled: true,
  widget_file_upload_enabled: true,
  widget_exit_intent_enabled: false,
  widget_scroll_depth_trigger: null,
  widget_greeting_message: '',
  widget_header_text: '',
  widget_input_placeholder: '',
  widget_page_rules: [],
};

// ---------------------------------------------------------------------------
// Styles
// ---------------------------------------------------------------------------

// Theme-aware style factory: produces light or dark styles based on admin UI color scheme
function makeStyles(dark: boolean) {
  // Four-tier dark mode hierarchy: chrome → page → surface → border
  const bg = dark ? tokens.surface : '#FFFFFF';
  const pageBg = dark ? tokens.page : '#F9FAFB';
  const border = dark ? tokens.border : '#D1D5DB';
  const borderLight = dark ? tokens.border : '#E5E7EB';
  const text = dark ? tokens.textPrimary : '#111827';
  const textSecondary = dark ? tokens.textMuted : '#374151';
  const textMuted = dark ? tokens.textTertiary : '#6B7280';
  const inputBg = dark ? tokens.page : '#FFFFFF';
  const inputText = dark ? tokens.textSecondary : '#111827';
  const codeEditorBg = dark ? tokens.chrome : '#F9FAFB';
  const buttonBg = dark ? tokens.border : '#F3F4F6';
  const removeBtnBg = dark ? tokens.surface : '#FFFFFF';
  const errorBg = dark ? 'rgba(220,38,38,0.1)' : '#FEF2F2';
  const errorBorder = dark ? 'rgba(220,38,38,0.3)' : '#FECACA';

  return {
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
      background: bg,
      border: `1px solid ${borderLight}`,
      borderRadius: 8,
      padding: 24,
      marginBottom: 24,
    } as React.CSSProperties,

    tabs: {
      display: 'flex',
      borderBottom: `2px solid ${borderLight}`,
      marginBottom: 24,
      gap: 0,
    } as React.CSSProperties,

    tab: (active: boolean): React.CSSProperties => ({
      padding: '10px 20px',
      fontSize: 14,
      fontWeight: active ? 600 : 500,
      color: active ? tokens.action : textMuted,
      background: 'transparent',
      border: 'none',
      borderBottom: active ? `2px solid ${tokens.action}` : '2px solid transparent',
      marginBottom: -2,
      cursor: 'pointer',
      transition: 'color 0.15s ease',
    }),

    sectionTitle: {
      fontSize: 16,
      fontWeight: 600,
      color: text,
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
      color: textSecondary,
      marginBottom: 4,
    } as React.CSSProperties,

    description: {
      display: 'block',
      fontSize: 12,
      color: textMuted,
      marginBottom: 8,
      lineHeight: 1.4,
    } as React.CSSProperties,

    input: {
      width: '100%',
      padding: '8px 12px',
      fontSize: 14,
      border: `1px solid ${border}`,
      borderRadius: 6,
      color: inputText,
      background: inputBg,
      outline: 'none',
      boxSizing: 'border-box' as const,
    } as React.CSSProperties,

    textarea: {
      width: '100%',
      padding: '8px 12px',
      fontSize: 14,
      border: `1px solid ${border}`,
      borderRadius: 6,
      color: inputText,
      background: inputBg,
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
      border: `1px solid ${border}`,
      borderRadius: 6,
      color: inputText,
      background: inputBg,
      outline: 'none',
      boxSizing: 'border-box' as const,
      cursor: 'pointer',
    } as React.CSSProperties,

    numberInput: {
      width: 120,
      padding: '8px 12px',
      fontSize: 14,
      border: `1px solid ${border}`,
      borderRadius: 6,
      color: inputText,
      background: inputBg,
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
      border: `2px solid ${border}`,
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
      background: on ? tokens.action : (dark ? '#4B5563' : '#D1D5DB'),
      position: 'relative' as const,
      transition: 'background 0.2s ease',
      flexShrink: 0,
    }),

    toggleKnob: (on: boolean): React.CSSProperties => ({
      width: 18,
      height: 18,
      borderRadius: '50%',
      background: tokens.white,
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
      border: `1px solid ${border}`,
      borderRadius: 6,
      color: inputText,
      background: codeEditorBg,
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
      border: `1px solid ${border}`,
      borderRadius: 4,
      background: removeBtnBg,
      color: tokens.danger,
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
      color: textSecondary,
      background: buttonBg,
      border: `1px solid ${border}`,
      borderRadius: 4,
      cursor: 'pointer',
    } as React.CSSProperties,

    saveBar: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '12px 24px',
      background: dark ? tokens.chrome : '#111827',
      borderRadius: 8,
      marginBottom: 16,
      color: tokens.white,
      fontSize: 14,
      border: dark ? `1px solid ${border}` : 'none',
    } as React.CSSProperties,

    saveButton: {
      padding: '8px 24px',
      background: tokens.action,
      color: tokens.white,
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
      color: textMuted,
      fontSize: 14,
    } as React.CSSProperties,

    errorContainer: {
      padding: 24,
      background: errorBg,
      border: `1px solid ${errorBorder}`,
      borderRadius: 8,
      color: dark ? '#FCA5A5' : '#991B1B',
      fontSize: 14,
      textAlign: 'center' as const,
    } as React.CSSProperties,

    retryButton: {
      marginTop: 12,
      padding: '6px 16px',
      background: tokens.danger,
      color: tokens.white,
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
      color: text,
      margin: '0 0 12px 0',
    } as React.CSSProperties,

    previewFrame: (widgetDarkMode: boolean): React.CSSProperties => ({
      background: widgetDarkMode ? '#1F2937' : '#F3F4F6',
      borderRadius: 12,
      padding: 24,
      minHeight: 480,
      position: 'relative' as const,
      overflow: 'hidden',
      border: `1px solid ${borderLight}`,
    }),

    emptyPageRules: {
      padding: 16,
      background: dark ? tokens.page : '#F9FAFB',
      borderRadius: 6,
      border: `1px dashed ${border}`,
      textAlign: 'center' as const,
      fontSize: 13,
      color: textMuted,
      marginTop: 8,
    } as React.CSSProperties,

    toggleLabel: (on: boolean): React.CSSProperties => ({
      fontSize: 13,
      color: on ? text : textMuted,
    }),

    pageRuleDesc: {
      fontSize: 12,
      color: textMuted,
      margin: '0 0 12px 0',
      lineHeight: 1.5,
    } as React.CSSProperties,

    // Named appearance bar (C4)
    appearanceBar: {
      display: 'flex',
      alignItems: 'center',
      gap: 12,
      padding: '10px 16px',
      background: dark ? tokens.chrome : '#F9FAFB',
      border: `1px solid ${border}`,
      borderRadius: 8,
      marginBottom: 16,
      flexWrap: 'wrap' as const,
    } as React.CSSProperties,

    appearanceLabel: {
      fontSize: 13,
      color: textMuted,
      whiteSpace: 'nowrap' as const,
    } as React.CSSProperties,

    appearanceName: {
      fontSize: 13,
      fontWeight: 600,
      color: text,
      background: dark ? tokens.border : '#E5E7EB',
      padding: '2px 10px',
      borderRadius: 4,
    } as React.CSSProperties,

    appearanceSelect: {
      padding: '4px 8px',
      fontSize: 13,
      border: `1px solid ${border}`,
      borderRadius: 4,
      color: inputText,
      background: inputBg,
      cursor: 'pointer',
    } as React.CSSProperties,

    appearanceBtn: {
      padding: '4px 10px',
      fontSize: 12,
      fontWeight: 500,
      border: `1px solid ${border}`,
      borderRadius: 4,
      background: buttonBg,
      color: textSecondary,
      cursor: 'pointer',
      whiteSpace: 'nowrap' as const,
    } as React.CSSProperties,

    // Save As modal
    modalOverlay: {
      position: 'fixed' as const,
      inset: 0,
      background: 'rgba(0,0,0,0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 9999,
    } as React.CSSProperties,

    modalContent: {
      background: bg,
      border: `1px solid ${border}`,
      borderRadius: 12,
      padding: 24,
      width: 400,
      maxWidth: '90vw',
      boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
    } as React.CSSProperties,

    modalTitle: {
      fontSize: 16,
      fontWeight: 600,
      color: text,
      margin: '0 0 16px 0',
    } as React.CSSProperties,

    modalActions: {
      display: 'flex',
      justifyContent: 'flex-end',
      gap: 8,
      marginTop: 16,
    } as React.CSSProperties,
  };
}

// ---------------------------------------------------------------------------
// Sub-components: Form fields
// ---------------------------------------------------------------------------

type Styles = ReturnType<typeof makeStyles>;

interface FieldProps {
  label: string;
  description?: string;
  children: React.ReactNode;
  st: Styles;
}

const Field: React.FC<FieldProps> = ({ label, description, children, st }) => (
  <div style={st.fieldGroup}>
    <label style={st.label}>{label}</label>
    {description && <span style={st.description}>{description}</span>}
    {children}
  </div>
);

// ---------------------------------------------------------------------------
// HSV ↔ HEX color utilities (pure functions, no external deps)
// ---------------------------------------------------------------------------

function hexToHsv(hex: string): { h: number; s: number; v: number } {
  const c = hex.replace('#', '');
  if (c.length !== 6) return { h: 0, s: 1, v: 1 };
  const r = parseInt(c.substring(0, 2), 16) / 255;
  const g = parseInt(c.substring(2, 4), 16) / 255;
  const b = parseInt(c.substring(4, 6), 16) / 255;
  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  const d = max - min;
  let h = 0;
  if (d !== 0) {
    if (max === r) h = ((g - b) / d + (g < b ? 6 : 0)) / 6;
    else if (max === g) h = ((b - r) / d + 2) / 6;
    else h = ((r - g) / d + 4) / 6;
  }
  const s = max === 0 ? 0 : d / max;
  return { h: h * 360, s, v: max };
}

function hsvToHex(h: number, s: number, v: number): string {
  const hi = Math.floor((h / 60) % 6);
  const f = h / 60 - hi;
  const p = v * (1 - s);
  const q = v * (1 - f * s);
  const t = v * (1 - (1 - f) * s);
  let r = 0, g = 0, b = 0;
  switch (hi) {
    case 0: r = v; g = t; b = p; break;
    case 1: r = q; g = v; b = p; break;
    case 2: r = p; g = v; b = t; break;
    case 3: r = p; g = q; b = v; break;
    case 4: r = t; g = p; b = v; break;
    case 5: r = v; g = p; b = q; break;
  }
  const toHex = (n: number) => Math.round(n * 255).toString(16).padStart(2, '0');
  return `#${toHex(r)}${toHex(g)}${toHex(b)}`;
}

// Brand and popular preset colors for quick selection
const PRESET_COLORS = [
  '#ff3621', '#E53935', '#D81B60', '#8E24AA', '#5C6BC0',
  '#1E88E5', '#039BE5', '#00ACC1', '#00897B', '#43A047',
  '#7CB342', '#C0CA33', '#FDD835', '#FFB300', '#FB8C00',
  '#F4511E', '#6D4C41', '#757575', '#546E7A', '#000000',
  '#FFFFFF', '#fafaf9', '#E0E0E0', '#9E9E9E', '#212121',
];

// ---------------------------------------------------------------------------
// ColorPickerField — proper color picker with gradient area + hex input
// ---------------------------------------------------------------------------

interface ColorPickerFieldProps {
  label: string;
  description?: string;
  value: string;
  onChange: (val: string) => void;
  st: Styles;
}

const ColorPickerField: React.FC<ColorPickerFieldProps> = ({ label, description, value, onChange, st }) => {
  const [open, setOpen] = useState(false);
  const [hsv, setHsv] = useState(() => hexToHsv(value || tokens.brand));
  const svAreaRef = React.useRef<HTMLDivElement>(null);
  const hueBarRef = React.useRef<HTMLDivElement>(null);
  const containerRef = React.useRef<HTMLDivElement>(null);

  // Detect dark mode from Mantine color scheme attribute
  const isDark = typeof document !== 'undefined'
    && document.documentElement.getAttribute('data-mantine-color-scheme') === 'dark';

  // Sync external value changes into HSV state
  useEffect(() => {
    if (value && /^#[0-9a-fA-F]{6}$/.test(value)) {
      const newHsv = hexToHsv(value);
      // Only update if the hex value actually differs (avoid loop)
      if (hsvToHex(hsv.h, hsv.s, hsv.v).toLowerCase() !== value.toLowerCase()) {
        setHsv(newHsv);
      }
    }
  }, [value]);

  // Close picker when clicking outside
  useEffect(() => {
    if (!open) return;
    const handler = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, [open]);

  // Update from HSV and emit hex
  const emitFromHsv = useCallback((h: number, s: number, v: number) => {
    setHsv({ h, s, v });
    onChange(hsvToHex(h, s, v));
  }, [onChange]);

  // Saturation-Value area drag handler
  const handleSvDrag = useCallback((e: React.MouseEvent | MouseEvent) => {
    if (!svAreaRef.current) return;
    const rect = svAreaRef.current.getBoundingClientRect();
    const x = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
    const y = Math.max(0, Math.min(1, (e.clientY - rect.top) / rect.height));
    emitFromHsv(hsv.h, x, 1 - y);
  }, [hsv.h, emitFromHsv]);

  const startSvDrag = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    handleSvDrag(e);
    const onMove = (ev: MouseEvent) => {
      if (!svAreaRef.current) return;
      const rect = svAreaRef.current.getBoundingClientRect();
      const x = Math.max(0, Math.min(1, (ev.clientX - rect.left) / rect.width));
      const y = Math.max(0, Math.min(1, (ev.clientY - rect.top) / rect.height));
      emitFromHsv(hsv.h, x, 1 - y);
    };
    const onUp = () => {
      document.removeEventListener('mousemove', onMove);
      document.removeEventListener('mouseup', onUp);
    };
    document.addEventListener('mousemove', onMove);
    document.addEventListener('mouseup', onUp);
  }, [hsv.h, emitFromHsv, handleSvDrag]);

  // Hue bar drag handler
  const handleHueDrag = useCallback((e: React.MouseEvent | MouseEvent) => {
    if (!hueBarRef.current) return;
    const rect = hueBarRef.current.getBoundingClientRect();
    const x = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
    emitFromHsv(x * 360, hsv.s, hsv.v);
  }, [hsv.s, hsv.v, emitFromHsv]);

  const startHueDrag = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    handleHueDrag(e);
    const onMove = (ev: MouseEvent) => {
      if (!hueBarRef.current) return;
      const rect = hueBarRef.current.getBoundingClientRect();
      const x = Math.max(0, Math.min(1, (ev.clientX - rect.left) / rect.width));
      emitFromHsv(x * 360, hsv.s, hsv.v);
    };
    const onUp = () => {
      document.removeEventListener('mousemove', onMove);
      document.removeEventListener('mouseup', onUp);
    };
    document.addEventListener('mousemove', onMove);
    document.addEventListener('mouseup', onUp);
  }, [hsv.s, hsv.v, emitFromHsv, handleHueDrag]);

  const panelBg = isDark ? tokens.surface : '#FFFFFF';
  const panelBorder = isDark ? tokens.border : '#D1D5DB';
  const panelText = isDark ? tokens.textSecondary : '#111827';
  const panelMuted = isDark ? tokens.textTertiary : '#6B7280';

  return (
    <Field label={label} description={description} st={st}>
      <div ref={containerRef} style={{ position: 'relative' }}>
        <div style={st.colorRow}>
          {/* Swatch — toggles picker */}
          <div
            style={st.colorSwatch(value || '#FFFFFF')}
            onClick={() => setOpen(!open)}
            role="button"
            tabIndex={0}
            aria-label={`Pick ${label}`}
            onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); setOpen(!open); } }}
          />
          {/* Hex text input */}
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
            style={{ ...st.input, width: 120 }}
            onFocus={() => setOpen(false)}
          />
        </div>

        {/* Expandable color picker panel */}
        {open && (
          <div style={{
            position: 'absolute',
            top: '100%',
            left: 0,
            zIndex: 999,
            marginTop: 8,
            padding: 16,
            background: panelBg,
            border: `1px solid ${panelBorder}`,
            borderRadius: 10,
            boxShadow: '0 8px 32px rgba(0,0,0,0.25)',
            width: 280,
          }}>
            {/* Saturation / Value area */}
            <div
              ref={svAreaRef}
              onMouseDown={startSvDrag}
              style={{
                width: '100%',
                height: 160,
                borderRadius: 6,
                position: 'relative',
                cursor: 'crosshair',
                background: `linear-gradient(to right, #FFFFFF, ${hsvToHex(hsv.h, 1, 1)})`,
                marginBottom: 12,
                overflow: 'hidden',
              }}
            >
              {/* Black overlay for brightness */}
              <div style={{
                position: 'absolute',
                inset: 0,
                background: 'linear-gradient(to bottom, transparent, #000000)',
                borderRadius: 6,
              }} />
              {/* Picker thumb */}
              <div style={{
                position: 'absolute',
                left: `${hsv.s * 100}%`,
                top: `${(1 - hsv.v) * 100}%`,
                width: 14,
                height: 14,
                borderRadius: '50%',
                border: '2px solid #FFFFFF',
                boxShadow: '0 0 0 1px rgba(0,0,0,0.3), 0 2px 4px rgba(0,0,0,0.3)',
                transform: 'translate(-50%, -50%)',
                pointerEvents: 'none',
              }} />
            </div>

            {/* Hue bar */}
            <div
              ref={hueBarRef}
              onMouseDown={startHueDrag}
              style={{
                width: '100%',
                height: 14,
                borderRadius: 7,
                cursor: 'pointer',
                position: 'relative',
                background: 'linear-gradient(to right, #FF0000, #FFFF00, #00FF00, #00FFFF, #0000FF, #FF00FF, #FF0000)',
                marginBottom: 14,
              }}
            >
              {/* Hue thumb */}
              <div style={{
                position: 'absolute',
                left: `${(hsv.h / 360) * 100}%`,
                top: '50%',
                width: 16,
                height: 16,
                borderRadius: '50%',
                border: '2px solid #FFFFFF',
                boxShadow: '0 0 0 1px rgba(0,0,0,0.2), 0 1px 3px rgba(0,0,0,0.3)',
                transform: 'translate(-50%, -50%)',
                pointerEvents: 'none',
                background: hsvToHex(hsv.h, 1, 1),
              }} />
            </div>

            {/* Preset swatches */}
            <div style={{ marginBottom: 8 }}>
              <span style={{ fontSize: 11, fontWeight: 600, color: panelMuted, display: 'block', marginBottom: 6 }}>
                Presets
              </span>
              <div style={{
                display: 'flex',
                flexWrap: 'wrap',
                gap: 4,
              }}>
                {PRESET_COLORS.map((color) => (
                  <div
                    key={color}
                    onClick={() => {
                      onChange(color);
                      setHsv(hexToHsv(color));
                    }}
                    style={{
                      width: 22,
                      height: 22,
                      borderRadius: 4,
                      background: color,
                      cursor: 'pointer',
                      border: value.toLowerCase() === color.toLowerCase()
                        ? `2px solid ${tokens.brand}`
                        : `1px solid ${color === '#FFFFFF' ? panelBorder : 'transparent'}`,
                      boxSizing: 'border-box',
                    }}
                    title={color}
                    role="button"
                    tabIndex={0}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        onChange(color);
                        setHsv(hexToHsv(color));
                      }
                    }}
                  />
                ))}
              </div>
            </div>

            {/* Current value display */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              marginTop: 10,
              paddingTop: 10,
              borderTop: `1px solid ${panelBorder}`,
            }}>
              <div style={{
                width: 28,
                height: 28,
                borderRadius: 6,
                background: value || '#FFFFFF',
                border: `1px solid ${panelBorder}`,
                flexShrink: 0,
              }} />
              <span style={{ fontSize: 13, fontWeight: 500, color: panelText, fontFamily: "'JetBrains Mono', monospace" }}>
                {value || '#FFFFFF'}
              </span>
            </div>
          </div>
        )}
      </div>
    </Field>
  );
};

interface ToggleFieldProps {
  label: string;
  description?: string;
  value: boolean;
  onChange: (val: boolean) => void;
  st: Styles;
}

const ToggleField: React.FC<ToggleFieldProps> = ({ label, description, value, onChange, st }) => (
  <Field label={label} description={description} st={st}>
    <div
      style={st.toggle}
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
      <div style={st.toggleTrack(value)}>
        <div style={st.toggleKnob(value)} />
      </div>
      <span style={st.toggleLabel(value)}>
        {value ? 'Enabled' : 'Disabled'}
      </span>
    </div>
  </Field>
);

// ---------------------------------------------------------------------------
// Sub-component: Live Preview
// ---------------------------------------------------------------------------

interface QuickActionPreview {
  id: string;
  label: string;
  icon: string | null;
}

interface PreviewProps {
  config: WidgetConfig;
  st: Styles;
  quickActions?: QuickActionPreview[];
}

const WidgetPreview: React.FC<PreviewProps> = ({ config, st, quickActions }) => {
  const isDark = config.widget_dark_mode;
  // Contrast check: compute luminance for text readability
  const hexToLum = (hex: string): number => {
    const c = hex.replace('#', '');
    if (c.length !== 6) return 0.5;
    const r = parseInt(c.substring(0, 2), 16) / 255;
    const g = parseInt(c.substring(2, 4), 16) / 255;
    const b = parseInt(c.substring(4, 6), 16) / 255;
    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
  };

  const primaryColor = config.widget_primary_color || tokens.brand;
  const bgColor = isDark ? '#1A1A2E' : (config.widget_background_color || '#FFFFFF');
  const textColor = isDark ? '#E5E7EB' : '#111827';
  const subtextColor = isDark ? '#9CA3AF' : '#6B7280';
  const agentBubbleBg = config.widget_agent_bubble_color || (isDark ? '#374151' : '#F3F4F6');
  const agentBubbleText = config.widget_agent_bubble_text_color || textColor;
  const customerBubbleBg = config.widget_customer_bubble_color || primaryColor;
  const customerBubbleTextAuto = hexToLum(customerBubbleBg) > 0.5 ? '#111827' : '#FFFFFF';
  const customerBubbleText = config.widget_customer_bubble_text_color || customerBubbleTextAuto;
  const launcherShape = config.widget_launcher_shape || 'circle';
  const launcherBorderRadius = launcherShape === 'rounded-square' ? 12 : launcherShape === 'pill' ? 24 : '50%';
  const launcherIcon = config.widget_launcher_icon || 'chat';
  const headerText = config.widget_header_text || 'Chat with us';
  const agentName = config.widget_agent_display_name || 'Support';
  const agentTitle = config.widget_agent_title || 'AI Assistant';
  const placeholder = config.widget_input_placeholder || 'Type a message...';
  const position = config.widget_position || 'bottom-right';

  const headerTextColor = hexToLum(primaryColor) > 0.5 ? '#111827' : '#FFFFFF';

  return (
    <div>
      <p style={st.previewTitle}>Live preview</p>
      <div style={st.previewFrame(isDark)}>
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
                color: agentBubbleText,
                maxWidth: '75%',
                lineHeight: 1.4,
              }}>
                {config.widget_greeting_message || 'Hi there! How can I help you today?'}
              </div>
            </div>

            {/* Quick action pills (WI #245) */}
            {quickActions && quickActions.length > 0 && (
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: 6,
                marginTop: 4,
                marginBottom: 4,
              }}>
                {quickActions.slice(0, 2).map((qa) => (
                  <div
                    key={qa.id}
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: 4,
                      padding: '5px 12px',
                      borderRadius: 16,
                      border: `1px solid ${isDark ? '#374151' : '#E5E7EB'}`,
                      background: isDark ? '#2A2A2A' : '#F7F7F8',
                      fontSize: 12,
                      color: textColor,
                      cursor: 'default',
                    }}
                  >
                    {qa.icon && <span>{qa.icon}</span>}
                    <span>{qa.label}</span>
                  </div>
                ))}
              </div>
            )}

            {/* Customer message */}
            <div style={{
              display: 'flex',
              justifyContent: 'flex-end',
            }}>
              <div style={{
                background: customerBubbleBg,
                borderRadius: '12px 12px 4px 12px',
                padding: '8px 12px',
                fontSize: 13,
                color: customerBubbleText,
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
                color: agentBubbleText,
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
            borderRadius: launcherBorderRadius,
            background: primaryColor,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 4px 12px rgba(0,0,0,0.2)',
            cursor: 'default',
          }}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke={headerTextColor} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              {launcherIcon === 'headset' ? (
                <>
                  <path d="M3 18v-6a9 9 0 0 1 18 0v6" />
                  <path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3zM3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z" />
                </>
              ) : launcherIcon === 'help' ? (
                <>
                  <circle cx="12" cy="12" r="10" />
                  <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />
                  <line x1="12" y1="17" x2="12.01" y2="17" />
                </>
              ) : (
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
              )}
            </svg>
          </div>
        </div>

        {/* Position indicator */}
        <div style={{
          marginTop: 8,
          textAlign: 'center',
          fontSize: 11,
          color: isDark ? '#9CA3AF' : '#6B7280',
        }}>
          Position: {position} &middot; Shape: {launcherShape} &middot; Offset: {config.widget_offset_x}px / {config.widget_offset_y}px
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

  // Quick actions for preview (WI #245)
  const [previewQuickActions, setPreviewQuickActions] = useState<QuickActionPreview[]>([]);

  // Detect dark mode from Mantine color scheme attribute
  const isDarkMode = typeof document !== 'undefined'
    && document.documentElement.getAttribute('data-mantine-color-scheme') === 'dark';

  // Build theme-aware styles
  const s = useMemo(() => makeStyles(isDarkMode), [isDarkMode]);

  // Data hooks
  const config = useConfig(apiFetch);
  const { updateConfig, loading: saving, error: saveError } = useUpdateConfig(apiFetch);

  // Named appearance state (C4)
  const [showSaveAsModal, setShowSaveAsModal] = useState(false);
  const [saveAsName, setSaveAsName] = useState('');

  // Named appearance hooks
  const {
    data: appearancesData,
    loading: appearancesLoading,
    refetch: refetchAppearances,
  } = useWidgetAppearances(apiFetch);
  const { saveAppearance, loading: savingAppearance } = useSaveWidgetAppearance(apiFetch);
  const { activateAppearance, loading: activatingAppearance } = useActivateWidgetAppearance(apiFetch);
  const { deleteAppearance, loading: deletingAppearance } = useDeleteWidgetAppearance(apiFetch);

  const appearances: NamedConfigSummary[] = useMemo(
    () => appearancesData?.configs ?? [],
    [appearancesData],
  );
  const activeAppearanceName: string = useMemo(() => {
    const active = appearances.find((a) => a.isActive);
    return active?.name ?? 'Default';
  }, [appearances]);

  // Sync remote config to local state
  useEffect(() => {
    if (config.data?.config) {
      const extracted = extractWidgetConfig(config.data.config);
      setLocalConfig(extracted);
      setSavedConfig(extracted);
    }
  }, [config.data]);

  // Fetch quick actions for preview (WI #245)
  useEffect(() => {
    (async () => {
      try {
        const resp = await apiFetch('/api/admin/quick-actions');
        if (resp.ok) {
          const data = await resp.json();
          const actions = (data.actions || [])
            .filter((a: { isActive?: boolean; is_active?: boolean }) => a.isActive || a.is_active)
            .slice(0, 2)
            .map((a: { id: string; label: string; icon?: string | null }) => ({
              id: a.id,
              label: a.label,
              icon: a.icon || null,
            }));
          setPreviewQuickActions(actions);
        }
      } catch { /* preview is non-critical */ }
    })();
  }, [apiFetch]);

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
      onNotify(`${changeCount} widget setting${changeCount > 1 ? 's' : ''} saved to draft — activate to apply.`, 'success');
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
  // Named appearance handlers (C4)
  // -------------------------------------------------------------------------

  const handleSaveAppearance = useCallback(async () => {
    const name = saveAsName.trim();
    if (!name) return;
    const ok = await saveAppearance(name);
    if (ok) {
      setShowSaveAsModal(false);
      setSaveAsName('');
      onNotify(`Widget appearance "${name}" saved.`, 'success');
      refetchAppearances();
    } else {
      onNotify('Failed to save widget appearance.', 'error');
    }
  }, [saveAsName, saveAppearance, onNotify, refetchAppearances]);

  const handleActivateAppearance = useCallback(
    async (name: string) => {
      const ok = await activateAppearance(name);
      if (ok) {
        onNotify(`Widget appearance "${name}" activated.`, 'success');
        refetchAppearances();
        config.refetch();
      } else {
        onNotify(`Failed to activate appearance "${name}".`, 'error');
      }
    },
    [activateAppearance, onNotify, refetchAppearances, config],
  );

  const handleDeleteAppearance = useCallback(
    async (name: string) => {
      const ok = await deleteAppearance(name);
      if (ok) {
        onNotify(`Widget appearance "${name}" deleted.`, 'success');
        refetchAppearances();
      } else {
        onNotify(`Failed to delete appearance "${name}".`, 'error');
      }
    },
    [deleteAppearance, onNotify, refetchAppearances],
  );

  const handleRestoreDefaultAppearance = useCallback(async () => {
    const ok = await activateAppearance('Default');
    if (ok) {
      onNotify('Restored to Default widget appearance.', 'success');
      refetchAppearances();
      config.refetch();
    } else {
      onNotify('Failed to restore Default appearance.', 'error');
    }
  }, [activateAppearance, onNotify, refetchAppearances, config]);

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
        {/* Unsaved changes indicator */}
        {hasChanges && (
          <div style={s.saveBar}>
            <span>{changeCount} unsaved change{changeCount > 1 ? 's' : ''}</span>
          </div>
        )}

        {/* Named Appearance Bar (C4) */}
        <div style={s.appearanceBar}>
          <span style={s.appearanceLabel}>Selected appearance:</span>
          <span style={s.appearanceName}>{activeAppearanceName}</span>

          {/* Switch to a different named appearance */}
          {appearances.filter((a) => !a.isActive).length > 0 && (
            <select
              style={s.appearanceSelect}
              value=""
              onChange={(e) => {
                if (e.target.value) handleActivateAppearance(e.target.value);
              }}
              disabled={activatingAppearance}
            >
              <option value="">Switch appearance...</option>
              {appearances
                .filter((a) => !a.isActive)
                .map((a) => (
                  <option key={a.name} value={a.name}>
                    {a.name}
                  </option>
                ))}
            </select>
          )}

          {/* Save As */}
          <button
            style={s.appearanceBtn}
            onClick={() => { setSaveAsName(''); setShowSaveAsModal(true); }}
            disabled={savingAppearance}
          >
            Save as...
          </button>

          {/* Restore to Default (only visible when non-Default is active) */}
          {activeAppearanceName !== 'Default' && (
            <button
              style={s.appearanceBtn}
              onClick={handleRestoreDefaultAppearance}
              disabled={activatingAppearance}
            >
              Restore to Default
            </button>
          )}

          {/* Delete an appearance (excludes Default and active) */}
          {appearances.filter((a) => !a.isDefault && !a.isActive).length > 0 && (
            <select
              style={s.appearanceSelect}
              value=""
              onChange={(e) => {
                if (e.target.value) handleDeleteAppearance(e.target.value);
              }}
              disabled={deletingAppearance}
            >
              <option value="">Delete...</option>
              {appearances
                .filter((a) => !a.isDefault && !a.isActive)
                .map((a) => (
                  <option key={a.name} value={a.name}>
                    {a.name}
                  </option>
                ))}
            </select>
          )}
        </div>

        {/* Save As Modal (C4) */}
        {showSaveAsModal && (
          <div
            style={s.modalOverlay}
            onClick={(e) => { if (e.target === e.currentTarget) setShowSaveAsModal(false); }}
          >
            <div style={s.modalContent}>
              <h3 style={s.modalTitle}>Save widget appearance as</h3>
              <Field st={s} label="Appearance name" description="Choose a descriptive name for this set of widget settings.">
                <input
                  type="text"
                  style={s.input}
                  value={saveAsName}
                  placeholder='e.g. "Dark Theme", "Holiday", "Brand v2"'
                  maxLength={64}
                  autoFocus
                  onChange={(e) => setSaveAsName(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && saveAsName.trim()) handleSaveAppearance();
                    if (e.key === 'Escape') setShowSaveAsModal(false);
                  }}
                />
              </Field>
              {saveAsName.trim().toLowerCase() === 'default' && (
                <div style={{ fontSize: 12, color: tokens.warning, marginTop: 4 }}>
                  This will overwrite the Default appearance snapshot.
                </div>
              )}
              <div style={s.modalActions}>
                <button
                  style={s.discardButton}
                  onClick={() => setShowSaveAsModal(false)}
                >
                  Cancel
                </button>
                <button
                  style={s.saveButton}
                  onClick={handleSaveAppearance}
                  disabled={!saveAsName.trim() || savingAppearance}
                >
                  {savingAppearance ? 'Saving...' : 'Save appearance'}
                </button>
              </div>
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
              st={s}
              label="Widget primary color"
              description="Header background, send button, and customer message bubbles."
              value={localConfig.widget_primary_color}
              onChange={(v) => updateField('widget_primary_color', v)}
            />
            <ColorPickerField
              st={s}
              label="Chat background color"
              description="Background of the conversation panel. White is recommended."
              value={localConfig.widget_background_color}
              onChange={(v) => updateField('widget_background_color', v)}
            />
            <ToggleField
              st={s}
              label="Dark mode"
              description="Use a dark color scheme. Your primary color is still used for accents."
              value={localConfig.widget_dark_mode}
              onChange={(v) => updateField('widget_dark_mode', v)}
            />

            <h4 style={s.sectionTitle}>Message bubble colors</h4>
            <ColorPickerField
              st={s}
              label="Agent bubble color"
              description="Background of AI / agent messages. Leave blank for default."
              value={localConfig.widget_agent_bubble_color}
              onChange={(v) => updateField('widget_agent_bubble_color', v)}
            />
            <ColorPickerField
              st={s}
              label="Agent bubble text color"
              description="Text color in agent messages. Leave blank for auto-contrast."
              value={localConfig.widget_agent_bubble_text_color}
              onChange={(v) => updateField('widget_agent_bubble_text_color', v)}
            />
            <ColorPickerField
              st={s}
              label="Customer bubble color"
              description="Background of customer messages. Defaults to your primary color."
              value={localConfig.widget_customer_bubble_color}
              onChange={(v) => updateField('widget_customer_bubble_color', v)}
            />
            <ColorPickerField
              st={s}
              label="Customer bubble text color"
              description="Text color in customer messages. Leave blank for auto-contrast."
              value={localConfig.widget_customer_bubble_text_color}
              onChange={(v) => updateField('widget_customer_bubble_text_color', v)}
            />

            <h4 style={s.sectionTitle}>Launcher</h4>
            <Field
              st={s}
              label="Launcher shape"
              description="Shape of the floating launcher button."
            >
              <select
                style={s.select}
                value={localConfig.widget_launcher_shape}
                onChange={(e) => updateField('widget_launcher_shape', e.target.value as 'circle' | 'rounded-square' | 'pill')}
              >
                <option value="circle">Circle</option>
                <option value="rounded-square">Rounded square</option>
                <option value="pill">Pill</option>
              </select>
            </Field>
            <Field
              st={s}
              label="Launcher icon"
              description="Icon displayed on the launcher button."
            >
              <select
                style={s.select}
                value={localConfig.widget_launcher_icon}
                onChange={(e) => updateField('widget_launcher_icon', e.target.value as 'chat' | 'headset' | 'help')}
              >
                <option value="chat">Chat bubble</option>
                <option value="headset">Headset</option>
                <option value="help">Help / question mark</option>
              </select>
            </Field>
            <Field
              st={s}
              label="Panel height"
              description="Chat panel height. Short (420px) saves space; Tall (620px) for longer conversations."
            >
              <select
                style={s.select}
                value={localConfig.widget_panel_height}
                onChange={(e) => updateField('widget_panel_height', e.target.value as 'short' | 'standard' | 'tall')}
              >
                <option value="short">Short (420px)</option>
                <option value="standard">Standard (520px)</option>
                <option value="tall">Tall (620px)</option>
              </select>
            </Field>
            <Field
              st={s}
              label="Widget language"
              description="Language for widget UI text. Auto detects the visitor's browser language."
            >
              <select
                style={s.select}
                value={localConfig.widget_locale}
                onChange={(e) => updateField('widget_locale', e.target.value as WidgetConfigShape['widget_locale'])}
              >
                <option value="auto">Auto-detect</option>
                <option value="en">English</option>
                <option value="es">Espa&#241;ol</option>
                <option value="fr">Fran&#231;ais</option>
                <option value="de">Deutsch</option>
                <option value="pt">Portugu&#234;s</option>
                <option value="ja">&#26085;&#26412;&#35486;</option>
                <option value="zh">&#20013;&#25991;</option>
                <option value="ko">&#54620;&#44397;&#50612;</option>
              </select>
            </Field>

            <h4 style={s.sectionTitle}>Position & layout</h4>
            <Field
              st={s}
              label="Widget position"
              description="Which corner of the screen the launcher appears in."
            >
              <select
                style={s.select}
                value={localConfig.widget_position}
                onChange={(e) => updateField('widget_position', e.target.value as 'bottom-right' | 'bottom-left')}
              >
                <option value="bottom-right">Bottom right</option>
                <option value="bottom-left">Bottom left</option>
              </select>
            </Field>
            <div style={{ display: 'flex', gap: 16 }}>
              <Field st={s} label="Horizontal offset (px)" description="Distance from screen edge.">
                <input
                  type="number"
                  style={s.numberInput}
                  value={localConfig.widget_offset_x}
                  min={0}
                  max={100}
                  onChange={(e) => updateField('widget_offset_x', Math.max(0, Math.min(100, Number(e.target.value))))}
                />
              </Field>
              <Field st={s} label="Vertical offset (px)" description="Distance from bottom edge.">
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

            <h4 style={s.sectionTitle}>Agent identity</h4>
            <Field
              st={s}
              label="Agent display name"
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
              st={s}
              label="Agent title"
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
              st={s}
              label="Agent avatar URL"
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
              st={s}
              label="Widget logo URL"
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

            <h4 style={s.sectionTitle}>Display options</h4>
            <ToggleField
              st={s}
              label="Show 'Powered by Agent Red'"
              description={
                tenantContext.tier === 'enterprise'
                  ? 'Toggle off to remove Agent Red branding from the widget.'
                  : 'Available on Enterprise tier \u2014 Upgrade to remove branding.'
              }
              value={tenantContext.tier !== 'enterprise' ? true : localConfig.widget_show_branding}
              onChange={(v) => {
                if (tenantContext.tier !== 'enterprise') {
                  onNotify('Branding removal is available on the Enterprise tier. Upgrade to remove "Powered by Agent Red".', 'warning');
                  return;
                }
                updateField('widget_show_branding', v);
              }}
            />
            <ToggleField
              st={s}
              label="Show on mobile"
              description="Hide widget on screens narrower than 768px when disabled."
              value={localConfig.widget_mobile_enabled}
              onChange={(v) => updateField('widget_mobile_enabled', v)}
            />
            <ToggleField
              st={s}
              label="Mobile fullscreen"
              description="Chat panel fills the entire screen on mobile devices."
              value={localConfig.widget_mobile_fullscreen}
              onChange={(v) => updateField('widget_mobile_fullscreen', v)}
            />
            <Field
              st={s}
              label="Mobile position override"
              description="Override the desktop position for mobile devices. Leave empty to inherit."
            >
              <select
                style={s.select}
                value={localConfig.widget_mobile_position || ''}
                onChange={(e) => updateField('widget_mobile_position', e.target.value ? (e.target.value as 'bottom-right' | 'bottom-left') : null)}
              >
                <option value="">Inherit from desktop</option>
                <option value="bottom-right">Bottom right</option>
                <option value="bottom-left">Bottom left</option>
              </select>
            </Field>
            <div style={{ display: 'flex', gap: 16 }}>
              <Field st={s} label="Mobile horizontal offset (px)" description="Override for mobile. Leave empty to inherit.">
                <input
                  type="number"
                  style={s.numberInput}
                  value={localConfig.widget_mobile_offset_x ?? ''}
                  min={0}
                  max={100}
                  placeholder="Inherit"
                  onChange={(e) => updateField('widget_mobile_offset_x', e.target.value ? Math.max(0, Math.min(100, Number(e.target.value))) : null)}
                />
              </Field>
              <Field st={s} label="Mobile vertical offset (px)" description="Override for mobile. Leave empty to inherit.">
                <input
                  type="number"
                  style={s.numberInput}
                  value={localConfig.widget_mobile_offset_y ?? ''}
                  min={0}
                  max={100}
                  placeholder="Inherit"
                  onChange={(e) => updateField('widget_mobile_offset_y', e.target.value ? Math.max(0, Math.min(100, Number(e.target.value))) : null)}
                />
              </Field>
            </div>
          </div>
        )}

        {/* ============================================================ */}
        {/* BEHAVIOR TAB                                                 */}
        {/* ============================================================ */}
        {activeTab === 'behavior' && (
          <div style={s.card}>
            <h4 style={s.sectionTitle}>Auto-Open</h4>
            <ToggleField
              st={s}
              label="Auto-open widget"
              description="Open the widget automatically after a delay. Use sparingly."
              value={localConfig.widget_auto_open}
              onChange={(v) => updateField('widget_auto_open', v)}
            />
            {localConfig.widget_auto_open && (
              <Field
                st={s}
                label="Auto-open delay (seconds)"
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

            <h4 style={s.sectionTitle}>Offline settings</h4>
            <Field
              st={s}
              label="Offline behavior"
              description="What happens when your team is offline."
            >
              <select
                style={s.select}
                value={localConfig.widget_offline_behavior}
                onChange={(e) => updateField('widget_offline_behavior', e.target.value as 'ai_only' | 'show_form' | 'hide_widget')}
              >
                <option value="ai_only">AI Only (recommended)</option>
                <option value="show_form">Show leave-a-message form</option>
                <option value="hide_widget">Hide widget</option>
              </select>
            </Field>
            <Field
              st={s}
              label="Offline message"
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

            <h4 style={s.sectionTitle}>Notifications & attachments</h4>
            <ToggleField
              st={s}
              label="Notification sound"
              description="Play a subtle sound when new messages arrive and widget is minimized."
              value={localConfig.widget_sound_enabled}
              onChange={(v) => updateField('widget_sound_enabled', v)}
            />
            <ToggleField
              st={s}
              label="File uploads"
              description="Allow visitors to attach images and files (PNG, JPG, PDF, up to 10MB)."
              value={localConfig.widget_file_upload_enabled}
              onChange={(v) => updateField('widget_file_upload_enabled', v)}
            />
            <ToggleField
              st={s}
              label="Post-chat rating"
              description="Show thumbs up/down prompt after conversations end. Tracked in Analytics."
              value={localConfig.widget_chat_rating_enabled}
              onChange={(v) => updateField('widget_chat_rating_enabled', v)}
            />

            <h4 style={s.sectionTitle}>Engagement triggers</h4>
            <ToggleField
              st={s}
              label="Exit-intent auto-open"
              description="Desktop only: auto-opens the widget when the visitor's mouse leaves the browser window. Fires once per page visit."
              value={localConfig.widget_exit_intent_enabled}
              onChange={(v) => updateField('widget_exit_intent_enabled', v)}
            />
            <Field
              st={s}
              label="Scroll-depth auto-open (%)"
              description="Auto-open when visitor scrolls past this % of the page. Leave empty to disable."
            >
              <input
                type="number"
                min={1}
                max={100}
                step={5}
                placeholder="Disabled"
                style={s.input}
                value={localConfig.widget_scroll_depth_trigger ?? ''}
                onChange={(e) => updateField('widget_scroll_depth_trigger', e.target.value ? Math.max(1, Math.min(100, Number(e.target.value))) : null)}
              />
            </Field>

            <h4 style={s.sectionTitle}>Pre-chat form</h4>
            <Field
              st={s}
              label="Pre-chat form configuration (JSON)"
              description='Collect visitor information before chat starts. Format: {"enabled": true, "fields": [{"name": "email", "label": "Email", "type": "email", "required": true}]}'
            >
              <textarea
                style={{
                  ...s.jsonEditor,
                  borderColor: jsonErrors['widget_prechat_form'] ? tokens.danger : undefined,
                }}
                value={safeJsonStringify(localConfig.widget_prechat_form)}
                placeholder='{"enabled": true, "fields": [...]}'
                onChange={(e) => handleJsonField('widget_prechat_form', e.target.value)}
              />
              {jsonErrors['widget_prechat_form'] && (
                <span style={{ fontSize: 12, color: tokens.danger, marginTop: 4, display: 'block' }}>
                  {jsonErrors['widget_prechat_form']}
                </span>
              )}
            </Field>

            <h4 style={s.sectionTitle}>Operating hours</h4>
            <Field
              st={s}
              label="Operating hours (JSON)"
              description='Schedule with timezone and per-day ranges. Format: {"timezone": "America/New_York", "schedule": {"monday": [{"start": "09:00", "end": "17:00"}]}}'
            >
              <textarea
                style={{
                  ...s.jsonEditor,
                  borderColor: jsonErrors['widget_operating_hours'] ? tokens.danger : undefined,
                }}
                value={safeJsonStringify(localConfig.widget_operating_hours)}
                placeholder='{"timezone": "America/New_York", "schedule": {...}}'
                onChange={(e) => handleJsonField('widget_operating_hours', e.target.value)}
              />
              {jsonErrors['widget_operating_hours'] && (
                <span style={{ fontSize: 12, color: tokens.danger, marginTop: 4, display: 'block' }}>
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
            <h4 style={s.sectionTitle}>Greeting & content</h4>
            <Field
              st={s}
              label="Greeting message"
              description="Welcome message shown when a visitor opens the chat. Leave blank to hide."
            >
              <textarea
                style={s.textarea}
                value={localConfig.widget_greeting_message}
                placeholder="e.g. Hi there! How can I help you today?"
                maxLength={500}
                onChange={(e) => updateField('widget_greeting_message', e.target.value)}
              />
            </Field>
            <Field
              st={s}
              label="Widget header text"
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
              st={s}
              label="Input placeholder"
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

            <h4 style={s.sectionTitle}>Page visibility rules</h4>
            <p style={s.pageRuleDesc}>
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
                + Add rule
              </button>
            )}

            {localConfig.widget_page_rules.length === 0 && (
              <div style={s.emptyPageRules}>
                No page rules configured. The widget will appear on all pages.
              </div>
            )}
          </div>
        )}
        {/* Save draft inputs — persists field edits to draft state */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', padding: '16px 0' }}>
          <button style={s.saveButton} onClick={handleSave} disabled={saving || !hasChanges}>
            {saving ? 'Saving draft...' : 'Save draft inputs'}
          </button>
        </div>
      </div>

      {/* Preview panel */}
      <div style={s.previewPanel}>
        <WidgetPreview config={localConfig} st={s} quickActions={previewQuickActions} />
      </div>
    </div>
  );
};

export default WidgetConfigurator;
