// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

import React, { useState, useEffect } from 'react';
import {
  Paper,
  ColorPicker,
  Slider,
  Select,
  SegmentedControl,
  Switch,
  NumberInput,
  TextInput,
  Textarea,
  Chip,
  Button,
  Group,
  Stack,
  Title,
  Text,
  Box,
  Divider,
  LoadingOverlay,
  useComputedColorScheme,
  Modal,
  Alert,
  CopyButton,
  Tooltip,
  ActionIcon,
  Code,
} from '@mantine/core';
import { useAppContext } from '../layouts/StandaloneLayout';
import { useConfig, useUpdateConfig, useRotateWidgetKey } from '../../shared/hooks/index';
import { useAvatarUpload, useDeleteAvatar } from '../../shared/hooks/useAvatar';
import { HelpTooltip } from '../../shared/HelpTooltip';
import { tokens } from '../../shared/theme/styles';

const DOCS_BASE = 'https://agentredcx.com/docs/admin-guide';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const BRAND_RED = tokens.brand;

const FONT_OPTIONS = [
  { value: 'Inter, system-ui, sans-serif', label: 'Inter (System)' },
  { value: '"Inter", sans-serif', label: 'Inter' },
  { value: '"Roboto", sans-serif', label: 'Roboto' },
  { value: '"Open Sans", sans-serif', label: 'Open Sans' },
];

const ICON_OPTIONS = [
  { value: 'chat', label: 'Chat bubble' },
  { value: 'headset', label: 'Headset' },
  { value: 'help', label: 'Help circle' },
];

const PRE_CHAT_FIELDS = ['name', 'email', 'phone', 'company'];

/** Template variables available in the greeting message. */
const GREETING_VARIABLES: { token: string; label: string; preview: string }[] = [
  { token: '<FIRST_NAME>', label: 'Customer first name', preview: 'Sarah' },
  { token: '<LAST_NAME>', label: 'Customer last name', preview: 'Johnson' },
  { token: '<FULL_NAME>', label: 'Customer full name', preview: 'Sarah Johnson' },
  { token: '<COMPANY>', label: 'Company name', preview: 'Acme Inc.' },
];

/** Replace template tokens with preview sample values. */
function renderGreetingPreview(msg: string): string {
  let rendered = msg;
  for (const v of GREETING_VARIABLES) {
    rendered = rendered.replaceAll(v.token, v.preview);
  }
  return rendered;
}

// ---------------------------------------------------------------------------
// Local WidgetConfig interface + defaults
// ---------------------------------------------------------------------------

interface WidgetConfig {
  primaryColor: string;
  headerGradientEnd: string;
  headerGradientEnabled: boolean;
  fontFamily: string;
  borderRadius: number;
  launcherSize: number;
  launcherIcon: 'chat' | 'headset' | 'help' | 'custom';
  position: 'bottom-right' | 'bottom-left';
  positionOffsetX: number;
  positionOffsetY: number;
  shadowIntensity: 'none' | 'subtle' | 'standard' | 'heavy';
  panelWidth: 'compact' | 'standard' | 'wide';
  panelHeight: 'short' | 'standard' | 'tall';
  locale: 'auto' | 'en' | 'es' | 'fr' | 'de' | 'pt' | 'ja' | 'zh' | 'ko';
  colorMode: 'light' | 'dark' | 'auto';
  autoOpen: boolean;
  autoOpenDelay: number;
  greetingEnabled: boolean;
  greetingMode: 'static' | 'ai_generated';
  greetingMessage: string;
  preChatFormEnabled: boolean;
  preChatFields: string[];
  offlineFormEnabled: boolean;
  soundEnabled: boolean;
  mobileFullscreen: boolean;
  mobilePosition: 'bottom-right' | 'bottom-left' | null;
  mobileOffsetX: number | null;
  mobileOffsetY: number | null;
  pageRules: string[];
  exitIntentEnabled: boolean;
  scrollDepthTrigger: number | null;
  headerTitle: string;
  headerSubtitle: string;
  inputPlaceholder: string;
  agentAvatarUrl: string;
  agentDisplayName: string;
}

const DEFAULT_WIDGET_CONFIG: WidgetConfig = {
  primaryColor: BRAND_RED,
  headerGradientEnd: '#8B1520',
  headerGradientEnabled: false,
  fontFamily: 'Inter, system-ui, sans-serif',
  borderRadius: 16,
  launcherSize: 60,
  launcherIcon: 'chat',
  position: 'bottom-right',
  positionOffsetX: 20,
  positionOffsetY: 20,
  shadowIntensity: 'standard',
  panelWidth: 'standard',
  panelHeight: 'standard',
  locale: 'auto',
  colorMode: 'auto',
  autoOpen: false,
  autoOpenDelay: 5,
  greetingEnabled: true,
  greetingMode: 'static',
  greetingMessage: String.fromCodePoint(0x1F44B) + ' Hi there! How can I help you today?',
  preChatFormEnabled: false,
  preChatFields: ['name', 'email'],
  offlineFormEnabled: true,
  soundEnabled: true,
  mobileFullscreen: false,
  mobilePosition: null,
  mobileOffsetX: null,
  mobileOffsetY: null,
  pageRules: [],
  exitIntentEnabled: false,
  scrollDepthTrigger: null,
  headerTitle: 'Support',
  headerSubtitle: 'We typically reply within minutes',
  inputPlaceholder: 'Type your message...',
  agentAvatarUrl: '',
  agentDisplayName: '',
};

// ---------------------------------------------------------------------------
// Mapping helpers: widget_* config keys <-> WidgetConfig shape
// ---------------------------------------------------------------------------

