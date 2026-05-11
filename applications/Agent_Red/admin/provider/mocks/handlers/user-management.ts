// @ts-nocheck
/**
 * Mock handlers — Provider user management (platform admins).
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { GET, POST, PUT, DELETE } from '../router';
import { getStore } from '../store';
import type { MockRequest, MockResponse } from '../router';

export function registerUserManagementHandlers(): void {
  GET('/api/superadmin/platform-admin/users', (_req: MockRequest): MockResponse => {
    return { status: 200, body: { users: getStore().userManagement.users } };
  });

  POST('/api/superadmin/platform-admin/users', (req: MockRequest): MockResponse => {
    const store = getStore();
    const body = req.body as Record<string, unknown>;
    const user = {
      id: `admin-${Date.now()}`, email: body.email, role: 'operator', isSuperadmin: false,
      isActive: true, mfaEnabled: false, notificationEmail: null,
      createdAt: new Date().toISOString(), lastLoginAt: null,
    };
    store.userManagement.users.push(user);
    return { status: 201, body: user };
  });

  DELETE('/api/superadmin/platform-admin/users/:adminId', (req: MockRequest): MockResponse => {
    const store = getStore();
    const user = store.userManagement.users.find(u => u.id === req.params.adminId);
    if (!user) return { status: 404, body: { detail: 'User not found' } };
    user.isActive = false;
    return { status: 200, body: {} };
  });

  POST('/api/superadmin/platform-admin/users/backup-codes', (_req: MockRequest): MockResponse => {
    return {
      status: 200,
      body: { codes: ['A1B2C3D4', 'E5F6G7H8', 'J9K0L1M2', 'N3P4Q5R6', 'S7T8U9V0'] },
    };
  });

  PUT('/api/superadmin/platform-admin/users/notification-email', (req: MockRequest): MockResponse => {
    const body = req.body as Record<string, unknown>;
    const store = getStore();
    const admin = store.userManagement.users.find(u => u.isSuperadmin);
    if (admin) admin.notificationEmail = body.email;
    return { status: 200, body: {} };
  });

  POST('/api/superadmin/platform-admin/regenerate-key', (_req: MockRequest): MockResponse => {
    return { status: 200, body: { newKey: `ar_spa_plat_mock_${Date.now()}` } };
  });
}
