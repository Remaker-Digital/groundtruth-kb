/**
 * ConfirmDialog — Reusable confirmation modal for destructive or important actions.
 *
 * Generic dialog used across all admin pages when an action requires explicit
 * user confirmation before proceeding (delete, deactivate, disconnect, etc.).
 *
 * Props:
 *   - open         — whether the dialog is visible
 *   - title        — dialog heading
 *   - message      — body text (string or ReactNode for richer content)
 *   - confirmLabel — text on the confirm button (default: "Confirm")
 *   - cancelLabel  — text on the cancel button (default: "Cancel")
 *   - variant      — "destructive" (red) or "primary" (brand) or "default" (neutral)
 *   - loading      — disables confirm button and shows loading text
 *   - onConfirm    — called when user clicks confirm
 *   - onCancel     — called when user clicks cancel or overlay
 *
 * Usage:
 *   <ConfirmDialog
 *     open={showDelete}
 *     title="Delete article"
 *     message="This article will be permanently removed. This action cannot be undone."
 *     confirmLabel="Delete"
 *     variant="destructive"
 *     loading={deleting}
 *     onConfirm={handleDelete}
 *     onCancel={() => setShowDelete(false)}
 *   />
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React from 'react';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface ConfirmDialogProps {
  open: boolean;
  title: string;
  message: React.ReactNode;
  confirmLabel?: string;
  cancelLabel?: string;
  variant?: 'destructive' | 'primary' | 'default';
  loading?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function ConfirmDialog({
  open,
  title,
  message,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  variant = 'default',
  loading = false,
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  if (!open) return null;

  const confirmColor = VARIANT_COLORS[variant];
  const loadingLabel = confirmLabel.endsWith('e')
    ? confirmLabel.slice(0, -1) + 'ing\u2026'
    : confirmLabel + 'ing\u2026';

  return (
    <div style={overlayStyle} onClick={onCancel}>
      <div style={dialogStyle} onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div style={headerStyle}>
          <h2 style={titleStyle}>{title}</h2>
          <button onClick={onCancel} style={closeButtonStyle} aria-label="Close">
            ✕
          </button>
        </div>

        {/* Body */}
        <div style={bodyStyle}>
          {typeof message === 'string' ? (
            <p style={messageStyle}>{message}</p>
          ) : (
            message
          )}
        </div>

        {/* Footer */}
        <div style={footerStyle}>
          <button onClick={onCancel} style={cancelButtonStyle}>
            {cancelLabel}
          </button>
          <button
            onClick={onConfirm}
            disabled={loading}
            style={{
              ...confirmButtonStyle,
              backgroundColor: confirmColor,
              opacity: loading ? 0.5 : 1,
              cursor: loading ? 'not-allowed' : 'pointer',
            }}
          >
            {loading ? loadingLabel : confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Variant colors
// ---------------------------------------------------------------------------

const VARIANT_COLORS: Record<string, string> = {
  destructive: '#D32F2F',
  primary: '#3B82F6',
  default: '#444',
};

// ---------------------------------------------------------------------------
// Styles (inline, dark theme — matches RestoreDialog / ActivationDialog)
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
  maxWidth: '440px',
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

const messageStyle: React.CSSProperties = {
  color: '#c0c0c0',
  fontSize: '14px',
  lineHeight: '1.6',
  margin: 0,
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

const confirmButtonStyle: React.CSSProperties = {
  color: '#fff',
  border: 'none',
  borderRadius: '6px',
  padding: '8px 20px',
  fontSize: '13px',
  fontWeight: 600,
};
