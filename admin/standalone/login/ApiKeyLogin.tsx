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

import React, { useState, useCallback, useMemo } from 'react';
import {
  Anchor,
  Box,
  Button,
  Center,
  Paper,
  PasswordInput,
  Stack,
  Text,
  TextInput,
  ThemeIcon,
  Title,
} from '@mantine/core';
import { Icons } from '../../shared/icons';
import { tokens } from '../../shared/theme/styles';

const API_BASE_URL = import.meta.env?.VITE_API_URL || '';

interface ApiKeyLoginProps {
  onLogin: (apiKey: string) => void;
  /** Callback for magic link session token login. */
  onMagicLinkLogin?: (sessionToken: string) => void;
  /** Error from a failed magic link verification (e.g. expired link). */
  verifyError?: string | null;
}

type View = 'login' | 'reset' | 'reset-sent' | 'magic-link' | 'magic-link-sent';

export const ApiKeyLogin: React.FC<ApiKeyLoginProps> = ({
  onLogin,
  onMagicLinkLogin,
  verifyError,
}) => {
  // SPEC-0429: Magic link is primary when tenant context is available.
  // Cache tenant ID once at mount — avoids re-reading URL at submit time
  // (SPA routing or history changes could strip query params between mount and submit).
  const tenantId = useMemo(() => {
    try {
      return new URLSearchParams(window.location.search).get('tenant') || null;
    } catch {
      return null;
    }
  }, []);
  const hasTenant = !!tenantId;

  const defaultView: View = (hasTenant && onMagicLinkLogin) ? 'magic-link' : 'login';
  const [view, setView] = useState<View>(defaultView);
  const [apiKey, setApiKey] = useState('');
  const [email, setEmail] = useState('');
  const [magicEmail, setMagicEmail] = useState('');
  const [signInCode, setSignInCode] = useState('');
  const [error, setError] = useState<string | null>(verifyError ?? null);
  const [loading, setLoading] = useState(false);

  /** Navigate back to whichever view is the "home" for this context. */
  const goHome = useCallback(() => {
    setView(defaultView);
    setError(null);
    setApiKey('');
    setMagicEmail('');
    setEmail('');
  }, [defaultView]);

  const handleLogin = useCallback(
    async (e: React.FormEvent) => {
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
          } else {
            setError(`Server error (${resp.status}). Please try again later.`);
          }
          return;
        }

        onLogin(apiKey.trim());
      } catch {
        setError('Unable to connect. Please check your network and try again.');
      } finally {
        setLoading(false);
      }
    },
    [apiKey, tenantId, onLogin],
  );

  const handleReset = useCallback(
    async (e: React.FormEvent) => {
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
      } catch {
        setError('Unable to connect. Please check your network and try again.');
      } finally {
        setLoading(false);
      }
    },
    [email],
  );

  const handleMagicLink = useCallback(
    async (e: React.FormEvent) => {
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
      } catch {
        setError('Unable to connect. Please check your network and try again.');
      } finally {
        setLoading(false);
      }
    },
    [magicEmail],
  );

  // SPEC-0429 S188: Verify 6-digit sign-in code (alternative to clicking link)
  const handleCodeVerify = useCallback(
    async (e: React.FormEvent) => {
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
      } catch {
        setError('Unable to connect. Please check your network and try again.');
      } finally {
        setLoading(false);
      }
    },
    [signInCode, tenantId, onMagicLinkLogin],
  );

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
    w: '100%' as const,
    maw: 380,
    bg: tokens.surface,
    radius: 'md' as const,
    p: 'xl' as const,
    styles: { root: { border: `1px solid ${tokens.border}` } },
  };

  const brandBlock = (
    <Stack align="center" gap="xs" mb="xl">
      <img
        src="/admin/standalone/primary-logo-no-wordmark.svg"
        alt="Agent Red"
        style={{ width: '200px', height: 'auto' }}
      />
      <Text size="sm" c="dimmed">
        Customer Experience Admin
      </Text>
    </Stack>
  );

  const divider = (
    <Box mt="lg" mb="sm" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
      <div style={{ flex: 1, height: '1px', backgroundColor: tokens.border }} />
      <Text size="xs" c="dimmed">or</Text>
      <div style={{ flex: 1, height: '1px', backgroundColor: tokens.border }} />
    </Box>
  );

  /* ---- Invalid URL: no tenant context ---------------------------------- */

  if (!hasTenant) {
    return (
      <Center mih="100vh" bg={tokens.chrome}>
        <Paper {...cardProps}>
          {brandBlock}

          <Stack align="center" gap="md">
            <ThemeIcon size={48} radius="xl" color="red" variant="light">
              <Icons.alerts size={24} />
            </ThemeIcon>

            <Title order={4} ta="center" c={tokens.textPrimary}>
              Invalid URL
            </Title>

            <Text size="sm" c={tokens.textSecondary} ta="center" lh={1.6}>
              This URL does not include a tenant identifier and cannot be used to sign in.
              Please use the link from your welcome email, which includes your tenant context.
            </Text>
          </Stack>
        </Paper>
      </Center>
    );
  }

  /* ---- Magic link view (PRIMARY per SPEC-0429) ------------------------- */

  if (view === 'magic-link') {
    return (
      <Center mih="100vh" bg={tokens.chrome}>
        <Paper {...cardProps}>
          {brandBlock}

          <form onSubmit={handleMagicLink}>
            <TextInput
              label="Email address"
              type="email"
              placeholder="you@company.com"
              value={magicEmail}
              onChange={(e) => setMagicEmail(e.currentTarget.value)}
              error={error}
              autoFocus
              aria-label="Email address"
              styles={inputStyles}
            />

            <Button
              type="submit"
              fullWidth
              mt="md"
              loading={loading}
              color="action"
              aria-label="Send sign-in link"
            >
              Send sign-in link
            </Button>
          </form>

          <Text size="xs" c="dimmed" ta="center" mt="sm" lh={1.5}>
            We'll email you a secure sign-in link. No password required.
          </Text>

          {divider}

          <Button
            fullWidth
            variant="outline"
            color="action"
            onClick={() => { setView('login'); setError(null); setApiKey(''); }}
            aria-label="Sign in with API key"
          >
            Sign in with API key
          </Button>
        </Paper>
      </Center>
    );
  }

  /* ---- API key view (secondary fallback) -------------------------------- */

  if (view === 'login') {
    return (
      <Center mih="100vh" bg={tokens.chrome}>
        <Paper {...cardProps}>
          {brandBlock}

          <form onSubmit={handleLogin}>
            <PasswordInput
              label="API key"
              placeholder="Enter your API key"
              value={apiKey}
              onChange={(e) => setApiKey(e.currentTarget.value)}
              error={error}
              autoFocus
              aria-label="API key"
              styles={inputStyles}
            />

            <Button
              type="submit"
              fullWidth
              mt="md"
              loading={loading}
              color="action"
              aria-label="Sign in"
            >
              Sign in
            </Button>
          </form>

          <Text ta="center" mt="lg" size="sm">
            <Anchor
              c={tokens.action}
              size="sm"
              component="button"
              type="button"
              onClick={() => { setView('reset'); setError(null); setEmail(''); }}
            >
              Lost your API key? Request a new one
            </Anchor>
          </Text>

          {onMagicLinkLogin && (
            <>
              {divider}

              <Button
                fullWidth
                variant="outline"
                color="action"
                onClick={() => { setView('magic-link'); setError(null); setMagicEmail(''); }}
                aria-label="Sign in with email"
              >
                Sign in with email
              </Button>
            </>
          )}

          <Text size="xs" c="dimmed" ta="center" mt="sm" lh={1.5}>
            Your API key was sent in your welcome email.
            <br />
            If you need a new key, click the link above.
          </Text>
        </Paper>
      </Center>
    );
  }

  /* ---- Reset view (enter email) ---------------------------------------- */

  if (view === 'reset') {
    return (
      <Center mih="100vh" bg={tokens.chrome}>
        <Paper {...cardProps}>
          {brandBlock}

          <Title order={4} c={tokens.textPrimary} mb={4}>
            Request new API key
          </Title>
          <Text size="sm" c="dimmed" lh={1.5} mb="lg">
            Enter the email address associated with your account.
            We'll generate a new API key and send it to you. Your previous key will be revoked.
          </Text>

          <form onSubmit={handleReset}>
            <TextInput
              label="Email address"
              type="email"
              placeholder="you@company.com"
              value={email}
              onChange={(e) => setEmail(e.currentTarget.value)}
              error={error}
              autoFocus
              aria-label="Email address"
              styles={inputStyles}
            />

            <Button
              type="submit"
              fullWidth
              mt="md"
              loading={loading}
              color="action"
              aria-label="Request new API key"
            >
              Request new API key
            </Button>
          </form>

          <Text ta="center" mt="lg" size="sm">
            <Anchor
              c={tokens.action}
              size="sm"
              component="button"
              type="button"
              onClick={goHome}
            >
              Back to sign in
            </Anchor>
          </Text>
        </Paper>
      </Center>
    );
  }

  /* ---- Magic link sent (confirmation + code entry, SPEC-0429) ---------- */

  if (view === 'magic-link-sent') {
    return (
      <Center mih="100vh" bg={tokens.chrome}>
        <Paper {...cardProps}>
          {brandBlock}

          <Stack align="center" gap="xs" py="sm">
            <ThemeIcon
              size={48}
              radius="xl"
              variant="light"
              color="action"
              aria-hidden
            >
              <Icons.email size={24} />
            </ThemeIcon>

            <Title order={4} c={tokens.textPrimary} ta="center">
              Check your email
            </Title>
            <Text size="sm" c={tokens.textSecondary} ta="center" lh={1.5}>
              If an account with <Text span fw={600} c={tokens.textPrimary}>{magicEmail}</Text> exists,
              we've sent a sign-in code and link to that address.
            </Text>
            <Text size="xs" c="dimmed" ta="center" lh={1.5}>
              Enter the 6-digit code from the email, or click the link. Expires in 15 minutes.
            </Text>
          </Stack>

          {/* SPEC-0429 S188: Sign-in code entry */}
          <form onSubmit={handleCodeVerify}>
            <TextInput
              label="Sign-in code"
              placeholder="000000"
              value={signInCode}
              onChange={(e) => {
                const v = e.currentTarget.value.replace(/\D/g, '').slice(0, 6);
                setSignInCode(v);
                setError(null);
              }}
              error={error}
              maxLength={6}
              autoFocus
              autoComplete="one-time-code"
              inputMode="numeric"
              aria-label="Sign-in code"
              styles={{
                ...inputStyles,
                input: {
                  ...inputStyles.input,
                  textAlign: 'center' as const,
                  fontSize: '24px',
                  fontFamily: 'monospace',
                  letterSpacing: '8px',
                  fontWeight: 600,
                },
              }}
            />

            <Button
              type="submit"
              fullWidth
              mt="md"
              loading={loading}
              color="action"
              aria-label="Verify code"
            >
              Verify code
            </Button>
          </form>

          <Text ta="center" mt="md" size="sm">
            <Anchor
              c={tokens.action}
              size="sm"
              component="button"
              type="button"
              onClick={() => { setView('magic-link'); setError(null); setSignInCode(''); }}
            >
              Didn't receive it? Try again
            </Anchor>
          </Text>
        </Paper>
      </Center>
    );
  }

  /* ---- Reset sent (confirmation) --------------------------------------- */

  return (
    <Center mih="100vh" bg={tokens.chrome}>
      <Paper {...cardProps}>
        {brandBlock}

        <Stack align="center" gap="xs" py="sm">
          <ThemeIcon
            size={48}
            radius="xl"
            variant="light"
            color="action"
            aria-hidden
          >
            <Icons.email size={24} />
          </ThemeIcon>

          <Title order={4} c={tokens.textPrimary} ta="center">
            Check your email
          </Title>
          <Text size="sm" c={tokens.textSecondary} ta="center" lh={1.5}>
            If an account with <Text span fw={600} c={tokens.textPrimary}>{email}</Text> exists,
            we've generated a new API key and sent it to that address.
          </Text>
          <Text size="xs" c="dimmed" ta="center" lh={1.5}>
            Your previous API key has been revoked for security.
          </Text>
          <Text size="xs" c="dimmed" ta="center" lh={1.5}>
            The email may take a minute to arrive. Check your spam folder if you don't see it.
          </Text>
        </Stack>

        <Button
          fullWidth
          mt="md"
          color="action"
          onClick={goHome}
          aria-label="Back to sign in"
        >
          Back to sign in
        </Button>

        <Text ta="center" mt="sm" size="sm">
          <Anchor
            c={tokens.action}
            size="sm"
            component="button"
            type="button"
            onClick={() => { setView('reset'); setError(null); }}
          >
            Didn't receive it? Try again
          </Anchor>
        </Text>
      </Paper>
    </Center>
  );
};
