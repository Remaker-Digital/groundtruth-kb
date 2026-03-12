// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

/**
 * useAutoSaveDraft — debounced auto-save on focusout for AI Configuration pages.
 *
 * Each page provides its own `save` callback that computes and sends changes.
 * The hook debounces blur events, tracks save count for the indicator, and
 * provides an `onBlur` handler to attach to the form container.
 */

import { useRef, useCallback, useState } from 'react';

interface UseAutoSaveDraftOptions {
  /** Async function that saves current form state. Return true on success. */
  save: () => Promise<boolean>;
  /** Debounce delay in ms after the last blur event. Default 500. */
  debounceMs?: number;
}

interface UseAutoSaveDraftResult {
  /** Attach to the form container's onBlur. */
  onBlur: () => void;
  /** Incremented on each successful save — pass to AutoSaveIndicator. */
  saveCount: number;
  /** Whether a save is currently in progress. */
  saving: boolean;
}

export function useAutoSaveDraft({
  save,
  debounceMs = 500,
}: UseAutoSaveDraftOptions): UseAutoSaveDraftResult {
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const [saveCount, setSaveCount] = useState(0);
  const [saving, setSaving] = useState(false);

  const onBlur = useCallback(() => {
    // Clear any pending debounce timer
    if (timerRef.current) clearTimeout(timerRef.current);

    timerRef.current = setTimeout(async () => {
      setSaving(true);
      try {
        const ok = await save();
        if (ok) setSaveCount((c) => c + 1);
      } finally {
        setSaving(false);
      }
    }, debounceMs);
  }, [save, debounceMs]);

  return { onBlur, saveCount, saving };
}
