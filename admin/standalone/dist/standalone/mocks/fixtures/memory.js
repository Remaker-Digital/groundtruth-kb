// @ts-nocheck
/**
 * Memory & Privacy fixture.
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
export function createMemoryFixture() {
    return {
        settings: {
            memoryEnabled: true,
            retentionDays: 90,
            piiMaskingEnabled: true,
            gdprCompliant: true,
            layers: [
                { id: "layer-1", name: "Conversation Memory", enabled: true, scope: "session", description: "Remembers context within a single conversation" },
                { id: "layer-2", name: "Customer Memory", enabled: true, scope: "customer", description: "Remembers returning customers across sessions" },
                { id: "layer-3", name: "Product Memory", enabled: true, scope: "tenant", description: "Learns product information from conversations" },
                { id: "layer-4", name: "Analytics Memory", enabled: false, scope: "tenant", description: "Enterprise-only: aggregated pattern learning", tierGate: "enterprise" },
            ],
        },
    };
}
//# sourceMappingURL=memory.js.map