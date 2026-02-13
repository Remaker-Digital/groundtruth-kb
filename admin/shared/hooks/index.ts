/**
 * Shared React hooks for the Admin component library.
 *
 * Each hook encapsulates API communication for a specific domain.
 * Shells inject the `apiFetch` function (which handles auth headers)
 * so hooks are auth-agnostic.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import type {
  ConfigReadResult,
  ConfigUpdateResult,
  UsageDashboard,
  DailyVolume,
  ConversationSummary,
  InboxConversation,
  ConversationMessage,
  KBArticle,
  KBUploadResult,
  AnalyticsSummary,
  IntentBreakdown,
  KnowledgeGap,
  TeamMember,
  PaginatedList,
  IntegrationSummary,
  IntegrationDetail,
  IntegrationResponse,
} from '../types/index';

// ---------------------------------------------------------------------------
// Generic fetch hook
// ---------------------------------------------------------------------------

type ApiFetch = (path: string, init?: RequestInit) => Promise<Response>;

interface UseApiResult<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

function useApi<T>(apiFetch: ApiFetch, path: string, enabled = true): UseApiResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tick, setTick] = useState(0);

  const refetch = useCallback(() => setTick((t) => t + 1), []);

  useEffect(() => {
    if (!enabled) return;

    let cancelled = false;
    setLoading(true);
    setError(null);

    apiFetch(path)
      .then(async (resp) => {
        if (cancelled) return;
        if (!resp.ok) {
          const body = await resp.text().catch(() => '');
          throw new Error(`${resp.status}: ${body}`);
        }
        const json = await resp.json();
        setData(json);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message || 'Request failed');
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [apiFetch, path, tick, enabled]);

  return { data, loading, error, refetch };
}

// ---------------------------------------------------------------------------
// Config hooks
// ---------------------------------------------------------------------------

export function useConfig(apiFetch: ApiFetch) {
  return useApi<ConfigReadResult>(apiFetch, '/api/config');
}

export function useConfigSchema(apiFetch: ApiFetch, step?: string) {
  const path = step ? `/api/config/schema/${step}` : '/api/config/schema';
  return useApi<{ fields: Array<Record<string, unknown>> }>(apiFetch, path);
}

export function useConfigVersions(apiFetch: ApiFetch) {
  return useApi<{ versions: Array<Record<string, unknown>> }>(apiFetch, '/api/config/versions');
}

export function useUpdateConfig(apiFetch: ApiFetch) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const updateConfig = useCallback(
    async (changes: Record<string, unknown>): Promise<ConfigUpdateResult | null> => {
      setLoading(true);
      setError(null);
      try {
        const resp = await apiFetch('/api/config', {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ fields: changes }),
        });
        if (!resp.ok) throw new Error(`${resp.status}`);
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

  return { updateConfig, loading, error };
}

// ---------------------------------------------------------------------------
// Named Configuration hooks (C3)
// ---------------------------------------------------------------------------

export interface NamedConfigSummary {
  name: string;
  version: number;
  isActive: boolean;
  isDefault: boolean;
  createdAt: string;
  createdBy: string | null;
  fieldCount: number;
}

export function useNamedConfigs(apiFetch: ApiFetch) {
  return useApi<{ configs: NamedConfigSummary[]; total: number }>(
    apiFetch,
    '/api/config/named',
  );
}

export function useSaveNamedConfig(apiFetch: ApiFetch) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const saveNamed = useCallback(
    async (name: string): Promise<ConfigUpdateResult | null> => {
      setLoading(true);
      setError(null);
      try {
        const resp = await apiFetch('/api/config/named', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name }),
        });
        if (!resp.ok) {
          const body = await resp.json().catch(() => ({ detail: `${resp.status}` }));
          throw new Error(body.detail || `Save failed: ${resp.status}`);
        }
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

  return { saveNamed, loading, error };
}

export function useActivateNamedConfig(apiFetch: ApiFetch) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const activateNamed = useCallback(
    async (name: string): Promise<ConfigUpdateResult | null> => {
      setLoading(true);
      setError(null);
      try {
        const resp = await apiFetch(`/api/config/named/${encodeURIComponent(name)}/activate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({}),
        });
        if (!resp.ok) {
          const body = await resp.json().catch(() => ({ detail: `${resp.status}` }));
          throw new Error(body.detail || `Activate failed: ${resp.status}`);
        }
        return await resp.json();
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Activate failed';
        setError(msg);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [apiFetch],
  );

  return { activateNamed, loading, error };
}

export function useDeleteNamedConfig(apiFetch: ApiFetch) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const deleteNamed = useCallback(
    async (name: string): Promise<boolean> => {
      setLoading(true);
      setError(null);
      try {
        const resp = await apiFetch(`/api/config/named/${encodeURIComponent(name)}`, {
          method: 'DELETE',
        });
        if (!resp.ok) {
          const body = await resp.json().catch(() => ({ detail: `${resp.status}` }));
          throw new Error(body.detail || `Delete failed: ${resp.status}`);
        }
        return true;
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Delete failed';
        setError(msg);
        return false;
      } finally {
        setLoading(false);
      }
    },
    [apiFetch],
  );

  return { deleteNamed, loading, error };
}

// ---------------------------------------------------------------------------
// Widget Appearance hooks (C4 — Named widget appearance lifecycle)
// ---------------------------------------------------------------------------

export function useWidgetAppearances(apiFetch: ApiFetch) {
  return useApi<{ configs: NamedConfigSummary[] }>(apiFetch, '/api/config/widget-appearances');
}

export function useSaveWidgetAppearance(apiFetch: ApiFetch) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const saveAppearance = useCallback(
    async (name: string): Promise<boolean> => {
      setLoading(true);
      setError(null);
      try {
        const res = await apiFetch('/api/config/widget-appearances', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name }),
        });
        if (!res.ok) {
          const body = await res.json().catch(() => ({}));
          setError(body.detail ?? 'Failed to save widget appearance');
          return false;
        }
        return true;
      } catch {
        setError('Network error saving widget appearance');
        return false;
      } finally {
        setLoading(false);
      }
    },
    [apiFetch],
  );

  return { saveAppearance, loading, error };
}

export function useActivateWidgetAppearance(apiFetch: ApiFetch) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const activateAppearance = useCallback(
    async (name: string): Promise<boolean> => {
      setLoading(true);
      setError(null);
      try {
        const res = await apiFetch(`/api/config/widget-appearances/${encodeURIComponent(name)}/activate`, {
          method: 'POST',
        });
        if (!res.ok) {
          const body = await res.json().catch(() => ({}));
          setError(body.detail ?? 'Failed to activate widget appearance');
          return false;
        }
        return true;
      } catch {
        setError('Network error activating widget appearance');
        return false;
      } finally {
        setLoading(false);
      }
    },
    [apiFetch],
  );

  return { activateAppearance, loading, error };
}

export function useDeleteWidgetAppearance(apiFetch: ApiFetch) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const deleteAppearance = useCallback(
    async (name: string): Promise<boolean> => {
      setLoading(true);
      setError(null);
      try {
        const res = await apiFetch(`/api/config/widget-appearances/${encodeURIComponent(name)}`, {
          method: 'DELETE',
        });
        if (!res.ok) {
          const body = await res.json().catch(() => ({}));
          setError(body.detail ?? 'Failed to delete widget appearance');
          return false;
        }
        return true;
      } catch {
        setError('Network error deleting widget appearance');
        return false;
      } finally {
        setLoading(false);
      }
    },
    [apiFetch],
  );

  return { deleteAppearance, loading, error };
}

// ---------------------------------------------------------------------------
// Activation hooks (Save → Activate model)
// ---------------------------------------------------------------------------

/** Lightweight activation status for polling. */
export interface ActivationStatus {
  has_pending_changes: boolean;
  active_version: number;
  active_activated_at: string | null;
  draft_version: number | null;
}

