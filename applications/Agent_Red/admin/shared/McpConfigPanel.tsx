// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * McpConfigPanel — Stripe MCP credential management and connection testing.
 *
 * Rendered inside IntegrationsManager when the Stripe integration card
 * is expanded (enabled + connected). Provides:
 *   1. Credential input — masked API key, "Save Key" button
 *   2. Connection test — "Test Connection" button → green/red status + tool count
 *   3. Status display — connection status badge from stripe_mcp_status
 *
 * AGNTCY Phase 3B (Cycle 5) — assertion 3.6 (Admin UI).
 * Migrated to Mantine components (Cycle 10, item 10f).
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useCallback, useState } from 'react';
import {
  Alert,
  Badge,
  Box,
  Button,
  Group,
  Paper,
  PasswordInput,
  Stack,
  Text,
  Title,
} from '@mantine/core';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface McpConfigPanelProps {
  tenantId: string;
  apiFetch: (url: string, options?: RequestInit) => Promise<Response>;
  onNotify: (message: string, severity: 'success' | 'error' | 'info') => void;
  onStatusChange?: () => void;
}

interface ConnectionTestResult {
  success: boolean;
  tool_count: number;
  tools: string[];
  error: string | null;
  elapsed_ms: number;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export const McpConfigPanel: React.FC<McpConfigPanelProps> = ({
  tenantId,
  apiFetch,
  onNotify,
  onStatusChange,
}) => {
  const [apiKey, setApiKey] = useState('');
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<ConnectionTestResult | null>(null);

  // ---- Save Stripe API key ----
  const handleSaveKey = useCallback(async () => {
    if (!apiKey || apiKey.length < 10) {
      onNotify('Please enter a valid Stripe API key.', 'error');
      return;
    }

    setSaving(true);
    try {
      const resp = await apiFetch('/api/admin/integrations/stripe/credentials', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_key: apiKey }),
      });

      if (resp.ok) {
        setApiKey('');
        onNotify('Stripe API key saved successfully.', 'success');
        onStatusChange?.();
      } else {
        const data = await resp.json().catch(() => ({}));
        onNotify(data.detail || 'Failed to save API key.', 'error');
      }
    } catch {
      onNotify('Network error saving API key.', 'error');
    } finally {
      setSaving(false);
    }
  }, [apiKey, apiFetch, onNotify, onStatusChange]);

  // ---- Test connection ----
  const handleTestConnection = useCallback(async () => {
    setTesting(true);
    setTestResult(null);
    try {
      const resp = await apiFetch('/api/admin/integrations/stripe/test', {
        method: 'POST',
      });

      const data: ConnectionTestResult = await resp.json();
      setTestResult(data);

      if (data.success) {
        onNotify(`Connected! ${data.tool_count} tools available.`, 'success');
        onStatusChange?.();
      } else {
        onNotify(data.error || 'Connection test failed.', 'error');
      }
    } catch {
      setTestResult({
        success: false,
        tool_count: 0,
        tools: [],
        error: 'Network error during connection test.',
        elapsed_ms: 0,
      });
      onNotify('Network error during connection test.', 'error');
    } finally {
      setTesting(false);
    }
  }, [apiFetch, onNotify, onStatusChange]);

  // ---- Remove credentials ----
  const handleRemoveCredentials = useCallback(async () => {
    try {
      const resp = await apiFetch('/api/admin/integrations/stripe/credentials', {
        method: 'DELETE',
      });

      if (resp.ok) {
        setTestResult(null);
        onNotify('Stripe credentials removed.', 'success');
        onStatusChange?.();
      } else {
        onNotify('Failed to remove credentials.', 'error');
      }
    } catch {
      onNotify('Network error removing credentials.', 'error');
    }
  }, [apiFetch, onNotify, onStatusChange]);

  return (
    <Paper bg="dark.8" p="md" radius="sm" mt="sm" withBorder>
      <Title order={5} mb="sm">
        Stripe MCP Configuration
      </Title>

      {/* Section 1: Credential Input */}
      <Stack gap="xs" mb="md">
        <PasswordInput
          label="Stripe API Key (Restricted)"
          placeholder="rk_live_... or sk_test_..."
          value={apiKey}
          onChange={(e) => setApiKey(e.currentTarget.value)}
          aria-label="Stripe API key"
          styles={{
            label: {
              fontSize: 12,
              fontWeight: 600,
              textTransform: 'uppercase',
              letterSpacing: '0.04em',
            },
            input: {
              fontFamily: 'monospace',
            },
          }}
        />
        <Group gap="sm">
          <Button
            size="xs"
            color="action"
            onClick={handleSaveKey}
            disabled={saving || !apiKey}
            loading={saving}
            aria-label="Save Stripe API key"
          >
            Save Key
          </Button>
        </Group>
        <Text size="xs" c="dimmed">
          Use a restricted key from your Stripe Dashboard for best security.
        </Text>
      </Stack>

      {/* Section 2: Connection Test */}
      <Group gap="sm" mb="md">
        <Button
          size="xs"
          variant="default"
          onClick={handleTestConnection}
          disabled={testing}
          loading={testing}
          aria-label="Test Stripe connection"
        >
          Test Connection
        </Button>
        <Button
          size="xs"
          variant="outline"
          color="red"
          onClick={handleRemoveCredentials}
          aria-label="Remove Stripe credentials"
        >
          Remove Key
        </Button>
      </Group>

      {/* Section 3: Test Result */}
      {testResult && (
        <Alert
          color={testResult.success ? 'green' : 'red'}
          radius="sm"
          variant="light"
          title={
            <Group gap="xs">
              <Badge
                size="sm"
                variant="dot"
                color={testResult.success ? 'green' : 'red'}
              >
                {testResult.success ? 'Connected' : 'Connection Failed'}
              </Badge>
              <Text size="xs" c="dimmed">
                {testResult.elapsed_ms.toFixed(0)}ms
              </Text>
            </Group>
          }
        >
          {testResult.success && (
            <Text size="sm" c="dimmed">
              {testResult.tool_count} tools available
              {testResult.tools.length > 0 && (
                <Text span size="xs" c="dimmed">
                  {' '}&mdash; {testResult.tools.slice(0, 5).join(', ')}
                  {testResult.tools.length > 5 && ` +${testResult.tools.length - 5} more`}
                </Text>
              )}
            </Text>
          )}

          {testResult.error && (
            <Text size="sm" c="red">
              {testResult.error}
            </Text>
          )}
        </Alert>
      )}
    </Paper>
  );
};
