// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * ConfirmRemoveDialog — Modal confirmation for removing a team member.
 *
 * Extracted from TeamManager.tsx. Presentational component: receives the
 * member to remove, loading state, and confirm/cancel callbacks as props.
 *
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React from 'react';
import type { ConfirmRemoveDialogProps } from './types';

export const ConfirmRemoveDialog: React.FC<ConfirmRemoveDialogProps> = ({
  member,
  styles: s,
  actionLoading,
  onConfirm,
  onCancel,
}) => {
  return (
    <div
      style={s.overlay}
      onClick={() => {
        if (!actionLoading) onCancel();
      }}
    >
      <div style={s.modal} onClick={(e) => e.stopPropagation()}>
        <h4 style={s.modalTitle}>Remove team member</h4>
        <p style={s.modalBody}>
          Are you sure you want to permanently remove <strong>{member.displayName || member.email}</strong> ({member.email})?
          Their API key will be revoked and they will lose all access immediately.
          This action cannot be undone — to restore access, you must re-invite them.
        </p>
        <div style={s.modalActions}>
          <button
            style={s.modalCancel}
            onClick={onCancel}
            disabled={actionLoading}
          >
            Cancel
          </button>
          <button
            style={{
              ...s.modalConfirm,
              ...(actionLoading ? { opacity: 0.6, cursor: 'not-allowed' } : {}),
            }}
            onClick={onConfirm}
            disabled={actionLoading}
          >
            {actionLoading ? 'Removing...' : 'Remove member'}
          </button>
        </div>
      </div>
    </div>
  );
};
