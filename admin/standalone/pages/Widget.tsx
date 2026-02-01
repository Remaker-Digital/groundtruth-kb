/**
 * Widget page — Standalone admin.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React from 'react';
import { useAppContext } from '../layouts/StandaloneLayout';
import { WidgetConfigurator } from '../../shared/WidgetConfigurator';

export const WidgetPage: React.FC = () => {
  const { tenantContext, apiFetch, onNotify } = useAppContext();
  if (!tenantContext) return null;

  return (
    <div>
      <h1 style={{ margin: '0 0 24px', fontSize: '24px', fontWeight: 600, color: '#1a1a1a' }}>
        Widget Appearance
      </h1>
      <WidgetConfigurator tenantContext={tenantContext} apiFetch={apiFetch} onNotify={onNotify} />
    </div>
  );
};
