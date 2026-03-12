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
        { agent: 'CustomerServiceAgent', invocationCount: 85, percentage: 45.5 },
        { agent: 'OrderStatusAgent', invocationCount: 52, percentage: 27.8 },
        { agent: 'ProductRecommendationAgent', invocationCount: 30, percentage: 16.0 },
        { agent: 'ReturnRefundAgent', invocationCount: 15, percentage: 8.0 },
        { agent: 'EscalationAgent', invocationCount: 5, percentage: 2.7 },
      ],
    },
    gaps: { gaps: [] },
    conversations: {
      items: [],
      totalCount: 187,
      offset: 0,
      limit: 50,
    },
  };
}