/** Map from API config record (widget_* keys) to local WidgetConfig. */
function configToWidgetConfig(cfg: Record<string, unknown>): Partial<WidgetConfig> {
  const partial: Partial<WidgetConfig> = {};

  if (cfg.widget_primary_color != null) partial.primaryColor = String(cfg.widget_primary_color);
  if (cfg.widget_header_gradient_end != null) partial.headerGradientEnd = String(cfg.widget_header_gradient_end);
  if (cfg.widget_header_gradient_enabled != null) partial.headerGradientEnabled = Boolean(cfg.widget_header_gradient_enabled);
  if (cfg.widget_font_family != null) partial.fontFamily = String(cfg.widget_font_family);
  if (cfg.widget_border_radius != null) partial.borderRadius = Number(cfg.widget_border_radius);
  if (cfg.widget_launcher_size != null) partial.launcherSize = Number(cfg.widget_launcher_size);
  if (cfg.widget_launcher_icon != null) partial.launcherIcon = String(cfg.widget_launcher_icon) as WidgetConfig['launcherIcon'];
  if (cfg.widget_position != null) partial.position = String(cfg.widget_position) as WidgetConfig['position'];
  if (cfg.widget_position_offset_x != null) partial.positionOffsetX = Number(cfg.widget_position_offset_x);
  if (cfg.widget_position_offset_y != null) partial.positionOffsetY = Number(cfg.widget_position_offset_y);
  if (cfg.widget_shadow_intensity != null) partial.shadowIntensity = String(cfg.widget_shadow_intensity) as WidgetConfig['shadowIntensity'];
  if (cfg.widget_panel_width != null) partial.panelWidth = String(cfg.widget_panel_width) as WidgetConfig['panelWidth'];
  if (cfg.widget_panel_height != null) partial.panelHeight = String(cfg.widget_panel_height) as WidgetConfig['panelHeight'];
  if (cfg.widget_locale != null) partial.locale = String(cfg.widget_locale) as WidgetConfig['locale'];
  if (cfg.widget_color_mode != null) partial.colorMode = String(cfg.widget_color_mode) as WidgetConfig['colorMode'];
  if (cfg.widget_auto_open != null) partial.autoOpen = Boolean(cfg.widget_auto_open);
  if (cfg.widget_auto_open_delay != null) partial.autoOpenDelay = Number(cfg.widget_auto_open_delay);
  if (cfg.widget_greeting_enabled != null) partial.greetingEnabled = Boolean(cfg.widget_greeting_enabled);
  if (cfg.widget_greeting_mode != null) partial.greetingMode = String(cfg.widget_greeting_mode) as WidgetConfig['greetingMode'];
  if (cfg.widget_greeting_message != null) partial.greetingMessage = String(cfg.widget_greeting_message);
  if (cfg.widget_pre_chat_form_enabled != null) partial.preChatFormEnabled = Boolean(cfg.widget_pre_chat_form_enabled);
  if (cfg.widget_pre_chat_fields != null && Array.isArray(cfg.widget_pre_chat_fields)) partial.preChatFields = cfg.widget_pre_chat_fields as string[];
  if (cfg.widget_offline_form_enabled != null) partial.offlineFormEnabled = Boolean(cfg.widget_offline_form_enabled);
  if (cfg.widget_sound_enabled != null) partial.soundEnabled = Boolean(cfg.widget_sound_enabled);
  if (cfg.widget_mobile_fullscreen != null) partial.mobileFullscreen = Boolean(cfg.widget_mobile_fullscreen);
  if (cfg.widget_mobile_position != null) partial.mobilePosition = String(cfg.widget_mobile_position) as WidgetConfig['mobilePosition'];
  if (cfg.widget_mobile_offset_x != null) partial.mobileOffsetX = Number(cfg.widget_mobile_offset_x);
  if (cfg.widget_mobile_offset_y != null) partial.mobileOffsetY = Number(cfg.widget_mobile_offset_y);
  if (cfg.widget_page_rules != null && Array.isArray(cfg.widget_page_rules)) partial.pageRules = cfg.widget_page_rules as string[];
  if (cfg.widget_exit_intent_enabled != null) partial.exitIntentEnabled = Boolean(cfg.widget_exit_intent_enabled);
  if (cfg.widget_scroll_depth_trigger != null) partial.scrollDepthTrigger = Number(cfg.widget_scroll_depth_trigger);
  if (cfg.widget_header_title != null) partial.headerTitle = String(cfg.widget_header_title);
  if (cfg.widget_header_subtitle != null) partial.headerSubtitle = String(cfg.widget_header_subtitle);
  if (cfg.widget_input_placeholder != null) partial.inputPlaceholder = String(cfg.widget_input_placeholder);
  if (cfg.widget_agent_avatar_url != null) partial.agentAvatarUrl = String(cfg.widget_agent_avatar_url);
  if (cfg.widget_agent_display_name != null) partial.agentDisplayName = String(cfg.widget_agent_display_name);

  return partial;
}

/** Map from local WidgetConfig to API config record (widget_* keys). */
function widgetConfigToApiFields(wc: WidgetConfig): Record<string, unknown> {
  return {
    widget_primary_color: wc.primaryColor,
    widget_header_gradient_end: wc.headerGradientEnd,
    widget_header_gradient_enabled: wc.headerGradientEnabled,
    widget_font_family: wc.fontFamily,
    widget_border_radius: wc.borderRadius,
    widget_launcher_size: wc.launcherSize,
    widget_launcher_icon: wc.launcherIcon,
    widget_position: wc.position,
    widget_position_offset_x: wc.positionOffsetX,
    widget_position_offset_y: wc.positionOffsetY,
    widget_shadow_intensity: wc.shadowIntensity,
    widget_panel_width: wc.panelWidth,
    widget_panel_height: wc.panelHeight,
    widget_locale: wc.locale,
    widget_color_mode: wc.colorMode,
    widget_auto_open: wc.autoOpen,
    widget_auto_open_delay: wc.autoOpenDelay,
    widget_greeting_enabled: wc.greetingEnabled,
    widget_greeting_mode: wc.greetingMode,
    widget_greeting_message: wc.greetingMessage,
    widget_pre_chat_form_enabled: wc.preChatFormEnabled,
    widget_pre_chat_fields: wc.preChatFields,
    widget_offline_form_enabled: wc.offlineFormEnabled,
    widget_sound_enabled: wc.soundEnabled,
    widget_mobile_fullscreen: wc.mobileFullscreen,
    widget_mobile_position: wc.mobilePosition,
    widget_mobile_offset_x: wc.mobileOffsetX,
    widget_mobile_offset_y: wc.mobileOffsetY,
    widget_page_rules: wc.pageRules.length > 0 ? wc.pageRules : null,
    widget_exit_intent_enabled: wc.exitIntentEnabled,
    widget_scroll_depth_trigger: wc.scrollDepthTrigger,
    widget_header_title: wc.headerTitle,
    widget_header_subtitle: wc.headerSubtitle,
    widget_input_placeholder: wc.inputPlaceholder,
    widget_agent_avatar_url: wc.agentAvatarUrl || null,
    widget_agent_display_name: wc.agentDisplayName || null,
  };
}

// ---------------------------------------------------------------------------
// SectionHeader
// ---------------------------------------------------------------------------

function SectionHeader({ children, tooltip, docLink }: { children: React.ReactNode; tooltip?: string; docLink?: string }) {
  return (
    <Text size="sm" fw={700} c="dimmed" mb={4}>
      {children}
      {tooltip && <HelpTooltip text={tooltip} docLink={docLink} />}
    </Text>
  );
}

// ---------------------------------------------------------------------------
// ColorField — Mantine ColorPicker + hex input + swatches
// ---------------------------------------------------------------------------

function ColorField({
  label,
  value,
  onChange,
  swatches,
}: {
  label: string;
  value: string;
  onChange: (val: string) => void;
  swatches?: string[];
}) {
  const defaultSwatches = [BRAND_RED, '#2563EB', '#059669', '#7C3AED', '#D97706', '#DB2777', '#000000', '#FFFFFF'];

  return (
    <div>
      <Text size="sm" fw={500} mb={6}>{label}</Text>
      {/* Swatch preview + hex input row */}
      <Group gap={10} mb={8} align="center">
        <Box
          style={{
            width: 36,
            height: 36,
            borderRadius: 6,
            background: value || '#FFFFFF',
            border: '1px solid var(--mantine-color-default-border)',
            flexShrink: 0,
          }}
        />
        <TextInput
          value={value}
          onChange={(e) => {
            const v = e.currentTarget.value;
            if (/^#[0-9a-fA-F]{0,6}$/.test(v) || v === '') {
              onChange(v);
            }
          }}
          placeholder="#RRGGBB"
          maxLength={7}
          style={{ width: 120 }}
          styles={{ input: { fontFamily: "'JetBrains Mono', monospace", fontSize: 13 } }}
        />
      </Group>
      {/* Gradient picker with hue slider */}
      <ColorPicker
        value={value}
        onChange={onChange}
        format="hex"
        fullWidth
        swatches={swatches || defaultSwatches}
        swatchesPerRow={8}
        saturationLabel="Saturation"
        hueLabel="Hue"
        size="md"
      />
    </div>
  );
}

// ---------------------------------------------------------------------------
// Shadow intensity -> CSS box-shadow
// ---------------------------------------------------------------------------

