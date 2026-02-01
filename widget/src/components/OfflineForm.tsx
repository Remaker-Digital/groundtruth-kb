/**
 * OfflineForm — leave-a-message form when chat is unavailable.
 *
 * Shown when:
 *   - Operating hours are configured and it's outside hours
 *   - widget_offline_behavior === 'show_form'
 *
 * Collects name, email, and message. Submits to the API for
 * follow-up by the merchant's team.
 *
 * Visual reference: Zapier (form styling, spacing, button design).
 * Functional reference: Tidio (offline form fields, success state).
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { h, FunctionComponent } from 'preact';
import { useState, useCallback } from 'preact/hooks';
import type { DesignTokens } from '@/theme/tokens';
import type { Locale } from '@/locale/en';

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface OfflineFormProps {
  tokens: DesignTokens;
  locale: Locale;
  offlineMessage: string | null;
  onSubmit: (data: { name: string; email: string; message: string }) => void;
  isLoading: boolean;
}

// ---------------------------------------------------------------------------
// Validation
// ---------------------------------------------------------------------------

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export const OfflineForm: FunctionComponent<OfflineFormProps> = ({
  tokens,
  locale,
  offlineMessage,
  onSubmit,
  isLoading,
}) => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [submitted, setSubmitted] = useState(false);

  const validate = useCallback((): Record<string, string> => {
    const errs: Record<string, string> = {};
    if (!name.trim()) errs.name = locale.fieldRequired;
    if (!email.trim()) errs.email = locale.fieldRequired;
    else if (!EMAIL_REGEX.test(email.trim())) errs.email = locale.fieldInvalidEmail;
    if (!message.trim()) errs.message = locale.fieldRequired;
    return errs;
  }, [name, email, message, locale]);

  const handleSubmit = useCallback((e: Event) => {
    e.preventDefault();
    const errs = validate();
    setErrors(errs);
    if (Object.keys(errs).length > 0) return;

    onSubmit({
      name: name.trim(),
      email: email.trim(),
      message: message.trim(),
    });
    setSubmitted(true);
  }, [validate, name, email, message, onSubmit]);

  if (submitted) {
    return (
      <div
        style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: tokens.space6,
          textAlign: 'center',
          animation: 'ar-fade-in 0.3s ease',
        }}
      >
        {/* Success icon */}
        <div
          style={{
            width: '48px',
            height: '48px',
            borderRadius: tokens.borderRadiusFull,
            backgroundColor: tokens.colorSuccess,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: tokens.space4,
          }}
        >
          <svg
            width={24}
            height={24}
            viewBox="0 0 24 24"
            fill="none"
            stroke="#FFFFFF"
            stroke-width="3"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <polyline points="20 6 9 17 4 12" />
          </svg>
        </div>
        <div
          style={{
            fontSize: tokens.fontSizeLg,
            fontWeight: tokens.fontWeightSemibold,
            fontFamily: tokens.fontFamily,
            color: tokens.colorText,
            lineHeight: tokens.lineHeightNormal,
          }}
        >
          {locale.offlineFormSuccess}
        </div>
      </div>
    );
  }

  return (
    <div
      style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        padding: tokens.space6,
        overflow: 'auto',
      }}
    >
      {/* Title */}
      <div
        style={{
          fontSize: tokens.fontSizeLg,
          fontWeight: tokens.fontWeightSemibold,
          fontFamily: tokens.fontFamily,
          color: tokens.colorText,
          marginBottom: tokens.space2,
        }}
      >
        {locale.offlineFormTitle}
      </div>

      {/* Offline message */}
      {offlineMessage && (
        <div
          style={{
            fontSize: tokens.fontSizeSm,
            fontFamily: tokens.fontFamily,
            color: tokens.colorTextSecondary,
            lineHeight: tokens.lineHeightNormal,
            marginBottom: tokens.space4,
          }}
        >
          {offlineMessage}
        </div>
      )}

      <form
        onSubmit={handleSubmit}
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: tokens.space3,
        }}
      >
        {/* Name */}
        <FieldGroup
          tokens={tokens}
          label="Name"
          required
          error={errors.name}
        >
          <input
            type="text"
            value={name}
            onInput={(e) => setName((e.target as HTMLInputElement).value)}
            style={inputStyle(tokens, !!errors.name)}
          />
        </FieldGroup>

        {/* Email */}
        <FieldGroup
          tokens={tokens}
          label="Email"
          required
          error={errors.email}
        >
          <input
            type="email"
            value={email}
            onInput={(e) => setEmail((e.target as HTMLInputElement).value)}
            style={inputStyle(tokens, !!errors.email)}
          />
        </FieldGroup>

        {/* Message */}
        <FieldGroup
          tokens={tokens}
          label="Message"
          required
          error={errors.message}
        >
          <textarea
            value={message}
            onInput={(e) => setMessage((e.target as HTMLTextAreaElement).value)}
            rows={4}
            style={{
              ...inputStyle(tokens, !!errors.message),
              resize: 'vertical',
              minHeight: '80px',
            }}
          />
        </FieldGroup>

        {/* Submit */}
        <button
          type="submit"
          disabled={isLoading}
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
            cursor: isLoading ? 'default' : 'pointer',
            opacity: isLoading ? 0.7 : 1,
            transition: `background-color ${tokens.transitionFast}, opacity ${tokens.transitionFast}`,
            outline: 'none',
            marginTop: tokens.space2,
          }}
        >
          {isLoading ? '...' : locale.offlineFormSubmit}
        </button>
      </form>
    </div>
  );
};

// ---------------------------------------------------------------------------
// Field group helper
// ---------------------------------------------------------------------------

const FieldGroup: FunctionComponent<{
  tokens: DesignTokens;
  label: string;
  required?: boolean;
  error?: string;
}> = ({ tokens, label, required, error, children }) => (
  <div style={{ display: 'flex', flexDirection: 'column' }}>
    <label
      style={{
        fontSize: tokens.fontSizeSm,
        fontWeight: tokens.fontWeightMedium,
        fontFamily: tokens.fontFamily,
        color: tokens.colorText,
        marginBottom: tokens.space1,
      }}
    >
      {label}
      {required && <span style={{ color: tokens.colorError, marginLeft: '2px' }}>*</span>}
    </label>
    {children}
    {error && (
      <div
        style={{
          fontSize: tokens.fontSizeXs,
          fontFamily: tokens.fontFamily,
          color: tokens.colorError,
          marginTop: tokens.space1,
        }}
      >
        {error}
      </div>
    )}
  </div>
);

// ---------------------------------------------------------------------------
// Shared input style
// ---------------------------------------------------------------------------

function inputStyle(tokens: DesignTokens, hasError: boolean): Record<string, string> {
  return {
    width: '100%',
    padding: `${tokens.space2} ${tokens.space3}`,
    fontSize: tokens.fontSizeMd,
    fontFamily: tokens.fontFamily,
    color: tokens.colorText,
    backgroundColor: tokens.colorBackground,
    border: `${tokens.borderWidth} solid ${hasError ? tokens.colorError : tokens.colorBorder}`,
    borderRadius: tokens.borderRadius,
    outline: 'none',
    transition: `border-color ${tokens.transitionFast}`,
    lineHeight: `${tokens.lineHeightNormal}`,
  };
}
