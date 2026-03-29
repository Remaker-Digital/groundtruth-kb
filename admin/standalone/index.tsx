/**
 * Standalone Admin Shell — entry point.
 *
 * This is the main entry for Stripe-direct (non-Shopify) merchants.
 * It provides:
 *   1. Auth gate — magic link primary, API key fallback (SPEC-0429)
 *   2. MantineProvider with Agent Red brand theme (dark mode default)
 *   3. Mantine AppShell layout with sidebar navigation
 *   4. Routes to 9 admin pages using prototype Mantine components
 *   5. Authenticated apiFetch via API key or session token header
 *
 * Architecture (Decision UI-7):
 *   Standalone admin is required because Stripe-direct merchants
 *   have no Shopify account and cannot access the embedded admin.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { NavigateWithQuery } from './components/NavigateWithQuery';
import { MantineProvider } from '@mantine/core';
import { Notifications } from '@mantine/notifications';

import '@mantine/core/styles.css';
import '@mantine/notifications/styles.css';
import '../shared/theme/tokens.css';
import { tokens } from '../shared/theme/styles';

import { agentRedTheme } from '../shared/theme/agentRedTheme';
import { StandaloneLayout } from './layouts/StandaloneLayout';
import { ApiKeyLogin } from './login/ApiKeyLogin';
import { DashboardPage } from './pages/Dashboard';
import { AnalyticsPage } from './pages/Analytics';
import { InboxPage } from './pages/Inbox';

import { ConfigurationPage } from './pages/Configuration';
import { KnowledgeBasePage } from './pages/KnowledgeBase';
import { WidgetPage } from './pages/Widget';
import { BillingPage } from './pages/Billing';
import { TeamPage } from './pages/Team';
import { IntegrationsPage } from './pages/Integrations';
import { QuickActionsPage } from './pages/QuickActions';
import { MemoryPrivacyPage } from './pages/MemoryPrivacy';
import { AgentsPage } from './pages/Agents';
import { ProtectedRoute } from './components/ProtectedRoute';
import { TwoFaChallenge } from './components/TwoFaChallenge';

// ---------------------------------------------------------------------------
// Auth state
// ---------------------------------------------------------------------------

/** Auth credential — either an API key or a magic link session token. */
interface AuthCredential {
  type: 'api_key' | 'session_token';
  value: string;
}

/** Pending 2FA state — returned when magic link verify requires 2FA. */
interface Pending2faState {
  pendingToken: string;
  tenantId: string;
  email: string;
  mfaMethods: string[];
}

function getStoredAuth(): AuthCredential | null {
  try {
    const apiKey = sessionStorage.getItem('agentred_api_key');
    if (apiKey) return { type: 'api_key', value: apiKey };
    const sessionToken = sessionStorage.getItem('agentred_session_token');
    if (sessionToken) return { type: 'session_token', value: sessionToken };
    return null;
  } catch {
    return null;
  }
}

function storeApiKey(key: string): void {
  try {
    sessionStorage.removeItem('agentred_session_token');
    sessionStorage.setItem('agentred_api_key', key);
  } catch {
    // sessionStorage unavailable
  }
}

function storeSessionToken(token: string): void {
  try {
    sessionStorage.removeItem('agentred_api_key');
    sessionStorage.setItem('agentred_session_token', token);
  } catch {
    // sessionStorage unavailable
  }
}

function clearAuth(): void {
  try {
    sessionStorage.removeItem('agentred_api_key');
    sessionStorage.removeItem('agentred_session_token');
  } catch {
    // sessionStorage unavailable
  }
}

// ---------------------------------------------------------------------------
// App
// ---------------------------------------------------------------------------

/** Handle magic link verification from URL query params. */
function checkMagicLinkVerify(): AuthCredential | null {
  try {
    const params = new URLSearchParams(window.location.search);
    const token = params.get('token');
    const path = window.location.pathname;
    if (token && path.includes('verify-magic-link')) {
      return { type: 'session_token', value: token };
    }
  } catch {
    // ignore
  }
  return null;
}

