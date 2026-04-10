// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * MessageBubble — renders a single message in the conversation.
 *
 * Handles:
 *   - Customer messages (right-aligned, primary color)
 *   - Agent messages (left-aligned, surface color, optional avatar)
 *   - System messages (centered, muted)
 *   - Streaming state (cursor animation)
 *   - Retracted messages (fallback text with icon)
 *   - Timestamps
 *
 * Visual reference: Zapier (clean borders, consistent padding, readable type).
 * Functional reference: Tidio (bubble layout, avatar, streaming cursor).
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { FunctionComponent, VNode } from 'preact';
import type { DesignTokens } from '@/theme/tokens';
import type { Message } from '@/state/store';
import type { Locale } from '@/locale/en';
import { AnswerBlocks } from './AnswerBlocks';

// ---------------------------------------------------------------------------
// Markdown link parser — converts [text](url) to clickable <a> elements
// ---------------------------------------------------------------------------

const MARKDOWN_LINK_RE = /\[([^\]]+)\]\((https?:\/\/[^)]+)\)/g;

function renderWithLinks(
  text: string,
  tokens: DesignTokens,
  linkColor: string,
): (string | VNode)[] {
  const parts: (string | VNode)[] = [];
  let lastIndex = 0;
  let match: RegExpExecArray | null;

  // Reset regex state for each call
  MARKDOWN_LINK_RE.lastIndex = 0;

  while ((match = MARKDOWN_LINK_RE.exec(text)) !== null) {
    // Text before the link
    if (match.index > lastIndex) {
      parts.push(text.slice(lastIndex, match.index));
    }
    // The clickable link — target="_top" opens in the parent frame (not the widget iframe)
    parts.push(
      <a
        href={match[2]}
        target="_top"
        rel="noopener noreferrer"
        style={{
          color: linkColor,
          textDecoration: 'underline',
          textUnderlineOffset: '2px',
          fontWeight: tokens.fontWeightMedium,
          cursor: 'pointer',
        }}
      >
        {match[1]}
      </a>
    );
    lastIndex = match.index + match[0].length;
  }

  // Remaining text after last link
  if (lastIndex < text.length) {
    parts.push(text.slice(lastIndex));
  }

  return parts.length > 0 ? parts : [text];
}

