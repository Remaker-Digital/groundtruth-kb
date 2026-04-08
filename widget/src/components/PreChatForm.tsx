/**
 * PreChatForm — collects customer information before starting a chat.
 *
 * Renders fields defined in the merchant's widget_prechat_form config.
 * Supports:
 *   - Text input fields (name, email, phone, custom)
 *   - Textarea fields (question/description)
 *   - Field-level validation (required, email format)
 *   - Loading state during submission
 *
 * The form configuration shape (from PreferencesDocument.widget_prechat_form):
 *   { fields: [{ name: string, label: string, type: 'text'|'email'|'textarea',
 *                required: boolean, placeholder?: string }] }
 *
 * Visual reference: Zapier (form layouts, input styling, spacing).
 * Functional reference: Tidio (pre-chat form fields, validation).
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { FunctionComponent } from 'preact';
import { useState, useCallback } from 'preact/hooks';
import type { DesignTokens } from '@/theme/tokens';
import type { Locale } from '@/locale/en';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface FormField {
  name: string;
  label: string;
  type: 'text' | 'email' | 'phone' | 'textarea';
  required: boolean;
  placeholder?: string;
}

interface PreChatFormConfig {
  fields: FormField[];
}

interface PreChatFormProps {
  tokens: DesignTokens;
  locale: Locale;
  formConfig: PreChatFormConfig;
  onSubmit: (data: Record<string, string>) => void;
  onSkip?: () => void;
  isLoading: boolean;
}

// ---------------------------------------------------------------------------
// Validation
// ---------------------------------------------------------------------------

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const PHONE_E164_REGEX = /^\+[1-9]\d{1,14}$/;

function validateField(field: FormField, value: string, locale: Locale): string | null {
  if (field.required && !value.trim()) return locale.fieldRequired;
  if (field.type === 'email' && value.trim() && !EMAIL_REGEX.test(value.trim())) {
    return locale.fieldInvalidEmail;
  }
  if (field.type === 'phone' && value.trim() && !PHONE_E164_REGEX.test(value.trim())) {
    return locale.fieldInvalidPhone;
  }
  return null;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export const PreChatForm: FunctionComponent<PreChatFormProps> = ({
  tokens,
  locale,
  formConfig,
  onSubmit,
  onSkip,
  isLoading,
}) => {
  const [values, setValues] = useState<Record<string, string>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});

  const handleChange = useCallback((name: string, value: string) => {
    setValues((prev) => ({ ...prev, [name]: value }));
    // Clear error on change
    if (errors[name]) {
      setErrors((prev) => {
        const next = { ...prev };
        delete next[name];
        return next;
      });
    }
  }, [errors]);

  const handleBlur = useCallback((field: FormField) => {
    setTouched((prev) => ({ ...prev, [field.name]: true }));
    const err = validateField(field, values[field.name] || '', locale);
    if (err) {
      setErrors((prev) => ({ ...prev, [field.name]: err }));
    }
  }, [values, locale]);

  const handleSubmit = useCallback((e: Event) => {
    e.preventDefault();

    // Validate all fields
    const newErrors: Record<string, string> = {};
    const allTouched: Record<string, boolean> = {};

    for (const field of formConfig.fields) {
      allTouched[field.name] = true;
      const err = validateField(field, values[field.name] || '', locale);
      if (err) newErrors[field.name] = err;
    }

    setTouched(allTouched);
    setErrors(newErrors);

    if (Object.keys(newErrors).length > 0) return;

    // Submit clean values
    const data: Record<string, string> = {};
    for (const field of formConfig.fields) {
      const val = (values[field.name] || '').trim();
      if (val) data[field.name] = val;
    }
    onSubmit(data);
  }, [formConfig.fields, values, locale, onSubmit]);

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
          marginBottom: tokens.space4,
        }}
      >
        {locale.preChatTitle}
      </div>

      <form
        onSubmit={handleSubmit}
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: tokens.space4,
        }}
      >
        {formConfig.fields.map((field) => {
          const value = values[field.name] || '';
          const error = touched[field.name] ? errors[field.name] : undefined;
          const isTextarea = field.type === 'textarea';

          return (
            <div key={field.name} style={{ display: 'flex', flexDirection: 'column' }}>
              {/* Label */}
              <label
                style={{
                  fontSize: tokens.fontSizeSm,
                  fontWeight: tokens.fontWeightMedium,
                  fontFamily: tokens.fontFamily,
                  color: tokens.colorText,
                  marginBottom: tokens.space1,
                }}
              >
                {field.label}
                {field.required && (
                  <span style={{ color: tokens.colorError, marginLeft: '2px' }}>*</span>
                )}
              </label>

              {/* Input */}
              {isTextarea ? (
                <textarea
                  value={value}
                  onInput={(e) => handleChange(field.name, (e.target as HTMLTextAreaElement).value)}
                  onBlur={() => handleBlur(field)}
                  placeholder={field.placeholder || ''}
                  rows={3}
                  style={{
                    ...inputBaseStyle(tokens, !!error),
                    resize: 'vertical',
                    minHeight: '72px',
                  }}
                />
              ) : (
                <input
                  type={field.type === 'phone' ? 'tel' : field.type}
                  inputMode={field.type === 'phone' ? 'tel' : undefined}
                  value={value}
                  onInput={(e) => handleChange(field.name, (e.target as HTMLInputElement).value)}
                  onBlur={() => handleBlur(field)}
                  placeholder={field.placeholder || (field.type === 'phone' ? '+15551234567' : '')}
                  style={inputBaseStyle(tokens, !!error)}
                />
              )}

              {/* Error message */}
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
        })}

        {/* Submit button */}
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
          {isLoading ? '...' : locale.preChatSubmit}
        </button>

        {/* "Continue as guest" skip link — soft gate, not hard gate */}
        {onSkip && (
          <button
            type="button"
            onClick={onSkip}
            style={{
              background: 'none',
              border: 'none',
              padding: `${tokens.space2} 0`,
              fontSize: tokens.fontSizeXs,
              fontFamily: tokens.fontFamily,
              color: tokens.colorTextMuted,
              cursor: 'pointer',
              textAlign: 'center',
              textDecoration: 'none',
              outline: 'none',
              marginTop: tokens.space1,
            }}
          >
            {locale.preChatSkip}
          </button>
        )}
      </form>
    </div>
  );
};

// ---------------------------------------------------------------------------
// Shared input style
// ---------------------------------------------------------------------------

function inputBaseStyle(tokens: DesignTokens, hasError: boolean): Record<string, string> {
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
