/**
 * Provider Admin Login — SUPERADMIN API key authentication.
 *
 * Login page where the platform operator enters their SUPERADMIN API key.
 * Validates against /api/superadmin/tenants/summary (requires SUPERADMIN role).
 * After validation, checks MFA status — if enabled, signals mfa_required.
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
            setError('Invalid API key or insufficient permissions. SUPERADMIN role required.');
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
    <Center mih="100vh" bg="#0a0a0a">
      <Paper
        w="100%"
        maw={380}
        bg="#1f1f1f"
        radius="md"
        p="xl"
        styles={{ root: { border: '1px solid #272727' } }}
      >
        <Stack align="center" gap="xs" mb="xl">
          <img
            src="/admin/provider/primary-logo-no-wordmark.svg"
            alt="Agent Red"
            style={{ width: '200px', height: 'auto' }}
          />
          <Text size="sm" c="dimmed">
            Provider Console
          </Text>
        </Stack>

        <form onSubmit={handleLogin}>
          <PasswordInput
            label="SUPERADMIN API key"
            placeholder="Enter your SUPERADMIN API key"
            value={apiKey}
            onChange={(e) => setApiKey(e.currentTarget.value)}
            error={error}
            autoFocus
            aria-label="SUPERADMIN API key"
            styles={{
              input: {
                backgroundColor: '#141414',
                borderColor: error ? '#ff6b6b' : '#272727',
                color: '#e0e0e0',
                '&:focus': { borderColor: '#ff3621' },
              },
              label: { color: '#e0e0e0', fontWeight: 500 },
            }}
          />

          <Button
            type="submit"
            fullWidth
            mt="md"
            loading={loading}
            color="#ff3621"
            aria-label="Sign in"
          >
            Sign in
          </Button>
        </form>

        <Text size="xs" c="dimmed" ta="center" mt="lg" lh={1.5}>
          Platform operator access only.
          <br />
          Contact your administrator if you need access.
        </Text>
      </Paper>
    </Center>
  );
};
