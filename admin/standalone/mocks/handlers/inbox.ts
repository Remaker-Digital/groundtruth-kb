// @ts-nocheck
/**
 * Inbox handlers - conversations, messages, search, actions.
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { GET, POST } from "../router";
import { getStore } from "../store";

export function registerInboxHandlers() {
  const s = () => getStore().inbox;

  GET("/api/admin/conversations", (req) => {
    let convs = s().conversations;
    if (req.query.archived === "only") {
      convs = convs.filter((c: { archivedAt: string | null }) => c.archivedAt !== null);
    } else if (req.query.archived !== "include") {
      convs = convs.filter((c: { archivedAt: string | null }) => c.archivedAt === null);
    }
    return { status: 200, body: { conversations: convs } };
  });

  GET("/api/admin/conversations/:id", (req) => {
    const conv = s().conversations.find((c: { conversationId: string }) => c.conversationId === req.params.id);
    if (!conv) return { status: 404, body: { detail: "Conversation not found" } };
    return { status: 200, body: conv };
  });

  GET("/api/admin/conversations/:id/messages", (req) => {
    const messages = s().messages[req.params.id] || [];
    return { status: 200, body: { messages } };
  });

  GET("/api/admin/conversations/:id/trace", (req) => {
    return {
      status: 200,
      body: {
        traceId: "trace-" + req.params.id,
        stages: [
          { stage: "intent_classification", elapsedMs: 45, succeeded: true },
          { stage: "knowledge_retrieval", elapsedMs: 120, succeeded: true },
          { stage: "response_generation", elapsedMs: 850, succeeded: true },
          { stage: "critic_review", elapsedMs: 200, succeeded: true },
        ],
        totalLatencyMs: 1215,
        intent: "customer_service",
        confidence: 0.94,
        criticPassed: true,
        modelUsed: "gpt-4o",
      },
    };
  });

  POST("/api/admin/conversations/search", (req) => {
    const body = req.body as Record<string, string>;
    const query = (body.query || "").toLowerCase();
    const results = s().conversations
      .filter((c: { customerName: string | null; conversationId: string }) =>
        (c.customerName || "").toLowerCase().includes(query) ||
        c.conversationId.includes(query)
      )
      .map((c: { conversationId: string; customerId: string | null; customerName: string | null; status: string | null; startedAt: string | null; lastActivityAt: string | null; messageCount: number }) => ({
        conversation_id: c.conversationId,
        customer_id: c.customerId,
        customer_name: c.customerName,
        status: c.status,
        started_at: c.startedAt,
        last_activity_at: c.lastActivityAt,
        message_count: c.messageCount,
        snippet: "Matched conversation",
        matched_in: "customer_name",
      }));
    return { status: 200, body: { results } };
  });

  POST("/api/admin/conversations/:id/resolve", () => ({
    status: 200,
    body: { success: true, message: "Conversation resolved" },
  }));

  POST("/api/admin/conversations/:id/escalate", () => ({
    status: 200,
    body: { success: true, message: "Conversation escalated" },
  }));

  POST("/api/admin/conversations/:id/archive", () => ({
    status: 200,
    body: { success: true, message: "Conversation archived" },
  }));

  POST("/api/admin/conversations/:id/unarchive", () => ({
    status: 200,
    body: { success: true, message: "Conversation unarchived" },
  }));

  POST("/api/admin/conversations/:id/assign", () => ({
    status: 200,
    body: { success: true },
  }));
}
