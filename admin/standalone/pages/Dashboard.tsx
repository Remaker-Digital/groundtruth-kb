/**
 * Dashboard page — Standalone admin.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React from 'react';
import { useAppContext } from '../layouts/StandaloneLayout';
import { AnalyticsOverview } from '../../shared/AnalyticsOverview';
import { UsageDashboard } from '../../shared/UsageDashboard';

export const DashboardPage: React.FC = () => {
  const { tenantContext, apiFetch, onNotify } = useAppContext();
  if (!tenantContext) return null;
  const baseProps = { tenantContext, apiFetch, onNotify };

  return (
    <div>
      <h1 style={{ margin: '0 0 24px', fontSize: '24px', fontWeight: 600, color: '#1a1a1a' }}>
        Dashboard
      </h1>
      <div style={{ marginBottom: '24px' }}>
        <AnalyticsOverview {...baseProps} />
      </div>
      <UsageDashboard {...baseProps} />
    </div>
  );
};
