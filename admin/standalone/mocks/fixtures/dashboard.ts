// @ts-nocheck
/**
 * Dashboard fixture — analytics summary, daily volume, intent breakdown.
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

/** Deterministic daily volume — fixed values, no Math.random(). */
function generateDailyVolume(days: number) {
  const base = [32, 28, 41, 25, 38, 19, 35, 30, 44, 22, 37, 27, 40, 24, 33, 29, 43, 21, 36, 26, 39, 23, 34, 31, 42, 20, 38, 28, 35, 30];
  const result = [];
  const now = new Date();
  for (let i = days - 1; i >= 0; i--) {
    const d = new Date(now);
    d.setDate(d.getDate() - i);
    const total = base[i % base.length];
    result.push({
      date: d.toISOString().slice(0, 10),
      total,
      billable: Math.floor(total * 0.8),
    });
  }
  return result;
}

export function createDashboardFixture() {
  return {
    usage: {
      tenantId: 'mock-tenant-001',
      billingPeriod: '2026-03',
      totalConversations: 342,
      includedAllowance: 500,
      remainingIncluded: 158,
      packBalance: 0,
      overageConversations: 0,
      overageReported: 0,
      usagePercent: 68.4,
      estimatedOverageCost: 0,
      activeAlerts: [],
    },
    daily: { days: generateDailyVolume(30) },
    summary: {
      tenantId: 'mock-tenant-001',
      since: '2026-02-08T00:00:00Z',
      until: '2026-03-10T23:59:59Z',
      totalConversations: 342,
      billableConversations: 274,
      avgTurns: 4.2,
      avgMessages: 8.6,
      avgResponseTime: 1.8,
      resolutionRate: 0.87,
      customerSatisfaction: 4.3,
      statusBreakdown: [
        { status: 'resolved', count: 298 },
        { status: 'escalated', count: 32 },
        { status: 'active', count: 8 },
        { status: 'timed_out', count: 4 },
      ],
      escalationCount: 32,
      escalationRate: 0.094,
      criticPassed: 310,
      criticFailed: 32,
      criticPassRate: 0.906,
    },
    intents: {
      intents: [
        { agent: 'Customer support', invocationCount: 156, percentage: 45.6 },
        { agent: 'Product recommendations', invocationCount: 89, percentage: 26.0 },
        { agent: 'Order status', invocationCount: 52, percentage: 15.2 },
        { agent: 'Returns & refunds', invocationCount: 31, percentage: 9.1 },
        { agent: 'Escalation', invocationCount: 14, percentage: 4.1 },
      ],
    },
    gaps: { gaps: [] },
    conversations: {
      items: [
        { conversationId: 'conv-sa-001', status: 'resolved', customerId: 'user1@example.com', isBillable: true, messageCount: 10, turnCount: 5, startedAt: '2026-03-10T14:22:00Z', endedAt: '2026-03-10T14:38:00Z', modelUsed: 'gpt-4o', criticPassed: true },
        { conversationId: 'conv-sa-002', status: 'resolved', customerId: 'user2@example.com', isBillable: true, messageCount: 6, turnCount: 3, startedAt: '2026-03-10T13:10:00Z', endedAt: '2026-03-10T13:22:00Z', modelUsed: 'gpt-4o', criticPassed: true },
        { conversationId: 'conv-sa-003', status: 'escalated', customerId: 'user3@example.com', isBillable: true, messageCount: 14, turnCount: 7, startedAt: '2026-03-10T11:45:00Z', endedAt: '2026-03-10T12:15:00Z', modelUsed: 'gpt-4o', criticPassed: false },
        { conversationId: 'conv-sa-004', status: 'resolved', customerId: 'user4@example.com', isBillable: true, messageCount: 8, turnCount: 4, startedAt: '2026-03-10T10:30:00Z', endedAt: '2026-03-10T10:45:00Z', modelUsed: 'gpt-4o', criticPassed: true },
        { conversationId: 'conv-sa-005', status: 'active', customerId: 'user5@example.com', isBillable: false, messageCount: 4, turnCount: 2, startedAt: '2026-03-10T09:15:00Z', endedAt: null, modelUsed: 'gpt-4o', criticPassed: null },
      ],
      totalCount: 342,
      offset: 0,
      limit: 50,
    },
  };
}
