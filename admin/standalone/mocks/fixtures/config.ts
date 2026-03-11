// @ts-nocheck
/**
 * Config fixture - widget configuration, named configs, activation state.
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

export function createConfigFixture() {
  return {
    draft: {
      config: {
        brand_name: "Mock Store",
        agent_name: "Agent Red",
        agent_role: "Customer service assistant",
        greeting_message: "Hi there! How can I help you today?",
        escalation_message: "Let me connect you with a human agent.",
        widget_primary_color: "#ff3621",
        widget_launcher_color: "#ff3621",
        widget_position: "bottom-right",
        widget_launcher_size: 56,
        widget_launcher_icon: "chat",
        widget_border_radius: 12,
        widget_header_text: "Chat with us",
        widget_subtitle: "We typically reply within minutes",
        widget_placeholder: "Type your message...",
        widget_page_rules: [],
        widget_pre_chat_fields: [],
        tone: "friendly",
        response_length: "medium",
        language: "en",
        max_turns: 20,
        escalation_threshold: 3,
        rate_limit_rpm: 500,
      },
      version: 4,
      tier: "professional",
      fromCache: false,
    },
    schema: {
      fields: [
        { key: "brand_name", label: "Brand name", type: "string", group: "brand", stepOrder: 1 },
        { key: "agent_name", label: "Agent name", type: "string", group: "brand", stepOrder: 2 },
        { key: "greeting_message", label: "Greeting", type: "textarea", group: "behavior", stepOrder: 3 },
      ],
    },
    named: {
      configs: [
        { name: "Default", version: 3, isActive: true, isDefault: true, createdAt: "2026-01-15T08:00:00Z", createdBy: "admin@mockstore.com", fieldCount: 22 },
        { name: "Holiday Mode", version: 1, isActive: false, isDefault: false, createdAt: "2026-02-20T10:00:00Z", createdBy: "admin@mockstore.com", fieldCount: 22 },
      ],
      total: 2,
    },
    versions: {
      versions: [
        { version: 4, createdAt: "2026-03-08T14:00:00Z", actor: "admin@mockstore.com", changeCount: 3 },
        { version: 3, createdAt: "2026-03-01T12:00:00Z", actor: "admin@mockstore.com", changeCount: 5 },
      ],
    },
    draftState: {
      has_pending_changes: false,
      active_version: 3,
      active_activated_at: "2026-03-01T12:00:00Z",
      draft_version: 4,
      changed_fields: [],
      draft_config: {},
      active_config: {},
    },
    widgetAppearances: {
      configs: [
        { name: "Default Look", version: 1, isActive: true, isDefault: true, createdAt: "2026-01-15T08:00:00Z", createdBy: null, fieldCount: 8 },
      ],
    },
  };
}
