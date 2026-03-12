// @ts-nocheck
/**
 * Tenant handlers - lookup, activation status, whoami, product version.
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { GET, POST } from "../router";
import { getStore, resetStore } from "../store";

export function registerTenantHandlers() {
  const s = () => getStore().tenant;

  GET("/api/tenants/lookup", () => ({
    status: 200,
    body: s().lookup,
  }));

  // activation-status is registered in config.ts (authoritative handler for config store)

  GET("/api/admin/team/whoami", () => ({
    status: 200,
    body: s().whoami,
  }));

  GET("/api/admin/product-version", () => ({
    status: 200,
    body: { version: s().productVersion },
  }));

  GET("/api/health", () => ({
    status: 200,
    body: { status: "healthy", product_version: s().productVersion },
  }));

  // Test-only: reset store to initial fixture state (used by e2e_mock tests)
  POST("/api/__test__/reset", () => {
    resetStore();
    return { status: 200, body: { success: true, message: "Store reset to fixture data" } };
  });
}