/** Full draft state including diff vs active. */
export interface DraftState {
  has_pending_changes: boolean;
  active_version: number;
  active_activated_at: string | null;
  draft_version: number | null;
  changed_fields: string[];
  draft_config: Record<string, unknown>;
  active_config: Record<string, unknown>;
}

export function useActivationStatus(apiFetch: ApiFetch) {
  return useApi<ActivationStatus>(apiFetch, '/api/config/activation-status');
}

export function useDraftState(apiFetch: ApiFetch) {
  return useApi<DraftState>(apiFetch, '/api/config/draft');
}

export function useActivateDraft(apiFetch: ApiFetch) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const activate = useCallback(
    async (): Promise<boolean> => {
      setLoading(true);
      setError(null);
      try {
        const res = await apiFetch('/api/config/draft/activate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: '{}',
        });
        if (!res.ok) {
          const body = await res.json().catch(() => ({}));
          setError(body.detail?.errors?.[0]?.message ?? body.detail ?? 'Activation failed');
          return false;
        }
        return true;
      } catch {
        setError('Network error during activation');
        return false;
      } finally {
        setLoading(false);
      }
    },
    [apiFetch],
  );

  return { activate, loading, error };
}

export function useDiscardDraft(apiFetch: ApiFetch) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const discard = useCallback(
    async (): Promise<boolean> => {
      setLoading(true);
      setError(null);
      try {
        const res = await apiFetch('/api/config/draft/discard', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: '{}',
        });
        if (!res.ok) {
          const body = await res.json().catch(() => ({}));
          setError(body.detail ?? 'Failed to discard draft');
          return false;
        }
        return true;
      } catch {
        setError('Network error discarding draft');
        return false;
      } finally {
        setLoading(false);
      }
    },
    [apiFetch],
  );

  return { discard, loading, error };
}

