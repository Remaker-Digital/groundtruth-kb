"""Credential refusal across proposal, revision and implementation-report delivery."""

import pytest

from platform_tests.groundtruth_kb.bridge_fixtures import authored, claim, deliver
from platform_tests.groundtruth_kb.bridge_fixtures import bridge as bridge
from platform_tests.groundtruth_kb.native_fixtures import native as native

pytestmark = [pytest.mark.integration, pytest.mark.timeout(120)]


@pytest.mark.parametrize("status", ["NEW", "REVISED", "READY"])
def test_credentials_are_not_published_or_silently_redacted(bridge, status):
    _, client, contexts, root = bridge
    document = "authored-credential-check"
    if status == "NEW":
        context, version = "pb1", 1
    else:
        deliver(client, contexts, document, "pb1", 1, "NEW")
        deliver(client, contexts, document, "lo1", 2, "NO-GO" if status == "REVISED" else "GO")
        context, version = "pb2", 3
    reserved = claim(client, document, context, version - 1, status)
    assert reserved.status_code == 200, reserved.text
    fence = reserved.json()["fence"]
    clean = authored(contexts[context], document, version, status)
    before = client.get(f"/v1/bridge/{document}/show?include_content=true").json()
    for credential in ["ar" + "_live_" + "TESTTOKEN123456", "AK" + "IA" + "ABCDEFGHIJKLMNOP"]:
        response = client.post(
            f"/v1/bridge/{document}/deliver",
            json={"native_context_id": context, "fence": fence, "content": clean + credential},
        )
        assert response.status_code == 422, response.text
        assert response.json()["error"]["code"] == "bridge_credential_detected"
        assert credential not in response.text
        assert client.get(f"/v1/bridge/{document}/show?include_content=true").json() == before
    # Contact information is not a credential, and the authored bytes are retained.
    content = clean + "Contact support@example.com or +15551234567 for the test instructions.\n"
    response = client.post(
        f"/v1/bridge/{document}/deliver",
        json={"native_context_id": context, "fence": fence, "content": content},
    )
    assert response.status_code == 200, response.text
    state = client.get(f"/v1/bridge/{document}/show?include_content=true").json()
    assert state["messages"][-1]["content"] == content
    assert not (root / "bridge").exists()
