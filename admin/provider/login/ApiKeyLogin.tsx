/**
 * Provider Admin Login — SUPERADMIN API key authentication.
 *
 * Login page where the platform operator enters their SUPERADMIN API key.
 * Validates against /api/superadmin/tenants/summary (requires SUPERADMIN role).
 * After validation, checks MFA status — if enabled, signals mfa_required.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useState, useCallback } from 'react';

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

  const outerStyle: React.CSSProperties = {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#0a0a0a',
    fontFamily: 'Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
  };

  const cardStyle: React.CSSProperties = {
    width: '100%',
    maxWidth: '380px',
    backgroundColor: '#1f1f1f',
    borderRadius: '12px',
    border: '1px solid #272727',
    padding: '40px',
  };

  const inputStyle = (hasError: boolean): React.CSSProperties => ({
    width: '100%',
    padding: '10px 14px',
    fontSize: '14px',
    border: `1px solid ${hasError ? '#ff6b6b' : '#272727'}`,
    borderRadius: '8px',
    outline: 'none',
    boxSizing: 'border-box',
    backgroundColor: '#141414',
    color: '#e0e0e0',
    transition: 'border-color 0.15s',
  });

  const primaryBtnStyle = (disabled: boolean): React.CSSProperties => ({
    width: '100%',
    marginTop: '16px',
    padding: '10px',
    backgroundColor: disabled ? '#555' : '#ff3621',
    color: '#ffffff',
    border: 'none',
    borderRadius: '8px',
    fontSize: '14px',
    fontWeight: 600,
    cursor: disabled ? 'default' : 'pointer',
    transition: 'background-color 0.15s',
  });

  const focusHandler = (e: React.FocusEvent<HTMLInputElement>) => {
    if (!error) e.target.style.borderColor = '#ff3621';
  };
  const blurHandler = (e: React.FocusEvent<HTMLInputElement>) => {
    if (!error) e.target.style.borderColor = '#272727';
  };

  return (
    <div style={outerStyle}>
      <div style={cardStyle}>
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <img
            src="/admin/provider/primary-logo-no-wordmark.svg"
            alt="Agent Red"
            style={{ width: '200px', height: 'auto', marginBottom: '16px' }}
          />
          <p style={{ margin: 0, fontSize: '14px', color: '#a0a0a0' }}>
            Provider Console
          </p>
        </div>

        <form onSubmit={handleLogin}>
          <label
            htmlFor="api-key"
            style={{
              display: 'block',
              fontSize: '14px',
              fontWeight: 500,
              color: '#e0e0e0',
              marginBottom: '6px',
            }}
          >
            SUPERADMIN API key
          </label>
          <input
            id="api-key"
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="Enter your SUPERADMIN API key"
            autoFocus
            style={inputStyle(!!error)}
            onFocus={focusHandler}
            onBlur={blurHandler}
          />

          {error && (
            <p style={{ margin: '8px 0 0', fontSize: '13px', color: '#ff6b6b' }}>
              {error}
            </p>
          )}

          <button type="submit" disabled={loading} style={primaryBtnStyle(loading)}>
            {loading ? 'Verifying...' : 'Sign in'}
          </button>
        </form>

        <p style={{ marginTop: '20px', textAlign: 'center', fontSize: '12px', color: '#787878', lineHeight: '1.5' }}>
          Platform operator access only.
          <br />
          Contact your administrator if you need access.
        </p>
      </div>
    </div>
  );
};
