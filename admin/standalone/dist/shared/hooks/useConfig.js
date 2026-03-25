/**
 * Configuration hooks — config CRUD, named configs, widget appearances, activation.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { useState, useCallback } from 'react';
import { useApi } from './useApi';
// ---------------------------------------------------------------------------
// Config hooks
// ---------------------------------------------------------------------------
export function useConfig(apiFetch) {
    return useApi(apiFetch, '/api/config?state=draft');
}
export function useConfigSchema(apiFetch, step) {
    const path = step ? `/api/config/schema/${step}` : '/api/config/schema';
    return useApi(apiFetch, path);
}
export function useConfigVersions(apiFetch) {
    return useApi(apiFetch, '/api/config/versions');
}
export function useUpdateConfig(apiFetch) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const updateConfig = useCallback(async (changes) => {
        setLoading(true);
        setError(null);
        try {
            const resp = await apiFetch('/api/config', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ fields: changes }),
            });
            if (!resp.ok) {
                let detail = `Save failed (HTTP ${resp.status})`;
                try {
                    const body = await resp.json();
                    if (typeof body?.detail === 'string')
                        detail = body.detail;
                    else if (body?.detail?.errors?.length) {
                        detail = body.detail.errors.map((e) => e.message || e.field).join('; ');
                    }
                }
                catch { /* response body not JSON */ }
                throw new Error(detail);
            }
            return await resp.json();
        }
        catch (err) {
            const msg = err instanceof Error ? err.message : 'Update failed';
            setError(msg);
            // Return error detail so callers can read it synchronously
            // (React state won't update until next render cycle).
            return { success: false, error: msg };
        }
        finally {
            setLoading(false);
        }
    }, [apiFetch]);
    const clearError = useCallback(() => setError(null), []);
    return { updateConfig, loading, error, clearError };
}
// ---------------------------------------------------------------------------
// Widget key rotation
// ---------------------------------------------------------------------------
export function useRotateWidgetKey(apiFetch) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const rotateWidgetKey = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const resp = await apiFetch('/api/keys/rotate-widget-key', { method: 'POST' });
            if (!resp.ok) {
                let detail = `Rotation failed (HTTP ${resp.status})`;
                try {
                    const body = await resp.json();
                    if (typeof body?.detail === 'string')
                        detail = body.detail;
                }
                catch { /* not JSON */ }
                throw new Error(detail);
            }
            return await resp.json();
        }
        catch (err) {
            const msg = err instanceof Error ? err.message : 'Widget key rotation failed';
            setError(msg);
            return null;
        }
        finally {
            setLoading(false);
        }
    }, [apiFetch]);
    return { rotateWidgetKey, loading, error };
}
export function useNamedConfigs(apiFetch) {
    return useApi(apiFetch, '/api/config/named');
}
export function useSaveNamedConfig(apiFetch) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const saveNamed = useCallback(async (name) => {
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
        }
        catch (err) {
            const msg = err instanceof Error ? err.message : 'Save failed';
            setError(msg);
            // Return error detail so callers can read it synchronously
            // (React state won't update until next render cycle).
            return { success: false, error: msg };
        }
        finally {
            setLoading(false);
        }
    }, [apiFetch]);
    return { saveNamed, loading, error };
}
export function useActivateNamedConfig(apiFetch) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const activateNamed = useCallback(async (name) => {
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
        }
        catch (err) {
            const msg = err instanceof Error ? err.message : 'Activate failed';
            setError(msg);
            // Return error detail so callers can read it synchronously
            // (React state won't update until next render cycle).
            return { success: false, error: msg };
        }
        finally {
            setLoading(false);
        }
    }, [apiFetch]);
    return { activateNamed, loading, error };
}
export function useDeleteNamedConfig(apiFetch) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const deleteNamed = useCallback(async (name) => {
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
        }
        catch (err) {
            const msg = err instanceof Error ? err.message : 'Delete failed';
            setError(msg);
            return false;
        }
        finally {
            setLoading(false);
        }
    }, [apiFetch]);
    return { deleteNamed, loading, error };
}
// ---------------------------------------------------------------------------
// Widget Appearance hooks (C4 — Named widget appearance lifecycle)
// ---------------------------------------------------------------------------
export function useWidgetAppearances(apiFetch) {
    return useApi(apiFetch, '/api/config/widget-appearances');
}
export function useSaveWidgetAppearance(apiFetch) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const saveAppearance = useCallback(async (name) => {
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
        }
        catch {
            setError('Network error saving widget appearance');
            return false;
        }
        finally {
            setLoading(false);
        }
    }, [apiFetch]);
    return { saveAppearance, loading, error };
}
export function useActivateWidgetAppearance(apiFetch) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const activateAppearance = useCallback(async (name) => {
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
        }
        catch {
            setError('Network error activating widget appearance');
            return false;
        }
        finally {
            setLoading(false);
        }
    }, [apiFetch]);
    return { activateAppearance, loading, error };
}
export function useDeleteWidgetAppearance(apiFetch) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const deleteAppearance = useCallback(async (name) => {
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
        }
        catch {
            setError('Network error deleting widget appearance');
            return false;
        }
        finally {
            setLoading(false);
        }
    }, [apiFetch]);
    return { deleteAppearance, loading, error };
}
export function useActivationStatus(apiFetch) {
    return useApi(apiFetch, '/api/config/activation-status');
}
export function useDraftState(apiFetch) {
    return useApi(apiFetch, '/api/config/draft');
}
export function useActivateDraft(apiFetch) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const activate = useCallback(async () => {
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
        }
        catch {
            setError('Network error during activation');
            return false;
        }
        finally {
            setLoading(false);
        }
    }, [apiFetch]);
    return { activate, loading, error };
}
export function useDiscardDraft(apiFetch) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const discard = useCallback(async () => {
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
        }
        catch {
            setError('Network error discarding draft');
            return false;
        }
        finally {
            setLoading(false);
        }
    }, [apiFetch]);
    return { discard, loading, error };
}
export function useRestorePrevious(apiFetch) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const restore = useCallback(async () => {
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
        }
        catch {
            setError('Network error restoring configuration');
            return false;
        }
        finally {
            setLoading(false);
        }
    }, [apiFetch]);
    return { restore, loading, error };
}
//# sourceMappingURL=useConfig.js.map