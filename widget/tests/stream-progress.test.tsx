/**
 * P3-5: Message stream progress indicator — pre-implementation tests.
 *
 * The live streaming contract uses messages[last].streaming (store.ts:28,
 * MessageList.tsx:276), not a top-level isStreaming prop.
 * These tests will FAIL until P3-5 is implemented.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { describe, it, expect } from 'vitest';

describe('P3-5: Stream progress indicator', () => {
  it.skip('progress bar visible when last message is streaming', () => {
    // TODO P3-5: render MessageList with messages where last.streaming=true
    // assert progress bar element exists in DOM
  });

  it.skip('progress bar hidden when last message not streaming', () => {
    // TODO P3-5: render with last.streaming=false
    // assert no progress bar element
  });

  it.skip('progress bar uses primary color', () => {
    // TODO P3-5: render with streaming message
    // assert element style contains colorPrimary value
  });
});
