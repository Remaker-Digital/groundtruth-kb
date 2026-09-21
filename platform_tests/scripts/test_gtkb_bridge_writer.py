"""Authored-message validation for the native bridge writer.

Raw file publication, automatic headers, version renumbering, footer injection
and pending-publication sidecars are retired obligations. Exact delivery,
fencing and recovery are exercised by test_bridge_publication_preimage_scoping
and the installed provider/native-CLI workflows. The raw writer's remaining
consumers still require retirement before integration.
"""

from __future__ import annotations

from itertools import permutations

import pytest
from groundtruth_kb.bridge.native import parse_authored_message
from groundtruth_kb.postgres_kernel import PostgresKernelError

from platform_tests.groundtruth_kb.bridge_fixtures import authored


def message(status="NEW", **fields):
    return authored({"session_context_id": "receiving-context"}, "assigned-document", 1, status, **fields)


@pytest.mark.parametrize(
    "status",
    [
        "NEW",
        "REVISED",
        "READY",
        "VERDICT-REJECTED",
        "BLOCKED",
        "GO",
        "NO-GO",
        "NOT-READY",
        "SUPERSEDED",
        "VERIFIED",
        "WITHDRAWN",
        "ADVISORY",
    ],
)
def test_native_writer_accepts_each_authored_canonical_status(status):
    parsed = parse_authored_message(message(status))
    assert parsed["status"] == status
    assert parsed["version"] == 1
    assert parsed["metadata"]["document"] == "assigned-document"


@pytest.mark.parametrize("head", list(permutations(["::init gtkb lo", "::open build", "NEW"])))
def test_authored_dispatch_header_order_is_not_rewritten(head):
    content = message().splitlines(keepends=True)
    supplied = "\r\n".join(head) + "\r\n" + "".join(content[3:])
    assert parse_authored_message(supplied)["status"] == "NEW"


@pytest.mark.parametrize(
    "field",
    [
        "bridge_kind",
        "Document",
        "Date",
        "author_identity",
        "author_harness_id",
        "author_session_context_id",
        "author_model",
        "Project",
        "Work Item",
        "recipient_role",
    ],
)
def test_native_writer_refuses_missing_authored_metadata(field):
    content = "\r\n".join(line for line in message().splitlines() if not line.startswith(field + ":"))
    with pytest.raises(PostgresKernelError) as error:
        parse_authored_message(content)
    assert error.value.code == "invalid_bridge_header"


@pytest.mark.parametrize("field", ["target_role", "Project Authorization", "pauth", "receiver_kind", "spec_ids"])
def test_retired_metadata_is_refused_instead_of_carried_forward(field):
    with pytest.raises(PostgresKernelError) as error:
        parse_authored_message(message(**{field: "obsolete"}))
    assert error.value.code == "invalid_bridge_header"


@pytest.mark.parametrize("version", ["0", "-1", "one", "1.0"])
def test_invalid_version_is_refused_instead_of_renumbered(version):
    with pytest.raises(PostgresKernelError) as error:
        parse_authored_message(message(Version=version))
    assert error.value.code == "invalid_bridge_header"


@pytest.mark.parametrize("field", ["DOCUMENT", "author-model", "work item"])
def test_duplicate_metadata_is_refused_even_with_alternate_spelling(field):
    with pytest.raises(PostgresKernelError) as error:
        parse_authored_message(message(**{field: "duplicate"}))
    assert error.value.code == "invalid_bridge_header"


@pytest.mark.parametrize(
    "old,new",
    [
        ("::init gtkb lo", "::init gtkb pb"),
        ("::open build", "::open operations"),
        ("NEW", "NO-ACTION"),
        ("NEW", "DEFERRED"),
    ],
)
def test_wrong_recipient_activity_or_retired_status_is_refused(old, new):
    with pytest.raises(PostgresKernelError) as error:
        parse_authored_message(message().replace(old, new, 1))
    assert error.value.code == "invalid_bridge_header"


@pytest.mark.parametrize("status", ["ADVISORY", "VERIFIED", "WITHDRAWN", "SUPERSEDED", "BLOCKED"])
def test_non_dispatchable_delivery_cannot_grow_an_agent_envelope(status):
    with pytest.raises(PostgresKernelError) as error:
        parse_authored_message("::init gtkb lo\r\n::open build\r\n" + message(status))
    assert error.value.code == "invalid_bridge_header"
