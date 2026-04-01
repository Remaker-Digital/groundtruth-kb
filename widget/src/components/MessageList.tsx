/**
 * MessageList — scrollable container for conversation messages.
 *
 * Handles:
 *   - Auto-scroll to bottom on new messages
 *   - "Scroll to latest" button when user scrolls up
 *   - Day separator labels (Today, Yesterday, date)
 *   - Consecutive message grouping (hide avatar for runs of agent msgs)
 *   - Typing indicator
 *   - Greeting message (first thing the user sees)
 *
 * Visual reference: Zapier (clean scrollbar, generous padding).
 * Functional reference: Tidio (auto-scroll, date separators, typing dots).
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { FunctionComponent, JSX } from 'preact';
import { useRef, useEffect, useState, useCallback } from 'preact/hooks';
import type { DesignTokens, QuickActionButton } from '@/theme/tokens';
import type { Locale } from '@/locale/en';
import type { Message } from '@/state/store';
import { MessageBubble, TypingIndicator } from './MessageBubble';
import { QuickActions } from './QuickActions';

// ---------------------------------------------------------------------------
// Scrollbar styles (injected once into widget shadow DOM)
// ---------------------------------------------------------------------------

let scrollStyleInjected = false;

function injectScrollbarStyles(): void {
  if (scrollStyleInjected) return;
  scrollStyleInjected = true;
  try {
    const style = document.createElement('style');
    style.textContent = `
      .ar-message-scroll::-webkit-scrollbar { width: 6px; }
      .ar-message-scroll::-webkit-scrollbar-track { background: transparent; }
      .ar-message-scroll::-webkit-scrollbar-thumb {
        background: rgba(128,128,128,0.25);
        border-radius: 3px;
      }
      .ar-message-scroll::-webkit-scrollbar-thumb:hover {
        background: rgba(128,128,128,0.45);
      }
      .ar-message-scroll {
        scrollbar-width: thin;
        scrollbar-color: rgba(128,128,128,0.25) transparent;
      }
    `;
    document.head.appendChild(style);
  } catch { /* Shadow DOM or SSR — ignore */ }
}

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface MessageListProps {
  tokens: DesignTokens;
  locale: Locale;
  messages: Message[];
  isAgentTyping: boolean;
  agentName: string;
  agentAvatarUrl: string | null;
  greetingMessage: string | null;
  /** Quick action prompt buttons for the greeting area (WI #228). */
  quickActions?: QuickActionButton[];
  /** Callback when a quick action button is clicked. */
  onQuickAction?: (promptTemplate: string) => void;
  /** Callback for per-message feedback (SPEC-1836). */
  onMessageFeedback?: (messageId: string, rating: 'positive' | 'negative') => void;
  /** Number of messages restored from previous session (SPEC-1868). */
  restoredMessageCount?: number;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function isSameDay(ts1: number, ts2: number): boolean {
  const d1 = new Date(ts1);
  const d2 = new Date(ts2);
  return (
    d1.getFullYear() === d2.getFullYear() &&
    d1.getMonth() === d2.getMonth() &&
    d1.getDate() === d2.getDate()
  );
}

function getDayLabel(timestamp: number, locale: Locale): string {
  const now = new Date();
  const date = new Date(timestamp);

  if (isSameDay(now.getTime(), timestamp)) return locale.today;

  const yesterday = new Date(now);
  yesterday.setDate(yesterday.getDate() - 1);
  if (isSameDay(yesterday.getTime(), timestamp)) return locale.yesterday;

  return date.toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
  });
}

