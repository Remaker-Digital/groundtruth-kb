/**
 * Transcript persistence — stores conversation_id with TTL for
 * transcript continuity across page loads (SPEC-1868).
 *
 * Storage modes:
 *   - 'session': sessionStorage (survives reload, lost on tab close)
 *   - 'persistent': localStorage with TTL-based expiry
 *   - 'none': no persistence (default)
 *
 * All storage access is wrapped in try/catch to gracefully degrade
 * when storage is unavailable (private browsing, SecurityError).
 *
 * Key namespace: __agentred_{widgetKeyPrefix}_conv to prevent
 * collisions across tenants on the same origin.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

interface StoredTranscript {
  conversationId: string;
  savedAt: number; // epoch milliseconds
}

function makeKey(widgetKey: string): string {
  // Use first 12 chars of widget key as namespace prefix
  const prefix = widgetKey.replace(/^pk_live_/, '').slice(0, 12);
  return `__agentred_${prefix}_conv`;
}

function getStorage(mode: 'session' | 'persistent'): Storage | null {
  try {
    const storage = mode === 'session' ? sessionStorage : localStorage;
    // Probe access — some browsers throw on property access alone
    const probe = '__agentred_probe';
    storage.setItem(probe, '1');
    storage.removeItem(probe);
    return storage;
  } catch {
    return null;
  }
}

/**
 * Save a conversation_id for later restoration.
 */
export function saveTranscript(
  widgetKey: string,
  conversationId: string,
  mode: 'none' | 'session' | 'persistent',
): void {
  if (mode === 'none') return;
  const storage = getStorage(mode);
  if (!storage) return;
  try {
    const data: StoredTranscript = {
      conversationId,
      savedAt: Date.now(),
    };
    storage.setItem(makeKey(widgetKey), JSON.stringify(data));
  } catch { /* quota or security — silently degrade */ }
}

/**
 * Load a stored conversation_id if it exists and hasn't expired.
 * Returns null if not found, expired, or storage unavailable.
 */
export function loadTranscript(
  widgetKey: string,
  mode: 'none' | 'session' | 'persistent',
  ttlHours: number,
): string | null {
  if (mode === 'none') return null;
  const storage = getStorage(mode);
  if (!storage) return null;
  try {
    const raw = storage.getItem(makeKey(widgetKey));
    if (!raw) return null;
    const data: StoredTranscript = JSON.parse(raw);
    // TTL check (persistent mode only — session mode relies on browser lifecycle)
    if (mode === 'persistent') {
      const ttlMs = ttlHours * 60 * 60 * 1000;
      if (Date.now() - data.savedAt > ttlMs) {
        storage.removeItem(makeKey(widgetKey));
        return null;
      }
    }
    return data.conversationId || null;
  } catch {
    return null;
  }
}

/**
 * Clear stored transcript (user-initiated or conversation end).
 */
export function clearTranscript(
  widgetKey: string,
  mode: 'none' | 'session' | 'persistent',
): void {
  if (mode === 'none') return;
  // Clear from both storages to handle mode changes
  for (const storageType of ['session', 'persistent'] as const) {
    const storage = getStorage(storageType);
    if (storage) {
      try {
        storage.removeItem(makeKey(widgetKey));
      } catch { /* ignore */ }
    }
  }
}
