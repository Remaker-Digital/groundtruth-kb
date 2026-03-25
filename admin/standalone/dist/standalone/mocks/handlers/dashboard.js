// @ts-nocheck
/**
 * Dashboard / Analytics handlers.
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { GET } from "../router";
import { getStore } from "../store";
export function registerDashboardHandlers() {
    const s = () => getStore().dashboard;
    GET("/api/dashboard/usage", () => ({ status: 200, body: s().usage }));
    GET("/api/dashboard/usage/daily", () => ({ status: 200, body: s().daily }));
    GET("/api/dashboard/conversations", () => ({ status: 200, body: s().conversations }));
    GET("/api/analytics/summary", () => ({ status: 200, body: s().summary }));
    GET("/api/analytics/intents", () => ({ status: 200, body: s().intents }));
    GET("/api/analytics/gaps", () => ({ status: 200, body: s().gaps }));
}
//# sourceMappingURL=dashboard.js.map