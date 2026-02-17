/**
 * Admin hooks — team management, billing, integrations.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { useState, useCallback } from 'react';
import type {
  TeamMember,
  IntegrationSummary,
  IntegrationDetail,
  IntegrationResponse,
} from '../types/index';
import { useApi } from './useApi';
import type { ApiFetch } from './useApi';

// ---------------------------------------------------------------------------
// Team hooks
// ---------------------------------------------------------------------------

export function useTeamMembers(apiFetch: ApiFetch) {
  return useApi<{ members: TeamMember[] }>(apiFetch, '/api/admin/team');
}

export function useInviteTeamMember(apiFetch: ApiFetch) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const invite = useCallback(
    async (email: string, role: string, name?: string) => {
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
        if (!resp.ok) throw new Error(`${resp.status}`);
        return await resp.json();
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Invite failed';
        setError(msg);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [apiFetch],
  );

  return { invite, loading, error };
}

// ---------------------------------------------------------------------------
// Billing hooks
// ---------------------------------------------------------------------------

export function useBillingStatus(
  apiFetch: ApiFetch,
  channel: 'shopify' | 'stripe',
  shopDomain?: string,
) {
  const path =
    channel === 'shopify'
      ? `/api/shopify/billing/status?shop=${encodeURIComponent(shopDomain || '')}`
      : '/api/billing/status';
  const enabled = channel === 'stripe' || !!shopDomain;
  return useApi<Record<string, unknown>>(apiFetch, path, enabled);
}

export function usePackBalance(apiFetch: ApiFetch, customerId: string) {
  return useApi<{ balance: number; packs: Array<Record<string, unknown>> }>(
    apiFetch,
    `/api/packs/balance/${customerId}`,
    !!customerId,
  );
}

// ---------------------------------------------------------------------------
// Integration hooks (C10)
// ---------------------------------------------------------------------------

export function useIntegrations(apiFetch: ApiFetch) {
  return useApi<IntegrationSummary[]>(apiFetch, '/api/admin/integrations');
}

export function useIntegrationDetail(apiFetch: ApiFetch, type: string) {
  return useApi<IntegrationDetail>(apiFetch, `/api/admin/integrations/${type}`, !!type);
}

export function useActivateIntegration(apiFetch: ApiFetch) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const activate = useCallback(
    async (type: string): Promise<IntegrationResponse | null> => {
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
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Activation failed';
        setError(msg);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [apiFetch],
  );

  return { activate, loading, error };
}

export function useDeactivateIntegration(apiFetch: ApiFetch) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const deactivate = useCallback(
    async (type: string): Promise<IntegrationResponse | null> => {
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
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Deactivation failed';
        setError(msg);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [apiFetch],
  );

  return { deactivate, loading, error };
}

export function useDisconnectIntegration(apiFetch: ApiFetch) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const disconnect = useCallback(
    async (type: string): Promise<IntegrationResponse | null> => {
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
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Disconnect failed';
        setError(msg);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [apiFetch],
  );

  return { disconnect, loading, error };
}
