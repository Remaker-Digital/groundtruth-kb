"""Regression tests for SPEC_TEST_HEADING_RE re.MULTILINE in the bridge-compliance-gate hook.

SPEC_TEST_HEADING_RE is consumed via .search(content) in _has_spec_derived_verification.
Without re.MULTILINE the caret anchor matches only string offset 0, so a VERIFIED verdict
(whose content begins with the literal "VERIFIED" line) never matches its mid-document
"## Spec-to-Test Mapping" heading, and the gate hard-blocks every complete Claude-authored
VERIFIED verdict. The fix adds re.MULTILINE; these tests lock in the corrected behavior and
the preserved failure paths.

The fix is applied identically to the live hook and the scaffold template, so the
behavioral tests are parametrized over both copies.

Source: bridge/gtkb-bridge-compliance-gate-spec-test-heading-multiline-fix-001.md
(Codex GO at -002); WI-3351 under PROJECT-GTKB-RELIABILITY-FIXES;
GOV-FILE-BRIDGE-AUTHORITY-001, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001.
"""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
LIVE_HOOK = REPO_ROOT / ".claude" / "hooks" / "bridge-compliance-gate.py"
TEMPLATE_HOOK = REPO_ROOT / "groundtruth-kb" / "templates" / "hooks" / "bridge-compliance-gate.py"


def _load_gate(path: Path, module_name: str) -> ModuleType:
    """Import a hyphenated hook file by path under a unique module name."""
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_HOOKS = {
    "live": _load_gate(LIVE_HOOK, "bcg_spec_test_heading_live"),
    "template": _load_gate(TEMPLATE_HOOK, "bcg_spec_test_heading_template"),
}


@pytest.fixture(params=sorted(_HOOKS), ids=sorted(_HOOKS))
def gate(request: pytest.FixtureRequest) -> ModuleType:
    """The bridge-compliance-gate hook module, once per copy (live + template)."""
    return _HOOKS[request.param]


# --- fixture builders -------------------------------------------------------

# Built at runtime so the source file carries no literal 64-hex blob.
_CLEAN_PACKET_HASH = "packet_hash: sha256:" + "0" * 64
_SPEC_LINKS = "## Specification Links\n\n- GOV-FILE-BRIDGE-AUTHORITY-001 - canonical workflow state.\n"
_APPLICABILITY = "## Applicability Preflight\n\n" + _CLEAN_PACKET_HASH + "\nmissing_required_specs: []\n"
_SPEC_TO_TEST = (
    "## Spec-to-Test Mapping\n\n| Spec | Test |\n|------|------|\n| GOV-FILE-BRIDGE-AUTHORITY-001 | test_x |\n"
)
_COMMAND_EVIDENCE = "Executed: python -m pytest platform_tests/hooks/test_x.py\n"
_COMMIT_FINALIZATION = (
    "## Commit Finalization Evidence\n\n"
    "- Finalization helper: `.claude/skills/verify/helpers/write_verdict.py --finalize-verified`\n"
    "- Same-transaction path set:\n"
    "- `scripts/foo.py`\n"
    "- `bridge/test-sample-thread-002.md`\n"
    "- `bridge/test-sample-thread-003.md`\n"
)
_AUTHOR_METADATA = (
    "author_identity: Codex\n"
    "author_harness_id: A\n"
    "author_session_context_id: session-123\n"
    "author_model: GPT-5.5\n"
    "author_model_version: 5.5\n"
    "author_model_configuration: Extra High\n"
)


def _complete_verified_verdict() -> str:
    """A VERIFIED verdict carrying every element the gate requires."""
    return (
        "VERIFIED\n" + _AUTHOR_METADATA + "\n"
        "# Loyal Opposition Verification - Sample\n\n"
        + _SPEC_LINKS
        + "\n"
        + _APPLICABILITY
        + "\n"
        + _SPEC_TO_TEST
        + "\n"
        + _COMMAND_EVIDENCE
        + "\n"
        + _COMMIT_FINALIZATION
    )


# --- tests ------------------------------------------------------------------


def test_spec_test_heading_re_multiline_flag(gate: ModuleType) -> None:
    """SPEC_TEST_HEADING_RE carries re.MULTILINE and matches a mid-document heading."""
    assert gate.SPEC_TEST_HEADING_RE.flags & re.MULTILINE
    content = "VERIFIED\n\n# Title\n\n## Spec-to-Test Mapping\n"
    assert gate.SPEC_TEST_HEADING_RE.search(content) is not None


def test_spec_derived_verification_detects_present_mapping(gate: ModuleType) -> None:
    """A complete VERIFIED verdict passes _has_spec_derived_verification (the core regression)."""
    assert gate._has_spec_derived_verification(_complete_verified_verdict()) is True


def test_complete_verified_verdict_not_blocked(gate: ModuleType, tmp_path: Path) -> None:
    """A complete VERIFIED verdict is no longer hard-blocked by _deny_reason_for_content."""
    reason = gate._deny_reason_for_content(
        cwd_path=tmp_path,
        file_path="bridge/test-sample-thread-003.md",
        content=_complete_verified_verdict(),
        run_pending_preflight=False,
    )
    assert reason is None


def test_verified_verdict_missing_mapping_still_fails(gate: ModuleType) -> None:
    """A VERIFIED verdict lacking any spec-to-test heading still fails the gate."""
    content = "VERIFIED\n\n# Sample\n\n" + _SPEC_LINKS + "\n" + _APPLICABILITY + "\n" + _COMMAND_EVIDENCE
    assert gate._has_spec_derived_verification(content) is False


def test_verified_verdict_missing_command_evidence_still_fails(gate: ModuleType) -> None:
    """A VERIFIED verdict lacking executed-test command evidence still fails the gate."""
    content = "VERIFIED\n\n# Sample\n\n" + _SPEC_LINKS + "\n" + _APPLICABILITY + "\n" + _SPEC_TO_TEST
    assert gate._has_spec_derived_verification(content) is False
