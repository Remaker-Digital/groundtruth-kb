// @ts-nocheck
/**
 * Agent handlers — overlay CRUD, binding CRUD, effective config, available skills.
 *
 * Routes match /api/admin/agents (tenant-admin surface, Phase 4a).
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { GET, PUT, DELETE } from "../router";
import { getStore } from "../store";

export function registerAgentHandlers() {
  const s = () => getStore().agents;

  // GET /api/admin/agents — list agents with overlay status
  GET("/api/admin/agents", () => ({
    status: 200,
    body: s().agents,
  }));

  // GET /api/admin/agents/:aid/overlay
  GET("/api/admin/agents/:aid/overlay", (req) => {
    const overlay = s().overlays[req.params.aid];
    if (!overlay) return { status: 404, body: { detail: "No overlay for this agent" } };
    return { status: 200, body: overlay };
  });

  // PUT /api/admin/agents/:aid/overlay
  PUT("/api/admin/agents/:aid/overlay", (req) => {
    const { aid } = req.params;
    const body = req.body as Record<string, any>;
    const now = new Date().toISOString();

    const existing = s().overlays[aid] || {
      agentId: aid,
      promptOverrides: {},
      skillOverrides: {},
      customMetadata: {},
    };

    const updated = {
      ...existing,
      enabled: body.enabled ?? existing.enabled ?? true,
      promptOverrides: body.promptOverrides ?? existing.promptOverrides,
      skillOverrides: body.skillOverrides ?? existing.skillOverrides,
      customMetadata: body.customMetadata ?? existing.customMetadata,
      updatedAt: now,
    };

    s().overlays[aid] = updated;

    // Update agent summary
    const agent = s().agents.find((a: any) => a.agentId === aid);
    if (agent) {
      agent.hasOverlay = true;
      agent.enabled = updated.enabled;
    }

    return { status: 200, body: updated };
  });

  // DELETE /api/admin/agents/:aid/overlay
  DELETE("/api/admin/agents/:aid/overlay", (req) => {
    const { aid } = req.params;
    if (!s().overlays[aid]) return { status: 404, body: { detail: "No overlay for this agent" } };
    delete s().overlays[aid];

    const agent = s().agents.find((a: any) => a.agentId === aid);
    if (agent) {
      agent.hasOverlay = false;
      agent.enabled = true;
    }

    return { status: 204, body: null };
  });

  // GET /api/admin/agents/:aid/effective-config
  GET("/api/admin/agents/:aid/effective-config", (req) => {
    const { aid } = req.params;
    const agent = s().agents.find((a: any) => a.agentId === aid);
    if (!agent) return { status: 404, body: { detail: `Unknown agent: ${aid}` } };

    const overlay = s().overlays[aid];
    const agentBindings = s().bindings.filter((b: any) => b.agentId === aid);
    const skills = agentBindings.map((b: any) => {
      const avail = s().availableSkills.find((sk: any) => sk.skillId === b.skillId);
      return {
        skillId: b.skillId,
        displayName: avail?.displayName || b.skillId,
        mode: b.mode,
        enabled: b.enabled,
        credentialRef: b.credentialRef,
      };
    });

    return {
      status: 200,
      body: {
        agentId: agent.agentId,
        displayName: agent.displayName,
        agentKind: agent.agentKind,
        enabled: overlay?.enabled ?? agent.enabled,
        promptOverrides: overlay?.promptOverrides || {},
        skills,
      },
    };
  });

  // GET /api/admin/agents/:aid/bindings
  GET("/api/admin/agents/:aid/bindings", (req) => {
    const { aid } = req.params;
    const bindings = s().bindings.filter((b: any) => b.agentId === aid);
    return { status: 200, body: bindings };
  });

  // GET /api/admin/agents/:aid/skills/:sid/binding
  GET("/api/admin/agents/:aid/skills/:sid/binding", (req) => {
    const { aid, sid } = req.params;
    const binding = s().bindings.find((b: any) => b.agentId === aid && b.skillId === sid);
    if (!binding) return { status: 404, body: { detail: "No binding found" } };
    return { status: 200, body: binding };
  });

  // PUT /api/admin/agents/:aid/skills/:sid/binding
  PUT("/api/admin/agents/:aid/skills/:sid/binding", (req) => {
    const { aid, sid } = req.params;
    const body = req.body as Record<string, any>;

    const idx = s().bindings.findIndex((b: any) => b.agentId === aid && b.skillId === sid);
    const binding = {
      agentId: aid,
      skillId: sid,
      credentialRef: body.credentialRef ?? null,
      mode: body.mode ?? "read",
      approvalPolicy: body.approvalPolicy ?? "auto",
      enabled: body.enabled ?? true,
    };

    if (idx >= 0) {
      s().bindings[idx] = binding;
    } else {
      s().bindings.push(binding);
    }

    return { status: 200, body: binding };
  });

  // DELETE /api/admin/agents/:aid/skills/:sid/binding
  DELETE("/api/admin/agents/:aid/skills/:sid/binding", (req) => {
    const { aid, sid } = req.params;
    const idx = s().bindings.findIndex((b: any) => b.agentId === aid && b.skillId === sid);
    if (idx < 0) return { status: 404, body: { detail: "No binding found" } };
    s().bindings.splice(idx, 1);
    return { status: 204, body: null };
  });

  // GET /api/admin/agents/available-skills
  GET("/api/admin/agents/available-skills", (req) => {
    const agentId = req.query.agent_id;
    let skills = s().availableSkills;
    if (agentId) {
      skills = skills.filter((sk: any) => sk.skillId.startsWith(agentId + ':'));
    }
    return { status: 200, body: skills };
  });
}
