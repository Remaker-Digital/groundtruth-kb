"""ADVISORY uses native attribution and has no receiving agent envelope."""

import pytest
from groundtruth_kb.bridge.native import parse_authored_message
from groundtruth_kb.postgres_kernel import PostgresKernelError

from platform_tests.groundtruth_kb.test_native_authority_service import native as native
from platform_tests.groundtruth_kb.test_native_bridge import authored, deliver
from platform_tests.groundtruth_kb.test_native_bridge import bridge as bridge


@pytest.mark.parametrize("context", ["pb1", "lo1"])
def test_advisory_accepts_either_bound_agent_role(bridge, context):
    _, client, contexts, _ = bridge
    result, request = deliver(client, contexts, "advisory", context, 1, "ADVISORY", work_item_id=None)
    assert result.json()["bridge_status"] == "ADVISORY"
    observed = client.get("/v1/bridge/advisory/show?include_content=true").json()
    assert observed["messages"][0]["content"] == request["content"]


@pytest.mark.parametrize("prefix", ["::init gtkb pb\n", "::open build\n", "recipient_role: prime-builder\n"])
def test_advisory_refuses_a_dispatch_envelope_without_repair(prefix):
    content = authored({"session_context_id": "fixture"}, "advisory", 1, "ADVISORY")
    parse_authored_message(content)
    with pytest.raises(PostgresKernelError):
        parse_authored_message(prefix + content)
