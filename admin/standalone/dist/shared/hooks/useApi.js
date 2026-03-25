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
// Generic fetch hook
// ---------------------------------------------------------------------------
export function useApi(apiFetch, path, enabled = true) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [tick, setTick] = useState(0);
    const refetch = useCallback(() => setTick((t) => t + 1), []);
    useEffect(() => {
        if (!enabled)
            return;
        let cancelled = false;
        setLoading(true);
        setError(null);
        apiFetch(path)
            .then(async (resp) => {
            if (cancelled)
                return;
            if (!resp.ok) {
                const body = await resp.text().catch(() => '');
                throw new Error(`${resp.status}: ${body}`);
            }
            const json = await resp.json();
            setData(json);
        })
            .catch((err) => {
            if (!cancelled)
                setError(err.message || 'Request failed');
        })
            .finally(() => {
            if (!cancelled)
                setLoading(false);
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
export function usePolling(apiFetch, path, intervalMs = 5000) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [tick, setTick] = useState(0);
    const intervalRef = useRef();
    const refetch = useCallback(() => setTick((t) => t + 1), []);
    useEffect(() => {
        let cancelled = false;
        const fetchData = () => {
            setLoading(true);
            apiFetch(path)
                .then(async (resp) => {
                if (cancelled)
                    return;
                if (!resp.ok)
                    throw new Error(`${resp.status}`);
                const json = await resp.json();
                setData(json);
                setError(null);
            })
                .catch((err) => {
                if (!cancelled)
                    setError(err.message);
            })
                .finally(() => {
                if (!cancelled)
                    setLoading(false);
            });
        };
        fetchData();
        intervalRef.current = setInterval(fetchData, intervalMs);
        return () => {
            cancelled = true;
            if (intervalRef.current)
                clearInterval(intervalRef.current);
        };
    }, [apiFetch, path, intervalMs, tick]);
    return { data, loading, error, refetch };
}
//# sourceMappingURL=useApi.js.map