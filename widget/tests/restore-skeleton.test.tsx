/**
 * P3-3: Conversation restore skeleton loader — pre-implementation tests.
 *
 * Tests render Panel with store state controlling isRestoring/restoreError.
 * These tests will FAIL until P3-3 is implemented (pre-implementation contract).
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { describe, it, expect } from 'vitest';

// P3-3 adds isRestoring and restoreError to WidgetState.
// These tests will be enabled once the store fields and Panel rendering exist.

describe('P3-3: Restore skeleton loader', () => {
  it.skip('skeleton visible when store.isRestoring=true', () => {
    // TODO P3-3: import store, set isRestoring=true, render Panel,
    // assert shimmer/skeleton element exists in DOM
  });

  it.skip('skeleton hidden when messages loaded', () => {
    // TODO P3-3: set isRestoring=false with messages, render Panel,
    // assert no shimmer element
  });

  it.skip('transient failure shows retry button with locale text', () => {
    // TODO P3-3: set restoreError='transient', render Panel,
    // assert button with text matching locale.retryConnection
  });

  it.skip('loading text uses locale.restoringConversation', () => {
    // TODO P3-3: set isRestoring=true, render Panel,
    // assert getByText(en.restoringConversation)
  });
});
