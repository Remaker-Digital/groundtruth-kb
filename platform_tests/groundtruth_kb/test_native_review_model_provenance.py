"""Declared model diversity at current proposal/report review admission.

The fixture simulates authored provenance. These cases do not authenticate an
executing model or replace the owner's/dispatcher's actual model selection.
"""

from __future__ import annotations

import json
from types import SimpleNamespace

import pytest
from groundtruth_kb.bridge.native import NativeBridgeService
from groundtruth_kb.postgres_kernel import PostgresKernelError

from platform_tests.groundtruth_kb.bridge_fixtures import authored, claim, deliver
from platform_tests.groundtruth_kb.bridge_fixtures import bridge as bridge
from platform_tests.groundtruth_kb.finalization_fixtures import post
from platform_tests.groundtruth_kb.native_fixtures import native as native

pytestmark = [pytest.mark.integration, pytest.mark.timeout(120)]


def _refuse_same_model(client, contexts, document, version, status, model, **extra):
    reserved = claim(client, document, "lo2", version - 1, status)
    assert reserved.status_code == 200, reserved.text
    before = client.get(f"/v1/bridge/{document}/show", params={"include_content": True}).json()
    request = {
        "native_context_id": "lo2",
        "fence": reserved.json()["fence"],
        "content": authored(contexts["lo2"], document, version, status, author_model=model, **extra),
    }
    refused = client.post(f"/v1/bridge/{document}/deliver", json=request)
    assert refused.status_code == 422, refused.text
    assert refused.json()["error"]["code"] == "different_model_review_required"
    assert client.get(f"/v1/bridge/{document}/show", params={"include_content": True}).json() == before
    fence = {"native_context_id": "lo2", "fence": reserved.json()["fence"]}
    assert client.post(f"/v1/bridge/{document}/check", json=fence).status_code == 200
    # Simulate truthful different-model provenance using the same unconsumed
    # fixture reservation. Real callers must not relabel a same-model review.
    request["content"] = authored(
        contexts["lo2"], document, version, status, author_model="different-review-model", **extra
    )
    accepted = client.post(f"/v1/bridge/{document}/deliver", json=request)
    assert accepted.status_code == 200, accepted.text
    assert client.post(f"/v1/bridge/{document}/check", json=fence).status_code == 422


@pytest.mark.parametrize("status", ["GO", "VERIFIED"])
def test_same_declared_model_refuses_before_publication_and_preserves_claim(bridge, status):
    _, client, contexts, _ = bridge
    document = "model-admission"
    deliver(client, contexts, document, "pb1", 1, "NEW", author_model="current-producer")
    if status == "GO":
        _refuse_same_model(client, contexts, document, 2, status, " CURRENT-PRODUCER ")
    else:
        deliver(client, contexts, document, "lo1", 2, "GO")
        deliver(client, contexts, document, "pb2", 3, "READY", author_model="current-report")
        artifacts = client.get(f"/v1/bridge/{document}/artifacts").json()
        _refuse_same_model(
            client, contexts, document, 4, status, " CURRENT-REPORT ", verified_artifacts=json.dumps(artifacts)
        )


def test_go_compares_latest_revised_proposal_not_original_proposal(bridge):
    _, client, contexts, _ = bridge
    document = "revised-model"
    deliver(client, contexts, document, "pb1", 1, "NEW", author_model="original-proposal")
    deliver(client, contexts, document, "lo1", 2, "NO-GO")
    deliver(client, contexts, document, "pb2", 3, "REVISED", author_model="current-proposal")
    _refuse_same_model(client, contexts, document, 4, "GO", "current-proposal")


def test_corrected_go_compares_proposal_not_verdict_rejection_author(bridge):
    _, client, contexts, _ = bridge
    document = "corrected-go-model"
    deliver(client, contexts, document, "pb1", 1, "NEW", author_model="current-proposal")
    deliver(client, contexts, document, "lo1", 2, "GO")
    deliver(client, contexts, document, "pb2", 3, "VERDICT-REJECTED", author_model="rejection-author")
    _refuse_same_model(client, contexts, document, 4, "GO", "current-proposal")


def test_verified_compares_latest_corrected_ready_from_same_producer(bridge):
    _, client, contexts, _ = bridge
    document = "corrected-report-model"
    deliver(client, contexts, document, "pb1", 1, "NEW")
    deliver(client, contexts, document, "lo1", 2, "GO")
    deliver(client, contexts, document, "pb2", 3, "READY", author_model="earlier-report")
    deliver(client, contexts, document, "lo1", 4, "NOT-READY")
    deliver(client, contexts, document, "pb2", 5, "READY", author_model="current-report")
    artifacts = client.get(f"/v1/bridge/{document}/artifacts").json()
    _refuse_same_model(
        client, contexts, document, 6, "VERIFIED", "current-report", verified_artifacts=json.dumps(artifacts)
    )


def test_fresh_verified_compares_report_not_previous_review_model(bridge):
    _, client, contexts, root = bridge
    document = "reverification-model"
    deliver(client, contexts, document, "pb1", 1, "NEW")
    deliver(client, contexts, document, "lo1", 2, "GO")
    deliver(client, contexts, document, "pb2", 3, "READY", author_model="current-report")
    artifacts = client.get(f"/v1/bridge/{document}/artifacts").json()
    deliver(
        client,
        contexts,
        document,
        "lo1",
        4,
        "VERIFIED",
        author_model="previous-review-model",
        verified_artifacts=json.dumps(artifacts),
    )
    # A second verdict is lawful only after canonical finalization requests it.
    # Change actual reviewed bytes and let the normal prepare API identify them.
    (root / "code.py").write_text("corrected = 3\n", encoding="utf-8")
    prepared = post(client, "prepare-commit")
    assert prepared.status_code == 200, prepared.text
    assert prepared.json() == {
        "status": "fresh_verification_required",
        "reason": "verified_bytes_changed",
        "work_item_ids": ["WI-1"],
    }
    current_artifacts = client.get(f"/v1/bridge/{document}/artifacts").json()
    assert current_artifacts != artifacts
    _refuse_same_model(
        client,
        contexts,
        document,
        5,
        "VERIFIED",
        "current-report",
        verified_artifacts=json.dumps(current_artifacts),
    )


def test_missing_current_producer_model_refuses_without_guessing_from_context():
    class Cursor:
        def __init__(self):
            self.calls = []

        def execute(self, query, parameters):
            self.calls.append((query, parameters))

        def fetchone(self):
            return None

    cursor = Cursor()
    tx = SimpleNamespace(schema="isolated", cursor=cursor)
    attempt = {"id": "missing-producer", "proposal_context_id": "pb-context", "head_version": 3}
    with pytest.raises(PostgresKernelError) as error:
        NativeBridgeService._require_different_review_model(tx, attempt, "GO", "reviewer-model")
    assert error.value.code == "review_model_provenance_missing"
    assert len(cursor.calls) == 1
    assert cursor.calls[0][1] == ("missing-producer", "pb-context", ["NEW", "REVISED"], 3)
