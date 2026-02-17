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
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useCallback, useState } from 'react';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const BRAND_PRIMARY = '#ff3621';

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
// Styles
// ---------------------------------------------------------------------------

const panelStyle: React.CSSProperties = {
  marginTop: 12,
  padding: 16,
  background: '#141414',
  border: '1px solid #272727',
  borderRadius: 8,
};

const sectionStyle: React.CSSProperties = {
  marginBottom: 16,
};

const labelStyle: React.CSSProperties = {
  display: 'block',
  fontSize: 12,
  fontWeight: 600,
  color: '#A0A0A0',
  marginBottom: 6,
  textTransform: 'uppercase' as const,
  letterSpacing: '0.04em',
};

const inputStyle: React.CSSProperties = {
  width: '100%',
  padding: '8px 12px',
  background: '#1f1f1f',
  border: '1px solid #272727',
  borderRadius: 6,
  color: '#F5F5F5',
  fontSize: 13,
  fontFamily: 'monospace',
  outline: 'none',
  boxSizing: 'border-box' as const,
};

const btnStyle = (variant: 'primary' | 'outline'): React.CSSProperties => ({
  padding: '6px 14px',
  borderRadius: 6,
  fontSize: 13,
  fontWeight: 500,
  cursor: 'pointer',
  transition: 'background 150ms ease',
  border: variant === 'primary' ? 'none' : '1px solid #272727',
  background: variant === 'primary' ? BRAND_PRIMARY : 'transparent',
  color: variant === 'primary' ? '#fff' : '#A0A0A0',
});

const statusDotStyle = (color: string): React.CSSProperties => ({
  width: 8,
  height: 8,
  borderRadius: '50%',
  background: color,
  display: 'inline-block',
  marginRight: 6,
});

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
    } catch (err) {
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
    } catch (err) {
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
    } catch (err) {
      onNotify('Network error removing credentials.', 'error');
    }
  }, [apiFetch, onNotify, onStatusChange]);

  return (
    <div style={panelStyle}>
      <div style={{ fontSize: 14, fontWeight: 600, color: '#F5F5F5', marginBottom: 12 }}>
        Stripe MCP Configuration
      </div>

      {/* Section 1: Credential Input */}
      <div style={sectionStyle}>
        <label style={labelStyle}>Stripe API Key (Restricted)</label>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <input
            type="password"
            placeholder="rk_live_... or sk_test_..."
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            style={{ ...inputStyle, flex: 1 }}
          />
          <button
            style={btnStyle('primary')}
            onClick={handleSaveKey}
            disabled={saving || !apiKey}
          >
            {saving ? 'Saving...' : 'Save Key'}
          </button>
        </div>
        <div style={{ fontSize: 11, color: '#5C5C5C', marginTop: 4 }}>
          Use a restricted key from your Stripe Dashboard for best security.
        </div>
      </div>

      {/* Section 2: Connection Test */}
      <div style={sectionStyle}>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <button
            style={btnStyle('outline')}
            onClick={handleTestConnection}
            disabled={testing}
          >
            {testing ? 'Testing...' : 'Test Connection'}
          </button>
          <button
            style={{
              ...btnStyle('outline'),
              color: '#D32F2F',
              borderColor: '#D32F2F44',
            }}
            onClick={handleRemoveCredentials}
          >
            Remove Key
          </button>
        </div>
      </div>

      {/* Section 3: Test Result */}
      {testResult && (
        <div
          style={{
            padding: 12,
            background: testResult.success ? '#0D7C3E11' : '#D32F2F11',
            border: `1px solid ${testResult.success ? '#0D7C3E33' : '#D32F2F33'}`,
            borderRadius: 6,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: 4 }}>
            <span
              style={statusDotStyle(testResult.success ? '#0D7C3E' : '#D32F2F')}
            />
            <span
              style={{
                fontSize: 13,
                fontWeight: 600,
                color: testResult.success ? '#0D7C3E' : '#D32F2F',
              }}
            >
              {testResult.success ? 'Connected' : 'Connection Failed'}
            </span>
            <span style={{ fontSize: 11, color: '#787878', marginLeft: 8 }}>
              {testResult.elapsed_ms.toFixed(0)}ms
            </span>
          </div>

          {testResult.success && (
            <div style={{ fontSize: 12, color: '#A0A0A0' }}>
              {testResult.tool_count} tools available
              {testResult.tools.length > 0 && (
                <span style={{ color: '#5C5C5C' }}>
                  {' '}— {testResult.tools.slice(0, 5).join(', ')}
                  {testResult.tools.length > 5 && ` +${testResult.tools.length - 5} more`}
                </span>
              )}
            </div>
          )}

          {testResult.error && (
            <div style={{ fontSize: 12, color: '#D32F2F', marginTop: 4 }}>
              {testResult.error}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
