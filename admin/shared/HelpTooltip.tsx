/**
 * HelpTooltip — Shared inline help icon with hover tooltip.
 *
 * Renders a small circled "?" icon that reveals contextual help text
 * on hover. Used consistently across all 9 admin shared components
 * to surface field-level help, metric explanations, and doc links.
 *
 * Pure React + inline styles — no Mantine, no Polaris dependency.
 *
 * Usage:
 *   <HelpTooltip text="Conversations where the AI produced a response." />
 *   <HelpTooltip text="Only Professional+ tiers." docLink="https://docs.agentred.ai/..." />
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useState, useRef, useCallback } from 'react';

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
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const show = useCallback(() => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    setVisible(true);
  }, []);

  const hide = useCallback(() => {
    timeoutRef.current = setTimeout(() => setVisible(false), 150);
  }, []);

  const iconStyle: React.CSSProperties = {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    width: size,
    height: size,
    borderRadius: '50%',
    border: '1px solid #9ca3af',
    color: '#9ca3af',
    fontSize: size * 0.65,
    fontWeight: 700,
    lineHeight: 1,
    cursor: 'help',
    marginLeft: 6,
    verticalAlign: 'middle',
    flexShrink: 0,
    userSelect: 'none',
    position: 'relative',
  };

  const tooltipStyle: React.CSSProperties = {
    position: 'absolute',
    bottom: '100%',
    left: '50%',
    transform: 'translateX(-50%)',
    marginBottom: 8,
    background: '#1f2937',
    color: '#f9fafb',
    fontSize: 12,
    lineHeight: 1.5,
    padding: '8px 12px',
    borderRadius: 6,
    whiteSpace: 'normal',
    width: 240,
    maxWidth: 280,
    zIndex: 9999,
    boxShadow: '0 4px 12px rgba(0,0,0,0.25)',
    pointerEvents: 'auto',
  };

  const arrowStyle: React.CSSProperties = {
    position: 'absolute',
    top: '100%',
    left: '50%',
    transform: 'translateX(-50%)',
    width: 0,
    height: 0,
    borderLeft: '5px solid transparent',
    borderRight: '5px solid transparent',
    borderTop: '5px solid #1f2937',
  };

  return (
    <span
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
      {visible && (
        <span
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
                style={{ color: '#93c5fd', textDecoration: 'underline' }}
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
