/**
 * Inbox hooks — conversation list, messages, search, actions.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { useState, useCallback } from 'react';
import { useApi } from './useApi';
// ---------------------------------------------------------------------------
// Inbox hooks
// ---------------------------------------------------------------------------
export function useInboxConversations(apiFetch, archived) {
    const url = archived
        ? `/api/admin/conversations?archived=${archived}`
        : '/api/admin/conversations';
    return useApi(apiFetch, url);
}
export function useConversationMessages(apiFetch, conversationId) {
    return useApi(apiFetch, `/api/admin/conversations/${conversationId}/messages`, !!conversationId);
}
export function useAssignConversation(apiFetch) {
    const [loading, setLoading] = useState(false);
    const assign = useCallback(async (conversationId, agentId) => {
        setLoading(true);
        try {
            await apiFetch(`/api/admin/conversations/${conversationId}/assign`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ agent_id: agentId }),
            });
        }
        finally {
            setLoading(false);
        }
    }, [apiFetch]);
    return { assign, loading };
}
export function useSearchConversations(apiFetch) {
    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState(null);
    const [error, setError] = useState(null);
    const search = useCallback(async (query, status) => {
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
            if (!resp.ok)
                throw new Error(`Search failed: ${resp.status}`);
            const body = await resp.json();
            setResults(body.results ?? []);
        }
        catch (err) {
            const msg = err instanceof Error ? err.message : 'Search failed';
            setError(msg);
            setResults(null);
        }
        finally {
            setLoading(false);
        }
    }, [apiFetch]);
    const clearSearch = useCallback(() => {
        setResults(null);
        setError(null);
    }, []);
    return { search, clearSearch, results, loading, error };
}
export function useEscalateConversation(apiFetch) {
    const [loading, setLoading] = useState(false);
    const escalate = useCallback(async (conversationId, opts) => {
        setLoading(true);
        try {
            const payload = {};
            if (opts?.category)
                payload.category = opts.category;
            if (opts?.agentId)
                payload.agent_id = opts.agentId;
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
        }
        finally {
            setLoading(false);
        }
    }, [apiFetch]);
    return { escalate, loading };
}
export function useResolveConversation(apiFetch) {
    const [loading, setLoading] = useState(false);
    const resolve = useCallback(async (conversationId) => {
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
        }
        finally {
            setLoading(false);
        }
    }, [apiFetch]);
    return { resolve, loading };
}
export function useArchiveConversation(apiFetch) {
    const [loading, setLoading] = useState(false);
    const archive = useCallback(async (conversationId) => {
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
        }
        finally {
            setLoading(false);
        }
    }, [apiFetch]);
    const unarchive = useCallback(async (conversationId) => {
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
        }
        finally {
            setLoading(false);
        }
    }, [apiFetch]);
    return { archive, unarchive, loading };
}
/** Fetch pipeline trace for a conversation (SPEC-1531). */
export function useConversationTrace(apiFetch, conversationId) {
    return useApi(apiFetch, `/api/admin/conversations/${conversationId}/trace`, !!conversationId);
}
//# sourceMappingURL=useInbox.js.map