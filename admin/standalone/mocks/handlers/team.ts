// @ts-nocheck
/**
 * Team handlers - CRUD, role change, active toggle.
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { GET, POST, PUT, DELETE } from "../router";
import { getStore } from "../store";

export function registerTeamHandlers() {
  const s = () => getStore().team;

  GET("/api/admin/team", () => ({
    status: 200,
    body: { members: s().members },
  }));

  POST("/api/admin/team", (req) => {
    const body = req.body as Record<string, string>;
    const store = s();
    const newMember = {
      id: "member-" + String(store.nextId++).padStart(3, "0"),
      tenantId: "mock-tenant-001",
      email: body.email || "new@mockstore.com",
      displayName: body.display_name || body.email?.split("@")[0] || "New Member",
      role: body.role || "viewer",
      isActive: true,
      maxConcurrentConversations: 5,
      escalationCategories: [],
      userApiKeyPrefix: "ar_user_mock...",
      userApiKey: "ar_user_mock_" + Math.random().toString(36).slice(2, 18),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      lastLoginAt: null,
      invitedBy: "admin@mockstore.com",
      unresolvedEscalationCount: 0,
    };
    store.members.push(newMember);
    return { status: 201, body: newMember };
  });

  PUT("/api/admin/team/:id/role", (req) => {
    const member = s().members.find((m: { id: string }) => m.id === req.params.id);
    if (!member) return { status: 404, body: { detail: "Member not found" } };
    const body = req.body as Record<string, string>;
    member.role = body.role || member.role;
    member.updatedAt = new Date().toISOString();
    return { status: 200, body: member };
  });

  PUT("/api/admin/team/:id/active", (req) => {
    const member = s().members.find((m: { id: string }) => m.id === req.params.id);
    if (!member) return { status: 404, body: { detail: "Member not found" } };
    const body = req.body as Record<string, boolean>;
    member.isActive = body.is_active ?? !member.isActive;
    member.updatedAt = new Date().toISOString();
    return { status: 200, body: member };
  });

  DELETE("/api/admin/team/:id", (req) => {
    const store = s();
    const idx = store.members.findIndex((m: { id: string }) => m.id === req.params.id);
    if (idx === -1) return { status: 404, body: { detail: "Member not found" } };
    store.members.splice(idx, 1);
    return { status: 200, body: { success: true } };
  });
}
