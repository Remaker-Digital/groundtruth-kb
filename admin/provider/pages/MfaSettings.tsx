/**
 * MfaSettings — MFA/TOTP enrollment and management page.
 *
 * Not enrolled: "Enable MFA" button → enrollment flow (QR code, manual
 * secret, backup codes download, confirm with first TOTP code).
 *
 * Enrolled: status card (enabled since, backup codes remaining),
 * "Disable MFA" button (requires valid TOTP code).
 *
 * API: GET/POST /api/superadmin/mfa/*
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useCallback, useEffect, useState } from 'react';
import {
  Alert,
  Badge,
  Button,
  Card,
  Code,
  CopyButton,
  Group,
  Modal,
  Paper,
  SimpleGrid,
  Stack,
  Text,
  TextInput,
  Title,
} from '@mantine/core';
import { useProviderContext } from '../layouts/ProviderLayout';
import { LoadingState } from '../../shared/LoadingState';
import { HelpTooltip } from '../../shared/HelpTooltip';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface MfaStatus {
  mfaEnabled: boolean;
  enrolledAt: string | null;
  backupCodesRemaining: number;
}

interface EnrollmentData {
  qrCodeDataUrl: string;
  provisioningUri: string;
  backupCodes: string[];
  backupCodeHashes: string[];
}

type Step = 'idle' | 'qr' | 'backup' | 'confirm';

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function MfaSettingsPage() {
  const { apiFetch, onNotify } = useProviderContext();

  const [status, setStatus] = useState<MfaStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Enrollment state
  const [step, setStep] = useState<Step>('idle');
  const [enrollment, setEnrollment] = useState<EnrollmentData | null>(null);
  const [confirmCode, setConfirmCode] = useState('');
  const [confirmLoading, setConfirmLoading] = useState(false);

  // Disable state
  const [showDisable, setShowDisable] = useState(false);
  const [disableCode, setDisableCode] = useState('');
  const [disableLoading, setDisableLoading] = useState(false);

  // Fetch MFA status
  const fetchStatus = useCallback(async () => {
    setLoading(true);
    try {
      const res = await apiFetch('/api/superadmin/mfa/status');
      if (res.ok) {
        const data = await res.json();
        setStatus(data);
      } else {
        setError('Failed to load MFA status');
      }
    } catch {
      setError('Unable to connect');
    } finally {
      setLoading(false);
    }
  }, [apiFetch]);

  useEffect(() => {
    fetchStatus();
  }, [fetchStatus]);

  // Start enrollment
  const handleEnroll = useCallback(async () => {
    try {
      const res = await apiFetch('/api/superadmin/mfa/enroll', { method: 'POST' });
      if (res.ok) {
        const data: EnrollmentData = await res.json();
        setEnrollment(data);
        setStep('qr');
      } else {
        const err = await res.json().catch(() => ({}));
        onNotify(err.detail || 'Enrollment failed', 'error');
      }
    } catch {
      onNotify('Unable to start enrollment', 'error');
    }
  }, [apiFetch, onNotify]);

  // Confirm enrollment
  const handleConfirm = useCallback(async () => {
    if (!confirmCode.trim() || !enrollment) return;
    setConfirmLoading(true);
    try {
      const res = await apiFetch('/api/superadmin/mfa/confirm', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code: confirmCode.trim(),
          backupCodeHashes: enrollment.backupCodeHashes,
        }),
      });
      if (res.ok) {
        onNotify('MFA enrollment confirmed', 'success');
        setStep('idle');
        setEnrollment(null);
        setConfirmCode('');
        fetchStatus();
      } else {
        onNotify('Invalid code. Please try again.', 'error');
      }
    } catch {
      onNotify('Verification failed', 'error');
    } finally {
      setConfirmLoading(false);
    }
  }, [apiFetch, confirmCode, enrollment, onNotify, fetchStatus]);

  // Disable MFA
  const handleDisable = useCallback(async () => {
    if (!disableCode.trim()) return;
    setDisableLoading(true);
    try {
      const res = await apiFetch('/api/superadmin/mfa/disable', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: disableCode.trim() }),
      });
      if (res.ok) {
        onNotify('MFA has been disabled', 'success');
        setShowDisable(false);
        setDisableCode('');
        fetchStatus();
      } else {
        onNotify('Invalid code. MFA was not disabled.', 'error');
      }
    } catch {
      onNotify('Failed to disable MFA', 'error');
    } finally {
      setDisableLoading(false);
    }
  }, [apiFetch, disableCode, onNotify, fetchStatus]);

  // Download backup codes as text file
  const downloadBackupCodes = useCallback(() => {
    if (!enrollment) return;
    const text = [
      'Agent Red — MFA Backup Codes',
      `Generated: ${new Date().toISOString()}`,
      '',
      'Each code can only be used once. Store these codes in a safe place.',
      '',
      ...enrollment.backupCodes.map((c, i) => `${String(i + 1).padStart(2, ' ')}. ${c}`),
    ].join('\n');

    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'agentred-mfa-backup-codes.txt';
    a.click();
    URL.revokeObjectURL(url);
  }, [enrollment]);

  // Loading state
  if (loading) {
    return <LoadingState text="Loading MFA settings" />;
  }

  if (error) {
    return (
      <Alert color="red" title="Error">
        {error}
      </Alert>
    );
  }

  // -------------------------------------------------------------------------
  // Enrollment flow
  // -------------------------------------------------------------------------

  if (step === 'qr' && enrollment) {
    return (
      <Stack gap="lg" maw={520}>
        <Title order={3} c="#F5F5F5">
          Set Up Authenticator App
        </Title>
        <Text c="dimmed" size="sm">
          Scan the QR code with your authenticator app (Google Authenticator,
          Authy, 1Password, etc.), then continue to save your backup codes.
        </Text>

        <Card withBorder radius="md" bg="#1a1a1a" p="xl" style={{ textAlign: 'center' }}>
          <img
            src={enrollment.qrCodeDataUrl}
            alt="MFA QR code"
            style={{ width: '200px', height: '200px', imageRendering: 'pixelated' }}
          />
        </Card>

        <Paper withBorder radius="md" p="sm" bg="#141414">
          <Text size="xs" c="dimmed" mb={4}>
            Manual entry key:
          </Text>
          <Group gap="xs">
            <Code style={{ flex: 1, wordBreak: 'break-all', fontSize: '12px' }}>
              {enrollment.provisioningUri.match(/secret=([^&]+)/)?.[1] || ''}
            </Code>
            <CopyButton
              value={enrollment.provisioningUri.match(/secret=([^&]+)/)?.[1] || ''}
            >
              {({ copied, copy }) => (
                <Button size="xs" variant="light" color={copied ? 'teal' : 'gray'} onClick={copy}>
                  {copied ? 'Copied' : 'Copy'}
                </Button>
              )}
            </CopyButton>
          </Group>
        </Paper>

        <Group justify="flex-end">
          <Button variant="subtle" color="gray" onClick={() => { setStep('idle'); setEnrollment(null); }}>
            Cancel
          </Button>
          <Button color="#ff3621" onClick={() => setStep('backup')}>
            Continue
          </Button>
        </Group>
      </Stack>
    );
  }

  if (step === 'backup' && enrollment) {
    return (
      <Stack gap="lg" maw={520}>
        <Title order={3} c="#F5F5F5">
          Save Backup Codes
        </Title>
        <Alert color="orange" title="Important">
          Save these backup codes in a safe place. Each code can only be used
          once. If you lose access to your authenticator app, you can use a
          backup code to sign in.
        </Alert>

        <SimpleGrid cols={2}>
          {enrollment.backupCodes.map((code, i) => (
            <Paper key={i} withBorder radius="sm" p="xs" bg="#141414" style={{ textAlign: 'center' }}>
              <Code style={{ fontSize: '14px', letterSpacing: '0.1em' }}>{code}</Code>
            </Paper>
          ))}
        </SimpleGrid>

        <Group justify="space-between">
          <Button variant="light" color="gray" onClick={downloadBackupCodes}>
            Download as text file
          </Button>
          <Group>
            <Button variant="subtle" color="gray" onClick={() => setStep('qr')}>
              Back
            </Button>
            <Button color="#ff3621" onClick={() => setStep('confirm')}>
              I've saved these codes
            </Button>
          </Group>
        </Group>
      </Stack>
    );
  }

  if (step === 'confirm') {
    return (
      <Stack gap="lg" maw={400}>
        <Title order={3} c="#F5F5F5">
          Verify Setup
        </Title>
        <Text c="dimmed" size="sm">
          Enter the 6-digit code from your authenticator app to confirm setup.
        </Text>

        <TextInput
          value={confirmCode}
          onChange={(e) => setConfirmCode(e.currentTarget.value)}
          placeholder="000000"
          maxLength={6}
          size="lg"
          autoFocus
          styles={{
            input: {
              textAlign: 'center',
              letterSpacing: '0.3em',
              fontSize: '24px',
              fontFamily: 'monospace',
            },
          }}
          onKeyDown={(e) => {
            if (e.key === 'Enter') handleConfirm();
          }}
        />

        <Group justify="flex-end">
          <Button
            variant="subtle"
            color="gray"
            onClick={() => setStep('backup')}
          >
            Back
          </Button>
          <Button
            color="#ff3621"
            loading={confirmLoading}
            onClick={handleConfirm}
            disabled={confirmCode.trim().length < 6}
          >
            Confirm
          </Button>
        </Group>
      </Stack>
    );
  }

  // -------------------------------------------------------------------------
  // Main view (idle state)
  // -------------------------------------------------------------------------

  return (
    <Stack gap="lg">
      <Title order={3} c="#F5F5F5">
        MFA Settings
      </Title><HelpTooltip text="Multi-factor authentication adds a second verification step using a TOTP authenticator app when signing into the Provider Console." />

      {status?.mfaEnabled ? (
        <>
          <Card withBorder radius="md" bg="#1a1a1a" p="lg">
            <Group justify="space-between" mb="md">
              <Text fw={600} c="#F5F5F5">
                Two-Factor Authentication
              </Text>
              <Badge color="green" variant="filled" size="lg">
                Enabled
              </Badge>
            </Group>

            <SimpleGrid cols={2}>
              <div>
                <Text size="xs" c="dimmed">
                  Enrolled since
                </Text>
                <Text size="sm" c="#F5F5F5">
                  {status.enrolledAt
                    ? new Date(status.enrolledAt).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                      })
                    : 'Unknown'}
                </Text>
              </div>
              <div>
                <Text size="xs" c="dimmed">
                  Backup codes remaining
                </Text><HelpTooltip text="Single-use codes for signing in when your authenticator app is unavailable. Generate new codes by re-enrolling." />
                <Text
                  size="sm"
                  c={status.backupCodesRemaining <= 2 ? '#ff6b6b' : '#F5F5F5'}
                  fw={status.backupCodesRemaining <= 2 ? 600 : 400}
                >
                  {status.backupCodesRemaining} of 10
                </Text>
              </div>
            </SimpleGrid>

            {status.backupCodesRemaining <= 2 && (
              <Alert color="orange" mt="md" title="Low backup codes">
                You have {status.backupCodesRemaining} backup code
                {status.backupCodesRemaining !== 1 ? 's' : ''} remaining.
                Consider disabling and re-enabling MFA to generate new codes.
              </Alert>
            )}
          </Card>

          <Card withBorder radius="md" bg="#1a1a1a" p="lg">
            <Text fw={600} c="#F5F5F5" mb="xs">
              Disable MFA
            </Text>
            <Text size="sm" c="dimmed" mb="md">
              Removing two-factor authentication will make your account less
              secure. You will need to enter a valid TOTP code to disable MFA.
            </Text>
            <Button
              color="red"
              variant="outline"
              onClick={() => setShowDisable(true)}
            >
              Disable MFA
            </Button>
          </Card>
        </>
      ) : (
        <Card withBorder radius="md" bg="#1a1a1a" p="lg">
          <Group justify="space-between" mb="md">
            <Text fw={600} c="#F5F5F5">
              Two-Factor Authentication
            </Text>
            <Badge color="gray" variant="outline" size="lg">
              Not Enabled
            </Badge>
          </Group>
          <Text size="sm" c="dimmed" mb="md">
            Add an extra layer of security to your account. When enabled,
            you&apos;ll need to enter a code from your authenticator app in
            addition to your API key when signing in.
          </Text>
          <Button color="#ff3621" onClick={handleEnroll}>
            Enable MFA
          </Button>
        </Card>
      )}

      {/* Disable MFA modal */}
      <Modal
        opened={showDisable}
        onClose={() => {
          setShowDisable(false);
          setDisableCode('');
        }}
        title="Disable MFA"
        centered
        styles={{
          header: { backgroundColor: '#1f1f1f' },
          body: { backgroundColor: '#1f1f1f' },
          content: { backgroundColor: '#1f1f1f' },
        }}
      >
        <Stack gap="md">
          <Text size="sm" c="dimmed">
            Enter a valid TOTP code from your authenticator app to confirm
            disabling MFA.
          </Text>
          <TextInput
            value={disableCode}
            onChange={(e) => setDisableCode(e.currentTarget.value)}
            placeholder="000000"
            maxLength={6}
            autoFocus
            styles={{
              input: {
                textAlign: 'center',
                letterSpacing: '0.3em',
                fontSize: '20px',
                fontFamily: 'monospace',
              },
            }}
            onKeyDown={(e) => {
              if (e.key === 'Enter') handleDisable();
            }}
          />
          <Group justify="flex-end">
            <Button
              variant="subtle"
              color="gray"
              onClick={() => {
                setShowDisable(false);
                setDisableCode('');
              }}
            >
              Cancel
            </Button>
            <Button
              color="red"
              loading={disableLoading}
              onClick={handleDisable}
              disabled={disableCode.trim().length < 6}
            >
              Disable MFA
            </Button>
          </Group>
        </Stack>
      </Modal>
    </Stack>
  );
}
