// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
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
import { tokens, dialog, button } from './theme/styles';

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
    <div style={dialog.overlay} onClick={onClose}>
      <div style={dialogPanel} onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div style={headerStyle}>
          <h2 style={dialog.title}>Restore previous configuration</h2>
          <button onClick={onClose} style={dialog.closeButton}>✕</button>
        </div>

        {/* Content */}
        <div style={bodyStyle}>
          <div style={warningBoxStyle}>
            <div style={warningIconStyle}>⚠</div>
            <div>
              <div style={dialog.warningText}>
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
          <button onClick={onClose} style={dialog.cancelButton}>Cancel</button>
          <button
            onClick={handleRestore}
            disabled={restoring}
            style={{
              ...button.action,
              ...(restoring ? button.disabled : {}),
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
// Local style overrides
// ---------------------------------------------------------------------------

const dialogPanel: React.CSSProperties = {
  ...dialog.panel(480),
  display: 'flex',
  flexDirection: 'column',
};

const headerStyle: React.CSSProperties = {
  ...dialog.header,
  padding: '20px 24px 16px',
};

const bodyStyle: React.CSSProperties = {
  padding: '20px 24px',
};

const warningBoxStyle: React.CSSProperties = {
  ...dialog.warningBox,
  display: 'flex',
  gap: '12px',
  padding: '14px 16px',
};

const warningIconStyle: React.CSSProperties = {
  fontSize: '20px',
  lineHeight: '1.4',
  flexShrink: 0,
};

const detailTextStyle: React.CSSProperties = {
  color: tokens.textMuted,
  fontSize: '13px',
  marginTop: '6px',
};

const noteStyle: React.CSSProperties = {
  color: tokens.textMuted,
  fontSize: '13px',
  lineHeight: '1.5',
};

const footerStyle: React.CSSProperties = {
  ...dialog.footer,
  padding: '16px 24px',
};
