/**
 * Shared TypeScript types for the Admin component library.
 *
 * These types are used by all 9 shared components and both admin shells
 * (Shopify embedded + Standalone). Framework-agnostic — no Polaris or
 * shell-specific dependencies.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

// ---------------------------------------------------------------------------
// Tenant & Auth
// ---------------------------------------------------------------------------

export type TenantTier = 'trial' | 'starter' | 'professional' | 'enterprise';
export type TenantStatus = 'active' | 'suspended' | 'cancelled' | 'trial_expired';
export type BillingChannel = 'shopify' | 'stripe';

export interface TenantContext {
  tenantId: string;
  tier: TenantTier;
  status: TenantStatus;
  billingChannel: BillingChannel;
  shopDomain?: string;
}

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------

export type ConfigFieldType = 'string' | 'number' | 'boolean' | 'select' | 'textarea' | 'color' | 'json';

export interface ConfigField {
  key: string;
  label: string;
  description: string;
  type: ConfigFieldType;
  defaultValue: unknown;
  currentValue: unknown;
  options?: Array<{ value: string; label: string }>;
  tierGate?: TenantTier;
  stepOrder: number;
  group: string;
}

export interface ConfigVersion {
  version: number;
  createdAt: string;
  actor: string;
  changeCount: number;
}

export interface ConfigDiff {
  field: string;
  before: unknown;
  after: unknown;
}

export interface ConfigReadResult {
  config: Record<string, unknown>;
  version: number;
  tier: TenantTier;
  fromCache: boolean;
}

export interface ConfigUpdateResult {
  success: boolean;
  version: number;
  changes: ConfigDiff[];
  message: string;
}

// ---------------------------------------------------------------------------
// Onboarding
// ---------------------------------------------------------------------------

export type OnboardingStep =
  | 'brand_and_tone'
  | 'ai_behavior'
  | 'escalation'
  | 'integrations'
  | 'knowledge_base'
  | 'response_policies'
  | 'customer_memory'
  | 'notifications'
  | 'widget_appearance';

export interface OnboardingStepConfig {
  step: OnboardingStep;
  label: string;
  description: string;
  fields: ConfigField[];
  isComplete: boolean;
}

// ---------------------------------------------------------------------------
// Usage & Billing
// ---------------------------------------------------------------------------

export interface UsageDashboard {
  tenantId: string;
  billingPeriod: string;
  totalConversations: number;
  includedAllowance: number;
  remainingIncluded: number;
  packBalance: number;
  overageConversations: number;
  overageReported: number;
  usagePercent: number;
  estimatedOverageCost: number;
  activeAlerts: string[];
}

export interface DailyVolume {
  date: string;
  total: number;
  billable: number;
}

export interface ConversationSummary {
  conversationId: string;
  status: string | null;
  customerId: string | null;
  isBillable: boolean;
  messageCount: number;
  turnCount: number;
  startedAt: string | null;
  endedAt: string | null;
  agentsInvoked: string[];
  modelUsed: string | null;
  criticPassed: boolean | null;
}

export interface ConversationDetail extends ConversationSummary {
  tenantId: string;
}

export interface PaginatedList<T> {
  items: T[];
  totalCount: number;
  offset: number;
  limit: number;
}

// ---------------------------------------------------------------------------
// Conversations (Inbox)
// ---------------------------------------------------------------------------

export type ConversationStatus = 'active' | 'ended' | 'escalated' | 'idle';

export interface ConversationMessage {
  id: string;
  role: 'customer' | 'agent' | 'system';
  content: string;
  timestamp: number;
  agentName?: string;
}

export interface InboxConversation {
  id: string;
  customerId: string | null;
  customerName: string | null;
  status: ConversationStatus;
  assignedTo: string | null;
  messageCount: number;
  lastMessageAt: string | null;
  startedAt: string;
  isEscalated: boolean;
}

// ---------------------------------------------------------------------------
// Knowledge Base
// ---------------------------------------------------------------------------

export type KBArticleStatus = 'draft' | 'published' | 'archived';

export interface KBArticle {
  id: string;
  title: string;
  content: string;
  category: string;
  status: KBArticleStatus;
  createdAt: string;
  updatedAt: string;
}

// ---------------------------------------------------------------------------
// Analytics
// ---------------------------------------------------------------------------

export interface AnalyticsSummary {
  totalConversations: number;
  avgResponseTime: number;
  resolutionRate: number;
  escalationRate: number;
  customerSatisfaction: number | null;
  period: string;
}

export interface IntentBreakdown {
  intent: string;
  count: number;
  percentage: number;
}

export interface KnowledgeGap {
  query: string;
  frequency: number;
  lastSeen: string;
}

// ---------------------------------------------------------------------------
// Team
// ---------------------------------------------------------------------------

export type TeamRole = 'owner' | 'admin' | 'agent' | 'viewer';

export interface TeamMember {
  id: string;
  email: string;
  name: string;
  role: TeamRole;
  status: 'active' | 'invited' | 'disabled';
  joinedAt: string | null;
  lastActiveAt: string | null;
}

// ---------------------------------------------------------------------------
// Common component props
// ---------------------------------------------------------------------------

/** Base props that every shared component receives from the shell. */
export interface BaseComponentProps {
  tenantContext: TenantContext;
  /** API client function — shells provide their own fetch wrapper with auth. */
  apiFetch: (path: string, init?: RequestInit) => Promise<Response>;
  /** Notification callback — shells implement their own toast/banner system. */
  onNotify: (message: string, type: 'success' | 'error' | 'warning' | 'info') => void;
  /** Navigation callback — shells implement their own routing. */
  onNavigate?: (path: string) => void;
}
