/**
 * Agent provider logos — inline SVGs from Simple Icons (CC0 license)
 * and the Agent Red brand logo.
 *
 * Usage:
 *   import { getAgentLogo } from '../../shared/icons/agent-logos';
 *   const Logo = getAgentLogo('stripe_mcp');
 *   <Logo size={32} />
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React from 'react';

interface LogoProps {
  size?: number;
  className?: string;
}

// ---------------------------------------------------------------------------
// Agent Red (first-party agents)
// ---------------------------------------------------------------------------

/**
 * Agent Red brand logo — The Beacon ({r} monogram).
 * Simplified inline version of branding/logo/SVG/icon-master.svg.
 * White {r} on Agent Red orange-red (#ff3621) rounded rectangle.
 * S259 D9: replaced placeholder "R" with real brand monogram.
 */
const AgentRedLogo: React.FC<LogoProps> = ({ size = 32 }) => (
  <svg width={size} height={size} viewBox="0 0 128 128" fill="none">
    <rect width="128" height="128" rx="21" fill="#ff3621" />
    {/* Left curly brace */}
    <path d="M25 90V74c0-4-4-5-7-5v-8c3 0 7-1 7-5V39c0-7 6-11 12-11h7v10h-4c-3 0-4 2-4 5v14c0 6-5 8-8 8v1c3 0 8 2 8 9v13c0 3 1 5 4 5h4v10h-7c-6 0-12-5-12-11z" fill="white"/>
    {/* Lowercase r */}
    <path d="M51 44h12v7h0c2-5 8-8 14-8 2 0 2 0 3 0v12c-1 0-3-1-4-1-7 0-12 5-12 11v21H51V44z" fill="white"/>
    {/* Right curly brace */}
    <path d="M86 91h4c3 0 4-2 4-5V73c0-7 5-8 8-9V64c-4 0-8-2-8-6V44c0-3-1-5-4-5h-4V29h7c6 0 12 5 12 11v17c0 3 4 5 7 5v8c-3 0-7 1-7 5V90c0 7-6 11-12 11h-7z" fill="white"/>
  </svg>
);

// ---------------------------------------------------------------------------
// Third-party logos (Simple Icons, CC0 license)
// Paths sourced from https://github.com/simple-icons/simple-icons
// ---------------------------------------------------------------------------