function shadowCss(intensity: WidgetConfig['shadowIntensity'], isDark: boolean): string {
  switch (intensity) {
    case 'none': return 'none';
    case 'subtle': return isDark
      ? '0 4px 12px rgba(0,0,0,0.20)'
      : '0 4px 12px rgba(0,0,0,0.08)';
    case 'standard': return isDark
      ? '0 10px 25px rgba(0,0,0,0.30), 0 4px 10px rgba(0,0,0,0.20)'
      : '0 10px 25px rgba(0,0,0,0.15), 0 4px 10px rgba(0,0,0,0.10)';
    case 'heavy': return isDark
      ? '0 16px 40px rgba(0,0,0,0.45), 0 6px 16px rgba(0,0,0,0.30)'
      : '0 16px 40px rgba(0,0,0,0.25), 0 6px 16px rgba(0,0,0,0.15)';
    default: return '0 10px 25px rgba(0,0,0,0.15), 0 4px 10px rgba(0,0,0,0.10)';
  }
}

// ---------------------------------------------------------------------------
// Launcher icon SVGs for the preview
// ---------------------------------------------------------------------------

function LauncherIcon({ icon, size }: { icon: string; size: number }) {
  const iconSize = Math.round(size * 0.45);
  switch (icon) {
    case 'headset':
      return (
        <svg width={iconSize} height={iconSize} viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M3 18v-6a9 9 0 0 1 18 0v6" />
          <path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3zM3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z" />
        </svg>
      );
    case 'help':
      return (
        <svg width={iconSize} height={iconSize} viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="10" />
          <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />
          <line x1="12" y1="17" x2="12.01" y2="17" />
        </svg>
      );
    case 'custom':
    case 'chat':
    default:
      return (
        <svg width={iconSize} height={iconSize} viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
        </svg>
      );
  }
}

// ---------------------------------------------------------------------------
// Live Preview Component
// ---------------------------------------------------------------------------

/** Resolve panel width preset to pixel value (preview scale). */
function resolvePreviewPanelWidth(preset: WidgetConfig['panelWidth']): number {
  switch (preset) {
    case 'compact': return 300;
    case 'wide': return 400;
    case 'standard':
    default: return 350;
  }
}

/** Resolve panel width preset to real widget pixel value. */
function resolvePanelWidthPx(preset: WidgetConfig['panelWidth']): string {
  switch (preset) {
    case 'compact': return '320px';
    case 'wide': return '440px';
    case 'standard':
    default: return '380px';
  }
}

/** Resolve panel height preset to pixel value (preview scale). */
function resolvePreviewPanelHeight(preset: WidgetConfig['panelHeight']): number {
  switch (preset) {
    case 'short': return 380;
    case 'tall': return 530;
    case 'standard':
    default: return 460;
  }
}

interface QuickActionPreview {
  id: string;
  label: string;
  icon: string | null;
}

