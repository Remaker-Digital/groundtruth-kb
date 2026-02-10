/**
 * IssueReport — customer-facing issue report form.
 *
 * Allows end customers to report issues with the AI conversation
 * back to the merchant. Issue categories:
 *   - Wrong information
 *   - Rude response
 *   - Not helpful
 *   - Other
 *
 * C7: Report an Issue widget button.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { FunctionComponent } from 'preact';
import { useState, useCallback } from 'preact/hooks';
import type { DesignTokens } from '@/theme/tokens';
import type { Locale } from '@/locale/en';

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface IssueReportProps {
  tokens: DesignTokens;
  locale: Locale;
  onSubmit: (issueType: string, details: string) => Promise<void>;
  onCancel: () => void;
  isLoading: boolean;
}

// ---------------------------------------------------------------------------
// Issue type options
// ---------------------------------------------------------------------------

const ISSUE_TYPES = [
  { value: 'wrong_information', localeKey: 'issueTypeWrongInfo' as const },
  { value: 'rude_response', localeKey: 'issueTypeRudeResponse' as const },
  { value: 'not_helpful', localeKey: 'issueTypeNotHelpful' as const },
  { value: 'other', localeKey: 'issueTypeOther' as const },
];

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export const IssueReport: FunctionComponent<IssueReportProps> = ({
  tokens,
  locale,
  onSubmit,
  onCancel,
  isLoading,
}) => {
  const [selectedType, setSelectedType] = useState<string>('');
  const [details, setDetails] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = useCallback(async () => {
    if (!selectedType || isLoading) return;

    try {
      await onSubmit(selectedType, details);
      setSubmitted(true);
    } catch {
      // Error handling is done by the parent
    }
  }, [selectedType, details, isLoading, onSubmit]);

  // ---- Success state -------------------------------------------------------

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
          gap: tokens.space4,
          textAlign: 'center',
        }}
      >
        {/* Checkmark icon */}
        <div
          style={{
            width: '48px',
            height: '48px',
            borderRadius: '50%',
            backgroundColor: '#22C55E',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            animation: 'ar-fade-in 0.3s ease',
          }}
        >
          <svg
            width={24}
            height={24}
            viewBox="0 0 24 24"
            fill="none"
            stroke="#FFFFFF"
            stroke-width="2.5"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <polyline points="20 6 9 17 4 12" />
          </svg>
        </div>

        <p
          style={{
            fontSize: tokens.fontSizeMd,
            fontWeight: tokens.fontWeightMedium,
            color: tokens.colorText,
            margin: 0,
          }}
        >
          {locale.issueSubmitSuccess}
        </p>

        <button
          type="button"
          onClick={onCancel}
          style={{
            marginTop: tokens.space2,
            padding: `${tokens.space2} ${tokens.space6}`,
            fontSize: tokens.fontSizeSm,
            fontFamily: tokens.fontFamily,
            fontWeight: tokens.fontWeightMedium,
            color: tokens.colorPrimary,
            backgroundColor: 'transparent',
            border: `1px solid ${tokens.colorPrimary}`,
            borderRadius: tokens.borderRadius,
            cursor: 'pointer',
          }}
        >
          {locale.issueCancel}
        </button>
      </div>
    );
  }

  // ---- Form state ----------------------------------------------------------

  return (
    <div
      style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        padding: tokens.space4,
        gap: tokens.space4,
        overflowY: 'auto',
        animation: 'ar-slide-up 0.25s ease',
      }}
    >
      {/* Title */}
      <div>
        <h3
          style={{
            fontSize: tokens.fontSizeLg,
            fontWeight: tokens.fontWeightBold,
            color: tokens.colorText,
            margin: `0 0 ${tokens.space1} 0`,
          }}
        >
          {locale.issueReportTitle}
        </h3>
        <p
          style={{
            fontSize: tokens.fontSizeSm,
            color: tokens.colorTextSecondary,
            margin: 0,
          }}
        >
          {locale.issueReportDescription}
        </p>
      </div>

      {/* Issue type selector */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: tokens.space2 }}>
        {ISSUE_TYPES.map(({ value, localeKey }) => (
          <button
            key={value}
            type="button"
            onClick={() => setSelectedType(value)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: tokens.space3,
              padding: `${tokens.space3} ${tokens.space4}`,
              fontSize: tokens.fontSizeSm,
              fontFamily: tokens.fontFamily,
              fontWeight: selectedType === value ? tokens.fontWeightMedium : tokens.fontWeightNormal,
              color: tokens.colorText,
              backgroundColor: selectedType === value
                ? `${tokens.colorPrimary}15`
                : tokens.colorSurface,
              border: `1px solid ${selectedType === value ? tokens.colorPrimary : tokens.colorBorder}`,
              borderRadius: tokens.borderRadius,
              cursor: 'pointer',
              textAlign: 'left',
              transition: 'all 0.15s ease',
            }}
          >
            {/* Radio circle */}
            <div
              style={{
                width: '16px',
                height: '16px',
                borderRadius: '50%',
                border: `2px solid ${selectedType === value ? tokens.colorPrimary : tokens.colorBorder}`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
              }}
            >
              {selectedType === value && (
                <div
                  style={{
                    width: '8px',
                    height: '8px',
                    borderRadius: '50%',
                    backgroundColor: tokens.colorPrimary,
                  }}
                />
              )}
            </div>
            {locale[localeKey]}
          </button>
        ))}
      </div>

      {/* Details textarea */}
      <textarea
        value={details}
        onInput={(e) => setDetails((e.target as HTMLTextAreaElement).value)}
        placeholder={locale.issueDetailsPlaceholder}
        maxLength={2000}
        style={{
          padding: tokens.space3,
          fontSize: tokens.fontSizeSm,
          fontFamily: tokens.fontFamily,
          color: tokens.colorText,
          backgroundColor: tokens.colorSurface,
          border: `1px solid ${tokens.colorBorder}`,
          borderRadius: tokens.borderRadius,
          resize: 'vertical',
          minHeight: '80px',
          maxHeight: '160px',
          outline: 'none',
        }}
      />

      {/* Actions */}
      <div
        style={{
          display: 'flex',
          gap: tokens.space3,
          marginTop: 'auto',
          paddingTop: tokens.space2,
        }}
      >
        <button
          type="button"
          onClick={onCancel}
          style={{
            flex: 1,
            padding: `${tokens.space3} ${tokens.space4}`,
            fontSize: tokens.fontSizeSm,
            fontFamily: tokens.fontFamily,
            fontWeight: tokens.fontWeightMedium,
            color: tokens.colorText,
            backgroundColor: tokens.colorSurface,
            border: `1px solid ${tokens.colorBorder}`,
            borderRadius: tokens.borderRadius,
            cursor: 'pointer',
          }}
        >
          {locale.issueCancel}
        </button>

        <button
          type="button"
          onClick={handleSubmit}
          disabled={!selectedType || isLoading}
          style={{
            flex: 1,
            padding: `${tokens.space3} ${tokens.space4}`,
            fontSize: tokens.fontSizeSm,
            fontFamily: tokens.fontFamily,
            fontWeight: tokens.fontWeightMedium,
            color: '#FFFFFF',
            backgroundColor: !selectedType || isLoading
              ? `${tokens.colorPrimary}80`
              : tokens.colorPrimary,
            border: 'none',
            borderRadius: tokens.borderRadius,
            cursor: !selectedType || isLoading ? 'not-allowed' : 'pointer',
            opacity: isLoading ? 0.7 : 1,
          }}
        >
          {isLoading ? locale.issueSubmitting : locale.issueSubmit}
        </button>
      </div>
    </div>
  );
};
