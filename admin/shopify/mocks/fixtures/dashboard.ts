// @ts-nocheck
/**
 * Dashboard fixture — analytics summary, daily volume, intent breakdown.
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

/** Deterministic daily volume — fixed values, no Math.random(). */
function generateDailyVolume(days: number) {
  const base = [28, 35, 22, 31, 18, 42, 25, 37, 19, 33, 27, 40, 23, 36, 29, 38, 21, 34, 26, 41, 24, 32, 30, 39, 20, 43, 28, 35, 22, 31];
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
      tenantId: 'mock-shopify-tenant-001',
      billingPeriod: '2026-03',
      totalConversations: 187,
      includedAllowance: 500,
      remainingIncluded: 313,
      packBalance: 0,
      overageConversations: 0,
      overageReported: 0,
      usagePercent: 37.4,
      estimatedOverageCost: 0,
      activeAlerts: [],
    },
    daily: { days: generateDailyVolume(30) },
    summary: {
      tenantId: 'mock-shopify-tenant-001',
      since: '2026-02-08T00:00:00Z',
      until: '2026-03-10T23:59:59Z',
      totalConversations: 187,
      billableConversations: 150,
      avgTurns: 3.8,
      avgMessages: 7.6,
      avgResponseTime: 1.5,
      resolutionRate: 0.91,
      customerSatisfaction: 4.5,
      statusBreakdown: [
        { status: 'resolved', count: 170 },
        { status: 'escalated', count: 12 },
        { status: 'active', count: 3 },
        { status: 'timed_out', count: 2 },
      ],
      escalationCount: 12,
      escalationRate: 0.064,
      criticPassed: 175,
      criticFailed: 12,
      criticPassRate: 0.936,
    },
    intents: {
      intents: [
        { agent: 'Customer support', invocationCount: 85, percentage: 45.5 },
        { agent: 'Order status', invocationCount: 52, percentage: 27.8 },
        { agent: 'Product recommendations', invocationCount: 30, percentage: 16.0 },
        { agent: 'Returns & refunds', invocationCount: 15, percentage: 8.0 },
        { agent: 'Escalation', invocationCount: 5, percentage: 2.7 },
      ],
    },
    gaps: { gaps: [] },
    conversations: {
      items: [
        { conversationId: 'conv-sh-001', status: 'resolved', customerId: 'alice@example.com', isBillable: true, messageCount: 8, turnCount: 4, startedAt: '2026-03-10T14:22:00Z', endedAt: '2026-03-10T14:35:00Z', modelUsed: 'gpt-4o', criticPassed: true },
        { conversationId: 'conv-sh-002', status: 'resolved', customerId: 'bob@example.com', isBillable: true, messageCount: 12, turnCount: 6, startedAt: '2026-03-10T13:10:00Z', endedAt: '2026-03-10T13:28:00Z', modelUsed: 'gpt-4o', criticPassed: true },
        { conversationId: 'conv-sh-003', status: 'escalated', customerId: 'carol@example.com', isBillable: true, messageCount: 16, turnCount: 8, startedAt: '2026-03-10T11:45:00Z', endedAt: '2026-03-10T12:10:00Z', modelUsed: 'gpt-4o', criticPassed: false },
        { conversationId: 'conv-sh-004', status: 'resolved', customerId: 'dave@example.com', isBillable: true, messageCount: 6, turnCount: 3, startedAt: '2026-03-10T10:30:00Z', endedAt: '2026-03-10T10:42:00Z', modelUsed: 'gpt-4o', criticPassed: true },
        { conversationId: 'conv-sh-005', status: 'active', customerId: 'eve@example.com', isBillable: false, messageCount: 4, turnCount: 2, startedAt: '2026-03-10T09:15:00Z', endedAt: null, modelUsed: 'gpt-4o', criticPassed: null },
      ],
      totalCount: 187,
      offset: 0,
      limit: 50,
    },
  };
}
