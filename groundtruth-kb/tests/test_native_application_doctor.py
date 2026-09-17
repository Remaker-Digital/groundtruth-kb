"""Native application doctor: schema-v1 envelope, human report, failure exit, catalog-backed registry check.

These cases carry the retained R14 duties of the retired SQLite-era platform
doctor matrix and discoverability doctor cases: machine-readable JSON with
every check and its required flag, a nonzero exit on a required failure,
human output without --json, and catalog-backed application identities with
no occupancy limit.
"""

from __future__ import annotations

import json

import pytest

from groundtruth_kb.project.doctor import format_native_doctor_report, inspect_native_application

pytestmark = [pytest.mark.integration, pytest.mark.timeout(300)]

EXPECTED_CHECKS = (
    "Native authority configuration",
    "isolation:application-registry",
    "Native commit hook",
    "Platform leakage",
    "isolation:chroma-regeneratable",
    "canonical terminology",
    "Core spec intake",
)


def _doctor(host, name: str = "Alpha", *args: str):
    return host.invoke("project", "doctor", "--project-id", "PROJECT-" + name, "--host-root", str(host.host), *args)


def _check(payload: dict, name: str) -> dict:
    return next(check for check in payload["checks"] if check["name"] == name)


def test_doctor_json_emits_the_schema_v1_envelope_with_every_check(native_application) -> None:
    native_application.scaffold("Alpha", profile="dual-agent")
    result = _doctor(native_application, "Alpha", "--json")
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["schema_version"] == "1" and payload["profile"] == "dual-agent"
    assert payload["overall"] == "warning" and payload["status"] == payload["overall"], "intake is open"
    assert [check["name"] for check in payload["checks"]] == list(EXPECTED_CHECKS)
    assert all({"name", "required", "found", "status", "message"} <= set(check) for check in payload["checks"])
    assert payload["checks"][0]["required"] is True and payload["checks"][-1]["status"] == "warning"
    registry = _check(payload, "isolation:application-registry")
    assert registry["status"] == "pass" and "registered with a consistent marker" in registry["message"]
    assert payload["canonical_writes"] == 0


def test_doctor_exits_nonzero_with_json_when_a_required_check_fails(native_application) -> None:
    target = native_application.scaffold("Alpha")
    (target / ".githooks/reference-transaction").unlink()
    result = _doctor(native_application, "Alpha", "--json")
    assert result.exit_code == 1
    payload = json.loads(result.output)
    assert payload["overall"] == "fail"
    hook = _check(payload, "Native commit hook")
    assert hook["status"] == "fail" and hook["required"] is True and hook["found"] is False


def test_doctor_without_json_prints_the_human_report(native_application) -> None:
    native_application.scaffold("Alpha")
    report = inspect_native_application(native_application.client, "PROJECT-Alpha", native_application.host)
    result = _doctor(native_application, "Alpha")
    assert result.exit_code == 0, result.output
    assert result.output == format_native_doctor_report(report) + "\n"
    assert "Overall: [WARN] WARNING" in result.output and "Core spec intake" in result.output
    failing = _doctor(native_application, "Missing")
    assert failing.exit_code == 1 and "Error:" in failing.output


def test_registry_check_reports_an_inconsistent_or_missing_marker(native_application) -> None:
    target = native_application.scaffold("Alpha")
    marker = target / "application.toml"
    marker.write_text('[application]\nname = "Other"\n', encoding="utf-8")
    payload = inspect_native_application(native_application.client, "PROJECT-Alpha", native_application.host)
    registry = _check(payload, "isolation:application-registry")
    assert registry["status"] == "fail" and "Inconsistent application marker" in registry["message"]
    assert payload["overall"] == "fail"
    marker.unlink()
    payload = inspect_native_application(native_application.client, "PROJECT-Alpha", native_application.host)
    registry = _check(payload, "isolation:application-registry")
    assert registry["status"] == "fail" and registry["found"] is False and "missing" in registry["message"]


def test_several_registered_applications_are_ordinary(native_application) -> None:
    """No occupancy limit: two registered, initialized applications both pass; inspection reports both slots."""
    native_application.scaffold("Alpha")
    native_application.scaffold("Beta")
    for name in ("Alpha", "Beta"):
        result = _doctor(native_application, name, "--json")
        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)
        registry = _check(payload, "isolation:application-registry")
        assert registry["status"] == "pass" and "2 registered applications" in registry["message"]
        assert "P0" not in result.output and "occupancy" not in result.output.lower()
    inspection = native_application.invoke(
        "application", "inspect", "--host-root", str(native_application.host), "--json"
    )
    assert inspection.exit_code == 0, inspection.output
    state = json.loads(inspection.output)
    assert set(state["slots_status"]) == {"Alpha", "Beta"} and state["verdicts"] == []
