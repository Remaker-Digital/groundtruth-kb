/**
 * ConsentBanner — collects customer consent for Persistent Customer Memory.
 *
 * Displayed at the top of the conversation view when the tenant has
 * consent_collection_enabled = true and consent hasn't been collected yet.
 *
 * The banner is dismissable: "Allow" records granted, "No thanks" records
 * denied. Either choice hides the banner for the rest of the session.
 *
 * WI #87: Widget consent collection for PCM vectorization.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { FunctionComponent } from 'preact';
import type { DesignTokens } from '@/theme/tokens';
import type { Locale } from '@/locale/en';

interface ConsentBannerProps {
  tokens: DesignTokens;
  locale: Locale;
  onAccept: () => void;
  onDecline: () => void;
}

export const ConsentBanner: FunctionComponent<ConsentBannerProps> = ({
  tokens,
  locale,
  onAccept,
  onDecline,
}) => {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: tokens.space2,
        padding: `${tokens.space3} ${tokens.space4}`,
        backgroundColor: tokens.colorSurface,
        borderBottom: `1px solid ${tokens.colorBorder}`,
        fontSize: tokens.fontSizeXs,
        fontFamily: tokens.fontFamily,
        color: tokens.colorTextSecondary,
        animation: 'ar-fade-in 0.3s ease',
        flexShrink: 0,
      }}
    >
      <div style={{ lineHeight: '1.4' }}>
        {locale.consentPrompt}
      </div>
      <div style={{ display: 'flex', gap: tokens.space2 }}>
        <button
          type="button"
          onClick={onAccept}
          style={{
            padding: `${tokens.space1} ${tokens.space3}`,
            fontSize: tokens.fontSizeXs,
            fontFamily: tokens.fontFamily,
            fontWeight: tokens.fontWeightMedium,
            color: '#FFFFFF',
            backgroundColor: tokens.colorPrimary,
            border: 'none',
            borderRadius: tokens.borderRadius,
            cursor: 'pointer',
          }}
        >
          {locale.consentAccept}
        </button>
        <button
          type="button"
          onClick={onDecline}
          style={{
            padding: `${tokens.space1} ${tokens.space3}`,
            fontSize: tokens.fontSizeXs,
            fontFamily: tokens.fontFamily,
            fontWeight: tokens.fontWeightMedium,
            color: tokens.colorTextSecondary,
            backgroundColor: 'transparent',
            border: `1px solid ${tokens.colorBorder}`,
            borderRadius: tokens.borderRadius,
            cursor: 'pointer',
          }}
        >
          {locale.consentDecline}
        </button>
      </div>
    </div>
  );
};
