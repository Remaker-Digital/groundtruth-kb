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

import { FunctionComponent } from 'preact';
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
  /** Subtitle shown below the title (e.g. "We typically reply within minutes"). */
  headerSubtitle: string | null;
  /** Optional second color for a left→right gradient header. */
  gradientEnd: string | null;
  onClose: () => void;
  /** Enable drag-to-reposition by mousedown on header (WI #253). */
  onDragStart?: (e: MouseEvent) => void;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export const Header: FunctionComponent<HeaderProps> = ({
  tokens,
  locale,
  agentName,
  agentTitle: _agentTitle,
  agentAvatarUrl,
  logoUrl,
  headerText,
  headerSubtitle,
  gradientEnd,
  onClose,
  onDragStart,
}) => {
  const displayTitle = headerText || locale.headerTitle;
  const displaySubtitle = headerSubtitle || 'We typically reply within minutes';
  // Avatar initials: first 2 chars of agent name (WI-0872 consistency fix)
  const avatarInitials = agentName.slice(0, 2).toUpperCase() || 'AR';

  // Header background: gradient when a second color is configured, flat otherwise
  const headerBg = gradientEnd
    ? `linear-gradient(135deg, ${tokens.colorPrimary} 0%, ${gradientEnd} 100%)`
    : tokens.colorPrimary;

  return (
    <div
      style={{
        height: tokens.headerHeight,
        background: headerBg,
        color: tokens.colorPrimaryText,
        display: 'flex',
        alignItems: 'center',
        padding: `0 ${tokens.space4}`,
        flexShrink: 0,
        position: 'relative',
        cursor: onDragStart ? 'grab' : undefined,
        userSelect: onDragStart ? 'none' : undefined,
      }}
      onMouseDown={(e) => {
        // Only start drag on left-click and if target is not the close button
        if (onDragStart && e.button === 0 && !(e.target as HTMLElement).closest('button')) {
          onDragStart(e as unknown as MouseEvent);
        }
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
          fontSize: '12px',
          fontWeight: 700,
          color: '#fff',
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
          avatarInitials
        )}
      </div>

      {/* Agent info — 3 rows: title / subtitle / online */}
      <div
        style={{
          marginLeft: tokens.space3,
          flex: 1,
          minWidth: 0,
          overflow: 'hidden',
        }}
      >
        {/* Row 1: Title */}
        <div
          style={{
            fontSize: tokens.fontSizeSm,
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
        {/* Row 2: Subtitle */}
        <div
          style={{
            fontSize: tokens.fontSizeXs,
            fontFamily: tokens.fontFamily,
            color: 'rgba(255,255,255,0.85)',
            lineHeight: 1.3,
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
          }}
        >
          {displaySubtitle}
        </div>
        {/* Row 3: Online indicator */}
        <div
          style={{
            fontSize: '10px',
            fontFamily: tokens.fontFamily,
            color: 'rgba(255,255,255,0.8)',
            lineHeight: tokens.lineHeightTight,
            marginTop: '2px',
            display: 'flex',
            alignItems: 'center',
            gap: tokens.space1,
          }}
        >
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
          <span>Online</span>
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
