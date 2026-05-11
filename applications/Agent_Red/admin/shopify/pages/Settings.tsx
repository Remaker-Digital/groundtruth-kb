// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * Settings page — Shopify embedded admin.
 *
 * Renders TeamManager shared component + GDPR controls.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useCallback, useState } from 'react';
import { Page } from '@shopify/polaris';
import { useAppContext } from '../layouts/ShopifyAppLayout';
import { TeamManager } from '../../shared/TeamManager';

export const SettingsPage: React.FC = () => {
  const { tenantContext, apiFetch, onNotify } = useAppContext();
  const [gdprLoading, setGdprLoading] = useState(false);

  const handleExportData = useCallback(async () => {
    setGdprLoading(true);
    try {
      const resp = await apiFetch('/api/admin/gdpr/export', { method: 'POST' });
      if (!resp.ok) throw new Error('Export failed');
      onNotify('Data export initiated. You will receive a download link.', 'success');
    } catch {
      onNotify('Data export failed. Please try again.', 'error');
    } finally {
      setGdprLoading(false);
    }
  }, [apiFetch, onNotify]);

  if (!tenantContext) return null;

  return (
    <Page title="Settings">
      <div style={{ marginBottom: '24px' }}>
        <TeamManager
          tenantContext={tenantContext}
          apiFetch={apiFetch}
          onNotify={onNotify}
        />
      </div>

      {/* GDPR Section */}
      <div
        style={{
          border: '1px solid #e1e3e5',
          borderRadius: '8px',
          padding: '20px',
          backgroundColor: '#fafbfb',
        }}
      >
        <h2 style={{ margin: '0 0 8px', fontSize: '16px', fontWeight: 600 }}>
          Data & Privacy
        </h2>
        <p style={{ margin: '0 0 16px', color: '#6d7175', fontSize: '14px' }}>
          Export or delete your data in compliance with GDPR requirements.
        </p>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button
            onClick={handleExportData}
            disabled={gdprLoading}
            style={{
              padding: '8px 16px',
              backgroundColor: '#ffffff',
              border: '1px solid #c9cccf',
              borderRadius: '4px',
              cursor: gdprLoading ? 'default' : 'pointer',
              fontSize: '14px',
              color: '#202223',
            }}
          >
            {gdprLoading ? 'Exporting...' : 'Export My Data'}
          </button>
        </div>
      </div>
    </Page>
  );
};
