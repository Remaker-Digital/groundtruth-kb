"""The terminology check verifies projected guidance, never prompt-file term content.

Carries the retained duties of the legacy canonical-terminology doctor cases:
the projected configuration and primer are present for a selected harness,
the primer teaches the native retrieval route, a missing or malformed
projection is a required failure, and the retired prompt-file term contract
is refused rather than evaluated.
"""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

import pytest

from groundtruth_kb.project.doctor import (
    RETIRED_TERMINOLOGY_CONTRACT_KEYS,
    _check_canonical_terminology,
    inspect_native_application,
)

pytestmark = [pytest.mark.integration, pytest.mark.timeout(300)]
BASELINE = Path(__file__).resolve().parents[2] / ".harness-baseline-configuration/rules/canonical-terminology.toml"


def test_baseline_configuration_carries_no_prompt_file_term_contract() -> None:
    config = tomllib.loads(BASELINE.read_text(encoding="utf-8"))
    for name, profile in config["config"]["profiles"].items():
        assert not set(profile) & set(RETIRED_TERMINOLOGY_CONTRACT_KEYS), name
    assert config["config"]["defaults"]["primer_path"].endswith("canonical-terminology.md")


def test_projected_guidance_passes_and_the_native_doctor_reports_it(native_application) -> None:
    native_application.stage_baseline()
    target = native_application.scaffold("Alpha", profile="dual-agent", harnesses=("claude",))
    check = _check_canonical_terminology(target, "dual-agent")
    assert check.status == "pass" and check.required and "gt terms" in check.message
    report = inspect_native_application(native_application.client, "PROJECT-Alpha", native_application.host)
    finding = next(row for row in report["checks"] if row["name"] == "canonical terminology")
    assert finding["status"] == "pass"
    result = native_application.invoke(
        "project", "doctor", "--project-id", "PROJECT-Alpha", "--host-root", str(native_application.host), "--json"
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["checks"][-1]["name"] == "Core spec intake"


def test_without_a_selected_harness_the_check_is_informational(native_application) -> None:
    native_application.scaffold("Beta")
    report = inspect_native_application(native_application.client, "PROJECT-Beta", native_application.host)
    finding = next(row for row in report["checks"] if row["name"] == "canonical terminology")
    assert finding["status"] == "info" and finding["required"] is False


def test_missing_primer_or_configuration_is_a_required_failure(native_application) -> None:
    native_application.stage_baseline()
    target = native_application.scaffold("Alpha", profile="dual-agent", harnesses=("claude",))
    primer = target / ".claude/rules/canonical-terminology.md"
    primer.write_text("# Read current terminology\n\nSee the glossary file.\n", encoding="utf-8")
    check = _check_canonical_terminology(target, "dual-agent")
    assert check.status == "fail" and "gt terms" in check.message
    primer.unlink()
    check = _check_canonical_terminology(target, "dual-agent")
    assert check.status == "fail" and check.found is False and "upgrade" in check.message
    (target / ".claude/rules/canonical-terminology.toml").unlink()
    check = _check_canonical_terminology(target, "dual-agent")
    assert check.status == "fail" and "canonical-terminology.toml" in check.message


def test_the_checkout_projection_passes_the_check() -> None:
    checkout = Path(__file__).resolve().parents[2]
    check = _check_canonical_terminology(checkout, "dual-agent")
    assert check.status == "pass", check.message


def test_a_stale_projection_with_the_retired_contract_warns_instead_of_counting_terms(native_application) -> None:
    native_application.stage_baseline()
    target = native_application.scaffold("Alpha", profile="dual-agent", harnesses=("claude",))
    config = target / ".claude/rules/canonical-terminology.toml"
    config.write_text(
        config.read_text(encoding="utf-8").replace(
            '[config.profiles.dual-agent]\nmissing_severity = "ERROR"',
            '[config.profiles.dual-agent]\nmissing_severity = "ERROR"\nrequired_startup_terms = ["MemBase"]',
        ),
        encoding="utf-8",
    )
    check = _check_canonical_terminology(target, "dual-agent")
    assert check.status == "warning" and "required_startup_terms" in check.message and "upgrade" in check.message
