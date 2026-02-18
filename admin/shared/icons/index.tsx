/**
 * Shared SVG Icon Library — single source for all admin surfaces.
 *
 * All icons use a consistent style:
 *   - 18x18 default size (customizable via props)
 *   - viewBox 0 0 24 24
 *   - stroke="currentColor" (inherits parent color)
 *   - strokeWidth="2", strokeLinecap="round", strokeLinejoin="round"
 *
 * Usage:
 *   import { Icons } from '../../shared/icons';
 *   <Icons.dashboard />
 *   <Icons.dashboard size={24} />
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React from 'react';

interface IconProps {
  /** Icon width and height in pixels. Default: 18 */
  size?: number;
  /** Additional className for styling */
  className?: string;
  /** Accessibility label. If provided, renders role="img" + aria-label. */
  'aria-label'?: string;
}

const defaultProps: Required<Pick<IconProps, 'size'>> = { size: 18 };

function svgAttrs(props: IconProps) {
  const size = props.size ?? defaultProps.size;
  return {
    width: size,
    height: size,
    viewBox: '0 0 24 24',
    fill: 'none',
    stroke: 'currentColor',
    strokeWidth: 2,
    strokeLinecap: 'round' as const,
    strokeLinejoin: 'round' as const,
    className: props.className,
    ...(props['aria-label']
      ? { role: 'img' as const, 'aria-label': props['aria-label'] }
      : { 'aria-hidden': true as const }),
  };
}

// ---------------------------------------------------------------------------
// Navigation icons (Provider + Standalone)
// ---------------------------------------------------------------------------

/** 2x2 grid — Dashboard overview */
const Dashboard: React.FC<IconProps> = (props) => (
  <svg {...svgAttrs(props)}>
    <rect x="3" y="3" width="7" height="7" /><rect x="14" y="3" width="7" height="7" />
    <rect x="3" y="14" width="7" height="7" /><rect x="14" y="14" width="7" height="7" />
  </svg>
);

/** Chat bubble — Inbox / Conversations */
const Inbox: React.FC<IconProps> = (props) => (
  <svg {...svgAttrs(props)}>
    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
  </svg>
);

/** Book — Knowledge Base */
const Knowledge: React.FC<IconProps> = (props) => (
  <svg {...svgAttrs(props)}>
    <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
    <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
  </svg>
);

/** Bar chart — Analytics / SLA Trends */
const Analytics: React.FC<IconProps> = (props) => (
  <svg {...svgAttrs(props)}>
    <line x1="18" y1="20" x2="18" y2="10" /><line x1="12" y1="20" x2="12" y2="4" />
    <line x1="6" y1="20" x2="6" y2="14" />
  </svg>
);

/** Gear — Configuration / Settings */
const Config: React.FC<IconProps> = (props) => (
  <svg {...svgAttrs(props)}>
    <circle cx="12" cy="12" r="3" />
    <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" />
  </svg>
);

/** Monitor — Widget */
const Widget: React.FC<IconProps> = (props) => (
  <svg {...svgAttrs(props)}>
    <rect x="2" y="3" width="20" height="14" rx="2" ry="2" />
    <line x1="8" y1="21" x2="16" y2="21" /><line x1="12" y1="17" x2="12" y2="21" />
  </svg>
);

/** Credit card — Billing */
const Billing: React.FC<IconProps> = (props) => (
  <svg {...svgAttrs(props)}>
    <rect x="1" y="4" width="22" height="16" rx="2" ry="2" />
    <line x1="1" y1="10" x2="23" y2="10" />
  </svg>
);

/** People group — Team / Tenants */
const Team: React.FC<IconProps> = (props) => (
  <svg {...svgAttrs(props)}>
    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" /><circle cx="9" cy="7" r="4" />
    <path d="M23 21v-2a4 4 0 0 0-3-3.87" /><path d="M16 3.13a4 4 0 0 1 0 7.75" />
  </svg>
);

/** Chain link — Integrations */
const Integrations: React.FC<IconProps> = (props) => (
  <svg {...svgAttrs(props)}>
    <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
    <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
  </svg>
);

/** Open book — Documentation */
const Docs: React.FC<IconProps> = (props) => (
  <svg {...svgAttrs(props)}>
    <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
    <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
  </svg>
);

/** Arrow-out-of-door — Logout / Sign out */
const Logout: React.FC<IconProps> = (props) => (
  <svg {...svgAttrs(props)}>
    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
    <polyline points="16 17 21 12 16 7" /><line x1="21" y1="12" x2="9" y2="12" />
  </svg>
);

/** External link arrow — used in nav items and storefront link */
const ExternalLink: React.FC<IconProps> = (props) => {
  const size = props.size ?? 12;
  return (
    <svg {...svgAttrs({ ...props, size })}>
      <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
      <polyline points="15 3 21 3 21 9" /><line x1="10" y1="14" x2="21" y2="3" />
    </svg>
  );
};

