/**
 * EmptyState — centered icon + title + optional subtitle for zero-data views.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React from 'react';
import { COLOR_TEXT, COLOR_TEXT_SECONDARY } from './styles';

export interface EmptyStateProps {
  icon: string;
  title: string;
  subtitle?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({ icon, title, subtitle }) => (
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
    <span style={{ fontSize: '40px', marginBottom: '12px' }}>{icon}</span>
    <span style={{ fontSize: '15px', fontWeight: 600, color: COLOR_TEXT, marginBottom: '4px' }}>{title}</span>
    {subtitle && <span style={{ fontSize: '13px' }}>{subtitle}</span>}
  </div>
);
