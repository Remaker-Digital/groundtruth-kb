/**
 * QuickActions — contextual prompt button pills in the greeting area (WI #228).
 *
 * Renders 1-2 pill-shaped buttons below the greeting message. Each button
 * sends a hidden, enriched prompt to the AI when clicked. The buttons
 * disappear once the conversation starts (messages.length > 0).
 *
 * Design:
 *   ┌─────────────────────────────┐
 *   │   [🏷️ What's on sale?]     │
 *   │   [❓ Help with my order]   │
 *   └─────────────────────────────┘
 *
 * Buttons use `colorSurface` background with `colorText`, hover to
 * `colorSurfaceHover`. Subtle fade-in animation via CSS class `ar-fade-in`.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { FunctionComponent } from 'preact';
import { useState } from 'preact/hooks';
import type { DesignTokens } from '@/theme/tokens';
import type { QuickActionButton } from '@/theme/tokens';

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface QuickActionsProps {
  tokens: DesignTokens;
  actions: QuickActionButton[];
  onAction: (promptTemplate: string) => void;
  disabled: boolean;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export const QuickActions: FunctionComponent<QuickActionsProps> = ({
  tokens,
  actions,
  onAction,
  disabled,
}) => {
  const [hoveredId, setHoveredId] = useState<string | null>(null);

  if (!actions || actions.length === 0) return null;

  // Show max 2 buttons (enforced server-side, but safeguard here)
  const visibleActions = actions.slice(0, 2);

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'row',
        flexWrap: 'wrap',
        justifyContent: 'center',
        gap: tokens.space2,
        marginTop: tokens.space4,
        padding: `0 ${tokens.space4}`,
        /* P3-6: Animation moved to individual buttons for staggered entrance */
      }}
    >
      {visibleActions.map((action, index) => (
        <button
          key={action.id}
          type="button"
          disabled={disabled}
          onClick={() => onAction(action.prompt_template)}
          onMouseEnter={() => setHoveredId(action.id)}
          onMouseLeave={() => setHoveredId(null)}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: tokens.space2,
            padding: '5px 12px',
            backgroundColor:
              hoveredId === action.id
                ? tokens.colorSurfaceHover
                : tokens.colorSurface,
            color: tokens.colorAgentBubbleText,
            border: `${tokens.borderWidth} solid ${tokens.colorBorder}`,
            borderRadius: '16px',
            cursor: disabled ? 'not-allowed' : 'pointer',
            opacity: disabled ? 0.6 : 1,
            fontSize: tokens.fontSizeSm,
            fontFamily: tokens.fontFamily,
            fontWeight: tokens.fontWeightMedium,
            lineHeight: tokens.lineHeightNormal,
            transition: `background-color ${tokens.transitionFast}, opacity ${tokens.transitionFast}`,
            maxWidth: '280px',
            textAlign: 'center',
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            // P3-6: Staggered entrance — 50ms delay per button
            animation: 'ar-fade-in 0.3s ease-out both',
            animationDelay: `${index * 50}ms`,
          }}
        >
          {action.icon && <span>{action.icon}</span>}
          <span>{action.label}</span>
        </button>
      ))}
    </div>
  );
};
