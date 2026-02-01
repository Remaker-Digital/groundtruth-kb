/**
 * StandaloneLayout — custom layout with sidebar navigation.
 *
 * Provides:
 *   - Agent Red branded sidebar with navigation links
 *   - Authenticated apiFetch via API key header
 *   - TenantContext resolution from API key
 *   - Notification banner system
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { createContext, useCallback, useContext, useEffect, useState } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import type { TenantContext } from '../../shared/types';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface StandaloneLayoutProps {
  apiKey: string;
  onLogout: () => void;
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
  if (!ctx) throw new Error('useAppContext must be used within StandaloneLayout');
  return ctx;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const API_BASE_URL = import.meta.env?.VITE_API_URL || '';

const BRAND_COLOR = '#C41E2A';
const SIDEBAR_WIDTH = 240;

const NAV_ITEMS = [
  { path: '/', label: 'Dashboard', icon: '\u{1F4CA}' },
  { path: '/inbox', label: 'Inbox', icon: '\u{1F4E8}' },
  { path: '/configuration', label: 'Configuration', icon: '\u{2699}\u{FE0F}' },
  { path: '/knowledge-base', label: 'Knowledge Base', icon: '\u{1F4DA}' },
  { path: '/widget', label: 'Widget', icon: '\u{1F4AC}' },
  { path: '/billing', label: 'Billing', icon: '\u{1F4B3}' },
  { path: '/settings', label: 'Settings', icon: '\u{1F527}' },
];

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export const StandaloneLayout: React.FC<StandaloneLayoutProps> = ({
  apiKey,
  onLogout,
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

  // ---- Authenticated fetch -----------------------------------------------

  const apiFetch = useCallback(
    async (path: string, init?: RequestInit): Promise<Response> => {
      const headers = new Headers(init?.headers);
      headers.set('X-API-Key', apiKey);

      return fetch(`${API_BASE_URL}${path}`, {
        ...init,
        headers,
      });
    },
    [apiKey],
  );

  // ---- Notification handler ----------------------------------------------

  const onNotify = useCallback(
    (message: string, type: 'success' | 'error' | 'warning' | 'info') => {
      setNotification({ message, type });
      setTimeout(() => setNotification(null), 5000);
    },
    [],
  );

  // ---- Tenant context resolution -----------------------------------------

  useEffect(() => {
    let cancelled = false;

    async function resolveTenant() {
      try {
        const resp = await apiFetch('/api/tenants/lookup');
        if (!resp.ok) {
          if (resp.status === 401 || resp.status === 403) {
            onLogout();
            return;
          }
          throw new Error(`Tenant lookup failed: ${resp.status}`);
        }
        const data = await resp.json();
        if (!cancelled) {
          setTenantContext({
            tenantId: data.tenant_id,
            tier: data.tier,
            status: data.status,
            billingChannel: 'stripe',
          });
          setLoading(false);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load');
          setLoading(false);
        }
      }
    }

    resolveTenant();
    return () => { cancelled = true; };
  }, [apiFetch, onLogout]);

  // ---- Notification colors -----------------------------------------------

  const notifColors: Record<string, { bg: string; border: string; text: string }> = {
    success: { bg: '#f1f8f5', border: '#2e7d32', text: '#1b5e20' },
    error: { bg: '#fef2f2', border: '#d72c0d', text: '#c62828' },
    warning: { bg: '#fffbeb', border: '#f59e0b', text: '#92400e' },
    info: { bg: '#eff6ff', border: '#3b82f6', text: '#1e40af' },
  };

  // ---- Render ------------------------------------------------------------

  const contextValue: AppContextValue = {
    tenantContext,
    apiFetch,
    onNotify,
    loading,
  };

  return (
    <AppContext.Provider value={contextValue}>
      <div style={{ display: 'flex', minHeight: '100vh', fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif' }}>
        {/* Sidebar */}
        <aside
          style={{
            width: `${SIDEBAR_WIDTH}px`,
            backgroundColor: '#1a1a2e',
            color: '#ffffff',
            display: 'flex',
            flexDirection: 'column',
            flexShrink: 0,
          }}
        >
          {/* Brand */}
          <div style={{ padding: '20px 16px', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div
                style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '8px',
                  backgroundColor: BRAND_COLOR,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '14px',
                  fontWeight: 700,
                }}
              >
                AR
              </div>
              <div>
                <div style={{ fontSize: '14px', fontWeight: 600 }}>Agent Red</div>
                <div style={{ fontSize: '11px', opacity: 0.6 }}>Customer Experience</div>
              </div>
            </div>
          </div>

          {/* Nav Links */}
          <nav style={{ flex: 1, padding: '8px 0' }}>
            {NAV_ITEMS.map((item) => {
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '10px',
                    padding: '10px 16px',
                    fontSize: '14px',
                    color: isActive ? '#ffffff' : 'rgba(255,255,255,0.7)',
                    backgroundColor: isActive ? 'rgba(255,255,255,0.1)' : 'transparent',
                    textDecoration: 'none',
                    borderLeft: isActive ? `3px solid ${BRAND_COLOR}` : '3px solid transparent',
                    transition: 'all 0.15s',
                  }}
                >
                  <span style={{ fontSize: '16px', width: '20px', textAlign: 'center' }}>
                    {item.icon}
                  </span>
                  {item.label}
                </Link>
              );
            })}
          </nav>

          {/* Tier badge + Logout */}
          <div style={{ padding: '16px', borderTop: '1px solid rgba(255,255,255,0.1)' }}>
            {tenantContext && (
              <div
                style={{
                  fontSize: '11px',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em',
                  opacity: 0.6,
                  marginBottom: '12px',
                }}
              >
                {tenantContext.tier} tier
              </div>
            )}
            <button
              onClick={onLogout}
              style={{
                width: '100%',
                padding: '8px',
                backgroundColor: 'rgba(255,255,255,0.1)',
                color: 'rgba(255,255,255,0.8)',
                border: 'none',
                borderRadius: '4px',
                fontSize: '13px',
                cursor: 'pointer',
              }}
            >
              Sign Out
            </button>
          </div>
        </aside>

        {/* Main content */}
        <main style={{ flex: 1, backgroundColor: '#f6f6f7', overflow: 'auto' }}>
          {/* Notification banner */}
          {notification && (
            <div
              style={{
                padding: '12px 20px',
                backgroundColor: notifColors[notification.type].bg,
                borderBottom: `2px solid ${notifColors[notification.type].border}`,
                color: notifColors[notification.type].text,
                fontSize: '14px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}
            >
              <span>{notification.message}</span>
              <button
                onClick={() => setNotification(null)}
                style={{
                  background: 'none',
                  border: 'none',
                  fontSize: '16px',
                  cursor: 'pointer',
                  color: 'inherit',
                  padding: '0 4px',
                }}
              >
                x
              </button>
            </div>
          )}

          {/* Error state */}
          {error && (
            <div style={{ padding: '20px', color: '#d72c0d' }}>
              Failed to load: {error}
            </div>
          )}

          {/* Loading state */}
          {loading && (
            <div style={{ padding: '40px', textAlign: 'center', color: '#8c9196' }}>
              Loading...
            </div>
          )}

          {/* Page content */}
          {!loading && !error && (
            <div style={{ padding: '24px' }}>
              {children}
            </div>
          )}
        </main>
      </div>
    </AppContext.Provider>
  );
};