const App: React.FC = () => {
  const [auth, setAuth] = React.useState<AuthCredential | null>(getStoredAuth);
  const [verifying, setVerifying] = React.useState(false);
  const [verifyError, setVerifyError] = React.useState<string | null>(null);
  const [pending2fa, setPending2fa] = React.useState<Pending2faState | null>(null);

  // Handle magic link verification on mount
  React.useEffect(() => {
    const pending = checkMagicLinkVerify();
    if (!pending) return;
    setVerifying(true);
    const API_BASE_URL = import.meta.env?.VITE_API_URL || '';
    fetch(`${API_BASE_URL}/api/auth/magic-link/verify?token=${encodeURIComponent(pending.value)}`)
      .then(async (resp) => {
        if (resp.ok) {
          const data = await resp.json();

          // Two-stage auth: 2FA required for admin roles
          // Preserve ?tenant= while cleaning magic link params
          const _tenant = new URLSearchParams(window.location.search).get('tenant');
          const _cleanUrl = '/admin/standalone/' + (_tenant ? `?tenant=${_tenant}` : '');

          if (data.requires_2fa && data.pending_2fa_token) {
            setPending2fa({
              pendingToken: data.pending_2fa_token,
              tenantId: data.tenant_id,
              email: data.email,
              mfaMethods: data.mfa_methods || ['totp'],
            });
            window.history.replaceState({}, '', _cleanUrl);
            return;
          }

          storeSessionToken(data.session_token);
          setAuth({ type: 'session_token', value: data.session_token });
          // Clean URL (preserve tenant param for SPEC-1654)
          window.history.replaceState({}, '', _cleanUrl);
        } else {
          const body = await resp.json().catch(() => ({}));
          setVerifyError(body.message || 'This sign-in link is invalid or has expired.');
        }
      })
      .catch(() => {
        setVerifyError('Unable to verify sign-in link. Please check your network.');
      })
      .finally(() => setVerifying(false));
  }, []);

  const handleApiKeyLogin = React.useCallback((key: string) => {
    storeApiKey(key);
    setAuth({ type: 'api_key', value: key });
  }, []);

  const handleMagicLinkLogin = React.useCallback((token: string) => {
    storeSessionToken(token);
    setAuth({ type: 'session_token', value: token });
  }, []);

  const handleLogout = React.useCallback(() => {
    clearAuth();
    setAuth(null);
    setVerifyError(null);
    setPending2fa(null);
  }, []);

  /** Called when 2FA challenge succeeds — receives the full session token. */
  const handle2faComplete = React.useCallback((sessionToken: string) => {
    storeSessionToken(sessionToken);
    setAuth({ type: 'session_token', value: sessionToken });
    setPending2fa(null);
  }, []);

  /** Cancel 2FA — go back to login. */
  const handle2faCancel = React.useCallback(() => {
    setPending2fa(null);
  }, []);

  // Show verifying state while checking magic link
  if (verifying) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center',
        minHeight: '100vh', backgroundColor: tokens.chrome, color: tokens.textSecondary }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '18px', marginBottom: '8px' }}>Signing you in...</div>
          <div style={{ fontSize: '14px', color: '#808080' }}>Verifying your sign-in link</div>
        </div>
      </div>
    );
  }

  // 2FA challenge screen — shown after magic link verify requires 2FA
  if (pending2fa) {
    return (
      <TwoFaChallenge
        pendingToken={pending2fa.pendingToken}
        email={pending2fa.email}
        mfaMethods={pending2fa.mfaMethods}
        onComplete={handle2faComplete}
        onCancel={handle2faCancel}
      />
    );
  }

  // Auth gate renders OUTSIDE MantineProvider — it has its own dark styling
  // SPEC-0429: Magic link is primary when ?tenant= present; API key is fallback
  if (!auth) {
    return (
      <ApiKeyLogin
        onLogin={handleApiKeyLogin}
        onMagicLinkLogin={handleMagicLinkLogin}
        verifyError={verifyError}
      />
    );
  }

  return (
    <>
      <Notifications position="top-right" />
      <BrowserRouter basename="/admin/standalone">
        <StandaloneLayout auth={auth} onLogout={handleLogout}>
          <Routes>
            {/* Open to all roles */}
            <Route path="/" element={<DashboardPage />} />
            <Route path="/inbox" element={<InboxPage />} />
            <Route path="/team" element={<TeamPage />} />
            <Route path="/analytics" element={<AnalyticsPage />} />

            {/* Admin-only routes */}
            <Route path="/agents" element={
              <ProtectedRoute allowedRoles={['superadmin', 'admin']}>
                <AgentsPage />
              </ProtectedRoute>
            } />
            <Route path="/configuration" element={
              <ProtectedRoute allowedRoles={['superadmin', 'admin']}>
                <ConfigurationPage />
              </ProtectedRoute>
            } />
            <Route path="/knowledge-base" element={
              <ProtectedRoute allowedRoles={['superadmin', 'admin']}>
                <KnowledgeBasePage />
              </ProtectedRoute>
            } />
            <Route path="/widget" element={
              <ProtectedRoute allowedRoles={['superadmin', 'admin']}>
                <WidgetPage />
              </ProtectedRoute>
            } />
            <Route path="/quick-actions" element={
              <ProtectedRoute allowedRoles={['superadmin', 'admin']}>
                <QuickActionsPage />
              </ProtectedRoute>
            } />
            <Route path="/billing" element={
              <ProtectedRoute allowedRoles={['superadmin', 'admin']}>
                <BillingPage />
              </ProtectedRoute>
            } />
            <Route path="/integrations" element={
              <ProtectedRoute allowedRoles={['superadmin', 'admin']}>
                <IntegrationsPage />
              </ProtectedRoute>
            } />
            <Route path="/memory-privacy" element={
              <ProtectedRoute allowedRoles={['superadmin', 'admin']}>
                <MemoryPrivacyPage />
              </ProtectedRoute>
            } />
            <Route path="*" element={<NavigateWithQuery to="/" replace />} />
          </Routes>
        </StandaloneLayout>
      </BrowserRouter>
    </>
  );
};

// ---------------------------------------------------------------------------
// Mount
// ---------------------------------------------------------------------------

const root = document.getElementById('app');
if (root) {
  createRoot(root).render(
    <MantineProvider theme={agentRedTheme} defaultColorScheme="dark">
      <App />
    </MantineProvider>,
  );
}
