// @ts-nocheck
/**
 * Vite mock API plugin - configureServer hook that intercepts /api/* requests.
 *
 * Registered only in mock mode (vite --mode mock). Intercepts all API requests
 * before they reach the Vite proxy, returning mock data from the in-memory store.
 *
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import type { Plugin, ViteDevServer } from "vite";

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
import { registerAgentHandlers } from "./handlers/agents";

let handlersRegistered = false;
function ensureHandlers(): void {
  if (handlersRegistered) return;
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
  registerAgentHandlers();
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
    name: "agent-red-mock-api",
    configureServer(server: ViteDevServer) {
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

        // SSE preview endpoint — bypasses standard JSON mock router (SPEC-1872)
        if (method === "POST" && pathname === "/api/admin/preview/chat") {
          const body = await readBody(req) as { message?: string } | undefined;
          const message = body?.message ?? "Hello";
          const convId = "preview-" + Date.now();

          res.writeHead(200, {
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            "X-Preview-Mode": "true",
            "X-Conversation-Id": convId,
            "X-Mock": "true",
          });

          // Simulate pipeline SSE events with delays
          const events = [
            `event: stage\ndata: ${JSON.stringify({ stage: "intent-classifier", status: "started" })}\n\n`,
            `event: stage\ndata: ${JSON.stringify({ stage: "knowledge-retrieval", status: "started" })}\n\n`,
            `event: stage\ndata: ${JSON.stringify({ stage: "response-generator", status: "started" })}\n\n`,
            `event: token\ndata: ${JSON.stringify({ text: "Thank you for your question" })}\n\n`,
            `event: token\ndata: ${JSON.stringify({ text: " about \"" + message.slice(0, 40) + "\"." })}\n\n`,
            `event: token\ndata: ${JSON.stringify({ text: " Based on our knowledge base, " })}\n\n`,
            `event: token\ndata: ${JSON.stringify({ text: "I can help you with that. " })}\n\n`,
            `event: token\ndata: ${JSON.stringify({ text: "This is a preview response generated in mock mode to demonstrate the streaming interface." })}\n\n`,
            `event: validated\ndata: ${JSON.stringify({ conversation_id: convId, critic_passed: true })}\n\n`,
            `event: done\ndata: ${JSON.stringify({ reason: "complete" })}\n\n`,
            `event: trace\ndata: ${JSON.stringify({ trace: { detected_intent: "general_inquiry", confidence: 0.87, route: "knowledge-retrieval", agent: "response-generator", sources: [{ title: "FAQ", relevance: 0.92 }], timing_ms: { intent: 45, kr: 120, rg: 890 } }, conversation_id: convId })}\n\n`,
          ];

          let i = 0;
          const interval = setInterval(() => {
            if (i >= events.length) {
              clearInterval(interval);
              res.end();
              return;
            }
            res.write(events[i]);
            i++;
          }, 150);

          return;
        }

        const matched = matchRoute(method, pathname);

        if (!matched) {
          // No handler registered - return 404
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

          // Add mock indicator + product version headers
          const headers: Record<string, string> = {
            "Content-Type": "application/json",
            "X-Mock": "true",
            "X-Product-Version": "1.98.65-mock",
            ...mockRes.headers,
          };

          res.writeHead(mockRes.status, headers);
          res.end(JSON.stringify(mockRes.body));
        } catch (err) {
          console.error("[mock] Handler error:", err);
          res.writeHead(500, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ detail: "Mock handler error: " + String(err) }));
        }
      });

      console.log("[mock] API mock plugin active - all /api/* requests intercepted");
    },
  };
}
