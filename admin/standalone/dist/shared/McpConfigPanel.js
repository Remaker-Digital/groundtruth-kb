import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
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
import { useCallback, useState } from 'react';
import { Alert, Badge, Button, Group, Paper, PasswordInput, Stack, Text, Title, } from '@mantine/core';
// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------
export const McpConfigPanel = ({ tenantId, apiFetch, onNotify, onStatusChange, }) => {
    const [apiKey, setApiKey] = useState('');
    const [saving, setSaving] = useState(false);
    const [testing, setTesting] = useState(false);
    const [testResult, setTestResult] = useState(null);
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
            }
            else {
                const data = await resp.json().catch(() => ({}));
                onNotify(data.detail || 'Failed to save API key.', 'error');
            }
        }
        catch {
            onNotify('Network error saving API key.', 'error');
        }
        finally {
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
            const data = await resp.json();
            setTestResult(data);
            if (data.success) {
                onNotify(`Connected! ${data.tool_count} tools available.`, 'success');
                onStatusChange?.();
            }
            else {
                onNotify(data.error || 'Connection test failed.', 'error');
            }
        }
        catch {
            setTestResult({
                success: false,
                tool_count: 0,
                tools: [],
                error: 'Network error during connection test.',
                elapsed_ms: 0,
            });
            onNotify('Network error during connection test.', 'error');
        }
        finally {
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
            }
            else {
                onNotify('Failed to remove credentials.', 'error');
            }
        }
        catch {
            onNotify('Network error removing credentials.', 'error');
        }
    }, [apiFetch, onNotify, onStatusChange]);
    return (_jsxs(Paper, { bg: "dark.8", p: "md", radius: "sm", mt: "sm", withBorder: true, children: [_jsx(Title, { order: 5, mb: "sm", children: "Stripe MCP Configuration" }), _jsxs(Stack, { gap: "xs", mb: "md", children: [_jsx(PasswordInput, { label: "Stripe API Key (Restricted)", placeholder: "rk_live_... or sk_test_...", value: apiKey, onChange: (e) => setApiKey(e.currentTarget.value), "aria-label": "Stripe API key", styles: {
                            label: {
                                fontSize: 12,
                                fontWeight: 600,
                                textTransform: 'uppercase',
                                letterSpacing: '0.04em',
                            },
                            input: {
                                fontFamily: 'monospace',
                            },
                        } }), _jsx(Group, { gap: "sm", children: _jsx(Button, { size: "xs", color: "action", onClick: handleSaveKey, disabled: saving || !apiKey, loading: saving, "aria-label": "Save Stripe API key", children: "Save Key" }) }), _jsx(Text, { size: "xs", c: "dimmed", children: "Use a restricted key from your Stripe Dashboard for best security." })] }), _jsxs(Group, { gap: "sm", mb: "md", children: [_jsx(Button, { size: "xs", variant: "default", onClick: handleTestConnection, disabled: testing, loading: testing, "aria-label": "Test Stripe connection", children: "Test Connection" }), _jsx(Button, { size: "xs", variant: "outline", color: "red", onClick: handleRemoveCredentials, "aria-label": "Remove Stripe credentials", children: "Remove Key" })] }), testResult && (_jsxs(Alert, { color: testResult.success ? 'green' : 'red', radius: "sm", variant: "light", title: _jsxs(Group, { gap: "xs", children: [_jsx(Badge, { size: "sm", variant: "dot", color: testResult.success ? 'green' : 'red', children: testResult.success ? 'Connected' : 'Connection Failed' }), _jsxs(Text, { size: "xs", c: "dimmed", children: [testResult.elapsed_ms.toFixed(0), "ms"] })] }), children: [testResult.success && (_jsxs(Text, { size: "sm", c: "dimmed", children: [testResult.tool_count, " tools available", testResult.tools.length > 0 && (_jsxs(Text, { span: true, size: "xs", c: "dimmed", children: [' ', "\u2014 ", testResult.tools.slice(0, 5).join(', '), testResult.tools.length > 5 && ` +${testResult.tools.length - 5} more`] }))] })), testResult.error && (_jsx(Text, { size: "sm", c: "red", children: testResult.error }))] }))] }));
};
//# sourceMappingURL=McpConfigPanel.js.map