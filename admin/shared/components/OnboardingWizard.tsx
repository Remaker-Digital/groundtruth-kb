/**
 * OnboardingWizard — First-login modal that guides merchants through:
 *   Step 1: Select product category (from template registry) + optional storefront URL
 *   Step 2: Apply template + storefront ingestion (Shopify or URL) → progress
 *   Step 3: Show config suggestions → Activate now (one-click) or dismiss
 *
 * Supports two ingestion paths:
 *   - Shopify merchants: Uses Shopify Admin API via shopDomain prop
 *   - Non-Shopify merchants: Crawls storefront URL entered in Step 1
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Modal,
  Button,
  Stack,
  Text,
  Group,
  SimpleGrid,
  Card,
  ThemeIcon,
  Loader,
  Progress,
  Badge,
  Alert,
  Divider,
  Box,
  TextInput,
} from '@mantine/core';
import type { ApiFetch } from '../hooks';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface Template {
  id: string;
  name: string;
  description: string;
  article_count: number;
  suggested_brand_voice: string;
  suggested_escalation_keywords: string[];
}

interface ApplyResult {
  articlesCreated: number;
  articlesFailed: number;
  totalChars: number;
  configSuggestions?: Record<string, string>;
}

interface IngestionJob {
  job_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  source_type: string;
  pages_crawled?: number;
  articles_created?: number;
  articles_failed?: number;
  total_chars?: number;
  error?: string;
  progress_pct?: number;
}

interface ConfigSuggestion {
  fieldName: string;
  value: string | string[];
  source: string;
  confidence: number;
}

interface Props {
  opened: boolean;
  onClose: () => void;
  apiFetch: ApiFetch;
  shopDomain?: string;
  onNavigate?: (path: string) => void;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Validate a URL string (basic check for protocol + domain). */
