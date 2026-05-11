// @ts-nocheck
/**
 * Inbox fixture - conversations with messages, customer info, pipeline traces.
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

export function createInboxFixture() {
  const conversations = [
    {
      conversationId: "conv-001", customerId: "cust-101", customerName: "Emily Watson",
      status: "active", assignedTo: null, messageCount: 4, turnCount: 2,
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
      { messageId: "msg-002-5", role: "customer", content: "It's the /api/orders endpoint. I get a 500 with no body.", timestamp: "2026-03-09T14:40:00Z", metadata: null },
      { messageId: "msg-002-6", role: "human_agent", content: "Thanks Marcus. I can see the issue in our logs — there was a database timeout. We're deploying a fix now.", timestamp: "2026-03-09T14:50:00Z", metadata: null },
      { messageId: "msg-002-7", role: "customer", content: "Any idea on the ETA?", timestamp: "2026-03-09T15:00:00Z", metadata: null },
      { messageId: "msg-002-8", role: "human_agent", content: "Should be resolved within the next 30 minutes. I'll follow up.", timestamp: "2026-03-09T15:05:00Z", metadata: null },
      { messageId: "msg-002-9", role: "customer", content: "OK I'll check again in half an hour. Thanks.", timestamp: "2026-03-09T15:10:00Z", metadata: null },
      { messageId: "msg-002-10", role: "human_agent", content: "The fix has been deployed. Could you try again?", timestamp: "2026-03-09T16:00:00Z", metadata: null },
      { messageId: "msg-002-11", role: "customer", content: "It's working now, thank you!", timestamp: "2026-03-09T16:30:00Z", metadata: null },
      { messageId: "msg-002-12", role: "human_agent", content: "Great to hear! I'll close this out. Don't hesitate to reach out if you hit any other issues.", timestamp: "2026-03-09T16:45:00Z", metadata: null },
    ],
    "conv-003": [
      { messageId: "msg-003-1", role: "customer", content: "What's the status of my order #5678?", timestamp: "2026-03-08T10:00:00Z", metadata: null },
      { messageId: "msg-003-2", role: "ai", content: "Let me check on order #5678 for you. It was shipped on March 7th via FedEx and is currently in transit.", timestamp: "2026-03-08T10:00:03Z", metadata: null },
      { messageId: "msg-003-3", role: "customer", content: "Do you have a tracking number?", timestamp: "2026-03-08T10:02:00Z", metadata: null },
      { messageId: "msg-003-4", role: "ai", content: "Yes! Your tracking number is FX-789012345. You can track it on the FedEx website. It's expected to arrive by March 10th.", timestamp: "2026-03-08T10:02:03Z", metadata: null },
      { messageId: "msg-003-5", role: "customer", content: "Perfect, thanks!", timestamp: "2026-03-08T10:05:00Z", metadata: null },
      { messageId: "msg-003-6", role: "ai", content: "You're welcome, Sophie! Is there anything else I can help with?", timestamp: "2026-03-08T10:05:02Z", metadata: null },
      { messageId: "msg-003-7", role: "customer", content: "No that's all, have a good day!", timestamp: "2026-03-08T10:10:00Z", metadata: null },
      { messageId: "msg-003-8", role: "ai", content: "You too! Don't hesitate to reach out if you need anything else.", timestamp: "2026-03-08T10:10:02Z", metadata: null },
    ],
    "conv-004": [
      { messageId: "msg-004-1", role: "customer", content: "I'd like to return the headphones I purchased last week.", timestamp: "2026-03-07T16:00:00Z", metadata: null },
      { messageId: "msg-004-2", role: "ai", content: "Of course, I can help with that return. Could you provide the order number?", timestamp: "2026-03-07T16:00:03Z", metadata: null },
      { messageId: "msg-004-3", role: "customer", content: "Order #3456. They don't fit comfortably.", timestamp: "2026-03-07T16:03:00Z", metadata: null },
      { messageId: "msg-004-4", role: "ai", content: "I've initiated the return for order #3456. You'll receive a return shipping label at david.park@example.com within the next hour. Once we receive the item, your refund will be processed within 3-5 business days.", timestamp: "2026-03-07T16:03:05Z", metadata: null },
    ],
    "conv-005": [
      { messageId: "msg-005-1", role: "customer", content: "Hi, I'm looking for a good laptop for graphic design work. Any recommendations?", timestamp: "2026-03-10T09:00:00Z", metadata: null },
      { messageId: "msg-005-2", role: "ai", content: "Great question! For graphic design, I'd recommend looking at our MacBook Pro 16-inch or the Dell XPS 15. Both have excellent color-accurate displays and powerful GPUs. What's your budget range?", timestamp: "2026-03-10T09:00:04Z", metadata: null },
      { messageId: "msg-005-3", role: "customer", content: "Around $2000. I'll look into both of those, thanks!", timestamp: "2026-03-10T09:05:00Z", metadata: null },
    ],
  };

  return { conversations, messages };
}
