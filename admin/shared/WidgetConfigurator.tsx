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
  widget_primary_color: '#ff3621',
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

// Theme-aware style factory: produces light or dark styles based on admin UI color scheme
function makeStyles(dark: boolean) {
  // Four-tier dark mode hierarchy: chrome #0a0a0a → page #141414 → surface #1f1f1f → border #272727
  const bg = dark ? '#1f1f1f' : '#FFFFFF';
  const pageBg = dark ? '#141414' : '#F9FAFB';
  const border = dark ? '#272727' : '#D1D5DB';
  const borderLight = dark ? '#272727' : '#E5E7EB';
  const text = dark ? '#F5F5F5' : '#111827';
  const textSecondary = dark ? '#A0A0A0' : '#374151';
  const textMuted = dark ? '#787878' : '#6B7280';
  const inputBg = dark ? '#141414' : '#FFFFFF';
  const inputText = dark ? '#E0E0E0' : '#111827';
  const codeEditorBg = dark ? '#0a0a0a' : '#F9FAFB';
  const buttonBg = dark ? '#272727' : '#F3F4F6';
  const removeBtnBg = dark ? '#1f1f1f' : '#FFFFFF';
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
      color: active ? '#ff3621' : textMuted,
      background: 'transparent',
      border: 'none',
      borderBottom: active ? '2px solid #ff3621' : '2px solid transparent',
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
      background: on ? '#ff3621' : (dark ? '#4B5563' : '#D1D5DB'),
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
      background: dark ? '#0a0a0a' : '#111827',
      borderRadius: 8,
      marginBottom: 16,
      color: '#FFFFFF',
      fontSize: 14,
      border: dark ? `1px solid ${border}` : 'none',
    } as React.CSSProperties,

    saveButton: {
      padding: '8px 24px',
      background: '#ff3621',
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
      background: dark ? '#141414' : '#F9FAFB',
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
  '#FFFFFF', '#F5F5F5', '#E0E0E0', '#9E9E9E', '#212121',
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
  const [hsv, setHsv] = useState(() => hexToHsv(value || '#ff3621'));
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

  const panelBg = isDark ? '#1f1f1f' : '#FFFFFF';
  const panelBorder = isDark ? '#272727' : '#D1D5DB';
  const panelText = isDark ? '#E0E0E0' : '#111827';
  const panelMuted = isDark ? '#787878' : '#6B7280';

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
                        ? '2px solid #ff3621'
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

interface PreviewProps {
  config: WidgetConfig;
  st: Styles;
}

const WidgetPreview: React.FC<PreviewProps> = ({ config, st }) => {
  const isDark = config.widget_dark_mode;
  const primaryColor = config.widget_primary_color || '#ff3621';
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
      <p style={st.previewTitle}>Live Preview</p>
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

  // Detect dark mode from Mantine color scheme attribute
  const isDarkMode = typeof document !== 'undefined'
    && document.documentElement.getAttribute('data-mantine-color-scheme') === 'dark';

  // Build theme-aware styles
  const s = useMemo(() => makeStyles(isDarkMode), [isDarkMode]);

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
              st={s}
              label="Widget Primary Color"
              description="Header background, send button, and customer message bubbles."
              value={localConfig.widget_primary_color}
              onChange={(v) => updateField('widget_primary_color', v)}
            />
            <ColorPickerField
              st={s}
              label="Chat Background Color"
              description="Background of the conversation panel. White is recommended."
              value={localConfig.widget_background_color}
              onChange={(v) => updateField('widget_background_color', v)}
            />
            <ToggleField
              st={s}
              label="Dark Mode"
              description="Use a dark color scheme. Your primary color is still used for accents."
              value={localConfig.widget_dark_mode}
              onChange={(v) => updateField('widget_dark_mode', v)}
            />

            <h4 style={s.sectionTitle}>Position & Layout</h4>
            <Field
              st={s}
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
              <Field st={s} label="Horizontal Offset (px)" description="Distance from screen edge.">
                <input
                  type="number"
                  style={s.numberInput}
                  value={localConfig.widget_offset_x}
                  min={0}
                  max={100}
                  onChange={(e) => updateField('widget_offset_x', Math.max(0, Math.min(100, Number(e.target.value))))}
                />
              </Field>
              <Field st={s} label="Vertical Offset (px)" description="Distance from bottom edge.">
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
              st={s}
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
              st={s}
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
              st={s}
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
              st={s}
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
              st={s}
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
              st={s}
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
              st={s}
              label="Auto-Open Widget"
              description="Open the widget automatically after a delay. Use sparingly."
              value={localConfig.widget_auto_open}
              onChange={(v) => updateField('widget_auto_open', v)}
            />
            {localConfig.widget_auto_open && (
              <Field
                st={s}
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
              st={s}
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
              st={s}
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
              st={s}
              label="Notification Sound"
              description="Play a subtle sound when new messages arrive and widget is minimized."
              value={localConfig.widget_sound_enabled}
              onChange={(v) => updateField('widget_sound_enabled', v)}
            />
            <ToggleField
              st={s}
              label="File Uploads"
              description="Allow visitors to attach images and files (PNG, JPG, PDF, up to 10MB)."
              value={localConfig.widget_file_upload_enabled}
              onChange={(v) => updateField('widget_file_upload_enabled', v)}
            />
            <ToggleField
              st={s}
              label="Post-Chat Rating"
              description="Show thumbs up/down prompt after conversations end. Tracked in Analytics."
              value={localConfig.widget_chat_rating_enabled}
              onChange={(v) => updateField('widget_chat_rating_enabled', v)}
            />

            <h4 style={s.sectionTitle}>Pre-Chat Form</h4>
            <Field
              st={s}
              label="Pre-Chat Form Configuration (JSON)"
              description='Collect visitor information before chat starts. Format: {"enabled": true, "fields": [{"name": "email", "label": "Email", "type": "email", "required": true}]}'
            >
              <textarea
                style={{
                  ...s.jsonEditor,
                  borderColor: jsonErrors['widget_prechat_form'] ? '#DC2626' : undefined,
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
              st={s}
              label="Operating Hours (JSON)"
              description='Schedule with timezone and per-day ranges. Format: {"timezone": "America/New_York", "schedule": {"monday": [{"start": "09:00", "end": "17:00"}]}}'
            >
              <textarea
                style={{
                  ...s.jsonEditor,
                  borderColor: jsonErrors['widget_operating_hours'] ? '#DC2626' : undefined,
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
              st={s}
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
              st={s}
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
                + Add Rule
              </button>
            )}

            {localConfig.widget_page_rules.length === 0 && (
              <div style={s.emptyPageRules}>
                No page rules configured. The widget will appear on all pages.
              </div>
            )}
          </div>
        )}
      </div>

      {/* Preview panel */}
      <div style={s.previewPanel}>
        <WidgetPreview config={localConfig} st={s} />
      </div>
    </div>
  );
};

export default WidgetConfigurator;
