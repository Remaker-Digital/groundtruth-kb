// @ts-nocheck
/**
 * Quick actions fixture.
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
export function createQuickActionsFixture() {
  return {
    actions: [
      { id: "qa-001", label: "Track Order", prompt: "I want to track my order", icon: "package", enabled: true, order: 1 },
      { id: "qa-002", label: "Return Item", prompt: "I need to return an item", icon: "refresh", enabled: true, order: 2 },
      { id: "qa-003", label: "Contact Support", prompt: "I need to speak with someone", icon: "headset", enabled: true, order: 3 },
      { id: "qa-004", label: "Size Help", prompt: "Help me find the right size", icon: "ruler", enabled: true, order: 4 },
      { id: "qa-005", label: "Product Info", prompt: "Tell me about this product", icon: "info", enabled: false, order: 5 },
    ],
    nextId: 6,
  };
}
