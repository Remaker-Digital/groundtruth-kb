/**
 * Provider Admin Login — Service Provider Administrator authentication.
 *
 * Login page where the Service Provider Administrator (SPA) enters their API key.
 * Validates against /api/superadmin/tenants/summary (requires SUPERADMIN role).
 * After validation, checks MFA status — if enabled, signals mfa_required.
 *
 * Note: The backend role is "SUPERADMIN" but the user-facing label is
 * "Service Provider Administration" — internal role names must not leak into UI.
 *
 * Migrated to Mantine components (Cycle 10, item 10e).
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useState, useCallback } from 'react';
import {
  Alert,
  Anchor,
  Box,
  Button,
  Center,
  Collapse,
  Paper,
  PasswordInput,
  Stack,
  Text,
  TextInput,
} from '@mantine/core';
import { tokens } from '../../shared/theme/styles';

const API_BASE_URL = import.meta.env?.VITE_API_URL || '';

export interface LoginResult {
  apiKey: string;
  mfaRequired: boolean;
}

interface ApiKeyLoginProps {
  onLogin: (result: LoginResult) => void;
}

export const ApiKeyLogin: React.FC<ApiKeyLoginProps> = ({ onLogin }) => {
  const [apiKey, setApiKey] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // SPEC-1678: Recovery state
  const [showRecovery, setShowRecovery] = useState(false);
  const [recoveryEmail, setRecoveryEmail] = useState('');
  const [recoveryCode, setRecoveryCode] = useState('');
  const [recoveryLoading, setRecoveryLoading] = useState(false);
  const [recoveryMessage, setRecoveryMessage] = useState<string | null>(null);

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
        // Validate by calling a SUPERADMIN-only endpoint
        const resp = await fetch(`${API_BASE_URL}/api/superadmin/tenants/summary`, {
          headers: { 'X-API-Key': apiKey.trim() },
        });

        if (!resp.ok) {
          if (resp.status === 401 || resp.status === 403) {
            setError('Invalid API key or insufficient permissions.');
          } else {
            setError(`Server error (${resp.status}). Please try again later.`);
          }
          return;
        }

        // Check MFA status
        let mfaRequired = false;
        try {
          const mfaResp = await fetch(`${API_BASE_URL}/api/superadmin/mfa/status`, {
            headers: { 'X-API-Key': apiKey.trim() },
          });
          if (mfaResp.ok) {
            const mfaData = await mfaResp.json();
            mfaRequired = !!mfaData.mfaEnabled;
          }
        } catch {
          // MFA check failed — proceed without MFA (service may not be configured)
        }

        onLogin({ apiKey: apiKey.trim(), mfaRequired });
      } catch {
        setError('Unable to connect. Please check your network and try again.');
      } finally {
        setLoading(false);
      }
    },
    [apiKey, onLogin],
  );

  // SPEC-1678: Recovery form handler
  const handleRecovery = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      if (!recoveryEmail.trim() || !recoveryCode.trim()) {
        setRecoveryMessage(null);
        return;
      }

      setRecoveryLoading(true);
      setRecoveryMessage(null);

      try {
        await fetch(`${API_BASE_URL}/api/auth/spa-recovery/recover`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: recoveryEmail.trim(),
            backup_code: recoveryCode.trim(),
          }),
        });
        // Always show success message (endpoint returns 200 regardless)
        setRecoveryMessage(
          'If the email and backup code are valid, a new API key has been sent to your email.',
        );
        setRecoveryCode('');
      } catch {
        setRecoveryMessage(
          'Unable to connect. Please check your network and try again.',
        );
      } finally {
        setRecoveryLoading(false);
      }
    },
    [recoveryEmail, recoveryCode],
  );

  return (
    <Center mih="100vh" bg={tokens.chrome}>
      <Paper
        w="100%"
        maw={380}
        bg={tokens.surface}
        radius="md"
        p="xl"
        styles={{ root: { border: `1px solid ${tokens.border}` } }}
      >
        <Stack align="center" gap="xs" mb="xl">
          <img
            src="/admin/provider/primary-logo-no-wordmark.svg"
            alt="Agent Red"
            style={{ width: '200px', height: 'auto' }}
          />
          <Text size="sm" c="dimmed">
            Service Provider Administration
          </Text>
        </Stack>

        <form onSubmit={handleLogin}>
          <PasswordInput
            label="API key"
            placeholder="Enter your API key"
            value={apiKey}
            onChange={(e) => setApiKey(e.currentTarget.value)}
            error={error}
            autoFocus
            aria-label="Service Provider API key"
            styles={{
              input: {
                backgroundColor: tokens.page,
                borderColor: error ? tokens.errorLight : tokens.border,
                color: tokens.textSecondary,
                '&:focus': { borderColor: tokens.action },
              },
              label: { color: tokens.textSecondary, fontWeight: 500 },
            }}
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

        {/* SPEC-1678: Recovery section */}
        <Box ta="center" mt="md">
          <Anchor
            size="xs"
            c="dimmed"
            onClick={() => {
              setShowRecovery((v) => !v);
              setRecoveryMessage(null);
            }}
            aria-label="Lost access? Use a backup code"
          >
            Lost access? Use a backup code
          </Anchor>
        </Box>

        <Collapse in={showRecovery}>
          <form onSubmit={handleRecovery}>
            <Stack gap="xs" mt="sm">
              <TextInput
                label="Email"
                placeholder="Your admin email"
                value={recoveryEmail}
                onChange={(e) => setRecoveryEmail(e.currentTarget.value)}
                size="xs"
                aria-label="Recovery email"
                styles={{
                  input: {
                    backgroundColor: tokens.page,
                    borderColor: tokens.border,
                    color: tokens.textSecondary,
                  },
                  label: { color: tokens.textSecondary, fontWeight: 500 },
                }}
              />
              <TextInput
                label="Backup code"
                placeholder="Enter 8-character backup code"
                value={recoveryCode}
                onChange={(e) => setRecoveryCode(e.currentTarget.value)}
                size="xs"
                aria-label="Backup code"
                styles={{
                  input: {
                    backgroundColor: tokens.page,
                    borderColor: tokens.border,
                    color: tokens.textSecondary,
                  },
                  label: { color: tokens.textSecondary, fontWeight: 500 },
                }}
              />
              <Button
                type="submit"
                fullWidth
                size="xs"
                loading={recoveryLoading}
                color="gray"
                variant="outline"
                aria-label="Recover access"
              >
                Recover access
              </Button>
              {recoveryMessage && (
                <Alert color="blue" variant="light" p="xs">
                  <Text size="xs">{recoveryMessage}</Text>
                </Alert>
              )}
            </Stack>
          </form>
        </Collapse>

        <Text size="xs" c="dimmed" ta="center" mt="lg" lh={1.5}>
          Service provider access only.
          <br />
          Contact your Remaker Digital administrator if you need access.
        </Text>
      </Paper>
    </Center>
  );
};
