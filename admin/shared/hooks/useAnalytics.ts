/**
 * Analytics and Usage hooks — summary, intents, knowledge gaps, usage dashboard.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import type {
  UsageDashboard,
  DailyVolume,
  ConversationSummary,
  AnalyticsSummary,
  IntentBreakdown,
  KnowledgeGap,
  PaginatedList,
} from '../types/index';
import { useApi } from './useApi';
import type { ApiFetch } from './useApi';

// ---------------------------------------------------------------------------
// Usage hooks
// ---------------------------------------------------------------------------

export function useUsageDashboard(apiFetch: ApiFetch, billingPeriod?: string) {
  const path = billingPeriod
    ? `/api/dashboard/usage?billing_period=${billingPeriod}`
    : '/api/dashboard/usage';
  return useApi<UsageDashboard>(apiFetch, path);
}

export function useDailyVolume(apiFetch: ApiFetch, billingPeriod?: string) {
  const path = billingPeriod
    ? `/api/dashboard/usage/daily?billing_period=${billingPeriod}`
    : '/api/dashboard/usage/daily';
  return useApi<{ days: DailyVolume[] }>(apiFetch, path);
}

export function useConversationList(
  apiFetch: ApiFetch,
  billingPeriod?: string,
  offset = 0,
  limit = 50,
) {
  const params = new URLSearchParams();
  if (billingPeriod) params.set('billing_period', billingPeriod);
  params.set('offset', String(offset));
  params.set('limit', String(limit));
  const path = `/api/dashboard/conversations?${params}`;
  return useApi<PaginatedList<ConversationSummary>>(apiFetch, path);
}

// ---------------------------------------------------------------------------
// Analytics hooks
// ---------------------------------------------------------------------------

/** Test mode filter for analytics: undefined = all, true = test only, false = production only. */
export type TestModeFilter = boolean | undefined;

/** Period preset for analytics date range filtering. */
export type AnalyticsPeriod = '7d' | '14d' | '30d' | '90d';

/** Build analytics query string from optional filters. */
function analyticsParams(opts?: {
  isTestMode?: TestModeFilter;
  period?: AnalyticsPeriod;
}): string {
  const params = new URLSearchParams();
  if (opts?.isTestMode === true) params.set('is_test_mode', 'true');
  else if (opts?.isTestMode === false) params.set('is_test_mode', 'false');
  if (opts?.period) {
    const days = parseInt(opts.period.replace('d', ''), 10);
    const until = new Date();
    const since = new Date(until.getTime() - days * 24 * 60 * 60 * 1000);
    params.set('since', since.toISOString());
    params.set('until', until.toISOString());
  }
  return params.toString();
}

export function useAnalyticsSummary(
  apiFetch: ApiFetch,
  isTestMode?: TestModeFilter,
  period?: AnalyticsPeriod,
) {
  const qs = analyticsParams({ isTestMode, period });
  const path = qs ? `/api/analytics/summary?${qs}` : '/api/analytics/summary';
  return useApi<AnalyticsSummary>(apiFetch, path);
}

export function useIntentBreakdown(
  apiFetch: ApiFetch,
  isTestMode?: TestModeFilter,
  period?: AnalyticsPeriod,
) {
  const qs = analyticsParams({ isTestMode, period });
  const path = qs ? `/api/analytics/intents?${qs}` : '/api/analytics/intents';
  return useApi<{ intents: IntentBreakdown[] }>(apiFetch, path);
}

export function useKnowledgeGaps(
  apiFetch: ApiFetch,
  isTestMode?: TestModeFilter,
  period?: AnalyticsPeriod,
) {
  const qs = analyticsParams({ isTestMode, period });
  const path = qs ? `/api/analytics/gaps?${qs}` : '/api/analytics/gaps';
  return useApi<{ gaps: KnowledgeGap[] }>(apiFetch, path);
}
