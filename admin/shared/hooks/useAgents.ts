/**
 * Agent lifecycle hooks — Phase 4a (WI-4016).
 *
 * Read hooks are built on useApi<T> (GET + loading + error + refetch).
 * Write hooks use apiFetch directly and return promises.
 *
 * All paths target /api/admin/agents (tenant-admin, RBAC-protected).
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { useState, useCallback } from 'react';
import { useApi } from './useApi';
import type { ApiFetch } from './useApi';
import type {
  AgentSummary,
  AgentOverlay,
  AgentOverlayInput,
  AgentBinding,
  AgentBindingInput,
  EffectiveSkill,
  EffectiveAgentConfig,
} from '../types/agents';

// ---------------------------------------------------------------------------
// Read hooks
// ---------------------------------------------------------------------------

/** List all agents with overlay status. */
export function useAgents(apiFetch: ApiFetch) {
  return useApi<AgentSummary[]>(apiFetch, '/api/admin/agents');
}

/** Get overlay for a specific agent (404 = no overlay, data is null). */
export function useAgentOverlay(apiFetch: ApiFetch, agentId: string, enabled = true) {
  return useApi<AgentOverlay>(
    apiFetch,
    `/api/admin/agents/${encodeURIComponent(agentId)}/overlay`,
    enabled && !!agentId,
  );
}

/** List bindings for a specific agent. */
export function useAgentBindings(apiFetch: ApiFetch, agentId: string, enabled = true) {
  return useApi<AgentBinding[]>(
    apiFetch,
    `/api/admin/agents/${encodeURIComponent(agentId)}/bindings`,
    enabled && !!agentId,
  );
}

/** List available (resolved) skills, optionally filtered by agent. */
export function useAvailableSkills(apiFetch: ApiFetch, agentId?: string, enabled = true) {
  const path = agentId
    ? `/api/admin/agents/available-skills?agent_id=${encodeURIComponent(agentId)}`
    : '/api/admin/agents/available-skills';
  return useApi<EffectiveSkill[]>(apiFetch, path, enabled);
}

/** List bindable skills from the registry (for Add Binding dialog).
 *
 * Unlike useAvailableSkills, this returns ALL skills for an agent regardless
 * of binding state — solving the bootstrapping problem where an agent with
 * zero bindings has zero available skills.
 */
export function useBindableSkills(apiFetch: ApiFetch, agentId: string, enabled = true) {
  return useApi<EffectiveSkill[]>(
    apiFetch,
    `/api/admin/agents/${encodeURIComponent(agentId)}/bindable-skills`,
    enabled && !!agentId,
  );
}

/** Get resolved effective config for an agent. */
export function useEffectiveConfig(apiFetch: ApiFetch, agentId: string, enabled = true) {
  return useApi<EffectiveAgentConfig>(
    apiFetch,
    `/api/admin/agents/${encodeURIComponent(agentId)}/effective-config`,
    enabled && !!agentId,
  );
}

// ---------------------------------------------------------------------------
// Write hooks
// ---------------------------------------------------------------------------

/** Toggle agent overlay enabled state (creates overlay on first toggle). */
export function useToggleOverlay(apiFetch: ApiFetch) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const toggle = useCallback(async (agentId: string, enabled: boolean): Promise<AgentOverlay | null> => {
    setLoading(true);
    setError(null);
    try {
      const body: AgentOverlayInput = { enabled };
      const resp = await apiFetch(
        `/api/admin/agents/${encodeURIComponent(agentId)}/overlay`,
        {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        },
      );
      if (!resp.ok) {
        const text = await resp.text().catch(() => '');
        throw new Error(`${resp.status}: ${text}`);
      }
      return await resp.json();
    } catch (err: any) {
      setError(err.message || 'Toggle failed');
      return null;
    } finally {
      setLoading(false);
    }
  }, [apiFetch]);

  return { toggle, loading, error };
}

/** Create or update a skill binding. */
export function useCreateBinding(apiFetch: ApiFetch) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const create = useCallback(async (
    agentId: string,
    skillId: string,
    input: AgentBindingInput,
  ): Promise<AgentBinding | null> => {
    setLoading(true);
    setError(null);
    try {
      const resp = await apiFetch(
        `/api/admin/agents/${encodeURIComponent(agentId)}/skills/${encodeURIComponent(skillId)}/binding`,
        {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(input),
        },
      );
      if (!resp.ok) {
        const text = await resp.text().catch(() => '');
        throw new Error(`${resp.status}: ${text}`);
      }
      return await resp.json();
    } catch (err: any) {
      setError(err.message || 'Create binding failed');
      return null;
    } finally {
      setLoading(false);
    }
  }, [apiFetch]);

  return { create, loading, error };
}

/** Delete a skill binding. */
export function useDeleteBinding(apiFetch: ApiFetch) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const remove = useCallback(async (agentId: string, skillId: string): Promise<boolean> => {
    setLoading(true);
    setError(null);
    try {
      const resp = await apiFetch(
        `/api/admin/agents/${encodeURIComponent(agentId)}/skills/${encodeURIComponent(skillId)}/binding`,
        { method: 'DELETE' },
      );
      if (!resp.ok && resp.status !== 204) {
        const text = await resp.text().catch(() => '');
        throw new Error(`${resp.status}: ${text}`);
      }
      return true;
    } catch (err: any) {
      setError(err.message || 'Delete binding failed');
      return false;
    } finally {
      setLoading(false);
    }
  }, [apiFetch]);

  return { remove, loading, error };
}
