/**
 * Generic API fetch hook — foundation for all domain hooks.
 *
 * Provides the base `useApi<T>` hook and the `ApiFetch` type signature.
 * Shells inject the `apiFetch` function (which handles auth headers)
 * so hooks are auth-agnostic.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { useState, useEffect, useCallback, useRef } from 'react';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type ApiFetch = (path: string, init?: RequestInit) => Promise<Response>;

export interface UseApiResult<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

// ---------------------------------------------------------------------------
// Generic fetch hook
// ---------------------------------------------------------------------------

export function useApi<T>(apiFetch: ApiFetch, path: string, enabled = true): UseApiResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tick, setTick] = useState(0);

  const refetch = useCallback(() => setTick((t) => t + 1), []);

  // Clear stale data when path changes (prevents cross-entity data leak)
  const prevPathRef = useRef(path);
  useEffect(() => {
    if (prevPathRef.current !== path) {
      setData(null);
      setError(null);
      prevPathRef.current = path;
    }
  }, [path]);

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
        if (!cancelled) {
          setData(null);  // Clear stale data on error (e.g., 404)
          setError(err.message || 'Request failed');
        }
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