export function useRestorePrevious(apiFetch: ApiFetch) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const restore = useCallback(
    async (): Promise<boolean> => {
      setLoading(true);
      setError(null);
      try {
        const res = await apiFetch('/api/config/restore', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: '{}',
        });
        if (!res.ok) {
          const body = await res.json().catch(() => ({}));
          setError(body.detail ?? 'Failed to restore previous configuration');
          return false;
        }
        return true;
      } catch {
        setError('Network error restoring configuration');
        return false;
      } finally {
        setLoading(false);
      }
    },
    [apiFetch],
  );

  return { restore, loading, error };
}

// ---------------------------------------------------------------------------
// Usage hooks
// ---------------------------------------------------------------------------

export function useUsageDashboard(apiFetch: ApiFetch, billingPeriod?: string) {
  const path = billingPeriod
    ? `/api/dashboard/usage?billing_period=${billingPeriod}`
    : '/api/dashboard/usage';
  return useApi<UsageDashboard>(apiFetch, path);
}

export function useDailyVolume(apiFetch: ApiFetch, billingPeriod?: string) {
  const path = billingPeriod
    ? `/api/dashboard/usage/daily?billing_period=${billingPeriod}`
    : '/api/dashboard/usage/daily';
  return useApi<{ days: DailyVolume[] }>(apiFetch, path);
}

export function useConversationList(
  apiFetch: ApiFetch,
  billingPeriod?: string,
  offset = 0,
  limit = 50,
) {
  const params = new URLSearchParams();
  if (billingPeriod) params.set('billing_period', billingPeriod);
  params.set('offset', String(offset));
  params.set('limit', String(limit));
  const path = `/api/dashboard/conversations?${params}`;
  return useApi<PaginatedList<ConversationSummary>>(apiFetch, path);
}

// ---------------------------------------------------------------------------
// Inbox hooks
// ---------------------------------------------------------------------------

export function useInboxConversations(apiFetch: ApiFetch) {
  return useApi<{ conversations: InboxConversation[] }>(apiFetch, '/api/admin/conversations');
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
    async (conversationId: string) => {
      setLoading(true);
      try {
        const resp = await apiFetch(`/api/admin/conversations/${conversationId}/escalate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({}),
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

// ---------------------------------------------------------------------------
// Knowledge Base hooks
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

// ---------------------------------------------------------------------------
// Analytics hooks
// ---------------------------------------------------------------------------

/** Test mode filter for analytics: undefined = all, true = test only, false = production only. */
export type TestModeFilter = boolean | undefined;

export function useAnalyticsSummary(apiFetch: ApiFetch, isTestMode?: TestModeFilter) {
  const params = new URLSearchParams();
  if (isTestMode === true) params.set('is_test_mode', 'true');
  else if (isTestMode === false) params.set('is_test_mode', 'false');
  const qs = params.toString();
  const path = qs ? `/api/analytics/summary?${qs}` : '/api/analytics/summary';
  return useApi<AnalyticsSummary>(apiFetch, path);
}

export function useIntentBreakdown(apiFetch: ApiFetch, isTestMode?: TestModeFilter) {
  const params = new URLSearchParams();
  if (isTestMode === true) params.set('is_test_mode', 'true');
  else if (isTestMode === false) params.set('is_test_mode', 'false');
  const qs = params.toString();
  const path = qs ? `/api/analytics/intents?${qs}` : '/api/analytics/intents';
  return useApi<{ intents: IntentBreakdown[] }>(apiFetch, path);
}

export function useKnowledgeGaps(apiFetch: ApiFetch, isTestMode?: TestModeFilter) {
  const params = new URLSearchParams();
  if (isTestMode === true) params.set('is_test_mode', 'true');
  else if (isTestMode === false) params.set('is_test_mode', 'false');
  const qs = params.toString();
  const path = qs ? `/api/analytics/gaps?${qs}` : '/api/analytics/gaps';
  return useApi<{ gaps: KnowledgeGap[] }>(apiFetch, path);
}

// ---------------------------------------------------------------------------
// Team hooks
// ---------------------------------------------------------------------------

export function useTeamMembers(apiFetch: ApiFetch) {
  return useApi<{ members: TeamMember[] }>(apiFetch, '/api/admin/team');
}

export function useInviteTeamMember(apiFetch: ApiFetch) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const invite = useCallback(
    async (email: string, role: string, name?: string) => {
      setLoading(true);
      setError(null);
      try {
        // Backend expects display_name (required, min_length=1), not name
        const display_name = name?.trim() || email.split('@')[0];
        const resp = await apiFetch('/api/admin/team', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, role, display_name }),
        });
        if (!resp.ok) throw new Error(`${resp.status}`);
        return await resp.json();
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Invite failed';
        setError(msg);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [apiFetch],
  );

  return { invite, loading, error };
}

// ---------------------------------------------------------------------------
// Billing hooks
// ---------------------------------------------------------------------------

export function useBillingStatus(
  apiFetch: ApiFetch,
  channel: 'shopify' | 'stripe',
  shopDomain?: string,
) {
  const path =
    channel === 'shopify'
      ? `/api/shopify/billing/status?shop=${encodeURIComponent(shopDomain || '')}`
      : '/api/billing/status';
  const enabled = channel === 'stripe' || !!shopDomain;
  return useApi<Record<string, unknown>>(apiFetch, path, enabled);
}

export function usePackBalance(apiFetch: ApiFetch, customerId: string) {
  return useApi<{ balance: number; packs: Array<Record<string, unknown>> }>(
    apiFetch,
    `/api/packs/balance/${customerId}`,
    !!customerId,
  );
}

// ---------------------------------------------------------------------------
// Integration hooks (C10)
// ---------------------------------------------------------------------------

export function useIntegrations(apiFetch: ApiFetch) {
  return useApi<IntegrationSummary[]>(apiFetch, '/api/admin/integrations');
}

export function useIntegrationDetail(apiFetch: ApiFetch, type: string) {
  return useApi<IntegrationDetail>(apiFetch, `/api/admin/integrations/${type}`, !!type);
}

export function useActivateIntegration(apiFetch: ApiFetch) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const activate = useCallback(
    async (type: string): Promise<IntegrationResponse | null> => {
      setLoading(true);
      setError(null);
      try {
        const resp = await apiFetch(`/api/admin/integrations/${type}/activate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({}),
        });
        if (!resp.ok) {
          const data = await resp.json().catch(() => ({}));
          throw new Error(data.detail || `${resp.status}`);
        }
        return await resp.json();
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Activation failed';
        setError(msg);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [apiFetch],
  );

  return { activate, loading, error };
}

