"""Prior Deliberations placeholder gate tests for bridge-compliance-gate."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
LIVE_HOOK = REPO_ROOT / ".claude" / "hooks" / "bridge-compliance-gate.py"
TEMPLATE_HOOK = REPO_ROOT / "groundtruth-kb" / "templates" / "hooks" / "bridge-compliance-gate.py"

AUTHOR_METADATA = (
    "author_identity: Codex\n"
    "author_harness_id: A\n"
    "author_session_context_id: session-123\n"
    "author_model: GPT-5.5\n"
    "author_model_version: 5.5\n"
    "author_model_configuration: Extra High\n"
)

UNEDITED_PLACEHOLDER = "_No prior deliberations: <fill in reason before filing>._"


def _load_gate(path: Path, module_name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(params=((LIVE_HOOK, "live"), (TEMPLATE_HOOK, "template")))
def gate(request: pytest.FixtureRequest) -> ModuleType:
    path, name = request.param
    return _load_gate(path, f"bridge_compliance_gate_prior_deliberations_{name}")


def _proposal(*, status: str = "NEW", prior_section: str, extra_body: str = "") -> str:
    return (
        f"{status}\n"
        f"{AUTHOR_METADATA}\n"
        "bridge_kind: prime_proposal\n"
        "Project Authorization: PAUTH-TEST-PRIOR-DELIBERATIONS\n"
        "Project: PROJECT-TEST-PRIOR-DELIBERATIONS\n"
        "Work Item: WI-0000\n\n"
        'target_paths: ["scripts/example.py"]\n\n'
        "## Summary\n\n"
        "Fixture proposal.\n\n"
        "## Requirement Sufficiency\n\n"
        "Existing requirements sufficient.\n\n"
        "## Specification Links\n\n"
        "- GOV-FILE-BRIDGE-AUTHORITY-001\n"
        "- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001\n\n"
        f"## Prior Deliberations\n\n{prior_section}\n\n"
        "## Specification-Derived Verification\n\n"
        "Run `python -m pytest platform_tests/hooks/test_bridge_compliance_gate_prior_deliberations.py`.\n"
        f"{extra_body}"
    )


def _implementation_report(*, prior_section: str) -> str:
    return (
        f"NEW\n{AUTHOR_METADATA}\n"
        "bridge_kind: implementation_report\n"
        "Project Authorization: PAUTH-TEST-PRIOR-DELIBERATIONS\n"
        "Project: PROJECT-TEST-PRIOR-DELIBERATIONS\n"
        "Work Item: WI-0000\n\n"
        "## Summary\n\n"
        "Fixture report.\n\n"
        "## Specification Links\n\n"
        "- GOV-FILE-BRIDGE-AUTHORITY-001\n\n"
        f"## Prior Deliberations\n\n{prior_section}\n\n"
        "## Specification-Derived Verification\n\n"
        "Run `python -m pytest platform_tests/hooks/test_bridge_compliance_gate_prior_deliberations.py`.\n"
    )


def _deny(gate: ModuleType, tmp_path: Path, content: str, file_name: str = "test-prior-delibs-001.md") -> str | None:
    scratch_cwd = tmp_path / ".gtkb-state" / "prior-deliberations-fixture"
    scratch_cwd.mkdir(parents=True, exist_ok=True)
    return gate._deny_reason_for_content(
        cwd_path=scratch_cwd,
        file_path=f"bridge/{file_name}",
        content=content,
        run_pending_preflight=False,
    )


def test_new_proposal_with_unedited_prior_deliberations_placeholder_denied(gate: ModuleType, tmp_path: Path) -> None:
    reason = _deny(gate, tmp_path, _proposal(prior_section=UNEDITED_PLACEHOLDER))

    assert reason is not None
    assert "Prior Deliberations placeholder" in reason
    assert UNEDITED_PLACEHOLDER in reason


def test_revised_proposal_with_unedited_prior_deliberations_placeholder_denied(
    gate: ModuleType, tmp_path: Path
) -> None:
    reason = _deny(
        gate,
        tmp_path,
        _proposal(status="REVISED", prior_section=UNEDITED_PLACEHOLDER),
        file_name="test-prior-delibs-003.md",
    )

    assert reason is not None
    assert "Prior Deliberations placeholder" in reason


def test_substantive_no_prior_deliberations_reason_allowed(gate: ModuleType, tmp_path: Path) -> None:
    reason = _deny(gate, tmp_path, _proposal(prior_section="_No prior deliberations: novel fixture topic._"))

    assert reason is None


def test_placeholder_literal_outside_prior_deliberations_section_allowed(gate: ModuleType, tmp_path: Path) -> None:
    content = _proposal(
        prior_section="- DELIB-1234 - prior context reviewed.",
        extra_body=(f"\n\n## Evidence\n\nThe helper literal `{UNEDITED_PLACEHOLDER}` is discussed here as evidence.\n"),
    )

    reason = _deny(gate, tmp_path, content)

    assert reason is None


def test_verdicts_are_exempt_from_prior_deliberations_placeholder_gate(gate: ModuleType, tmp_path: Path) -> None:
    content = f"NO-GO\n{AUTHOR_METADATA}\n## Prior Deliberations\n\n{UNEDITED_PLACEHOLDER}\n"

    reason = _deny(gate, tmp_path, content, file_name="test-prior-delibs-002.md")

    assert reason is None


def test_implementation_reports_are_exempt_from_prior_deliberations_placeholder_gate(
    gate: ModuleType, tmp_path: Path
) -> None:
    reason = _deny(
        gate,
        tmp_path,
        _implementation_report(prior_section=UNEDITED_PLACEHOLDER),
        file_name="test-prior-delibs-003.md",
    )

    assert reason is None
