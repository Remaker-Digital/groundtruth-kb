/**
 * Inbox page — Standalone admin.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React from 'react';
import { useAppContext } from '../layouts/StandaloneLayout';
import { ConversationInbox } from '../../shared/ConversationInbox';

export const InboxPage: React.FC = () => {
  const { tenantContext, apiFetch, onNotify } = useAppContext();
  if (!tenantContext) return null;

  return (
    <div>
      <h1 style={{ margin: '0 0 24px', fontSize: '24px', fontWeight: 600, color: '#1a1a1a' }}>
        Conversation Inbox
      </h1>
      <ConversationInbox tenantContext={tenantContext} apiFetch={apiFetch} onNotify={onNotify} />
    </div>
  );
};
