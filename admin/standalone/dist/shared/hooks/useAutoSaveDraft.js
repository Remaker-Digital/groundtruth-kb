// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * useAutoSaveDraft — debounced auto-save for AI Configuration pages.
 *
 * Each page provides its own `save` callback that computes and sends changes.
 * The hook debounces events, tracks save count for the indicator, and provides:
 *   - `onBlur`      — attach to form container's onBlur for text-input saves
 *   - `triggerSave`  — call after SegmentedControl / Switch / Slider / etc.
 *                      onChange to ensure non-text controls persist changes
 *
 * The save function is stored in a ref so the debounced timer always calls the
 * latest version, avoiding stale-closure bugs when React state has changed
 * between the trigger and the timer firing.
 */
import { useRef, useCallback, useState } from 'react';
export function useAutoSaveDraft({ save, debounceMs = 500, }) {
    const timerRef = useRef(null);
    const saveRef = useRef(save);
    saveRef.current = save; // Always points to the latest save function
    const [saveCount, setSaveCount] = useState(0);
    const [saving, setSaving] = useState(false);
    const triggerSave = useCallback(() => {
        // Clear any pending debounce timer
        if (timerRef.current)
            clearTimeout(timerRef.current);
        timerRef.current = setTimeout(async () => {
            setSaving(true);
            try {
                const ok = await saveRef.current();
                if (ok)
                    setSaveCount((c) => c + 1);
            }
            finally {
                setSaving(false);
            }
        }, debounceMs);
    }, [debounceMs]);
    return { onBlur: triggerSave, triggerSave, saveCount, saving };
}
//# sourceMappingURL=useAutoSaveDraft.js.map