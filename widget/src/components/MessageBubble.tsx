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

import { h, FunctionComponent } from 'preact';
import type { DesignTokens } from '@/theme/tokens';
import type { Message } from '@/state/store';

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface MessageBubbleProps {
  tokens: DesignTokens;
  message: Message;
  agentAvatarUrl: string | null;
  agentName: string;
  showAvatar: boolean;  // false when consecutive agent messages
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
  message,
  agentAvatarUrl,
  agentName,
  showAvatar,
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

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: isCustomer ? 'row-reverse' : 'row',
        alignItems: 'flex-end',
        padding: `${tokens.space1} ${tokens.space4}`,
        gap: tokens.space2,
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
                agentName.charAt(0).toUpperCase()
              )}
            </div>
          )}
        </div>
      )}

      {/* Bubble */}
      <div
        style={{
          maxWidth: '75%',
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
            padding: `${tokens.space2} ${tokens.space3}`,
            borderRadius: tokens.borderRadiusLg,
            // Tail: flat corner on the sender's side
            borderBottomRightRadius: isCustomer ? tokens.borderRadiusSm : tokens.borderRadiusLg,
            borderBottomLeftRadius: isCustomer ? tokens.borderRadiusLg : tokens.borderRadiusSm,
            fontSize: tokens.fontSizeMd,
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
              <span>Message revised</span>
            </div>
          )}

          {/* Message content */}
          <span>{message.content}</span>

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

        {/* Timestamp */}
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
        agentName.charAt(0).toUpperCase()
      )}
    </div>

    {/* Typing bubble */}
    <div
      style={{
        backgroundColor: tokens.colorAgentBubble,
        padding: `${tokens.space2} ${tokens.space3}`,
        borderRadius: tokens.borderRadiusLg,
        borderBottomLeftRadius: tokens.borderRadiusSm,
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