function WidgetPreview({ config, adminIsDark, quickActions }: { config: WidgetConfig; adminIsDark: boolean; quickActions?: QuickActionPreview[] }) {
  // Preview is always static — chat panel always visible so merchants see the
  // full widget appearance.  No open/close toggle (that's storefront behavior).
  const isRight = config.position === 'bottom-right';
  const dk = config.colorMode === 'auto' ? adminIsDark : config.colorMode === 'dark';

  // Color tokens — light vs dark widget mode (Mazel design revision 2026-02-03 mockup)
  // Dark path uses hardcoded hex values (NOT tokens.*) because tokens are now CSS
  // variables that resolve to light values when admin is in light mode.
  const panelBg = dk ? '#292524' : '#fff';
  const msgAreaBg = dk ? '#1c1917' : '#fafafa';
  const agentBubbleBg = dk ? '#292524' : '#fff';
  const agentBubbleBorder = dk ? '#44403c' : '#e9ecef';
  const agentBubbleText = dk ? '#f5f5f4' : '#1f2937';
  const dateSepBg = dk ? '#292524' : '#f1f3f5';
  const dateSepText = dk ? '#57534e' : '#6b7280';
  const inputBg = dk ? '#292524' : '#f1f3f5';
  const inputText = dk ? '#57534e' : '#9ca3af';
  const inputBarBg = dk ? '#0c0a09' : '#fff';
  const inputBarBorder = dk ? '#44403c' : '#e9ecef';
  const brandingText = dk ? '#57534e' : '#9ca3af';
  const pageBg = dk ? '#1c1917' : '#f8f9fa';
  const pageBorder = dk ? '#44403c' : '#dee2e6';
  // Simulated page chrome
  const chromeBg = dk ? '#0c0a09' : '#e9ecef';
  const chromeBorder = dk ? '#44403c' : '#dee2e6';
  const skeletonDark = dk ? '#292524' : '#dee2e6';
  const skeletonLight = dk ? '#0c0a09' : '#e9ecef';

  return (
    <Box
      style={{
        position: 'relative',
        width: '100%',
        minHeight: 580,
        background: pageBg,
        borderRadius: 12,
        border: `1px solid ${pageBorder}`,
        overflow: 'hidden',
        padding: 20,
      }}
    >
      {/* Simulated browser content background */}
      <Box style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, opacity: 0.35 }}>
        <Box style={{ height: 40, background: chromeBg, borderBottom: `1px solid ${chromeBorder}`, display: 'flex', alignItems: 'center', padding: '0 12px', gap: 6 }}>
          <Box style={{ width: 10, height: 10, borderRadius: '50%', background: '#ff6b6b' }} />
          <Box style={{ width: 10, height: 10, borderRadius: '50%', background: '#ffd43b' }} />
          <Box style={{ width: 10, height: 10, borderRadius: '50%', background: '#69db7c' }} />
          <Box style={{ flex: 1, height: 20, background: skeletonDark, borderRadius: 10, marginLeft: 12 }} />
        </Box>
        <Box style={{ padding: 20 }}>
          <Box style={{ height: 14, background: skeletonDark, borderRadius: 4, marginBottom: 10, width: '60%' }} />
          <Box style={{ height: 10, background: skeletonLight, borderRadius: 4, marginBottom: 8, width: '90%' }} />
          <Box style={{ height: 10, background: skeletonLight, borderRadius: 4, marginBottom: 8, width: '75%' }} />
          <Box style={{ height: 10, background: skeletonLight, borderRadius: 4, marginBottom: 20, width: '85%' }} />
          <Box style={{ height: 120, background: skeletonLight, borderRadius: 8, marginBottom: 16 }} />
          <Box style={{ height: 10, background: skeletonLight, borderRadius: 4, marginBottom: 8, width: '80%' }} />
          <Box style={{ height: 10, background: skeletonLight, borderRadius: 4, width: '65%' }} />
        </Box>
      </Box>

      {/* Chat panel — always visible in preview (no toggle) */}
      <Box
        style={{
          position: 'absolute',
          bottom: 80,
          [isRight ? 'right' : 'left']: 16,
          width: resolvePreviewPanelWidth(config.panelWidth),
          height: resolvePreviewPanelHeight(config.panelHeight),
          borderRadius: config.borderRadius,
          boxShadow: shadowCss(config.shadowIntensity, dk),
          background: panelBg,
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          fontFamily: config.fontFamily,
          zIndex: 2,
        }}
      >
        {/* Header */}
        <Box
          style={{
            background: config.headerGradientEnabled
              ? `linear-gradient(135deg, ${config.primaryColor} 0%, ${config.headerGradientEnd} 100%)`
              : config.primaryColor,
            padding: '16px 18px',
            color: '#fff',
            flexShrink: 0,
          }}
        >
          <Group gap={10} align="center">
            <Box
              style={{
                width: 36,
                height: 36,
                borderRadius: '50%',
                background: 'rgba(255,255,255,0.2)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 14,
                fontWeight: 700,
                overflow: 'hidden',
              }}
            >
              {config.agentAvatarUrl ? (
                <img
                  src={config.agentAvatarUrl}
                  alt="Agent"
                  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                />
              ) : (
                (config.agentDisplayName || config.headerTitle || 'AR').slice(0, 2).toUpperCase()
              )}
            </Box>
            <div>
              <Text size="sm" fw={700} c="#fff" lh={1.3}>
                {config.headerTitle || 'Support'}
              </Text>
              <Text size="xs" c="rgba(255,255,255,0.8)" lh={1.3}>
                {config.headerSubtitle || 'We typically reply within minutes'}
              </Text>
            </div>
          </Group>
          {/* Online indicator */}
          <Group gap={6} mt={8}>
            <Box style={{ width: 7, height: 7, borderRadius: '50%', background: '#69db7c' }} />
            <Text size="xs" c="rgba(255,255,255,0.7)">Online</Text>
          </Group>
        </Box>

        {/* Messages area */}
        <Box style={{ flex: 1, padding: '14px 16px', overflowY: 'auto', background: msgAreaBg }}>
          {/* Date separator */}
          <Group justify="center" mb={12}>
            <Text size="xs" c={dateSepText || 'dimmed'} style={{ background: dateSepBg, padding: '2px 10px', borderRadius: 10 }}>
              Today
            </Text>
          </Group>

          {/* Greeting message */}
          {config.greetingEnabled && (config.greetingMode === 'ai_generated' || config.greetingMessage) && (
            <Group gap={8} align="flex-start" mb={12}>
              <Box
                style={{
                  width: 28,
                  height: 28,
                  borderRadius: '50%',
                  background: config.primaryColor,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#fff',
                  fontSize: 10,
                  fontWeight: 700,
                  flexShrink: 0,
                  overflow: 'hidden',
                }}
              >
                {config.agentAvatarUrl ? (
                  <img
                    src={config.agentAvatarUrl}
                    alt=""
                    style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                  />
                ) : (
                  (config.agentDisplayName || 'AR').slice(0, 2).toUpperCase()
                )}
              </Box>
              <Box
                style={{
                  background: agentBubbleBg,
                  border: `1px solid ${agentBubbleBorder}`,
                  borderRadius: '4px 16px 16px 16px',
                  padding: '10px 14px',
                  maxWidth: '78%',
                }}
              >
                <Text size="xs" c={agentBubbleText} style={{ lineHeight: 1.5, ...(config.greetingMode === 'ai_generated' ? { fontStyle: 'italic' } : {}) }}>
                  {config.greetingMode === 'ai_generated'
                    ? 'Hi Sarah! I see you\u2019re browsing our new arrivals \u2014 can I help you find something?'
                    : renderGreetingPreview(config.greetingMessage)}
                </Text>
              </Box>
            </Group>
          )}

          {/* Quick action pills (WI-0797) */}
          {quickActions && quickActions.length > 0 && (
            <Box style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6, marginTop: 4, marginBottom: 12 }}>
              {quickActions.slice(0, 2).map((qa) => (
                <Box
                  key={qa.id}
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: 4,
                    padding: '5px 12px',
                    borderRadius: 16,
                    border: `1px solid ${dk ? '#44403c' : '#e5e7eb'}`,
                    background: dk ? '#292524' : '#f7f7f8',
                    fontSize: 12,
                    color: agentBubbleText,
                    cursor: 'default',
                  }}
                >
                  {qa.icon && <span>{qa.icon}</span>}
                  <span>{qa.label}</span>
                </Box>
              ))}
            </Box>
          )}

          {/* Sample customer message */}
          <Group justify="flex-end" mb={12}>
            <Box
              style={{
                background: config.primaryColor,
                color: '#fff',
                borderRadius: '16px 16px 4px 16px',
                padding: '10px 14px',
                maxWidth: '78%',
              }}
            >
              <Text size="xs" c="#fff" style={{ lineHeight: 1.5 }}>
                Hi, I have a question about my order.
              </Text>
            </Box>
          </Group>

          {/* Agent response */}
          <Group gap={8} align="flex-start">
            <Box
              style={{
                width: 28,
                height: 28,
                borderRadius: '50%',
                background: config.primaryColor,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#fff',
                fontSize: 10,
                fontWeight: 700,
                flexShrink: 0,
              }}
            >
              AR
            </Box>
            <Box
              style={{
                background: agentBubbleBg,
                border: `1px solid ${agentBubbleBorder}`,
                borderRadius: '4px 16px 16px 16px',
                padding: '10px 14px',
                maxWidth: '78%',
              }}
            >
              <Text size="xs" c={agentBubbleText} style={{ lineHeight: 1.5 }}>
                Of course! I'd be happy to help. Could you share your order number?
              </Text>
            </Box>
          </Group>
        </Box>

        {/* Input bar */}
        <Box
          style={{
            borderTop: `1px solid ${inputBarBorder}`,
            padding: '10px 12px',
            background: inputBarBg,
            flexShrink: 0,
          }}
        >
          <Group gap={8} wrap="nowrap">
            <Box
              style={{
                flex: 1,
                background: inputBg,
                borderRadius: config.borderRadius > 12 ? 20 : 8,
                padding: '8px 14px',
                fontSize: 12,
                color: inputText,
              }}
            >
              {config.inputPlaceholder || 'Type your message...'}
            </Box>
            <Box
              style={{
                width: 32,
                height: 32,
                borderRadius: '50%',
                background: config.primaryColor,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
                cursor: 'pointer',
              }}
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <line x1="22" y1="2" x2="11" y2="13" />
                <polygon points="22 2 15 22 11 13 2 9 22 2" />
              </svg>
            </Box>
          </Group>
          {/* Branding */}
          <Text size="xs" c={brandingText || 'dimmed'} ta="center" mt={6} style={{ fontSize: 10 }}>
            Powered by <span style={{ fontWeight: 600, color: config.primaryColor }}>Agent Red</span>
          </Text>
        </Box>
      </Box>

      {/* Launcher button — decorative in preview, no click handler */}
      <Box
        style={{
          position: 'absolute',
          bottom: Math.round(config.positionOffsetY * 0.5),
          [isRight ? 'right' : 'left']: Math.round(config.positionOffsetX * 0.5),
          width: config.launcherSize,
          height: config.launcherSize,
          borderRadius: '50%',
          background: config.primaryColor,
          boxShadow: '0 4px 16px rgba(0,0,0,0.2)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          cursor: 'default',
          zIndex: 3,
        }}
      >
        <LauncherIcon icon={config.launcherIcon} size={config.launcherSize} />
      </Box>
    </Box>
  );
}

// ---------------------------------------------------------------------------
// Avatar Drop Zone — compact image upload for agent avatar
// ---------------------------------------------------------------------------

const AVATAR_ACCEPTED_TYPES = '.png,.jpg,.jpeg';
const AVATAR_MAX_KB = 256;

interface AvatarDropZoneProps {
  onFileSelected: (file: File) => void;
  uploading: boolean;
  progress: 'idle' | 'uploading' | 'processing' | 'done';
  error: string | null;
}

