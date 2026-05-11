// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * OtpVerification — 6-digit code entry screen for email verification.
 *
 * Displayed after the pre-chat form when customer_email_verification
 * is "required" or "optional". The customer enters the OTP code
 * received by email.
 *
 * Design: Minimal — "Enter the code we sent to your email." + 6-digit
 * input + Verify button. No elaboration per owner directive.
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

interface OtpVerificationProps {
  tokens: DesignTokens;
  locale: Locale;
  email: string;
  onVerify: (code: string) => void;
  onSkip?: () => void;
  onResend: () => void;
  isLoading: boolean;
  error?: string;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export const OtpVerification: FunctionComponent<OtpVerificationProps> = ({
  tokens,
  locale,
  email,
  onVerify,
  onSkip,
  onResend,
  isLoading,
  error,
}) => {
  const [digits, setDigits] = useState<string[]>(['', '', '', '', '', '']);
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);
  const [resendCooldown, setResendCooldown] = useState(0);

  // Auto-focus first input on mount
  useEffect(() => {
    inputRefs.current[0]?.focus();
  }, []);

  // Resend cooldown timer
  useEffect(() => {
    if (resendCooldown <= 0) return;
    const timer = setTimeout(() => setResendCooldown((c) => c - 1), 1000);
    return () => clearTimeout(timer);
  }, [resendCooldown]);

  const handleDigitChange = useCallback(
    (index: number, value: string) => {
      // Only accept digits
      const digit = value.replace(/\D/g, '').slice(-1);
      setDigits((prev) => {
        const next = [...prev];
        next[index] = digit;
        return next;
      });

      // Auto-advance to next input
      if (digit && index < 5) {
        inputRefs.current[index + 1]?.focus();
      }
    },
    [],
  );

  const handleKeyDown = useCallback(
    (index: number, e: KeyboardEvent) => {
      if (e.key === 'Backspace' && !digits[index] && index > 0) {
        // Move back on backspace when current input is empty
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

      // Focus the input after the last pasted digit
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

  const handleResend = useCallback(() => {
    if (resendCooldown > 0) return;
    onResend();
    setResendCooldown(60); // 60-second cooldown
  }, [resendCooldown, onResend]);

  const isComplete = digits.every((d) => d !== '');

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
      {/* Prompt — minimal per owner directive */}
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
        {locale.otpPrompt}
      </div>

      {/* Email display */}
      <div
        style={{
          fontSize: tokens.fontSizeSm,
          fontFamily: tokens.fontFamily,
          color: tokens.colorTextMuted,
          marginBottom: tokens.space6,
          textAlign: 'center',
        }}
      >
        {email}
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
        disabled={resendCooldown > 0}
        style={{
          background: 'none',
          border: 'none',
          padding: `${tokens.space3} 0`,
          fontSize: tokens.fontSizeXs,
          fontFamily: tokens.fontFamily,
          color: resendCooldown > 0 ? tokens.colorTextMuted : tokens.colorPrimary,
          cursor: resendCooldown > 0 ? 'default' : 'pointer',
          textAlign: 'center',
          textDecoration: 'none',
          outline: 'none',
        }}
      >
        {resendCooldown > 0
          ? `${locale.otpResend} (${resendCooldown}s)`
          : locale.otpResend}
      </button>

      {/* "Continue without verifying" skip link — only if mode is "optional" */}
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
