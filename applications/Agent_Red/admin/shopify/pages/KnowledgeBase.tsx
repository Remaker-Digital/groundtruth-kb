// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * Knowledge Base page — Shopify embedded admin.
 *
 * Renders KnowledgeBaseManager shared component.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React from 'react';
import { Page } from '@shopify/polaris';
import { useAppContext } from '../layouts/ShopifyAppLayout';
import { KnowledgeBaseManager } from '../../shared/KnowledgeBaseManager';

export const KnowledgeBasePage: React.FC = () => {
  const { tenantContext, apiFetch, onNotify } = useAppContext();

  if (!tenantContext) return null;

  return (
    <Page title="Knowledge Base">
      <KnowledgeBaseManager
        tenantContext={tenantContext}
        apiFetch={apiFetch}
        onNotify={onNotify}
      />
    </Page>
  );
};
