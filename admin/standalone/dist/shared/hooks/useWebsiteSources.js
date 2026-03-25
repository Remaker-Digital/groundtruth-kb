/**
 * Website Sources hooks — CRUD + crawl trigger for automated website crawling.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { useState, useCallback } from 'react';
import { useApi } from './useApi';
// ---------------------------------------------------------------------------
// List hook
// ---------------------------------------------------------------------------
export function useWebsiteSources(apiFetch) {
    return useApi(apiFetch, '/api/admin/knowledge/sources');
}
// ---------------------------------------------------------------------------
// Create hook
// ---------------------------------------------------------------------------
export function useCreateWebsiteSource(apiFetch) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const create = useCallback(async (payload) => {
        setLoading(true);
        setError(null);
        try {
            const resp = await apiFetch('/api/admin/knowledge/sources', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    start_url: payload.startUrl,
                    max_pages: payload.maxPages ?? 25,
                    auto_refresh: payload.autoRefresh ?? true,
                    refresh_interval_hours: payload.refreshIntervalHours ?? 24,
                }),
            });
            if (!resp.ok) {
                const body = await resp.json().catch(() => ({ detail: `${resp.status}` }));
                throw new Error(body.detail || `Failed: ${resp.status}`);
            }
            return await resp.json();
        }
        catch (err) {
            const msg = err instanceof Error ? err.message : 'Create failed';
            setError(msg);
            return null;
        }
        finally {
            setLoading(false);
        }
    }, [apiFetch]);
    return { create, loading, error };
}
// ---------------------------------------------------------------------------
// Update hook
// ---------------------------------------------------------------------------
export function useUpdateWebsiteSource(apiFetch) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const update = useCallback(async (sourceId, payload) => {
        setLoading(true);
        setError(null);
        try {
            const body = {};
            if (payload.maxPages != null)
                body.max_pages = payload.maxPages;
            if (payload.autoRefresh != null)
                body.auto_refresh = payload.autoRefresh;
            if (payload.refreshIntervalHours != null)
                body.refresh_interval_hours = payload.refreshIntervalHours;
            if (payload.status != null)
                body.status = payload.status;
            const resp = await apiFetch(`/api/admin/knowledge/sources/${sourceId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body),
            });
            if (!resp.ok) {
                const data = await resp.json().catch(() => ({ detail: `${resp.status}` }));
                throw new Error(data.detail || `Failed: ${resp.status}`);
            }
            return await resp.json();
        }
        catch (err) {
            const msg = err instanceof Error ? err.message : 'Update failed';
            setError(msg);
            return null;
        }
        finally {
            setLoading(false);
        }
    }, [apiFetch]);
    return { update, loading, error };
}
// ---------------------------------------------------------------------------
// Delete hook
// ---------------------------------------------------------------------------
export function useDeleteWebsiteSource(apiFetch) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const remove = useCallback(async (sourceId) => {
        setLoading(true);
        setError(null);
        try {
            const resp = await apiFetch(`/api/admin/knowledge/sources/${sourceId}`, {
                method: 'DELETE',
            });
            if (!resp.ok) {
                const data = await resp.json().catch(() => ({ detail: `${resp.status}` }));
                throw new Error(data.detail || `Failed: ${resp.status}`);
            }
            return await resp.json();
        }
        catch (err) {
            const msg = err instanceof Error ? err.message : 'Delete failed';
            setError(msg);
            return null;
        }
        finally {
            setLoading(false);
        }
    }, [apiFetch]);
    return { remove, loading, error };
}
// ---------------------------------------------------------------------------
// Trigger crawl hook
// ---------------------------------------------------------------------------
export function useTriggerCrawl(apiFetch) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const trigger = useCallback(async (sourceId) => {
        setLoading(true);
        setError(null);
        try {
            const resp = await apiFetch(`/api/admin/knowledge/sources/${sourceId}/crawl`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({}),
            });
            if (!resp.ok) {
                const data = await resp.json().catch(() => ({ detail: `${resp.status}` }));
                throw new Error(data.detail || `Failed: ${resp.status}`);
            }
            return await resp.json();
        }
        catch (err) {
            const msg = err instanceof Error ? err.message : 'Crawl trigger failed';
            setError(msg);
            return null;
        }
        finally {
            setLoading(false);
        }
    }, [apiFetch]);
    return { trigger, loading, error };
}
//# sourceMappingURL=useWebsiteSources.js.map