// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * Locale barrel — exports locale resolution and the buildLocale function.
 *
 * Architecture:
 *   1. Merchant sets widget_locale in config ('auto' | 'en' | 'es' | ... | 'ko')
 *   2. 'auto' detects visitor browser language via navigator.language
 *   3. Explicit locale codes select a specific pack
 *   4. Merchant overrides (header_text, input_placeholder, offline_message)
 *      always take precedence over the locale pack
 *   5. English is the ultimate fallback
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import type { Locale } from './en';
import { en } from './en';
import { es } from './es';
import { fr } from './fr';
import { de } from './de';
import { pt } from './pt';
import { ja } from './ja';
import { zh } from './zh';
import { ko } from './ko';

export type { Locale };
export type LocaleCode = 'en' | 'es' | 'fr' | 'de' | 'pt' | 'ja' | 'zh' | 'ko';

/** Map of supported locale codes to their packs. */
export const LOCALE_MAP: Record<LocaleCode, Locale> = {
  en, es, fr, de, pt, ja, zh, ko,
};

/** All supported locale codes. */
export const SUPPORTED_LOCALES: LocaleCode[] = ['en', 'es', 'fr', 'de', 'pt', 'ja', 'zh', 'ko'];

/**
 * Detect the visitor's preferred language from the browser.
 * Returns a supported LocaleCode or null if no match.
 */
export function detectBrowserLocale(): LocaleCode | null {
  if (typeof navigator === 'undefined') return null;
  // navigator.languages gives ordered preference list; fall back to navigator.language
  const candidates = navigator.languages?.length
    ? Array.from(navigator.languages)
    : [navigator.language];
  for (const tag of candidates) {
    if (!tag) continue;
    const base = tag.split('-')[0].toLowerCase() as LocaleCode;
    if (base in LOCALE_MAP) return base;
  }
  return null;
}

/**
 * Resolve the locale code from a widget_locale config value.
 * 'auto' → browser detection with 'en' fallback.
 * Explicit code → that locale if supported, else 'en'.
 * null/undefined → 'en'.
 */
export function resolveLocaleCode(
  widgetLocale: string | null | undefined,
): LocaleCode {
  if (!widgetLocale || widgetLocale === 'auto') {
    return detectBrowserLocale() || 'en';
  }
  const code = widgetLocale.toLowerCase() as LocaleCode;
  return code in LOCALE_MAP ? code : 'en';
}

/**
 * Get the Locale pack for a given code.
 */
export function getLocalePack(code: LocaleCode): Locale {
  return LOCALE_MAP[code] ?? en;
}
