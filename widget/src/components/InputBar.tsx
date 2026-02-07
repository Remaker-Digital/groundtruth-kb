/**
 * InputBar — message input area at the bottom of the conversation panel.
 *
 * Handles:
 *   - Text input (auto-growing textarea)
 *   - Send button (enabled only when message is non-empty)
 *   - Enter to send, Shift+Enter for newline
 *   - File attachment button (when enabled)
 *   - Character count (for excessively long messages)
 *   - Loading state (while sending)
 *   - Powered-by branding (when show_branding is true)
 *
 * Visual reference: Zapier (clean input, subtle borders, consistent sizing).
 * Functional reference: Tidio (auto-grow, enter-to-send, attachment).
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { FunctionComponent } from 'preact';
import { useState, useRef, useCallback } from 'preact/hooks';
import type { DesignTokens } from '@/theme/tokens';
import type { Locale } from '@/locale/en';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const MAX_MESSAGE_LENGTH = 2000;
const MIN_TEXTAREA_HEIGHT = 44;
const MAX_TEXTAREA_HEIGHT = 120;

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface InputBarProps {
  tokens: DesignTokens;
  locale: Locale;
  onSend: (content: string) => void;
  isLoading: boolean;
  disabled: boolean;
  fileUploadEnabled: boolean;
  showBranding: boolean;
  inputPlaceholder: string | null;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export const InputBar: FunctionComponent<InputBarProps> = ({
  tokens,
  locale,
  onSend,
  isLoading,
  disabled,
  fileUploadEnabled,
  showBranding,
  inputPlaceholder,
}) => {
  const [text, setText] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const placeholder = inputPlaceholder || locale.inputPlaceholder;
  const canSend = text.trim().length > 0 && !isLoading && !disabled;

  const handleSend = useCallback(() => {
    const trimmed = text.trim();
    if (!trimmed || isLoading || disabled) return;
    onSend(trimmed);
    setText('');
    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = `${MIN_TEXTAREA_HEIGHT}px`;
    }
  }, [text, isLoading, disabled, onSend]);

  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSend();
      }
    },
    [handleSend],
  );

  const handleInput = useCallback((e: Event) => {
    const target = e.target as HTMLTextAreaElement;
    let value = target.value;

    // Enforce max length
    if (value.length > MAX_MESSAGE_LENGTH) {
      value = value.substring(0, MAX_MESSAGE_LENGTH);
    }
    setText(value);

    // Auto-grow textarea
    target.style.height = `${MIN_TEXTAREA_HEIGHT}px`;
    const scrollHeight = target.scrollHeight;
    target.style.height = `${Math.min(scrollHeight, MAX_TEXTAREA_HEIGHT)}px`;
  }, []);

  return (
    <div
      style={{
        borderTop: `${tokens.borderWidth} solid ${tokens.colorBorder}`,
        backgroundColor: tokens.colorBackground,
        flexShrink: 0,
      }}
    >
      {/* Input row */}
      <div
        style={{
          display: 'flex',
          alignItems: 'flex-end',
          padding: `${tokens.space2} ${tokens.space3}`,
          gap: tokens.space2,
        }}
      >
        {/* File upload button */}
        {fileUploadEnabled && (
          <button
            type="button"
            aria-label={locale.attachFile}
            disabled={disabled}
            style={{
              background: 'none',
              border: 'none',
              color: disabled ? tokens.colorTextMuted : tokens.colorTextSecondary,
              cursor: disabled ? 'default' : 'pointer',
              padding: tokens.space1,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              borderRadius: tokens.borderRadiusSm,
              transition: `color ${tokens.transitionFast}`,
              outline: 'none',
              flexShrink: 0,
            }}
            onMouseEnter={(e) => {
              if (!disabled) (e.currentTarget as HTMLElement).style.color = tokens.colorText;
            }}
            onMouseLeave={(e) => {
              if (!disabled) (e.currentTarget as HTMLElement).style.color = tokens.colorTextSecondary;
            }}
          >
            <PaperclipIcon size={18} />
          </button>
        )}

        {/* Textarea */}
        <textarea
          ref={textareaRef}
          value={text}
          onInput={handleInput}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          rows={2}
          aria-label={placeholder}
          style={{
            flex: 1,
            resize: 'none',
            border: 'none',
            outline: 'none',
            backgroundColor: 'transparent',
            color: tokens.colorText,
            fontSize: tokens.fontSizeMd,
            fontFamily: tokens.fontFamily,
            lineHeight: tokens.lineHeightNormal,
            padding: `${tokens.space1} 0`,
            height: `${MIN_TEXTAREA_HEIGHT}px`,
            maxHeight: `${MAX_TEXTAREA_HEIGHT}px`,
            overflow: 'auto',
            // Remove default textarea styling
            appearance: 'none' as unknown as string,
            WebkitAppearance: 'none',
          }}
        />

        {/* Send button */}
        <button
          type="button"
          aria-label={locale.sendButton}
          onClick={handleSend}
          disabled={!canSend}
          style={{
            width: '32px',
            height: '32px',
            borderRadius: tokens.borderRadiusFull,
            backgroundColor: canSend ? tokens.colorPrimary : tokens.colorSurface,
            color: canSend ? tokens.colorPrimaryText : tokens.colorTextMuted,
            border: 'none',
            cursor: canSend ? 'pointer' : 'default',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
            transition: `background-color ${tokens.transitionFast}, color ${tokens.transitionFast}`,
            outline: 'none',
            padding: 0,
          }}
        >
          {isLoading ? <SpinnerIcon size={16} /> : <SendIcon size={16} />}
        </button>
      </div>

      {/* Character count warning */}
      {text.length > MAX_MESSAGE_LENGTH * 0.9 && (
        <div
          style={{
            fontSize: tokens.fontSizeXs,
            fontFamily: tokens.fontFamily,
            color: text.length >= MAX_MESSAGE_LENGTH ? tokens.colorError : tokens.colorTextMuted,
            textAlign: 'right',
            padding: `0 ${tokens.space3} ${tokens.space1}`,
          }}
        >
          {text.length}/{MAX_MESSAGE_LENGTH}
        </div>
      )}

      {/* Powered by branding */}
      {showBranding && (
        <div
          style={{
            textAlign: 'center',
            padding: `${tokens.space1} 0 ${tokens.space2}`,
            fontSize: tokens.fontSizeXs,
            fontFamily: tokens.fontFamily,
            color: tokens.colorTextMuted,
          }}
        >
          <a
            href="https://remakerdigital.com"
            target="_blank"
            rel="noopener noreferrer"
            style={{
              color: 'inherit',
              textDecoration: 'none',
              transition: `color ${tokens.transitionFast}`,
            }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLElement).style.color = tokens.colorTextSecondary;
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLElement).style.color = tokens.colorTextMuted;
            }}
          >
            {locale.poweredBy}
          </a>
        </div>
      )}
    </div>
  );
};

// ---------------------------------------------------------------------------
// Icons (inline SVG)
// ---------------------------------------------------------------------------

function SendIcon({ size }: { size: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="currentColor"
    >
      <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
    </svg>
  );
}

function PaperclipIcon({ size }: { size: number }) {
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
      <path d="m21.44 11.05-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48" />
    </svg>
  );
}

function SpinnerIcon({ size }: { size: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="2.5"
      stroke-linecap="round"
      style={{
        animation: 'ar-spin 0.8s linear infinite',
      }}
    >
      <path d="M12 2a10 10 0 0 1 10 10" />
    </svg>
  );
}
