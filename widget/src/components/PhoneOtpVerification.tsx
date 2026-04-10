// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * PhoneOtpVerification — 6-digit code entry screen for SMS phone verification.
 *
 * Displayed after pre-chat form phone collection when SMS OTP is enabled.
 * Mirrors OtpVerification.tsx but for phone/SMS channel (SPEC-1879 Phase 3).
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { FunctionComponent } from 'preact';
import { useState, useCallback, useRef, useEffect } from 'preact/hooks';
import type { DesignTokens } from '@/theme/tokens';
import type { Locale } from '@/locale/en';

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface PhoneOtpVerificationProps {
  tokens: DesignTokens;
  locale: Locale;
  phone: string;
  onVerify: (code: string) => void;
  onSkip?: () => void;
  onResend: () => Promise<boolean>;
  isLoading: boolean;
  error?: string;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export const PhoneOtpVerification: FunctionComponent<PhoneOtpVerificationProps> = ({
  tokens,
  locale,
  phone,
  onVerify,
  onSkip,
  onResend,
  isLoading,
  error,
}) => {
  const [digits, setDigits] = useState<string[]>(['', '', '', '', '', '']);
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);
  const resendInFlightRef = useRef(false);
  const [resendCooldown, setResendCooldown] = useState(0);
  const [resendPending, setResendPending] = useState(false);

  // Auto-focus first input on mount
  useEffect(() => {
    inputRefs.current[0]?.focus();
  }, []);

  // Clear digit inputs on verification failure so the customer starts fresh
  useEffect(() => {
    if (error) {
      setDigits(['', '', '', '', '', '']);
      inputRefs.current[0]?.focus();
    }
  }, [error]);

  // Resend cooldown timer
  useEffect(() => {
    if (resendCooldown <= 0) return;
    const timer = setTimeout(() => setResendCooldown((c) => c - 1), 1000);
    return () => clearTimeout(timer);
  }, [resendCooldown]);

  const handleDigitChange = useCallback(
    (index: number, value: string) => {
      const digit = value.replace(/\D/g, '').slice(-1);
      setDigits((prev) => {
        const next = [...prev];
        next[index] = digit;
        return next;
      });
      if (digit && index < 5) {
        inputRefs.current[index + 1]?.focus();
      }
    },
    [],
  );

  const handleKeyDown = useCallback(
    (index: number, e: KeyboardEvent) => {
      if (e.key === 'Backspace' && !digits[index] && index > 0) {
        inputRefs.current[index - 1]?.focus();
      }
    },
    [digits],
  );

  const handlePaste = useCallback(
    (e: ClipboardEvent) => {
      e.preventDefault();
      const pasted = (e.clipboardData?.getData('text') ?? '').replace(/\D/g, '').slice(0, 6);
      if (!pasted) return;

      const newDigits = [...digits];
      for (let i = 0; i < pasted.length; i++) {
        newDigits[i] = pasted[i];
      }
      setDigits(newDigits);

      const focusIndex = Math.min(pasted.length, 5);
      inputRefs.current[focusIndex]?.focus();
    },
    [digits],
  );

  const handleSubmit = useCallback(
    (e: Event) => {
      e.preventDefault();
      const code = digits.join('');
      if (code.length === 6) {
        onVerify(code);
      }
    },
    [digits, onVerify],
  );

  const handleResend = useCallback(async () => {
    if (resendCooldown > 0 || resendInFlightRef.current || isLoading) return;

    resendInFlightRef.current = true;
    setResendPending(true);
    try {
      const success = await onResend();
    // Only start cooldown if the send succeeded or was an intentional tier-gate outcome.
    // On transport failure onResend() returns false — suppress cooldown so the
    // customer can retry immediately without being locked out for 60 seconds.
    if (success) setResendCooldown(60);
    } finally {
      resendInFlightRef.current = false;
      setResendPending(false);
    }
  }, [isLoading, onResend, resendCooldown]);

  // Mask phone for display: show country code + last 3 digits
  const maskedPhone = phone.length > 6
    ? `${phone.slice(0, 3)}***${phone.slice(-3)}`
    : phone;

  const isComplete = digits.every((d) => d !== '');
  const resendDisabled = resendCooldown > 0 || resendPending || isLoading;

  return (
    <div
      style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        padding: tokens.space6,
        overflow: 'auto',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      {/* Prompt */}
      <div
        style={{
          fontSize: tokens.fontSizeMd,
          fontWeight: tokens.fontWeightMedium,
          fontFamily: tokens.fontFamily,
          color: tokens.colorText,
          marginBottom: tokens.space2,
          textAlign: 'center',
        }}
      >
        {locale.phoneOtpPrompt}
      </div>

      {/* Phone display (masked) */}
      <div
        style={{
          fontSize: tokens.fontSizeSm,
          fontFamily: tokens.fontFamily,
          color: tokens.colorTextMuted,
          marginBottom: tokens.space6,
          textAlign: 'center',
        }}
      >
        {maskedPhone}
      </div>

      {/* 6-digit input grid */}
      <form onSubmit={handleSubmit}>
        <div
          style={{
            display: 'flex',
            gap: tokens.space2,
            marginBottom: tokens.space4,
            justifyContent: 'center',
          }}
        >
          {digits.map((digit, i) => (
            <input
              key={i}
              ref={(el) => { inputRefs.current[i] = el; }}
              type="text"
              inputMode="numeric"
              maxLength={1}
              value={digit}
              onInput={(e) => handleDigitChange(i, (e.target as HTMLInputElement).value)}
              onKeyDown={(e) => handleKeyDown(i, e as unknown as KeyboardEvent)}
              onPaste={i === 0 ? (e) => handlePaste(e as unknown as ClipboardEvent) : undefined}
              style={{
                width: '40px',
                height: '48px',
                textAlign: 'center',
                fontSize: '20px',
                fontWeight: tokens.fontWeightSemibold,
                fontFamily: tokens.fontFamily,
                color: tokens.colorText,
                backgroundColor: tokens.colorBackground,
                border: `${tokens.borderWidth} solid ${error ? tokens.colorError : tokens.colorBorder}`,
                borderRadius: tokens.borderRadius,
                outline: 'none',
                transition: `border-color ${tokens.transitionFast}`,
              }}
              aria-label={`Digit ${i + 1}`}
            />
          ))}
        </div>

        {/* Error message */}
        {error && (
          <div
            style={{
              fontSize: tokens.fontSizeXs,
              fontFamily: tokens.fontFamily,
              color: tokens.colorError,
              textAlign: 'center',
              marginBottom: tokens.space3,
            }}
          >
            {error}
          </div>
        )}

        {/* Verify button */}
        <button
          type="submit"
          disabled={isLoading || !isComplete}
          style={{
            width: '100%',
            padding: `${tokens.space3} ${tokens.space4}`,
            backgroundColor: tokens.colorPrimary,
            color: tokens.colorPrimaryText,
            border: 'none',
            borderRadius: tokens.borderRadius,
            fontSize: tokens.fontSizeMd,
            fontWeight: tokens.fontWeightSemibold,
            fontFamily: tokens.fontFamily,
            cursor: isLoading || !isComplete ? 'default' : 'pointer',
            opacity: isLoading || !isComplete ? 0.5 : 1,
            transition: `background-color ${tokens.transitionFast}, opacity ${tokens.transitionFast}`,
            outline: 'none',
          }}
        >
          {isLoading ? '...' : locale.otpVerify}
        </button>
      </form>

      {/* Resend link */}
      <button
        type="button"
        onClick={handleResend}
        disabled={resendDisabled}
        style={{
          background: 'none',
          border: 'none',
          padding: `${tokens.space3} 0`,
          fontSize: tokens.fontSizeXs,
          fontFamily: tokens.fontFamily,
          color: resendDisabled ? tokens.colorTextMuted : tokens.colorPrimary,
          cursor: resendDisabled ? 'default' : 'pointer',
          textAlign: 'center',
          textDecoration: 'none',
          outline: 'none',
        }}
      >
        {resendCooldown > 0
          ? `${locale.phoneOtpResend} (${resendCooldown}s)`
          : locale.phoneOtpResend}
      </button>

      {/* Skip link — only if optional */}
      {onSkip && (
        <button
          type="button"
          onClick={onSkip}
          style={{
            background: 'none',
            border: 'none',
            padding: `${tokens.space1} 0`,
            fontSize: tokens.fontSizeXs,
            fontFamily: tokens.fontFamily,
            color: tokens.colorTextMuted,
            cursor: 'pointer',
            textAlign: 'center',
            textDecoration: 'none',
            outline: 'none',
          }}
        >
          {locale.otpSkip}
        </button>
      )}
    </div>
  );
};
