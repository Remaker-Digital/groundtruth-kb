/**
 * Billing page — Shopify embedded admin.
 *
 * Renders BillingPortal shared component with Shopify-specific billing management.
 * Uses App Bridge redirect to Shopify billing page.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useCallback } from 'react';
import { Page } from '@shopify/polaris';
import { useAppContext } from '../layouts/ShopifyAppLayout';
import { BillingPortal } from '../../shared/BillingPortal';

export const BillingPage: React.FC = () => {
  const { tenantContext, apiFetch, onNotify } = useAppContext();

  const handleManageBilling = useCallback(() => {
    // App Bridge redirect to Shopify billing settings
    const shopify = (window as unknown as {
      shopify?: { redirect: (url: string) => void };
    }).shopify;
    if (shopify?.redirect) {
      shopify.redirect('shopify://admin/settings/billing');
    }
  }, []);

  const handlePurchasePack = useCallback(
    async (packSize: number) => {
      try {
        const resp = await apiFetch('/api/packs/purchase', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ pack_size: packSize }),
        });
        if (!resp.ok) throw new Error('Purchase failed');
        onNotify(`Conversation pack (${(packSize ?? 0).toLocaleString()}) purchased!`, 'success');
      } catch {
        onNotify('Failed to purchase pack. Please try again.', 'error');
      }
    },
    [apiFetch, onNotify],
  );

  if (!tenantContext) return null;

  return (
    <Page title="Billing & Usage">
      <BillingPortal
        tenantContext={tenantContext}
        apiFetch={apiFetch}
        onNotify={onNotify}
        onManageBilling={handleManageBilling}
        onPurchasePack={handlePurchasePack}
      />
    </Page>
  );
};
