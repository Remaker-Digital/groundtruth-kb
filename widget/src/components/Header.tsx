/**
 * Header — top bar of the conversation panel.
 *
 * Displays:
 *   - Agent avatar (configurable)
 *   - Agent name + title
 *   - Online status indicator
 *   - Close button
 *
 * Visual reference: Zapier (clean, minimal, consistent spacing).
 * Functional reference: Tidio (avatar, name, status, close).
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { h, FunctionComponent } from 'preact';
import type { DesignTokens } from '@/theme/tokens';
import type { Locale } from '@/locale/en';

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface HeaderProps {
  tokens: DesignTokens;
  locale: Locale;
  agentName: string;
  agentTitle: string;
  agentAvatarUrl: string | null;
  logoUrl: string | null;
  headerText: string | null;
  onClose: () => void;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export const Header: FunctionComponent<HeaderProps> = ({
  tokens,
  locale,
  agentName,
  agentTitle,
  agentAvatarUrl,
  logoUrl,
  headerText,
  onClose,
}) => {
  const displayTitle = headerText || locale.headerTitle;

  return (
    <div
      style={{
        height: tokens.headerHeight,
        backgroundColor: tokens.colorPrimary,
        color: tokens.colorPrimaryText,
        display: 'flex',
        alignItems: 'center',
        padding: `0 ${tokens.space4}`,
        flexShrink: 0,
        position: 'relative',
      }}
    >
      {/* Agent avatar */}
      <div
        style={{
          width: tokens.avatarSize,
          height: tokens.avatarSize,
          borderRadius: tokens.borderRadiusFull,
          backgroundColor: 'rgba(255,255,255,0.2)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          overflow: 'hidden',
          flexShrink: 0,
        }}
      >
        {agentAvatarUrl ? (
          <img
            src={agentAvatarUrl}
            alt={agentName}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
            }}
          />
        ) : (
          <AgentDefaultIcon size={22} />
        )}
      </div>

      {/* Agent info */}
      <div
        style={{
          marginLeft: tokens.space3,
          flex: 1,
          minWidth: 0,
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            fontSize: tokens.fontSizeMd,
            fontWeight: tokens.fontWeightSemibold,
            fontFamily: tokens.fontFamily,
            lineHeight: tokens.lineHeightTight,
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
          }}
        >
          {displayTitle}
        </div>
        <div
          style={{
            fontSize: tokens.fontSizeXs,
            fontFamily: tokens.fontFamily,
            opacity: 0.85,
            lineHeight: tokens.lineHeightTight,
            marginTop: '2px',
            display: 'flex',
            alignItems: 'center',
            gap: tokens.space1,
          }}
        >
          {/* Online status dot */}
          <span
            style={{
              width: '6px',
              height: '6px',
              borderRadius: tokens.borderRadiusFull,
              backgroundColor: tokens.colorSuccess,
              display: 'inline-block',
              flexShrink: 0,
            }}
          />
          <span
            style={{
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
            }}
          >
            {agentName}{agentTitle ? ` \u00B7 ${agentTitle}` : ''}
          </span>
        </div>
      </div>

      {/* Logo (if provided) */}
      {logoUrl && (
        <img
          src={logoUrl}
          alt="Logo"
          style={{
            height: '24px',
            width: 'auto',
            marginRight: tokens.space2,
            opacity: 0.9,
          }}
        />
      )}

      {/* Close button */}
      <button
        type="button"
        aria-label={locale.closeWidget}
        onClick={onClose}
        style={{
          background: 'none',
          border: 'none',
          color: 'inherit',
          cursor: 'pointer',
          padding: tokens.space2,
          margin: `0 -${tokens.space2} 0 0`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          borderRadius: tokens.borderRadiusSm,
          transition: `background-color ${tokens.transitionFast}`,
          outline: 'none',
          opacity: 0.9,
        }}
        onMouseEnter={(e) => {
          (e.currentTarget as HTMLElement).style.backgroundColor = 'rgba(255,255,255,0.15)';
        }}
        onMouseLeave={(e) => {
          (e.currentTarget as HTMLElement).style.backgroundColor = 'transparent';
        }}
      >
        <CloseIcon size={18} />
      </button>
    </div>
  );
};

// ---------------------------------------------------------------------------
// Icons (inline SVG)
// ---------------------------------------------------------------------------

function AgentDefaultIcon({ size }: { size: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="currentColor"
    >
      <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
    </svg>
  );
}

function CloseIcon({ size }: { size: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    >
      <line x1="18" y1="6" x2="6" y2="18" />
      <line x1="6" y1="6" x2="18" y2="18" />
    </svg>
  );
}
