/**
 * ErrorBanner — inline error message with an optional Retry button.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React from 'react';
import { COLOR_DANGER, COLOR_BORDER, BORDER_RADIUS, FONT_FAMILY } from './styles';

export interface ErrorBannerProps {
  message: string;
  onRetry?: () => void;
}

export const ErrorBanner: React.FC<ErrorBannerProps> = ({ message, onRetry }) => (
  <div
    style={{
      padding: '12px 16px',
      backgroundColor: '#ffeef0',
      border: `1px solid ${COLOR_DANGER}33`,
      borderRadius: BORDER_RADIUS,
      margin: '16px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      gap: '12px',
    }}
  >
    <span style={{ fontSize: '13px', color: COLOR_DANGER }}>{message}</span>
    {onRetry && (
      <button
        onClick={onRetry}
        style={{
          padding: '4px 12px',
          border: `1px solid ${COLOR_DANGER}`,
          borderRadius: BORDER_RADIUS,
          backgroundColor: 'transparent',
          color: COLOR_DANGER,
          fontSize: '12px',
          fontFamily: FONT_FAMILY,
          cursor: 'pointer',
          whiteSpace: 'nowrap',
        }}
      >
        Retry
      </button>
    )}
  </div>
);
