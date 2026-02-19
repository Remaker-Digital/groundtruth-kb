/**
 * ActivationBanner — Persistent banner for pending configuration changes.
 *
 * Displayed below the header and above page content when draft (unsaved)
 * config changes exist.  Polls GET /api/config/activation-status every
 * 30 seconds to detect changes made on other tabs or by other admins.
 *
 * Actions:
 *   - [Activate] — opens the ActivationDialog
 *   - [Discard]  — discards all draft changes
 *
 * Props (from layout shell):
 *   - apiFetch     — shell-provided fetch wrapper with auth headers
 *   - onNotify     — shell toast callback
 *   - onActivate   — callback to open the ActivationDialog
 *   - refreshKey   — increment to force immediate re-poll after save/discard
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useCallback, useEffect, useState } from 'react';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface ActivationStatus {
  has_pending_changes: boolean;
  active_version: number;
  active_activated_at: string | null;
  draft_version: number | null;
}

interface ActivationBannerProps {
  apiFetch: (path: string, init?: RequestInit) => Promise<Response>;
  onNotify: (message: string, type: 'success' | 'error' | 'warning' | 'info') => void;
  onActivate: () => void;
  refreshKey?: number;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function ActivationBanner({
  apiFetch,
  onNotify,
  onActivate,
  refreshKey = 0,
}: ActivationBannerProps) {
  const [status, setStatus] = useState<ActivationStatus | null>(null);
  const [discarding, setDiscarding] = useState(false);

  // Poll activation status
  const fetchStatus = useCallback(async () => {
    try {
      const res = await apiFetch('/api/config/activation-status');
      if (res.ok) {
        const data: ActivationStatus = await res.json();
        setStatus(data);
      }
    } catch {
      // Silently ignore polling errors
    }
  }, [apiFetch]);

  // Initial fetch + polling every 30s
  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 30_000);
    return () => clearInterval(interval);
  }, [fetchStatus, refreshKey]);

  // Discard handler
  const handleDiscard = useCallback(async () => {
    if (!confirm('Discard all draft changes? This cannot be undone.')) return;

    setDiscarding(true);
    try {
      const res = await apiFetch('/api/config/draft/discard', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: '{}',
      });
      if (res.ok) {
        onNotify('Draft changes discarded', 'info');
        setStatus(null);
        fetchStatus();
      } else {
        onNotify('Failed to discard draft', 'error');
      }
    } catch {
      onNotify('Network error discarding draft', 'error');
    } finally {
      setDiscarding(false);
    }
  }, [apiFetch, onNotify, fetchStatus]);

  // Don't render if no pending changes
  if (!status?.has_pending_changes) return null;

  return (
    <div style={bannerStyle}>
      <div style={contentStyle}>
        <div style={textStyle}>
          <span style={iconStyle}>●</span>
          You have configuration changes that are not yet live.
          {status.draft_version != null && (
            <span style={versionStyle}> (draft v{status.draft_version})</span>
          )}
        </div>
        <div style={actionsStyle}>
          <button
            onClick={onActivate}
            style={activateButtonStyle}
          >
            Activate
          </button>
          <button
            onClick={handleDiscard}
            disabled={discarding}
            style={discardButtonStyle}
          >
            {discarding ? 'Discarding…' : 'Discard'}
          </button>
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Styles (inline, matching dark theme)
// ---------------------------------------------------------------------------

const bannerStyle: React.CSSProperties = {
  backgroundColor: '#1c1917',
  borderBottom: '1px solid #3B82F6',
  padding: '10px 20px',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
};

const contentStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  width: '100%',
  maxWidth: '1200px',
  gap: '16px',
};

const textStyle: React.CSSProperties = {
  color: '#e0e0e0',
  fontSize: '14px',
  lineHeight: '1.4',
};

const iconStyle: React.CSSProperties = {
  color: '#3B82F6',
  marginRight: '8px',
  fontSize: '10px',
};

const versionStyle: React.CSSProperties = {
  color: '#888',
  fontSize: '12px',
};

const actionsStyle: React.CSSProperties = {
  display: 'flex',
  gap: '8px',
  flexShrink: 0,
};

const activateButtonStyle: React.CSSProperties = {
  backgroundColor: '#2b8a3e',
  color: '#fff',
  border: 'none',
  borderRadius: '6px',
  padding: '6px 16px',
  fontSize: '13px',
  fontWeight: 600,
  cursor: 'pointer',
};

const discardButtonStyle: React.CSSProperties = {
  backgroundColor: 'transparent',
  color: '#888',
  border: '1px solid #333',
  borderRadius: '6px',
  padding: '6px 16px',
  fontSize: '13px',
  cursor: 'pointer',
};
