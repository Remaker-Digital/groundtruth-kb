/**
 * KBStalenessBadge — displays a colored pill badge for a KB article's freshness
 * category (Fresh / Aging / Stale / Very stale).
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React from 'react';
import { COLOR_LIGHT_GRAY, COLOR_GRAY, STALENESS_BADGE_STYLES } from './styles';

export interface KBStalenessBadgeProps {
  category: string | null | undefined;
}

export const KBStalenessBadge: React.FC<KBStalenessBadgeProps> = ({ category }) => {
  if (!category) {
    return (
      <span
        style={{
          display: 'inline-block',
          fontSize: '11px',
          fontWeight: 600,
          padding: '2px 8px',
          borderRadius: '10px',
          backgroundColor: COLOR_LIGHT_GRAY,
          color: COLOR_GRAY,
        }}
      >
        --
      </span>
    );
  }
  const style = STALENESS_BADGE_STYLES[category] ?? STALENESS_BADGE_STYLES.fresh;
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
