"""A fresh application consumes the native authority; no placeholder endpoint or local store is configured."""

from __future__ import annotations

import tomllib

from groundtruth_kb.project.doctor import inspect_native_application
from groundtruth_kb.project.doctor_isolation import run_isolation_checks


def test_clean_adopter_selects_the_native_authority(clean_adopter, native_application) -> None:
    adopter, _host = clean_adopter
    config = tomllib.loads((adopter / "groundtruth.toml").read_text(encoding="utf-8"))
    assert config["groundtruth"]["authority_url"] == native_application.client.url
    assert "db_path" not in config["groundtruth"] and "service" not in config
    assert config["project"]["profile"] == "dual-agent"


def test_clean_adopter_service_endpoint_check_passes(clean_adopter) -> None:
    adopter, host = clean_adopter
    checks = {check.name: check for check in run_isolation_checks(adopter, "dual-agent", product_root=host.parent)}
    assert checks["isolation:service-endpoint"].status == "pass"


def test_project_doctor_reports_a_matching_configuration_and_hook(clean_adopter, native_application) -> None:
    adopter, host = clean_adopter
    report = inspect_native_application(native_application.client, "PROJECT-Alpha", host)
    findings = {row["name"]: row for row in report["checks"]}
    assert findings["Native authority configuration"]["status"] == "pass"
    assert findings["Native commit hook"]["status"] == "pass"
    assert findings["Platform leakage"]["status"] == "pass"
    assert findings["isolation:chroma-regeneratable"]["status"] == "pass"
    assert findings["Core spec intake"]["status"] == "warning", "intake is open until the owner answers"
    assert report["status"] == "warning" and report["canonical_writes"] == 0
    assert report["target"] == str(adopter)
