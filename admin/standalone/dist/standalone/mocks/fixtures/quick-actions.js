// @ts-nocheck
/**
 * Quick actions fixture.
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
export function createQuickActionsFixture() {
    return {
        actions: [
            { id: "qa-001", label: "Track Order", prompt: "I want to track my order", icon: "📦", enabled: true, order: 1 },
            { id: "qa-002", label: "Return Item", prompt: "I need to return an item", icon: "🔄", enabled: true, order: 2 },
            { id: "qa-003", label: "Contact Support", prompt: "I need to speak with someone", icon: "🎧", enabled: true, order: 3 },
            { id: "qa-004", label: "Size Help", prompt: "Help me find the right size", icon: "📏", enabled: true, order: 4 },
            { id: "qa-005", label: "Product Info", prompt: "Tell me about this product", icon: "ℹ️", enabled: false, order: 5 },
        ],
        nextId: 6,
        assignments: [
            { pageType: "all", pageHandle: null, slot1ActionId: "qa-001", slot2ActionId: "qa-002", autoOpen: false, autoOpenDelayMs: 3000 },
            { pageType: "home", pageHandle: null, slot1ActionId: null, slot2ActionId: null, autoOpen: false, autoOpenDelayMs: 3000 },
            { pageType: "product", pageHandle: null, slot1ActionId: "qa-004", slot2ActionId: "qa-005", autoOpen: false, autoOpenDelayMs: 3000 },
            { pageType: "collection", pageHandle: null, slot1ActionId: null, slot2ActionId: null, autoOpen: false, autoOpenDelayMs: 3000 },
            { pageType: "cart", pageHandle: null, slot1ActionId: "qa-001", slot2ActionId: null, autoOpen: false, autoOpenDelayMs: 3000 },
            { pageType: "search", pageHandle: null, slot1ActionId: null, slot2ActionId: null, autoOpen: false, autoOpenDelayMs: 3000 },
            { pageType: "blog", pageHandle: null, slot1ActionId: null, slot2ActionId: null, autoOpen: false, autoOpenDelayMs: 3000 },
            { pageType: "page", pageHandle: null, slot1ActionId: null, slot2ActionId: null, autoOpen: false, autoOpenDelayMs: 3000 },
            { pageType: "other", pageHandle: null, slot1ActionId: null, slot2ActionId: null, autoOpen: false, autoOpenDelayMs: 3000 },
        ],
    };
}
//# sourceMappingURL=quick-actions.js.map