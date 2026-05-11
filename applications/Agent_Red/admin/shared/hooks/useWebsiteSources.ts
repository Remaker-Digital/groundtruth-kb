/**
 * Website Sources hooks — CRUD + crawl trigger for automated website crawling.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { useState, useCallback } from 'react';
import { useApi } from './useApi';
import type { ApiFetch } from './useApi';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface WebsiteSource {
  id: string;
  tenantId: string;
  domain: string;
  startUrl: string;
  maxPages: number;
  entryType: string;
  autoRefresh: boolean;
  refreshIntervalHours: number;
  status: string;
  lastCrawledAt: string | null;
  nextCrawlAt: string | null;
  pagesDiscovered: number;
  pagesCrawled: number;
  articlesCreated: number;
  totalChars: number;
  errorMessage: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface WebsiteSourceList {
  tenantId: string;
  sources: WebsiteSource[];
  totalCount: number;
}

export interface WebsiteSourceAction {
  success: boolean;
  message: string;
  sourceId: string | null;
}

// ---------------------------------------------------------------------------
// List hook
// ---------------------------------------------------------------------------

export function useWebsiteSources(apiFetch: ApiFetch) {
  return useApi<WebsiteSourceList>(apiFetch, '/api/admin/knowledge/sources');
}

// ---------------------------------------------------------------------------
// Create hook
// ---------------------------------------------------------------------------

export function useCreateWebsiteSource(apiFetch: ApiFetch) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const create = useCallback(
    async (payload: {
      startUrl: string;
      maxPages?: number;
      autoRefresh?: boolean;
      refreshIntervalHours?: number;
    }): Promise<WebsiteSource | null> => {
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
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Create failed';
        setError(msg);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [apiFetch],
  );

  return { create, loading, error };
}

// ---------------------------------------------------------------------------
// Update hook
// ---------------------------------------------------------------------------

export function useUpdateWebsiteSource(apiFetch: ApiFetch) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const update = useCallback(
    async (
      sourceId: string,
      payload: {
        maxPages?: number;
        autoRefresh?: boolean;
        refreshIntervalHours?: number;
        status?: string;
      },
    ): Promise<WebsiteSource | null> => {
      setLoading(true);
      setError(null);
      try {
        const body: Record<string, unknown> = {};
        if (payload.maxPages != null) body.max_pages = payload.maxPages;
        if (payload.autoRefresh != null) body.auto_refresh = payload.autoRefresh;
        if (payload.refreshIntervalHours != null) body.refresh_interval_hours = payload.refreshIntervalHours;
        if (payload.status != null) body.status = payload.status;

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
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Update failed';
        setError(msg);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [apiFetch],
  );

  return { update, loading, error };
}

// ---------------------------------------------------------------------------
// Delete hook
// ---------------------------------------------------------------------------

export function useDeleteWebsiteSource(apiFetch: ApiFetch) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const remove = useCallback(
    async (sourceId: string): Promise<WebsiteSourceAction | null> => {
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
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Delete failed';
        setError(msg);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [apiFetch],
  );

  return { remove, loading, error };
}

// ---------------------------------------------------------------------------
// Trigger crawl hook
// ---------------------------------------------------------------------------

export function useTriggerCrawl(apiFetch: ApiFetch) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const trigger = useCallback(
    async (sourceId: string): Promise<WebsiteSourceAction | null> => {
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
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Crawl trigger failed';
        setError(msg);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [apiFetch],
  );

  return { trigger, loading, error };
}
