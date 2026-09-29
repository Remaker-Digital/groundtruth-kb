"""c120: the bridge says where a VERIFIED map belongs and which header field names an unknown harness.

M13 host I on the installed c119 (2026-09-28): the Q6 verifier put a correct verified_artifacts map below the message
header, where the parser does not read it; its deliveries were refused reviewed_artifacts_required without being told
where the map belongs until the launcher's turn limit ended the cell. PB1 delivered with its native context id as
author_harness_id and was told only that a harnesses record does not exist. Both refusals keep their codes; their
messages now name the header line and the field, and the two verifier skills state that the map is a header line.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from platform_tests.groundtruth_kb.bridge_fixtures import authored, claim, deliver
from platform_tests.groundtruth_kb.bridge_fixtures import bridge as bridge
from platform_tests.groundtruth_kb.native_fixtures import native as native

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MISSING = (
    "VERIFIED must identify the exact reviewed Git mode/object map as one header line, "
    "verified_artifacts: <JSON map>, among the key: value lines that follow the status line"
)


def _ready_for_verification(client, contexts):
    deliver(client, contexts, "chain", "pb1", 1, "NEW")
    deliver(client, contexts, "chain", "lo1", 2, "GO")
    deliver(client, contexts, "chain", "pb2", 3, "READY")
    artifacts = client.get("/v1/bridge/chain/artifacts").json()
    reserved = claim(client, "chain", "lo2", 3, "VERIFIED")
    assert reserved.status_code == 200, reserved.text
    return artifacts, {"native_context_id": "lo2", "fence": reserved.json()["fence"]}


def _refused(client, fence, content):
    response = client.post("/v1/bridge/chain/deliver", json={**fence, "content": content})
    assert response.status_code == 422, response.text
    return response.json()["error"]


@pytest.mark.integration
@pytest.mark.timeout(120)
@pytest.mark.parametrize("shape", ["line", "heading"])
def test_a_map_below_the_header_is_named_and_the_same_claim_accepts_it_as_a_header_line(bridge, shape):
    _, client, contexts, _ = bridge
    artifacts, fence = _ready_for_verification(client, contexts)
    reviewed = json.dumps(artifacts)
    below = (
        f"verified_artifacts: {reviewed}\r\n"
        if shape == "line"
        else f"## verified_artifacts\r\n\r\n```json\r\n{json.dumps(artifacts, indent=2)}\r\n```\r\n"
    )
    error = _refused(client, fence, authored(contexts["lo2"], "chain", 4, "VERIFIED") + below)
    assert error["code"] == "reviewed_artifacts_required", error
    assert error["message"] == MISSING + "; a verified_artifacts line below the header is not read", error
    accepted = client.post(
        "/v1/bridge/chain/deliver",
        json={**fence, "content": authored(contexts["lo2"], "chain", 4, "VERIFIED", verified_artifacts=reviewed)},
    )
    assert accepted.status_code == 200, accepted.text


@pytest.mark.integration
@pytest.mark.timeout(120)
def test_a_header_value_that_is_not_json_is_named(bridge):
    _, client, contexts, _ = bridge
    _, fence = _ready_for_verification(client, contexts)
    content = authored(contexts["lo2"], "chain", 4, "VERIFIED", verified_artifacts="see the body")
    error = _refused(client, fence, content)
    assert error["code"] == "reviewed_artifacts_required", error
    assert error["message"] == MISSING + "; the header's verified_artifacts value is not valid JSON", error


@pytest.mark.integration
@pytest.mark.timeout(120)
def test_a_verified_without_a_map_names_the_header_line(bridge):
    _, client, contexts, _ = bridge
    _, fence = _ready_for_verification(client, contexts)
    error = _refused(client, fence, authored(contexts["lo2"], "chain", 4, "VERIFIED"))
    assert error["code"] == "reviewed_artifacts_required" and error["message"] == MISSING, error


@pytest.mark.integration
@pytest.mark.timeout(120)
def test_an_unknown_author_harness_names_the_field_and_the_same_claim_then_delivers(bridge):
    _, client, contexts, _ = bridge
    reserved = claim(client, "chain", "pb1", 0, "NEW")
    assert reserved.status_code == 200, reserved.text
    fence = {"native_context_id": "pb1", "fence": reserved.json()["fence"]}
    content = authored(contexts["pb1"], "chain", 1, "NEW", author_harness_id="pb1")
    error = client.post("/v1/bridge/chain/deliver", json={**fence, "content": content}).json()["error"]
    assert error["code"] == "not_found", error
    details = {key: error["details"].get(key) for key in ("domain", "id", "field")}
    assert details == {"domain": "harnesses", "id": "pb1", "field": "author_harness_id"}, error
    assert "author_harness_id" in error["message"] and "gt harness list" in error["message"], error
    delivered = client.post(
        "/v1/bridge/chain/deliver", json={**fence, "content": authored(contexts["pb1"], "chain", 1, "NEW")}
    )
    assert delivered.status_code == 200, delivered.text


@pytest.mark.parametrize("skill", ["gtkb-verify", "gtkb-bridge"])
def test_both_verifier_skills_say_the_map_is_one_header_line(skill):
    text = " ".join((PROJECT_ROOT / ".agents/skills" / skill / "SKILL.md").read_text(encoding="utf-8").split())
    assert "header line" in text and "verified_artifacts: {" in text, skill
    assert "the service reads the map nowhere else" in text, skill
