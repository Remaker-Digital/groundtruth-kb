// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * Vitest setup for the provider admin console (WI-3221).
 *
 * Registers jest-dom matchers, cleans up the DOM between tests, and installs the
 * browser-API shims Mantine needs under happy-dom (matchMedia, ResizeObserver,
 * scrollIntoView).
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import '@testing-library/jest-dom/vitest';
import { afterEach, vi } from 'vitest';
import { cleanup } from '@testing-library/react';

afterEach(() => {
  cleanup();
});

// Mantine reads window.matchMedia for color-scheme / responsive logic.
if (typeof window !== 'undefined' && !window.matchMedia) {
  window.matchMedia = vi.fn().mockImplementation((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  }));
}

// Mantine's overlay/scroll components reference ResizeObserver + scrollIntoView.
class ResizeObserverStub {
  observe(): void {}
  unobserve(): void {}
  disconnect(): void {}
}
if (!globalThis.ResizeObserver) {
  globalThis.ResizeObserver = ResizeObserverStub as unknown as typeof ResizeObserver;
}

if (typeof window !== 'undefined' && !window.HTMLElement.prototype.scrollIntoView) {
  window.HTMLElement.prototype.scrollIntoView = vi.fn();
}
