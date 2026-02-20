/**
 * EmptyState — Shared empty state component for all admin surfaces.
 *
 * Renders a centered message with an icon, title, optional subtitle,
 * and optional call-to-action button. Works with both Mantine and
 * framework-agnostic (shared component) contexts.
 *
 * Usage:
 *   <EmptyState
 *     icon={<Icons.inbox />}
 *     title="No conversations yet"
 *     subtitle="Conversations will appear here once customers start chatting."
 *     action={{ label: 'View documentation', onClick: () => navigate('/docs') }}
 *   />
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React from 'react';
import { tokens } from './theme/styles';

interface EmptyStateAction {
  label: string;
  onClick: () => void;
}

interface EmptyStateProps {
  /** Icon element (e.g. <Icons.inbox size={36} />) */
  icon: React.ReactNode;
  /** Primary message — brief, actionable */
  title: string;
  /** Optional explanatory text */
  subtitle?: string;
  /** Optional CTA button */
  action?: EmptyStateAction;
}

const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    justifyContent: 'center',
    padding: '48px 24px',
    textAlign: 'center' as const,
    color: tokens.textMuted,
  },
  iconWrapper: {
    marginBottom: '16px',
    color: tokens.textTertiary,
  },
  title: {
    fontSize: '15px',
    fontWeight: 600,
    color: tokens.textSecondary,
    marginBottom: '6px',
    lineHeight: 1.4,
  },
  subtitle: {
    fontSize: '13px',
    color: tokens.textMuted,
    maxWidth: '360px',
    lineHeight: 1.5,
  },
  actionButton: {
    marginTop: '16px',
    padding: '8px 16px',
    fontSize: '13px',
    fontWeight: 500,
    borderRadius: '6px',
  },
};

export const EmptyState: React.FC<EmptyStateProps> = ({ icon, title, subtitle, action }) => (
  <div style={styles.container} role="status" aria-label={title}>
    <div style={styles.iconWrapper}>{icon}</div>
    <div style={styles.title}>{title}</div>
    {subtitle && <div style={styles.subtitle}>{subtitle}</div>}
    {action && (
      <button
        type="button"
        className="ar-btn-action ar-opacity-hover"
        style={styles.actionButton}
        onClick={action.onClick}
      >
        {action.label}
      </button>
    )}
  </div>
);

export default EmptyState;
