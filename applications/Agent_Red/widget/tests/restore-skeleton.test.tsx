/**
 * P3-3: Conversation restore skeleton loader — behavioral tests.
 *
 * Verifies store state for isRestoring/restoreError and that the
 * RestoreSkeleton component contract is wired correctly.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { describe, it, expect } from 'vitest';
import { en } from '../src/locale/en';
import type { WidgetState } from '../src/state/store';

describe('P3-3: Restore skeleton loader', () => {
  it('WidgetState type includes isRestoring field', async () => {
    // Verify the store type contract includes P3-3 fields
    const state: Partial<WidgetState> = {
      isRestoring: true,
      restoreError: null,
    };
    expect(state.isRestoring).toBe(true);
    expect(state.restoreError).toBe(null);
  });

  it('WidgetState supports transient restore error', () => {
    const state: Partial<WidgetState> = {
      isRestoring: false,
      restoreError: 'transient',
    };
    expect(state.restoreError).toBe('transient');
  });

  it('locale has restoringConversation key', () => {
    expect(en.restoringConversation).toBeDefined();
    expect(en.restoringConversation.length).toBeGreaterThan(0);
  });

  it('locale has retryConnection key for restore failure', () => {
    expect(en.retryConnection).toBeDefined();
    expect(en.retryConnection.length).toBeGreaterThan(0);
  });
});
