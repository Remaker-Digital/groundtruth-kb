/**
 * useTenantDirectory — Shared hook that caches the tenant directory for
 * human-readable tenant identification across all Provider Console pages.
 *
 * Fetches the tenant list once and builds a lookup map:
 *   tenantId → { displayName, customerEmail, shopifyShopDomain }
 *
 * SPEC-1569 / WI-0883: Provider Console human-readable tenant identification.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { useCallback, useEffect, useRef, useState } from 'react';

export interface TenantDisplayInfo {
  /** Best human-readable name: email → domain → tenantId */
  displayName: string;
  /** Whether displayName is just the raw UUID (no email/domain available) */
  isUuid: boolean;
  customerEmail: string | null;
  shopifyShopDomain: string | null;
}

interface TenantSummary {
  tenantId: string;
  customerEmail?: string | null;
  shopifyShopDomain?: string | null;
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
        // Fetch all tenants (up to 500 — sufficient for beta/launch scale)
        const res = await apiFetch('/api/superadmin/tenants?limit=500');
        if (!res.ok) return;
        const data = await res.json();
        const tenants: TenantSummary[] = data.tenants ?? [];

        const lookup = new Map<string, TenantDisplayInfo>();
        for (const t of tenants) {
          const email = t.customerEmail ?? null;
          const domain = t.shopifyShopDomain ?? null;
          const displayName = email || domain || t.tenantId;
          lookup.set(t.tenantId, {
            displayName,
            isUuid: displayName === t.tenantId,
            customerEmail: email,
            shopifyShopDomain: domain,
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
        customerEmail: null,
        shopifyShopDomain: null,
      };
    },
    [map],
  );

  return { getTenantDisplay, loaded };
}
