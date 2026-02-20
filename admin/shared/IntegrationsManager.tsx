/**
 * IntegrationsManager — Shared component for managing third-party integrations.
 *
 * Displays available integrations (Shopify, Zendesk, Mailchimp, Google Analytics,
 * Stripe MCP) as cards with status badges, activate/deactivate toggles, and
 * disconnect actions. Stripe includes MCP credential management panel.
 * Tier-gated integrations show upgrade prompts for lower-tier tenants.
 *
 * C10 capability dependency for Launch UI Test.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useCallback, useState } from 'react';
import type { BaseComponentProps, IntegrationSummary } from './types/index';
import {
  useIntegrations,
  useActivateIntegration,
  useDeactivateIntegration,
  useDisconnectIntegration,
} from './hooks/index';
import { HelpTooltip } from './HelpTooltip';
import { McpConfigPanel } from './McpConfigPanel';
import { tokens } from './theme/styles';


// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

/** Map HoverButton variant → CSS utility class */
const VARIANT_CLASS: Record<string, string> = {
  primary: 'ar-btn-action',
  success: 'ar-btn-activate',
  outline: 'ar-btn-ghost',
  danger: 'ar-btn-danger-outline',
};

const STATUS_COLORS: Record<string, string> = {
  connected: tokens.success,
  disconnected: tokens.textTertiary,
  error: tokens.danger,
};

const STATUS_LABELS: Record<string, string> = {
  connected: 'Connected',
  disconnected: 'Not Connected',
  error: 'Error',
};

// Integration logo mapping: type → filename stem (without -dark/-light suffix)
const INTEGRATION_LOGO_MAP: Record<string, string> = {
  shopify: 'shopify-logo',
  zendesk: 'zendesk-logo',
  mailchimp: 'mailchimp-logo',
  google_analytics: 'google-analytics-logo',
  stripe: 'stripe-logo',
};

const DOCS_BASE = 'https://agentredcx.com/docs/admin-guide';

/** Per-integration tooltip text + doc link. */
const INTEGRATION_TOOLTIPS: Record<string, { text: string; docLink: string }> = {
  shopify: {
    text: 'Core commerce integration. Syncs products, orders, and customer data to power AI responses with real-time store information.',
    docLink: `${DOCS_BASE}/integrations#shopify`,
  },
  zendesk: {
    text: 'Route escalated conversations to Zendesk tickets. Requires Professional tier or above.',
    docLink: `${DOCS_BASE}/integrations#zendesk`,
  },
  mailchimp: {
    text: 'Sync customer emails and conversation insights to Mailchimp audiences for targeted marketing.',
    docLink: `${DOCS_BASE}/integrations#mailchimp`,
  },
  google_analytics: {
    text: 'Send conversation events and conversion data to Google Analytics 4 for unified reporting.',
    docLink: `${DOCS_BASE}/integrations#google-analytics`,
  },
};

// Fallback inline SVG icons (used if logo image fails to load)
const IntegrationIcons: Record<string, React.FC> = {
  shopify: () => (
    <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <path d="M15.5 2.5L14 10l-3.5-1L7 17.5l-2-1L3 22h18l-2-8-3.5 1L15.5 2.5z" />
    </svg>
  ),
  zendesk: () => (
    <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <circle cx="12" cy="12" r="9" />
      <path d="M8 15l4-6 4 6" />
    </svg>
  ),
  mailchimp: () => (
    <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
      <polyline points="22,6 12,13 2,6" />
    </svg>
  ),
  google_analytics: () => (
    <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <line x1="18" y1="20" x2="18" y2="10" />
      <line x1="12" y1="20" x2="12" y2="4" />
      <line x1="6" y1="20" x2="6" y2="14" />
    </svg>
  ),
  stripe: () => (
    <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <rect x="1" y="4" width="22" height="16" rx="2" ry="2" />
      <line x1="1" y1="10" x2="23" y2="10" />
    </svg>
  ),
};

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

interface IntegrationCardProps {
  integration: IntegrationSummary;
  onActivate: (type: string) => void;
  onDeactivate: (type: string) => void;
  onDisconnect: (type: string) => void;
  activating: boolean;
  deactivating: boolean;
}

const cardStyle: React.CSSProperties = {
  background: tokens.surface,
  border: `1px solid ${tokens.border}`,
  borderRadius: 8,
  padding: 16,
  display: 'flex',
  flexDirection: 'row',
  alignItems: 'center',
  gap: 16,
};

const iconContainerStyle: React.CSSProperties = {
  width: 180,
  height: 180,
  borderRadius: 8,
  background: tokens.page,
  border: `1px solid ${tokens.border}`,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  color: tokens.textMuted,
  flexShrink: 0,
  overflow: 'hidden',
};

const badgeStyle = (color: string): React.CSSProperties => ({
  display: 'inline-flex',
  alignItems: 'center',
  gap: 4,
  padding: '2px 8px',
  borderRadius: 10,
  fontSize: 11,
  fontWeight: 600,
  background: `${color}22`,
  color,
  border: `1px solid ${color}44`,
});