/** Whether this message should show an avatar (first in a run of agent msgs). */
function shouldShowAvatar(messages: Message[], index: number): boolean {
  const msg = messages[index];
  if (msg.role !== 'agent') return false;
  if (index === 0) return true;
  const prev = messages[index - 1];
  // Show avatar if previous message is from a different role or different day
  return prev.role !== 'agent' || !isSameDay(prev.timestamp, msg.timestamp);
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export const MessageList: FunctionComponent<MessageListProps> = ({
  tokens,
  locale,
  messages,
  isAgentTyping,
  agentName,
  agentAvatarUrl,
  greetingMessage,
  quickActions,
  onQuickAction,
  onMessageFeedback,
  restoredMessageCount = 0,
}) => {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [isAtBottom, setIsAtBottom] = useState(true);
  const [showScrollBtn, setShowScrollBtn] = useState(false);

  // Inject subtle scrollbar CSS (WI #256)
  useEffect(() => { injectScrollbarStyles(); }, []);

  // Auto-scroll to bottom when new messages arrive (if already at bottom)
  useEffect(() => {
    if (isAtBottom && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isAgentTyping, isAtBottom]);

  // Track scroll position
  const handleScroll = useCallback(() => {
    if (!scrollRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = scrollRef.current;
    const atBottom = scrollHeight - scrollTop - clientHeight < 40;
    setIsAtBottom(atBottom);
    setShowScrollBtn(!atBottom);
  }, []);

  const scrollToBottom = useCallback(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: 'smooth',
      });
    }
  }, []);

  // Build message list with day separators
  const elements: JSX.Element[] = [];
  let lastDay = 0;

  for (let i = 0; i < messages.length; i++) {
    const msg = messages[i];

    // Day separator
    if (!isSameDay(msg.timestamp, lastDay)) {
      lastDay = msg.timestamp;
      elements.push(
        <div
          key={`day-${msg.timestamp}`}
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: `${tokens.space3} ${tokens.space4}`,
          }}
        >
          <div
            style={{
              fontSize: tokens.fontSizeXs,
              fontFamily: tokens.fontFamily,
              color: tokens.colorTextMuted,
              backgroundColor: tokens.colorSurface,
              padding: `${tokens.space1} ${tokens.space3}`,
              borderRadius: tokens.borderRadiusFull,
              fontWeight: tokens.fontWeightMedium,
            }}
          >
            {getDayLabel(msg.timestamp, locale)}
          </div>
        </div>,
      );
    }

    elements.push(
      <MessageBubble
        key={msg.id}
        tokens={tokens}
        message={msg}
        agentName={agentName}
        agentAvatarUrl={agentAvatarUrl}
        showAvatar={shouldShowAvatar(messages, i)}
        onFeedback={onMessageFeedback}
      />,
    );

    // SPEC-1868: Separator between restored and new messages
    if (restoredMessageCount > 0 && i === restoredMessageCount - 1 && i < messages.length - 1) {
      elements.push(
        <div
          key="restored-separator"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: tokens.space2,
            padding: `${tokens.space2} ${tokens.space4}`,
          }}
        >
          <div style={{ flex: 1, height: '1px', backgroundColor: tokens.colorBorder }} />
          <span
            style={{
              fontSize: tokens.fontSizeXs,
              fontFamily: tokens.fontFamily,
              color: tokens.colorTextMuted,
              whiteSpace: 'nowrap',
            }}
          >
            Previous conversation
          </span>
          <div style={{ flex: 1, height: '1px', backgroundColor: tokens.colorBorder }} />
        </div>,
      );
    }
  }

  return (
    <div
      style={{
        flex: 1,
        overflow: 'hidden',
        position: 'relative',
        backgroundColor: tokens.colorBackground,
      }}
    >
      <div
        ref={scrollRef}
        className="ar-message-scroll"
        onScroll={handleScroll}
        style={{
          height: '100%',
          overflowY: 'auto',
          overflowX: 'hidden',
          paddingTop: tokens.space3,
          paddingBottom: tokens.space2,
        }}
      >
        {/* Greeting message at top of conversation — left-aligned bubble */}
        {(greetingMessage || (quickActions && quickActions.length > 0)) && messages.length === 0 && (
          <>
            {/* "Today" date separator */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                padding: `${tokens.space3} ${tokens.space4}`,
              }}
            >
              <div
                style={{
                  fontSize: tokens.fontSizeXs,
                  fontFamily: tokens.fontFamily,
                  color: tokens.colorTextMuted,
                  backgroundColor: tokens.colorSurface,
                  padding: `${tokens.space1} ${tokens.space3}`,
                  borderRadius: tokens.borderRadiusFull,
                  fontWeight: tokens.fontWeightMedium,
                }}
              >
                {locale.today}
              </div>
            </div>

            {/* Greeting bubble — agent avatar + message */}
            {greetingMessage && <div
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                padding: `${tokens.space1} ${tokens.space4}`,
                gap: tokens.space2,
              }}
            >
              {/* Agent avatar (28px) */}
              <div
                style={{
                  width: tokens.avatarSizeSm,
                  height: tokens.avatarSizeSm,
                  borderRadius: tokens.borderRadiusFull,
                  backgroundColor: tokens.colorPrimary,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: tokens.colorPrimaryText,
                  overflow: 'hidden',
                  fontSize: tokens.fontSizeXs,
                  fontWeight: tokens.fontWeightSemibold,
                  fontFamily: tokens.fontFamily,
                  flexShrink: 0,
                }}
              >
                {agentAvatarUrl ? (
                  <img
                    src={agentAvatarUrl}
                    alt={agentName}
                    style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                  />
                ) : (
                  agentName.slice(0, 2).toUpperCase() || 'AR'
                )}
              </div>

              {/* Bubble */}
              <div
                style={{
                  maxWidth: '78%',
                }}
              >
                <div
                  style={{
                    backgroundColor: tokens.colorAgentBubble,
                    border: `1px solid ${tokens.colorAgentBubbleBorder}`,
                    borderRadius: '4px 16px 16px 16px',
                    padding: '10px 14px',
                    color: tokens.colorAgentBubbleText,
                    fontSize: tokens.fontSizeSm,
                    fontFamily: tokens.fontFamily,
                    lineHeight: tokens.lineHeightNormal,
                  }}
                >
                  {greetingMessage}
                </div>
              </div>
            </div>}

            {/* Quick action prompt buttons (WI #228) */}
            {quickActions && quickActions.length > 0 && onQuickAction && (
              <QuickActions
                tokens={tokens}
                actions={quickActions}
                onAction={onQuickAction}
                disabled={false}
              />
            )}
          </>
        )}

        {/* Messages */}
        {elements}

        {/* Typing indicator */}
        {isAgentTyping && (
          <TypingIndicator
            tokens={tokens}
            agentName={agentName}
            agentAvatarUrl={agentAvatarUrl}
            locale={locale.typingIndicator}
          />
        )}
      </div>

      {/* Scroll-to-bottom button */}
      {showScrollBtn && (
        <button
          type="button"
          aria-label={locale.scrollToBottom}
          onClick={scrollToBottom}
          style={{
            position: 'absolute',
            bottom: tokens.space3,
            left: '50%',
            transform: 'translateX(-50%)',
            backgroundColor: tokens.colorSurface,
            color: tokens.colorText,
            border: `${tokens.borderWidth} solid ${tokens.colorBorder}`,
            borderRadius: tokens.borderRadiusFull,
            padding: `${tokens.space1} ${tokens.space3}`,
            fontSize: tokens.fontSizeXs,
            fontFamily: tokens.fontFamily,
            fontWeight: tokens.fontWeightMedium,
            cursor: 'pointer',
            boxShadow: tokens.shadowMd,
            display: 'flex',
            alignItems: 'center',
            gap: tokens.space1,
            outline: 'none',
          }}
        >
          <ChevronDownIcon size={12} />
          {locale.scrollToBottom}
        </button>
      )}
    </div>
  );
};

// ---------------------------------------------------------------------------
// Icons (inline SVG)
// ---------------------------------------------------------------------------

function ChevronDownIcon({ size }: { size: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="2.5"
      stroke-linecap="round"
      stroke-linejoin="round"
    >
      <polyline points="6 9 12 15 18 9" />
    </svg>
  );
}
