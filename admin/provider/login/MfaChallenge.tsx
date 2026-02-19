/**
 * MfaChallenge — TOTP verification step during login.
 *
 * Displayed after successful API key authentication when the user
 * has MFA enabled. Accepts a 6-digit TOTP code or an 8-character
 * backup code. On success, stores the MFA session token.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useState, useCallback, useRef, useEffect } from 'react';

const API_BASE_URL = import.meta.env?.VITE_API_URL || '';

interface MfaChallengeProps {
  apiKey: string;
  onSuccess: (mfaToken: string) => void;
  onCancel: () => void;
}

export const MfaChallenge: React.FC<MfaChallengeProps> = ({
  apiKey,
  onSuccess,
  onCancel,
}) => {
  const [code, setCode] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [useBackup, setUseBackup] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, [useBackup]);

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      const trimmed = code.trim().toUpperCase();
      if (!trimmed) {
        setError(useBackup ? 'Backup code is required' : 'TOTP code is required');
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const endpoint = useBackup
          ? '/api/superadmin/mfa/backup-verify'
          : '/api/superadmin/mfa/verify';

        const resp = await fetch(`${API_BASE_URL}${endpoint}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-API-Key': apiKey,
          },
          body: JSON.stringify({ code: trimmed }),
        });

        if (!resp.ok) {
          if (resp.status === 401) {
            setError(useBackup ? 'Invalid backup code' : 'Invalid TOTP code');
          } else {
            setError(`Verification failed (${resp.status})`);
          }
          return;
        }

        const data = await resp.json();
        onSuccess(data.mfaToken);
      } catch {
        setError('Unable to verify. Please try again.');
      } finally {
        setLoading(false);
      }
    },
    [code, apiKey, useBackup, onSuccess],
  );

  const outerStyle: React.CSSProperties = {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#0c0a09',
    fontFamily:
      'Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
  };

  const cardStyle: React.CSSProperties = {
    width: '100%',
    maxWidth: '380px',
    backgroundColor: '#292524',
    borderRadius: '12px',
    border: '1px solid #44403c',
    padding: '40px',
  };

  const inputStyle: React.CSSProperties = {
    width: '100%',
    padding: '12px 14px',
    fontSize: useBackup ? '16px' : '24px',
    letterSpacing: useBackup ? 'normal' : '0.3em',
    textAlign: 'center',
    border: `1px solid ${error ? '#ff6b6b' : '#44403c'}`,
    borderRadius: '8px',
    outline: 'none',
    boxSizing: 'border-box',
    backgroundColor: '#1c1917',
    color: '#e0e0e0',
    fontFamily: 'monospace',
    transition: 'border-color 0.15s',
  };

  const primaryBtn = (disabled: boolean): React.CSSProperties => ({
    width: '100%',
    marginTop: '16px',
    padding: '10px',
    backgroundColor: disabled ? '#555' : '#3B82F6',
    color: '#fff',
    border: 'none',
    borderRadius: '8px',
    fontSize: '14px',
    fontWeight: 600,
    cursor: disabled ? 'default' : 'pointer',
  });

  const linkStyle: React.CSSProperties = {
    background: 'none',
    border: 'none',
    color: '#3B82F6',
    fontSize: '13px',
    cursor: 'pointer',
    padding: 0,
    textDecoration: 'underline',
  };

  return (
    <div style={outerStyle}>
      <div style={cardStyle}>
        <div style={{ textAlign: 'center', marginBottom: '24px' }}>
          <div style={{ fontSize: '32px', marginBottom: '8px' }}>
            {useBackup ? '\u{1F511}' : '\u{1F512}'}
          </div>
          <h2
            style={{
              margin: 0,
              fontSize: '18px',
              fontWeight: 600,
              color: '#fafaf9',
            }}
          >
            {useBackup ? 'Enter Backup Code' : 'Two-Factor Authentication'}
          </h2>
          <p style={{ margin: '8px 0 0', fontSize: '13px', color: '#a0a0a0' }}>
            {useBackup
              ? 'Enter one of your 8-character backup codes'
              : 'Enter the 6-digit code from your authenticator app'}
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          <input
            ref={inputRef}
            type="text"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder={useBackup ? 'XXXXXXXX' : '000000'}
            maxLength={useBackup ? 8 : 6}
            autoComplete="one-time-code"
            style={inputStyle}
            onFocus={(e) => {
              if (!error) e.target.style.borderColor = '#3B82F6';
            }}
            onBlur={(e) => {
              if (!error) e.target.style.borderColor = '#44403c';
            }}
          />

          {error && (
            <p style={{ margin: '8px 0 0', fontSize: '13px', color: '#ff6b6b' }}>
              {error}
            </p>
          )}

          <button type="submit" disabled={loading} style={primaryBtn(loading)}>
            {loading ? 'Verifying...' : 'Verify'}
          </button>
        </form>

        <div
          style={{
            marginTop: '16px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <button
            type="button"
            onClick={() => {
              setUseBackup(!useBackup);
              setCode('');
              setError(null);
            }}
            style={linkStyle}
          >
            {useBackup ? 'Use authenticator app' : 'Use backup code'}
          </button>
          <button type="button" onClick={onCancel} style={linkStyle}>
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
};