export function useDeactivateIntegration(apiFetch: ApiFetch) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const deactivate = useCallback(
    async (type: string): Promise<IntegrationResponse | null> => {
      setLoading(true);
      setError(null);
      try {
        const resp = await apiFetch(`/api/admin/integrations/${type}/deactivate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({}),
        });
        if (!resp.ok) {
          const data = await resp.json().catch(() => ({}));
          throw new Error(data.detail || `${resp.status}`);
        }
        return await resp.json();
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Deactivation failed';
        setError(msg);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [apiFetch],
  );

  return { deactivate, loading, error };
}

export function useDisconnectIntegration(apiFetch: ApiFetch) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const disconnect = useCallback(
    async (type: string): Promise<IntegrationResponse | null> => {
      setLoading(true);
      setError(null);
      try {
        const resp = await apiFetch(`/api/admin/integrations/${type}`, {
          method: 'DELETE',
        });
        if (!resp.ok) {
          const data = await resp.json().catch(() => ({}));
          throw new Error(data.detail || `${resp.status}`);
        }
        return await resp.json();
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Disconnect failed';
        setError(msg);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [apiFetch],
  );

  return { disconnect, loading, error };
}

// ---------------------------------------------------------------------------
// Polling hook (for real-time inbox)
// ---------------------------------------------------------------------------

export function usePolling<T>(
  apiFetch: ApiFetch,
  path: string,
  intervalMs = 5000,
): UseApiResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tick, setTick] = useState(0);
  const intervalRef = useRef<ReturnType<typeof setInterval>>();

  const refetch = useCallback(() => setTick((t) => t + 1), []);

  useEffect(() => {
    let cancelled = false;

    const fetchData = () => {
      setLoading(true);
      apiFetch(path)
        .then(async (resp) => {
          if (cancelled) return;
          if (!resp.ok) throw new Error(`${resp.status}`);
          const json = await resp.json();
          setData(json);
          setError(null);
        })
        .catch((err) => {
          if (!cancelled) setError(err.message);
        })
        .finally(() => {
          if (!cancelled) setLoading(false);
        });
    };

    fetchData();
    intervalRef.current = setInterval(fetchData, intervalMs);

    return () => {
      cancelled = true;
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [apiFetch, path, intervalMs, tick]);

  return { data, loading, error, refetch };
}
