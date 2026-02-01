/**
 * Billing page — Standalone admin (Stripe-direct merchants).
 *
 * Uses Stripe Customer Portal for billing management.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useCallback } from 'react';
import { useAppContext } from '../layouts/StandaloneLayout';
import { BillingPortal } from '../../shared/BillingPortal';

export const BillingPage: React.FC = () => {
  const { tenantContext, apiFetch, onNotify } = useAppContext();

  const handleManageBilling = useCallback(async () => {
    try {
      const resp = await apiFetch('/api/billing/portal', { method: 'POST' });
      if (!resp.ok) throw new Error('Failed to create portal session');
      const data = await resp.json();
      if (data.url) {
        window.open(data.url, '_blank');
      }
    } catch {
      onNotify('Failed to open billing portal. Please try again.', 'error');
    }
  }, [apiFetch, onNotify]);

  const handlePurchasePack = useCallback(
    async (packSize: number) => {
      try {
        const resp = await apiFetch('/api/packs/purchase', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ pack_size: packSize }),
        });
        if (!resp.ok) throw new Error('Purchase failed');
        const data = await resp.json();
        if (data.url) {
          window.location.href = data.url;
        }
      } catch {
        onNotify('Failed to start purchase. Please try again.', 'error');
      }
    },
    [apiFetch, onNotify],
  );

  if (!tenantContext) return null;

  return (
    <div>
      <h1 style={{ margin: '0 0 24px', fontSize: '24px', fontWeight: 600, color: '#1a1a1a' }}>
        Billing & Usage
      </h1>
      <BillingPortal
        tenantContext={tenantContext}
        apiFetch={apiFetch}
        onNotify={onNotify}
        onManageBilling={handleManageBilling}
        onPurchasePack={handlePurchasePack}
      />
    </div>
  );
};
