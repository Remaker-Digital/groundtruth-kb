// @ts-nocheck
/**
 * Vite mock API plugin — Provider admin console.
 *
 * Intercepts /api/superadmin/* requests in mock mode, returning fixture data.
 * Same architecture as standalone mock plugin.
 *
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import type { Plugin, ViteDevServer } from "vite";

import { registerDashboardHandlers } from "./handlers/dashboard";
import { registerTenantHandlers } from "./handlers/tenants";
import { registerAlertHandlers } from "./handlers/alerts";
import { registerIncidentHandlers } from "./handlers/incidents";
import { registerCopilotHandlers } from "./handlers/copilot";
import { registerPipelineHandlers } from "./handlers/pipeline";
import { registerContactHandlers } from "./handlers/contact-messages";
import { registerServiceMessageHandlers } from "./handlers/service-messages";
import { registerUserManagementHandlers } from "./handlers/user-management";
import { registerOperationsHandlers } from "./handlers/operations";
import { registerComplianceHandlers } from "./handlers/compliance";
import { registerMfaHandlers } from "./handlers/mfa";

let handlersRegistered = false;
function ensureHandlers(): void {
  if (handlersRegistered) return;
  registerDashboardHandlers();
  registerTenantHandlers();
  registerAlertHandlers();
  registerIncidentHandlers();
  registerCopilotHandlers();
  registerPipelineHandlers();
  registerContactHandlers();
  registerServiceMessageHandlers();
  registerUserManagementHandlers();
  registerOperationsHandlers();
  registerComplianceHandlers();
  registerMfaHandlers();
  handlersRegistered = true;
}

import { matchRoute } from "./router";
import type { MockRequest } from "./router";

/** Collect request body from Node IncomingMessage. */
function readBody(req: import("http").IncomingMessage): Promise<unknown> {
  return new Promise((resolve) => {
    const chunks: Buffer[] = [];
    req.on("data", (chunk: Buffer) => chunks.push(chunk));
    req.on("end", () => {
      const raw = Buffer.concat(chunks).toString("utf-8");
      if (!raw) { resolve(undefined); return; }
      try { resolve(JSON.parse(raw)); } catch { resolve(raw); }
    });
    req.on("error", () => resolve(undefined));
  });
}

/** Parse URL query string into a Record. */
function parseQuery(url: string): Record<string, string> {
  const idx = url.indexOf("?");
  if (idx === -1) return {};
  const params = new URLSearchParams(url.slice(idx + 1));
  const result: Record<string, string> = {};
  params.forEach((v, k) => { result[k] = v; });
  return result;
}

export function mockApiPlugin(): Plugin {
  return {
    name: "agent-red-provider-mock-api",
    configureServer(server: ViteDevServer) {
      ensureHandlers();

      server.middlewares.use(async (req, res, next) => {
        const url = req.url || "/";
        const pathname = url.split("?")[0];

        if (!pathname.startsWith("/api/") && pathname !== "/api") {
          next();
          return;
        }

        const method = (req.method || "GET").toUpperCase();
        const matched = matchRoute(method, pathname);

        if (!matched) {
          res.writeHead(404, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ detail: "Mock endpoint not registered: " + method + " " + pathname }));
          return;
        }

        try {
          const body = method !== "GET" ? await readBody(req) : undefined;
          const mockReq: MockRequest = {
            method,
            path: pathname,
            params: matched.params,
            query: parseQuery(url),
            body,
          };

          const mockRes = await matched.handler(mockReq);

          const headers: Record<string, string> = {
            "Content-Type": "application/json",
            "X-Mock": "true",
            "X-Product-Version": "1.82.0-mock",
            ...mockRes.headers,
          };

          res.writeHead(mockRes.status, headers);
          res.end(JSON.stringify(mockRes.body));
        } catch (err) {
          console.error("[mock-provider] Handler error:", err);
          res.writeHead(500, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ detail: "Mock handler error: " + String(err) }));
        }
      });

      console.log("[mock-provider] API mock plugin active — all /api/* requests intercepted");
    },
  };
}
