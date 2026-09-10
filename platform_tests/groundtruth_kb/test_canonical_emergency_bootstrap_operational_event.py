"""A restored repair route uses native work, claims and independent review.

The unimplemented emergency bundle/permission ledger is retired. This test
neither authorizes a bypass nor qualifies an actual emergency operation.
"""

import json

from platform_tests.groundtruth_kb.test_native_authority_service import native as native
from platform_tests.groundtruth_kb.test_native_bridge import authored, claim
from platform_tests.groundtruth_kb.test_native_bridge import bridge as bridge


def test_wi7164_canonical_emergency_bootstrap_operational_event(bridge):
    _, client, contexts, root = bridge
    original = (root / "code.py").read_bytes()
    assert claim(client, "repair", "pb1", 0, "READY").status_code == 422
    for version, (context, status) in enumerate(
        [("pb1", "NEW"), ("lo1", "GO"), ("pb2", "READY"), ("lo2", "VERIFIED")], 1
    ):
        reservation = claim(client, "repair", context, version - 1, status)
        assert reservation.status_code == 200, reservation.text
        extra = {}
        if status == "VERIFIED":
            artifacts = client.get("/v1/bridge/repair/artifacts").json()
            extra["verified_artifacts"] = json.dumps(artifacts)
        content = authored(contexts[context], "repair", version, status, **extra).replace("::open build", "::open ops")
        request = {"native_context_id": context, "fence": reservation.json()["fence"], "content": content}
        before = client.get("/v1/bridge/repair/show?include_content=true").json()
        bad = client.post("/v1/bridge/repair/deliver", json={**request, "fence": request["fence"] + 1})
        assert bad.status_code == 422
        assert client.get("/v1/bridge/repair/show?include_content=true").json() == before
        accepted = client.post("/v1/bridge/repair/deliver", json=request)
        assert accepted.status_code == 200, accepted.text
        replay = client.post("/v1/bridge/repair/deliver", json=request)
        assert replay.status_code == 200
        assert replay.json() == {"status": "already_delivered", "document": "repair", "version": version}
    assert (root / "code.py").read_bytes() == original
    work = client.get("/v1/work-items/WI-1").json()
    assert work["work_item"]["resolution_status"] == "verified"
    assert client.get("/v1/projects/PROJECT-1").json()["project"]["status"] == "active"
