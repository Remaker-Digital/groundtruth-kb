// @ts-nocheck
/**
 * Provider service messages fixture — bulk notification data.
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
export function createServiceMessagesFixture() {
  return {
    sentMessages: [
      { id: "sm-001", subject: "Scheduled maintenance — March 15", body: "Brief API downtime expected 2-4 AM ET.", recipientCount: 14, sentAt: "2026-03-11T10:00:00Z", filterStatus: "active", filterTier: null },
      { id: "sm-002", subject: "New feature: Quick Actions", body: "Quick action buttons are now available for your widget.", recipientCount: 19, sentAt: "2026-03-01T09:00:00Z", filterStatus: null, filterTier: null },
    ],
  };
}
