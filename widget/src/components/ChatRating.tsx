/**
 * ChatRating — post-conversation feedback prompt.
 *
 * Shown after a conversation ends (when chat_rating_enabled is true).
 * Collects:
 *   - Thumbs up / thumbs down rating
 *   - Optional comment
 *
 * After submission, shows thank-you message and option to start
 * a new conversation.
 *
 * Visual reference: Zapier (buttons, spacing, form layout).
 * Functional reference: Tidio (post-chat rating flow).
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

interface ChatRatingProps {
  tokens: DesignTokens;
  locale: Locale;
  onSubmit: (rating: 'positive' | 'negative', comment?: string) => void;
  onNewConversation: () => void;
  isLoading: boolean;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export const ChatRating: FunctionComponent<ChatRatingProps> = ({
  tokens,
  locale,
  onSubmit,
  onNewConversation,
  isLoading,
}) => {
  const [selectedRating, setSelectedRating] = useState<'positive' | 'negative' | null>(null);
  const [comment, setComment] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleRate = useCallback((rating: 'positive' | 'negative') => {
    setSelectedRating(rating);
  }, []);

  const handleSubmit = useCallback(() => {
    if (!selectedRating) return;
    onSubmit(selectedRating, comment.trim() || undefined);
    setSubmitted(true);
  }, [selectedRating, comment, onSubmit]);

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
        {/* Checkmark */}
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
          <CheckIcon size={24} color="#FFFFFF" />
        </div>
        <div
          style={{
            fontSize: tokens.fontSizeLg,
            fontWeight: tokens.fontWeightSemibold,
            fontFamily: tokens.fontFamily,
            color: tokens.colorText,
            marginBottom: tokens.space2,
          }}
        >
          {locale.ratingThankYou}
        </div>
        <button
          type="button"
          onClick={onNewConversation}
          style={{
            marginTop: tokens.space4,
            padding: `${tokens.space2} ${tokens.space5}`,
            backgroundColor: 'transparent',
            color: tokens.colorPrimary,
            border: `${tokens.borderWidth} solid ${tokens.colorPrimary}`,
            borderRadius: tokens.borderRadius,
            fontSize: tokens.fontSizeSm,
            fontWeight: tokens.fontWeightMedium,
            fontFamily: tokens.fontFamily,
            cursor: 'pointer',
            outline: 'none',
            transition: `background-color ${tokens.transitionFast}`,
          }}
        >
          {locale.newConversation}
        </button>
      </div>
    );
  }

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
      {/* Prompt */}
      <div
        style={{
          fontSize: tokens.fontSizeLg,
          fontWeight: tokens.fontWeightSemibold,
          fontFamily: tokens.fontFamily,
          color: tokens.colorText,
          marginBottom: tokens.space5,
        }}
      >
        {locale.ratingPrompt}
      </div>

      {/* Rating buttons */}
      <div
        style={{
          display: 'flex',
          gap: tokens.space4,
          marginBottom: tokens.space5,
        }}
      >
        <RatingButton
          tokens={tokens}
          type="positive"
          selected={selectedRating === 'positive'}
          onClick={() => handleRate('positive')}
        />
        <RatingButton
          tokens={tokens}
          type="negative"
          selected={selectedRating === 'negative'}
          onClick={() => handleRate('negative')}
        />
      </div>

      {/* Comment (visible after selecting a rating) */}
      {selectedRating && (
        <div
          style={{
            width: '100%',
            maxWidth: '280px',
            animation: 'ar-fade-in 0.2s ease',
          }}
        >
          <textarea
            value={comment}
            onInput={(e) => setComment((e.target as HTMLTextAreaElement).value)}
            placeholder={locale.ratingCommentPlaceholder}
            rows={3}
            style={{
              width: '100%',
              padding: `${tokens.space2} ${tokens.space3}`,
              fontSize: tokens.fontSizeSm,
              fontFamily: tokens.fontFamily,
              color: tokens.colorText,
              backgroundColor: tokens.colorBackground,
              border: `${tokens.borderWidth} solid ${tokens.colorBorder}`,
              borderRadius: tokens.borderRadius,
              outline: 'none',
              resize: 'vertical',
              minHeight: '60px',
              lineHeight: `${tokens.lineHeightNormal}`,
            }}
          />
          <button
            type="button"
            onClick={handleSubmit}
            disabled={isLoading}
            style={{
              width: '100%',
              marginTop: tokens.space3,
              padding: `${tokens.space2} ${tokens.space4}`,
              backgroundColor: tokens.colorPrimary,
              color: tokens.colorPrimaryText,
              border: 'none',
              borderRadius: tokens.borderRadius,
              fontSize: tokens.fontSizeSm,
              fontWeight: tokens.fontWeightSemibold,
              fontFamily: tokens.fontFamily,
              cursor: isLoading ? 'default' : 'pointer',
              opacity: isLoading ? 0.7 : 1,
              transition: `opacity ${tokens.transitionFast}`,
              outline: 'none',
            }}
          >
            {locale.sendButton}
          </button>
        </div>
      )}
    </div>
  );
};

// ---------------------------------------------------------------------------
// Rating button
// ---------------------------------------------------------------------------

const RatingButton: FunctionComponent<{
  tokens: DesignTokens;
  type: 'positive' | 'negative';
  selected: boolean;
  onClick: () => void;
}> = ({ tokens, type, selected, onClick }) => {
  const isPositive = type === 'positive';

  return (
    <button
      type="button"
      onClick={onClick}
      aria-label={isPositive ? 'Helpful' : 'Not helpful'}
      style={{
        width: '56px',
        height: '56px',
        borderRadius: tokens.borderRadiusFull,
        backgroundColor: selected
          ? (isPositive ? tokens.colorSuccess : tokens.colorError)
          : tokens.colorSurface,
        color: selected ? '#FFFFFF' : tokens.colorTextSecondary,
        border: `2px solid ${selected
          ? (isPositive ? tokens.colorSuccess : tokens.colorError)
          : tokens.colorBorder}`,
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        transition: `all ${tokens.transitionFast}`,
        outline: 'none',
        padding: 0,
      }}
    >
      {isPositive ? <ThumbUpIcon size={24} /> : <ThumbDownIcon size={24} />}
    </button>
  );
};

// ---------------------------------------------------------------------------
// Icons (inline SVG)
// ---------------------------------------------------------------------------

function ThumbUpIcon({ size }: { size: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="currentColor"
    >
      <path d="M1 21h4V9H1v12zm22-11c0-1.1-.9-2-2-2h-6.31l.95-4.57.03-.32c0-.41-.17-.79-.44-1.06L14.17 1 7.59 7.59C7.22 7.95 7 8.45 7 9v10c0 1.1.9 2 2 2h9c.83 0 1.54-.5 1.84-1.22l3.02-7.05c.09-.23.14-.47.14-.73v-2z" />
    </svg>
  );
}

function ThumbDownIcon({ size }: { size: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="currentColor"
    >
      <path d="M15 3H6c-.83 0-1.54.5-1.84 1.22l-3.02 7.05c-.09.23-.14.47-.14.73v2c0 1.1.9 2 2 2h6.31l-.95 4.57-.03.32c0 .41.17.79.44 1.06L9.83 23l6.59-6.59c.36-.36.58-.86.58-1.41V5c0-1.1-.9-2-2-2zm4 0v12h4V3h-4z" />
    </svg>
  );
}

function CheckIcon({ size, color }: { size: number; color: string }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke={color}
      stroke-width="3"
      stroke-linecap="round"
      stroke-linejoin="round"
    >
      <polyline points="20 6 9 17 4 12" />
    </svg>
  );
}
