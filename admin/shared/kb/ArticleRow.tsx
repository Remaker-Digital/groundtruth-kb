/**
 * ArticleRow — a single table row in the KB article list, showing title,
 * category, status badge, staleness badge, last-updated date, and a
 * conditional "Verify" action button.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React from 'react';
import type { KBArticle } from '../types';
import { KBStatusBadge } from './KBStatusBadge';
import { KBStalenessBadge } from './KBStalenessBadge';
import { formatDate } from './utils';
import {
  COLOR_LIGHT_GRAY,
  COLOR_WHITE,
  COLOR_BORDER,
  COLOR_TEXT,
  COLOR_TEXT_SECONDARY,
  COLOR_SUCCESS,
  BORDER_RADIUS,
  FONT_FAMILY,
} from './styles';

export interface ArticleRowProps {
  article: KBArticle;
  onClick: () => void;
  onVerify?: (id: string) => void;
  verifying?: boolean;
}

export const ArticleRow: React.FC<ArticleRowProps> = ({ article, onClick, onVerify, verifying }) => (
  <tr
    onClick={onClick}
    style={{ cursor: 'pointer', transition: 'background-color 0.15s ease' }}
    onMouseEnter={(e) => {
      (e.currentTarget as HTMLElement).style.backgroundColor = COLOR_LIGHT_GRAY;
    }}
    onMouseLeave={(e) => {
      (e.currentTarget as HTMLElement).style.backgroundColor = COLOR_WHITE;
    }}
  >
    <td style={{ padding: '12px 16px', borderBottom: `1px solid ${COLOR_BORDER}` }}>
      <span style={{ fontSize: '14px', fontWeight: 500, color: COLOR_TEXT }}>{article.title}</span>
    </td>
    <td style={{ padding: '12px 16px', borderBottom: `1px solid ${COLOR_BORDER}` }}>
      <span
        style={{
          fontSize: '12px',
          color: COLOR_TEXT_SECONDARY,
          backgroundColor: COLOR_LIGHT_GRAY,
          padding: '2px 8px',
          borderRadius: '10px',
        }}
      >
        {article.category || 'Uncategorized'}
      </span>
    </td>
    <td style={{ padding: '12px 16px', borderBottom: `1px solid ${COLOR_BORDER}` }}>
      <KBStatusBadge status={article.status} isActive={article.is_active} />
    </td>
    <td style={{ padding: '12px 16px', borderBottom: `1px solid ${COLOR_BORDER}` }}>
      <KBStalenessBadge category={article.stalenessCategory} />
    </td>
    <td
      style={{
        padding: '12px 16px',
        borderBottom: `1px solid ${COLOR_BORDER}`,
        fontSize: '13px',
        color: COLOR_TEXT_SECONDARY,
      }}
    >
      {formatDate(article.updatedAt)}
    </td>
    <td
      style={{
        padding: '12px 16px',
        borderBottom: `1px solid ${COLOR_BORDER}`,
      }}
    >
      {onVerify && (article.stalenessCategory === 'stale' || article.stalenessCategory === 'aging' || article.stalenessCategory === 'very_stale') && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            onVerify(article.id);
          }}
          disabled={verifying}
          style={{
            padding: '4px 10px',
            border: `1px solid ${COLOR_SUCCESS}`,
            borderRadius: BORDER_RADIUS,
            backgroundColor: 'transparent',
            color: COLOR_SUCCESS,
            fontSize: '11px',
            fontFamily: FONT_FAMILY,
            fontWeight: 500,
            cursor: verifying ? 'not-allowed' : 'pointer',
            opacity: verifying ? 0.6 : 1,
            whiteSpace: 'nowrap' as const,
          }}
        >
          {verifying ? 'Verifying...' : 'Verify'}
        </button>
      )}
    </td>
  </tr>
);
