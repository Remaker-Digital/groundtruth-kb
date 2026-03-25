/**
 * Analytics and Usage hooks — summary, intents, knowledge gaps, usage dashboard.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { useApi } from './useApi';
// ---------------------------------------------------------------------------
// Usage hooks
// ---------------------------------------------------------------------------
export function useUsageDashboard(apiFetch, billingPeriod) {
    const path = billingPeriod
        ? `/api/dashboard/usage?billing_period=${billingPeriod}`
        : '/api/dashboard/usage';
    return useApi(apiFetch, path);
}
export function useDailyVolume(apiFetch, billingPeriod) {
    const path = billingPeriod
        ? `/api/dashboard/usage/daily?billing_period=${billingPeriod}`
        : '/api/dashboard/usage/daily';
    return useApi(apiFetch, path);
}
export function useConversationList(apiFetch, billingPeriod, offset = 0, limit = 50) {
    const params = new URLSearchParams();
    if (billingPeriod)
        params.set('billing_period', billingPeriod);
    params.set('offset', String(offset));
    params.set('limit', String(limit));
    const path = `/api/dashboard/conversations?${params}`;
    return useApi(apiFetch, path);
}
/** Build analytics query string from optional filters. */
function analyticsParams(opts) {
    const params = new URLSearchParams();
    if (opts?.isTestMode === true)
        params.set('is_test_mode', 'true');
    else if (opts?.isTestMode === false)
        params.set('is_test_mode', 'false');
    if (opts?.period) {
        const days = parseInt(opts.period.replace('d', ''), 10);
        const until = new Date();
        const since = new Date(until.getTime() - days * 24 * 60 * 60 * 1000);
        params.set('since', since.toISOString());
        params.set('until', until.toISOString());
    }
    return params.toString();
}
export function useAnalyticsSummary(apiFetch, isTestMode, period) {
    const qs = analyticsParams({ isTestMode, period });
    const path = qs ? `/api/analytics/summary?${qs}` : '/api/analytics/summary';
    return useApi(apiFetch, path);
}
export function useIntentBreakdown(apiFetch, isTestMode, period) {
    const qs = analyticsParams({ isTestMode, period });
    const path = qs ? `/api/analytics/intents?${qs}` : '/api/analytics/intents';
    return useApi(apiFetch, path);
}
export function useKnowledgeGaps(apiFetch, isTestMode, period) {
    const qs = analyticsParams({ isTestMode, period });
    const path = qs ? `/api/analytics/gaps?${qs}` : '/api/analytics/gaps';
    return useApi(apiFetch, path);
}
//# sourceMappingURL=useAnalytics.js.map