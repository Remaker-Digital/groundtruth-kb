// @ts-nocheck
/**
 * Tenant handlers - lookup, activation status, whoami, product version.
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { GET } from "../router";
import { getStore } from "../store";

export function registerTenantHandlers() {
  const s = () => getStore().tenant;

  GET("/api/tenants/lookup", () => ({
    status: 200,
    body: s().lookup,
  }));

  GET("/api/config/activation-status", () => ({
    status: 200,
    body: s().activationStatus,
  }));

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
}