/** Extract unique source domains from markdown links in message text. */
function extractSourceDomains(text: string): string[] {
  MARKDOWN_LINK_RE.lastIndex = 0;
  const domains = new Set<string>();
  let match: RegExpExecArray | null;
  while ((match = MARKDOWN_LINK_RE.exec(text)) !== null) {
    try {
      const url = new URL(match[2]);
      // Strip "www." prefix for cleaner display
      domains.add(url.hostname.replace(/^www\./, ''));
    } catch { /* invalid URL — skip */ }
  }
  return Array.from(domains);
}

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface MessageBubbleProps {
  tokens: DesignTokens;
  locale: Locale;
  message: Message;
  agentAvatarUrl: string | null;
  agentName: string;
  showAvatar: boolean;  // false when consecutive agent messages
  /** Callback to submit per-message feedback (SPEC-1836). */
  onFeedback?: (messageId: string, rating: 'positive' | 'negative') => void;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatTime(timestamp: number): string {
  const date = new Date(timestamp);
  const hours = date.getHours();
  const minutes = date.getMinutes().toString().padStart(2, '0');
  const ampm = hours >= 12 ? 'PM' : 'AM';
  const displayHours = hours % 12 || 12;
  return `${displayHours}:${minutes} ${ampm}`;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export const MessageBubble: FunctionComponent<MessageBubbleProps> = ({
  tokens,
  locale,
  message,
  agentAvatarUrl,
  agentName,
  showAvatar,
  onFeedback,
}) => {
  // System messages are centered and styled differently
  if (message.role === 'system') {
    return (
      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          padding: `${tokens.space2} ${tokens.space4}`,
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
            lineHeight: tokens.lineHeightNormal,
          }}
        >
          {message.content}
        </div>
      </div>
    );
  }

  const isCustomer = message.role === 'customer';

  // Entrance animation — messages slide up and fade in.
  // Only animate recent messages (within the last 2 seconds) to avoid
  // replaying animations on scroll or when loading history.
  const isRecent = Date.now() - message.timestamp < 2000;

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: isCustomer ? 'row-reverse' : 'row',
        alignItems: 'flex-end',
        padding: `${tokens.space1} ${tokens.space4}`,
        gap: tokens.space2,
        ...(isRecent ? {
          animation: 'ar-fade-in 0.25s ease-out both',
        } : {}),
      }}
    >
      {/* Agent avatar column */}
      {!isCustomer && (
        <div
          style={{
            width: tokens.avatarSizeSm,
            height: tokens.avatarSizeSm,
            flexShrink: 0,
            visibility: showAvatar ? 'visible' : 'hidden',
          }}
        >
          {showAvatar && (
            <div
              style={{
                width: tokens.avatarSizeSm,
                height: tokens.avatarSizeSm,
                borderRadius: tokens.borderRadiusFull,
                backgroundColor: tokens.colorPrimary,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                overflow: 'hidden',
                color: tokens.colorPrimaryText,
                fontSize: tokens.fontSizeXs,
                fontWeight: tokens.fontWeightSemibold,
                fontFamily: tokens.fontFamily,
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
                agentName.slice(0, 2).toUpperCase()
              )}
            </div>
          )}
        </div>
      )}

      {/* Bubble */}
      <div
        style={{
          maxWidth: '78%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: isCustomer ? 'flex-end' : 'flex-start',
        }}
      >
        <div
          style={{
            backgroundColor: isCustomer
              ? tokens.colorCustomerBubble
              : tokens.colorAgentBubble,
            color: isCustomer
              ? tokens.colorCustomerBubbleText
              : tokens.colorAgentBubbleText,
            border: isCustomer ? 'none' : `1px solid ${tokens.colorAgentBubbleBorder}`,
            padding: '10px 14px',
            borderRadius: isCustomer ? '16px 16px 4px 16px' : '4px 16px 16px 16px',
            fontSize: tokens.fontSizeSm,
            fontFamily: tokens.fontFamily,
            lineHeight: tokens.lineHeightNormal,
            wordBreak: 'break-word',
            position: 'relative',
            ...(message.retracted ? {
              opacity: 0.7,
              borderLeft: `3px solid ${tokens.colorError}`,
              borderBottomLeftRadius: tokens.borderRadiusSm,
            } : {}),
          }}
        >
          {/* Retraction icon */}
          {message.retracted && (
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: tokens.space1,
                marginBottom: tokens.space1,
                fontSize: tokens.fontSizeXs,
                color: isCustomer ? tokens.colorCustomerBubbleText : tokens.colorError,
                opacity: 0.8,
              }}
            >
              <RetractedIcon size={12} />
              <span>{locale.messageRevised}</span>
            </div>
          )}

          {/* Message content — renders markdown [text](url) as clickable links */}
          <span>
            {renderWithLinks(
              message.content,
              tokens,
              isCustomer ? tokens.colorCustomerBubbleText : tokens.colorPrimary,
            )}
          </span>

          {/* Streaming cursor */}
          {message.streaming && (
            <span
              style={{
                display: 'inline-block',
                width: '2px',
                height: '14px',
                backgroundColor: isCustomer
                  ? tokens.colorCustomerBubbleText
                  : tokens.colorAgentBubbleText,
                marginLeft: '2px',
                verticalAlign: 'text-bottom',
                animation: 'ar-blink 0.7s step-end infinite',
              }}
            />
          )}
        </div>

        {/* Timestamp + source attribution */}
        <div
          style={{
            fontSize: tokens.fontSizeXs,
            fontFamily: tokens.fontFamily,
            color: tokens.colorTextMuted,
            marginTop: '2px',
            padding: `0 ${tokens.space1}`,
            lineHeight: 1,
          }}
        >
          {formatTime(message.timestamp)}
        </div>

        {/* Source attribution (B1) — structured sources from validated event,
            fallback to domain extraction from markdown links */}
        {!isCustomer && !message.streaming && (() => {
          // Prefer structured sources from validated event (B1)
          if (message.sources && message.sources.length > 0) {
            return (
              <div
                style={{
                  display: 'flex',
                  flexWrap: 'wrap',
                  alignItems: 'center',
                  gap: tokens.space1,
                  marginTop: '2px',
                  padding: `0 ${tokens.space1}`,
                  fontSize: tokens.fontSizeXs,
                  fontFamily: tokens.fontFamily,
                  color: tokens.colorTextMuted,
                  lineHeight: 1.3,
                }}
              >
                <SourceIcon size={10} />
                {message.sources.map((src, i) => (
                  <span key={i}>
                    {src.url ? (
                      <a
                        href={src.url}
                        target="_top"
                        rel="noopener noreferrer"
                        style={{
                          color: tokens.colorTextMuted,
                          textDecoration: 'underline',
                          textUnderlineOffset: '2px',
                        }}
                      >
                        {src.title}
                      </a>
                    ) : (
                      src.title
                    )}
                    {i < message.sources!.length - 1 ? ', ' : ''}
                  </span>
                ))}
              </div>
            );
          }
          // Fallback: extract source domains from markdown links in text
          const domains = extractSourceDomains(message.content);
          if (domains.length === 0) return null;
          return (
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: tokens.space1,
                marginTop: '2px',
                padding: `0 ${tokens.space1}`,
                fontSize: tokens.fontSizeXs,
                fontFamily: tokens.fontFamily,
                color: tokens.colorTextMuted,
                lineHeight: 1,
              }}
            >
              <SourceIcon size={10} />
              <span>
                {domains.length === 1
                  ? domains[0]
                  : `${domains[0]} +${domains.length - 1}`
                }
              </span>
            </div>
          );
        })()}

        {/* Structured answer blocks (SPEC-1867) */}
        {!isCustomer && !message.streaming && message.blocks && message.blocks.length > 0 && (
          <AnswerBlocks blocks={message.blocks} tokens={tokens} />
        )}

        {/* Per-message feedback (SPEC-1836) — thumbs up/down on AI messages */}
        {!isCustomer && !message.streaming && message.id && onFeedback && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: tokens.space1,
              marginTop: '4px',
              padding: `0 ${tokens.space1}`,
            }}
          >
            <button
              type="button"
              onClick={() => onFeedback(message.id, 'positive')}
              aria-label={locale.feedbackHelpful}
              style={{
                background: 'none',
                border: 'none',
                cursor: message.feedbackRating ? 'default' : 'pointer',
                padding: '2px',
                borderRadius: tokens.borderRadiusSm,
                color: message.feedbackRating === 'positive'
                  ? tokens.colorPrimary
                  : tokens.colorTextMuted,
                opacity: message.feedbackRating === 'negative' ? 0.3 : 1,
                transition: 'color 0.15s ease, opacity 0.15s ease',
                display: 'flex',
                alignItems: 'center',
              }}
              disabled={!!message.feedbackRating}
            >
              <ThumbUpIcon size={14} filled={message.feedbackRating === 'positive'} />
            </button>
            <button
              type="button"
              onClick={() => onFeedback(message.id, 'negative')}
              aria-label={locale.feedbackNotHelpful}
              style={{
                background: 'none',
                border: 'none',
                cursor: message.feedbackRating ? 'default' : 'pointer',
                padding: '2px',
                borderRadius: tokens.borderRadiusSm,
                color: message.feedbackRating === 'negative'
                  ? tokens.colorError
                  : tokens.colorTextMuted,
                opacity: message.feedbackRating === 'positive' ? 0.3 : 1,
                transition: 'color 0.15s ease, opacity 0.15s ease',
                display: 'flex',
                alignItems: 'center',
              }}
              disabled={!!message.feedbackRating}
            >
              <ThumbDownIcon size={14} filled={message.feedbackRating === 'negative'} />
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

