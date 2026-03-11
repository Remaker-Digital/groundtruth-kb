// @ts-nocheck
/**
 * Dashboard fixture — analytics summary, daily volume, intent breakdown.
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

function generateDailyVolume(days: number) {
  const result = [];
  const now = new Date();
  for (let i = days - 1; i >= 0; i--) {
    const d = new Date(now);
    d.setDate(d.getDate() - i);
    const total = Math.floor(Math.random() * 40) + 10;
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
        { agent: 'CustomerServiceAgent', invocationCount: 156, percentage: 45.6 },
        { agent: 'ProductRecommendationAgent', invocationCount: 89, percentage: 26.0 },
        { agent: 'OrderStatusAgent', invocationCount: 52, percentage: 15.2 },
        { agent: 'ReturnRefundAgent', invocationCount: 31, percentage: 9.1 },
        { agent: 'EscalationAgent', invocationCount: 14, percentage: 4.1 },
      ],
    },
    gaps: { gaps: [] },
    conversations: {
      items: [],
      totalCount: 342,
      offset: 0,
      limit: 50,
    },
  };
}
