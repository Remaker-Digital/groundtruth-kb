// (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

import React, { useState } from 'react';
import {
  Page,
  Layout,
  LegacyCard,
  TextField,
  Select,
  RangeSlider,
  Checkbox,
  Text,
  Box,
  InlineStack,
  BlockStack,
  Divider,
} from '@shopify/polaris';
import { DEFAULT_WIDGET_CONFIG } from '../../data/mockData';

export function ShopifyWidget() {
  // Appearance
  const [primaryColor, setPrimaryColor] = useState(DEFAULT_WIDGET_CONFIG.primaryColor);
  const [fontFamily, setFontFamily] = useState(DEFAULT_WIDGET_CONFIG.fontFamily);
  const [borderRadius, setBorderRadius] = useState(DEFAULT_WIDGET_CONFIG.borderRadius);
  const [launcherSize, setLauncherSize] = useState(DEFAULT_WIDGET_CONFIG.launcherSize);
  const [position, setPosition] = useState(DEFAULT_WIDGET_CONFIG.position);

  // Behavior
  const [autoOpen, setAutoOpen] = useState(DEFAULT_WIDGET_CONFIG.autoOpen);
  const [autoOpenDelay, setAutoOpenDelay] = useState(String(DEFAULT_WIDGET_CONFIG.autoOpenDelay));
  const [greetingEnabled, setGreetingEnabled] = useState(DEFAULT_WIDGET_CONFIG.greetingEnabled);
  const [greetingMessage, setGreetingMessage] = useState(DEFAULT_WIDGET_CONFIG.greetingMessage);
  const [preChatFormEnabled, setPreChatFormEnabled] = useState(DEFAULT_WIDGET_CONFIG.preChatFormEnabled);
  const [offlineFormEnabled, setOfflineFormEnabled] = useState(DEFAULT_WIDGET_CONFIG.offlineFormEnabled);
  const [soundEnabled, setSoundEnabled] = useState(DEFAULT_WIDGET_CONFIG.soundEnabled);

  // Content
  const [headerTitle, setHeaderTitle] = useState(DEFAULT_WIDGET_CONFIG.headerTitle);
  const [headerSubtitle, setHeaderSubtitle] = useState(DEFAULT_WIDGET_CONFIG.headerSubtitle);
  const [inputPlaceholder, setInputPlaceholder] = useState(DEFAULT_WIDGET_CONFIG.inputPlaceholder);

  const fontOptions = [
    { label: 'Inter (Default)', value: 'Inter, system-ui, sans-serif' },
    { label: 'System UI', value: 'system-ui, -apple-system, sans-serif' },
    { label: 'Roboto', value: 'Roboto, sans-serif' },
    { label: 'Open Sans', value: '"Open Sans", sans-serif' },
    { label: 'Lato', value: 'Lato, sans-serif' },
  ];

  const positionOptions = [
    { label: 'Bottom Right', value: 'bottom-right' },
    { label: 'Bottom Left', value: 'bottom-left' },
  ];

  // Derive a darker shade for the gradient end
  function darkenColor(hex: string, factor: number): string {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    const dr = Math.round(r * (1 - factor));
    const dg = Math.round(g * (1 - factor));
    const db = Math.round(b * (1 - factor));
    return `#${dr.toString(16).padStart(2, '0')}${dg.toString(16).padStart(2, '0')}${db.toString(16).padStart(2, '0')}`;
  }

  // Compute contrasting text color (white or dark) for the header
  function textColorForBg(hex: string): string {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
    return luminance > 0.5 ? '#202223' : '#ffffff';
  }

  const gradientEnd = darkenColor(primaryColor, 0.35);
  const headerTextColor = textColorForBg(primaryColor);

  return (
    <Page title="Widget Customization">
      <Layout>
        {/* Left column: Form controls */}
        <Layout.Section>
          {/* Appearance */}
          <LegacyCard title="Appearance" sectioned>
            <BlockStack gap="400">
              <InlineStack gap="400" wrap={true} blockAlign="end">
                <div style={{ flex: '1 1 45%', minWidth: 200 }}>
                  <TextField
                    label="Primary Color"
                    type="text"
                    value={primaryColor}
                    onChange={setPrimaryColor}
                    autoComplete="off"
                    connectedRight={
                      <TextField
                        label=""
                        labelHidden
                        value={primaryColor}
                        onChange={setPrimaryColor}
                        autoComplete="off"
                        monospaced
                      />
                    }
                  />
                </div>
                <div style={{ flex: '1 1 45%', minWidth: 200 }}>
                  <Select
                    label="Font Family"
                    options={fontOptions}
                    value={fontFamily}
                    onChange={setFontFamily}
                  />
                </div>
              </InlineStack>
              <RangeSlider
                label={`Border Radius: ${borderRadius}px`}
                value={borderRadius}
                onChange={(value) => setBorderRadius(value as number)}
                min={0}
                max={32}
                step={2}
                output
              />
              <RangeSlider
                label={`Launcher Size: ${launcherSize}px`}
                value={launcherSize}
                onChange={(value) => setLauncherSize(value as number)}
                min={40}
                max={80}
                step={4}
                output
              />
              <Select
                label="Position"
                options={positionOptions}
                value={position}
                onChange={(v) => setPosition(v as any)}
              />
            </BlockStack>
          </LegacyCard>

          {/* Behavior */}
          <LegacyCard title="Behavior" sectioned>
            <BlockStack gap="300">
              <Checkbox
                label="Auto-open widget for new visitors"
                checked={autoOpen}
                onChange={setAutoOpen}
              />
              {autoOpen && (
                <Box paddingInlineStart="800">
                  <TextField
                    label="Auto-open delay"
                    type="number"
                    value={autoOpenDelay}
                    onChange={setAutoOpenDelay}
                    suffix="seconds"
                    autoComplete="off"
                  />
                </Box>
              )}
              <Checkbox
                label="Show greeting message"
                checked={greetingEnabled}
                onChange={setGreetingEnabled}
              />
              {greetingEnabled && (
                <Box paddingInlineStart="800">
                  <TextField
                    label="Greeting message"
                    value={greetingMessage}
                    onChange={setGreetingMessage}
                    autoComplete="off"
                  />
                </Box>
              )}
              <Checkbox
                label="Enable pre-chat form"
                checked={preChatFormEnabled}
                onChange={setPreChatFormEnabled}
                helpText="Collect name and email before starting a conversation"
              />
              <Checkbox
                label="Enable offline form"
                checked={offlineFormEnabled}
                onChange={setOfflineFormEnabled}
                helpText="Show a contact form when outside business hours"
              />
              <Checkbox
                label="Sound notifications"
                checked={soundEnabled}
                onChange={setSoundEnabled}
                helpText="Play a sound when new messages arrive"
              />
            </BlockStack>
          </LegacyCard>

          {/* Content */}
          <LegacyCard title="Content" sectioned>
            <BlockStack gap="400">
              <TextField
                label="Header Title"
                value={headerTitle}
                onChange={setHeaderTitle}
                autoComplete="off"
              />
              <TextField
                label="Header Subtitle"
                value={headerSubtitle}
                onChange={setHeaderSubtitle}
                autoComplete="off"
              />
              <TextField
                label="Input Placeholder"
                value={inputPlaceholder}
                onChange={setInputPlaceholder}
                autoComplete="off"
              />
            </BlockStack>
          </LegacyCard>
        </Layout.Section>

        {/* Right column: Live preview */}
        <Layout.Section variant="oneThird">
          <LegacyCard title="Preview" sectioned>
            <Box>
              <div
                style={{
                  width: '100%',
                  maxWidth: 320,
                  margin: '0 auto',
                  borderRadius: borderRadius,
                  overflow: 'hidden',
                  border: '1px solid #c9cccf',
                  boxShadow: '0 4px 20px rgba(0, 0, 0, 0.12)',
                  fontFamily: fontFamily,
                  background: '#ffffff',
                }}
              >
                {/* Header */}
                <div
                  style={{
                    background: `linear-gradient(135deg, ${primaryColor}, ${gradientEnd})`,
                    padding: '20px 16px',
                    color: headerTextColor,
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <div
                      style={{
                        width: 36,
                        height: 36,
                        borderRadius: '50%',
                        background: 'rgba(255,255,255,0.2)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: 16,
                        fontWeight: 700,
                        flexShrink: 0,
                      }}
                    >
                      AR
                    </div>
                    <div>
                      <div style={{ fontWeight: 600, fontSize: 15, lineHeight: '20px' }}>
                        {headerTitle || 'Support'}
                      </div>
                      <div style={{ fontSize: 12, opacity: 0.85, lineHeight: '16px' }}>
                        {headerSubtitle || 'We typically reply within minutes'}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Message area */}
                <div style={{ padding: '16px', minHeight: 200, background: '#f6f6f7' }}>
                  {/* Greeting message bubble */}
                  {greetingEnabled && (
                    <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
                      <div
                        style={{
                          width: 28,
                          height: 28,
                          borderRadius: '50%',
                          background: primaryColor,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          color: headerTextColor,
                          fontSize: 10,
                          fontWeight: 700,
                          flexShrink: 0,
                        }}
                      >
                        AR
                      </div>
                      <div
                        style={{
                          background: '#ffffff',
                          padding: '10px 14px',
                          borderRadius: `${Math.min(borderRadius, 16)}px ${Math.min(borderRadius, 16)}px ${Math.min(borderRadius, 16)}px 4px`,
                          fontSize: 13,
                          lineHeight: '18px',
                          color: '#202223',
                          maxWidth: '80%',
                          boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
                        }}
                      >
                        {greetingMessage || 'Hi there! How can we help you today?'}
                      </div>
                    </div>
                  )}

                  {/* Sample customer message */}
                  <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 16 }}>
                    <div
                      style={{
                        background: primaryColor,
                        color: headerTextColor,
                        padding: '10px 14px',
                        borderRadius: `${Math.min(borderRadius, 16)}px ${Math.min(borderRadius, 16)}px 4px ${Math.min(borderRadius, 16)}px`,
                        fontSize: 13,
                        lineHeight: '18px',
                        maxWidth: '80%',
                      }}
                    >
                      I need help with my order
                    </div>
                  </div>

                  {/* Typing indicator */}
                  <div style={{ display: 'flex', gap: 8 }}>
                    <div
                      style={{
                        width: 28,
                        height: 28,
                        borderRadius: '50%',
                        background: primaryColor,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: headerTextColor,
                        fontSize: 10,
                        fontWeight: 700,
                        flexShrink: 0,
                      }}
                    >
                      AR
                    </div>
                    <div
                      style={{
                        background: '#ffffff',
                        padding: '12px 18px',
                        borderRadius: `${Math.min(borderRadius, 16)}px ${Math.min(borderRadius, 16)}px ${Math.min(borderRadius, 16)}px 4px`,
                        boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
                        display: 'flex',
                        gap: 4,
                        alignItems: 'center',
                      }}
                    >
                      <div style={{ width: 6, height: 6, borderRadius: '50%', background: '#8c9196', opacity: 0.6 }} />
                      <div style={{ width: 6, height: 6, borderRadius: '50%', background: '#8c9196', opacity: 0.4 }} />
                      <div style={{ width: 6, height: 6, borderRadius: '50%', background: '#8c9196', opacity: 0.2 }} />
                    </div>
                  </div>
                </div>

                {/* Input bar */}
                <div
                  style={{
                    padding: '12px 16px',
                    borderTop: '1px solid #e1e3e5',
                    background: '#ffffff',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 8,
                  }}
                >
                  <div
                    style={{
                      flex: 1,
                      background: '#f6f6f7',
                      borderRadius: Math.min(borderRadius, 20),
                      padding: '10px 14px',
                      fontSize: 13,
                      color: '#8c9196',
                      border: '1px solid #e1e3e5',
                    }}
                  >
                    {inputPlaceholder || 'Type your message...'}
                  </div>
                  <div
                    style={{
                      width: 32,
                      height: 32,
                      borderRadius: '50%',
                      background: primaryColor,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      cursor: 'pointer',
                      flexShrink: 0,
                    }}
                  >
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" style={{ transform: 'rotate(-45deg)' }}>
                      <path d="M2 12L22 2L17 12L22 22L2 12Z" fill={headerTextColor} />
                    </svg>
                  </div>
                </div>

                {/* Powered by footer */}
                <div
                  style={{
                    textAlign: 'center',
                    padding: '6px',
                    fontSize: 10,
                    color: '#8c9196',
                    background: '#f6f6f7',
                    borderTop: '1px solid #e1e3e5',
                  }}
                >
                  Powered by <span style={{ fontWeight: 600, color: '#C41E2A' }}>Agent Red</span>
                </div>
              </div>

              {/* Launcher preview */}
              <Box paddingBlockStart="400">
                <Text as="p" variant="bodySm" tone="subdued" alignment="center">
                  Launcher button preview
                </Text>
                <div style={{ display: 'flex', justifyContent: position === 'bottom-right' ? 'flex-end' : 'flex-start', marginTop: 8 }}>
                  <div
                    style={{
                      width: launcherSize,
                      height: launcherSize,
                      borderRadius: '50%',
                      background: primaryColor,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
                      cursor: 'pointer',
                    }}
                  >
                    <svg width={launcherSize * 0.4} height={launcherSize * 0.4} viewBox="0 0 24 24" fill="none">
                      <path
                        d="M21 11.5C21 16.75 16.75 21 11.5 21C9.8 21 8.2 20.55 6.8 19.75L2 21L3.25 16.2C2.45 14.8 2 13.2 2 11.5C2 6.25 6.25 2 11.5 2C16.75 2 21 6.25 21 11.5Z"
                        fill={headerTextColor}
                      />
                    </svg>
                  </div>
                </div>
              </Box>
            </Box>
          </LegacyCard>
        </Layout.Section>
      </Layout>
    </Page>
  );
}
