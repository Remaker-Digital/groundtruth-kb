/**
 * ApiKeyLogin — API key authentication for standalone admin.
 *
 * Login page where Stripe-direct merchants enter their API key.
 * Includes a "Forgot your key?" flow that sends a reset email.
 *
 * Migrated to Mantine components (Cycle 10, item 10e).
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useState, useCallback } from 'react';
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
  const [view, setView] = useState<View>('login');
  const [apiKey, setApiKey] = useState('');
  const [email, setEmail] = useState('');
  const [magicEmail, setMagicEmail] = useState('');
  const [error, setError] = useState<string | null>(verifyError ?? null);
  const [loading, setLoading] = useState(false);

  const handleLogin = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      if (!apiKey.trim()) {
        setError('API key is required');
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const resp = await fetch(`${API_BASE_URL}/api/tenants/lookup`, {
          headers: { 'X-API-Key': apiKey.trim() },
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
    [apiKey, onLogin],
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
        // SPEC-1619: Include tenant slug from URL so the magic link
        // returns the user to the same tenant-scoped page.
        const tenantSlug = new URLSearchParams(window.location.search).get('tenant');
        const resp = await fetch(`${API_BASE_URL}/api/auth/magic-link/request`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: trimmed, ...(tenantSlug && { tenant: tenantSlug }) }),
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

  /* ---- Login view ------------------------------------------------------ */

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
              <Box mt="lg" mb="sm" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{ flex: 1, height: '1px', backgroundColor: tokens.border }} />
                <Text size="xs" c="dimmed">or</Text>
                <div style={{ flex: 1, height: '1px', backgroundColor: tokens.border }} />
              </Box>

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
              onClick={() => { setView('login'); setError(null); setApiKey(''); }}
            >
              Back to sign in
            </Anchor>
          </Text>
        </Paper>
      </Center>
    );
  }

  /* ---- Magic link view (enter email) ----------------------------------- */

  if (view === 'magic-link') {
    return (
      <Center mih="100vh" bg={tokens.chrome}>
        <Paper {...cardProps}>
          {brandBlock}

          <Title order={4} c={tokens.textPrimary} mb={4}>
            Sign in with email
          </Title>
          <Text size="sm" c="dimmed" lh={1.5} mb="lg">
            Enter your email address and we'll send you a sign-in link.
            No password required.
          </Text>

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

          <Text ta="center" mt="lg" size="sm">
            <Anchor
              c={tokens.action}
              size="sm"
              component="button"
              type="button"
              onClick={() => { setView('login'); setError(null); setApiKey(''); }}
            >
              Back to sign in with API key
            </Anchor>
          </Text>
        </Paper>
      </Center>
    );
  }

  /* ---- Magic link sent (confirmation) --------------------------------- */

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
              we've sent a sign-in link to that address.
            </Text>
            <Text size="xs" c="dimmed" ta="center" lh={1.5}>
              The link will expire in 15 minutes. Check your spam folder if you don't see it.
            </Text>
          </Stack>

          <Button
            fullWidth
            mt="md"
            color="action"
            onClick={() => { setView('login'); setError(null); setApiKey(''); setMagicEmail(''); }}
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
              onClick={() => { setView('magic-link'); setError(null); }}
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
          onClick={() => { setView('login'); setError(null); setApiKey(''); setEmail(''); }}
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
