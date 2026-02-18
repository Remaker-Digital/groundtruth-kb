/**
 * Inbox hooks — conversation list, messages, search, actions.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { useState, useCallback } from 'react';
import type { InboxConversation, ConversationMessage } from '../types/index';
import { useApi } from './useApi';
import type { ApiFetch } from './useApi';

// ---------------------------------------------------------------------------
// Inbox hooks
// ---------------------------------------------------------------------------

export function useInboxConversations(apiFetch: ApiFetch, archived?: 'only' | 'include') {
  const url = archived
    ? `/api/admin/conversations?archived=${archived}`
    : '/api/admin/conversations';
  return useApi<{ conversations: InboxConversation[] }>(apiFetch, url);
}

export function useConversationMessages(apiFetch: ApiFetch, conversationId: string) {
  return useApi<{ messages: ConversationMessage[] }>(
    apiFetch,
    `/api/admin/conversations/${conversationId}/messages`,
    !!conversationId,
  );
}

export function useAssignConversation(apiFetch: ApiFetch) {
  const [loading, setLoading] = useState(false);

  const assign = useCallback(
    async (conversationId: string, agentId: string) => {
      setLoading(true);
      try {
        await apiFetch(`/api/admin/conversations/${conversationId}/assign`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ agent_id: agentId }),
        });
      } finally {
        setLoading(false);
      }
    },
    [apiFetch],
  );

  return { assign, loading };
}

export interface SearchResult {
  conversation_id: string;
  customer_id: string | null;
  customer_name: string | null;
  status: string | null;
  started_at: string | null;
  last_activity_at: string | null;
  message_count: number;
  snippet: string;
  matched_in: string;
}

export function useSearchConversations(apiFetch: ApiFetch) {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<SearchResult[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  const search = useCallback(
    async (query: string, status?: string) => {
      if (!query.trim()) {
        setResults(null);
        return;
      }
      setLoading(true);
      setError(null);
      try {
        const resp = await apiFetch('/api/admin/conversations/search', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: query.trim(), status, limit: 50 }),
        });
        if (!resp.ok) throw new Error(`Search failed: ${resp.status}`);
        const body = await resp.json();
        setResults(body.results ?? []);
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Search failed';
        setError(msg);
        setResults(null);
      } finally {
        setLoading(false);
      }
    },
    [apiFetch],
  );

  const clearSearch = useCallback(() => {
    setResults(null);
    setError(null);
  }, []);

  return { search, clearSearch, results, loading, error };
}

export function useEscalateConversation(apiFetch: ApiFetch) {
  const [loading, setLoading] = useState(false);

  const escalate = useCallback(
    async (conversationId: string, opts?: { category?: string; agentId?: string }) => {
      setLoading(true);
      try {
        const payload: Record<string, string> = {};
        if (opts?.category) payload.category = opts.category;
        if (opts?.agentId) payload.agent_id = opts.agentId;
        const resp = await apiFetch(`/api/admin/conversations/${conversationId}/escalate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        if (!resp.ok) {
          const body = await resp.json().catch(() => ({ detail: `${resp.status}` }));
          throw new Error(body.detail || `Escalation failed: ${resp.status}`);
        }
        return await resp.json();
      } finally {
        setLoading(false);
      }
    },
    [apiFetch],
  );

  return { escalate, loading };
}

export function useResolveConversation(apiFetch: ApiFetch) {
  const [loading, setLoading] = useState(false);

  const resolve = useCallback(
    async (conversationId: string) => {
      setLoading(true);
      try {
        const resp = await apiFetch(`/api/admin/conversations/${conversationId}/resolve`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({}),
        });
        if (!resp.ok) {
          const body = await resp.json().catch(() => ({ detail: `${resp.status}` }));
          throw new Error(body.detail || `Resolve failed: ${resp.status}`);
        }
        return await resp.json();
      } finally {
        setLoading(false);
      }
    },
    [apiFetch],
  );

  return { resolve, loading };
}

export function useArchiveConversation(apiFetch: ApiFetch) {
  const [loading, setLoading] = useState(false);

  const archive = useCallback(
    async (conversationId: string) => {
      setLoading(true);
      try {
        const resp = await apiFetch(`/api/admin/conversations/${conversationId}/archive`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({}),
        });
        if (!resp.ok) {
          const body = await resp.json().catch(() => ({ detail: `${resp.status}` }));
          throw new Error(body.detail || `Archive failed: ${resp.status}`);
        }
        return await resp.json();
      } finally {
        setLoading(false);
      }
    },
    [apiFetch],
  );

  const unarchive = useCallback(
    async (conversationId: string) => {
      setLoading(true);
      try {
        const resp = await apiFetch(`/api/admin/conversations/${conversationId}/unarchive`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({}),
        });
        if (!resp.ok) {
          const body = await resp.json().catch(() => ({ detail: `${resp.status}` }));
          throw new Error(body.detail || `Unarchive failed: ${resp.status}`);
        }
        return await resp.json();
      } finally {
        setLoading(false);
      }
    },
    [apiFetch],
  );

  return { archive, unarchive, loading };
}
