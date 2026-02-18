/**
 * LoadingSpinner — centered spinner with a text label, used while KB data loads.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React from 'react';
import { COLOR_TEXT_SECONDARY, COLOR_BORDER, BRAND_PRIMARY } from './styles';

export interface LoadingSpinnerProps {
  text?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ text = 'Loading...' }) => (
  <div
    style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '48px 16px',
      color: COLOR_TEXT_SECONDARY,
    }}
  >
    <div
      style={{
        width: '32px',
        height: '32px',
        border: `3px solid ${COLOR_BORDER}`,
        borderTopColor: BRAND_PRIMARY,
        borderRadius: '50%',
        animation: 'kbSpin 0.8s linear infinite',
        marginBottom: '12px',
      }}
    />
    <span style={{ fontSize: '14px' }}>{text}</span>
    <style>{`@keyframes kbSpin { to { transform: rotate(360deg); } }`}</style>
  </div>
);
