// @ts-nocheck
/**
 * Provider incidents fixture — status page incident data.
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
export function createIncidentsFixture() {
  return {
    incidents: [
      {
        id: "inc-001",
        title: "Elevated API latency in East US region",
        status: "resolved",
        severity: "minor",
        createdAt: "2026-03-08T03:10:00Z",
        resolvedAt: "2026-03-08T03:30:00Z",
        updates: [
          { id: "upd-001", message: "Investigating elevated p99 latency", status: "investigating", createdAt: "2026-03-08T03:10:00Z" },
          { id: "upd-002", message: "Root cause identified — Azure Cosmos throttling", status: "identified", createdAt: "2026-03-08T03:18:00Z" },
          { id: "upd-003", message: "RU allocation increased. Latency normalized.", status: "resolved", createdAt: "2026-03-08T03:30:00Z" },
        ],
      },
      {
        id: "inc-002",
        title: "Scheduled maintenance — database migration",
        status: "scheduled",
        severity: "maintenance",
        createdAt: "2026-03-12T00:00:00Z",
        resolvedAt: null,
        scheduledFor: "2026-03-15T02:00:00Z",
        updates: [
          { id: "upd-004", message: "Planned maintenance window: 2:00-4:00 AM ET. Expect brief API unavailability.", status: "scheduled", createdAt: "2026-03-12T00:00:00Z" },
        ],
      },
    ],
    nextIncidentId: 3,
  };
}
