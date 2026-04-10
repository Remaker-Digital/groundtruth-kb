// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
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

import React, { useState, useCallback } from 'react';
import {
  Anchor,
  Box,
  Button,
  Center,
  Paper,
  PinInput,
  Stack,
  Text,
  TextInput,
  ThemeIcon,
  Title,
} from '@mantine/core';
import { Icons } from '../../shared/icons';
import { tokens } from '../../shared/theme/styles';

const API_BASE_URL = import.meta.env?.VITE_API_URL || '';

type ChallengeView = 'totp' | 'backup' | 'sms' | 'sms-sent';

interface TwoFaChallengeProps {
  pendingToken: string;
  email: string;
  mfaMethods: string[];
  onComplete: (sessionToken: string) => void;
  onCancel: () => void;
}

export const TwoFaChallenge: React.FC<TwoFaChallengeProps> = ({
  pendingToken,
  email,
  mfaMethods,
  onComplete,
  onCancel,
}) => {
  const hasSms = mfaMethods.includes('sms');
  const [view, setView] = useState<ChallengeView>('totp');
  const [code, setCode] = useState('');
  const [backupCode, setBackupCode] = useState('');
  const [smsCode, setSmsCode] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [phoneHint, setPhoneHint] = useState<string | null>(null);

  /* ---- Shared UI -------------------------------------------------------- */

  const cardProps = {
    w: '100%' as const,
    maw: 400,
    bg: tokens.surface,
    radius: 'md' as const,
    p: 'xl' as const,
    styles: { root: { border: `1px solid ${tokens.border}` } },
  };

  const brandBlock = (
    <Stack align="center" gap="xs" mb="lg">
      <img
        src="/admin/standalone/primary-logo-no-wordmark.svg"
        alt="Agent Red"
        style={{ width: '160px', height: 'auto' }}
      />
    </Stack>
  );

  /* ---- API calls -------------------------------------------------------- */

  const verifyTotp = useCallback(async (totpCode: string) => {
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
      } else if (resp.status === 429) {
        setError('Too many attempts. Please request a new sign-in link.');
      } else {
        setError(data.message || 'Invalid code. Please try again.');
      }
    } catch {
      setError('Unable to verify. Please check your network.');
    } finally {
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
      } else if (resp.status === 429) {
        setError('Too many attempts. Please request a new sign-in link.');
      } else {
        setError(data.message || 'Invalid backup code. Please try again.');
      }
    } catch {
      setError('Unable to verify. Please check your network.');
    } finally {
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
      } else {
        setError(data.message || 'Unable to send SMS. Try TOTP instead.');
      }
    } catch {
      setError('Unable to send SMS. Please check your network.');
    } finally {
      setLoading(false);
    }
  }, [pendingToken]);

  const verifySms = useCallback(async (smsOtp: string) => {
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
      } else if (resp.status === 429) {
        setError('Too many attempts. Please request a new sign-in link.');
      } else {
        setError(data.message || 'Invalid code. Please try again.');
      }
    } catch {
      setError('Unable to verify. Please check your network.');
    } finally {
      setLoading(false);
    }
  }, [pendingToken, onComplete]);

  /* ---- TOTP challenge view ---------------------------------------------- */

  if (view === 'totp') {
    return (
      <Center mih="100vh" bg={tokens.chrome}>
        <Paper {...cardProps}>
          {brandBlock}

          <Stack align="center" gap={4} mb="lg">
            <ThemeIcon size={40} radius="xl" variant="light" color="action" aria-hidden>
              <Icons.mfa size={20} />
            </ThemeIcon>
            <Title order={4} c={tokens.textPrimary} ta="center">
              Two-factor authentication
            </Title>
            <Text size="sm" c={tokens.textSecondary} ta="center" lh={1.5}>
              Enter the 6-digit code from your authenticator app
            </Text>
          </Stack>

          <Center>
            <PinInput
              length={6}
              type="number"
              autoFocus
              size="lg"
              value={code}
              onChange={(val) => { setCode(val); setError(null); }}
              onComplete={(val) => verifyTotp(val)}
              error={!!error}
              styles={{
                input: {
                  backgroundColor: tokens.page,
                  borderColor: error ? tokens.errorLight : tokens.border,
                  color: tokens.textPrimary,
                  fontSize: '20px',
                  fontWeight: 600,
                },
              }}
            />
          </Center>

          {error && (
            <Text size="sm" c={tokens.errorLight} ta="center" mt="sm">
              {error}
            </Text>
          )}

          <Button
            fullWidth
            mt="lg"
            loading={loading}
            color="action"
            onClick={() => verifyTotp(code)}
            aria-label="Verify code"
          >
            Verify
          </Button>

          <Stack align="center" gap={4} mt="lg">
            <Anchor
              c={tokens.action}
              size="sm"
              component="button"
              type="button"
              onClick={() => { setView('backup'); setError(null); setBackupCode(''); }}
            >
              Use a backup code instead
            </Anchor>

            {hasSms && (
              <Anchor
                c={tokens.action}
                size="sm"
                component="button"
                type="button"
                onClick={() => { setError(null); requestSms(); }}
              >
                Send code via SMS
              </Anchor>
            )}

            <Anchor
              c="dimmed"
              size="xs"
              component="button"
              type="button"
              onClick={onCancel}
            >
              Cancel and return to sign in
            </Anchor>
          </Stack>
        </Paper>
      </Center>
    );
  }

  /* ---- Backup code view ------------------------------------------------- */

  if (view === 'backup') {
    return (
      <Center mih="100vh" bg={tokens.chrome}>
        <Paper {...cardProps}>
          {brandBlock}

          <Stack align="center" gap={4} mb="lg">
            <ThemeIcon size={40} radius="xl" variant="light" color="action" aria-hidden>
              <Icons.secrets size={20} />
            </ThemeIcon>
            <Title order={4} c={tokens.textPrimary} ta="center">
              Backup code
            </Title>
            <Text size="sm" c={tokens.textSecondary} ta="center" lh={1.5}>
              Enter one of your 8-character recovery codes
            </Text>
          </Stack>

          <form onSubmit={(e) => { e.preventDefault(); verifyBackup(); }}>
            <TextInput
              placeholder="ABCD1234"
              value={backupCode}
              onChange={(e) => { setBackupCode(e.currentTarget.value); setError(null); }}
              error={error}
              autoFocus
              aria-label="Backup code"
              styles={{
                input: {
                  backgroundColor: tokens.page,
                  borderColor: error ? tokens.errorLight : tokens.border,
                  color: tokens.textPrimary,
                  fontFamily: 'monospace',
                  fontSize: '18px',
                  letterSpacing: '2px',
                  textAlign: 'center',
                },
              }}
            />

            <Button
              type="submit"
              fullWidth
              mt="md"
              loading={loading}
              color="action"
              aria-label="Verify backup code"
            >
              Verify backup code
            </Button>
          </form>

          <Stack align="center" gap={4} mt="lg">
            <Anchor
              c={tokens.action}
              size="sm"
              component="button"
              type="button"
              onClick={() => { setView('totp'); setError(null); setCode(''); }}
            >
              Use authenticator app instead
            </Anchor>

            <Anchor
              c="dimmed"
              size="xs"
              component="button"
              type="button"
              onClick={onCancel}
            >
              Cancel and return to sign in
            </Anchor>
          </Stack>
        </Paper>
      </Center>
    );
  }

  /* ---- SMS sent view ---------------------------------------------------- */

  return (
    <Center mih="100vh" bg={tokens.chrome}>
      <Paper {...cardProps}>
        {brandBlock}

        <Stack align="center" gap={4} mb="lg">
          <ThemeIcon size={40} radius="xl" variant="light" color="action" aria-hidden>
            <Icons.contact size={20} />
          </ThemeIcon>
          <Title order={4} c={tokens.textPrimary} ta="center">
            Verify your phone
          </Title>
          <Text size="sm" c={tokens.textSecondary} ta="center" lh={1.5}>
            We sent a 6-digit code to{' '}
            <Text span fw={600} c={tokens.textPrimary}>
              {phoneHint || 'your phone'}
            </Text>
          </Text>
        </Stack>

        <Center>
          <PinInput
            length={6}
            type="number"
            autoFocus
            size="lg"
            value={smsCode}
            onChange={(val) => { setSmsCode(val); setError(null); }}
            onComplete={(val) => verifySms(val)}
            error={!!error}
            styles={{
              input: {
                backgroundColor: tokens.page,
                borderColor: error ? tokens.errorLight : tokens.border,
                color: tokens.textPrimary,
                fontSize: '20px',
                fontWeight: 600,
              },
            }}
          />
        </Center>

        {error && (
          <Text size="sm" c={tokens.errorLight} ta="center" mt="sm">
            {error}
          </Text>
        )}

        <Button
          fullWidth
          mt="lg"
          loading={loading}
          color="action"
          onClick={() => verifySms(smsCode)}
          aria-label="Verify SMS code"
        >
          Verify
        </Button>

        <Stack align="center" gap={4} mt="lg">
          <Anchor
            c={tokens.action}
            size="sm"
            component="button"
            type="button"
            onClick={() => { setError(null); requestSms(); }}
          >
            Resend code
          </Anchor>

          <Anchor
            c={tokens.action}
            size="sm"
            component="button"
            type="button"
            onClick={() => { setView('totp'); setError(null); setCode(''); }}
          >
            Use authenticator app instead
          </Anchor>

          <Anchor
            c="dimmed"
            size="xs"
            component="button"
            type="button"
            onClick={onCancel}
          >
            Cancel and return to sign in
          </Anchor>
        </Stack>
      </Paper>
    </Center>
  );
};