function isValidUrl(url: string): boolean {
  try {
    const parsed = new URL(url);
    return parsed.protocol === 'http:' || parsed.protocol === 'https:';
  } catch {
    return false;
  }
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export const OnboardingWizard: React.FC<Props> = ({
  opened,
  onClose,
  apiFetch,
  shopDomain,
  onNavigate,
}) => {
  const [step, setStep] = useState<1 | 2 | 3>(1);
  const [templates, setTemplates] = useState<Template[]>([]);
  const [templatesLoading, setTemplatesLoading] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [storefrontUrl, setStorefrontUrl] = useState('');
  const [applyLoading, setApplyLoading] = useState(false);
  const [applyResult, setApplyResult] = useState<ApplyResult | null>(null);
  const [applyError, setApplyError] = useState<string | null>(null);
  const [ingestionJob, setIngestionJob] = useState<IngestionJob | null>(null);
  const [ingestionRunning, setIngestionRunning] = useState(false);
  const [suggestions, setSuggestions] = useState<ConfigSuggestion[] | null>(null);
  const [suggestionsLoading, setSuggestionsLoading] = useState(false);
  const [activating, setActivating] = useState(false);
  const [activateError, setActivateError] = useState<string | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // The effective ingestion URL for non-Shopify merchants
  const effectiveUrl = !shopDomain && storefrontUrl.trim() ? storefrontUrl.trim() : null;
  const urlValid = !effectiveUrl || isValidUrl(effectiveUrl);

  // Load templates on open
  useEffect(() => {
    if (!opened) return;
    setTemplatesLoading(true);
    apiFetch('/api/admin/knowledge/templates')
      .then((r) => r.json())
      .then((data) => setTemplates(data.templates || data || []))
      .catch(() => setTemplates([]))
      .finally(() => setTemplatesLoading(false));
  }, [opened, apiFetch]);

  // Clean up polling on unmount
  useEffect(() => {
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, []);

  // -------------------------------------------------------------------
  // Shared ingestion polling logic
  // -------------------------------------------------------------------

  const startIngestionPolling = useCallback(() => {
    if (pollRef.current) clearInterval(pollRef.current);
    pollRef.current = setInterval(async () => {
      try {
        const statusRes = await apiFetch('/api/admin/knowledge/ingest/status');
        if (statusRes.ok) {
          const status = await statusRes.json();
          if (!status || !status.status) {
            // No active job — ingestion finished or was never started
            if (pollRef.current) clearInterval(pollRef.current);
            pollRef.current = null;
            setIngestionRunning(false);
            return;
          }
          setIngestionJob(status);
          if (status.status === 'completed' || status.status === 'failed' || status.status === 'cancelled') {
            if (pollRef.current) clearInterval(pollRef.current);
            pollRef.current = null;
            setIngestionRunning(false);
          }
        }
      } catch { /* continue polling */ }
    }, 3000);
  }, [apiFetch]);

  // -------------------------------------------------------------------
  // Step 2: Apply template
  // -------------------------------------------------------------------

  const handleApplyTemplate = useCallback(async () => {
    if (!selectedCategory) return;
    setApplyLoading(true);
    setApplyError(null);
    setStep(2);

    try {
      const res = await apiFetch(`/api/admin/knowledge/templates/${selectedCategory}/apply`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({}),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Template application failed' }));
        throw new Error(err.detail || `HTTP ${res.status}`);
      }
      const result = await res.json();
      setApplyResult({
        articlesCreated: result.articles_created ?? result.articlesCreated ?? 0,
        articlesFailed: result.articles_failed ?? result.articlesFailed ?? 0,
        totalChars: result.total_chars ?? result.totalChars ?? 0,
        configSuggestions: result.config_suggestions ?? result.configSuggestions,
      });

      // Start storefront ingestion: Shopify path or URL path
      if (shopDomain) {
        startStorefrontIngestion();
      } else if (effectiveUrl) {
        startUrlIngestion(effectiveUrl);
      }
    } catch (e: any) {
      setApplyError(e.message || 'Failed to apply template');
    } finally {
      setApplyLoading(false);
    }
  }, [selectedCategory, apiFetch, shopDomain, effectiveUrl]);

  // -------------------------------------------------------------------
  // Shopify ingestion
  // -------------------------------------------------------------------

  const startStorefrontIngestion = useCallback(async () => {
    setIngestionRunning(true);
    try {
      const res = await apiFetch('/api/admin/knowledge/ingest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sourceType: 'shopify' }),
      });
      if (res.ok) {
        const job = await res.json();
        setIngestionJob(job);
        startIngestionPolling();
      } else {
        setIngestionRunning(false);
      }
    } catch {
      setIngestionRunning(false);
    }
  }, [apiFetch, startIngestionPolling]);

  // -------------------------------------------------------------------
  // URL ingestion (non-Shopify merchants)
  // -------------------------------------------------------------------

  const startUrlIngestion = useCallback(async (url: string) => {
    setIngestionRunning(true);
    try {
      const res = await apiFetch('/api/admin/knowledge/ingest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sourceType: 'url', url, maxPages: 20 }),
      });
      if (res.ok) {
        const job = await res.json();
        setIngestionJob(job);
        startIngestionPolling();
      } else {
        setIngestionRunning(false);
      }
    } catch {
      setIngestionRunning(false);
    }
  }, [apiFetch, startIngestionPolling]);

  // -------------------------------------------------------------------
  // Step 3: Load suggestions + Activate
  // -------------------------------------------------------------------

  const handleViewSuggestions = useCallback(async () => {
    setStep(3);
    setSuggestionsLoading(true);
    setActivateError(null);
    try {
      const res = await apiFetch('/api/admin/knowledge/suggestions');
      if (res.ok) {
        const data = await res.json();
        setSuggestions(Array.isArray(data) ? data : data.suggestions || []);
      }
    } catch { /* suggestions are best-effort */ }
    setSuggestionsLoading(false);
  }, [apiFetch]);

  /** One-click activation: save suggested config fields, then activate. */
  const handleActivateWithSuggestions = useCallback(async () => {
    setActivating(true);
    setActivateError(null);
    try {
      // Build fields from suggestions
      const fields: Record<string, unknown> = {};
      for (const s of suggestions || []) {
        fields[s.fieldName] = Array.isArray(s.value) ? s.value.join(', ') : s.value;
      }

      // Save config draft (only if we have suggestions to apply)
      if (Object.keys(fields).length > 0) {
        const saveRes = await apiFetch('/api/config', {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ fields }),
        });
        if (!saveRes.ok) {
          const err = await saveRes.json().catch(() => ({ detail: 'Failed to save configuration' }));
          throw new Error(err.detail || `Save failed: HTTP ${saveRes.status}`);
        }
      }

      // Activate the draft
      const activateRes = await apiFetch('/api/config/draft/activate', {
        method: 'POST',
      });
      if (!activateRes.ok) {
        const err = await activateRes.json().catch(() => ({ detail: 'Activation failed' }));
        throw new Error(err.detail || `Activate failed: HTTP ${activateRes.status}`);
      }

      // Success — close wizard and go to dashboard
      handleClose();
      if (onNavigate) onNavigate('/');
    } catch (e: any) {
      setActivateError(e.message || 'Activation failed');
    } finally {
      setActivating(false);
    }
  }, [suggestions, apiFetch, onNavigate]);

  // Navigate to config page (fallback for manual review)
  const handleGoToConfig = useCallback(() => {
    onClose();
    if (onNavigate) onNavigate('/configuration');
  }, [onClose, onNavigate]);

  // Reset on close
  const handleClose = useCallback(() => {
    setStep(1);
    setSelectedCategory(null);
    setStorefrontUrl('');
    setApplyResult(null);
    setApplyError(null);
    setIngestionJob(null);
    setIngestionRunning(false);
    setSuggestions(null);
    setActivating(false);
    setActivateError(null);
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
    onClose();
  }, [onClose]);

  const selectedTemplate = templates.find((t) => t.id === selectedCategory);

  // The label shown during ingestion progress
  const ingestionLabel = shopDomain
    ? `Importing pages from ${shopDomain}...`
    : effectiveUrl
      ? `Scanning ${new URL(effectiveUrl).hostname}...`
      : 'Scanning your storefront...';

  return (
    <Modal
      opened={opened}
      onClose={handleClose}
      title={
        <Group gap="xs">
          <ThemeIcon size="md" variant="light" color="action">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M8 0L9.8 6.2L16 8L9.8 9.8L8 16L6.2 9.8L0 8L6.2 6.2L8 0Z" fill="currentColor" />
            </svg>
          </ThemeIcon>
          <Text fw={600} size="lg">
            {step === 1 && 'Set up your AI assistant'}
            {step === 2 && 'Building your knowledge base'}
            {step === 3 && 'Ready to activate'}
          </Text>
        </Group>
      }
      centered
      size="lg"
      closeOnClickOutside={false}
      closeOnEscape={step === 1}
    >
      {/* Step 1: Category selection + storefront URL */}
      {step === 1 && (
        <Stack gap="md">
          <Text size="sm" c="dimmed">
            What type of products or services does your store sell? We'll create
            starter knowledge base articles tailored to your industry.
          </Text>

          {templatesLoading ? (
            <Group justify="center" py="xl">
              <Loader size="sm" />
              <Text size="sm" c="dimmed">Loading categories...</Text>
            </Group>
          ) : (
            <SimpleGrid cols={{ base: 2, sm: 3 }} spacing="xs">
              {templates.map((t) => (
                <Card
                  key={t.id}
                  padding="sm"
                  radius="sm"
                  withBorder
                  style={{
                    cursor: 'pointer',
                    borderColor: selectedCategory === t.id ? 'var(--mantine-color-action-6)' : undefined,
                    backgroundColor: selectedCategory === t.id ? 'var(--mantine-color-action-0)' : undefined,
                  }}
                  onClick={() => setSelectedCategory(t.id)}
                >
                  <Text size="sm" fw={500} lineClamp={1}>
                    {t.name}
                  </Text>
                  <Text size="xs" c="dimmed" lineClamp={2} mt={2}>
                    {t.description}
                  </Text>
                </Card>
              ))}
            </SimpleGrid>
          )}

          {selectedTemplate && (
            <Alert variant="light" color="action" radius="sm">
              <Text size="xs">
                <strong>{selectedTemplate.article_count} articles</strong> will be
                created for <strong>{selectedTemplate.name}</strong>.
                {selectedTemplate.suggested_brand_voice && (
                  <> Suggested voice: <em>{selectedTemplate.suggested_brand_voice}</em>.</>
                )}
              </Text>
            </Alert>
          )}

          {/* Storefront URL input — shown for non-Shopify merchants (4A) */}
          {!shopDomain && (
            <TextInput
              label="Your storefront URL (optional)"
              placeholder="https://www.yourstore.com"
              description="We'll scan your website to create knowledge base articles about your products and policies."
              value={storefrontUrl}
              onChange={(e) => setStorefrontUrl(e.currentTarget.value)}
              error={storefrontUrl.trim() && !urlValid ? 'Enter a valid URL starting with https://' : undefined}
              size="sm"
            />
          )}

          <Group justify="space-between" mt="xs">
            <Button variant="subtle" color="dimmed" onClick={handleClose} size="sm">
              Skip for now
            </Button>
            <Button
              color="action"
              onClick={handleApplyTemplate}
              disabled={!selectedCategory || (!!storefrontUrl.trim() && !urlValid)}
              size="sm"
            >
              Continue
            </Button>
          </Group>
        </Stack>
      )}

      {/* Step 2: Template application + ingestion progress */}
      {step === 2 && (
        <Stack gap="md">
          {applyLoading && (
            <Group justify="center" py="lg">
              <Loader size="sm" />
              <Text size="sm">Applying {selectedTemplate?.name} template...</Text>
            </Group>
          )}

          {applyError && (
            <Alert color="red" radius="sm" title="Template Error">
              <Text size="sm">{applyError}</Text>
              <Button
                size="xs"
                variant="light"
                color="red"
                mt="xs"
                onClick={() => { setApplyError(null); setStep(1); }}
              >
                Go back
              </Button>
            </Alert>
          )}

          {applyResult && !applyLoading && (
            <>
              <Alert variant="light" color="green" radius="sm" title="Knowledge base created">
                <Text size="sm">
                  <strong>{applyResult.articlesCreated}</strong> articles added
                  {applyResult.articlesFailed > 0 && (
                    <> ({applyResult.articlesFailed} failed)</>
                  )}
                </Text>
              </Alert>

              {ingestionRunning && ingestionJob && (
                <>
                  <Divider label="Scanning your storefront" labelPosition="center" />
                  <Stack gap="xs">
                    <Group justify="space-between">
                      <Text size="sm">
                        {ingestionLabel}
                      </Text>
                      <Badge size="sm" color="yellow" variant="light">
                        {ingestionJob.status}
                      </Badge>
                    </Group>
                    <Progress
                      value={ingestionJob.progress_pct ?? 0}
                      animated
                      size="sm"
                      color="action"
                    />
                    {ingestionJob.pages_crawled != null && (
                      <Text size="xs" c="dimmed">
                        {ingestionJob.pages_crawled} pages crawled,{' '}
                        {ingestionJob.articles_created ?? 0} articles created
                      </Text>
                    )}
                  </Stack>
                </>
              )}

              {ingestionJob && !ingestionRunning && ingestionJob.status === 'completed' && (
                <>
                  <Divider label="Storefront scan complete" labelPosition="center" />
                  <Alert variant="light" color="green" radius="sm">
                    <Text size="sm">
                      Imported <strong>{ingestionJob.articles_created ?? 0}</strong> additional
                      articles from your storefront.
                    </Text>
                  </Alert>
                </>
              )}

              {ingestionJob && !ingestionRunning && ingestionJob.status === 'failed' && (
                <Alert variant="light" color="yellow" radius="sm">
                  <Text size="sm">
                    Storefront scan encountered an issue. Your template articles are still available.
                    You can retry the scan later from the Knowledge Base page.
                  </Text>
                </Alert>
              )}

              <Group justify="flex-end" mt="xs">
                <Button
                  color="action"
                  onClick={handleViewSuggestions}
                  disabled={ingestionRunning}
                  size="sm"
                >
                  {ingestionRunning ? 'Please wait...' : 'Continue'}
                </Button>
              </Group>
            </>
          )}
        </Stack>
      )}

      {/* Step 3: Config suggestions + Activate */}
      {step === 3 && (
        <Stack gap="md">
          {suggestionsLoading ? (
            <Group justify="center" py="lg">
              <Loader size="sm" />
              <Text size="sm">Analyzing your knowledge base...</Text>
            </Group>
          ) : (
            <>
              <Text size="sm" c="dimmed">
                Based on your knowledge base, we've prepared these configuration
                settings. Click <strong>Activate now</strong> to go live immediately.
              </Text>

              {suggestions && suggestions.length > 0 ? (
                <Stack gap="xs">
                  {suggestions.map((suggestion) => (
                    <Card key={suggestion.fieldName} padding="xs" radius="sm" withBorder>
                      <Group justify="space-between" wrap="nowrap">
                        <Box>
                          <Text size="xs" fw={500} tt="capitalize">
                            {suggestion.fieldName.replace(/_/g, ' ')}
                          </Text>
                          <Text size="xs" c="dimmed" lineClamp={2}>
                            {Array.isArray(suggestion.value)
                              ? suggestion.value.join(', ')
                              : String(suggestion.value)}
                          </Text>
                        </Box>
                        <Badge size="xs" color="grape" variant="light">
                          Suggested
                        </Badge>
                      </Group>
                    </Card>
                  ))}
                </Stack>
              ) : (
                <Alert variant="light" color="blue" radius="sm">
                  <Text size="sm">
                    No configuration suggestions were generated. You can still
                    activate with default settings or configure manually.
                  </Text>
                </Alert>
              )}

              {activateError && (
                <Alert variant="light" color="red" radius="sm">
                  <Text size="sm">{activateError}</Text>
                </Alert>
              )}

              <Divider />

              <Group justify="space-between">
                <Button variant="subtle" color="dimmed" onClick={handleClose} size="sm">
                  I'll configure later
                </Button>
                <Group gap="xs">
                  <Button
                    variant="light"
                    color="action"
                    onClick={handleGoToConfig}
                    size="sm"
                  >
                    Review first
                  </Button>
                  <Button
                    color="green"
                    onClick={handleActivateWithSuggestions}
                    loading={activating}
                    size="sm"
                  >
                    Activate now
                  </Button>
                </Group>
              </Group>
            </>
          )}
        </Stack>
      )}
    </Modal>
  );
};

export default OnboardingWizard;
