/**
 * ShopifyAppLayout — Polaris + App Bridge layout wrapper.
 *
 * Provides:
 *   - App Bridge initialization (session token auth)
 *   - Navigation menu via App Bridge NavMenu API
 *   - TenantContext resolution from session token
 *   - Authenticated apiFetch for shared components
 *   - Error boundary and loading states
 *
 * Architecture (Decision UI-7):
 *   Session token auth is automatic via App Bridge — no cookie-based auth.
 *   The session token is included in every API call as Bearer token.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { createContext, useCallback, useContext, useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { Frame, Loading, Banner } from '@shopify/polaris';
import type { TenantContext } from '../../shared/types';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface ShopifyConfig {
  apiKey: string;
  host: string;
  shop: string;
}

interface ShopifyAppLayoutProps {
  shopifyConfig: ShopifyConfig;
  children: React.ReactNode;
}

interface AppContextValue {
  tenantContext: TenantContext | null;
  apiFetch: (path: string, init?: RequestInit) => Promise<Response>;
  onNotify: (message: string, type: 'success' | 'error' | 'warning' | 'info') => void;
  loading: boolean;
}

// ---------------------------------------------------------------------------
// Context
// ---------------------------------------------------------------------------

const AppContext = createContext<AppContextValue | null>(null);

export function useAppContext(): AppContextValue {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useAppContext must be used within ShopifyAppLayout');
  return ctx;
}

// ---------------------------------------------------------------------------
// API base URL
// ---------------------------------------------------------------------------

const API_BASE_URL = import.meta.env.VITE_API_URL || '';
const STANDALONE_ADMIN_URL = `${API_BASE_URL || ''}/admin/standalone/`;
const DOCS_URL = 'https://agentredcx.com';

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export const ShopifyAppLayout: React.FC<ShopifyAppLayoutProps> = ({
  shopifyConfig,
  children,
}) => {
  const location = useLocation();
  const [tenantContext, setTenantContext] = useState<TenantContext | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [notification, setNotification] = useState<{
    message: string;
    type: 'success' | 'error' | 'warning' | 'info';
  } | null>(null);

  // ---- Session token retrieval -------------------------------------------

  const getSessionToken = useCallback(async (): Promise<string> => {
    // In Shopify embedded apps, shopify.idToken() provides the session token.
    // This is the App Bridge 4.x pattern (replaces getSessionToken from 3.x).
    try {
      const shopify = (window as unknown as { shopify?: { idToken: () => Promise<string> } }).shopify;
      if (shopify?.idToken) {
        return await shopify.idToken();
      }
    } catch (e) {
      console.error('[AgentRed] App Bridge idToken() failed:', e);
    }
    throw new Error('Shopify App Bridge not available — this app must be opened from the Shopify admin.');
  }, []);

  // ---- Authenticated fetch -----------------------------------------------

  const apiFetch = useCallback(
    async (path: string, init?: RequestInit): Promise<Response> => {
      const token = await getSessionToken();
      const headers = new Headers(init?.headers);
      headers.set('Authorization', `Bearer ${token}`);
      headers.set('X-Shopify-Shop', shopifyConfig.shop);

      return fetch(`${API_BASE_URL}${path}`, {
        ...init,
        headers,
      });
    },
    [getSessionToken, shopifyConfig.shop],
  );

  // ---- Notification handler ----------------------------------------------

  const onNotify = useCallback(
    (message: string, type: 'success' | 'error' | 'warning' | 'info') => {
      setNotification({ message, type });
      // Auto-dismiss after 5 seconds
      setTimeout(() => setNotification(null), 5000);
    },
    [],
  );

  // ---- Tenant context resolution -----------------------------------------

  useEffect(() => {
    let cancelled = false;

    async function resolveTenant() {
      try {
        const shop = shopifyConfig.shop || '';
        if (!shop) {
          throw new Error('Shop domain not found — this app must be opened from the Shopify admin.');
        }

        // Try authenticated fetch first, fall back to unauthenticated lookup
        let resp: Response;
        try {
          resp = await apiFetch(`/api/tenants/lookup?shop=${encodeURIComponent(shop)}`);
        } catch {
          // App Bridge may not be available (e.g. during initial load) —
          // tenant lookup is auth-exempt, so try without auth
          resp = await fetch(`${API_BASE_URL}/api/tenants/lookup?shop=${encodeURIComponent(shop)}`);
        }

        if (!resp.ok) throw new Error(`Tenant lookup failed: ${resp.status}`);
        const data = await resp.json();
        if (!data.found) throw new Error(`Store "${shop}" is not registered with Agent Red.`);

        if (!cancelled) {
          setTenantContext({
            tenantId: data.tenant_id,
            tier: data.tier,
            status: data.status,
            billingChannel: 'shopify',
            shopDomain: shopifyConfig.shop,
          });
          setLoading(false);
        }
      } catch (err) {
        console.error('[AgentRed] Tenant resolution failed:', err);
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load tenant');
          setLoading(false);
        }
      }
    }

    resolveTenant();
    return () => { cancelled = true; };
  }, [apiFetch, shopifyConfig.shop]);

  // ---- Navigation menu (App Bridge) --------------------------------------

  useEffect(() => {
    // App Bridge 4.x navigation via shopify.navigation
    const shopify = (window as unknown as {
      shopify?: {
        navigation?: {
          dispatch: (action: string, payload: unknown) => void;
        };
      };
    }).shopify;

    if (shopify?.navigation) {
      // Register navigation items
      const navItems = [
        { label: 'Dashboard', destination: '/' },
        { label: 'Inbox', destination: '/inbox' },
        { label: 'Configuration', destination: '/configuration' },
        { label: 'Knowledge Base', destination: '/knowledge-base' },
        { label: 'Widget', destination: '/widget' },
        { label: 'Billing', destination: '/billing' },
        { label: 'Settings', destination: '/settings' },
      ];

      // Set active item based on current location
      const active = navItems.find((item) => item.destination === location.pathname);
      if (active) {
        shopify.navigation.dispatch('UPDATE', {
          items: navItems,
          active: active.destination,
        });
      }
    }
  }, [location.pathname]);

  // ---- Render ------------------------------------------------------------

  const contextValue: AppContextValue = {
    tenantContext,
    apiFetch,
    onNotify,
    loading,
  };

  return (
    <AppContext.Provider value={contextValue}>
      <Frame>
        {loading && <Loading />}

        {notification && (
          <div style={{ padding: '16px' }}>
            <Banner
              tone={
                notification.type === 'error' ? 'critical' :
                notification.type === 'warning' ? 'warning' :
                notification.type === 'success' ? 'success' : 'info'
              }
              onDismiss={() => setNotification(null)}
            >
              <p>{notification.message}</p>
            </Banner>
          </div>
        )}

        {error && (
          <div style={{ padding: '16px' }}>
            <Banner tone="critical">
              <p>{error}</p>
              <p style={{ marginTop: '8px', fontSize: '13px' }}>
                If you are seeing this outside of Shopify Admin, open your app from
                Shopify Admin → Apps → Agent Red Customer Experience.
              </p>
            </Banner>
          </div>
        )}

        {!loading && !error && (
          <>
            {/* Cross-navigation: standalone admin + docs */}
            <div style={{
              display: 'flex',
              justifyContent: 'flex-end',
              gap: 12,
              padding: '8px 16px 0',
              fontSize: 13,
            }}>
              <a
                href={DOCS_URL}
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: '#2c6ecb', textDecoration: 'none' }}
              >
                Documentation ↗
              </a>
              <a
                href={STANDALONE_ADMIN_URL}
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: '#2c6ecb', textDecoration: 'none' }}
              >
                Open full admin ↗
              </a>
            </div>
            {children}
          </>
        )}
      </Frame>
    </AppContext.Provider>
  );
};
