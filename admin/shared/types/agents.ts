/**
 * Agent lifecycle types — Phase 4a (WI-4016).
 *
 * All interfaces match the backend CamelCaseModel wire format exactly.
 * Field names are camelCase as received from the API.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

// ---------------------------------------------------------------------------
// Agent Summary (from GET /api/admin/agents)
// ---------------------------------------------------------------------------

export interface AgentSummary {
  agentId: string;
  displayName: string;
  description: string;
  agentKind: string;
  category: string;
  hasOverlay: boolean;
  enabled: boolean;
}

// ---------------------------------------------------------------------------
// Overlay (from GET /api/admin/agents/{id}/overlay)
// ---------------------------------------------------------------------------

export interface SkillOverride {
  enabled: boolean;
  modeOverride: string | null;
  credentialRef: string | null;
}

export interface AgentOverlay {
  agentId: string;
  enabled: boolean;
  promptOverrides: Record<string, string>;
  skillOverrides: Record<string, SkillOverride>;
  customMetadata: Record<string, unknown>;
  visibilityScope: string;
  staffDomainTags: string[];
  updatedAt: string;
}

export interface AgentOverlayInput {
  enabled: boolean;
  promptOverrides?: Record<string, string>;
  skillOverrides?: Record<string, SkillOverride>;
  customMetadata?: Record<string, unknown>;
  visibilityScope?: string;
  staffDomainTags?: string[];
}

// ---------------------------------------------------------------------------
// Binding (from GET /api/admin/agents/{id}/bindings)
// ---------------------------------------------------------------------------

export interface AgentBinding {
  agentId: string;
  skillId: string;
  credentialRef: string | null;
  mode: string;
  approvalPolicy: string;
  enabled: boolean;
}

export interface AgentBindingInput {
  credentialRef?: string | null;
  mode?: string;
  approvalPolicy?: string;
  enabled?: boolean;
}

// ---------------------------------------------------------------------------
// Effective Config (from GET /api/admin/agents/{id}/effective-config)
// ---------------------------------------------------------------------------

export interface EffectiveSkill {
  skillId: string;
  displayName: string;
  description: string;
  mode: string;
  enabled: boolean;
  credentialRef: string | null;
}

export interface EffectiveAgentConfig {
  agentId: string;
  displayName: string;
  agentKind: string;
  enabled: boolean;
  promptOverrides: Record<string, string>;
  skills: EffectiveSkill[];
}
