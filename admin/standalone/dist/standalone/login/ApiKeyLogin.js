import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
/**
 * ApiKeyLogin — Authentication gate for standalone admin.
 *
 * SPEC-0429: Magic link is the PRIMARY auth method (email → link → 2FA).
 * API key login is a secondary fallback for tenants without a ?tenant= URL param.
 *
 * When ?tenant= is present: defaults to magic link view (primary per SPEC-0429).
 * When ?tenant= is absent: shows invalid URL error (tenant context required).
 *
 * Migrated to Mantine components (Cycle 10, item 10e).
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { useState, useCallback, useMemo } from 'react';
import { Anchor, Box, Button, Center, Paper, PasswordInput, Stack, Text, TextInput, ThemeIcon, Title, } from '@mantine/core';
import { Icons } from '../../shared/icons';
import { tokens } from '../../shared/theme/styles';
const API_BASE_URL = import.meta.env?.VITE_API_URL || '';
export const ApiKeyLogin = ({ onLogin, onMagicLinkLogin, verifyError, }) => {
    // SPEC-0429: Magic link is primary when tenant context is available.
    // Cache tenant ID once at mount — avoids re-reading URL at submit time
    // (SPA routing or history changes could strip query params between mount and submit).
    const tenantId = useMemo(() => {
        try {
            return new URLSearchParams(window.location.search).get('tenant') || null;
        }
        catch {
            return null;
        }
    }, []);
    const hasTenant = !!tenantId;
    const defaultView = (hasTenant && onMagicLinkLogin) ? 'magic-link' : 'login';
    const [view, setView] = useState(defaultView);
    const [apiKey, setApiKey] = useState('');
    const [email, setEmail] = useState('');
    const [magicEmail, setMagicEmail] = useState('');
    const [signInCode, setSignInCode] = useState('');
    const [error, setError] = useState(verifyError ?? null);
    const [loading, setLoading] = useState(false);
    /** Navigate back to whichever view is the "home" for this context. */
    const goHome = useCallback(() => {
        setView(defaultView);
        setError(null);
        setApiKey('');
        setMagicEmail('');
        setEmail('');
    }, [defaultView]);
    const handleLogin = useCallback(async (e) => {
        e.preventDefault();
        if (!apiKey.trim()) {
            setError('API key is required');
            return;
        }
        // SPEC-1644: API keys MUST NOT identify tenants.
        // The tenant comes from the URL; the key only authenticates.
        if (!tenantId) {
            setError('Tenant context required. Use the link from your welcome email.');
            return;
        }
        setLoading(true);
        setError(null);
        try {
            const resp = await fetch(`${API_BASE_URL}/api/tenants/auth/validate-key`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-Key': apiKey.trim(),
                },
                body: JSON.stringify({ tenant: tenantId }),
            });
            if (!resp.ok) {
                if (resp.status === 401 || resp.status === 403) {
                    setError('Invalid API key. Please check and try again.');
                }
                else {
                    setError(`Server error (${resp.status}). Please try again later.`);
                }
                return;
            }
            onLogin(apiKey.trim());
        }
        catch {
            setError('Unable to connect. Please check your network and try again.');
        }
        finally {
            setLoading(false);
        }
    }, [apiKey, tenantId, onLogin]);
    const handleReset = useCallback(async (e) => {
        e.preventDefault();
        const trimmed = email.trim();
        if (!trimmed) {
            setError('Email address is required');
            return;
        }
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trimmed)) {
            setError('Please enter a valid email address');
            return;
        }
        setLoading(true);
        setError(null);
        try {
            const resp = await fetch(`${API_BASE_URL}/api/admin/api-keys/reset`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: trimmed }),
            });
            if (resp.status === 429) {
                setError('Too many requests. Please wait a few minutes and try again.');
                return;
            }
            // Always show success (the server returns 200 regardless of email match)
            setView('reset-sent');
        }
        catch {
            setError('Unable to connect. Please check your network and try again.');
        }
        finally {
            setLoading(false);
        }
    }, [email]);
    const handleMagicLink = useCallback(async (e) => {
        e.preventDefault();
        const trimmed = magicEmail.trim();
        if (!trimmed) {
            setError('Email address is required');
            return;
        }
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trimmed)) {
            setError('Please enter a valid email address');
            return;
        }
        setLoading(true);
        setError(null);
        try {
            // SPEC-1644: The URL must identify the tenant. The ?tenant= parameter
            // is required for magic link requests (tenant-scoped authentication).
            // Uses tenantId cached at mount — not re-read from URL (which may have changed).
            if (!tenantId) {
                setError('Sign-in link requires a tenant URL. Use the link from your welcome email.');
                return;
            }
            const resp = await fetch(`${API_BASE_URL}/api/auth/magic-link/request`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: trimmed, tenant: tenantId }),
            });
            if (resp.status === 429) {
                setError('Too many requests. Please wait a few minutes and try again.');
                return;
            }
            // Always show success (the server returns 200 regardless)
            setView('magic-link-sent');
        }
        catch {
            setError('Unable to connect. Please check your network and try again.');
        }
        finally {
            setLoading(false);
        }
    }, [magicEmail]);
    // SPEC-0429 S188: Verify 6-digit sign-in code (alternative to clicking link)
    const handleCodeVerify = useCallback(async (e) => {
        e.preventDefault();
        const code = signInCode.trim();
        if (!code || code.length !== 6 || !/^\d{6}$/.test(code)) {
            setError('Please enter a valid 6-digit code.');
            return;
        }
        if (!tenantId) {
            setError('Tenant context required. Use the link from your welcome email.');
            return;
        }
        setLoading(true);
        setError(null);
        try {
            const resp = await fetch(`${API_BASE_URL}/api/auth/magic-link/verify-code`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code, tenant: tenantId }),
            });
            if (resp.status === 429) {
                setError('Too many attempts. Please wait a few minutes and try again.');
                return;
            }
            const data = await resp.json();
            if (!resp.ok) {
                setError(data.message || 'Invalid or expired code. Please request a new one.');
                return;
            }
            // Same handling as magic link verify (2FA or direct login)
            if (data.requires_2fa && data.pending_2fa_token) {
                // Trigger 2FA flow — pass through to parent
                // For now, store the pending state the same way link-verify does
                if (onMagicLinkLogin) {
                    onMagicLinkLogin(data.session_token || data.pending_2fa_token);
                }
                return;
            }
            if (data.session_token && onMagicLinkLogin) {
                onMagicLinkLogin(data.session_token);
            }
        }
        catch {
            setError('Unable to connect. Please check your network and try again.');
        }
        finally {
            setLoading(false);
        }
    }, [signInCode, tenantId, onMagicLinkLogin]);
    /* ---- Shared UI elements ---------------------------------------------- */
    const inputStyles = {
        input: {
            backgroundColor: tokens.page,
            borderColor: error ? tokens.errorLight : tokens.border,
            color: tokens.textSecondary,
            '&:focus': { borderColor: tokens.action },
        },
        label: { color: tokens.textSecondary, fontWeight: 500 },
    };
    const cardProps = {
        w: '100%',
        maw: 380,
        bg: tokens.surface,
        radius: 'md',
        p: 'xl',
        styles: { root: { border: `1px solid ${tokens.border}` } },
    };
    const brandBlock = (_jsxs(Stack, { align: "center", gap: "xs", mb: "xl", children: [_jsx("img", { src: "/admin/standalone/primary-logo-no-wordmark.svg", alt: "Agent Red", style: { width: '200px', height: 'auto' } }), _jsx(Text, { size: "sm", c: "dimmed", children: "Customer Experience Admin" })] }));
    const divider = (_jsxs(Box, { mt: "lg", mb: "sm", style: { display: 'flex', alignItems: 'center', gap: '12px' }, children: [_jsx("div", { style: { flex: 1, height: '1px', backgroundColor: tokens.border } }), _jsx(Text, { size: "xs", c: "dimmed", children: "or" }), _jsx("div", { style: { flex: 1, height: '1px', backgroundColor: tokens.border } })] }));
    /* ---- Invalid URL: no tenant context ---------------------------------- */
    if (!hasTenant) {
        return (_jsx(Center, { mih: "100vh", bg: tokens.chrome, children: _jsxs(Paper, { ...cardProps, children: [brandBlock, _jsxs(Stack, { align: "center", gap: "md", children: [_jsx(ThemeIcon, { size: 48, radius: "xl", color: "red", variant: "light", children: _jsx(Icons.alerts, { size: 24 }) }), _jsx(Title, { order: 4, ta: "center", c: tokens.textPrimary, children: "Invalid URL" }), _jsx(Text, { size: "sm", c: tokens.textSecondary, ta: "center", lh: 1.6, children: "This URL does not include a tenant identifier and cannot be used to sign in. Please use the link from your welcome email, which includes your tenant context." })] })] }) }));
    }
    /* ---- Magic link view (PRIMARY per SPEC-0429) ------------------------- */
    if (view === 'magic-link') {
        return (_jsx(Center, { mih: "100vh", bg: tokens.chrome, children: _jsxs(Paper, { ...cardProps, children: [brandBlock, _jsxs("form", { onSubmit: handleMagicLink, children: [_jsx(TextInput, { label: "Email address", type: "email", placeholder: "you@company.com", value: magicEmail, onChange: (e) => setMagicEmail(e.currentTarget.value), error: error, autoFocus: true, "aria-label": "Email address", styles: inputStyles }), _jsx(Button, { type: "submit", fullWidth: true, mt: "md", loading: loading, color: "action", "aria-label": "Send sign-in link", children: "Send sign-in link" })] }), _jsx(Text, { size: "xs", c: "dimmed", ta: "center", mt: "sm", lh: 1.5, children: "We'll email you a secure sign-in link. No password required." }), divider, _jsx(Button, { fullWidth: true, variant: "outline", color: "action", onClick: () => { setView('login'); setError(null); setApiKey(''); }, "aria-label": "Sign in with API key", children: "Sign in with API key" })] }) }));
    }
    /* ---- API key view (secondary fallback) -------------------------------- */
    if (view === 'login') {
        return (_jsx(Center, { mih: "100vh", bg: tokens.chrome, children: _jsxs(Paper, { ...cardProps, children: [brandBlock, _jsxs("form", { onSubmit: handleLogin, children: [_jsx(PasswordInput, { label: "API key", placeholder: "Enter your API key", value: apiKey, onChange: (e) => setApiKey(e.currentTarget.value), error: error, autoFocus: true, "aria-label": "API key", styles: inputStyles }), _jsx(Button, { type: "submit", fullWidth: true, mt: "md", loading: loading, color: "action", "aria-label": "Sign in", children: "Sign in" })] }), _jsx(Text, { ta: "center", mt: "lg", size: "sm", children: _jsx(Anchor, { c: tokens.action, size: "sm", component: "button", type: "button", onClick: () => { setView('reset'); setError(null); setEmail(''); }, children: "Lost your API key? Request a new one" }) }), onMagicLinkLogin && (_jsxs(_Fragment, { children: [divider, _jsx(Button, { fullWidth: true, variant: "outline", color: "action", onClick: () => { setView('magic-link'); setError(null); setMagicEmail(''); }, "aria-label": "Sign in with email", children: "Sign in with email" })] })), _jsxs(Text, { size: "xs", c: "dimmed", ta: "center", mt: "sm", lh: 1.5, children: ["Your API key was sent in your welcome email.", _jsx("br", {}), "If you need a new key, click the link above."] })] }) }));
    }
    /* ---- Reset view (enter email) ---------------------------------------- */
    if (view === 'reset') {
        return (_jsx(Center, { mih: "100vh", bg: tokens.chrome, children: _jsxs(Paper, { ...cardProps, children: [brandBlock, _jsx(Title, { order: 4, c: tokens.textPrimary, mb: 4, children: "Request new API key" }), _jsx(Text, { size: "sm", c: "dimmed", lh: 1.5, mb: "lg", children: "Enter the email address associated with your account. We'll generate a new API key and send it to you. Your previous key will be revoked." }), _jsxs("form", { onSubmit: handleReset, children: [_jsx(TextInput, { label: "Email address", type: "email", placeholder: "you@company.com", value: email, onChange: (e) => setEmail(e.currentTarget.value), error: error, autoFocus: true, "aria-label": "Email address", styles: inputStyles }), _jsx(Button, { type: "submit", fullWidth: true, mt: "md", loading: loading, color: "action", "aria-label": "Request new API key", children: "Request new API key" })] }), _jsx(Text, { ta: "center", mt: "lg", size: "sm", children: _jsx(Anchor, { c: tokens.action, size: "sm", component: "button", type: "button", onClick: goHome, children: "Back to sign in" }) })] }) }));
    }
    /* ---- Magic link sent (confirmation + code entry, SPEC-0429) ---------- */
    if (view === 'magic-link-sent') {
        return (_jsx(Center, { mih: "100vh", bg: tokens.chrome, children: _jsxs(Paper, { ...cardProps, children: [brandBlock, _jsxs(Stack, { align: "center", gap: "xs", py: "sm", children: [_jsx(ThemeIcon, { size: 48, radius: "xl", variant: "light", color: "action", "aria-hidden": true, children: _jsx(Icons.email, { size: 24 }) }), _jsx(Title, { order: 4, c: tokens.textPrimary, ta: "center", children: "Check your email" }), _jsxs(Text, { size: "sm", c: tokens.textSecondary, ta: "center", lh: 1.5, children: ["If an account with ", _jsx(Text, { span: true, fw: 600, c: tokens.textPrimary, children: magicEmail }), " exists, we've sent a sign-in code and link to that address."] }), _jsx(Text, { size: "xs", c: "dimmed", ta: "center", lh: 1.5, children: "Enter the 6-digit code from the email, or click the link. Expires in 15 minutes." })] }), _jsxs("form", { onSubmit: handleCodeVerify, children: [_jsx(TextInput, { label: "Sign-in code", placeholder: "000000", value: signInCode, onChange: (e) => {
                                    const v = e.currentTarget.value.replace(/\D/g, '').slice(0, 6);
                                    setSignInCode(v);
                                    setError(null);
                                }, error: error, maxLength: 6, autoFocus: true, autoComplete: "one-time-code", inputMode: "numeric", "aria-label": "Sign-in code", styles: {
                                    ...inputStyles,
                                    input: {
                                        ...inputStyles.input,
                                        textAlign: 'center',
                                        fontSize: '24px',
                                        fontFamily: 'monospace',
                                        letterSpacing: '8px',
                                        fontWeight: 600,
                                    },
                                } }), _jsx(Button, { type: "submit", fullWidth: true, mt: "md", loading: loading, color: "action", "aria-label": "Verify code", children: "Verify code" })] }), _jsx(Text, { ta: "center", mt: "md", size: "sm", children: _jsx(Anchor, { c: tokens.action, size: "sm", component: "button", type: "button", onClick: () => { setView('magic-link'); setError(null); setSignInCode(''); }, children: "Didn't receive it? Try again" }) })] }) }));
    }
    /* ---- Reset sent (confirmation) --------------------------------------- */
    return (_jsx(Center, { mih: "100vh", bg: tokens.chrome, children: _jsxs(Paper, { ...cardProps, children: [brandBlock, _jsxs(Stack, { align: "center", gap: "xs", py: "sm", children: [_jsx(ThemeIcon, { size: 48, radius: "xl", variant: "light", color: "action", "aria-hidden": true, children: _jsx(Icons.email, { size: 24 }) }), _jsx(Title, { order: 4, c: tokens.textPrimary, ta: "center", children: "Check your email" }), _jsxs(Text, { size: "sm", c: tokens.textSecondary, ta: "center", lh: 1.5, children: ["If an account with ", _jsx(Text, { span: true, fw: 600, c: tokens.textPrimary, children: email }), " exists, we've generated a new API key and sent it to that address."] }), _jsx(Text, { size: "xs", c: "dimmed", ta: "center", lh: 1.5, children: "Your previous API key has been revoked for security." }), _jsx(Text, { size: "xs", c: "dimmed", ta: "center", lh: 1.5, children: "The email may take a minute to arrive. Check your spam folder if you don't see it." })] }), _jsx(Button, { fullWidth: true, mt: "md", color: "action", onClick: goHome, "aria-label": "Back to sign in", children: "Back to sign in" }), _jsx(Text, { ta: "center", mt: "sm", size: "sm", children: _jsx(Anchor, { c: tokens.action, size: "sm", component: "button", type: "button", onClick: () => { setView('reset'); setError(null); }, children: "Didn't receive it? Try again" }) })] }) }));
};
//# sourceMappingURL=ApiKeyLogin.js.map