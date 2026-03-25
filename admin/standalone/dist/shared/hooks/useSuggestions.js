/**
 * Configuration suggestions hooks — fetch AI-generated config field suggestions.
 *
 * KA-7: Knowledge Automation Admin UI.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { useApi } from './useApi';
// ---------------------------------------------------------------------------
// Hooks
// ---------------------------------------------------------------------------
/** Fetch configuration suggestions generated from KB content analysis. */
export function useConfigSuggestions(apiFetch) {
    return useApi(apiFetch, '/api/admin/knowledge/suggestions');
}
//# sourceMappingURL=useSuggestions.js.map