/**
 * useQueryPreservingNavigate — navigate() wrapper that carries forward URL search params.
 *
 * React Router's navigate('/inbox') replaces the entire URL, dropping ?tenant=<slug>
 * and any other query parameters. This hook reads the current location.search and
 * appends it to path-only targets so that ?tenant= (SPEC-1617) survives sidebar
 * clicks, redirect loops, and every other client-side navigation.
 *
 * If the target path already contains a query string, it is used as-is.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

export function useQueryPreservingNavigate() {
  const navigate = useNavigate();
  const location = useLocation();

  return useCallback(
    (to: string, options?: { replace?: boolean; state?: unknown }) => {
      // If `to` already has a query string, use it as-is
      if (to.includes('?')) {
        navigate(to, options);
        return;
      }
      // Carry forward current search params (e.g. ?tenant=blanco-9939)
      const search = location.search;
      navigate(search ? `${to}${search}` : to, options);
    },
    [navigate, location.search],
  );
}
