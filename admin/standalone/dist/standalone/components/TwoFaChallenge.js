import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * TwoFaChallenge — 2FA verification screen for admin magic link flow.
 *
 * Shown after magic link verification when the backend returns
 * requires_2fa: true. Supports three 2FA methods:
 *   1. TOTP (authenticator app) — 6-digit code
 *   2. Backup code — 8-character recovery code
 *   3. SMS OTP — 6-digit code sent to verified phone
 *
 * On successful verification, calls onComplete(session_token).
 * On cancel, returns to the login screen.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { useState, useCallback } from 'react';
import { Anchor, Button, Center, Paper, PinInput, Stack, Text, TextInput, ThemeIcon, Title, } from '@mantine/core';
import { Icons } from '../../shared/icons';
import { tokens } from '../../shared/theme/styles';
const API_BASE_URL = import.meta.env?.VITE_API_URL || '';
export const TwoFaChallenge = ({ pendingToken, email, mfaMethods, onComplete, onCancel, }) => {
    const hasSms = mfaMethods.includes('sms');
    const [view, setView] = useState('totp');
    const [code, setCode] = useState('');
    const [backupCode, setBackupCode] = useState('');
    const [smsCode, setSmsCode] = useState('');
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    const [phoneHint, setPhoneHint] = useState(null);
    /* ---- Shared UI -------------------------------------------------------- */
    const cardProps = {
        w: '100%',
        maw: 400,
        bg: tokens.surface,
        radius: 'md',
        p: 'xl',
        styles: { root: { border: `1px solid ${tokens.border}` } },
    };
    const brandBlock = (_jsx(Stack, { align: "center", gap: "xs", mb: "lg", children: _jsx("img", { src: "/admin/standalone/primary-logo-no-wordmark.svg", alt: "Agent Red", style: { width: '160px', height: 'auto' } }) }));
    /* ---- API calls -------------------------------------------------------- */
    const verifyTotp = useCallback(async (totpCode) => {
        if (totpCode.length !== 6) {
            setError('Enter a 6-digit code');
            return;
        }
        setLoading(true);
        setError(null);
        try {
            const resp = await fetch(`${API_BASE_URL}/api/auth/2fa/totp/verify`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ pending_token: pendingToken, code: totpCode }),
            });
            const data = await resp.json();
            if (resp.ok && data.session_token) {
                onComplete(data.session_token);
            }
            else if (resp.status === 429) {
                setError('Too many attempts. Please request a new sign-in link.');
            }
            else {
                setError(data.message || 'Invalid code. Please try again.');
            }
        }
        catch {
            setError('Unable to verify. Please check your network.');
        }
        finally {
            setLoading(false);
        }
    }, [pendingToken, onComplete]);
    const verifyBackup = useCallback(async () => {
        const trimmed = backupCode.trim();
        if (!trimmed) {
            setError('Enter your backup code');
            return;
        }
        setLoading(true);
        setError(null);
        try {
            const resp = await fetch(`${API_BASE_URL}/api/auth/2fa/totp/backup-verify`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ pending_token: pendingToken, code: trimmed }),
            });
            const data = await resp.json();
            if (resp.ok && data.session_token) {
                onComplete(data.session_token);
            }
            else if (resp.status === 429) {
                setError('Too many attempts. Please request a new sign-in link.');
            }
            else {
                setError(data.message || 'Invalid backup code. Please try again.');
            }
        }
        catch {
            setError('Unable to verify. Please check your network.');
        }
        finally {
            setLoading(false);
        }
    }, [pendingToken, backupCode, onComplete]);
    const requestSms = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const resp = await fetch(`${API_BASE_URL}/api/auth/2fa/sms/request`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ pending_token: pendingToken }),
            });
            const data = await resp.json();
            if (resp.ok) {
                setPhoneHint(data.phone_hint || null);
                setView('sms-sent');
            }
            else {
                setError(data.message || 'Unable to send SMS. Try TOTP instead.');
            }
        }
        catch {
            setError('Unable to send SMS. Please check your network.');
        }
        finally {
            setLoading(false);
        }
    }, [pendingToken]);
    const verifySms = useCallback(async (smsOtp) => {
        if (smsOtp.length !== 6) {
            setError('Enter a 6-digit code');
            return;
        }
        setLoading(true);
        setError(null);
        try {
            const resp = await fetch(`${API_BASE_URL}/api/auth/2fa/sms/verify`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ pending_token: pendingToken, code: smsOtp }),
            });
            const data = await resp.json();
            if (resp.ok && data.session_token) {
                onComplete(data.session_token);
            }
            else if (resp.status === 429) {
                setError('Too many attempts. Please request a new sign-in link.');
            }
            else {
                setError(data.message || 'Invalid code. Please try again.');
            }
        }
        catch {
            setError('Unable to verify. Please check your network.');
        }
        finally {
            setLoading(false);
        }
    }, [pendingToken, onComplete]);
    /* ---- TOTP challenge view ---------------------------------------------- */
    if (view === 'totp') {
        return (_jsx(Center, { mih: "100vh", bg: tokens.chrome, children: _jsxs(Paper, { ...cardProps, children: [brandBlock, _jsxs(Stack, { align: "center", gap: 4, mb: "lg", children: [_jsx(ThemeIcon, { size: 40, radius: "xl", variant: "light", color: "action", "aria-hidden": true, children: _jsx(Icons.mfa, { size: 20 }) }), _jsx(Title, { order: 4, c: tokens.textPrimary, ta: "center", children: "Two-factor authentication" }), _jsx(Text, { size: "sm", c: tokens.textSecondary, ta: "center", lh: 1.5, children: "Enter the 6-digit code from your authenticator app" })] }), _jsx(Center, { children: _jsx(PinInput, { length: 6, type: "number", autoFocus: true, size: "lg", value: code, onChange: (val) => { setCode(val); setError(null); }, onComplete: (val) => verifyTotp(val), error: !!error, styles: {
                                input: {
                                    backgroundColor: tokens.page,
                                    borderColor: error ? tokens.errorLight : tokens.border,
                                    color: tokens.textPrimary,
                                    fontSize: '20px',
                                    fontWeight: 600,
                                },
                            } }) }), error && (_jsx(Text, { size: "sm", c: tokens.errorLight, ta: "center", mt: "sm", children: error })), _jsx(Button, { fullWidth: true, mt: "lg", loading: loading, color: "action", onClick: () => verifyTotp(code), "aria-label": "Verify code", children: "Verify" }), _jsxs(Stack, { align: "center", gap: 4, mt: "lg", children: [_jsx(Anchor, { c: tokens.action, size: "sm", component: "button", type: "button", onClick: () => { setView('backup'); setError(null); setBackupCode(''); }, children: "Use a backup code instead" }), hasSms && (_jsx(Anchor, { c: tokens.action, size: "sm", component: "button", type: "button", onClick: () => { setError(null); requestSms(); }, children: "Send code via SMS" })), _jsx(Anchor, { c: "dimmed", size: "xs", component: "button", type: "button", onClick: onCancel, children: "Cancel and return to sign in" })] })] }) }));
    }
    /* ---- Backup code view ------------------------------------------------- */
    if (view === 'backup') {
        return (_jsx(Center, { mih: "100vh", bg: tokens.chrome, children: _jsxs(Paper, { ...cardProps, children: [brandBlock, _jsxs(Stack, { align: "center", gap: 4, mb: "lg", children: [_jsx(ThemeIcon, { size: 40, radius: "xl", variant: "light", color: "action", "aria-hidden": true, children: _jsx(Icons.secrets, { size: 20 }) }), _jsx(Title, { order: 4, c: tokens.textPrimary, ta: "center", children: "Backup code" }), _jsx(Text, { size: "sm", c: tokens.textSecondary, ta: "center", lh: 1.5, children: "Enter one of your 8-character recovery codes" })] }), _jsxs("form", { onSubmit: (e) => { e.preventDefault(); verifyBackup(); }, children: [_jsx(TextInput, { placeholder: "ABCD1234", value: backupCode, onChange: (e) => { setBackupCode(e.currentTarget.value); setError(null); }, error: error, autoFocus: true, "aria-label": "Backup code", styles: {
                                    input: {
                                        backgroundColor: tokens.page,
                                        borderColor: error ? tokens.errorLight : tokens.border,
                                        color: tokens.textPrimary,
                                        fontFamily: 'monospace',
                                        fontSize: '18px',
                                        letterSpacing: '2px',
                                        textAlign: 'center',
                                    },
                                } }), _jsx(Button, { type: "submit", fullWidth: true, mt: "md", loading: loading, color: "action", "aria-label": "Verify backup code", children: "Verify backup code" })] }), _jsxs(Stack, { align: "center", gap: 4, mt: "lg", children: [_jsx(Anchor, { c: tokens.action, size: "sm", component: "button", type: "button", onClick: () => { setView('totp'); setError(null); setCode(''); }, children: "Use authenticator app instead" }), _jsx(Anchor, { c: "dimmed", size: "xs", component: "button", type: "button", onClick: onCancel, children: "Cancel and return to sign in" })] })] }) }));
    }
    /* ---- SMS sent view ---------------------------------------------------- */
    return (_jsx(Center, { mih: "100vh", bg: tokens.chrome, children: _jsxs(Paper, { ...cardProps, children: [brandBlock, _jsxs(Stack, { align: "center", gap: 4, mb: "lg", children: [_jsx(ThemeIcon, { size: 40, radius: "xl", variant: "light", color: "action", "aria-hidden": true, children: _jsx(Icons.contact, { size: 20 }) }), _jsx(Title, { order: 4, c: tokens.textPrimary, ta: "center", children: "Verify your phone" }), _jsxs(Text, { size: "sm", c: tokens.textSecondary, ta: "center", lh: 1.5, children: ["We sent a 6-digit code to", ' ', _jsx(Text, { span: true, fw: 600, c: tokens.textPrimary, children: phoneHint || 'your phone' })] })] }), _jsx(Center, { children: _jsx(PinInput, { length: 6, type: "number", autoFocus: true, size: "lg", value: smsCode, onChange: (val) => { setSmsCode(val); setError(null); }, onComplete: (val) => verifySms(val), error: !!error, styles: {
                            input: {
                                backgroundColor: tokens.page,
                                borderColor: error ? tokens.errorLight : tokens.border,
                                color: tokens.textPrimary,
                                fontSize: '20px',
                                fontWeight: 600,
                            },
                        } }) }), error && (_jsx(Text, { size: "sm", c: tokens.errorLight, ta: "center", mt: "sm", children: error })), _jsx(Button, { fullWidth: true, mt: "lg", loading: loading, color: "action", onClick: () => verifySms(smsCode), "aria-label": "Verify SMS code", children: "Verify" }), _jsxs(Stack, { align: "center", gap: 4, mt: "lg", children: [_jsx(Anchor, { c: tokens.action, size: "sm", component: "button", type: "button", onClick: () => { setError(null); requestSms(); }, children: "Resend code" }), _jsx(Anchor, { c: tokens.action, size: "sm", component: "button", type: "button", onClick: () => { setView('totp'); setError(null); setCode(''); }, children: "Use authenticator app instead" }), _jsx(Anchor, { c: "dimmed", size: "xs", component: "button", type: "button", onClick: onCancel, children: "Cancel and return to sign in" })] })] }) }));
};
//# sourceMappingURL=TwoFaChallenge.js.map