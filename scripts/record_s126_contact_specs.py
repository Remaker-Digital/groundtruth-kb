"""Record Contact Us persistence specifications in KB (S126).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import json
import sys

sys.path.insert(0, "tools/knowledge-db")
from db import KnowledgeDB  # noqa: E402

CHANGED_BY = "claude/S126"
REASON = "Contact Us persistence feature — owner specification S126"


def main() -> None:
    db = KnowledgeDB()
    # -------------------------------------------------------------------
    # SPEC-1588: Contact Message Persistence
    # -------------------------------------------------------------------
    db.insert_spec(
        id="SPEC-1588",
        title="Contact Message Persistence — Cosmos DB Storage",
        description=(
            'Every "Contact Us" form submission from the merchant admin console '
            "must be persisted to an Azure Cosmos DB container in addition to being "
            "dispatched as an email. The contact_messages container stores each "
            "submission as a ContactMessageDocument with fields: id (UUID), "
            "tenant_id (partition key), topic, subject, message, member_email, "
            "member_role, member_id, tier, status (new/read/resolved/archived), "
            "created_at (ISO 8601 UTC), updated_at, notes (operator annotations). "
            "Persistence occurs BEFORE email dispatch so that even if email "
            "delivery fails the message is captured. The existing email dispatch "
            "behavior is unchanged — messages are still emailed to "
            "support@remakerdigital.com."
        ),
        status="specified",
        section="database",
        type="requirement",
        assertions=json.dumps([
            {"type": "glob", "pattern": "**/cosmos_schema.py", "contains": "ContactMessageDocument"},
            {"type": "glob", "pattern": "**/admin_contact_api.py", "contains": "contact_messages"},
            {"type": "grep", "pattern": "status.*new.*read.*resolved.*archived", "file_pattern": "**/cosmos_schema.py"},
        ]),
        changed_by=CHANGED_BY,
        change_reason=REASON,
    )
    print("SPEC-1588 inserted")

    # -------------------------------------------------------------------
    # SPEC-1589: Contact Messages Superadmin API
    # -------------------------------------------------------------------
    db.insert_spec(
        id="SPEC-1589",
        title="Contact Messages — Superadmin Query API",
        description=(
            "The superadmin API provides endpoints to query, update, and export "
            "contact messages across all tenants. Endpoints: "
            "GET /api/superadmin/contact-messages (list with pagination, filter by "
            "topic/status/tenant_id/date range, sort by created_at), "
            "GET /api/superadmin/contact-messages/{id} (single message detail), "
            "PATCH /api/superadmin/contact-messages/{id} (update status, add notes), "
            "GET /api/superadmin/contact-messages/export (CSV download with same "
            "filters as list endpoint). All endpoints require SUPERADMIN role. "
            "CSV export includes all document fields in a flat row format."
        ),
        status="specified",
        section="tenant_administration",
        type="requirement",
        assertions=json.dumps([
            {"type": "grep", "pattern": "contact.messages", "file_pattern": "**/superadmin_api.py"},
            {"type": "grep", "pattern": "export.*csv", "file_pattern": "**/superadmin_api.py"},
        ]),
        changed_by=CHANGED_BY,
        change_reason=REASON,
    )
    print("SPEC-1589 inserted")

    # -------------------------------------------------------------------
    # SPEC-1590: Contact Messages Provider Console UI
    # -------------------------------------------------------------------
    db.insert_spec(
        id="SPEC-1590",
        title="Contact Messages — Provider Console Admin Page",
        description=(
            'The Provider Console (SPA) includes a "Contact Messages" page for '
            "administering persisted contact form submissions. The page provides: "
            "(1) filterable/sortable table of all messages with columns for date, "
            "tenant, topic, subject, status, and member email; "
            "(2) message detail drawer/panel showing full message body, tenant "
            "context, and operator notes; "
            "(3) status update controls (new -> read -> resolved -> archived); "
            "(4) notes field for operator annotations; "
            "(5) CSV export button that triggers download of filtered results. "
            "The page is accessible from the Provider Console sidebar under the "
            "Operations nav group."
        ),
        status="specified",
        section="provider_administration",
        type="requirement",
        assertions=json.dumps([
            {"type": "glob", "pattern": "**/provider/pages/ContactMessages.tsx"},
            {"type": "grep", "pattern": "ContactMessages", "file_pattern": "**/provider/index.tsx"},
            {"type": "grep", "pattern": "contact-messages", "file_pattern": "**/provider/layouts/ProviderLayout.tsx"},
        ]),
        changed_by=CHANGED_BY,
        change_reason=REASON,
    )
    print("SPEC-1590 inserted")

    # -------------------------------------------------------------------
    # SPEC-1591: Contact Messages Cosmos Container
    # -------------------------------------------------------------------
    db.insert_spec(
        id="SPEC-1591",
        title="Contact Messages — Cosmos Container Provisioning",
        description=(
            "A Cosmos DB container named contact_messages is provisioned with "
            "partition key /tenant_id and serverless throughput. "
            "The container is the 19th in the agentred database. "
            "A provisioning script (create_contact_messages_container.py) handles "
            "creation. The CollectionConfig registry in cosmos_collections.py "
            "includes the contact_messages entry with partition key and "
            "document type mapping."
        ),
        status="specified",
        section="database",
        type="requirement",
        assertions=json.dumps([
            {"type": "grep", "pattern": "contact_messages", "file_pattern": "**/cosmos_collections.py"},
            {"type": "glob", "pattern": "**/create_contact_messages_container.py"},
        ]),
        changed_by=CHANGED_BY,
        change_reason=REASON,
    )
    print("SPEC-1591 inserted")

    # -------------------------------------------------------------------
    # SPEC-1592: Contact Message Status Lifecycle
    # -------------------------------------------------------------------
    db.insert_spec(
        id="SPEC-1592",
        title="Contact Message Status Lifecycle",
        description=(
            "Each contact message has a status field with valid values: "
            "new (initial, set on creation), read (operator has viewed), "
            "resolved (issue addressed), archived (closed/historical). "
            "Status transitions: new -> read -> resolved -> archived. "
            "Backward transitions are permitted (e.g., resolved -> read if "
            "reopened). updated_at is refreshed on every status change. "
            "The PATCH endpoint validates that status is one of the four "
            "valid values."
        ),
        status="specified",
        section="tenant_administration",
        type="requirement",
        assertions=json.dumps([
            {"type": "grep", "pattern": "new.*read.*resolved.*archived", "file_pattern": "**/superadmin_api.py"},
        ]),
        changed_by=CHANGED_BY,
        change_reason=REASON,
    )
    print("SPEC-1592 inserted")

    print("\nAll 5 specifications recorded.")


if __name__ == "__main__":
    main()
