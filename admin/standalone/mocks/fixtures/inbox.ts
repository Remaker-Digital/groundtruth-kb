// @ts-nocheck
/**
 * Inbox fixture - conversations with messages, customer info, pipeline traces.
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

export function createInboxFixture() {
  const conversations = [
    {
      conversationId: "conv-001", customerId: "cust-101", customerName: "Emily Watson",
      status: "active", assignedTo: null, messageCount: 6, turnCount: 3,
      startedAt: "2026-03-10T08:30:00Z", endedAt: null, lastActivityAt: "2026-03-10T09:15:00Z",
      isBillable: true, agentsInvoked: ["CustomerServiceAgent"], modelUsed: "gpt-4o",
      criticPassed: true, escalationCategory: null, archivedAt: null,
      customerVerified: true, identityEmail: "emily@example.com", pipelineTrace: null,
    },
    {
      conversationId: "conv-002", customerId: "cust-102", customerName: "Marcus Johnson",
      status: "escalated", assignedTo: "member-003", messageCount: 12, turnCount: 6,
      startedAt: "2026-03-09T14:20:00Z", endedAt: null, lastActivityAt: "2026-03-09T16:45:00Z",
      isBillable: true, agentsInvoked: ["CustomerServiceAgent", "EscalationAgent"], modelUsed: "gpt-4o",
      criticPassed: false, escalationCategory: "technical", archivedAt: null,
      customerVerified: true, identityEmail: "marcus@example.com", pipelineTrace: null,
    },
    {
      conversationId: "conv-003", customerId: "cust-103", customerName: "Sophie Chen",
      status: "resolved", assignedTo: null, messageCount: 8, turnCount: 4,
      startedAt: "2026-03-08T10:00:00Z", endedAt: "2026-03-08T10:15:00Z",
      lastActivityAt: "2026-03-08T10:15:00Z",
      isBillable: true, agentsInvoked: ["OrderStatusAgent"], modelUsed: "gpt-4o",
      criticPassed: true, escalationCategory: null, archivedAt: null,
      customerVerified: false, identityEmail: null, pipelineTrace: null,
    },
    {
      conversationId: "conv-004", customerId: "cust-104", customerName: "David Park",
      status: "resolved", assignedTo: null, messageCount: 4, turnCount: 2,
      startedAt: "2026-03-07T16:00:00Z", endedAt: "2026-03-07T16:08:00Z",
      lastActivityAt: "2026-03-07T16:08:00Z",
      isBillable: true, agentsInvoked: ["ReturnRefundAgent"], modelUsed: "gpt-4o",
      criticPassed: true, escalationCategory: null, archivedAt: null,
      customerVerified: true, identityEmail: "david.park@example.com", pipelineTrace: null,
    },
    {
      conversationId: "conv-005", customerId: "cust-105", customerName: "Aisha Patel",
      status: "active", assignedTo: null, messageCount: 3, turnCount: 1,
      startedAt: "2026-03-10T09:00:00Z", endedAt: null, lastActivityAt: "2026-03-10T09:05:00Z",
      isBillable: true, agentsInvoked: ["ProductRecommendationAgent"], modelUsed: "gpt-4o",
      criticPassed: true, escalationCategory: null, archivedAt: null,
      customerVerified: false, identityEmail: null, pipelineTrace: null,
    },
  ];

  const messages: Record<string, Array<{ messageId: string; role: string; content: string; timestamp: string; metadata: null }>> = {
    "conv-001": [
      { messageId: "msg-001-1", role: "customer", content: "Hi, I need help with my recent order #1234.", timestamp: "2026-03-10T08:30:00Z", metadata: null },
      { messageId: "msg-001-2", role: "ai", content: "Hello Emily! I would be happy to help you with order #1234. Let me look that up. Your order was placed on March 8th and is being prepared for shipment.", timestamp: "2026-03-10T08:30:02Z", metadata: null },
      { messageId: "msg-001-3", role: "customer", content: "Can I change the shipping address?", timestamp: "2026-03-10T08:31:00Z", metadata: null },
      { messageId: "msg-001-4", role: "ai", content: "Since your order has not shipped yet, I can help you update the shipping address. Could you please provide the new address?", timestamp: "2026-03-10T08:31:02Z", metadata: null },
    ],
    "conv-002": [
      { messageId: "msg-002-1", role: "customer", content: "Your API integration is broken! I keep getting 500 errors.", timestamp: "2026-03-09T14:20:00Z", metadata: null },
      { messageId: "msg-002-2", role: "ai", content: "I am sorry to hear about the API issues. Can you tell me which endpoint you are calling and share the error response?", timestamp: "2026-03-09T14:20:03Z", metadata: null },
      { messageId: "msg-002-3", role: "system", content: "Conversation escalated to technical support (agent: Alex Rivera)", timestamp: "2026-03-09T14:25:05Z", metadata: null },
      { messageId: "msg-002-4", role: "human_agent", content: "Hi Marcus, I am Alex from the technical team. I am looking into the 500 errors now.", timestamp: "2026-03-09T14:35:00Z", metadata: null },
    ],
  };

  return { conversations, messages };
}
