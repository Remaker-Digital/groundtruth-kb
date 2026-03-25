// @ts-nocheck
/**
 * Vite mock API plugin - configureServer hook that intercepts /api/* requests.
 *
 * Registered only in mock mode (vite --mode mock). Intercepts all API requests
 * before they reach the Vite proxy, returning mock data from the in-memory store.
 *
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
// Inline handler registration to avoid circular import (index.ts re-exports plugin)
import { registerTenantHandlers } from "./handlers/tenant";
import { registerDashboardHandlers } from "./handlers/dashboard";
import { registerTeamHandlers } from "./handlers/team";
import { registerInboxHandlers } from "./handlers/inbox";
import { registerConfigHandlers } from "./handlers/config";
import { registerKnowledgeHandlers } from "./handlers/knowledge";
import { registerQuickActionHandlers } from "./handlers/quick-actions";
import { registerWidgetHandlers } from "./handlers/widget";
import { registerBillingHandlers } from "./handlers/billing";
import { registerMemoryHandlers } from "./handlers/memory";
import { registerIntegrationHandlers } from "./handlers/integrations";
let handlersRegistered = false;
function ensureHandlers() {
    if (handlersRegistered)
        return;
    registerTenantHandlers();
    registerDashboardHandlers();
    registerTeamHandlers();
    registerInboxHandlers();
    registerConfigHandlers();
    registerKnowledgeHandlers();
    registerQuickActionHandlers();
    registerWidgetHandlers();
    registerBillingHandlers();
    registerMemoryHandlers();
    registerIntegrationHandlers();
    handlersRegistered = true;
}
import { matchRoute } from "./router";
/** Collect request body from Node IncomingMessage. */
function readBody(req) {
    return new Promise((resolve) => {
        const chunks = [];
        req.on("data", (chunk) => chunks.push(chunk));
        req.on("end", () => {
            const raw = Buffer.concat(chunks).toString("utf-8");
            if (!raw) {
                resolve(undefined);
                return;
            }
            try {
                resolve(JSON.parse(raw));
            }
            catch {
                resolve(raw);
            }
        });
        req.on("error", () => resolve(undefined));
    });
}
/** Parse URL query string into a Record. */
function parseQuery(url) {
    const idx = url.indexOf("?");
    if (idx === -1)
        return {};
    const params = new URLSearchParams(url.slice(idx + 1));
    const result = {};
    params.forEach((v, k) => { result[k] = v; });
    return result;
}
export function mockApiPlugin() {
    return {
        name: "agent-red-mock-api",
        configureServer(server) {
            // Register all mock handlers on first server start
            ensureHandlers();
            // Use server.middlewares (Connect instance) to add middleware BEFORE Vite internals
            server.middlewares.use(async (req, res, next) => {
                const url = req.url || "/";
                const pathname = url.split("?")[0];
                // Only intercept /api/* requests
                if (!pathname.startsWith("/api/") && pathname !== "/api") {
                    next();
                    return;
                }
                const method = (req.method || "GET").toUpperCase();
                const matched = matchRoute(method, pathname);
                if (!matched) {
                    // No handler registered - return 404
                    res.writeHead(404, { "Content-Type": "application/json" });
                    res.end(JSON.stringify({ detail: "Mock endpoint not registered: " + method + " " + pathname }));
                    return;
                }
                try {
                    const body = method !== "GET" ? await readBody(req) : undefined;
                    const mockReq = {
                        method,
                        path: pathname,
                        params: matched.params,
                        query: parseQuery(url),
                        body,
                    };
                    const mockRes = await matched.handler(mockReq);
                    // Add mock indicator + product version headers
                    const headers = {
                        "Content-Type": "application/json",
                        "X-Mock": "true",
                        "X-Product-Version": "1.82.0-mock",
                        ...mockRes.headers,
                    };
                    res.writeHead(mockRes.status, headers);
                    res.end(JSON.stringify(mockRes.body));
                }
                catch (err) {
                    console.error("[mock] Handler error:", err);
                    res.writeHead(500, { "Content-Type": "application/json" });
                    res.end(JSON.stringify({ detail: "Mock handler error: " + String(err) }));
                }
            });
            console.log("[mock] API mock plugin active - all /api/* requests intercepted");
        },
    };
}
//# sourceMappingURL=plugin.js.map