function AvatarDropZone({ onFileSelected, uploading, progress, error }: AvatarDropZoneProps) {
  const inputRef = React.useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = React.useState(false);

  const handleDrop = React.useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      if (uploading) return;
      const file = e.dataTransfer.files?.[0];
      if (file) onFileSelected(file);
    },
    [onFileSelected, uploading],
  );

  const handleFileChange = React.useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) onFileSelected(file);
      if (inputRef.current) inputRef.current.value = '';
    },
    [onFileSelected],
  );

  const progressLabel =
    progress === 'uploading' ? 'Uploading...' : progress === 'processing' ? 'Processing...' : '';

  return (
    <div>
      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => !uploading && inputRef.current?.click()}
        style={{
          border: `2px dashed ${dragOver ? tokens.action : tokens.border}`,
          borderRadius: '8px',
          padding: '20px 16px',
          textAlign: 'center' as const,
          cursor: uploading ? 'default' : 'pointer',
          backgroundColor: dragOver ? 'rgba(59, 130, 246, 0.03)' : tokens.page,
          transition: 'all 0.2s ease',
          opacity: uploading ? 0.7 : 1,
        }}
      >
        <input
          ref={inputRef}
          type="file"
          accept={AVATAR_ACCEPTED_TYPES}
          onChange={handleFileChange}
          style={{ display: 'none' }}
        />
        {uploading ? (
          <Text size="sm" fw={500}>{progressLabel}</Text>
        ) : (
          <>
            <Text size="sm" fw={500}>Drop an image or click to browse</Text>
            <Text size="xs" c="dimmed" mt={2}>PNG or JPEG, max {AVATAR_MAX_KB} KB</Text>
          </>
        )}
      </div>
      {error && (
        <Text size="xs" c="red" mt={4}>{error}</Text>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Widget Page Component
// ---------------------------------------------------------------------------

export function WidgetPage() {
  const { apiFetch, onNotify, refreshActivationStatus } = useAppContext();
  const configResult = useConfig(apiFetch);
  const { updateConfig: saveConfig, loading: saving, error: saveError } = useUpdateConfig(apiFetch);
  const avatarUpload = useAvatarUpload(apiFetch);
  const avatarDelete = useDeleteAvatar(apiFetch);
  const { rotateWidgetKey, loading: rotating, error: rotateError } = useRotateWidgetKey(apiFetch);

  const computedColorScheme = useComputedColorScheme('dark');
  const adminIsDark = computedColorScheme === 'dark';

  const [config, setConfig] = useState<WidgetConfig>({ ...DEFAULT_WIDGET_CONFIG });
  const [initialized, setInitialized] = useState(false);
  const [previewQuickActions, setPreviewQuickActions] = useState<QuickActionPreview[]>([]);

  // Widget key installation state
  const [rotateModalOpen, setRotateModalOpen] = useState(false);
  const [newKey, setNewKey] = useState<string | null>(null);
  const widgetKey = (configResult.data?.config?.widget_key as string | undefined) || null;
  const displayKey = newKey || widgetKey;
  const apiBaseUrl = ((typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_URL) as string) || window.location.origin;
  const embedSnippet = displayKey
    ? `<script\n  src="${apiBaseUrl}/widget.js"\n  data-widget-key="${displayKey}"\n  data-api-url="${apiBaseUrl}"\n></script>`
    : '';

  // Populate form from API config when loaded
  useEffect(() => {
    if (configResult.data?.config && !initialized) {
      const apiValues = configToWidgetConfig(configResult.data.config);
      setConfig((prev) => ({ ...prev, ...apiValues }));
      setInitialized(true);
    }
  }, [configResult.data, initialized]);

  // Fetch quick actions for preview (WI-0797)
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

  // Dispatch draft config to the live widget on this page (SPEC-1551).
  // The widget exposes window.AgentRed.setConfigPartial() which reactively
  // updates the launcher and panel, giving merchants a real-time preview.
  useEffect(() => {
    if (!initialized) return;
    const sdk = (window as any).AgentRed;
    if (sdk?.setConfigPartial) {
      sdk.setConfigPartial(widgetConfigToApiFields(config));
    }
  }, [config, initialized]);

  function update<K extends keyof WidgetConfig>(key: K, value: WidgetConfig[K]) {
    setConfig((prev) => ({ ...prev, [key]: value }));
  }

  function resetDefaults() {
    setConfig({ ...DEFAULT_WIDGET_CONFIG });
  }

  async function handleSave() {
    const changes = widgetConfigToApiFields(config);
    const result = await saveConfig(changes);
    if (result?.success) {
      onNotify('Draft widget settings saved successfully.', 'success');
      refreshActivationStatus();
    } else {
      const detail = (result as any)?.error || saveError || 'Failed to save widget settings';
      onNotify(`Failed to save: ${detail}`, 'error');
    }
  }

  async function handleRotateWidgetKey() {
    const result = await rotateWidgetKey();
    if (result?.newWidgetKey) {
      setNewKey(result.newWidgetKey);
      configResult.refetch();
      onNotify('Widget key rotated. Update the embed code on your website.', 'success');
      refreshActivationStatus();
    }
    setRotateModalOpen(false);
  }

  return (
    <Stack gap="lg" pos="relative">
      <LoadingOverlay visible={configResult.loading && !initialized} />

      {/* Page header */}
      <div>
        <Title order={2}>Widget configuration</Title>
        <Text c="dimmed" size="sm">
          Customize how your chat widget looks and behaves
        </Text>
      </div>

      {/* Form sections — full width (live widget serves as preview) */}
      <Stack gap="md">
            {/* Installation Section — widget key + embed code */}
            <Paper p="lg" radius="md" withBorder>
              <SectionHeader
                tooltip="Your widget key authenticates the chat widget on your website. The embed code snippet goes in your site's HTML."
                docLink={`${DOCS_BASE}/widget-appearance`}
              >
                Installation
              </SectionHeader>
              <Divider mb="md" />
              <Stack gap="md">
                {/* Widget key display */}
                <div>
                  <Text size="sm" fw={500} mb={6}>Widget key</Text>
                  {displayKey ? (
                    <>
                      <Group gap="xs" align="flex-end">
                        <TextInput
                          value={displayKey}
                          readOnly
                          size="sm"
                          style={{ flex: 1 }}
                          styles={{ input: { fontFamily: 'monospace', fontSize: '12px' } }}
                        />
                        <CopyButton value={displayKey}>
                          {({ copied, copy }) => (
                            <Tooltip label={copied ? 'Copied' : 'Copy key'}>
                              <ActionIcon color={copied ? 'green' : 'action'} onClick={copy} variant="subtle" size="lg">
                                {copied ? '\u2713' : '\uD83D\uDCCB'}
                              </ActionIcon>
                            </Tooltip>
                          )}
                        </CopyButton>
                        <Button
                          color="red"
                          variant="outline"
                          size="sm"
                          onClick={() => { setNewKey(null); setRotateModalOpen(true); }}
                        >
                          Rotate key
                        </Button>
                      </Group>
                      {newKey && (
                        <Alert color="green" mt="sm" radius="md">
                          New widget key generated. Update the embed code on your website.
                        </Alert>
                      )}
                    </>
                  ) : (
                    <Alert color="yellow" radius="md">
                      No widget key found. Activate your configuration to generate one.
                    </Alert>
                  )}
                </div>

                {/* API URL display */}
                <div>
                  <Text size="sm" fw={500} mb={6}>API URL</Text>
                  <Group gap="xs" align="flex-end">
                    <TextInput
                      value={apiBaseUrl}
                      readOnly
                      size="sm"
                      style={{ flex: 1 }}
                      styles={{ input: { fontFamily: 'monospace', fontSize: '12px' } }}
                    />
                    <CopyButton value={apiBaseUrl}>
                      {({ copied, copy }) => (
                        <Tooltip label={copied ? 'Copied' : 'Copy URL'}>
                          <ActionIcon color={copied ? 'green' : 'action'} onClick={copy} variant="subtle" size="lg">
                            {copied ? '\u2713' : '\uD83D\uDCCB'}
                          </ActionIcon>
                        </Tooltip>
                      )}
                    </CopyButton>
                  </Group>
                  <Text size="xs" c="dimmed" mt={4}>
                    Shopify merchants: paste this URL into the Agent Red theme block settings.
                  </Text>
                </div>

                {/* Embed code snippet */}
                {displayKey && (
                  <div>
                    <Group justify="space-between" mb={6}>
                      <Text size="sm" fw={500}>Embed code</Text>
                      <CopyButton value={embedSnippet}>
                        {({ copied, copy }) => (
                          <Button
                            size="compact-xs"
                            variant="subtle"
                            color={copied ? 'green' : 'action'}
                            onClick={copy}
                          >
                            {copied ? 'Copied!' : 'Copy snippet'}
                          </Button>
                        )}
                      </CopyButton>
                    </Group>
                    <Text size="xs" c="dimmed" mb={8}>
                      Paste this snippet before the closing &lt;/body&gt; tag on every page where you want the chat widget.
                    </Text>
                    <Code block style={{ fontSize: 12 }}>
                      {embedSnippet}
                    </Code>
                  </div>
                )}
              </Stack>
            </Paper>

            {/* Appearance Section */}
            <Paper p="lg" radius="md" withBorder>
              <SectionHeader tooltip="Colors, position, size, and visual style of the chat widget on your storefront." docLink={`${DOCS_BASE}/widget-appearance`}>Appearance</SectionHeader>
              <Divider mb="md" />
              <Stack gap="sm">
                {/* Header color pickers — side-by-side (WI #271) */}
                <Group grow align="flex-start" gap="md">
                  <ColorField
                    label="Header left color"
                    value={config.primaryColor}
                    onChange={(val) => update('primaryColor', val)}
                    swatches={[BRAND_RED, '#2563EB', '#059669', '#7C3AED', '#D97706', '#DB2777', '#000000', '#FFFFFF']}
                  />
                  <div style={{ opacity: config.headerGradientEnabled ? 1 : 0.4, pointerEvents: config.headerGradientEnabled ? 'auto' : 'none' }}>
                    <ColorField
                      label="Header right color"
                      value={config.headerGradientEnd}
                      onChange={(val) => update('headerGradientEnd', val)}
                      swatches={['#8B1520', '#1E40AF', '#047857', '#5B21B6', '#B45309', '#BE185D', '#1F2937', '#374151']}
                    />
                  </div>
                </Group>
                {/* Gradient toggle (WI #270) */}
                <Switch
                  label="Enable header gradient"
                  description="When off, the header uses a solid color. When on, it blends left and right colors."
                  checked={config.headerGradientEnabled}
                  onChange={(e) => update('headerGradientEnabled', e.currentTarget.checked)}
                  color="action"
                />
                <Select
                  label="Font family"
                  data={FONT_OPTIONS}
                  value={config.fontFamily}
                  onChange={(val) => update('fontFamily', val || DEFAULT_WIDGET_CONFIG.fontFamily)}
                />
                <div>
                  <Text size="sm" fw={500} mb={4}>
                    Border radius ({config.borderRadius}px)
                  </Text>
                  <Slider
                    min={0}
                    max={24}
                    step={1}
                    value={config.borderRadius}
                    onChange={(val) => update('borderRadius', val)}
                    color="action"
                    marks={[
                      { value: 0, label: '0' },
                      { value: 8, label: '8' },
                      { value: 16, label: '16' },
                      { value: 24, label: '24' },
                    ]}
                  />
                </div>
                <div style={{ marginTop: 8 }}>
                  <Text size="sm" fw={500} mb={4}>
                    Launcher size ({config.launcherSize}px)
                  </Text>
                  <Slider
                    min={48}
                    max={72}
                    step={1}
                    value={config.launcherSize}
                    onChange={(val) => update('launcherSize', val)}
                    color="action"
                    marks={[
                      { value: 48, label: '48' },
                      { value: 60, label: '60' },
                      { value: 72, label: '72' },
                    ]}
                  />
                </div>
                <Select
                  label="Launcher icon"
                  data={ICON_OPTIONS}
                  value={config.launcherIcon}
                  onChange={(val) => update('launcherIcon', (val as WidgetConfig['launcherIcon']) || 'chat')}
                  mt={8}
                />
                <div>
                  <Text size="sm" fw={500} mb={6}>
                    Position
                  </Text>
                  <SegmentedControl
                    fullWidth
                    value={config.position}
                    onChange={(val) => update('position', val as WidgetConfig['position'])}
                    data={[
                      { label: 'Bottom right', value: 'bottom-right' },
                      { label: 'Bottom left', value: 'bottom-left' },
                    ]}
                    color="action"
                  />
                  <Group grow mt={8}>
                    <NumberInput
                      label="Horizontal offset"
                      description="Distance from edge (px)"
                      size="xs"
                      min={0}
                      max={200}
                      step={4}
                      suffix=" px"
                      value={config.positionOffsetX}
                      onChange={(val) => update('positionOffsetX', typeof val === 'number' ? val : 20)}
                    />
                    <NumberInput
                      label="Vertical offset"
                      description="Distance from bottom (px)"
                      size="xs"
                      min={0}
                      max={200}
                      step={4}
                      suffix=" px"
                      value={config.positionOffsetY}
                      onChange={(val) => update('positionOffsetY', typeof val === 'number' ? val : 20)}
                    />
                  </Group>
                </div>
                <div>
                  <Text size="sm" fw={500} mb={6}>
                    Color mode
                  </Text>
                  <SegmentedControl
                    fullWidth
                    value={config.colorMode}
                    onChange={(val) => update('colorMode', val as WidgetConfig['colorMode'])}
                    data={[
                      { label: 'Light', value: 'light' },
                      { label: 'Dark', value: 'dark' },
                      { label: 'Auto', value: 'auto' },
                    ]}
                    color="action"
                  />
                </div>
                <div>
                  <Text size="sm" fw={500} mb={6}>
                    Panel width <HelpTooltip text="Set the chat panel width. Compact (320px) works well on smaller screens; Wide (440px) shows more content." docLink="https://agentredcx.com/docs/admin-guide/widget-appearance" />
                  </Text>
                  <SegmentedControl
                    fullWidth
                    value={config.panelWidth}
                    onChange={(val) => update('panelWidth', val as WidgetConfig['panelWidth'])}
                    data={[
                      { label: 'Compact', value: 'compact' },
                      { label: 'Standard', value: 'standard' },
                      { label: 'Wide', value: 'wide' },
                    ]}
                    color="action"
                  />
                </div>
                <div>
                  <Text size="sm" fw={500} mb={6}>
                    Panel height <HelpTooltip text="Set the chat panel height. Short (420px) saves screen space; Tall (620px) shows more conversation." docLink="https://agentredcx.com/docs/admin-guide/widget-appearance" />
                  </Text>
                  <SegmentedControl
                    fullWidth
                    value={config.panelHeight}
                    onChange={(val) => update('panelHeight', val as WidgetConfig['panelHeight'])}
                    data={[
                      { label: 'Short', value: 'short' },
                      { label: 'Standard', value: 'standard' },
                      { label: 'Tall', value: 'tall' },
                    ]}
                    color="action"
                  />
                </div>
                <div>
                  <Text size="sm" fw={500} mb={6}>
                    Widget language <HelpTooltip text="Language for all widget UI text. Auto detects the visitor's browser language with English fallback." docLink="https://agentredcx.com/docs/admin-guide/widget-appearance" />
                  </Text>
                  <Select
                    value={config.locale}
                    onChange={(val) => update('locale', (val || 'auto') as WidgetConfig['locale'])}
                    data={[
                      { label: 'Auto-detect', value: 'auto' },
                      { label: 'English', value: 'en' },
                      { label: 'Espa\u00f1ol', value: 'es' },
                      { label: 'Fran\u00e7ais', value: 'fr' },
                      { label: 'Deutsch', value: 'de' },
                      { label: 'Portugu\u00eas', value: 'pt' },
                      { label: '\u65e5\u672c\u8a9e', value: 'ja' },
                      { label: '\u4e2d\u6587', value: 'zh' },
                      { label: '\ud55c\uad6d\uc5b4', value: 'ko' },
                    ]}
                  />
                </div>
                <div>
                  <Text size="sm" fw={500} mb={6}>
                    Panel shadow
                  </Text>
                  <SegmentedControl
                    fullWidth
                    value={config.shadowIntensity}
                    onChange={(val) => update('shadowIntensity', val as WidgetConfig['shadowIntensity'])}
                    data={[
                      { label: 'None', value: 'none' },
                      { label: 'Subtle', value: 'subtle' },
                      { label: 'Standard', value: 'standard' },
                      { label: 'Heavy', value: 'heavy' },
                    ]}
                    color="action"
                  />
                </div>
              </Stack>
            </Paper>

            {/* Behavior Section */}
            <Paper p="lg" radius="md" withBorder>
              <SectionHeader tooltip="Auto-open timing, sound notifications, pre-chat form fields, and idle timeout." docLink={`${DOCS_BASE}/widget-behavior`}>Behavior</SectionHeader>
              <Divider mb="md" />
              <Stack gap="sm">
                <Switch
                  label="Greeting message"
                  checked={config.greetingEnabled}
                  onChange={(e) => update('greetingEnabled', e.currentTarget.checked)}
                  color="action"
                />
                {config.greetingEnabled && (
                  <SegmentedControl
                    data={[
                      { label: 'Static', value: 'static' },
                      { label: 'AI-generated', value: 'ai_generated' },
                    ]}
                    value={config.greetingMode}
                    onChange={(val) => update('greetingMode', val as WidgetConfig['greetingMode'])}
                    size="xs"
                  />
                )}
                {config.greetingMode === 'static' ? (
                  <div>
                    <Textarea
                      label={<>Greeting message <HelpTooltip text="This is a static welcome message, not generated by the AI. It is displayed exactly as written when a visitor opens the chat." docLink="https://agentredcx.com/docs/admin-guide/widget-behavior" /></>}
                      value={config.greetingMessage}
                      onChange={(e) => update('greetingMessage', e.currentTarget.value)}
                      disabled={!config.greetingEnabled}
                      autosize
                      minRows={2}
                      maxRows={4}
                      description="Personalize with template variables — click to insert."
                    />
                    {config.greetingEnabled && (
                      <Group gap={6} mt={6} wrap="wrap">
                        {GREETING_VARIABLES.map((v) => (
                          <Button
                            key={v.token}
                            size="compact-xs"
                            variant="light"
                            color="gray"
                            style={{ fontSize: 11, fontFamily: "'JetBrains Mono', monospace" }}
                            title={v.label}
                            onClick={() => {
                              const cur = config.greetingMessage;
                              const trimmed = cur.trimEnd();
                              const trailing = cur.slice(trimmed.length);
                              const needsSpace = trimmed.length > 0 && !trimmed.endsWith(' ');
                              update('greetingMessage', trimmed + (needsSpace ? ' ' : '') + v.token + trailing);
                            }}
                          >
                            {v.token}
                          </Button>
                        ))}
                      </Group>
                    )}
                  </div>
                ) : (
                  <Text size="sm" c="dimmed">
                    The AI will generate a unique, context-aware greeting for each visitor based on your brand persona, the current page, and time of day. No static message is needed.
                  </Text>
                )}
                <Divider variant="dashed" />
                <Switch
                  label={<>Pre-chat form <HelpTooltip text="Collects optional identity information from the visitor before starting a conversation. This is not a security feature — responses are self-reported, unverified, and should not be trusted for authentication. A single Shopify customer account may be shared by multiple people. If distinguishing individual users matters for your business, ask visitors to identify themselves explicitly." docLink="https://agentredcx.com/docs/admin-guide/widget-behavior#pre-chat-form" /></>}
                  description="Collect visitor name and email before starting a conversation."
                  checked={config.preChatFormEnabled}
                  onChange={(e) => update('preChatFormEnabled', e.currentTarget.checked)}
                  color="action"
                />
                {config.preChatFormEnabled && (
                  <div>
                    <Text size="sm" fw={500} mb={6}>
                      Pre-chat fields
                    </Text>
                    <Chip.Group
                      multiple
                      value={config.preChatFields}
                      onChange={(val) => update('preChatFields', val)}
                    >
                      <Group gap="xs">
                        {PRE_CHAT_FIELDS.map((field) => (
                          <Chip key={field} value={field} color="action" variant="outline">
                            {field.charAt(0).toUpperCase() + field.slice(1)}
                          </Chip>
                        ))}
                      </Group>
                    </Chip.Group>
                  </div>
                )}
                <Switch
                  label="Sound notifications"
                  checked={config.soundEnabled}
                  onChange={(e) => update('soundEnabled', e.currentTarget.checked)}
                  color="action"
                />
                <Divider variant="dashed" />
                <Switch
                  label={<>Exit-intent auto-open <HelpTooltip text="Automatically opens the widget when a desktop visitor moves their mouse out of the browser window. Fires at most once per page visit and only if the visitor hasn't already closed the widget." /></>}
                  description="Desktop only — triggers when the mouse leaves the viewport."
                  checked={config.exitIntentEnabled}
                  onChange={(e) => update('exitIntentEnabled', e.currentTarget.checked)}
                  color="action"
                />
                <NumberInput
                  label={<>Scroll-depth auto-open (%) <HelpTooltip text="Automatically opens the widget when the visitor scrolls past this percentage of the page. Fires at most once per page visit and only if the visitor hasn't already closed the widget. Leave empty to disable." /></>}
                  description="Opens the widget when the visitor scrolls past this % of the page."
                  size="xs"
                  min={1}
                  max={100}
                  step={5}
                  suffix="%"
                  placeholder="Disabled"
                  value={config.scrollDepthTrigger ?? ''}
                  onChange={(val) => update('scrollDepthTrigger', typeof val === 'number' ? val : null)}
                />
                <Divider variant="dashed" />
                <Switch
                  label="Mobile fullscreen"
                  description="Chat panel fills the entire screen on mobile devices"
                  checked={config.mobileFullscreen}
                  onChange={(e) => update('mobileFullscreen', e.currentTarget.checked)}
                  color="action"
                />
                <Select
                  label="Mobile position override"
                  description="Override the desktop position for mobile devices. Leave empty to inherit."
                  data={[
                    { value: '', label: 'Inherit from desktop' },
                    { value: 'bottom-right', label: 'Bottom right' },
                    { value: 'bottom-left', label: 'Bottom left' },
                  ]}
                  value={config.mobilePosition || ''}
                  onChange={(val) => update('mobilePosition', val ? (val as WidgetConfig['mobilePosition']) : null)}
                  clearable
                />
                <Group grow>
                  <NumberInput
                    label="Mobile horizontal offset"
                    description="Override for mobile (px)"
                    size="xs"
                    min={0}
                    max={100}
                    step={4}
                    suffix=" px"
                    placeholder="Inherit"
                    value={config.mobileOffsetX ?? ''}
                    onChange={(val) => update('mobileOffsetX', typeof val === 'number' ? val : null)}
                  />
                  <NumberInput
                    label="Mobile vertical offset"
                    description="Override for mobile (px)"
                    size="xs"
                    min={0}
                    max={100}
                    step={4}
                    suffix=" px"
                    placeholder="Inherit"
                    value={config.mobileOffsetY ?? ''}
                    onChange={(val) => update('mobileOffsetY', typeof val === 'number' ? val : null)}
                  />
                </Group>
                <Divider variant="dashed" />
                <Text size="sm" fw={500} mb={2}>
                  Page visibility rules <HelpTooltip text="Control which pages show the widget. Use + prefix to include, - prefix to exclude. Glob patterns (* and ?) are supported. Exclude rules take precedence over include rules." />
                </Text>
                {config.pageRules.length === 0 ? (
                  <Text size="xs" c="dimmed" fs="italic">
                    No page rules configured. The widget will appear on all pages.
                  </Text>
                ) : (
                  <Stack gap={6}>
                    {config.pageRules.map((rule, idx) => (
                      <Group key={idx} gap="xs" wrap="nowrap">
                        <TextInput
                          style={{ flex: 1 }}
                          size="xs"
                          value={rule}
                          placeholder="+/products/* or -/checkout"
                          onChange={(e) => {
                            const updated = [...config.pageRules];
                            updated[idx] = e.currentTarget.value;
                            update('pageRules', updated);
                          }}
                        />
                        <ActionIcon
                          size="sm"
                          variant="subtle"
                          color="red"
                          onClick={() => {
                            const updated = config.pageRules.filter((_, i) => i !== idx);
                            update('pageRules', updated);
                          }}
                        >
                          <svg width={14} height={14} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                        </ActionIcon>
                      </Group>
                    ))}
                  </Stack>
                )}
                <Button
                  size="compact-xs"
                  variant="light"
                  color="gray"
                  disabled={config.pageRules.length >= 20}
                  onClick={() => update('pageRules', [...config.pageRules, ''])}
                >
                  + Add rule
                </Button>
              </Stack>
            </Paper>

            {/* Content Section */}
            <Paper p="lg" radius="md" withBorder>
              <SectionHeader tooltip="Header text, greeting message, agent identity, and placeholder text shown in the widget." docLink={`${DOCS_BASE}/widget-appearance`}>Content</SectionHeader>
              <Divider mb="md" />
              <Stack gap="sm">
                <TextInput
                  label="Header title"
                  value={config.headerTitle}
                  onChange={(e) => update('headerTitle', e.currentTarget.value)}
                  placeholder="Support"
                />
                <TextInput
                  label="Header subtitle"
                  value={config.headerSubtitle}
                  onChange={(e) => update('headerSubtitle', e.currentTarget.value)}
                  placeholder="We typically reply within minutes"
                />
                <TextInput
                  label="Input placeholder"
                  value={config.inputPlaceholder}
                  onChange={(e) => update('inputPlaceholder', e.currentTarget.value)}
                  placeholder="Type your message..."
                />
                <Divider label="Agent identity" labelPosition="left" my={4} />
                <TextInput
                  label="Agent display name"
                  description="Name shown in chat header and greeting. Leave empty for default."
                  value={config.agentDisplayName}
                  onChange={(e) => update('agentDisplayName', e.currentTarget.value)}
                  placeholder="Agent Red"
                />
                <Text size="sm" fw={500}>Agent avatar</Text>
                <Text size="xs" c="dimmed" mb={4}>
                  Upload a PNG or JPEG image (max 256 KB). Leave empty for initials fallback.
                </Text>
                {config.agentAvatarUrl ? (
                  <Group gap="sm" align="center">
                    <div style={{
                      width: 48,
                      height: 48,
                      borderRadius: '50%',
                      overflow: 'hidden',
                      border: `1px solid ${tokens.border}`,
                      flexShrink: 0,
                    }}>
                      <img
                        src={config.agentAvatarUrl}
                        alt="Avatar preview"
                        style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                        onError={(e) => { (e.currentTarget as HTMLImageElement).style.display = 'none'; }}
                      />
                    </div>
                    <Stack gap={4}>
                      <Text size="xs" c="dimmed">Current avatar</Text>
                      <Button
                        size="compact-xs"
                        variant="subtle"
                        color="red"
                        loading={avatarDelete.loading}
                        onClick={async () => {
                          const result = await avatarDelete.deleteAvatar();
                          if (result?.success) {
                            update('agentAvatarUrl', '');
                            avatarUpload.reset();
                            onNotify('Avatar removed.', 'success');
                          } else {
                            onNotify(avatarDelete.error || 'Failed to remove avatar.', 'error');
                          }
                        }}
                      >
                        Remove avatar
                      </Button>
                    </Stack>
                  </Group>
                ) : (
                  <AvatarDropZone
                    uploading={avatarUpload.loading}
                    progress={avatarUpload.progress}
                    error={avatarUpload.error}
                    onFileSelected={async (file: File) => {
                      const result = await avatarUpload.upload(file);
                      if (result?.success && result.avatar_url) {
                        update('agentAvatarUrl', result.avatar_url);
                        onNotify('Avatar uploaded.', 'success');
                      } else {
                        onNotify(avatarUpload.error || 'Upload failed.', 'error');
                      }
                    }}
                  />
                )}
              </Stack>
            </Paper>

            {/* Action buttons */}
            <Group justify="flex-end" gap="sm">
              <Button variant="default" onClick={resetDefaults}>
                Reset to defaults
              </Button>
              <Button color="action" onClick={handleSave} loading={saving}>
                Save draft inputs
              </Button>
            </Group>
      </Stack>

      {/* Widget key rotation confirmation modal */}
      <Modal
        opened={rotateModalOpen}
        onClose={() => setRotateModalOpen(false)}
        title="Rotate widget key"
        centered
        size="sm"
      >
        <Stack gap="md">
          <Alert color="red" variant="light" radius="md">
            Rotating the widget key will <strong>immediately invalidate</strong> the current key.
            Any website using the old key will stop working until the embed code is updated.
          </Alert>
          <Text size="sm">Are you sure you want to rotate the widget key?</Text>
          {rotateError && (
            <Alert color="red" variant="light" radius="md">
              {rotateError}
            </Alert>
          )}
          <Group justify="flex-end" gap="sm">
            <Button variant="default" onClick={() => setRotateModalOpen(false)}>
              Cancel
            </Button>
            <Button color="red" onClick={handleRotateWidgetKey} loading={rotating}>
              Rotate key
            </Button>
          </Group>
        </Stack>
      </Modal>
    </Stack>
  );
}

export default WidgetPage;