// ---------------------------------------------------------------------------
// Typing indicator (separate export for MessageList)
// ---------------------------------------------------------------------------

export const TypingIndicator: FunctionComponent<{
  tokens: DesignTokens;
  agentName: string;
  agentAvatarUrl: string | null;
  locale: string;
}> = ({ tokens, agentName, agentAvatarUrl, locale }) => (
  <div
    style={{
      display: 'flex',
      alignItems: 'flex-end',
      padding: `${tokens.space1} ${tokens.space4}`,
      gap: tokens.space2,
    }}
  >
    {/* Avatar */}
    <div
      style={{
        width: tokens.avatarSizeSm,
        height: tokens.avatarSizeSm,
        borderRadius: tokens.borderRadiusFull,
        backgroundColor: tokens.colorPrimary,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        overflow: 'hidden',
        color: tokens.colorPrimaryText,
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
        agentName.slice(0, 2).toUpperCase()
      )}
    </div>

    {/* Typing bubble — shimmer background indicates thinking */}
    <div
      style={{
        backgroundColor: tokens.colorAgentBubble,
        border: `1px solid ${tokens.colorAgentBubbleBorder}`,
        backgroundImage: `linear-gradient(90deg, ${tokens.colorAgentBubble} 25%, ${tokens.colorSurfaceHover} 50%, ${tokens.colorAgentBubble} 75%)`,
        backgroundSize: '200% 100%',
        animation: 'ar-shimmer 2s ease-in-out infinite, ar-fade-in 0.25s ease-out both',
        padding: '10px 14px',
        borderRadius: '4px 16px 16px 16px',
        display: 'flex',
        alignItems: 'center',
        gap: tokens.space1,
      }}
    >
      {/* Three animated dots */}
      {[0, 1, 2].map((i) => (
        <span
          key={i}
          style={{
            width: '6px',
            height: '6px',
            borderRadius: tokens.borderRadiusFull,
            backgroundColor: tokens.colorTextMuted,
            display: 'inline-block',
            animation: `ar-typing-dot 1.2s ease-in-out ${i * 0.15}s infinite`,
          }}
        />
      ))}
      <span
        style={{
          fontSize: tokens.fontSizeXs,
          fontFamily: tokens.fontFamily,
          color: tokens.colorTextMuted,
          marginLeft: tokens.space1,
        }}
      >
        {agentName} {locale}
      </span>
    </div>
  </div>
);

