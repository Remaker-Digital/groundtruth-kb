// @ts-nocheck
/**
 * Provider user management fixture — platform admin users.
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
export function createUserManagementFixture() {
  return {
    users: [
      { id: "admin-001", email: "admin@remaker.digital", role: "superadmin", isSuperadmin: true, isActive: true, mfaEnabled: true, notificationEmail: "ops@remaker.digital", createdAt: "2025-09-01T10:00:00Z", lastLoginAt: "2026-03-11T08:00:00Z" },
      { id: "admin-002", email: "ops@remaker.digital", role: "operator", isSuperadmin: false, isActive: true, mfaEnabled: false, notificationEmail: null, createdAt: "2025-11-15T14:00:00Z", lastLoginAt: "2026-03-10T16:30:00Z" },
      { id: "admin-003", email: "support@remaker.digital", role: "operator", isSuperadmin: false, isActive: false, mfaEnabled: false, notificationEmail: null, createdAt: "2026-01-10T09:00:00Z", lastLoginAt: "2026-02-15T11:00:00Z" },
    ],
    mfaStatus: { mfaEnabled: false },
  };
}
