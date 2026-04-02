/**
 * Marketplace hooks — SPEC-1865.
 *
 * useMarketplace: list peer agents available for install.
 * useInstallAgent / useUninstallAgent: mutate install state.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { useCallback, useState } from 'react';
import { useApi } from './useApi';
import type { ApiFetch } from './useApi';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface MarketplaceAgent {
  agentId: string;
  displayName: string;
  description: string;
  category: string;
  tierGate: string;
  capabilities: string[];
  skillCount: number;
  installed: boolean;
}

interface MarketplaceListResponse {
  total: number;
  agents: MarketplaceAgent[];
}

interface InstallResult {
  agentId: string;
  overlayCreated: boolean;
  bindingsCreated: number;
  bindingsFailed: number;
}

interface UninstallResult {
  agentId: string;
  overlayRemoved: boolean;
  bindingsRemoved: number;
}

// ---------------------------------------------------------------------------
// Read hooks
// ---------------------------------------------------------------------------

export function useMarketplace(apiFetch: ApiFetch, category?: string) {
  const path = category
    ? `/api/admin/marketplace?category=${encodeURIComponent(category)}`
    : '/api/admin/marketplace';
  return useApi<MarketplaceListResponse>(apiFetch, path);
}

// ---------------------------------------------------------------------------
// Write hooks
// ---------------------------------------------------------------------------

export function useInstallAgent(apiFetch: ApiFetch) {
  const [loading, setLoading] = useState(false);

  const install = useCallback(
    async (agentId: string): Promise<InstallResult> => {
      setLoading(true);
      try {
        const res = await apiFetch(
          `/api/admin/marketplace/${encodeURIComponent(agentId)}/install`,
          { method: 'POST' },
        );
        if (!res.ok) {
          const err = await res.json().catch(() => ({ detail: res.statusText }));
          throw new Error(err.detail || 'Install failed');
        }
        return await res.json();
      } finally {
        setLoading(false);
      }
    },
    [apiFetch],
  );

  return { install, loading };
}

export function useUninstallAgent(apiFetch: ApiFetch) {
  const [loading, setLoading] = useState(false);

  const uninstall = useCallback(
    async (agentId: string): Promise<UninstallResult> => {
      setLoading(true);
      try {
        const res = await apiFetch(
          `/api/admin/marketplace/${encodeURIComponent(agentId)}/install`,
          { method: 'DELETE' },
        );
        if (!res.ok) {
          const err = await res.json().catch(() => ({ detail: res.statusText }));
          throw new Error(err.detail || 'Uninstall failed');
        }
        return await res.json();
      } finally {
        setLoading(false);
      }
    },
    [apiFetch],
  );

  return { uninstall, loading };
}
