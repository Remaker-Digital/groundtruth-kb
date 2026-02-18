/**
 * TeamManager utility functions — date formatting and dark-mode detection.
 *
 * Extracted from TeamManager.tsx. Pure functions (formatDate, formatRelativeDate)
 * and the useIsDark hook for Mantine color-scheme detection.
 *
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { useState, useEffect } from 'react';

// ---------------------------------------------------------------------------
// Date formatting
// ---------------------------------------------------------------------------

export function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr) return '--';
  try {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  } catch {
    return dateStr;
  }
}

export function formatRelativeDate(dateStr: string | null | undefined): string {
  if (!dateStr) return 'Never';
  try {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return formatDate(dateStr);
  } catch {
    return dateStr || 'Never';
  }
}

// ---------------------------------------------------------------------------
// Dark mode detection hook — reads Mantine's data-mantine-color-scheme attribute
// ---------------------------------------------------------------------------

export function useIsDark(): boolean {
  const [isDark, setIsDark] = useState(() => {
    if (typeof document === 'undefined') return false;
    return document.documentElement.getAttribute('data-mantine-color-scheme') === 'dark';
  });

  useEffect(() => {
    const observer = new MutationObserver(() => {
      setIsDark(document.documentElement.getAttribute('data-mantine-color-scheme') === 'dark');
    });
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['data-mantine-color-scheme'] });
    return () => observer.disconnect();
  }, []);

  return isDark;
}
