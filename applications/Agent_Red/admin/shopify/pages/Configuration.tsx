// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * Configuration page — Shopify embedded admin.
 *
 * Shows ConfigEditor for agent configuration. Changes are saved as DRAFT
 * and go live via the ActivationBanner/Dialog flow.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React from 'react';
import { Page } from '@shopify/polaris';
import { useAppContext } from '../layouts/ShopifyAppLayout';
import { ConfigEditor } from '../../shared/ConfigEditor';

export const ConfigurationPage: React.FC = () => {
  const { tenantContext, apiFetch, onNotify } = useAppContext();

  if (!tenantContext) return null;

  return (
    <Page title="Agent configuration">
      <ConfigEditor tenantContext={tenantContext} apiFetch={apiFetch} onNotify={onNotify} />
    </Page>
  );
};
