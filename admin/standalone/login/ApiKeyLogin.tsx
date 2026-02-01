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
        backgroundColor: '#f6f6f7',
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      }}
    >
      <div
        style={{
          width: '100%',
          maxWidth: '400px',
          backgroundColor: '#ffffff',
          borderRadius: '12px',
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
          padding: '40px',
        }}
      >
        {/* Logo / Brand */}
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: '48px',
              height: '48px',
              borderRadius: '12px',
              backgroundColor: '#C41E2A',
              color: '#ffffff',
              fontSize: '20px',
              fontWeight: 700,
              marginBottom: '16px',
            }}
          >
            AR
          </div>
          <h1 style={{ margin: '0 0 4px', fontSize: '20px', fontWeight: 600, color: '#1a1a1a' }}>
            Agent Red
          </h1>
          <p style={{ margin: 0, fontSize: '14px', color: '#6d7175' }}>
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
              color: '#202223',
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
              padding: '10px 12px',
              fontSize: '14px',
              border: `1px solid ${error ? '#d72c0d' : '#c9cccf'}`,
              borderRadius: '6px',
              outline: 'none',
              boxSizing: 'border-box',
              transition: 'border-color 0.15s',
            }}
            onFocus={(e) => {
              if (!error) (e.target as HTMLInputElement).style.borderColor = '#5c6ac4';
            }}
            onBlur={(e) => {
              if (!error) (e.target as HTMLInputElement).style.borderColor = '#c9cccf';
            }}
          />

          {error && (
            <p style={{ margin: '8px 0 0', fontSize: '13px', color: '#d72c0d' }}>
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
              backgroundColor: loading ? '#8c9196' : '#C41E2A',
              color: '#ffffff',
              border: 'none',
              borderRadius: '6px',
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
            color: '#8c9196',
          }}
        >
          Find your API key in your welcome email or contact support.
        </p>
      </div>
    </div>
  );
};