const tierBadgeStyle: React.CSSProperties = {
  display: 'inline-flex',
  alignItems: 'center',
  gap: 4,
  padding: '2px 8px',
  borderRadius: 10,
  fontSize: 11,
  fontWeight: 600,
  background: `${tokens.warning}22`,
  color: tokens.warning,
  border: `1px solid ${tokens.warning}44`,
};

const comingSoonBadgeStyle: React.CSSProperties = {
  display: 'inline-flex',
  alignItems: 'center',
  gap: 4,
  padding: '2px 8px',
  borderRadius: 10,
  fontSize: 11,
  fontWeight: 600,
  background: '#6366f122',
  color: '#818cf8',
  border: '1px solid #6366f144',
};

// Button component — uses CSS hover utility classes from tokens.css
const btnBase: React.CSSProperties = {
  padding: '6px 14px',
  borderRadius: 6,
  fontSize: 13,
  fontWeight: 500,
};

const HoverButton: React.FC<{
  variant: 'primary' | 'success' | 'outline' | 'danger';
  onClick: () => void;
  disabled?: boolean;
  children: React.ReactNode;
}> = ({ variant, onClick, disabled, children }) => (
  <button
    className={VARIANT_CLASS[variant] || 'ar-btn-action'}
    style={btnBase}
    onClick={onClick}
    disabled={disabled}
  >
    {children}
  </button>
);

const IntegrationCard: React.FC<IntegrationCardProps & {
  isDark?: boolean;
  basePath?: string;
  apiFetch?: (url: string, options?: RequestInit) => Promise<Response>;
  tenantId?: string;
  onNotify?: (message: string, severity: 'success' | 'error' | 'info') => void;
  onRefetch?: () => void;
}> = ({
  integration,
  onActivate,
  onDeactivate,
  onDisconnect,
  activating,
  deactivating,
  isDark = true,
  basePath = '',
  apiFetch,
  tenantId,
  onNotify,
  onRefetch,
}) => {
  const [showConfirm, setShowConfirm] = useState(false);
  const [logoError, setLogoError] = useState(false);
  const IconComponent = IntegrationIcons[integration.icon] || IntegrationIcons.shopify;
  const statusColor = STATUS_COLORS[integration.status || 'disconnected'] || tokens.textTertiary;
  const statusLabel = STATUS_LABELS[integration.status || 'disconnected'] || 'Not Configured';

  // Resolve logo path: dark variant for dark mode, light for light mode
  const logoStem = INTEGRATION_LOGO_MAP[integration.icon] || INTEGRATION_LOGO_MAP[integration.type];
  const logoSuffix = isDark ? 'dark' : 'light';
  const logoPath = logoStem ? `${basePath}/integration-logos/${logoStem}-${logoSuffix}.svg` : null;

  return (
    <div style={cardStyle}>
      {/* Logo: horizontal rectangle, left side */}
      <div style={iconContainerStyle}>
        {logoPath && !logoError ? (
          <img
            src={logoPath}
            alt={`${integration.name} logo`}
            style={{ objectFit: 'contain', display: 'block' }}
            onError={() => setLogoError(true)}
          />
        ) : (
          <IconComponent />
        )}
      </div>

      {/* Right side: name, badges, description, actions */}
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
          <span style={{ fontSize: 22, fontWeight: 600, color: tokens.textPrimary }}>
            {integration.name}
            {INTEGRATION_TOOLTIPS[integration.type] && (
              <HelpTooltip
                text={INTEGRATION_TOOLTIPS[integration.type].text}
                docLink={INTEGRATION_TOOLTIPS[integration.type].docLink}
              />
            )}
          </span>
          {integration.status && (
            <span style={badgeStyle(statusColor)}>
              <span
                style={{
                  width: 6,
                  height: 6,
                  borderRadius: '50%',
                  background: statusColor,
                  display: 'inline-block',
                }}
              />
              {statusLabel}
            </span>
          )}
          {integration.comingSoon && (
            <span style={comingSoonBadgeStyle}>
              Coming Soon
            </span>
          )}
          {!integration.comingSoon && !integration.tierMet && integration.tierGate && (
            <span style={tierBadgeStyle}>
              {String.fromCodePoint(0x2B06)} {integration.tierGate} tier
            </span>
          )}
        </div>
        <p style={{ margin: '4px 0 8px', fontSize: 13, color: tokens.textTertiary, lineHeight: 1.4 }}>
          {integration.description}
        </p>

        {/* Actions — inline with text */}
        <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
          {integration.comingSoon ? (
            <span style={{ fontSize: 12, color: '#818cf8' }}>
              This integration is under development and will be available soon.
            </span>
          ) : !integration.tierMet ? (
            <span style={{ fontSize: 12, color: tokens.warning }}>
              Upgrade to {integration.tierGate} to use this integration
            </span>
          ) : integration.enabled ? (
            <>
              <HoverButton
                variant="outline"
                onClick={() => onDeactivate(integration.type)}
                disabled={deactivating}
              >
                {deactivating ? 'Deactivating...' : 'Deactivate'}
              </HoverButton>
              {showConfirm ? (
                <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
                  <span style={{ fontSize: 12, color: tokens.danger }}>Disconnect? This removes credentials.</span>
                  <HoverButton
                    variant="danger"
                    onClick={() => { onDisconnect(integration.type); setShowConfirm(false); }}
                  >
                    Confirm
                  </HoverButton>
                  <HoverButton
                    variant="outline"
                    onClick={() => setShowConfirm(false)}
                  >
                    Cancel
                  </HoverButton>
                </div>
              ) : (
                <HoverButton
                  variant="danger"
                  onClick={() => setShowConfirm(true)}
                >
                  Disconnect
                </HoverButton>
              )}
            </>
          ) : (
            <HoverButton
              variant="success"
              onClick={() => onActivate(integration.type)}
              disabled={activating}
            >
              {activating ? 'Activating...' : 'Activate'}
            </HoverButton>
          )}
        </div>

        {/* Stripe MCP config panel — shown when Stripe is enabled */}
        {integration.type === 'stripe' && integration.enabled && apiFetch && tenantId && onNotify && (
          <McpConfigPanel
            tenantId={tenantId}
            apiFetch={apiFetch}
            onNotify={onNotify}
            onStatusChange={onRefetch}
          />
        )}
      </div>
    </div>
  );
};

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

