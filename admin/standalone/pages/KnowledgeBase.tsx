/**
 * Knowledge Base page — Standalone admin.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React from 'react';
import { useAppContext } from '../layouts/StandaloneLayout';
import { KnowledgeBaseManager } from '../../shared/KnowledgeBaseManager';

export const KnowledgeBasePage: React.FC = () => {
  const { tenantContext, apiFetch, onNotify } = useAppContext();
  if (!tenantContext) return null;

  return (
    <div>
      <h1 style={{ margin: '0 0 24px', fontSize: '24px', fontWeight: 600, color: '#1a1a1a' }}>
        Knowledge Base
      </h1>
      <KnowledgeBaseManager tenantContext={tenantContext} apiFetch={apiFetch} onNotify={onNotify} />
    </div>
  );
};