/** House — Storefront */
const Storefront: React.FC<IconProps> = (props) => {
  const size = props.size ?? 14;
  return (
    <svg {...svgAttrs({ ...props, size })}>
      <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
      <polyline points="9 22 9 12 15 12 15 22" />
    </svg>
  );
};

/** Lightning bolt — Quick Actions */
const QuickActions: React.FC<IconProps> = (props) => (
  <svg {...svgAttrs(props)}>
    <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
  </svg>
);

/** Padlock with vault — Memory / Privacy */
const Memory: React.FC<IconProps> = (props) => (
  <svg {...svgAttrs(props)}>
    <path d="M12 2a4 4 0 0 0-4 4v2H6a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V10a2 2 0 0 0-2-2h-2V6a4 4 0 0 0-4-4z" />
    <circle cx="12" cy="15" r="2" /><line x1="12" y1="17" x2="12" y2="19" />
  </svg>
);

// ---------------------------------------------------------------------------
// Provider-only navigation icons
// ---------------------------------------------------------------------------

/** Rocket — Deployments */
const Deployments: React.FC<IconProps> = (props) => (
  <svg {...svgAttrs(props)}>
    <path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z" />
    <path d="M12 15l-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z" />
    <path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0" />
    <path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5" />
  </svg>
);

/** Server racks — Queue Health */
const Queue: React.FC<IconProps> = (props) => (
  <svg {...svgAttrs(props)}>
    <rect x="2" y="4" width="20" height="5" rx="1" /><rect x="2" y="13" width="20" height="5" rx="1" />
    <line x1="6" y1="6.5" x2="6" y2="6.5" /><line x1="6" y1="15.5" x2="6" y2="15.5" />
  </svg>
);

/** Clock circle — Status Page */
const Status: React.FC<IconProps> = (props) => (
  <svg {...svgAttrs(props)}>
    <circle cx="12" cy="12" r="10" /><polyline points="12 6 12 12 16 14" />
  </svg>
);

/** Bell — Alerts */
const Alerts: React.FC<IconProps> = (props) => (
  <svg {...svgAttrs(props)}>
    <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
    <path d="M13.73 21a2 2 0 0 1-3.46 0" />
  </svg>
);

/** Shield — Compliance */
const Compliance: React.FC<IconProps> = (props) => (
  <svg {...svgAttrs(props)}>
    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
  </svg>
);

/** Key — Secrets */
const Secrets: React.FC<IconProps> = (props) => (
  <svg {...svgAttrs(props)}>
    <path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4" />
  </svg>
);

/** Padlock — MFA */
const Mfa: React.FC<IconProps> = (props) => (
  <svg {...svgAttrs(props)}>
    <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
    <path d="M7 11V7a5 5 0 0 1 10 0v4" />
  </svg>
);

// ---------------------------------------------------------------------------
// Utility icons (dark mode toggle, etc.)
// ---------------------------------------------------------------------------

/** Sun — Light mode indicator */
const Sun: React.FC<IconProps> = (props) => {
  const size = props.size ?? 16;
  return (
    <svg {...svgAttrs({ ...props, size })}>
      <circle cx="12" cy="12" r="5" />
      <line x1="12" y1="1" x2="12" y2="3" /><line x1="12" y1="21" x2="12" y2="23" />
      <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" /><line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
      <line x1="1" y1="12" x2="3" y2="12" /><line x1="21" y1="12" x2="23" y2="12" />
      <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" /><line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
    </svg>
  );
};

/** Moon — Dark mode indicator */
const Moon: React.FC<IconProps> = (props) => {
  const size = props.size ?? 16;
  return (
    <svg {...svgAttrs({ ...props, size })}>
      <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
    </svg>
  );
};

// ---------------------------------------------------------------------------
// Export as named map for consistent usage: <Icons.dashboard />
// ---------------------------------------------------------------------------

export const Icons = {
  // Shared across surfaces
  dashboard: Dashboard,
  inbox: Inbox,
  knowledge: Knowledge,
  analytics: Analytics,
  config: Config,
  widget: Widget,
  billing: Billing,
  team: Team,
  integrations: Integrations,
  docs: Docs,
  logout: Logout,
  externalLink: ExternalLink,
  storefront: Storefront,
  quickactions: QuickActions,
  memory: Memory,

  // Provider-only
  tenants: Team, // Alias — same icon
  deployments: Deployments,
  queue: Queue,
  status: Status,
  alerts: Alerts,
  compliance: Compliance,
  secrets: Secrets,
  sla: Analytics, // Alias — same bar chart icon
  mfa: Mfa,
  diagnostics: Config, // Alias — gear icon for support diagnostics
  cost: Billing, // Alias — same billing icon for cost analytics
  abuse: Alerts, // Alias — same alert icon for abuse detection

  // Utility
  sun: Sun,
  moon: Moon,
} as const;

export type IconName = keyof typeof Icons;
