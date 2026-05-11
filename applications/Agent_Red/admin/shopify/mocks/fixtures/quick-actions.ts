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
    ],
    nextId: 4,
    assignments: [
      { pageType: "all", pageHandle: null, slot1ActionId: "qa-001", slot2ActionId: "qa-002", autoOpen: false, autoOpenDelayMs: 3000 },
      { pageType: "home", pageHandle: null, slot1ActionId: null, slot2ActionId: null, autoOpen: false, autoOpenDelayMs: 3000 },
      { pageType: "product", pageHandle: null, slot1ActionId: "qa-003", slot2ActionId: null, autoOpen: false, autoOpenDelayMs: 3000 },
    ],
  };
}
