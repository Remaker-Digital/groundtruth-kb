/**
 * ApiKeyLogin — API key authentication for standalone admin.
 *
 * Simple login page where Stripe-direct merchants enter their API key.
 * Validates the key against the backend before granting access.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useState, useCallback } from 'react';

const API_BASE_URL = import.meta.env?.VITE_API_URL || '';

interface ApiKeyLoginProps {
  onLogin: (apiKey: string) => void;
}

export const ApiKeyLogin: React.FC<ApiKeyLoginProps> = ({ onLogin }) => {
  const [apiKey, setApiKey] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = useCallback(
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

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: '#0a0a0a',
        fontFamily: 'Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      }}
    >
      <div
        style={{
          width: '100%',
          maxWidth: '380px',
          backgroundColor: '#1f1f1f',
          borderRadius: '12px',
          border: '1px solid #272727',
          padding: '40px',
        }}
      >
        {/* Logo / Brand */}
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <img
            src="/admin/standalone/icon-master.svg"
            alt="Agent Red"
            style={{
              width: '48px',
              height: '48px',
              marginBottom: '16px',
            }}
          />
          <h1 style={{ margin: '0 0 4px', fontSize: '20px', fontWeight: 600, color: '#f5f5f5' }}>
            Agent Red
          </h1>
          <p style={{ margin: 0, fontSize: '14px', color: '#a0a0a0' }}>
            Customer Experience Admin
          </p>
        </div>

        {/* Login Form */}
        <form onSubmit={handleSubmit}>
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
            API Key
          </label>
          <input
            id="api-key"
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="Enter your API key"
            autoFocus
            style={{
              width: '100%',
              padding: '10px 14px',
              fontSize: '14px',
              border: `1px solid ${error ? '#ff6b6b' : '#272727'}`,
              borderRadius: '8px',
              outline: 'none',
              boxSizing: 'border-box',
              backgroundColor: '#141414',
              color: '#e0e0e0',
              transition: 'border-color 0.15s',
            }}
            onFocus={(e) => {
              if (!error) (e.target as HTMLInputElement).style.borderColor = '#ff3621';
            }}
            onBlur={(e) => {
              if (!error) (e.target as HTMLInputElement).style.borderColor = '#272727';
            }}
          />

          {error && (
            <p style={{ margin: '8px 0 0', fontSize: '13px', color: '#ff6b6b' }}>
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%',
              marginTop: '16px',
              padding: '10px',
              backgroundColor: loading ? '#555' : '#ff3621',
              color: '#ffffff',
              border: 'none',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: 600,
              cursor: loading ? 'default' : 'pointer',
              transition: 'background-color 0.15s',
            }}
          >
            {loading ? 'Verifying...' : 'Sign In'}
          </button>
        </form>

        <p
          style={{
            marginTop: '24px',
            textAlign: 'center',
            fontSize: '12px',
            color: '#787878',
          }}
        >
          Find your API key in your welcome email or contact support.
        </p>
      </div>
    </div>
  );
};
