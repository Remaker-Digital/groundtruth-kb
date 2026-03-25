/**
 * Shared TypeScript types for the Admin component library.
 *
 * These types are used by all 9 shared components and both admin shells
 * (Shopify embedded + Standalone). Framework-agnostic — no Polaris or
 * shell-specific dependencies.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
/** Standard escalation categories — same list used in Configuration and Team management. */
export const ESCALATION_CATEGORIES = [
    { id: 'sales', label: 'Sales', description: 'Purchase decisions, pricing questions, product comparisons' },
    { id: 'support', label: 'Support', description: 'Product issues, troubleshooting, how-to questions' },
    { id: 'service', label: 'Service', description: 'Returns, refunds, exchanges, order modifications' },
    { id: 'account', label: 'Account', description: 'Account access, billing, subscription management' },
    { id: 'technical', label: 'Technical assistance', description: 'Integration issues, API questions, advanced configuration' },
    { id: 'general', label: 'General inquiry', description: 'Complaints, legal, safety, or anything not matching other categories' },
];
//# sourceMappingURL=index.js.map