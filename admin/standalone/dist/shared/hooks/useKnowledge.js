/**
 * Knowledge Base hooks — CRUD, upload, import, export, staleness, conflict scan.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { useState, useCallback } from 'react';
import { useApi } from './useApi';
// ---------------------------------------------------------------------------
// Knowledge Base CRUD hooks
// ---------------------------------------------------------------------------
export function useKnowledgeBase(apiFetch) {
    return useApi(apiFetch, '/api/admin/knowledge');
}
export function useKBArticle(apiFetch, articleId) {
    return useApi(apiFetch, `/api/admin/knowledge/${articleId}`, !!articleId);
}
export function useSaveKBArticle(apiFetch) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const save = useCallback(async (article) => {
        setLoading(true);
        setError(null);
        try {
            const isNew = !article.id;
            const resp = await apiFetch(isNew ? '/api/admin/knowledge' : `/api/admin/knowledge/${article.id}`, {
                method: isNew ? 'POST' : 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(article),
            });
            if (!resp.ok)
                throw new Error(`${resp.status}`);
            return await resp.json();
        }
        catch (err) {
            const msg = err instanceof Error ? err.message : 'Save failed';
            setError(msg);
            return null;
        }
        finally {
            setLoading(false);
        }
    }, [apiFetch]);
    return { save, loading, error };
}
export function useUploadFile(apiFetch) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [progress, setProgress] = useState('idle');
    const upload = useCallback(async (file, entryType) => {
        setLoading(true);
        setError(null);
        setProgress('uploading');
        try {
            const formData = new FormData();
            formData.append('file', file);
            if (entryType)
                formData.append('entry_type', entryType);
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
        }
        catch (err) {
            const msg = err instanceof Error ? err.message : 'Upload failed';
            setError(msg);
            return null;
        }
        finally {
            setLoading(false);
        }
    }, [apiFetch]);
    const reset = useCallback(() => {
        setProgress('idle');
        setError(null);
    }, []);
    return { upload, loading, error, progress, reset };
}
export function useImportUrl(apiFetch) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const importUrl = useCallback(async (url, entryType, crawl, maxPages) => {
        setLoading(true);
        setError(null);
        try {
            const payload = { url, entry_type: entryType };
            if (crawl) {
                payload.crawl = true;
                if (maxPages != null)
                    payload.max_pages = maxPages;
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
        }
        catch (err) {
            const msg = err instanceof Error ? err.message : 'Import failed';
            setError(msg);
            return null;
        }
        finally {
            setLoading(false);
        }
    }, [apiFetch]);
    return { importUrl, loading, error };
}
export function useExportCSV(apiFetch) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const exportCSV = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const resp = await apiFetch('/api/admin/knowledge/export');
            if (!resp.ok)
                throw new Error(`Export failed: ${resp.status}`);
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
        }
        catch (err) {
            const msg = err instanceof Error ? err.message : 'Export failed';
            setError(msg);
            return false;
        }
        finally {
            setLoading(false);
        }
    }, [apiFetch]);
    return { exportCSV, loading, error };
}
export function useStalenessSummary(apiFetch) {
    return useApi(apiFetch, '/api/admin/knowledge/staleness');
}
export function useStaleEntries(apiFetch, threshold = 0.6) {
    return useApi(apiFetch, `/api/admin/knowledge/stale?threshold=${threshold}`);
}
export function useVerifyEntry(apiFetch) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const verify = useCallback(async (entryId) => {
        setLoading(true);
        setError(null);
        try {
            const resp = await apiFetch(`/api/admin/knowledge/${entryId}/verify`, {
                method: 'POST',
            });
            if (!resp.ok)
                throw new Error(`${resp.status}`);
            return await resp.json();
        }
        catch (err) {
            const msg = err instanceof Error ? err.message : 'Verify failed';
            setError(msg);
            return null;
        }
        finally {
            setLoading(false);
        }
    }, [apiFetch]);
    return { verify, loading, error };
}
export function useConflictScan(apiFetch) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [result, setResult] = useState(null);
    const scan = useCallback(async (force = false) => {
        setLoading(true);
        setError(null);
        try {
            const resp = await apiFetch(`/api/admin/knowledge/scan?force=${force}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({}),
            });
            if (!resp.ok)
                throw new Error(`${resp.status}`);
            const data = await resp.json();
            setResult(data);
            return data;
        }
        catch (err) {
            const msg = err instanceof Error ? err.message : 'Scan failed';
            setError(msg);
            return null;
        }
        finally {
            setLoading(false);
        }
    }, [apiFetch]);
    return { scan, result, loading, error };
}
//# sourceMappingURL=useKnowledge.js.map