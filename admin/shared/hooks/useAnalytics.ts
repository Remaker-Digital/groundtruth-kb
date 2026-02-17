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

export function useAnalyticsSummary(apiFetch: ApiFetch, isTestMode?: TestModeFilter) {
  const params = new URLSearchParams();
  if (isTestMode === true) params.set('is_test_mode', 'true');
  else if (isTestMode === false) params.set('is_test_mode', 'false');
  const qs = params.toString();
  const path = qs ? `/api/analytics/summary?${qs}` : '/api/analytics/summary';
  return useApi<AnalyticsSummary>(apiFetch, path);
}

export function useIntentBreakdown(apiFetch: ApiFetch, isTestMode?: TestModeFilter) {
  const params = new URLSearchParams();
  if (isTestMode === true) params.set('is_test_mode', 'true');
  else if (isTestMode === false) params.set('is_test_mode', 'false');
  const qs = params.toString();
  const path = qs ? `/api/analytics/intents?${qs}` : '/api/analytics/intents';
  return useApi<{ intents: IntentBreakdown[] }>(apiFetch, path);
}

export function useKnowledgeGaps(apiFetch: ApiFetch, isTestMode?: TestModeFilter) {
  const params = new URLSearchParams();
  if (isTestMode === true) params.set('is_test_mode', 'true');
  else if (isTestMode === false) params.set('is_test_mode', 'false');
  const qs = params.toString();
  const path = qs ? `/api/analytics/gaps?${qs}` : '/api/analytics/gaps';
  return useApi<{ gaps: KnowledgeGap[] }>(apiFetch, path);
}