// ---------------------------------------------------------------------------
// Icons (inline SVG)
// ---------------------------------------------------------------------------

/** Small link/globe icon for source citations. */
function SourceIcon({ size }: { size: number }) {
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
      <line x1="2" y1="12" x2="22" y2="12" />
      <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
    </svg>
  );
}

function RetractedIcon({ size }: { size: number }) {
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
      <line x1="12" y1="8" x2="12" y2="12" />
      <line x1="12" y1="16" x2="12.01" y2="16" />
    </svg>
  );
}

/** Thumbs up icon for per-message feedback (SPEC-1836). */
function ThumbUpIcon({ size, filled }: { size: number; filled?: boolean }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill={filled ? 'currentColor' : 'none'}
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    >
      <path d="M7 10v12" />
      <path d="M15 5.88 14 10h5.83a2 2 0 0 1 1.92 2.56l-2.33 8A2 2 0 0 1 17.5 22H4a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h2.76a2 2 0 0 0 1.79-1.11L12 2a3.13 3.13 0 0 1 3 3.88Z" />
    </svg>
  );
}

/** Thumbs down icon for per-message feedback (SPEC-1836). */
function ThumbDownIcon({ size, filled }: { size: number; filled?: boolean }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill={filled ? 'currentColor' : 'none'}
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    >
      <path d="M17 14V2" />
      <path d="M9 18.12 10 14H4.17a2 2 0 0 1-1.92-2.56l2.33-8A2 2 0 0 1 6.5 2H20a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-2.76a2 2 0 0 0-1.79 1.11L12 22a3.13 3.13 0 0 1-3-3.88Z" />
    </svg>
  );
}
