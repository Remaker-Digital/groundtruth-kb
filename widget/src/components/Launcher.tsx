/**
 * Launcher — the floating action button that opens/closes the widget.
 *
 * Rendered inside a Shadow DOM (closed) to prevent the merchant's CSS
 * from affecting its appearance. This is the only widget element that
 * lives in the merchant's DOM tree (the conversation panel is in an
 * iframe for full isolation).
 *
 * Architecture (Decision UI-3): Shadow DOM for launcher, iframe for panel.
 * Same approach as Zendesk.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { FunctionComponent } from 'preact';
import type { DesignTokens } from '@/theme/tokens';

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface LauncherProps {
  tokens: DesignTokens;
  position: 'bottom-right' | 'bottom-left';
  offsetX: number;
  offsetY: number;
  isOpen: boolean;
  unreadCount: number;
  launcherIcon: 'chat' | 'headset' | 'help';
  onClick: () => void;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export const Launcher: FunctionComponent<LauncherProps> = ({
  tokens,
  position,
  offsetX,
  offsetY,
  isOpen,
  unreadCount,
  launcherIcon,
  onClick,
}) => {
  const LauncherIconComponent = launcherIcon === 'headset' ? HeadsetIcon
    : launcherIcon === 'help' ? HelpIcon
    : ChatIcon;
  const positionStyle = position === 'bottom-right'
    ? { right: `${offsetX}px`, left: 'auto' }
    : { left: `${offsetX}px`, right: 'auto' };

  return (
    <button
      type="button"
      aria-label={isOpen ? 'Close chat' : 'Open chat'}
      aria-expanded={isOpen}
      onClick={onClick}
      style={{
        position: 'fixed',
        bottom: `${offsetY}px`,
        ...positionStyle,
        zIndex: tokens.zIndexLauncher,
        width: tokens.launcherSize,
        height: tokens.launcherSize,
        borderRadius: tokens.launcherBorderRadius,
        backgroundColor: tokens.colorPrimary,
        color: tokens.colorPrimaryText,
        border: 'none',
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        boxShadow: tokens.shadowLg,
        transition: `transform ${tokens.transitionNormal}, background-color ${tokens.transitionFast}`,
        transform: isOpen ? 'scale(0.9)' : 'scale(1)',
        outline: 'none',
        padding: 0,
      }}
      onMouseEnter={(e) => {
        (e.currentTarget as HTMLElement).style.backgroundColor = tokens.colorPrimaryHover;
      }}
      onMouseLeave={(e) => {
        (e.currentTarget as HTMLElement).style.backgroundColor = tokens.colorPrimary;
      }}
    >
      {/* Launcher icon (open state shows close) */}
      {isOpen ? <CloseIcon size={24} /> : <LauncherIconComponent size={28} />}

      {/* Unread badge */}
      {!isOpen && unreadCount > 0 && (
        <span
          style={{
            position: 'absolute',
            top: '-4px',
            right: '-4px',
            minWidth: '20px',
            height: '20px',
            borderRadius: tokens.borderRadiusFull,
            backgroundColor: tokens.colorError,
            color: '#FFFFFF',
            fontSize: tokens.fontSizeXs,
            fontWeight: tokens.fontWeightBold,
            fontFamily: tokens.fontFamily,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: `0 ${tokens.space1}`,
            lineHeight: 1,
          }}
        >
          {unreadCount > 9 ? '9+' : unreadCount}
        </span>
      )}
    </button>
  );
};

// ---------------------------------------------------------------------------
// Icons (inline SVG to avoid external dependencies)
// ---------------------------------------------------------------------------

function ChatIcon({ size }: { size: number }) {
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
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
    </svg>
  );
}

function HeadsetIcon({ size }: { size: number }) {
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
      <path d="M3 18v-6a9 9 0 0 1 18 0v6" />
      <path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3zM3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z" />
    </svg>
  );
}

function HelpIcon({ size }: { size: number }) {
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
      <circle cx="12" cy="12" r="10" />
      <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />
      <line x1="12" y1="17" x2="12.01" y2="17" />
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
