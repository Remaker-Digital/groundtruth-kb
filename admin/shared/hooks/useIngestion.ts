// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * Ingestion hooks — start, monitor, and cancel storefront ingestion jobs.
 *
 * KA-7: Knowledge Automation Admin UI.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { useState, useCallback } from 'react';
import { useApi } from './useApi';
import type { ApiFetch } from './useApi';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface IngestionJob {
  id: string;
  tenantId: string;
  jobType: 'shopify' | 'url' | 'category_template';
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  progressPercent: number;
  articlesCreated: number;
  articlesFailed: number;
  totalChars: number;
  pagesCrawled: number;
  errorMessage: string | null;
  createdAt: string;
  startedAt: string | null;
  completedAt: string | null;
}

export interface CategoryTemplate {
  id: string;
  name: string;
  description: string;
  articleCount: number;
  suggestedBrandVoice: string | null;
  suggestedEscalationKeywords: string[] | null;
}

export interface TemplateApplyResult {
  articlesCreated: number;
  articlesFailed: number;
  totalChars: number;
  configSuggestions: Record<string, unknown> | null;
}

// ---------------------------------------------------------------------------
// Hooks
// ---------------------------------------------------------------------------

/** Get the current/latest ingestion job status. */
export function useIngestionStatus(apiFetch: ApiFetch) {
  return useApi<IngestionJob | null>(apiFetch, '/api/admin/knowledge/ingest/status');
}

/** List available category templates. */
export function useTemplates(apiFetch: ApiFetch) {
  return useApi<CategoryTemplate[]>(apiFetch, '/api/admin/knowledge/templates');
}

/** Start an ingestion job. */
export function useStartIngestion(apiFetch: ApiFetch) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const start = useCallback(
    async (sourceType: string, options?: { url?: string; maxPages?: number; categoryId?: string }): Promise<IngestionJob | null> => {
      setLoading(true);
      setError(null);
      try {
        const body: Record<string, unknown> = { sourceType };
        if (options?.url) body.url = options.url;
        if (options?.maxPages) body.maxPages = options.maxPages;
        if (options?.categoryId) body.categoryId = options.categoryId;

        const resp = await apiFetch('/api/admin/knowledge/ingest', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        });
        if (!resp.ok) {
          const data = await resp.json().catch(() => ({ detail: `${resp.status}` }));
          throw new Error(data.detail || `Start failed: ${resp.status}`);
        }
        return await resp.json();
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Start failed';
        setError(msg);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [apiFetch],
  );

  return { start, loading, error };
}

/** Cancel the current ingestion job. */
export function useCancelIngestion(apiFetch: ApiFetch) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const cancel = useCallback(async (): Promise<boolean> => {
    setLoading(true);
    setError(null);
    try {
      const resp = await apiFetch('/api/admin/knowledge/ingest/cancel', {
        method: 'POST',
      });
      if (!resp.ok) {
        const data = await resp.json().catch(() => ({ detail: `${resp.status}` }));
        throw new Error(data.detail || `Cancel failed: ${resp.status}`);
      }
      return true;
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Cancel failed';
      setError(msg);
      return false;
    } finally {
      setLoading(false);
    }
  }, [apiFetch]);

  return { cancel, loading, error };
}

/** Apply a category template to the tenant's KB. */
export function useApplyTemplate(apiFetch: ApiFetch) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const apply = useCallback(
    async (categoryId: string): Promise<TemplateApplyResult | null> => {
      setLoading(true);
      setError(null);
      try {
        const resp = await apiFetch(`/api/admin/knowledge/templates/${categoryId}/apply`, {
          method: 'POST',
        });
        if (!resp.ok) {
          const data = await resp.json().catch(() => ({ detail: `${resp.status}` }));
          throw new Error(data.detail || `Apply failed: ${resp.status}`);
        }
        return await resp.json();
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Apply failed';
        setError(msg);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [apiFetch],
  );

  return { apply, loading, error };
}
