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
  hasStripeBilling: boolean;
  shopDomain?: string;
}

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------

export type ConfigFieldType = 'string' | 'number' | 'integer' | 'float' | 'boolean' | 'select' | 'textarea' | 'color' | 'json' | 'object';

/** Validation constraints for a config field. */
export interface ValidationRule {
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  minValue?: number;
  maxValue?: number;
  pattern?: string;
  allowedValues?: string[];
  maxItems?: number;
}

export interface ConfigField {
  key: string;
  label: string;
  description: string;
  /** Short hover tooltip (1-2 sentences). */
  tooltip?: string;
  /** Link to relevant documentation page. */
  docLink?: string;
  type: ConfigFieldType;
  defaultValue: unknown;
  currentValue: unknown;
  options?: Array<{ value: string; label: string }>;
  tierGate?: TenantTier;
  stepOrder: number;
  group: string;
  /** Validation constraints from the backend config schema. */
  validation?: ValidationRule;
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
  | 'mode_selection'
  | 'team'
  | 'ai_behavior'
  | 'knowledge_base'
  | 'quick_actions'
  | 'widget_appearance'
  | 'integrations'
  | 'go_live'
  // Legacy keys — retained for review summary grouping and backward compatibility
  | 'brand_and_tone'
  | 'escalation'
  | 'response_policies'
  | 'customer_memory'
  | 'notifications';

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

export type ConversationStatus = 'active' | 'ended' | 'escalated' | 'resolved' | 'timed_out' | 'error';

export interface ConversationMessage {
  messageId: string | null;
  role: 'customer' | 'agent' | 'system';
  content: string;
  timestamp: string | null;
  metadata?: Record<string, unknown> | null;
}

export interface InboxConversation {
  conversationId: string;
  customerId: string | null;
  customerName: string | null;
  status: string | null;
  assignedTo: string | null;
  messageCount: number;
  turnCount: number;
  startedAt: string | null;
  endedAt: string | null;
  lastActivityAt: string | null;
  isBillable: boolean;
  agentsInvoked: string[];
  modelUsed: string | null;
  criticPassed: boolean | null;
  escalationCategory: string | null;
  archivedAt: string | null;
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
  entryType?: string;
  is_active?: boolean;
  createdAt: string;
  updatedAt: string;
  sourceType?: string;
  sourceFilename?: string;
  sourceUrl?: string;
  chunkIndex?: number | null;
  parentEntryId?: string | null;
  stalenessScore?: number | null;
  stalenessCategory?: string | null;
  lastVerifiedAt?: string | null;
  embeddedAt?: string | null;
}

export interface KBUploadResult {
  source_type: string;
  source_filename?: string;
  source_url?: string;
  entries_created: number;
  total_chars: number;
  entry_ids: string[];
  parent_entry_id?: string | null;
}

// ---------------------------------------------------------------------------
// Analytics
// ---------------------------------------------------------------------------

export interface AnalyticsSummary {
  tenantId: string;
  since: string;
  until: string;
  totalConversations: number;
  billableConversations: number;
  avgTurns: number;
  avgMessages: number;
  avgResponseTime: number | null;
  resolutionRate: number | null;
  customerSatisfaction: number | null;
  statusBreakdown: Array<{ status: string; count: number }>;
  escalationCount: number;
  escalationRate: number;
  criticPassed: number;
  criticFailed: number;
  criticPassRate: number;
}

export interface IntentBreakdown {
  agent: string;
  invocationCount: number;
  percentage: number;
}

export interface KnowledgeGap {
  conversationId: string;
  status: string;
  customerId: string | null;
  turnCount: number;
  messageCount: number;
  agentsInvoked: string[];
  criticPassed: boolean | null;
  startedAt: string | null;
  endedAt: string | null;
}

// ---------------------------------------------------------------------------
// Team
// ---------------------------------------------------------------------------

export type TeamRole = 'superadmin' | 'admin' | 'escalation_agent' | 'viewer';

export interface TeamMember {
  id: string;
  tenantId: string;
  email: string;
  displayName: string;
  role: string;
  isActive: boolean;
  maxConcurrentConversations: number;
  /** Escalation categories this agent handles (WI #279). Only relevant for role = 'escalation_agent'. */
  escalationCategories?: string[];
  /** API key prefix for display (ar_user_rema...). Never the full key. */
  userApiKeyPrefix?: string | null;
  /** Full API key — only returned ONCE on creation or rotation. */
  userApiKey?: string | null;
  createdAt: string;
  updatedAt: string;
  lastLoginAt: string | null;
  invitedBy: string | null;
  unresolvedEscalationCount?: number;
}

/** Escalation category definition — shared between Configuration and Team pages (WI #279). */
export interface EscalationCategoryDef {
  id: string;
  label: string;
  description: string;
}

/** Standard escalation categories — same list used in Configuration and Team management. */
export const ESCALATION_CATEGORIES: EscalationCategoryDef[] = [
  { id: 'sales', label: 'Sales', description: 'Purchase decisions, pricing questions, product comparisons' },
  { id: 'support', label: 'Support', description: 'Product issues, troubleshooting, how-to questions' },
  { id: 'service', label: 'Service', description: 'Returns, refunds, exchanges, order modifications' },
  { id: 'account', label: 'Account', description: 'Account access, billing, subscription management' },
  { id: 'technical', label: 'Technical assistance', description: 'Integration issues, API questions, advanced configuration' },
  { id: 'general', label: 'General inquiry', description: 'Complaints, legal, safety, or anything not matching other categories' },
];

// ---------------------------------------------------------------------------
// Integrations (C10)
// ---------------------------------------------------------------------------

export type IntegrationType = 'shopify' | 'zendesk' | 'mailchimp' | 'google_analytics';
export type IntegrationStatus = 'connected' | 'disconnected' | 'error' | null;

export interface IntegrationSummary {
  type: IntegrationType;
  name: string;
  description: string;
  icon: string;
  enabled: boolean;
  status: IntegrationStatus;
  tierGate: string | null;
  tierMet: boolean;
  comingSoon: boolean;
}

export interface IntegrationDetail extends IntegrationSummary {
  configFields: Array<{ key: string; label: string; type: string }>;
}

export interface IntegrationResponse {
  success: boolean;
  message: string;
  integration: IntegrationSummary | null;
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
