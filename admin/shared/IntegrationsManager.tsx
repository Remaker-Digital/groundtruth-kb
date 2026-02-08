/**
 * IntegrationsManager — Shared component for managing third-party integrations.
 *
 * Displays available integrations (Shopify, Zendesk, Mailchimp, Google Analytics)
 * as cards with status badges, activate/deactivate toggles, and disconnect actions.
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

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const BRAND_PRIMARY = '#ff3621';

const STATUS_COLORS: Record<string, string> = {
  connected: '#0D7C3E',
  disconnected: '#787878',
  error: '#D32F2F',
};

const STATUS_LABELS: Record<string, string> = {
  connected: 'Connected',
  disconnected: 'Not Connected',
  error: 'Error',
};

// Integration icons (inline SVG for each service)
const IntegrationIcons: Record<string, React.FC> = {
  shopify: () => (
    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <path d="M15.5 2.5L14 10l-3.5-1L7 17.5l-2-1L3 22h18l-2-8-3.5 1L15.5 2.5z" />
    </svg>
  ),
  zendesk: () => (
    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <circle cx="12" cy="12" r="9" />
      <path d="M8 15l4-6 4 6" />
    </svg>
  ),
  mailchimp: () => (
    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
      <polyline points="22,6 12,13 2,6" />
    </svg>
  ),
  google_analytics: () => (
    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <line x1="18" y1="20" x2="18" y2="10" />
      <line x1="12" y1="20" x2="12" y2="4" />
      <line x1="6" y1="20" x2="6" y2="14" />
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
  background: '#1f1f1f',
  border: '1px solid #272727',
  borderRadius: 8,
  padding: 20,
  display: 'flex',
  flexDirection: 'column',
  gap: 12,
};

const cardHeaderStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: 12,
};

const iconContainerStyle: React.CSSProperties = {
  width: 48,
  height: 48,
  borderRadius: 8,
  background: '#141414',
  border: '1px solid #272727',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  color: '#A0A0A0',
  flexShrink: 0,
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
  background: '#E5A10022',
  color: '#E5A100',
  border: '1px solid #E5A10044',
};

const btnPrimaryStyle: React.CSSProperties = {
  padding: '6px 14px',
  borderRadius: 6,
  border: 'none',
  fontSize: 13,
  fontWeight: 500,
  cursor: 'pointer',
  background: BRAND_PRIMARY,
  color: '#fff',
};

const btnOutlineStyle: React.CSSProperties = {
  padding: '6px 14px',
  borderRadius: 6,
  border: '1px solid #272727',
  fontSize: 13,
  fontWeight: 500,
  cursor: 'pointer',
  background: 'transparent',
  color: '#A0A0A0',
};

const btnDangerStyle: React.CSSProperties = {
  padding: '6px 14px',
  borderRadius: 6,
  border: '1px solid #D32F2F44',
  fontSize: 13,
  fontWeight: 500,
  cursor: 'pointer',
  background: 'transparent',
  color: '#D32F2F',
};

const IntegrationCard: React.FC<IntegrationCardProps> = ({
  integration,
  onActivate,
  onDeactivate,
  onDisconnect,
  activating,
  deactivating,
}) => {
  const [showConfirm, setShowConfirm] = useState(false);
  const IconComponent = IntegrationIcons[integration.icon] || IntegrationIcons.shopify;
  const statusColor = STATUS_COLORS[integration.status || 'disconnected'] || '#787878';
  const statusLabel = STATUS_LABELS[integration.status || 'disconnected'] || 'Not Configured';

  return (
    <div style={cardStyle}>
      {/* Header: icon + name + status */}
      <div style={cardHeaderStyle}>
        <div style={iconContainerStyle}>
          <IconComponent />
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontSize: 15, fontWeight: 600, color: '#F5F5F5' }}>
              {integration.name}
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
            {!integration.tierMet && integration.tierGate && (
              <span style={tierBadgeStyle}>
                {String.fromCodePoint(0x2B06)} {integration.tierGate} tier
              </span>
            )}
          </div>
          <p style={{ margin: '4px 0 0', fontSize: 13, color: '#787878', lineHeight: 1.4 }}>
            {integration.description}
          </p>
        </div>
      </div>

      {/* Actions */}
      <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
        {!integration.tierMet ? (
          <span style={{ fontSize: 12, color: '#E5A100' }}>
            Upgrade to {integration.tierGate} to use this integration
          </span>
        ) : integration.enabled ? (
          <>
            <button
              style={{ ...btnOutlineStyle, opacity: deactivating ? 0.6 : 1 }}
              onClick={() => onDeactivate(integration.type)}
              disabled={deactivating}
            >
              {deactivating ? 'Deactivating...' : 'Deactivate'}
            </button>
            {showConfirm ? (
              <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
                <span style={{ fontSize: 12, color: '#D32F2F' }}>Disconnect? This removes credentials.</span>
                <button
                  style={btnDangerStyle}
                  onClick={() => { onDisconnect(integration.type); setShowConfirm(false); }}
                >
                  Confirm
                </button>
                <button
                  style={btnOutlineStyle}
                  onClick={() => setShowConfirm(false)}
                >
                  Cancel
                </button>
              </div>
            ) : (
              <button
                style={btnDangerStyle}
                onClick={() => setShowConfirm(true)}
              >
                Disconnect
              </button>
            )}
          </>
        ) : (
          <button
            style={{ ...btnPrimaryStyle, opacity: activating ? 0.6 : 1 }}
            onClick={() => onActivate(integration.type)}
            disabled={activating}
          >
            {activating ? 'Activating...' : 'Activate'}
          </button>
        )}
      </div>
    </div>
  );
};

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

export const IntegrationsManager: React.FC<BaseComponentProps> = ({
  tenantContext,
  apiFetch,
  onNotify,
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
      <div style={{ padding: 40, textAlign: 'center', color: '#787878' }}>
        Loading integrations...
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: 40, textAlign: 'center', color: '#D32F2F' }}>
        Failed to load integrations: {error}
      </div>
    );
  }

  const items = integrations ?? [];

  return (
    <div style={{ maxWidth: 800 }}>
      {/* Header */}
      <div style={{ marginBottom: 20 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <h2 style={{ margin: 0, fontSize: 20, fontWeight: 600, color: '#F5F5F5' }}>
            Integrations
          </h2>
          <HelpTooltip text="Connect third-party services to extend your AI agent's capabilities." />
        </div>
        <p style={{ margin: '6px 0 0', fontSize: 14, color: '#787878' }}>
          Connect and manage external services. Activate integrations to unlock additional capabilities
          for your AI agent.
        </p>
      </div>

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
          />
        ))}
      </div>

      {items.length === 0 && (
        <div
          style={{
            padding: 40,
            textAlign: 'center',
            color: '#787878',
            background: '#1f1f1f',
            border: '1px solid #272727',
            borderRadius: 8,
          }}
        >
          No integrations available.
        </div>
      )}

      {/* Summary footer */}
      <div style={{ marginTop: 16, fontSize: 12, color: '#5C5C5C' }}>
        {items.filter((i) => i.enabled).length} of {items.length} integrations active
        {tenantContext.tier === 'starter' || tenantContext.tier === 'trial' ? (
          <span> {String.fromCodePoint(0x2022)} Some integrations require Professional tier or above</span>
        ) : null}
      </div>
    </div>
  );
};
