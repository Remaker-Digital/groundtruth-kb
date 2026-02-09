/**
 * ApiKeyLogin — API key authentication for standalone admin.
 *
 * Login page where Stripe-direct merchants enter their API key.
 * Includes a "Forgot your key?" flow that sends a reset email.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useState, useCallback } from 'react';

const API_BASE_URL = import.meta.env?.VITE_API_URL || '';

interface ApiKeyLoginProps {
  onLogin: (apiKey: string) => void;
}

type View = 'login' | 'reset' | 'reset-sent';

export const ApiKeyLogin: React.FC<ApiKeyLoginProps> = ({ onLogin }) => {
  const [view, setView] = useState<View>('login');
  const [apiKey, setApiKey] = useState('');
  const [email, setEmail] = useState('');
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

  /* ---- shared styles -------------------------------------------------- */

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

  const linkStyle: React.CSSProperties = {
    color: '#ff3621',
    textDecoration: 'none',
    cursor: 'pointer',
    fontSize: '13px',
    background: 'none',
    border: 'none',
    padding: 0,
    fontFamily: 'inherit',
  };

  const focusHandler = (e: React.FocusEvent<HTMLInputElement>) => {
    if (!error) e.target.style.borderColor = '#ff3621';
  };
  const blurHandler = (e: React.FocusEvent<HTMLInputElement>) => {
    if (!error) e.target.style.borderColor = '#272727';
  };

  /* ---- Logo/Brand block (shared across all views) --------------------- */

  const brandBlock = (
    <div style={{ textAlign: 'center', marginBottom: '32px' }}>
      <img
        src="/admin/standalone/primary-logo-no-wordmark.svg"
        alt="Agent Red"
        style={{ width: '200px', height: 'auto', marginBottom: '16px' }}
      />
      <p style={{ margin: 0, fontSize: '14px', color: '#a0a0a0' }}>
        Customer Experience Admin
      </p>
    </div>
  );

  /* ---- Login view ----------------------------------------------------- */

  if (view === 'login') {
    return (
      <div style={outerStyle}>
        <div style={cardStyle}>
          {brandBlock}

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
              API key
            </label>
            <input
              id="api-key"
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="Enter your API key"
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

          <div style={{ marginTop: '20px', textAlign: 'center' }}>
            <button
              type="button"
              onClick={() => { setView('reset'); setError(null); setEmail(''); }}
              style={linkStyle}
            >
              Lost your API key? Request a new one
            </button>
          </div>

          <p style={{ marginTop: '16px', textAlign: 'center', fontSize: '12px', color: '#787878', lineHeight: '1.5' }}>
            Your API key was sent in your welcome email.
            <br />
            If you need a new key, click the link above.
          </p>
        </div>
      </div>
    );
  }

  /* ---- Reset view (enter email) --------------------------------------- */

  if (view === 'reset') {
    return (
      <div style={outerStyle}>
        <div style={cardStyle}>
          {brandBlock}

          <h2 style={{ margin: '0 0 8px', fontSize: '16px', fontWeight: 600, color: '#f5f5f5' }}>
            Request new API key
          </h2>
          <p style={{ margin: '0 0 20px', fontSize: '13px', color: '#a0a0a0', lineHeight: '1.5' }}>
            Enter the email address associated with your account.
            We'll generate a new API key and send it to you. Your previous key will be revoked.
          </p>

          <form onSubmit={handleReset}>
            <label
              htmlFor="reset-email"
              style={{
                display: 'block',
                fontSize: '14px',
                fontWeight: 500,
                color: '#e0e0e0',
                marginBottom: '6px',
              }}
            >
              Email address
            </label>
            <input
              id="reset-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@company.com"
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
              {loading ? 'Requesting...' : 'Request new API key'}
            </button>
          </form>

          <div style={{ marginTop: '20px', textAlign: 'center' }}>
            <button
              type="button"
              onClick={() => { setView('login'); setError(null); setApiKey(''); }}
              style={linkStyle}
            >
              Back to sign in
            </button>
          </div>
        </div>
      </div>
    );
  }

  /* ---- Reset sent (confirmation) -------------------------------------- */

  return (
    <div style={outerStyle}>
      <div style={cardStyle}>
        {brandBlock}

        <div style={{
          textAlign: 'center',
          padding: '8px 0',
        }}>
          <div style={{
            width: '48px',
            height: '48px',
            margin: '0 auto 16px',
            borderRadius: '50%',
            backgroundColor: 'rgba(255, 54, 33, 0.1)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '24px',
          }}>
            {String.fromCodePoint(0x2709)}
          </div>

          <h2 style={{ margin: '0 0 8px', fontSize: '16px', fontWeight: 600, color: '#f5f5f5' }}>
            Check your email
          </h2>
          <p style={{ margin: '0 0 8px', fontSize: '14px', color: '#e0e0e0', lineHeight: '1.5' }}>
            If an account with <strong style={{ color: '#f5f5f5' }}>{email}</strong> exists,
            we've generated a new API key and sent it to that address.
          </p>
          <p style={{ margin: '0 0 8px', fontSize: '13px', color: '#a0a0a0', lineHeight: '1.5' }}>
            Your previous API key has been revoked for security.
          </p>
          <p style={{ margin: '0 0 24px', fontSize: '13px', color: '#a0a0a0', lineHeight: '1.5' }}>
            The email may take a minute to arrive. Check your spam folder if you don't see it.
          </p>
        </div>

        <button
          type="button"
          onClick={() => { setView('login'); setError(null); setApiKey(''); setEmail(''); }}
          style={{
            ...primaryBtnStyle(false),
            marginTop: '0',
          }}
        >
          Back to sign in
        </button>

        <div style={{ marginTop: '16px', textAlign: 'center' }}>
          <button
            type="button"
            onClick={() => { setView('reset'); setError(null); }}
            style={linkStyle}
          >
            Didn't receive it? Try again
          </button>
        </div>
      </div>
    </div>
  );
};
