/**
 * Knowledge Base hooks — CRUD, upload, import, export, staleness, conflict scan.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { useState, useCallback } from 'react';
import type { KBArticle, KBUploadResult } from '../types/index';
import { useApi } from './useApi';
import type { ApiFetch } from './useApi';

// ---------------------------------------------------------------------------
// Knowledge Base CRUD hooks
// ---------------------------------------------------------------------------

export function useKnowledgeBase(apiFetch: ApiFetch) {
  return useApi<{ articles: KBArticle[] }>(apiFetch, '/api/admin/knowledge');
}

export function useKBArticle(apiFetch: ApiFetch, articleId: string) {
  return useApi<KBArticle>(apiFetch, `/api/admin/knowledge/${articleId}`, !!articleId);
}

export function useSaveKBArticle(apiFetch: ApiFetch) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const save = useCallback(
    async (article: Partial<KBArticle>): Promise<KBArticle | null> => {
      setLoading(true);
      setError(null);
      try {
        const isNew = !article.id;
        const resp = await apiFetch(
          isNew ? '/api/admin/knowledge' : `/api/admin/knowledge/${article.id}`,
          {
            method: isNew ? 'POST' : 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(article),
          },
        );
        if (!resp.ok) throw new Error(`${resp.status}`);
        return await resp.json();
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Save failed';
        setError(msg);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [apiFetch],
  );

  return { save, loading, error };
}

export function useUploadFile(apiFetch: ApiFetch) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState<'idle' | 'uploading' | 'processing' | 'done'>('idle');

  const upload = useCallback(
    async (file: File, entryType?: string): Promise<KBUploadResult | null> => {
      setLoading(true);
      setError(null);
      setProgress('uploading');
      try {
        const formData = new FormData();
        formData.append('file', file);
        if (entryType) formData.append('entry_type', entryType);

        setProgress('processing');
        const resp = await apiFetch('/api/admin/knowledge/upload', {
          method: 'POST',
          body: formData,
        });
        if (!resp.ok) {
          const body = await resp.json().catch(() => ({ detail: `${resp.status}` }));
          throw new Error(body.detail || `Upload failed: ${resp.status}`);
        }
        setProgress('done');
        return await resp.json();
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Upload failed';
        setError(msg);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [apiFetch],
  );

  const reset = useCallback(() => {
    setProgress('idle');
    setError(null);
  }, []);

  return { upload, loading, error, progress, reset };
}

export function useImportUrl(apiFetch: ApiFetch) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const importUrl = useCallback(
    async (url: string, entryType?: string, crawl?: boolean, maxPages?: number): Promise<KBUploadResult | null> => {
      setLoading(true);
      setError(null);
      try {
        const payload: Record<string, unknown> = { url, entry_type: entryType };
        if (crawl) {
          payload.crawl = true;
          if (maxPages != null) payload.max_pages = maxPages;
        }
        const resp = await apiFetch('/api/admin/knowledge/import-url', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        if (!resp.ok) {
          const body = await resp.json().catch(() => ({ detail: `${resp.status}` }));
          throw new Error(body.detail || `Import failed: ${resp.status}`);
        }
        return await resp.json();
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Import failed';
        setError(msg);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [apiFetch],
  );

  return { importUrl, loading, error };
}

export function useExportCSV(apiFetch: ApiFetch) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const exportCSV = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const resp = await apiFetch('/api/admin/knowledge/export');
      if (!resp.ok) throw new Error(`Export failed: ${resp.status}`);
      const blob = await resp.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `knowledge-base-export-${new Date().toISOString().slice(0, 10)}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      return true;
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Export failed';
      setError(msg);
      return false;
    } finally {
      setLoading(false);
    }
  }, [apiFetch]);

  return { exportCSV, loading, error };
}

// ---------------------------------------------------------------------------
// Knowledge Base Staleness hooks (WI #219-222)
// ---------------------------------------------------------------------------

export interface StalenessSummary {
  totalEntries: number;
  avgStalenessScore: number;
  freshCount: number;
  agingCount: number;
  staleCount: number;
  veryStaleCount: number;
  needsAttention: number;
}

export interface StalenessScore {
  id: string;
  stalenessScore: number;
  stalenessCategory: string;
  lastVerifiedAt: string | null;
  embeddedAt: string | null;
}

export function useStalenessSummary(apiFetch: ApiFetch) {
  return useApi<StalenessSummary>(apiFetch, '/api/admin/knowledge/staleness');
}

export function useStaleEntries(apiFetch: ApiFetch, threshold = 0.6) {
  return useApi<{ entries: StalenessScore[]; threshold: number }>(
    apiFetch,
    `/api/admin/knowledge/stale?threshold=${threshold}`,
  );
}

export function useVerifyEntry(apiFetch: ApiFetch) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const verify = useCallback(
    async (entryId: string): Promise<StalenessScore | null> => {
      setLoading(true);
      setError(null);
      try {
        const resp = await apiFetch(`/api/admin/knowledge/${entryId}/verify`, {
          method: 'POST',
        });
        if (!resp.ok) throw new Error(`${resp.status}`);
        return await resp.json();
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Verify failed';
        setError(msg);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [apiFetch],
  );

  return { verify, loading, error };
}

// ---------------------------------------------------------------------------
// KB Conflict Scanner hooks
// ---------------------------------------------------------------------------

export interface ConflictPair {
  entryAId: string;
  entryATitle: string;
  entryBId: string;
  entryBTitle: string;
  conflictType: 'near_duplicate' | 'conflicting' | 'topical_overlap' | 'similar_titles';
  severity: 'high' | 'medium' | 'low';
  embeddingSimilarity: number;
  contentOverlap: number;
  titleSimilarity: number;
  conflictingFacts: string[];
  resolution: string;
}

export interface ScanResult {
  tenantId: string;
  scannedAt: string;
  totalEntriesScanned: number;
  entriesWithEmbeddings: number;
  entriesWithoutEmbeddings: number;
  conflicts: ConflictPair[];
  highCount: number;
  mediumCount: number;
  lowCount: number;
  scanDurationMs: number;
}

export function useConflictScan(apiFetch: ApiFetch) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ScanResult | null>(null);

  const scan = useCallback(
    async (force = false): Promise<ScanResult | null> => {
      setLoading(true);
      setError(null);
      try {
        const resp = await apiFetch(`/api/admin/knowledge/scan?force=${force}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({}),
        });
        if (!resp.ok) throw new Error(`${resp.status}`);
        const data = await resp.json();
        setResult(data);
        return data;
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Scan failed';
        setError(msg);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [apiFetch],
  );

  return { scan, result, loading, error };
}
