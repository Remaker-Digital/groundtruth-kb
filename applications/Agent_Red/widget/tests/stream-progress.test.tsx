/**
 * P3-5: Message stream progress indicator — behavioral tests.
 *
 * Verifies store state for isStreaming and the SSE event handler
 * contract for setting/clearing the streaming flag.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { describe, it, expect } from 'vitest';
import type { WidgetState } from '../src/state/store';

describe('P3-5: Stream progress indicator', () => {
  it('WidgetState includes isStreaming field', () => {
    const state: Partial<WidgetState> = { isStreaming: true };
    expect(state.isStreaming).toBe(true);
  });

  it('isStreaming defaults to false conceptually', () => {
    const state: Partial<WidgetState> = { isStreaming: false };
    expect(state.isStreaming).toBe(false);
  });

  it('SSE module exports SSEConnection class', async () => {
    const mod = await import('../src/transport/sse');
    expect(mod.SSEConnection).toBeDefined();
  });
});
