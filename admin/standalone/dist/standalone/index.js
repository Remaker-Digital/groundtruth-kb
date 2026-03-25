import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
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
import { InboxPage } from './pages/Inbox';
import { ConfigurationPage } from './pages/Configuration';
import { KnowledgeBasePage } from './pages/KnowledgeBase';
import { WidgetPage } from './pages/Widget';
import { BillingPage } from './pages/Billing';
import { TeamPage } from './pages/Team';
import { IntegrationsPage } from './pages/Integrations';
import { QuickActionsPage } from './pages/QuickActions';
import { MemoryPrivacyPage } from './pages/MemoryPrivacy';
import { ProtectedRoute } from './components/ProtectedRoute';
import { TwoFaChallenge } from './components/TwoFaChallenge';
function getStoredAuth() {
    try {
        const apiKey = sessionStorage.getItem('agentred_api_key');
        if (apiKey)
            return { type: 'api_key', value: apiKey };
        const sessionToken = sessionStorage.getItem('agentred_session_token');
        if (sessionToken)
            return { type: 'session_token', value: sessionToken };
        return null;
    }
    catch {
        return null;
    }
}
function storeApiKey(key) {
    try {
        sessionStorage.removeItem('agentred_session_token');
        sessionStorage.setItem('agentred_api_key', key);
    }
    catch {
        // sessionStorage unavailable
    }
}
function storeSessionToken(token) {
    try {
        sessionStorage.removeItem('agentred_api_key');
        sessionStorage.setItem('agentred_session_token', token);
    }
    catch {
        // sessionStorage unavailable
    }
}
function clearAuth() {
    try {
        sessionStorage.removeItem('agentred_api_key');
        sessionStorage.removeItem('agentred_session_token');
    }
    catch {
        // sessionStorage unavailable
    }
}
// ---------------------------------------------------------------------------
// App
// ---------------------------------------------------------------------------
/** Handle magic link verification from URL query params. */
function checkMagicLinkVerify() {
    try {
        const params = new URLSearchParams(window.location.search);
        const token = params.get('token');
        const path = window.location.pathname;
        if (token && path.includes('verify-magic-link')) {
            return { type: 'session_token', value: token };
        }
    }
    catch {
        // ignore
    }
    return null;
}
const App = () => {
    const [auth, setAuth] = React.useState(getStoredAuth);
    const [verifying, setVerifying] = React.useState(false);
    const [verifyError, setVerifyError] = React.useState(null);
    const [pending2fa, setPending2fa] = React.useState(null);
    // Handle magic link verification on mount
    React.useEffect(() => {
        const pending = checkMagicLinkVerify();
        if (!pending)
            return;
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
            }
            else {
                const body = await resp.json().catch(() => ({}));
                setVerifyError(body.message || 'This sign-in link is invalid or has expired.');
            }
        })
            .catch(() => {
            setVerifyError('Unable to verify sign-in link. Please check your network.');
        })
            .finally(() => setVerifying(false));
    }, []);
    const handleApiKeyLogin = React.useCallback((key) => {
        storeApiKey(key);
        setAuth({ type: 'api_key', value: key });
    }, []);
    const handleMagicLinkLogin = React.useCallback((token) => {
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
    const handle2faComplete = React.useCallback((sessionToken) => {
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
        return (_jsx("div", { style: { display: 'flex', alignItems: 'center', justifyContent: 'center',
                minHeight: '100vh', backgroundColor: tokens.chrome, color: tokens.textSecondary }, children: _jsxs("div", { style: { textAlign: 'center' }, children: [_jsx("div", { style: { fontSize: '18px', marginBottom: '8px' }, children: "Signing you in..." }), _jsx("div", { style: { fontSize: '14px', color: '#808080' }, children: "Verifying your sign-in link" })] }) }));
    }
    // 2FA challenge screen — shown after magic link verify requires 2FA
    if (pending2fa) {
        return (_jsx(TwoFaChallenge, { pendingToken: pending2fa.pendingToken, email: pending2fa.email, mfaMethods: pending2fa.mfaMethods, onComplete: handle2faComplete, onCancel: handle2faCancel }));
    }
    // Auth gate renders OUTSIDE MantineProvider — it has its own dark styling
    // SPEC-0429: Magic link is primary when ?tenant= present; API key is fallback
    if (!auth) {
        return (_jsx(ApiKeyLogin, { onLogin: handleApiKeyLogin, onMagicLinkLogin: handleMagicLinkLogin, verifyError: verifyError }));
    }
    return (_jsxs(_Fragment, { children: [_jsx(Notifications, { position: "top-right" }), _jsx(BrowserRouter, { basename: "/admin/standalone", children: _jsx(StandaloneLayout, { auth: auth, onLogout: handleLogout, children: _jsxs(Routes, { children: [_jsx(Route, { path: "/", element: _jsx(DashboardPage, {}) }), _jsx(Route, { path: "/inbox", element: _jsx(InboxPage, {}) }), _jsx(Route, { path: "/team", element: _jsx(TeamPage, {}) }), _jsx(Route, { path: "/analytics", element: _jsx(NavigateWithQuery, { to: "/", replace: true }) }), _jsx(Route, { path: "/configuration", element: _jsx(ProtectedRoute, { allowedRoles: ['superadmin', 'admin'], children: _jsx(ConfigurationPage, {}) }) }), _jsx(Route, { path: "/knowledge-base", element: _jsx(ProtectedRoute, { allowedRoles: ['superadmin', 'admin'], children: _jsx(KnowledgeBasePage, {}) }) }), _jsx(Route, { path: "/widget", element: _jsx(ProtectedRoute, { allowedRoles: ['superadmin', 'admin'], children: _jsx(WidgetPage, {}) }) }), _jsx(Route, { path: "/quick-actions", element: _jsx(ProtectedRoute, { allowedRoles: ['superadmin', 'admin'], children: _jsx(QuickActionsPage, {}) }) }), _jsx(Route, { path: "/billing", element: _jsx(ProtectedRoute, { allowedRoles: ['superadmin', 'admin'], children: _jsx(BillingPage, {}) }) }), _jsx(Route, { path: "/integrations", element: _jsx(ProtectedRoute, { allowedRoles: ['superadmin', 'admin'], children: _jsx(IntegrationsPage, {}) }) }), _jsx(Route, { path: "/memory-privacy", element: _jsx(ProtectedRoute, { allowedRoles: ['superadmin', 'admin'], children: _jsx(MemoryPrivacyPage, {}) }) }), _jsx(Route, { path: "*", element: _jsx(NavigateWithQuery, { to: "/", replace: true }) })] }) }) })] }));
};
// ---------------------------------------------------------------------------
// Mount
// ---------------------------------------------------------------------------
const root = document.getElementById('app');
if (root) {
    createRoot(root).render(_jsx(MantineProvider, { theme: agentRedTheme, defaultColorScheme: "dark", children: _jsx(App, {}) }));
}
//# sourceMappingURL=index.js.map