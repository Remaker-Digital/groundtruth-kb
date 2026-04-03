/**
 * P3-7: New locale keys for Phase 3 features.
 *
 * Import-based checks — verifies locale keys exist in all 8 locale packs.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { describe, it, expect } from 'vitest';
import { en } from '../src/locale/en';
import { de } from '../src/locale/de';
import { es } from '../src/locale/es';
import { fr } from '../src/locale/fr';
import { ja } from '../src/locale/ja';
import { ko } from '../src/locale/ko';
import { pt } from '../src/locale/pt';
import { zh } from '../src/locale/zh';

const P3_KEYS = [
  'reconnectingAttempt',
  'connectionFailedPermanent',
  'retryConnection',
  'dismissError',
  'restoringConversation',
] as const;

const LOCALES = { en, de, es, fr, ja, ko, pt, zh };

describe('P3-7: New locale keys', () => {
  it('en.ts exports all P3 keys', () => {
    for (const key of P3_KEYS) {
      expect(en[key]).toBeDefined();
      expect(typeof en[key]).toBe('string');
      expect(en[key].length).toBeGreaterThan(0);
    }
  });

  it('all 8 locale files have all P3 keys', () => {
    for (const [name, locale] of Object.entries(LOCALES)) {
      for (const key of P3_KEYS) {
        const value = locale[key as keyof typeof locale];
        expect(value, `${name}.${key} missing or empty`).toBeDefined();
        expect(typeof value, `${name}.${key} not a string`).toBe('string');
        expect((value as string).length, `${name}.${key} is empty`).toBeGreaterThan(0);
      }
    }
  });
});
