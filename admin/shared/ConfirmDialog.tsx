// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
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
import { tokens, dialog, button } from './theme/styles';

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
// Variant colors
// ---------------------------------------------------------------------------

const VARIANT_COLORS: Record<string, string> = {
  destructive: tokens.danger,
  primary: tokens.action,
  default: tokens.border,
};

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
    <div style={dialog.overlay} onClick={onCancel}>
      <div style={dialogPanel} onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div style={headerStyle}>
          <h2 style={dialog.title}>{title}</h2>
          <button onClick={onCancel} style={dialog.closeButton} aria-label="Close">
            ✕
          </button>
        </div>

        {/* Body */}
        <div style={bodyStyle}>
          {typeof message === 'string' ? (
            <p style={dialog.message}>{message}</p>
          ) : (
            message
          )}
        </div>

        {/* Footer */}
        <div style={footerStyle}>
          <button onClick={onCancel} style={dialog.cancelButton}>
            {cancelLabel}
          </button>
          <button
            onClick={onConfirm}
            disabled={loading}
            style={{
              ...button.action,
              backgroundColor: confirmColor,
              ...(loading ? button.disabled : {}),
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
// Local style overrides (structure differs from shared dialog.* patterns)
// ---------------------------------------------------------------------------

const dialogPanel: React.CSSProperties = {
  ...dialog.panel(440),
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

const footerStyle: React.CSSProperties = {
  ...dialog.footer,
  padding: '16px 24px',
};
