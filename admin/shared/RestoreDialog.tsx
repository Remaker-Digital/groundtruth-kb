/**
 * RestoreDialog — Confirmation modal for restoring the previous activation snapshot.
 *
 * Shows the previous activation timestamp and a summary of what will change.
 * Accessible from a "Restore previous configuration" option in the settings area.
 *
 * API endpoints consumed:
 *   POST /api/config/restore — Execute restore
 *
 * Props:
 *   - apiFetch        — shell-provided fetch wrapper
 *   - onNotify        — shell toast callback
 *   - onClose         — close the dialog
 *   - onSuccess       — called after successful restore (trigger banner refresh)
 *   - activeVersion   — current active version number
 *   - activeActivatedAt — current active activation timestamp (ISO 8601)
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useCallback, useState } from 'react';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface RestoreResult {
  success: boolean;
  restored_version: number;
  restored_activated_at: string | null;
  error: string | null;
}

interface RestoreDialogProps {
  apiFetch: (path: string, init?: RequestInit) => Promise<Response>;
  onNotify: (message: string, type: 'success' | 'error' | 'warning' | 'info') => void;
  onClose: () => void;
  onSuccess: () => void;
  activeVersion: number;
  activeActivatedAt: string | null;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function RestoreDialog({
  apiFetch,
  onNotify,
  onClose,
  onSuccess,
  activeVersion,
  activeActivatedAt,
}: RestoreDialogProps) {
  const [restoring, setRestoring] = useState(false);

  const handleRestore = useCallback(async () => {
    setRestoring(true);
    try {
      const res = await apiFetch('/api/config/restore', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: '{}',
      });
      if (res.ok) {
        const result: RestoreResult = await res.json();
        if (result.success) {
          onNotify(
            `Restored to previous configuration (v${result.restored_version})`,
            'success',
          );
          onSuccess();
          onClose();
        } else {
          onNotify(result.error ?? 'Restore failed', 'error');
        }
      } else {
        const body = await res.json().catch(() => ({ detail: 'Restore failed' }));
        onNotify(body.detail ?? 'Restore failed', 'error');
      }
    } catch {
      onNotify('Network error during restore', 'error');
    } finally {
      setRestoring(false);
    }
  }, [apiFetch, onNotify, onClose, onSuccess]);

  const formattedDate = activeActivatedAt
    ? new Date(activeActivatedAt).toLocaleString()
    : 'Unknown';

  return (
    <div style={overlayStyle} onClick={onClose}>
      <div style={dialogStyle} onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div style={headerStyle}>
          <h2 style={titleStyle}>Restore previous configuration</h2>
          <button onClick={onClose} style={closeButtonStyle}>✕</button>
        </div>

        {/* Content */}
        <div style={bodyStyle}>
          <div style={warningBoxStyle}>
            <div style={warningIconStyle}>⚠</div>
            <div>
              <div style={warningTextStyle}>
                This will replace the current active configuration with the
                previously activated version.
              </div>
              <div style={detailTextStyle}>
                Current active: v{activeVersion}
                {activeActivatedAt && ` (activated ${formattedDate})`}
              </div>
            </div>
          </div>

          <div style={noteStyle}>
            The current active configuration will become the "previous" snapshot,
            so you can restore again if needed.
          </div>
        </div>

        {/* Footer */}
        <div style={footerStyle}>
          <button onClick={onClose} style={cancelButtonStyle}>Cancel</button>
          <button
            onClick={handleRestore}
            disabled={restoring}
            style={{
              ...restoreButtonStyle,
              opacity: restoring ? 0.5 : 1,
            }}
          >
            {restoring ? 'Restoring…' : 'Restore now'}
          </button>
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Styles (inline, dark theme)
// ---------------------------------------------------------------------------

const overlayStyle: React.CSSProperties = {
  position: 'fixed',
  inset: 0,
  backgroundColor: 'rgba(0,0,0,0.6)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  zIndex: 9999,
};

const dialogStyle: React.CSSProperties = {
  backgroundColor: '#292524',
  borderRadius: '12px',
  border: '1px solid #44403c',
  width: '90%',
  maxWidth: '480px',
  display: 'flex',
  flexDirection: 'column',
  boxShadow: '0 20px 60px rgba(0,0,0,0.5)',
};

const headerStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: '20px 24px 16px',
  borderBottom: '1px solid #44403c',
};

const titleStyle: React.CSSProperties = {
  color: '#e0e0e0',
  fontSize: '18px',
  fontWeight: 600,
  margin: 0,
};

const closeButtonStyle: React.CSSProperties = {
  background: 'none',
  border: 'none',
  color: '#666',
  fontSize: '18px',
  cursor: 'pointer',
  padding: '4px',
};

const bodyStyle: React.CSSProperties = {
  padding: '20px 24px',
};

const warningBoxStyle: React.CSSProperties = {
  display: 'flex',
  gap: '12px',
  backgroundColor: 'rgba(255,170,0,0.08)',
  borderRadius: '8px',
  padding: '14px 16px',
  marginBottom: '16px',
};

const warningIconStyle: React.CSSProperties = {
  fontSize: '20px',
  lineHeight: '1.4',
  flexShrink: 0,
};

const warningTextStyle: React.CSSProperties = {
  color: '#e0e0e0',
  fontSize: '14px',
  lineHeight: '1.5',
};

const detailTextStyle: React.CSSProperties = {
  color: '#888',
  fontSize: '13px',
  marginTop: '6px',
};

const noteStyle: React.CSSProperties = {
  color: '#888',
  fontSize: '13px',
  lineHeight: '1.5',
};

const footerStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'flex-end',
  gap: '8px',
  padding: '16px 24px',
  borderTop: '1px solid #44403c',
};

const cancelButtonStyle: React.CSSProperties = {
  backgroundColor: 'transparent',
  color: '#888',
  border: '1px solid #333',
  borderRadius: '6px',
  padding: '8px 20px',
  fontSize: '13px',
  cursor: 'pointer',
};

const restoreButtonStyle: React.CSSProperties = {
  backgroundColor: '#3B82F6',
  color: '#fff',
  border: 'none',
  borderRadius: '6px',
  padding: '8px 20px',
  fontSize: '13px',
  fontWeight: 600,
  cursor: 'pointer',
};
