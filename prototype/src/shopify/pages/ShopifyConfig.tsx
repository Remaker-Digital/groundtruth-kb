// (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

import React, { useState, useCallback } from 'react';
import {
  Page,
  Layout,
  LegacyCard,
  TextField,
  Select,
  RangeSlider,
  Tag,
  Banner,
  Button,
  Text,
  Badge,
  Box,
  InlineStack,
  BlockStack,
  Divider,
} from '@shopify/polaris';
import { DEFAULT_TENANT_CONFIG, CONFIG_ROLLOUTS } from '../../data/mockData';

export function ShopifyConfig() {
  // Brand & Persona
  const [brandName, setBrandName] = useState(DEFAULT_TENANT_CONFIG.brandName);
  const [brandVoice, setBrandVoice] = useState(DEFAULT_TENANT_CONFIG.brandVoice);
  const [formality, setFormality] = useState(DEFAULT_TENANT_CONFIG.formality);
  const [responseLength, setResponseLength] = useState(DEFAULT_TENANT_CONFIG.responseLength);

  // Policies
  const [returnWindow, setReturnWindow] = useState(String(DEFAULT_TENANT_CONFIG.returnWindow));
  const [refundPolicy, setRefundPolicy] = useState(DEFAULT_TENANT_CONFIG.refundPolicy);
  const [shippingPolicy, setShippingPolicy] = useState(DEFAULT_TENANT_CONFIG.shippingPolicy);

  // Escalation
  const [escalationThreshold, setEscalationThreshold] = useState(DEFAULT_TENANT_CONFIG.escalationThreshold * 100);
  const [autoEscalateTopics, setAutoEscalateTopics] = useState<string[]>(DEFAULT_TENANT_CONFIG.autoEscalateTopics);
  const [idleTimeout, setIdleTimeout] = useState(String(DEFAULT_TENANT_CONFIG.idleTimeoutMinutes));
  const [maxTurns, setMaxTurns] = useState(String(DEFAULT_TENANT_CONFIG.maxTurns));

  // Custom Instructions
  const [customInstructions, setCustomInstructions] = useState(DEFAULT_TENANT_CONFIG.customInstructions);

  const handleRemoveTag = useCallback(
    (tag: string) => () => {
      setAutoEscalateTopics((prev) => prev.filter((t) => t !== tag));
    },
    [],
  );

  const handleSave = useCallback(() => {
    // In a real implementation, this would call the config API
    console.log('Saving configuration...');
  }, []);

  const handleDiscard = useCallback(() => {
    setBrandName(DEFAULT_TENANT_CONFIG.brandName);
    setBrandVoice(DEFAULT_TENANT_CONFIG.brandVoice);
    setFormality(DEFAULT_TENANT_CONFIG.formality);
    setResponseLength(DEFAULT_TENANT_CONFIG.responseLength);
    setReturnWindow(String(DEFAULT_TENANT_CONFIG.returnWindow));
    setRefundPolicy(DEFAULT_TENANT_CONFIG.refundPolicy);
    setShippingPolicy(DEFAULT_TENANT_CONFIG.shippingPolicy);
    setEscalationThreshold(DEFAULT_TENANT_CONFIG.escalationThreshold * 100);
    setAutoEscalateTopics(DEFAULT_TENANT_CONFIG.autoEscalateTopics);
    setIdleTimeout(String(DEFAULT_TENANT_CONFIG.idleTimeoutMinutes));
    setMaxTurns(String(DEFAULT_TENANT_CONFIG.maxTurns));
    setCustomInstructions(DEFAULT_TENANT_CONFIG.customInstructions);
  }, []);

  const formalityOptions = [
    { label: 'Casual', value: 'casual' },
    { label: 'Professional', value: 'professional' },
    { label: 'Formal', value: 'formal' },
  ];

  const responseLengthOptions = [
    { label: 'Concise', value: 'concise' },
    { label: 'Moderate', value: 'moderate' },
    { label: 'Detailed', value: 'detailed' },
  ];

  // Find active and reverted rollouts
  const activeRollout = CONFIG_ROLLOUTS.find((r) => r.status === 'active');
  const revertedRollout = CONFIG_ROLLOUTS.find((r) => r.status === 'reverted');

  return (
    <Page
      title="Configuration"
      primaryAction={{ content: 'Save', disabled: false, onAction: handleSave }}
      secondaryActions={[{ content: 'Discard', onAction: handleDiscard }]}
    >
      <Layout>
        {/* Brand & Persona */}
        <Layout.AnnotatedSection
          title="Brand & Persona"
          description="Define how your AI agent communicates"
        >
          <LegacyCard sectioned>
            <BlockStack gap="400">
              <TextField
                label="Brand Name"
                value={brandName}
                onChange={setBrandName}
                autoComplete="off"
              />
              <TextField
                label="Brand Voice"
                value={brandVoice}
                onChange={setBrandVoice}
                multiline={4}
                autoComplete="off"
              />
              <InlineStack gap="400" wrap={true}>
                <div style={{ flex: '1 1 45%', minWidth: 200 }}>
                  <Select
                    label="Formality"
                    options={formalityOptions}
                    value={formality}
                    onChange={(v) => setFormality(v as any)}
                  />
                </div>
                <div style={{ flex: '1 1 45%', minWidth: 200 }}>
                  <Select
                    label="Response Length"
                    options={responseLengthOptions}
                    value={responseLength}
                    onChange={(v) => setResponseLength(v as any)}
                  />
                </div>
              </InlineStack>
            </BlockStack>
          </LegacyCard>
        </Layout.AnnotatedSection>

        {/* Policies */}
        <Layout.AnnotatedSection
          title="Policies"
          description="Business policies your AI will reference"
        >
          <LegacyCard sectioned>
            <BlockStack gap="400">
              <TextField
                label="Return Window"
                type="number"
                value={returnWindow}
                onChange={setReturnWindow}
                suffix="days"
                autoComplete="off"
              />
              <TextField
                label="Refund Policy"
                value={refundPolicy}
                onChange={setRefundPolicy}
                multiline={3}
                autoComplete="off"
              />
              <TextField
                label="Shipping Policy"
                value={shippingPolicy}
                onChange={setShippingPolicy}
                multiline={3}
                autoComplete="off"
              />
            </BlockStack>
          </LegacyCard>
        </Layout.AnnotatedSection>

        {/* Escalation */}
        <Layout.AnnotatedSection
          title="Escalation"
          description="Control when conversations transfer to humans"
        >
          <LegacyCard sectioned>
            <BlockStack gap="400">
              <div>
                <RangeSlider
                  label={`Escalation Threshold: ${(escalationThreshold / 100).toFixed(1)}`}
                  value={escalationThreshold}
                  onChange={(value) => setEscalationThreshold(value as number)}
                  min={0}
                  max={100}
                  step={5}
                  output
                />
                <Box paddingBlockStart="100">
                  <Text as="p" variant="bodySm" tone="subdued">
                    AI confidence below this threshold triggers escalation to a human agent.
                    Current: {(escalationThreshold / 100).toFixed(1)}
                  </Text>
                </Box>
              </div>
              <Divider />
              <div>
                <Text as="p" variant="bodyMd" fontWeight="semibold">
                  Auto-Escalate Topics
                </Text>
                <Box paddingBlockStart="200">
                  <InlineStack gap="200" wrap={true}>
                    {autoEscalateTopics.map((topic) => (
                      <Tag key={topic} onRemove={handleRemoveTag(topic)}>
                        {topic}
                      </Tag>
                    ))}
                  </InlineStack>
                </Box>
              </div>
              <Divider />
              <InlineStack gap="400" wrap={true}>
                <div style={{ flex: '1 1 45%', minWidth: 200 }}>
                  <TextField
                    label="Idle Timeout"
                    type="number"
                    value={idleTimeout}
                    onChange={setIdleTimeout}
                    suffix="minutes"
                    autoComplete="off"
                  />
                </div>
                <div style={{ flex: '1 1 45%', minWidth: 200 }}>
                  <TextField
                    label="Max Turns"
                    type="number"
                    value={maxTurns}
                    onChange={setMaxTurns}
                    autoComplete="off"
                  />
                </div>
              </InlineStack>
            </BlockStack>
          </LegacyCard>
        </Layout.AnnotatedSection>

        {/* Custom Instructions */}
        <Layout.AnnotatedSection
          title="Custom Instructions"
          description="Additional guidance for your AI. Safety rules always take precedence."
        >
          <LegacyCard sectioned>
            <TextField
              label="Custom Instructions"
              value={customInstructions}
              onChange={setCustomInstructions}
              multiline={5}
              autoComplete="off"
              helpText="These instructions guide your AI agent's behavior. Agent Red's safety guardrails cannot be overridden by custom instructions."
            />
          </LegacyCard>
        </Layout.AnnotatedSection>

        {/* Defensive Rollout */}
        <Layout.AnnotatedSection
          title="Defensive Rollout"
          description="Test configuration changes safely before full deployment"
        >
          <LegacyCard sectioned>
            <BlockStack gap="400">
              {activeRollout && (
                <>
                  <Banner
                    title={`Active rollout: ${activeRollout.name}`}
                    tone="info"
                  >
                    <p>
                      {activeRollout.trafficSplit}% of traffic is seeing the test configuration.
                      Started {new Date(activeRollout.startedAt!).toLocaleDateString()}.
                    </p>
                  </Banner>

                  <LegacyCard.Section title="Rollout Details">
                    <BlockStack gap="300">
                      <InlineStack gap="400">
                        <Text as="span" variant="bodySm" fontWeight="semibold">
                          Traffic Split:
                        </Text>
                        <Text as="span" variant="bodySm">
                          {100 - activeRollout.trafficSplit}% Group A (control) / {activeRollout.trafficSplit}% Group B (test)
                        </Text>
                      </InlineStack>
                      <InlineStack gap="400">
                        <Text as="span" variant="bodySm" fontWeight="semibold">
                          Selection Method:
                        </Text>
                        <Badge>{activeRollout.selectionMethod}</Badge>
                      </InlineStack>

                      <Divider />

                      <Text as="p" variant="bodyMd" fontWeight="semibold">
                        Changes Being Tested
                      </Text>
                      {activeRollout.changes.map((change, i) => (
                        <InlineStack key={i} gap="200" blockAlign="center">
                          <Badge tone="info">{change.field}</Badge>
                          <Text as="span" variant="bodySm" tone="subdued">
                            {String(change.currentValue)}
                          </Text>
                          <Text as="span" variant="bodySm">
                            &rarr;
                          </Text>
                          <Text as="span" variant="bodySm" fontWeight="semibold">
                            {String(change.newValue)}
                          </Text>
                        </InlineStack>
                      ))}

                      <Divider />

                      <Text as="p" variant="bodyMd" fontWeight="semibold">
                        Performance Comparison
                      </Text>
                      <div style={{ overflowX: 'auto' }}>
                        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
                          <thead>
                            <tr style={{ borderBottom: '1px solid #e1e3e5' }}>
                              <th style={{ textAlign: 'left', padding: '8px 12px', color: '#6d7175' }}>Metric</th>
                              <th style={{ textAlign: 'right', padding: '8px 12px', color: '#6d7175' }}>Group A (control)</th>
                              <th style={{ textAlign: 'right', padding: '8px 12px', color: '#6d7175' }}>Group B (test)</th>
                              <th style={{ textAlign: 'right', padding: '8px 12px', color: '#6d7175' }}>Delta</th>
                            </tr>
                          </thead>
                          <tbody>
                            {[
                              { label: 'Conversations', a: activeRollout.metrics.groupA.conversations, b: activeRollout.metrics.groupB.conversations, suffix: '' },
                              { label: 'Satisfaction', a: activeRollout.metrics.groupA.satisfaction, b: activeRollout.metrics.groupB.satisfaction, suffix: '/5' },
                              { label: 'Resolution Rate', a: activeRollout.metrics.groupA.resolutionRate, b: activeRollout.metrics.groupB.resolutionRate, suffix: '%' },
                              { label: 'Escalation Rate', a: activeRollout.metrics.groupA.escalationRate, b: activeRollout.metrics.groupB.escalationRate, suffix: '%' },
                            ].map((row) => {
                              const delta = row.b - row.a;
                              const isEscalation = row.label === 'Escalation Rate';
                              const isPositive = isEscalation ? delta < 0 : delta > 0;
                              return (
                                <tr key={row.label} style={{ borderBottom: '1px solid #f1f2f4' }}>
                                  <td style={{ padding: '8px 12px' }}>{row.label}</td>
                                  <td style={{ textAlign: 'right', padding: '8px 12px' }}>
                                    {row.a}{row.suffix}
                                  </td>
                                  <td style={{ textAlign: 'right', padding: '8px 12px', fontWeight: 600 }}>
                                    {row.b}{row.suffix}
                                  </td>
                                  <td style={{
                                    textAlign: 'right',
                                    padding: '8px 12px',
                                    color: isPositive ? '#108043' : '#D72C0D',
                                    fontWeight: 600,
                                  }}>
                                    {delta > 0 ? '+' : ''}{delta.toFixed(1)}{row.suffix}
                                  </td>
                                </tr>
                              );
                            })}
                          </tbody>
                        </table>
                      </div>
                    </BlockStack>
                  </LegacyCard.Section>
                </>
              )}

              {revertedRollout && revertedRollout.autoRevert.reverted && (
                <>
                  <Divider />
                  <Banner
                    title={`Reverted: ${revertedRollout.name}`}
                    tone="critical"
                  >
                    <p>{revertedRollout.autoRevert.revertReason}</p>
                    <p style={{ marginTop: 4, fontSize: 12, color: '#6d7175' }}>
                      Automatically reverted on{' '}
                      {new Date(revertedRollout.completedAt!).toLocaleDateString()} at{' '}
                      {new Date(revertedRollout.completedAt!).toLocaleTimeString()}.
                    </p>
                  </Banner>
                </>
              )}

              {!activeRollout && !revertedRollout && (
                <Box padding="400">
                  <BlockStack gap="200" align="center">
                    <Text as="p" variant="bodySm" tone="subdued" alignment="center">
                      No active rollouts. Create a rollout to test configuration changes
                      on a subset of traffic before applying them to all customers.
                    </Text>
                    <InlineStack align="center">
                      <Button>Create Rollout</Button>
                    </InlineStack>
                  </BlockStack>
                </Box>
              )}
            </BlockStack>
          </LegacyCard>
        </Layout.AnnotatedSection>
      </Layout>
    </Page>
  );
}
