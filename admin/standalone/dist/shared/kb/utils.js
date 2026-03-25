/**
 * Pure utility functions for the Knowledge Base manager.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
/** Format an ISO date string as "Mon DD, YYYY". */
export function formatDate(iso) {
    const d = new Date(iso);
    return d.toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' });
}
/** Extract a sorted, deduplicated list of category names from an array of articles. */
export function extractCategories(articles) {
    const set = new Set();
    for (const a of articles) {
        if (a.category)
            set.add(a.category);
    }
    return Array.from(set).sort();
}
//# sourceMappingURL=utils.js.map