"""Record Contact Us persistence tests and work items in KB (S126).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import sys

sys.path.insert(0, "tools/knowledge-db")
from db import KnowledgeDB  # noqa: E402

CHANGED_BY = "claude/S126"
REASON = "Contact Us persistence feature — S126"


def main() -> None:
    db = KnowledgeDB()

    # -------------------------------------------------------------------
    # Tests (TEST-2778..TEST-2795)
    # -------------------------------------------------------------------
    tests = [
        # SPEC-1588 — Cosmos persistence
        ("TEST-2778", "SPEC-1588", "ContactMessageDocument schema has required fields", "unit"),
        ("TEST-2779", "SPEC-1588", "Contact submission persists document to Cosmos before email", "unit"),
        ("TEST-2780", "SPEC-1588", "Contact submission still sends email after persistence", "unit"),
        ("TEST-2781", "SPEC-1588", "Email failure does not prevent persistence", "unit"),
        ("TEST-2782", "SPEC-1588", "New message has status=new and created_at set", "unit"),
        # SPEC-1589 — Superadmin query API
        ("TEST-2783", "SPEC-1589", "GET /contact-messages returns paginated list", "unit"),
        ("TEST-2784", "SPEC-1589", "GET /contact-messages filters by topic", "unit"),
        ("TEST-2785", "SPEC-1589", "GET /contact-messages filters by status", "unit"),
        ("TEST-2786", "SPEC-1589", "GET /contact-messages/{id} returns single message", "unit"),
        ("TEST-2787", "SPEC-1589", "PATCH /contact-messages/{id} updates status", "unit"),
        ("TEST-2788", "SPEC-1589", "PATCH /contact-messages/{id} adds notes", "unit"),
        ("TEST-2789", "SPEC-1589", "GET /contact-messages/export returns CSV", "unit"),
        ("TEST-2790", "SPEC-1589", "CSV export includes all document fields", "unit"),
        # SPEC-1590 — Provider Console UI
        ("TEST-2791", "SPEC-1590", "ContactMessages page registered in Provider Console routes", "unit"),
        ("TEST-2792", "SPEC-1590", "ContactMessages page has nav entry in sidebar", "unit"),
        # SPEC-1591 — Container provisioning
        ("TEST-2793", "SPEC-1591", "contact_messages container registered in CollectionConfig", "unit"),
        ("TEST-2794", "SPEC-1591", "Provisioning script creates contact_messages container", "unit"),
        # SPEC-1592 — Status lifecycle
        ("TEST-2795", "SPEC-1592", "PATCH validates status is one of new/read/resolved/archived", "unit"),
    ]

    for test_id, spec_id, title, test_type in tests:
        db.insert_test(
            id=test_id,
            spec_id=spec_id,
            title=title,
            test_type=test_type,
            expected_outcome="PASS",
            changed_by=CHANGED_BY,
            change_reason=REASON,
        )
        print(f"  {test_id} -> {spec_id}: {title}")

    print(f"\n{len(tests)} test artifacts recorded.")

    # -------------------------------------------------------------------
    # Work Items (WI-0899..WI-0905)
    # -------------------------------------------------------------------
    work_items = [
        (
            "WI-0899",
            "ContactMessageDocument schema + Cosmos container",
            "Add ContactMessageDocument to cosmos_schema.py, register contact_messages "
            "container in cosmos_collections.py, create provisioning script.",
            "new",
            "database",
            "SPEC-1588",
        ),
        (
            "WI-0900",
            "Persist contact submissions to Cosmos",
            "Modify admin_contact_api.py send_contact_message() to persist the "
            "ContactMessageDocument to Cosmos BEFORE dispatching email. Inject the "
            "contact_messages repository into the endpoint.",
            "new",
            "agent_implementation",
            "SPEC-1588",
        ),
        (
            "WI-0901",
            "Superadmin contact messages list + filter endpoints",
            "Add GET /api/superadmin/contact-messages with pagination, topic/status/"
            "tenant_id/date range filters, and sort. Add GET /{id} for single message.",
            "new",
            "tenant_administration",
            "SPEC-1589",
        ),
        (
            "WI-0902",
            "Superadmin contact message PATCH + status lifecycle",
            "Add PATCH /api/superadmin/contact-messages/{id} for status updates and "
            "notes. Validate status transitions.",
            "new",
            "tenant_administration",
            "SPEC-1589",
        ),
        (
            "WI-0903",
            "Superadmin contact messages CSV export",
            "Add GET /api/superadmin/contact-messages/export returning CSV with all "
            "document fields. Support same filters as list endpoint.",
            "new",
            "tenant_administration",
            "SPEC-1589",
        ),
        (
            "WI-0904",
            "Provider Console ContactMessages page",
            "Create ContactMessages.tsx in admin/provider/pages with filterable table, "
            "detail drawer, status controls, notes, and CSV export button. Register "
            "in ProviderLayout nav and index.tsx routes.",
            "new",
            "provider_administration",
            "SPEC-1590",
        ),
        (
            "WI-0905",
            "Contact messages test suite",
            "Write unit tests for persistence, API endpoints, CSV export, status "
            "lifecycle, and UI registration. Cover TEST-2778..TEST-2795.",
            "new",
            "test_harness",
            "SPEC-1588",
        ),
    ]

    for wi_id, title, description, origin, component, spec_id in work_items:
        db.insert_work_item(
            id=wi_id,
            title=title,
            description=description,
            resolution_status="specified",
            origin=origin,
            component=component,
            source_spec_id=spec_id,
            changed_by=CHANGED_BY,
            change_reason=REASON,
        )
        print(f"  {wi_id}: {title}")

    print(f"\n{len(work_items)} work items recorded.")
    db.close()


if __name__ == "__main__":
    main()
