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
  Box,
  Button,
  Center,
  Paper,
  PasswordInput,
  Stack,
  Text,
} from '@mantine/core';

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

  return (
    <Center mih="100vh" bg="#0c0a09">
      <Paper
        w="100%"
        maw={380}
        bg="#292524"
        radius="md"
        p="xl"
        styles={{ root: { border: '1px solid #44403c' } }}
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
                backgroundColor: '#1c1917',
                borderColor: error ? '#ff6b6b' : '#44403c',
                color: '#e0e0e0',
                '&:focus': { borderColor: '#3B82F6' },
              },
              label: { color: '#e0e0e0', fontWeight: 500 },
            }}
          />

          <Button
            type="submit"
            fullWidth
            mt="md"
            loading={loading}
            color="#3B82F6"
            aria-label="Sign in"
          >
            Sign in
          </Button>
        </form>

        <Text size="xs" c="dimmed" ta="center" mt="lg" lh={1.5}>
          Service provider access only.
          <br />
          Contact your Remaker Digital administrator if you need access.
        </Text>
      </Paper>
    </Center>
  );
};
