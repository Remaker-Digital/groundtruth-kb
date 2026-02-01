/**
 * useSaveBar — Shopify App Bridge contextual save bar hook.
 *
 * Integrates with Shopify's App Bridge Save Bar API to show the native
 * save bar when the merchant has unsaved changes. This provides the
 * standard Shopify embedded app save UX (save/discard buttons in the
 * top bar).
 *
 * Required by Shopify for embedded apps since 2025.
 *
 * Usage:
 *   const { markDirty, markClean, saving } = useSaveBar({
 *     onSave: async () => { await saveConfig(); },
 *     onDiscard: () => { resetForm(); },
 *   });
 *
 *   // When form values change:
 *   markDirty();
 *
 *   // After successful save:
 *   markClean();
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { useCallback, useEffect, useRef, useState } from 'react';

interface UseSaveBarOptions {
  /** Called when the merchant clicks "Save" in the save bar. */
  onSave: () => Promise<void>;
  /** Called when the merchant clicks "Discard" in the save bar. */
  onDiscard: () => void;
}

interface UseSaveBarReturn {
  /** Mark that there are unsaved changes — shows the save bar. */
  markDirty: () => void;
  /** Mark that changes are saved — hides the save bar. */
  markClean: () => void;
  /** Whether a save operation is in progress. */
  saving: boolean;
  /** Whether there are unsaved changes. */
  isDirty: boolean;
}

/** Access the global Shopify App Bridge object. */
function getShopify(): {
  saveBar?: {
    show: () => void;
    hide: () => void;
    leaveConfirmation?: {
      enable: () => void;
      disable: () => void;
    };
  };
} | null {
  const win = window as unknown as { shopify?: unknown };
  return win.shopify as ReturnType<typeof getShopify>;
}

export function useSaveBar({ onSave, onDiscard }: UseSaveBarOptions): UseSaveBarReturn {
  const [isDirty, setIsDirty] = useState(false);
  const [saving, setSaving] = useState(false);
  const onSaveRef = useRef(onSave);
  const onDiscardRef = useRef(onDiscard);

  // Keep refs up to date without re-subscribing to App Bridge events
  onSaveRef.current = onSave;
  onDiscardRef.current = onDiscard;

  // ---- Save Bar event listeners ------------------------------------------

  useEffect(() => {
    const shopify = getShopify();
    if (!shopify?.saveBar) return;

    // Listen for save bar save/discard actions
    // App Bridge 4.x fires custom events on the document
    const handleSave = async () => {
      setSaving(true);
      try {
        await onSaveRef.current();
        setIsDirty(false);
        shopify.saveBar?.hide();
        shopify.saveBar?.leaveConfirmation?.disable();
      } catch {
        // Save failed — keep save bar visible
      } finally {
        setSaving(false);
      }
    };

    const handleDiscard = () => {
      onDiscardRef.current();
      setIsDirty(false);
      shopify.saveBar?.hide();
      shopify.saveBar?.leaveConfirmation?.disable();
    };

    // App Bridge 4.x: listen for contextual save bar actions
    document.addEventListener('shopify:save-bar:save', handleSave);
    document.addEventListener('shopify:save-bar:discard', handleDiscard);

    return () => {
      document.removeEventListener('shopify:save-bar:save', handleSave);
      document.removeEventListener('shopify:save-bar:discard', handleDiscard);
    };
  }, []);

  // ---- Show/hide save bar based on dirty state ---------------------------

  useEffect(() => {
    const shopify = getShopify();
    if (!shopify?.saveBar) return;

    if (isDirty) {
      shopify.saveBar.show();
      shopify.saveBar.leaveConfirmation?.enable();
    } else {
      shopify.saveBar.hide();
      shopify.saveBar.leaveConfirmation?.disable();
    }
  }, [isDirty]);

  // ---- Public API --------------------------------------------------------

  const markDirty = useCallback(() => setIsDirty(true), []);
  const markClean = useCallback(() => setIsDirty(false), []);

  return { markDirty, markClean, saving, isDirty };
}