export const IntegrationsManager: React.FC<BaseComponentProps & { isDark?: boolean; basePath?: string }> = ({
  tenantContext,
  apiFetch,
  onNotify,
  isDark = true,
  basePath = '',
}) => {
  const { data: integrations, loading, error, refetch } = useIntegrations(apiFetch);
  const { activate, loading: activating } = useActivateIntegration(apiFetch);
  const { deactivate, loading: deactivating } = useDeactivateIntegration(apiFetch);
  const { disconnect } = useDisconnectIntegration(apiFetch);

  const [actionTarget, setActionTarget] = useState<string | null>(null);

  const handleActivate = useCallback(
    async (type: string) => {
      setActionTarget(type);
      const result = await activate(type);
      setActionTarget(null);
      if (result?.success) {
        onNotify(`${result.message}`, 'success');
        refetch();
      } else {
        onNotify('Failed to activate integration.', 'error');
      }
    },
    [activate, onNotify, refetch],
  );

  const handleDeactivate = useCallback(
    async (type: string) => {
      setActionTarget(type);
      const result = await deactivate(type);
      setActionTarget(null);
      if (result?.success) {
        onNotify(`${result.message}`, 'success');
        refetch();
      } else {
        onNotify('Failed to deactivate integration.', 'error');
      }
    },
    [deactivate, onNotify, refetch],
  );

  const handleDisconnect = useCallback(
    async (type: string) => {
      const result = await disconnect(type);
      if (result?.success) {
        onNotify(`${result.message}`, 'success');
        refetch();
      } else {
        onNotify('Failed to disconnect integration.', 'error');
      }
    },
    [disconnect, onNotify, refetch],
  );

  // ----- Loading / Error states -----

  if (loading) {
    return (
      <div style={{ padding: 40, textAlign: 'center', color: tokens.textTertiary }}>
        Loading integrations...
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: 40, textAlign: 'center', color: tokens.danger }}>
        Failed to load integrations: {error}
      </div>
    );
  }

  const items = integrations ?? [];

  return (
    <div style={{ maxWidth: 800 }}>
      {/* Integration cards */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        {items.map((integration) => (
          <IntegrationCard
            key={integration.type}
            integration={integration}
            onActivate={handleActivate}
            onDeactivate={handleDeactivate}
            onDisconnect={handleDisconnect}
            activating={activating && actionTarget === integration.type}
            deactivating={deactivating && actionTarget === integration.type}
            isDark={isDark}
            basePath={basePath}
            apiFetch={apiFetch}
            tenantId={tenantContext.tenantId}
            onNotify={onNotify}
            onRefetch={refetch}
          />
        ))}
      </div>

      {items.length === 0 && (
        <div
          style={{
            padding: 40,
            textAlign: 'center',
            color: tokens.textTertiary,
            background: tokens.surface,
            border: `1px solid ${tokens.border}`,
            borderRadius: 8,
          }}
        >
          No integrations available.
        </div>
      )}

      {/* Summary footer */}
      <div style={{ marginTop: 16, fontSize: 12, color: tokens.textTertiary }}>
        {items.filter((i) => i.enabled).length} of {items.length} integrations active
        {tenantContext.tier === 'starter' || tenantContext.tier === 'trial' ? (
          <span> {String.fromCodePoint(0x2022)} Some integrations require Professional tier or above</span>
        ) : null}
      </div>
    </div>
  );
};
