// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

import React, { useState } from 'react';
import {
  Paper,
  ColorInput,
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
} from '@mantine/core';
import { DEFAULT_WIDGET_CONFIG, WidgetConfig } from '../../data/mockData';

const BRAND_RED = '#C41E2A';

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
  { value: 'custom', label: 'Custom' },
];

const PRE_CHAT_FIELDS = ['name', 'email', 'phone', 'company'];

function SectionHeader({ children }: { children: React.ReactNode }) {
  return (
    <Text size="sm" fw={700} tt="uppercase" c="dimmed" mb={4}>
      {children}
    </Text>
  );
}

// --- Launcher icon SVGs for the preview ---
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

// --- Live Preview Component ---
function WidgetPreview({ config }: { config: WidgetConfig }) {
  const isRight = config.position === 'bottom-right';
  const dk = config.colorMode === 'dark';

  // Color tokens — light vs dark widget mode (Mazel design revision 2026-02-03 mockup)
  const panelBg = dk ? '#1f1f1f' : '#fff';
  const msgAreaBg = dk ? '#141414' : '#fafafa';
  const agentBubbleBg = dk ? '#1f1f1f' : '#fff';
  const agentBubbleBorder = dk ? '#272727' : '#e9ecef';
  const agentBubbleText = dk ? '#E0E0E0' : undefined;
  const dateSepBg = dk ? '#1f1f1f' : '#f1f3f5';
  const dateSepText = dk ? '#787878' : undefined;
  const inputBg = dk ? '#1f1f1f' : '#f1f3f5';
  const inputText = dk ? '#5C5C5C' : '#adb5bd';
  const inputBarBg = dk ? '#0a0a0a' : '#fff';
  const inputBarBorder = dk ? '#272727' : '#e9ecef';
  const brandingText = dk ? '#5C5C5C' : undefined;
  const pageBg = dk ? '#141414' : '#f8f9fa';
  const pageBorder = dk ? '#272727' : '#dee2e6';
  // Simulated page chrome
  const chromeBg = dk ? '#0a0a0a' : '#e9ecef';
  const chromeBorder = dk ? '#272727' : '#dee2e6';
  const skeletonDark = dk ? '#1f1f1f' : '#dee2e6';
  const skeletonLight = dk ? '#0a0a0a' : '#e9ecef';

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

      {/* Chat panel */}
      <Box
        style={{
          position: 'absolute',
          bottom: 80,
          [isRight ? 'right' : 'left']: 16,
          width: 350,
          height: 440,
          borderRadius: config.borderRadius,
          boxShadow: dk ? '0 8px 32px rgba(0,0,0,0.4)' : '0 8px 32px rgba(0,0,0,0.18)',
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
            background: `linear-gradient(135deg, ${config.primaryColor} 0%, ${config.headerGradientEnd} 100%)`,
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
              }}
            >
              AR
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
          {config.greetingEnabled && config.greetingMessage && (
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
                  {config.greetingMessage}
                </Text>
              </Box>
            </Group>
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

      {/* Launcher button */}
      <Box
        style={{
          position: 'absolute',
          bottom: 20,
          [isRight ? 'right' : 'left']: 20,
          width: config.launcherSize,
          height: config.launcherSize,
          borderRadius: '50%',
          background: config.primaryColor,
          boxShadow: '0 4px 16px rgba(0,0,0,0.2)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          cursor: 'pointer',
          zIndex: 3,
          transition: 'transform 0.15s ease',
        }}
      >
        <LauncherIcon icon={config.launcherIcon} size={config.launcherSize} />
      </Box>
    </Box>
  );
}

export function WidgetConfigPage() {
  const [config, setConfig] = useState<WidgetConfig>({ ...DEFAULT_WIDGET_CONFIG });

  function update<K extends keyof WidgetConfig>(key: K, value: WidgetConfig[K]) {
    setConfig((prev) => ({ ...prev, [key]: value }));
  }

  function resetDefaults() {
    setConfig({ ...DEFAULT_WIDGET_CONFIG });
  }

  return (
    <Stack gap="lg">
      {/* Page header */}
      <div>
        <Title order={2}>Widget Configurator</Title>
        <Text c="dimmed" size="sm">
          Customize how your chat widget looks and behaves
        </Text>
      </div>

      {/* Two-column layout: 55% form / 45% preview */}
      <Group align="flex-start" wrap="nowrap" gap="lg" style={{ minHeight: 600 }}>
        {/* Left column - Form controls */}
        <Box style={{ flex: '0 0 55%', maxWidth: '55%' }}>
          <Stack gap="md">
            {/* Appearance Section */}
            <Paper p="lg" radius="md" withBorder>
              <SectionHeader>Appearance</SectionHeader>
              <Divider mb="md" />
              <Stack gap="sm">
                <ColorInput
                  label="Primary Color"
                  value={config.primaryColor}
                  onChange={(val) => update('primaryColor', val)}
                  format="hex"
                  swatches={['#C41E2A', '#2563EB', '#059669', '#7C3AED', '#D97706', '#DB2777', '#000000']}
                />
                <ColorInput
                  label="Header Gradient End"
                  value={config.headerGradientEnd}
                  onChange={(val) => update('headerGradientEnd', val)}
                  format="hex"
                  swatches={['#8B1520', '#1E40AF', '#047857', '#5B21B6', '#B45309', '#BE185D', '#1F2937']}
                />
                <Select
                  label="Font Family"
                  data={FONT_OPTIONS}
                  value={config.fontFamily}
                  onChange={(val) => update('fontFamily', val || DEFAULT_WIDGET_CONFIG.fontFamily)}
                />
                <div>
                  <Text size="sm" fw={500} mb={4}>
                    Border Radius ({config.borderRadius}px)
                  </Text>
                  <Slider
                    min={0}
                    max={24}
                    step={1}
                    value={config.borderRadius}
                    onChange={(val) => update('borderRadius', val)}
                    color="brand"
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
                    Launcher Size ({config.launcherSize}px)
                  </Text>
                  <Slider
                    min={48}
                    max={72}
                    step={1}
                    value={config.launcherSize}
                    onChange={(val) => update('launcherSize', val)}
                    color="brand"
                    marks={[
                      { value: 48, label: '48' },
                      { value: 60, label: '60' },
                      { value: 72, label: '72' },
                    ]}
                  />
                </div>
                <Select
                  label="Launcher Icon"
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
                      { label: 'Bottom Right', value: 'bottom-right' },
                      { label: 'Bottom Left', value: 'bottom-left' },
                    ]}
                    color="brand"
                  />
                </div>
                <div>
                  <Text size="sm" fw={500} mb={6}>
                    Color Mode
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
                    color="brand"
                  />
                </div>
              </Stack>
            </Paper>

            {/* Behavior Section */}
            <Paper p="lg" radius="md" withBorder>
              <SectionHeader>Behavior</SectionHeader>
              <Divider mb="md" />
              <Stack gap="sm">
                <Switch
                  label="Auto-open widget"
                  checked={config.autoOpen}
                  onChange={(e) => update('autoOpen', e.currentTarget.checked)}
                  color="brand"
                />
                <NumberInput
                  label="Auto-open Delay (seconds)"
                  value={config.autoOpenDelay}
                  onChange={(val) => update('autoOpenDelay', typeof val === 'number' ? val : 5)}
                  min={1}
                  max={60}
                  disabled={!config.autoOpen}
                />
                <Divider variant="dashed" />
                <Switch
                  label="Greeting message"
                  checked={config.greetingEnabled}
                  onChange={(e) => update('greetingEnabled', e.currentTarget.checked)}
                  color="brand"
                />
                <Textarea
                  label="Greeting Message"
                  value={config.greetingMessage}
                  onChange={(e) => update('greetingMessage', e.currentTarget.value)}
                  disabled={!config.greetingEnabled}
                  autosize
                  minRows={2}
                  maxRows={4}
                />
                <Divider variant="dashed" />
                <Switch
                  label="Pre-chat form"
                  checked={config.preChatFormEnabled}
                  onChange={(e) => update('preChatFormEnabled', e.currentTarget.checked)}
                  color="brand"
                />
                {config.preChatFormEnabled && (
                  <div>
                    <Text size="sm" fw={500} mb={6}>
                      Pre-chat Fields
                    </Text>
                    <Chip.Group
                      multiple
                      value={config.preChatFields}
                      onChange={(val) => update('preChatFields', val)}
                    >
                      <Group gap="xs">
                        {PRE_CHAT_FIELDS.map((field) => (
                          <Chip key={field} value={field} color="brand" variant="outline">
                            {field.charAt(0).toUpperCase() + field.slice(1)}
                          </Chip>
                        ))}
                      </Group>
                    </Chip.Group>
                  </div>
                )}
                <Switch
                  label="Offline form"
                  checked={config.offlineFormEnabled}
                  onChange={(e) => update('offlineFormEnabled', e.currentTarget.checked)}
                  color="brand"
                />
                <Switch
                  label="Sound notifications"
                  checked={config.soundEnabled}
                  onChange={(e) => update('soundEnabled', e.currentTarget.checked)}
                  color="brand"
                />
              </Stack>
            </Paper>

            {/* Content Section */}
            <Paper p="lg" radius="md" withBorder>
              <SectionHeader>Content</SectionHeader>
              <Divider mb="md" />
              <Stack gap="sm">
                <TextInput
                  label="Header Title"
                  value={config.headerTitle}
                  onChange={(e) => update('headerTitle', e.currentTarget.value)}
                  placeholder="Support"
                />
                <TextInput
                  label="Header Subtitle"
                  value={config.headerSubtitle}
                  onChange={(e) => update('headerSubtitle', e.currentTarget.value)}
                  placeholder="We typically reply within minutes"
                />
                <TextInput
                  label="Input Placeholder"
                  value={config.inputPlaceholder}
                  onChange={(e) => update('inputPlaceholder', e.currentTarget.value)}
                  placeholder="Type your message..."
                />
              </Stack>
            </Paper>

            {/* Action buttons */}
            <Group justify="flex-end" gap="sm">
              <Button variant="default" onClick={resetDefaults}>
                Reset to Defaults
              </Button>
              <Button color="brand">
                Save Changes
              </Button>
            </Group>
          </Stack>
        </Box>

        {/* Right column - Live Preview */}
        <Box style={{ flex: '0 0 calc(45% - 16px)', position: 'sticky', top: 16 }}>
          <Paper p="md" radius="md" withBorder>
            <Text size="sm" fw={600} mb="sm">
              Live Preview
            </Text>
            <WidgetPreview config={config} />
          </Paper>
        </Box>
      </Group>
    </Stack>
  );
}
