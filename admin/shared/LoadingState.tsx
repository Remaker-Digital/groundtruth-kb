// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * LoadingState — Shared loading indicator for all admin surfaces.
 *
 * Provides two variants:
 *   - spinner: CSS-animated ring (default) — for page-level or section-level loading
 *   - skeleton: Pulsing placeholder blocks — for content-shaped loading placeholders
 *
 * Usage:
 *   <LoadingState />                               // Default spinner with "Loading..."
 *   <LoadingState text="Loading conversations" />  // Custom text
 *   <LoadingState variant="skeleton" lines={4} />  // Skeleton lines
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React from 'react';
import { tokens } from './theme/styles';

// ---------------------------------------------------------------------------
// Keyframes (injected once)
// ---------------------------------------------------------------------------

const KEYFRAMES_ID = 'agent-red-loading-keyframes';

function ensureKeyframes() {
  if (typeof document === 'undefined') return;
  if (document.getElementById(KEYFRAMES_ID)) return;
  const style = document.createElement('style');
  style.id = KEYFRAMES_ID;
  style.textContent = `
    @keyframes ar-spin { to { transform: rotate(360deg); } }
    @keyframes ar-pulse { 0%,100% { opacity: 0.4; } 50% { opacity: 0.15; } }
  `;
  document.head.appendChild(style);
}

// ---------------------------------------------------------------------------
// Spinner variant
// ---------------------------------------------------------------------------

interface SpinnerProps {
  variant?: 'spinner';
  /** Loading message displayed below the spinner */
  text?: string;
  /** Spinner size in pixels. Default: 32 */
  size?: number;
}

const Spinner: React.FC<SpinnerProps> = ({ text = 'Loading\u2026', size = 32 }) => {
  ensureKeyframes();
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '48px 16px',
        color: tokens.textMuted,
      }}
      role="status"
      aria-label={text}
    >
      <div
        style={{
          width: size,
          height: size,
          border: `3px solid ${tokens.border}`,
          borderTopColor: tokens.brand,
          borderRadius: '50%',
          animation: 'ar-spin 0.8s linear infinite',
          marginBottom: '12px',
        }}
      />
      <span style={{ fontSize: '14px' }}>{text}</span>
    </div>
  );
};

// ---------------------------------------------------------------------------
// Skeleton variant
// ---------------------------------------------------------------------------

interface SkeletonProps {
  variant: 'skeleton';
  /** Number of skeleton lines. Default: 3 */
  lines?: number;
  /** Whether to include a larger "header" block at the top. Default: true */
  showHeader?: boolean;
  text?: never;
  size?: never;
}

const Skeleton: React.FC<SkeletonProps> = ({ lines = 3, showHeader = true }) => {
  ensureKeyframes();
  const lineWidths = ['100%', '92%', '85%', '78%', '95%', '88%'];
  return (
    <div style={{ padding: '24px 0' }} role="status" aria-label="Loading content">
      {showHeader && (
        <div
          style={{
            height: '20px',
            width: '40%',
            background: tokens.border,
            borderRadius: '4px',
            marginBottom: '20px',
            animation: 'ar-pulse 1.5s ease-in-out infinite',
          }}
        />
      )}
      {Array.from({ length: lines }, (_, i) => (
        <div
          key={i}
          style={{
            height: '14px',
            width: lineWidths[i % lineWidths.length],
            background: tokens.border,
            borderRadius: '4px',
            marginBottom: '12px',
            animation: 'ar-pulse 1.5s ease-in-out infinite',
            animationDelay: `${i * 0.1}s`,
          }}
        />
      ))}
    </div>
  );
};

// ---------------------------------------------------------------------------
// Combined export
// ---------------------------------------------------------------------------

type LoadingStateProps = SpinnerProps | SkeletonProps;

export const LoadingState: React.FC<LoadingStateProps> = (props) => {
  if (props.variant === 'skeleton') {
    return <Skeleton {...props} />;
  }
  return <Spinner {...props} />;
};

export default LoadingState;
