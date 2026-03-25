/**
 * Admin hooks — team management, billing, integrations.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { useState, useCallback } from 'react';
import { useApi } from './useApi';
// ---------------------------------------------------------------------------
// Team hooks
// ---------------------------------------------------------------------------
export function useTeamMembers(apiFetch) {
    return useApi(apiFetch, '/api/admin/team');
}
export function useInviteTeamMember(apiFetch) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const invite = useCallback(async (email, role, name) => {
        setLoading(true);
        setError(null);
        try {
            // Backend expects display_name (required, min_length=1), not name
            const display_name = name?.trim() || email.split('@')[0];
            const resp = await apiFetch('/api/admin/team', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, role, display_name }),
            });
            if (!resp.ok) {
                const data = await resp.json().catch(() => ({}));
                if (resp.status === 409) {
                    throw new Error(data.detail || 'A team member with this email already exists.');
                }
                throw new Error(data.detail || `Failed to invite team member (${resp.status}).`);
            }
            return await resp.json();
        }
        catch (err) {
            const msg = err instanceof Error ? err.message : 'Invite failed';
            setError(msg);
            return null;
        }
        finally {
            setLoading(false);
        }
    }, [apiFetch]);
    return { invite, loading, error };
}
// ---------------------------------------------------------------------------
// Billing hooks
// ---------------------------------------------------------------------------
export function useBillingStatus(apiFetch, channel, shopDomain) {
    const path = channel === 'shopify'
        ? `/api/shopify/billing/status?shop=${encodeURIComponent(shopDomain || '')}`
        : '/api/billing/status';
    const enabled = channel === 'stripe' || !!shopDomain;
    return useApi(apiFetch, path, enabled);
}
export function usePackBalance(apiFetch, customerId) {
    return useApi(apiFetch, `/api/packs/balance/${customerId}`, !!customerId);
}
// ---------------------------------------------------------------------------
// Integration hooks (C10)
// ---------------------------------------------------------------------------
export function useIntegrations(apiFetch) {
    return useApi(apiFetch, '/api/admin/integrations');
}
export function useIntegrationDetail(apiFetch, type) {
    return useApi(apiFetch, `/api/admin/integrations/${type}`, !!type);
}
export function useActivateIntegration(apiFetch) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const activate = useCallback(async (type) => {
        setLoading(true);
        setError(null);
        try {
            const resp = await apiFetch(`/api/admin/integrations/${type}/activate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({}),
            });
            if (!resp.ok) {
                const data = await resp.json().catch(() => ({}));
                throw new Error(data.detail || `${resp.status}`);
            }
            return await resp.json();
        }
        catch (err) {
            const msg = err instanceof Error ? err.message : 'Activation failed';
            setError(msg);
            return null;
        }
        finally {
            setLoading(false);
        }
    }, [apiFetch]);
    return { activate, loading, error };
}
export function useDeactivateIntegration(apiFetch) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const deactivate = useCallback(async (type) => {
        setLoading(true);
        setError(null);
        try {
            const resp = await apiFetch(`/api/admin/integrations/${type}/deactivate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({}),
            });
            if (!resp.ok) {
                const data = await resp.json().catch(() => ({}));
                throw new Error(data.detail || `${resp.status}`);
            }
            return await resp.json();
        }
        catch (err) {
            const msg = err instanceof Error ? err.message : 'Deactivation failed';
            setError(msg);
            return null;
        }
        finally {
            setLoading(false);
        }
    }, [apiFetch]);
    return { deactivate, loading, error };
}
export function useDisconnectIntegration(apiFetch) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const disconnect = useCallback(async (type) => {
        setLoading(true);
        setError(null);
        try {
            const resp = await apiFetch(`/api/admin/integrations/${type}`, {
                method: 'DELETE',
            });
            if (!resp.ok) {
                const data = await resp.json().catch(() => ({}));
                throw new Error(data.detail || `${resp.status}`);
            }
            return await resp.json();
        }
        catch (err) {
            const msg = err instanceof Error ? err.message : 'Disconnect failed';
            setError(msg);
            return null;
        }
        finally {
            setLoading(false);
        }
    }, [apiFetch]);
    return { disconnect, loading, error };
}
//# sourceMappingURL=useAdmin.js.map