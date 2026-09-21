"""Direct requirement intake: temporary candidates, one canonical write, discard on rejection (O-7 R24).

Carries the retained duties of the retired queue tests: intent classification, capture without any canonical
effect, confirmation that creates exactly one specification with the requested fields and attribution, refusal
of wrong targets and of a taken identity without changing data, rejection that requires a reason and writes
nothing, and the rule that rejection never retires an existing specification.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

from groundtruth_kb.authority_client import AuthorityClientError
from groundtruth_kb.spec_intake import (
    CANDIDATE_KIND,
    IntakeError,
    capture_candidate,
    classify_intent,
    confirm_candidate,
    is_implementation_bearing,
    load_candidate,
    reject_candidate,
)

pytestmark = [pytest.mark.integration, pytest.mark.timeout(300)]


@pytest.mark.parametrize(
    ("text", "expected", "bound"),
    [
        ("The system must validate all user input and require authentication before login.", "directive", (0.8, 1.0)),
        ("Just something I'm thinking about.", "exploration", (0.0, 0.5)),
        ("How does the auth flow work?", "question", (0.0, 1.0)),
        (
            "The API must not exceed 300ms and cannot process more than 100 requests per second.",
            "constraint",
            (0.0, 1.0),
        ),
        ("maybe we should add logging", "exploration", (0.0, 0.7)),
        ("I would prefer the report in JSON, ideally with a summary.", "preference", (0.0, 1.0)),
    ],
)
def test_intent_classification(text, expected, bound) -> None:
    classification, confidence = classify_intent(text)
    assert classification == expected and bound[0] <= confidence <= bound[1]


def test_implementation_bearing_follows_explicit_markers_then_type() -> None:
    assert is_implementation_bearing("requirement") and not is_implementation_bearing("architecture_decision")
    assert is_implementation_bearing("architecture_decision", {"implementation_bearing": True})
    assert not is_implementation_bearing("requirement", {"implementation_bearing": False})
    assert is_implementation_bearing("design_constraint", None, ["implementation-bearing"])


def _specs(client) -> list[str]:
    return [row["id"] for row in client.request("GET", "/v1/specifications", query={"limit": 1000})["records"]]


def test_capture_is_temporary_and_writes_nothing(native_app_authority, tmp_path) -> None:
    client = native_app_authority["client"]
    before = _specs(client)
    candidate = capture_candidate(
        "The dashboard must refresh and validate every panel.",
        proposed_title="Dashboard refresh bound",
        proposed_section="Dashboard",
        candidate_dir=tmp_path / "intake",
    )
    assert candidate["kind"] == CANDIDATE_KIND and candidate["classification"] == "directive"
    saved = Path(candidate["path"])
    assert saved.is_file() and load_candidate(saved)["candidate_id"] == candidate["candidate_id"]
    assert _specs(client) == before
    with pytest.raises(IntakeError):
        capture_candidate("   ", proposed_title="x", proposed_section="y")
    with pytest.raises(IntakeError):
        capture_candidate("text", proposed_title="x", proposed_section="y", proposed_authority="owner")


def test_confirmation_writes_exactly_one_specification_with_readback(native_app_authority, tmp_path) -> None:
    client = native_app_authority["client"]
    before = _specs(client)
    candidate = capture_candidate(
        "Exports must be restartable after a network failure.",
        proposed_title="Restartable exports",
        proposed_section="Exports",
        proposed_scope="Platform",
        proposed_authority="provisional",
        candidate_dir=tmp_path / "intake",
    )
    result = confirm_candidate(client, candidate, actor="prime-builder/spec-intake-skill")
    spec = result["spec"]
    assert result["confirmed_spec_id"] == spec["id"] and spec["version"] == 1 and spec["status"] == "active"
    assert spec["title"] == "Restartable exports" and spec["description"] == candidate["raw_text"]
    assert spec["section"] == "Exports" and spec["scope"] == "Platform" and spec["authority"] == "provisional"
    assert spec["changed_by"] == "prime-builder/spec-intake-skill"
    assert result["implementation_bearing"] is True and result["backlog"]["created"] is False
    assert result["canonical_writes"] == 1 and not Path(candidate["path"]).exists()
    assert sorted(_specs(client)) == sorted(before + [spec["id"]])
    assert client.request("GET", f"/v1/specifications/{spec['id']}") == spec


def test_taken_identity_and_wrong_targets_are_refused_without_changes(native_app_authority) -> None:
    client = native_app_authority["client"]
    candidate = capture_candidate(
        "Audit logs must be immutable.", proposed_title="Immutable audit logs", proposed_section="Audit"
    )
    first = confirm_candidate(client, candidate, actor="qualification", spec_id="SPEC-INTAKE-TAKEN")
    with pytest.raises(AuthorityClientError) as refused:
        confirm_candidate(client, candidate, actor="qualification", spec_id="SPEC-INTAKE-TAKEN")
    assert refused.value.code == "cas_conflict"
    assert client.request("GET", "/v1/specifications/SPEC-INTAKE-TAKEN") == first["spec"]
    before = _specs(client)
    for wrong in (
        first["spec"],
        {"kind": "something-else"},
        {"kind": CANDIDATE_KIND, "raw_text": ""},
        "SPEC-INTAKE-TAKEN",
    ):
        with pytest.raises(IntakeError):
            confirm_candidate(client, wrong, actor="qualification")
    assert _specs(client) == before


def test_rejection_needs_a_reason_writes_nothing_and_never_retires_a_specification(
    native_app_authority, tmp_path
) -> None:
    client = native_app_authority["client"]
    candidate = capture_candidate(
        "Retire the nightly report.",
        proposed_title="Nightly report",
        proposed_section="Reports",
        candidate_dir=tmp_path,
    )
    confirmed = confirm_candidate(client, candidate, actor="qualification")
    later = capture_candidate(
        "Retire the nightly report.",
        proposed_title="Nightly report",
        proposed_section="Reports",
        candidate_dir=tmp_path,
    )
    with pytest.raises(IntakeError):
        reject_candidate(later, "   ")
    before = _specs(client)
    result = reject_candidate(later, "duplicate of the confirmed specification")
    assert result["rejected"] and result["discarded_file"] and result["canonical_writes"] == 0
    assert not Path(later["path"]).exists()
    assert _specs(client) == before
    assert client.request("GET", f"/v1/specifications/{confirmed['confirmed_spec_id']}")["status"] == "active"
    with pytest.raises(IntakeError):
        reject_candidate(confirmed["spec"], "not a candidate")


def test_credential_shaped_text_is_named_at_capture_and_refused_at_confirmation(native_app_authority) -> None:
    client = native_app_authority["client"]
    fake_key = "AK" + "IA" + "IOSFODNN7EXAMPLEKEY"
    candidate = capture_candidate(
        f'The API must use api_key="{fake_key}" for auth', proposed_title="API auth key", proposed_section="Security"
    )
    assert candidate["sensitive"] == ["api_key", "aws_key"] and fake_key in candidate["raw_text"]
    before = _specs(client)
    with pytest.raises(IntakeError, match="credential- or PII-shaped"):
        confirm_candidate(client, candidate, actor="qualification")
    assert _specs(client) == before
    clean = capture_candidate(
        "The API must require an authenticated key for every call.",
        proposed_title="API auth",
        proposed_section="Security",
    )
    assert clean["sensitive"] == []


def test_skill_helper_delegates_with_skill_attribution(native_app_authority, tmp_path) -> None:
    helper_path = Path(__file__).resolve().parents[2] / ".agents/skills/gtkb-spec-intake/helpers/spec_intake.py"
    spec = importlib.util.spec_from_file_location("gtkb_test_native_spec_intake_helper", helper_path)
    assert spec is not None and spec.loader is not None
    helper = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = helper
    spec.loader.exec_module(helper)
    client = native_app_authority["client"]
    candidate = helper.capture_candidate(
        "Sessions must expire after 30 minutes.",
        proposed_title="Session expiry",
        proposed_section="Security",
        candidate_dir=tmp_path,
    )
    assert json.loads(Path(candidate["path"]).read_text(encoding="utf-8"))["kind"] == CANDIDATE_KIND
    result = helper.confirm_candidate(client, candidate)
    assert result["spec"]["changed_by"] == "prime-builder/spec-intake-skill"
    with pytest.raises(helper.SpecIntakeConfirmFailed):
        helper.confirm_candidate(client, candidate, spec_id=result["confirmed_spec_id"])
    with pytest.raises(helper.SpecIntakeRejectFailed):
        helper.reject_candidate(candidate, " ")
    with pytest.raises(helper.SpecIntakeCaptureFailed):
        helper.capture_candidate("", proposed_title="x", proposed_section="y")
    other = helper.capture_candidate(
        "Maybe cache the report.", proposed_title="Report cache", proposed_section="Reports"
    )
    assert helper.reject_candidate(other, "exploratory only")["canonical_writes"] == 0
