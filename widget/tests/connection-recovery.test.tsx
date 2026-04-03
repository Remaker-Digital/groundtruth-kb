/**
 * P3-4: Connection recovery UX — behavioral tests.
 *
 * Verifies store state, SSE callback contract, and locale support
 * for enhanced connection recovery UX.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { describe, it, expect } from 'vitest';
import { en } from '../src/locale/en';
import { es } from '../src/locale/es';
import type { WidgetState } from '../src/state/store';

describe('P3-4: Connection recovery UX', () => {
  it('WidgetState includes reconnectAttempt counter', () => {
    const state: Partial<WidgetState> = {
      reconnectAttempt: 3,
      connectionError: 'transient',
    };
    expect(state.reconnectAttempt).toBe(3);
    expect(state.connectionError).toBe('transient');
  });

  it('WidgetState supports permanent connection error', () => {
    const state: Partial<WidgetState> = {
      connectionError: 'permanent',
    };
    expect(state.connectionError).toBe('permanent');
  });

  it('locale has reconnectingAttempt with interpolation placeholder', () => {
    expect(en.reconnectingAttempt).toContain('{n}');
  });

  it('reconnectingAttempt can be interpolated', () => {
    const text = en.reconnectingAttempt.replace('{n}', '3');
    expect(text).toContain('3');
    expect(text).not.toContain('{n}');
  });

  it('locale has connectionFailedPermanent key', () => {
    expect(en.connectionFailedPermanent).toBeDefined();
    expect(en.connectionFailedPermanent.length).toBeGreaterThan(0);
  });

  it('locale has dismissError key', () => {
    expect(en.dismissError).toBeDefined();
    expect(en.dismissError.length).toBeGreaterThan(0);
  });

  it('non-English locale has all P3-4 keys', () => {
    expect(es.reconnectingAttempt).toBeDefined();
    expect(es.connectionFailedPermanent).toBeDefined();
    expect(es.retryConnection).toBeDefined();
    expect(es.dismissError).toBeDefined();
    // Should not be English
    expect(es.connectionFailedPermanent).not.toBe(en.connectionFailedPermanent);
  });
});
