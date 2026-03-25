import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
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
import { useConfig, useUpdateConfig, useWidgetAppearances, useSaveWidgetAppearance, useActivateWidgetAppearance, useDeleteWidgetAppearance, } from './hooks';
import { tokens } from './theme/styles';
const DEFAULT_CONFIG = {
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
    widget_header_subtitle: '',
    widget_input_placeholder: '',
    widget_page_rules: [],
};
// ---------------------------------------------------------------------------
// Styles
// ---------------------------------------------------------------------------
// Theme-aware style factory: produces light or dark styles based on admin UI color scheme
function makeStyles(dark) {
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
            maxWidth: 900,
            margin: '0 auto',
        },
        card: {
            background: bg,
            border: `1px solid ${borderLight}`,
            borderRadius: 8,
            padding: 24,
            marginBottom: 24,
        },
        tabs: {
            display: 'flex',
            borderBottom: `2px solid ${borderLight}`,
            marginBottom: 24,
            gap: 0,
        },
        tab: (active) => ({
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
        },
        fieldGroup: {
            marginBottom: 20,
        },
        label: {
            display: 'block',
            fontSize: 13,
            fontWeight: 600,
            color: textSecondary,
            marginBottom: 4,
        },
        description: {
            display: 'block',
            fontSize: 12,
            color: textMuted,
            marginBottom: 8,
            lineHeight: 1.4,
        },
        input: {
            width: '100%',
            padding: '8px 12px',
            fontSize: 14,
            border: `1px solid ${border}`,
            borderRadius: 6,
            color: inputText,
            background: inputBg,
            outline: 'none',
            boxSizing: 'border-box',
        },
        textarea: {
            width: '100%',
            padding: '8px 12px',
            fontSize: 14,
            border: `1px solid ${border}`,
            borderRadius: 6,
            color: inputText,
            background: inputBg,
            outline: 'none',
            boxSizing: 'border-box',
            resize: 'vertical',
            minHeight: 80,
            fontFamily: 'inherit',
        },
        select: {
            width: '100%',
            padding: '8px 12px',
            fontSize: 14,
            border: `1px solid ${border}`,
            borderRadius: 6,
            color: inputText,
            background: inputBg,
            outline: 'none',
            boxSizing: 'border-box',
            cursor: 'pointer',
        },
        numberInput: {
            width: 120,
            padding: '8px 12px',
            fontSize: 14,
            border: `1px solid ${border}`,
            borderRadius: 6,
            color: inputText,
            background: inputBg,
            outline: 'none',
            boxSizing: 'border-box',
        },
        colorRow: {
            display: 'flex',
            alignItems: 'center',
            gap: 12,
        },
        colorSwatch: (color) => ({
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
            position: 'absolute',
            opacity: 0,
        },
        toggle: {
            display: 'flex',
            alignItems: 'center',
            gap: 10,
            cursor: 'pointer',
        },
        toggleTrack: (on) => ({
            width: 40,
            height: 22,
            borderRadius: 11,
            background: on ? tokens.action : (dark ? '#4B5563' : '#D1D5DB'),
            position: 'relative',
            transition: 'background 0.2s ease',
            flexShrink: 0,
        }),
        toggleKnob: (on) => ({
            width: 18,
            height: 18,
            borderRadius: '50%',
            background: tokens.white,
            position: 'absolute',
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
            boxSizing: 'border-box',
            resize: 'vertical',
            minHeight: 100,
            lineHeight: 1.5,
        },
        pageRuleRow: {
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            marginBottom: 8,
        },
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
        },
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
        },
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
        },
        saveButton: {
            padding: '8px 24px',
            background: tokens.action,
            color: tokens.white,
            border: 'none',
            borderRadius: 6,
            fontSize: 14,
            fontWeight: 600,
            cursor: 'pointer',
        },
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
        },
        loadingContainer: {
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: 48,
            color: textMuted,
            fontSize: 14,
        },
        errorContainer: {
            padding: 24,
            background: errorBg,
            border: `1px solid ${errorBorder}`,
            borderRadius: 8,
            color: dark ? '#FCA5A5' : '#991B1B',
            fontSize: 14,
            textAlign: 'center',
        },
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
        },
        emptyPageRules: {
            padding: 16,
            background: dark ? tokens.page : '#F9FAFB',
            borderRadius: 6,
            border: `1px dashed ${border}`,
            textAlign: 'center',
            fontSize: 13,
            color: textMuted,
            marginTop: 8,
        },
        toggleLabel: (on) => ({
            fontSize: 13,
            color: on ? text : textMuted,
        }),
        pageRuleDesc: {
            fontSize: 12,
            color: textMuted,
            margin: '0 0 12px 0',
            lineHeight: 1.5,
        },
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
            flexWrap: 'wrap',
        },
        appearanceLabel: {
            fontSize: 13,
            color: textMuted,
            whiteSpace: 'nowrap',
        },
        appearanceName: {
            fontSize: 13,
            fontWeight: 600,
            color: text,
            background: dark ? tokens.border : '#E5E7EB',
            padding: '2px 10px',
            borderRadius: 4,
        },
        appearanceSelect: {
            padding: '4px 8px',
            fontSize: 13,
            border: `1px solid ${border}`,
            borderRadius: 4,
            color: inputText,
            background: inputBg,
            cursor: 'pointer',
        },
        appearanceBtn: {
            padding: '4px 10px',
            fontSize: 12,
            fontWeight: 500,
            border: `1px solid ${border}`,
            borderRadius: 4,
            background: buttonBg,
            color: textSecondary,
            cursor: 'pointer',
            whiteSpace: 'nowrap',
        },
        // Save As modal
        modalOverlay: {
            position: 'fixed',
            inset: 0,
            background: 'rgba(0,0,0,0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 9999,
        },
        modalContent: {
            background: bg,
            border: `1px solid ${border}`,
            borderRadius: 12,
            padding: 24,
            width: 400,
            maxWidth: '90vw',
            boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
        },
        modalTitle: {
            fontSize: 16,
            fontWeight: 600,
            color: text,
            margin: '0 0 16px 0',
        },
        modalActions: {
            display: 'flex',
            justifyContent: 'flex-end',
            gap: 8,
            marginTop: 16,
        },
    };
}
const Field = ({ label, description, children, st }) => (_jsxs("div", { style: st.fieldGroup, children: [_jsx("label", { style: st.label, children: label }), description && _jsx("span", { style: st.description, children: description }), children] }));
// ---------------------------------------------------------------------------
// HSV ↔ HEX color utilities (pure functions, no external deps)
// ---------------------------------------------------------------------------
function hexToHsv(hex) {
    const c = hex.replace('#', '');
    if (c.length !== 6)
        return { h: 0, s: 1, v: 1 };
    const r = parseInt(c.substring(0, 2), 16) / 255;
    const g = parseInt(c.substring(2, 4), 16) / 255;
    const b = parseInt(c.substring(4, 6), 16) / 255;
    const max = Math.max(r, g, b);
    const min = Math.min(r, g, b);
    const d = max - min;
    let h = 0;
    if (d !== 0) {
        if (max === r)
            h = ((g - b) / d + (g < b ? 6 : 0)) / 6;
        else if (max === g)
            h = ((b - r) / d + 2) / 6;
        else
            h = ((r - g) / d + 4) / 6;
    }
    const s = max === 0 ? 0 : d / max;
    return { h: h * 360, s, v: max };
}
function hsvToHex(h, s, v) {
    const hi = Math.floor((h / 60) % 6);
    const f = h / 60 - hi;
    const p = v * (1 - s);
    const q = v * (1 - f * s);
    const t = v * (1 - (1 - f) * s);
    let r = 0, g = 0, b = 0;
    switch (hi) {
        case 0:
            r = v;
            g = t;
            b = p;
            break;
        case 1:
            r = q;
            g = v;
            b = p;
            break;
        case 2:
            r = p;
            g = v;
            b = t;
            break;
        case 3:
            r = p;
            g = q;
            b = v;
            break;
        case 4:
            r = t;
            g = p;
            b = v;
            break;
        case 5:
            r = v;
            g = p;
            b = q;
            break;
    }
    const toHex = (n) => Math.round(n * 255).toString(16).padStart(2, '0');
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
const ColorPickerField = ({ label, description, value, onChange, st }) => {
    const [open, setOpen] = useState(false);
    const [hsv, setHsv] = useState(() => hexToHsv(value || tokens.brand));
    const svAreaRef = React.useRef(null);
    const hueBarRef = React.useRef(null);
    const containerRef = React.useRef(null);
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
        if (!open)
            return;
        const handler = (e) => {
            if (containerRef.current && !containerRef.current.contains(e.target)) {
                setOpen(false);
            }
        };
        document.addEventListener('mousedown', handler);
        return () => document.removeEventListener('mousedown', handler);
    }, [open]);
    // Update from HSV and emit hex
    const emitFromHsv = useCallback((h, s, v) => {
        setHsv({ h, s, v });
        onChange(hsvToHex(h, s, v));
    }, [onChange]);
    // Saturation-Value area drag handler
    const handleSvDrag = useCallback((e) => {
        if (!svAreaRef.current)
            return;
        const rect = svAreaRef.current.getBoundingClientRect();
        const x = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
        const y = Math.max(0, Math.min(1, (e.clientY - rect.top) / rect.height));
        emitFromHsv(hsv.h, x, 1 - y);
    }, [hsv.h, emitFromHsv]);
    const startSvDrag = useCallback((e) => {
        e.preventDefault();
        handleSvDrag(e);
        const onMove = (ev) => {
            if (!svAreaRef.current)
                return;
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
    const handleHueDrag = useCallback((e) => {
        if (!hueBarRef.current)
            return;
        const rect = hueBarRef.current.getBoundingClientRect();
        const x = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
        emitFromHsv(x * 360, hsv.s, hsv.v);
    }, [hsv.s, hsv.v, emitFromHsv]);
    const startHueDrag = useCallback((e) => {
        e.preventDefault();
        handleHueDrag(e);
        const onMove = (ev) => {
            if (!hueBarRef.current)
                return;
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
    return (_jsx(Field, { label: label, description: description, st: st, children: _jsxs("div", { ref: containerRef, style: { position: 'relative' }, children: [_jsxs("div", { style: st.colorRow, children: [_jsx("div", { style: st.colorSwatch(value || '#FFFFFF'), onClick: () => setOpen(!open), role: "button", tabIndex: 0, "aria-label": `Pick ${label}`, onKeyDown: (e) => { if (e.key === 'Enter' || e.key === ' ') {
                                e.preventDefault();
                                setOpen(!open);
                            } } }), _jsx("input", { type: "text", value: value, onChange: (e) => {
                                const val = e.target.value;
                                if (/^#[0-9a-fA-F]{0,6}$/.test(val) || val === '') {
                                    onChange(val);
                                }
                            }, placeholder: "#RRGGBB", maxLength: 7, style: { ...st.input, width: 120 }, onFocus: () => setOpen(false) })] }), open && (_jsxs("div", { style: {
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
                    }, children: [_jsxs("div", { ref: svAreaRef, onMouseDown: startSvDrag, style: {
                                width: '100%',
                                height: 160,
                                borderRadius: 6,
                                position: 'relative',
                                cursor: 'crosshair',
                                background: `linear-gradient(to right, #FFFFFF, ${hsvToHex(hsv.h, 1, 1)})`,
                                marginBottom: 12,
                                overflow: 'hidden',
                            }, children: [_jsx("div", { style: {
                                        position: 'absolute',
                                        inset: 0,
                                        background: 'linear-gradient(to bottom, transparent, #000000)',
                                        borderRadius: 6,
                                    } }), _jsx("div", { style: {
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
                                    } })] }), _jsx("div", { ref: hueBarRef, onMouseDown: startHueDrag, style: {
                                width: '100%',
                                height: 14,
                                borderRadius: 7,
                                cursor: 'pointer',
                                position: 'relative',
                                background: 'linear-gradient(to right, #FF0000, #FFFF00, #00FF00, #00FFFF, #0000FF, #FF00FF, #FF0000)',
                                marginBottom: 14,
                            }, children: _jsx("div", { style: {
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
                                } }) }), _jsxs("div", { style: { marginBottom: 8 }, children: [_jsx("span", { style: { fontSize: 11, fontWeight: 600, color: panelMuted, display: 'block', marginBottom: 6 }, children: "Presets" }), _jsx("div", { style: {
                                        display: 'flex',
                                        flexWrap: 'wrap',
                                        gap: 4,
                                    }, children: PRESET_COLORS.map((color) => (_jsx("div", { onClick: () => {
                                            onChange(color);
                                            setHsv(hexToHsv(color));
                                        }, style: {
                                            width: 22,
                                            height: 22,
                                            borderRadius: 4,
                                            background: color,
                                            cursor: 'pointer',
                                            border: value.toLowerCase() === color.toLowerCase()
                                                ? `2px solid ${tokens.brand}`
                                                : `1px solid ${color === '#FFFFFF' ? panelBorder : 'transparent'}`,
                                            boxSizing: 'border-box',
                                        }, title: color, role: "button", tabIndex: 0, onKeyDown: (e) => {
                                            if (e.key === 'Enter' || e.key === ' ') {
                                                e.preventDefault();
                                                onChange(color);
                                                setHsv(hexToHsv(color));
                                            }
                                        } }, color))) })] }), _jsxs("div", { style: {
                                display: 'flex',
                                alignItems: 'center',
                                gap: 8,
                                marginTop: 10,
                                paddingTop: 10,
                                borderTop: `1px solid ${panelBorder}`,
                            }, children: [_jsx("div", { style: {
                                        width: 28,
                                        height: 28,
                                        borderRadius: 6,
                                        background: value || '#FFFFFF',
                                        border: `1px solid ${panelBorder}`,
                                        flexShrink: 0,
                                    } }), _jsx("span", { style: { fontSize: 13, fontWeight: 500, color: panelText, fontFamily: "'JetBrains Mono', monospace" }, children: value || '#FFFFFF' })] })] }))] }) }));
};
const ToggleField = ({ label, description, value, onChange, st }) => (_jsx(Field, { label: label, description: description, st: st, children: _jsxs("div", { style: st.toggle, onClick: () => onChange(!value), role: "switch", "aria-checked": value, tabIndex: 0, onKeyDown: (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                onChange(!value);
            }
        }, children: [_jsx("div", { style: st.toggleTrack(value), children: _jsx("div", { style: st.toggleKnob(value) }) }), _jsx("span", { style: st.toggleLabel(value), children: value ? 'Enabled' : 'Disabled' })] }) }));
// ---------------------------------------------------------------------------
// (Preview component removed — WI-0870: live preview now via ar:config-preview postMessage)
// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function extractWidgetConfig(raw) {
    const cfg = { ...DEFAULT_CONFIG };
    for (const key of Object.keys(DEFAULT_CONFIG)) {
        if (raw[key] !== undefined && raw[key] !== null) {
            cfg[key] = raw[key];
        }
    }
    return cfg;
}
function safeJsonStringify(val) {
    if (val === null || val === undefined)
        return '';
    try {
        return JSON.stringify(val, null, 2);
    }
    catch {
        return '';
    }
}
function safeJsonParse(str) {
    if (!str.trim())
        return null;
    try {
        return JSON.parse(str);
    }
    catch {
        return null;
    }
}
function diffConfig(original, current) {
    const changes = {};
    for (const key of Object.keys(DEFAULT_CONFIG)) {
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
export const WidgetConfigurator = ({ tenantContext, apiFetch, onNotify, }) => {
    const [activeTab, setActiveTab] = useState('visual');
    const [localConfig, setLocalConfig] = useState(DEFAULT_CONFIG);
    const [savedConfig, setSavedConfig] = useState(DEFAULT_CONFIG);
    const [jsonErrors, setJsonErrors] = useState({});
    // Quick actions for preview (WI #245)
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
    const { data: appearancesData, loading: appearancesLoading, refetch: refetchAppearances, } = useWidgetAppearances(apiFetch);
    const { saveAppearance, loading: savingAppearance } = useSaveWidgetAppearance(apiFetch);
    const { activateAppearance, loading: activatingAppearance } = useActivateWidgetAppearance(apiFetch);
    const { deleteAppearance, loading: deletingAppearance } = useDeleteWidgetAppearance(apiFetch);
    const appearances = useMemo(() => appearancesData?.configs ?? [], [appearancesData]);
    const activeAppearanceName = useMemo(() => {
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
    // Change tracking
    const pendingChanges = useMemo(() => diffConfig(savedConfig, localConfig), [savedConfig, localConfig]);
    const hasChanges = Object.keys(pendingChanges).length > 0;
    const changeCount = Object.keys(pendingChanges).length;
    // Field updater
    const updateField = useCallback((key, value) => {
        setLocalConfig((prev) => ({ ...prev, [key]: value }));
    }, []);
    // WI-0869: Dispatch live config preview to widget iframe
    useEffect(() => {
        const iframe = document.querySelector('iframe[data-agent-red-widget]');
        if (iframe?.contentWindow) {
            iframe.contentWindow.postMessage({ type: 'ar:config-preview', payload: localConfig }, '*');
        }
    }, [localConfig]);
    // Save handler
    const handleSave = useCallback(async () => {
        if (!hasChanges)
            return;
        // Validate JSON fields have no errors
        const jsonFieldErrors = Object.entries(jsonErrors).filter(([, err]) => err);
        if (jsonFieldErrors.length > 0) {
            onNotify(`Please fix JSON errors before saving: ${jsonFieldErrors.map(([k]) => k).join(', ')}`, 'error');
            return;
        }
        const result = await updateConfig(pendingChanges);
        if (result?.success) {
            setSavedConfig(localConfig);
            onNotify(`${changeCount} widget setting${changeCount > 1 ? 's' : ''} saved to draft — activate to apply.`, 'success');
        }
        else {
            const detail = result?.error || saveError || 'Failed to save widget settings.';
            onNotify(`Failed to save: ${detail}`, 'error');
        }
    }, [hasChanges, pendingChanges, localConfig, changeCount, updateConfig, onNotify, saveError, jsonErrors]);
    // Discard handler
    const handleDiscard = useCallback(() => {
        setLocalConfig(savedConfig);
        setJsonErrors({});
        onNotify('Changes discarded.', 'info');
    }, [savedConfig, onNotify]);
    // JSON field handler
    const handleJsonField = useCallback((key, raw) => {
        if (!raw.trim()) {
            updateField(key, null);
            setJsonErrors((prev) => {
                const next = { ...prev };
                delete next[key];
                return next;
            });
            return;
        }
        const parsed = safeJsonParse(raw);
        if (parsed !== null) {
            updateField(key, parsed);
            setJsonErrors((prev) => {
                const next = { ...prev };
                delete next[key];
                return next;
            });
        }
        else {
            setJsonErrors((prev) => ({ ...prev, [key]: 'Invalid JSON' }));
        }
    }, [updateField]);
    // Page rules handlers
    const addPageRule = useCallback(() => {
        updateField('widget_page_rules', [...localConfig.widget_page_rules, '']);
    }, [localConfig.widget_page_rules, updateField]);
    const updatePageRule = useCallback((index, value) => {
        const rules = [...localConfig.widget_page_rules];
        rules[index] = value;
        updateField('widget_page_rules', rules);
    }, [localConfig.widget_page_rules, updateField]);
    const removePageRule = useCallback((index) => {
        const rules = localConfig.widget_page_rules.filter((_, i) => i !== index);
        updateField('widget_page_rules', rules);
    }, [localConfig.widget_page_rules, updateField]);
    // -------------------------------------------------------------------------
    // Named appearance handlers (C4)
    // -------------------------------------------------------------------------
    const handleSaveAppearance = useCallback(async () => {
        const name = saveAsName.trim();
        if (!name)
            return;
        const ok = await saveAppearance(name);
        if (ok) {
            setShowSaveAsModal(false);
            setSaveAsName('');
            onNotify(`Widget appearance "${name}" saved.`, 'success');
            refetchAppearances();
        }
        else {
            onNotify('Failed to save widget appearance.', 'error');
        }
    }, [saveAsName, saveAppearance, onNotify, refetchAppearances]);
    const handleActivateAppearance = useCallback(async (name) => {
        const ok = await activateAppearance(name);
        if (ok) {
            onNotify(`Widget appearance "${name}" activated.`, 'success');
            refetchAppearances();
            config.refetch();
        }
        else {
            onNotify(`Failed to activate appearance "${name}".`, 'error');
        }
    }, [activateAppearance, onNotify, refetchAppearances, config]);
    const handleDeleteAppearance = useCallback(async (name) => {
        const ok = await deleteAppearance(name);
        if (ok) {
            onNotify(`Widget appearance "${name}" deleted.`, 'success');
            refetchAppearances();
        }
        else {
            onNotify(`Failed to delete appearance "${name}".`, 'error');
        }
    }, [deleteAppearance, onNotify, refetchAppearances]);
    const handleRestoreDefaultAppearance = useCallback(async () => {
        const ok = await activateAppearance('Default');
        if (ok) {
            onNotify('Restored to Default widget appearance.', 'success');
            refetchAppearances();
            config.refetch();
        }
        else {
            onNotify('Failed to restore Default appearance.', 'error');
        }
    }, [activateAppearance, onNotify, refetchAppearances, config]);
    // -------------------------------------------------------------------------
    // Loading state
    // -------------------------------------------------------------------------
    if (config.loading && !config.data) {
        return (_jsx("div", { style: s.container, children: _jsx("div", { style: s.loadingContainer, children: "Loading widget configuration..." }) }));
    }
    // -------------------------------------------------------------------------
    // Error state
    // -------------------------------------------------------------------------
    if (config.error && !config.data) {
        return (_jsx("div", { style: s.container, children: _jsxs("div", { style: s.errorContainer, children: [_jsxs("div", { children: ["Failed to load configuration: ", config.error] }), _jsx("button", { style: s.retryButton, onClick: config.refetch, children: "Retry" })] }) }));
    }
    // -------------------------------------------------------------------------
    // Render
    // -------------------------------------------------------------------------
    return (_jsx("div", { style: s.container, children: _jsxs("div", { children: [hasChanges && (_jsx("div", { style: s.saveBar, children: _jsxs("span", { children: [changeCount, " unsaved change", changeCount > 1 ? 's' : ''] }) })), _jsxs("div", { style: s.appearanceBar, children: [_jsx("span", { style: s.appearanceLabel, children: "Selected appearance:" }), _jsx("span", { style: s.appearanceName, children: activeAppearanceName }), appearances.filter((a) => !a.isActive).length > 0 && (_jsxs("select", { style: s.appearanceSelect, value: "", onChange: (e) => {
                                if (e.target.value)
                                    handleActivateAppearance(e.target.value);
                            }, disabled: activatingAppearance, children: [_jsx("option", { value: "", children: "Switch appearance..." }), appearances
                                    .filter((a) => !a.isActive)
                                    .map((a) => (_jsx("option", { value: a.name, children: a.name }, a.name)))] })), _jsx("button", { style: s.appearanceBtn, onClick: () => { setSaveAsName(''); setShowSaveAsModal(true); }, disabled: savingAppearance, children: "Save as..." }), activeAppearanceName !== 'Default' && (_jsx("button", { style: s.appearanceBtn, onClick: handleRestoreDefaultAppearance, disabled: activatingAppearance, children: "Restore to Default" })), appearances.filter((a) => !a.isDefault && !a.isActive).length > 0 && (_jsxs("select", { style: s.appearanceSelect, value: "", onChange: (e) => {
                                if (e.target.value)
                                    handleDeleteAppearance(e.target.value);
                            }, disabled: deletingAppearance, children: [_jsx("option", { value: "", children: "Delete..." }), appearances
                                    .filter((a) => !a.isDefault && !a.isActive)
                                    .map((a) => (_jsx("option", { value: a.name, children: a.name }, a.name)))] }))] }), showSaveAsModal && (_jsx("div", { style: s.modalOverlay, onClick: (e) => { if (e.target === e.currentTarget)
                        setShowSaveAsModal(false); }, children: _jsxs("div", { style: s.modalContent, children: [_jsx("h3", { style: s.modalTitle, children: "Save widget appearance as" }), _jsx(Field, { st: s, label: "Appearance name", description: "Choose a descriptive name for this set of widget settings.", children: _jsx("input", { type: "text", style: s.input, value: saveAsName, placeholder: 'e.g. "Dark Theme", "Holiday", "Brand v2"', maxLength: 64, autoFocus: true, onChange: (e) => setSaveAsName(e.target.value), onKeyDown: (e) => {
                                        if (e.key === 'Enter' && saveAsName.trim())
                                            handleSaveAppearance();
                                        if (e.key === 'Escape')
                                            setShowSaveAsModal(false);
                                    } }) }), saveAsName.trim().toLowerCase() === 'default' && (_jsx("div", { style: { fontSize: 12, color: tokens.warning, marginTop: 4 }, children: "This will overwrite the Default appearance snapshot." })), _jsxs("div", { style: s.modalActions, children: [_jsx("button", { style: s.discardButton, onClick: () => setShowSaveAsModal(false), children: "Cancel" }), _jsx("button", { style: s.saveButton, onClick: handleSaveAppearance, disabled: !saveAsName.trim() || savingAppearance, children: savingAppearance ? 'Saving...' : 'Save appearance' })] })] }) })), _jsx("div", { style: s.tabs, children: ['visual', 'behavior', 'content'].map((tab) => (_jsx("button", { style: s.tab(activeTab === tab), onClick: () => setActiveTab(tab), children: tab === 'visual' ? 'Visual' : tab === 'behavior' ? 'Behavior' : 'Content & Targeting' }, tab))) }), activeTab === 'visual' && (_jsxs("div", { style: s.card, children: [_jsx("h4", { style: s.sectionTitle, children: "Colors" }), _jsx(ColorPickerField, { st: s, label: "Widget primary color", description: "Header background, send button, and customer message bubbles.", value: localConfig.widget_primary_color, onChange: (v) => updateField('widget_primary_color', v) }), _jsx(ColorPickerField, { st: s, label: "Chat background color", description: "Background of the conversation panel. White is recommended.", value: localConfig.widget_background_color, onChange: (v) => updateField('widget_background_color', v) }), _jsx(ToggleField, { st: s, label: "Dark mode", description: "Use a dark color scheme. Your primary color is still used for accents.", value: localConfig.widget_dark_mode, onChange: (v) => updateField('widget_dark_mode', v) }), _jsx("h4", { style: s.sectionTitle, children: "Message bubble colors" }), _jsx(ColorPickerField, { st: s, label: "Agent bubble color", description: "Background of AI / agent messages. Leave blank for default.", value: localConfig.widget_agent_bubble_color, onChange: (v) => updateField('widget_agent_bubble_color', v) }), _jsx(ColorPickerField, { st: s, label: "Agent bubble text color", description: "Text color in agent messages. Leave blank for auto-contrast.", value: localConfig.widget_agent_bubble_text_color, onChange: (v) => updateField('widget_agent_bubble_text_color', v) }), _jsx(ColorPickerField, { st: s, label: "Customer bubble color", description: "Background of customer messages. Defaults to your primary color.", value: localConfig.widget_customer_bubble_color, onChange: (v) => updateField('widget_customer_bubble_color', v) }), _jsx(ColorPickerField, { st: s, label: "Customer bubble text color", description: "Text color in customer messages. Leave blank for auto-contrast.", value: localConfig.widget_customer_bubble_text_color, onChange: (v) => updateField('widget_customer_bubble_text_color', v) }), _jsx("h4", { style: s.sectionTitle, children: "Launcher" }), _jsx(Field, { st: s, label: "Launcher shape", description: "Shape of the floating launcher button.", children: _jsxs("select", { style: s.select, value: localConfig.widget_launcher_shape, onChange: (e) => updateField('widget_launcher_shape', e.target.value), children: [_jsx("option", { value: "circle", children: "Circle" }), _jsx("option", { value: "rounded-square", children: "Rounded square" }), _jsx("option", { value: "pill", children: "Pill" })] }) }), _jsx(Field, { st: s, label: "Launcher icon", description: "Icon displayed on the launcher button.", children: _jsxs("select", { style: s.select, value: localConfig.widget_launcher_icon, onChange: (e) => updateField('widget_launcher_icon', e.target.value), children: [_jsx("option", { value: "chat", children: "Chat bubble" }), _jsx("option", { value: "headset", children: "Headset" }), _jsx("option", { value: "help", children: "Help / question mark" })] }) }), _jsx(Field, { st: s, label: "Panel height", description: "Chat panel height. Short (420px) saves space; Tall (620px) for longer conversations.", children: _jsxs("select", { style: s.select, value: localConfig.widget_panel_height, onChange: (e) => updateField('widget_panel_height', e.target.value), children: [_jsx("option", { value: "short", children: "Short (420px)" }), _jsx("option", { value: "standard", children: "Standard (520px)" }), _jsx("option", { value: "tall", children: "Tall (620px)" })] }) }), _jsx(Field, { st: s, label: "Widget language", description: "Language for widget UI text. Auto detects the visitor's browser language.", children: _jsxs("select", { style: s.select, value: localConfig.widget_locale, onChange: (e) => updateField('widget_locale', e.target.value), children: [_jsx("option", { value: "auto", children: "Auto-detect" }), _jsx("option", { value: "en", children: "English" }), _jsx("option", { value: "es", children: "Espa\u00F1ol" }), _jsx("option", { value: "fr", children: "Fran\u00E7ais" }), _jsx("option", { value: "de", children: "Deutsch" }), _jsx("option", { value: "pt", children: "Portugu\u00EAs" }), _jsx("option", { value: "ja", children: "\u65E5\u672C\u8A9E" }), _jsx("option", { value: "zh", children: "\u4E2D\u6587" }), _jsx("option", { value: "ko", children: "\uD55C\uAD6D\uC5B4" })] }) }), _jsx("h4", { style: s.sectionTitle, children: "Position & layout" }), _jsx(Field, { st: s, label: "Widget position", description: "Which corner of the screen the launcher appears in.", children: _jsxs("select", { style: s.select, value: localConfig.widget_position, onChange: (e) => updateField('widget_position', e.target.value), children: [_jsx("option", { value: "bottom-right", children: "Bottom right" }), _jsx("option", { value: "bottom-left", children: "Bottom left" })] }) }), _jsxs("div", { style: { display: 'flex', gap: 16 }, children: [_jsx(Field, { st: s, label: "Horizontal offset (px)", description: "Distance from screen edge.", children: _jsx("input", { type: "number", style: s.numberInput, value: localConfig.widget_offset_x, min: 0, max: 100, onChange: (e) => updateField('widget_offset_x', Math.max(0, Math.min(100, Number(e.target.value)))) }) }), _jsx(Field, { st: s, label: "Vertical offset (px)", description: "Distance from bottom edge.", children: _jsx("input", { type: "number", style: s.numberInput, value: localConfig.widget_offset_y, min: 0, max: 100, onChange: (e) => updateField('widget_offset_y', Math.max(0, Math.min(100, Number(e.target.value)))) }) })] }), _jsx("h4", { style: s.sectionTitle, children: "Agent identity" }), _jsx(Field, { st: s, label: "Agent display name", description: "Name shown in the widget header and message bubbles.", children: _jsx("input", { type: "text", style: s.input, value: localConfig.widget_agent_display_name, placeholder: "e.g. Support, Amy, Help Desk", maxLength: 100, onChange: (e) => updateField('widget_agent_display_name', e.target.value) }) }), _jsx(Field, { st: s, label: "Agent title", description: "Subtitle under the agent name (e.g. Customer Support).", children: _jsx("input", { type: "text", style: s.input, value: localConfig.widget_agent_title, placeholder: "e.g. Customer Support, AI Assistant", maxLength: 100, onChange: (e) => updateField('widget_agent_title', e.target.value) }) }), _jsx(Field, { st: s, label: "Agent avatar URL", description: "URL of a square image (200x200px recommended). PNG, JPG, or WebP.", children: _jsx("input", { type: "text", style: s.input, value: localConfig.widget_agent_avatar_url, placeholder: "https://example.com/avatar.png", maxLength: 500, onChange: (e) => updateField('widget_agent_avatar_url', e.target.value) }) }), _jsx(Field, { st: s, label: "Widget logo URL", description: "Company logo in the header (120x40px landscape recommended).", children: _jsx("input", { type: "text", style: s.input, value: localConfig.widget_logo_url, placeholder: "https://example.com/logo.png", maxLength: 500, onChange: (e) => updateField('widget_logo_url', e.target.value) }) }), _jsx("h4", { style: s.sectionTitle, children: "Display options" }), _jsx(ToggleField, { st: s, label: "Show 'Powered by Agent Red'", description: tenantContext.tier === 'enterprise'
                                ? 'Toggle off to remove Agent Red branding from the widget.'
                                : 'Available on Enterprise tier \u2014 Upgrade to remove branding.', value: tenantContext.tier !== 'enterprise' ? true : localConfig.widget_show_branding, onChange: (v) => {
                                if (tenantContext.tier !== 'enterprise') {
                                    onNotify('Branding removal is available on the Enterprise tier. Upgrade to remove "Powered by Agent Red".', 'warning');
                                    return;
                                }
                                updateField('widget_show_branding', v);
                            } }), _jsx(ToggleField, { st: s, label: "Show on mobile", description: "Hide widget on screens narrower than 768px when disabled.", value: localConfig.widget_mobile_enabled, onChange: (v) => updateField('widget_mobile_enabled', v) }), _jsx(ToggleField, { st: s, label: "Mobile fullscreen", description: "Chat panel fills the entire screen on mobile devices.", value: localConfig.widget_mobile_fullscreen, onChange: (v) => updateField('widget_mobile_fullscreen', v) }), _jsx(Field, { st: s, label: "Mobile position override", description: "Override the desktop position for mobile devices. Leave empty to inherit.", children: _jsxs("select", { style: s.select, value: localConfig.widget_mobile_position || '', onChange: (e) => updateField('widget_mobile_position', e.target.value ? e.target.value : null), children: [_jsx("option", { value: "", children: "Inherit from desktop" }), _jsx("option", { value: "bottom-right", children: "Bottom right" }), _jsx("option", { value: "bottom-left", children: "Bottom left" })] }) }), _jsxs("div", { style: { display: 'flex', gap: 16 }, children: [_jsx(Field, { st: s, label: "Mobile horizontal offset (px)", description: "Override for mobile. Leave empty to inherit.", children: _jsx("input", { type: "number", style: s.numberInput, value: localConfig.widget_mobile_offset_x ?? '', min: 0, max: 100, placeholder: "Inherit", onChange: (e) => updateField('widget_mobile_offset_x', e.target.value ? Math.max(0, Math.min(100, Number(e.target.value))) : null) }) }), _jsx(Field, { st: s, label: "Mobile vertical offset (px)", description: "Override for mobile. Leave empty to inherit.", children: _jsx("input", { type: "number", style: s.numberInput, value: localConfig.widget_mobile_offset_y ?? '', min: 0, max: 100, placeholder: "Inherit", onChange: (e) => updateField('widget_mobile_offset_y', e.target.value ? Math.max(0, Math.min(100, Number(e.target.value))) : null) }) })] })] })), activeTab === 'behavior' && (_jsxs("div", { style: s.card, children: [_jsx("h4", { style: s.sectionTitle, children: "Auto-Open" }), _jsx(ToggleField, { st: s, label: "Auto-open widget", description: "Open the widget automatically after a delay. Use sparingly.", value: localConfig.widget_auto_open, onChange: (v) => updateField('widget_auto_open', v) }), localConfig.widget_auto_open && (_jsx(Field, { st: s, label: "Auto-open delay (seconds)", description: "How long to wait before auto-opening (1-120 seconds).", children: _jsx("input", { type: "number", style: s.numberInput, value: localConfig.widget_auto_open_delay, min: 1, max: 120, onChange: (e) => updateField('widget_auto_open_delay', Math.max(1, Math.min(120, Number(e.target.value)))) }) })), _jsx("h4", { style: s.sectionTitle, children: "Offline settings" }), _jsx(Field, { st: s, label: "Offline behavior", description: "What happens when your team is offline.", children: _jsxs("select", { style: s.select, value: localConfig.widget_offline_behavior, onChange: (e) => updateField('widget_offline_behavior', e.target.value), children: [_jsx("option", { value: "ai_only", children: "AI Only (recommended)" }), _jsx("option", { value: "show_form", children: "Show leave-a-message form" }), _jsx("option", { value: "hide_widget", children: "Hide widget" })] }) }), _jsx(Field, { st: s, label: "Offline message", description: "Displayed when human agents are offline. AI remains available 24/7.", children: _jsx("textarea", { style: s.textarea, value: localConfig.widget_offline_message, placeholder: "Our team is offline, but our AI assistant is here to help!", maxLength: 500, onChange: (e) => updateField('widget_offline_message', e.target.value) }) }), _jsx("h4", { style: s.sectionTitle, children: "Notifications & attachments" }), _jsx(ToggleField, { st: s, label: "Notification sound", description: "Play a subtle sound when new messages arrive and widget is minimized.", value: localConfig.widget_sound_enabled, onChange: (v) => updateField('widget_sound_enabled', v) }), _jsx(ToggleField, { st: s, label: "File uploads", description: "Allow visitors to attach images and files (PNG, JPG, PDF, up to 10MB).", value: localConfig.widget_file_upload_enabled, onChange: (v) => updateField('widget_file_upload_enabled', v) }), _jsx(ToggleField, { st: s, label: "Post-chat rating", description: "Show thumbs up/down prompt after conversations end. Tracked in Analytics.", value: localConfig.widget_chat_rating_enabled, onChange: (v) => updateField('widget_chat_rating_enabled', v) }), _jsx("h4", { style: s.sectionTitle, children: "Engagement triggers" }), _jsx(ToggleField, { st: s, label: "Exit-intent auto-open", description: "Desktop only: auto-opens the widget when the visitor's mouse leaves the browser window. Fires once per page visit.", value: localConfig.widget_exit_intent_enabled, onChange: (v) => updateField('widget_exit_intent_enabled', v) }), _jsx(Field, { st: s, label: "Scroll-depth auto-open (%)", description: "Auto-open when visitor scrolls past this % of the page. Leave empty to disable.", children: _jsx("input", { type: "number", min: 1, max: 100, step: 5, placeholder: "Disabled", style: s.input, value: localConfig.widget_scroll_depth_trigger ?? '', onChange: (e) => updateField('widget_scroll_depth_trigger', e.target.value ? Math.max(1, Math.min(100, Number(e.target.value))) : null) }) }), _jsx("h4", { style: s.sectionTitle, children: "Pre-chat form" }), _jsxs(Field, { st: s, label: "Pre-chat form configuration (JSON)", description: 'Collect visitor information before chat starts. Format: {"enabled": true, "fields": [{"name": "email", "label": "Email", "type": "email", "required": true}]}', children: [_jsx("textarea", { style: {
                                        ...s.jsonEditor,
                                        borderColor: jsonErrors['widget_prechat_form'] ? tokens.danger : undefined,
                                    }, value: safeJsonStringify(localConfig.widget_prechat_form), placeholder: '{"enabled": true, "fields": [...]}', onChange: (e) => handleJsonField('widget_prechat_form', e.target.value) }), jsonErrors['widget_prechat_form'] && (_jsx("span", { style: { fontSize: 12, color: tokens.danger, marginTop: 4, display: 'block' }, children: jsonErrors['widget_prechat_form'] }))] }), _jsx("h4", { style: s.sectionTitle, children: "Operating hours" }), _jsxs(Field, { st: s, label: "Operating hours (JSON)", description: 'Schedule with timezone and per-day ranges. Format: {"timezone": "America/New_York", "schedule": {"monday": [{"start": "09:00", "end": "17:00"}]}}', children: [_jsx("textarea", { style: {
                                        ...s.jsonEditor,
                                        borderColor: jsonErrors['widget_operating_hours'] ? tokens.danger : undefined,
                                    }, value: safeJsonStringify(localConfig.widget_operating_hours), placeholder: '{"timezone": "America/New_York", "schedule": {...}}', onChange: (e) => handleJsonField('widget_operating_hours', e.target.value) }), jsonErrors['widget_operating_hours'] && (_jsx("span", { style: { fontSize: 12, color: tokens.danger, marginTop: 4, display: 'block' }, children: jsonErrors['widget_operating_hours'] }))] })] })), activeTab === 'content' && (_jsxs("div", { style: s.card, children: [_jsx("h4", { style: s.sectionTitle, children: "Greeting & content" }), _jsx(Field, { st: s, label: "Greeting message", description: "Welcome message shown when a visitor opens the chat. Leave blank to hide.", children: _jsx("textarea", { style: s.textarea, value: localConfig.widget_greeting_message, placeholder: "e.g. Hi there! How can I help you today?", maxLength: 500, onChange: (e) => updateField('widget_greeting_message', e.target.value) }) }), _jsx(Field, { st: s, label: "Widget header text", description: "Custom title at the top of the widget. Defaults to 'Chat with us'.", children: _jsx("input", { type: "text", style: s.input, value: localConfig.widget_header_text, placeholder: "Chat with us", maxLength: 100, onChange: (e) => updateField('widget_header_text', e.target.value) }) }), _jsx(Field, { st: s, label: "Header subtitle", description: "Secondary text below the agent name. Default: 'We typically reply within minutes'.", children: _jsx("input", { type: "text", style: s.input, value: localConfig.widget_header_subtitle, placeholder: "We typically reply within minutes", maxLength: 150, onChange: (e) => updateField('widget_header_subtitle', e.target.value) }) }), _jsx(Field, { st: s, label: "Input placeholder", description: "Grey hint text in the message input box.", children: _jsx("input", { type: "text", style: s.input, value: localConfig.widget_input_placeholder, placeholder: "Type a message...", maxLength: 200, onChange: (e) => updateField('widget_input_placeholder', e.target.value) }) }), _jsx("h4", { style: s.sectionTitle, children: "Page visibility rules" }), _jsx("p", { style: s.pageRuleDesc, children: "Control which pages show the widget. Prefix with + to include or - to exclude. Examples: +/products/*, -/checkout, -/admin/*. If empty, the widget appears on all pages." }), localConfig.widget_page_rules.map((rule, idx) => (_jsxs("div", { style: s.pageRuleRow, children: [_jsx("input", { type: "text", style: { ...s.input, flex: 1 }, value: rule, placeholder: "+/products/* or -/checkout", maxLength: 500, onChange: (e) => updatePageRule(idx, e.target.value) }), _jsx("button", { style: s.removeButton, onClick: () => removePageRule(idx), title: "Remove rule", children: "\u2715" })] }, idx))), localConfig.widget_page_rules.length < 20 && (_jsx("button", { style: s.addButton, onClick: addPageRule, children: "+ Add rule" })), localConfig.widget_page_rules.length === 0 && (_jsx("div", { style: s.emptyPageRules, children: "No page rules configured. The widget will appear on all pages." }))] })), _jsx("div", { style: { display: 'flex', justifyContent: 'flex-end', padding: '16px 0' }, children: _jsx("button", { style: s.saveButton, onClick: handleSave, disabled: saving || !hasChanges, children: saving ? 'Saving draft...' : 'Save draft inputs' }) })] }) }));
};
export default WidgetConfigurator;
//# sourceMappingURL=WidgetConfigurator.js.map