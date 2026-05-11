/**
 * KBStatusBadge — displays a colored pill badge for a KB article's status
 * (Draft / Published / Archived).
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React from 'react';
import type { KBArticleStatus } from '../types';
import { STATUS_BADGE_STYLES } from './styles';

export interface KBStatusBadgeProps {
  status: KBArticleStatus;
  isActive?: boolean;
}

export const KBStatusBadge: React.FC<KBStatusBadgeProps> = ({ status, isActive }) => {
  // Backend may return is_active (boolean) instead of status (string).
  // Derive status from is_active if status is missing.
  const effectiveStatus: KBArticleStatus = status ?? (isActive === false ? 'archived' : 'published');
  const style = STATUS_BADGE_STYLES[effectiveStatus] ?? STATUS_BADGE_STYLES.published;
  return (
    <span
      style={{
        display: 'inline-block',
        fontSize: '11px',
        fontWeight: 600,
        padding: '2px 8px',
        borderRadius: '10px',
        backgroundColor: style.bg,
        color: style.color,
      }}
    >
      {style.label}
    </span>
  );
};
