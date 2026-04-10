/**
 * SPEC-1879 Phase 3 regression tests — phone OTP resend behavior.
 *
 * Covers two P2 findings from Codex advisory review:
 *   1. Resend cooldown must be gated on onResend() success (not unconditional).
 *   2. phoneSendFailed locale key must be present in all 8 locale packs.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { h } from 'preact';
import { render, screen, waitFor } from '@testing-library/preact';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';

import { PhoneOtpVerification } from '../src/components/PhoneOtpVerification';
import { resolveTokens } from '../src/theme/tokens';
import { en } from '../src/locale/en';
import { de } from '../src/locale/de';
import { es } from '../src/locale/es';
import { fr } from '../src/locale/fr';
import { ja } from '../src/locale/ja';
import { ko } from '../src/locale/ko';
import { pt } from '../src/locale/pt';
import { zh } from '../src/locale/zh';

// ---------------------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------------------

const tokens = resolveTokens({});
const locale = en;

function makeProps(overrides: Partial<Parameters<typeof PhoneOtpVerification>[0]> = {}) {
  return {
    tokens,
    locale,
    phone: '+12125550100',
    onVerify: vi.fn(),
    onResend: vi.fn<[], Promise<boolean>>().mockResolvedValue(true),
    isLoading: false,
    ...overrides,
  };
}

// ---------------------------------------------------------------------------
// Locale key coverage (phoneSendFailed across all 8 packs)
// ---------------------------------------------------------------------------

describe('SPEC-1879 P3: phoneSendFailed locale key', () => {
  const LOCALES = { en, de, es, fr, ja, ko, pt, zh };

  it('all 8 locale files export a non-empty phoneSendFailed string', () => {
    for (const [name, loc] of Object.entries(LOCALES)) {
      expect(loc.phoneSendFailed, `${name}.phoneSendFailed missing`).toBeDefined();
      expect(typeof loc.phoneSendFailed, `${name}.phoneSendFailed not a string`).toBe('string');
      expect(
        (loc.phoneSendFailed as string).length,
        `${name}.phoneSendFailed is empty`,
      ).toBeGreaterThan(0);
    }
  });
});

// ---------------------------------------------------------------------------
// Resend cooldown gating
// ---------------------------------------------------------------------------

describe('SPEC-1879 P3: PhoneOtpVerification resend cooldown gating', () => {
  it('starts 60-second cooldown when onResend() resolves true (success)', async () => {
    const onResend = vi.fn<[], Promise<boolean>>().mockResolvedValue(true);
    render(h(PhoneOtpVerification, makeProps({ onResend })));

    const resendBtn = screen.getByText(locale.phoneOtpResend);
    await userEvent.click(resendBtn);

    await waitFor(() => {
      expect(onResend).toHaveBeenCalledOnce();
      // Button now shows countdown — text starts with the resend label + seconds
      expect(screen.getByText(/\(\d+s\)/)).toBeTruthy();
    });
  });

  it('does NOT start cooldown when onResend() resolves false (transport error)', async () => {
    const onResend = vi.fn<[], Promise<boolean>>().mockResolvedValue(false);
    render(h(PhoneOtpVerification, makeProps({ onResend })));

    const resendBtn = screen.getByText(locale.phoneOtpResend);
    await userEvent.click(resendBtn);

    await waitFor(() => {
      expect(onResend).toHaveBeenCalledOnce();
    });

    // Button should remain with original text (no cooldown suffix)
    expect(screen.getByText(locale.phoneOtpResend)).toBeTruthy();
    expect(screen.queryByText(/\(\d+s\)/)).toBeNull();
  });

  it('allows retry after a completed transport failure', async () => {
    const onResend = vi.fn<[], Promise<boolean>>().mockResolvedValue(false);
    render(h(PhoneOtpVerification, makeProps({ onResend })));

    const resendBtn = screen.getByText(locale.phoneOtpResend);
    await userEvent.click(resendBtn);

    await waitFor(() => {
      expect(onResend).toHaveBeenCalledOnce();
    });

    await userEvent.click(screen.getByText(locale.phoneOtpResend));

    await waitFor(() => {
      expect(onResend).toHaveBeenCalledTimes(2);
    });
  });

  it('suppresses duplicate resend clicks while the first resend is still pending', async () => {
    let resolveResend: ((value: boolean) => void) | undefined;
    const onResend = vi.fn<[], Promise<boolean>>().mockImplementation(
      () => new Promise<boolean>((resolve) => {
        resolveResend = resolve;
      }),
    );
    render(h(PhoneOtpVerification, makeProps({ onResend })));

    const resendBtn = screen.getByText(locale.phoneOtpResend);
    await userEvent.click(resendBtn);
    await userEvent.click(resendBtn);

    expect(onResend).toHaveBeenCalledOnce();

    resolveResend?.(true);

    await waitFor(() => {
      expect(screen.getByText(/\(\d+s\)/)).toBeTruthy();
    });
  });

  it('prevents second click while cooldown is active after success', async () => {
    const onResend = vi.fn<[], Promise<boolean>>().mockResolvedValue(true);
    render(h(PhoneOtpVerification, makeProps({ onResend })));

    const resendBtn = screen.getByText(locale.phoneOtpResend);
    await userEvent.click(resendBtn);

    await waitFor(() => expect(onResend).toHaveBeenCalledOnce());

    // Try clicking the now-disabled countdown button
    const countdownBtn = screen.getByText(/\(\d+s\)/);
    await userEvent.click(countdownBtn);

    // Handler still called only once (button is disabled)
    expect(onResend).toHaveBeenCalledOnce();
  });
});
