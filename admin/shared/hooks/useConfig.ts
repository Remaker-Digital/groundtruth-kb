/**
 * Configuration hooks — config CRUD, named configs, widget appearances, activation.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { useState, useCallback } from 'react';
import type { ConfigReadResult, ConfigUpdateResult } from '../types/index';
import { useApi } from './useApi';
import type { ApiFetch } from './useApi';

// ---------------------------------------------------------------------------
// Config hooks
// ---------------------------------------------------------------------------

export function useConfig(apiFetch: ApiFetch) {
  return useApi<ConfigReadResult>(apiFetch, '/api/config?state=draft');
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
        if (!resp.ok) {
          let detail = `Save failed (HTTP ${resp.status})`;
          try {
            const body = await resp.json();
            if (typeof body?.detail === 'string') detail = body.detail;
            else if (body?.detail?.errors?.length) {
              detail = body.detail.errors.map((e: Record<string, string>) => e.message || e.field).join('; ');
            }
          } catch { /* response body not JSON */ }
          throw new Error(detail);
        }
        return await resp.json();
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Update failed';
        setError(msg);
        // Return error detail so callers can read it synchronously
        // (React state won't update until next render cycle).
        return { success: false, error: msg } as unknown as ConfigUpdateResult;
      } finally {
        setLoading(false);
      }
    },
    [apiFetch],
  );

  const clearError = useCallback(() => setError(null), []);

  return { updateConfig, loading, error, clearError };
}

// ---------------------------------------------------------------------------
// Widget key rotation
// ---------------------------------------------------------------------------

export function useRotateWidgetKey(apiFetch: ApiFetch) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const rotateWidgetKey = useCallback(
    async (): Promise<{ newWidgetKey: string; message: string } | null> => {
      setLoading(true);
      setError(null);
      try {
        const resp = await apiFetch('/api/keys/rotate-widget-key', { method: 'POST' });
        if (!resp.ok) {
          let detail = `Rotation failed (HTTP ${resp.status})`;
          try {
            const body = await resp.json();
            if (typeof body?.detail === 'string') detail = body.detail;
          } catch { /* not JSON */ }
          throw new Error(detail);
        }
        return await resp.json();
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Widget key rotation failed';
        setError(msg);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [apiFetch],
  );

  return { rotateWidgetKey, loading, error };
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
        // Return error detail so callers can read it synchronously
        // (React state won't update until next render cycle).
        return { success: false, error: msg } as unknown as ConfigUpdateResult;
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
        // Return error detail so callers can read it synchronously
        // (React state won't update until next render cycle).
        return { success: false, error: msg } as unknown as ConfigUpdateResult;
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
  is_configured: boolean;
  is_active: boolean;
  can_activate: boolean;
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