const StripeLogo: React.FC<LogoProps> = ({ size = 32 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="#635BFF">
    <path d="M13.976 9.15c-2.172-.806-3.356-1.426-3.356-2.409 0-.831.683-1.305 1.901-1.305 2.227 0 4.515.858 6.09 1.631l.89-5.494C18.252.975 15.697 0 12.165 0 9.667 0 7.589.654 6.104 1.872 4.56 3.147 3.757 4.992 3.757 7.218c0 4.039 2.467 5.76 6.476 7.219 2.585.92 3.445 1.574 3.445 2.583 0 .98-.84 1.545-2.354 1.545-1.875 0-4.965-.921-6.99-2.109l-.9 5.555C5.175 22.99 8.385 24 11.714 24c2.641 0 4.843-.624 6.328-1.813 1.664-1.305 2.525-3.236 2.525-5.732 0-4.128-2.524-5.851-6.591-7.305z"/>
  </svg>
);

const ShopifyLogo: React.FC<LogoProps> = ({ size = 32 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="#7AB55C">
    <path d="M15.337 23.979l7.216-1.561s-2.604-17.613-2.625-17.73c-.018-.116-.114-.192-.211-.192s-1.929-.136-1.929-.136-1.275-1.274-1.439-1.411c-.045-.037-.075-.058-.121-.074l-.914 21.104zm-1.332-17.606c0-.136 0-.253-.018-.389-.96-.502-2.013-.792-3.104-.792-.082 0-.162 0-.262.018.348-.559.575-1.21.575-1.929 0-1.58-.973-2.933-2.4-3.508C9.063.146 9.43.002 9.826.002c2.396 0 4.302 2.072 4.179 4.371zm-3.063-2.809c-.39-.503-.997-.834-1.679-.834-.084 0-.168.01-.252.027.651-.94 1.034-2.09 1.034-3.335 0-.291-.023-.57-.066-.839a3.78 3.78 0 0 1 1.572 3.115c0 .646-.179 1.295-.609 1.866zM8.678 1.58c-.455 0-.836.183-1.137.491-.705.723-.981 1.885-.79 2.959-1.09.348-1.846.59-1.855.593-.554.174-.571.192-.643.713C4.207 6.692 2.067 23.304 2.067 23.304l11.073 2.078L13.088.413c-.097.037-.193.058-.306.058-.175-.001-2.217-.079-4.104.109z"/>
  </svg>
);

const CoinbaseLogo: React.FC<LogoProps> = ({ size = 32 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="#0052FF">
    <path d="M12 0C5.372 0 0 5.372 0 12s5.372 12 12 12 12-5.372 12-12S18.628 0 12 0zm0 19.2a7.2 7.2 0 1 1 0-14.4 7.12 7.12 0 0 1 5.2 2.24l-2.56 2.56A3.55 3.55 0 0 0 12 8.4a3.6 3.6 0 1 0 2.64 6.0l2.56 2.56A7.12 7.12 0 0 1 12 19.2z"/>
  </svg>
);

const PayPalLogo: React.FC<LogoProps> = ({ size = 32 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="#003087">
    <path d="M7.076 21.337H2.47a.641.641 0 0 1-.633-.74L4.944.901C5.026.382 5.474 0 5.998 0h7.46c2.57 0 4.578.543 5.69 1.81 1.01 1.15 1.304 2.42 1.012 4.287-.023.143-.047.288-.077.437-.983 5.05-4.349 6.797-8.647 6.797h-2.19c-.524 0-.968.382-1.05.9l-1.12 7.106zm14.146-14.42a3.35 3.35 0 0 0-.607-.541c-.013.076-.026.175-.041.254-.93 4.778-4.005 7.201-9.138 7.201h-2.19a.563.563 0 0 0-.556.479l-1.187 7.527h-.506l-.24 1.516a.56.56 0 0 0 .554.647h3.882c.46 0 .85-.334.922-.788.06-.26.76-4.852.816-5.09a.932.932 0 0 1 .923-.788h.58c3.76 0 6.705-1.528 7.565-5.946.36-1.847.174-3.388-.777-4.471z"/>
  </svg>
);

const SquareLogo: React.FC<LogoProps> = ({ size = 32 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="#006AFF">
    <path d="M4.01 0A4.01 4.01 0 0 0 0 4.01v15.98A4.01 4.01 0 0 0 4.01 24h15.98A4.01 4.01 0 0 0 24 19.99V4.01A4.01 4.01 0 0 0 19.99 0zm2.04 5.37h11.9c.56 0 1.01.46 1.01 1.01v11.24c0 .56-.45 1.01-1.01 1.01H6.05c-.56 0-1.01-.45-1.01-1.01V6.38c0-.55.45-1.01 1.01-1.01zM8.1 8.18v7.63h7.8V8.18z"/>
  </svg>
);

const ZendeskLogo: React.FC<LogoProps> = ({ size = 32 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="#03363D">
    <path d="M11.088 3.2v13.568L0 3.2h11.088zM0 20.8a5.544 5.544 0 1 0 11.088 0A5.544 5.544 0 0 0 0 20.8zm12.912 0V7.232L24 20.8H12.912zM24 3.2a5.544 5.544 0 1 0-11.088 0A5.544 5.544 0 0 0 24 3.2z"/>
  </svg>
);

const SlackLogo: React.FC<LogoProps> = ({ size = 32 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <path d="M5.042 15.165a2.528 2.528 0 0 1-2.52 2.523A2.528 2.528 0 0 1 0 15.165a2.527 2.527 0 0 1 2.522-2.52h2.52v2.52zm1.271 0a2.527 2.527 0 0 1 2.521-2.52 2.527 2.527 0 0 1 2.521 2.52v6.313A2.528 2.528 0 0 1 8.834 24a2.528 2.528 0 0 1-2.521-2.522v-6.313z" fill="#E01E5A"/>
    <path d="M8.834 5.042a2.528 2.528 0 0 1-2.521-2.52A2.528 2.528 0 0 1 8.834 0a2.528 2.528 0 0 1 2.521 2.522v2.52H8.834zm0 1.271a2.528 2.528 0 0 1 2.521 2.521 2.528 2.528 0 0 1-2.521 2.521H2.522A2.528 2.528 0 0 1 0 8.834a2.528 2.528 0 0 1 2.522-2.521h6.312z" fill="#36C5F0"/>
    <path d="M18.956 8.834a2.528 2.528 0 0 1 2.522-2.521A2.528 2.528 0 0 1 24 8.834a2.528 2.528 0 0 1-2.522 2.521h-2.522V8.834zm-1.27 0a2.528 2.528 0 0 1-2.523 2.521 2.527 2.527 0 0 1-2.52-2.521V2.522A2.527 2.527 0 0 1 15.163 0a2.528 2.528 0 0 1 2.523 2.522v6.312z" fill="#2EB67D"/>
    <path d="M15.163 18.956a2.528 2.528 0 0 1 2.523 2.522A2.528 2.528 0 0 1 15.163 24a2.527 2.527 0 0 1-2.52-2.522v-2.522h2.52zm0-1.27a2.527 2.527 0 0 1-2.52-2.523 2.527 2.527 0 0 1 2.52-2.52h6.315A2.528 2.528 0 0 1 24 15.163a2.528 2.528 0 0 1-2.522 2.523h-6.315z" fill="#ECB22E"/>
  </svg>
);

const GoogleDocsLogo: React.FC<LogoProps> = ({ size = 32 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="#4285F4">
    <path d="M14.727 6.727H14V0H4.91c-.905 0-1.637.732-1.637 1.636v20.728c0 .904.732 1.636 1.636 1.636h14.182c.904 0 1.636-.732 1.636-1.636V6.727h-6zm-.545 10.455H7.09v-1.455h7.09v1.455zm2.727-2.909H7.091v-1.455h9.818v1.455zm0-2.91H7.091V9.91h9.818v1.454zM14.727 6V0l6.727 6h-6.727z"/>
  </svg>
);

// ---------------------------------------------------------------------------
// Logo registry — maps agent_id to logo component
// ---------------------------------------------------------------------------

const LOGO_MAP: Record<string, React.FC<LogoProps>> = {
  // External MCP
  stripe_mcp: StripeLogo,
  shopify_mcp: ShopifyLogo,
  coinbase_mcp: CoinbaseLogo,
  paypal_mcp: PayPalLogo,
  square_mcp: SquareLogo,
  // Integration agents
  zendesk: ZendeskLogo,
  slack: SlackLogo,
  google_docs: GoogleDocsLogo,
};

/**
 * Get the logo component for an agent.
 * Returns the third-party logo if available, otherwise the Agent Red logo.
 */
export function getAgentLogo(agentId: string): React.FC<LogoProps> {
  return LOGO_MAP[agentId] || AgentRedLogo;
}

export { AgentRedLogo };
