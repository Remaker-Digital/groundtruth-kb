// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * useTenantDirectory — Shared hook that caches the tenant directory for
 * human-readable tenant identification across all Provider Console pages.
 *
 * SPEC-1881: Uses display_name from the API for friendly tenant labels.
 * Falls back to tenantId only when display_name is not set.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { useCallback, useEffect, useRef, useState } from 'react';

export interface TenantDisplayInfo {
  /** Human-readable display name (SPEC-1881) or tenantId fallback */
  displayName: string;
  /** True if displayName is a raw UUID (no friendly name set) */
  isUuid: boolean;
}

interface TenantSummary {
  tenantId: string;
  displayName?: string | null;
}

/**
 * Hook that maintains a cached tenant directory lookup.
 *
 * @param apiFetch - Authenticated fetch function from ProviderContext
 * @returns getTenantDisplay function and loading state
 */
export function useTenantDirectory(
  apiFetch: (path: string, init?: RequestInit) => Promise<Response>,
) {
  const [map, setMap] = useState<Map<string, TenantDisplayInfo>>(new Map());
  const [loaded, setLoaded] = useState(false);
  const fetchedRef = useRef(false);

  useEffect(() => {
    if (fetchedRef.current) return;
    fetchedRef.current = true;

    (async () => {
      try {
        const res = await apiFetch('/api/superadmin/tenants?limit=500');
        if (!res.ok) return;
        const data = await res.json();
        const tenants: TenantSummary[] = data.tenants ?? [];

        const lookup = new Map<string, TenantDisplayInfo>();
        for (const t of tenants) {
          const hasDisplayName = !!t.displayName;
          lookup.set(t.tenantId, {
            displayName: t.displayName || t.tenantId,
            isUuid: !hasDisplayName,
          });
        }
        setMap(lookup);
      } catch {
        // Silently fail — pages fall back to raw UUID
      } finally {
        setLoaded(true);
      }
    })();
  }, [apiFetch]);

  const getTenantDisplay = useCallback(
    (tenantId: string): TenantDisplayInfo => {
      return map.get(tenantId) ?? {
        displayName: tenantId,
        isUuid: true,
      };
    },
    [map],
  );

  return { getTenantDisplay, loaded };
}
