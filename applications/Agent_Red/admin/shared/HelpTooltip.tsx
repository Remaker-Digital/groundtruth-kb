// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * HelpTooltip — Shared inline help icon with hover tooltip.
 *
 * Renders a small circled "?" icon that reveals contextual help text
 * on hover. Used consistently across all 9 admin shared components
 * to surface field-level help, metric explanations, and doc links.
 *
 * Uses position: fixed so the tooltip escapes any parent stacking
 * context and always renders above all page content (z-index: 10000).
 *
 * Pure React + inline styles — no Mantine, no Polaris dependency.
 *
 * Usage:
 *   <HelpTooltip text="Conversations where the AI produced a response." />
 *   <HelpTooltip text="Only Professional+ tiers." docLink="https://agentredcx.com/docs/..." />
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useState, useRef, useCallback, useLayoutEffect } from 'react';
import { tokens } from './theme/styles';

export interface HelpTooltipProps {
  /** Short tooltip text (1-2 sentences). */
  text: string;
  /** Optional link to documentation. */
  docLink?: string;
  /** Icon size in px (default 14). */
  size?: number;
}

export const HelpTooltip: React.FC<HelpTooltipProps> = ({
  text,
  docLink,
  size = 14,
}) => {
  const [visible, setVisible] = useState(false);
  const [pos, setPos] = useState<{ top: number; left: number } | null>(null);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const iconRef = useRef<HTMLSpanElement>(null);
  const tooltipRef = useRef<HTMLSpanElement>(null);

  const show = useCallback(() => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    setVisible(true);
  }, []);

  const hide = useCallback(() => {
    timeoutRef.current = setTimeout(() => setVisible(false), 150);
  }, []);

  // Compute fixed position whenever tooltip becomes visible or window scrolls
  useLayoutEffect(() => {
    if (!visible || !iconRef.current) return;

    const updatePosition = () => {
      const iconRect = iconRef.current!.getBoundingClientRect();
      const tooltipWidth = 240;

      // Position above the icon, centered horizontally
      let left = iconRect.left + iconRect.width / 2 - tooltipWidth / 2;
      // Clamp to viewport edges with 8px margin
      left = Math.max(8, Math.min(left, window.innerWidth - tooltipWidth - 8));

      // Get tooltip height (estimate if not yet rendered)
      const tooltipEl = tooltipRef.current;
      const tooltipHeight = tooltipEl ? tooltipEl.offsetHeight : 60;

      let top = iconRect.top - tooltipHeight - 8;
      // If tooltip would go above viewport, show below instead
      if (top < 8) {
        top = iconRect.bottom + 8;
      }

      setPos({ top, left });
    };

    updatePosition();

    // Update on scroll/resize so tooltip follows the icon
    window.addEventListener('scroll', updatePosition, true);
    window.addEventListener('resize', updatePosition);
    return () => {
      window.removeEventListener('scroll', updatePosition, true);
      window.removeEventListener('resize', updatePosition);
    };
  }, [visible]);

  const iconStyle: React.CSSProperties = {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    width: size,
    height: size,
    borderRadius: '50%',
    border: `1px solid ${tokens.textMuted}`,
    color: tokens.textMuted,
    fontSize: size * 0.65,
    fontWeight: 700,
    lineHeight: 1,
    cursor: 'help',
    marginLeft: 6,
    verticalAlign: 'middle',
    flexShrink: 0,
    userSelect: 'none',
  };

  const tooltipStyle: React.CSSProperties = {
    position: 'fixed',
    top: pos?.top ?? 0,
    left: pos?.left ?? 0,
    zIndex: 10000,
    background: tokens.surface,
    color: tokens.textPrimary,
    fontSize: 12,
    lineHeight: 1.5,
    padding: '8px 12px',
    borderRadius: 6,
    whiteSpace: 'normal',
    width: 240,
    maxWidth: 280,
    boxShadow: '0 4px 12px rgba(0,0,0,0.25)',
    pointerEvents: 'auto',
  };

  // Arrow points toward the icon — direction depends on placement
  const iconRect = iconRef.current?.getBoundingClientRect();
  const isBelow = pos && iconRect ? pos.top > iconRect.bottom : false;

  const arrowStyle: React.CSSProperties = isBelow
    ? {
        // Tooltip is below icon — arrow on top pointing up
        position: 'absolute',
        bottom: '100%',
        left: '50%',
        transform: 'translateX(-50%)',
        width: 0,
        height: 0,
        borderLeft: '5px solid transparent',
        borderRight: '5px solid transparent',
        borderBottom: `5px solid ${tokens.surface}`,
      }
    : {
        // Tooltip is above icon — arrow on bottom pointing down
        position: 'absolute',
        top: '100%',
        left: '50%',
        transform: 'translateX(-50%)',
        width: 0,
        height: 0,
        borderLeft: '5px solid transparent',
        borderRight: '5px solid transparent',
        borderTop: `5px solid ${tokens.surface}`,
      };

  return (
    <span
      ref={iconRef}
      style={iconStyle}
      onMouseEnter={show}
      onMouseLeave={hide}
      onFocus={show}
      onBlur={hide}
      tabIndex={0}
      role="button"
      aria-label={text}
    >
      ?
      {visible && pos && (
        <span
          ref={tooltipRef}
          style={tooltipStyle}
          onMouseEnter={show}
          onMouseLeave={hide}
        >
          {text}
          {docLink && (
            <>
              {' '}
              <a
                href={docLink}
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: tokens.action, textDecoration: 'underline' }}
              >
                Learn more
              </a>
            </>
          )}
          <span style={arrowStyle} />
        </span>
      )}
    </span>
  );
};

export default HelpTooltip;
