// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * Widget page — Shopify embedded admin.
 *
 * Renders WidgetConfigurator shared component.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React from 'react';
import { Page } from '@shopify/polaris';
import { useAppContext } from '../layouts/ShopifyAppLayout';
import { WidgetConfigurator } from '../../shared/WidgetConfigurator';

export const WidgetPage: React.FC = () => {
  const { tenantContext, apiFetch, onNotify } = useAppContext();

  if (!tenantContext) return null;

  return (
    <Page title="Widget configuration">
      <WidgetConfigurator
        tenantContext={tenantContext}
        apiFetch={apiFetch}
        onNotify={onNotify}
      />
    </Page>
  );
};
