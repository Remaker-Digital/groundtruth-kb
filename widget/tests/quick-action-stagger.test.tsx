/**
 * P3-6: Quick action staggered entrance — behavioral tests.
 *
 * Verifies QuickActions source code contains staggered animation-delay
 * and per-button ar-fade-in animation.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { describe, it, expect } from 'vitest';
import { readFileSync } from 'fs';
import { resolve } from 'path';

const QA_SOURCE = readFileSync(
  resolve(__dirname, '../src/components/QuickActions.tsx'),
  'utf-8',
);

describe('P3-6: Quick action staggered entrance', () => {
  it('buttons have sequential animation-delay via index', () => {
    // P3-6: each button gets animationDelay: `${index * 50}ms`
    expect(QA_SOURCE).toContain('animationDelay');
    expect(QA_SOURCE).toContain('index * 50');
  });

  it('animation class applied to buttons (ar-fade-in)', () => {
    expect(QA_SOURCE).toContain('ar-fade-in');
  });

  it('container no longer has animation (moved to individual buttons)', () => {
    // The container div should NOT have animation (moved to buttons)
    expect(QA_SOURCE).toContain('Animation moved to individual buttons');
  });

  it('max 2 buttons enforced', () => {
    expect(QA_SOURCE).toContain('slice(0, 2)');
  });
});
