"""W4 enforcement-calibration tests for the bridge-compliance gate (IP-3, IP-5).

Per bridge/gtkb-s358-w4-enforcement-calibration-005.md (Codex GO at -006);
WI-3368 under PROJECT-GTKB-GOVERNANCE-CORRECTION-S358.

IP-3 (fix 3): a Specification Links heading in a near-miss form is a
section-scanner boundary ambiguity, not a genuine missing section. It is
surfaced as an ask checkpoint rather than a hard deny; a genuinely absent
section still denies.

IP-5 (fix 5): the placeholder-content check on the Specification Links section
is evaluated per line. A citation line carrying a genuine spec-link token is
exempt -- its rationale prose may contain a placeholder-vocabulary word; a
placeholder-only section with no genuine citation is still rejected.

Linked specs: GOV-FILE-BRIDGE-AUTHORITY-001,
DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001,
DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
LIVE_HOOK = REPO_ROOT / ".claude" / "hooks" / "bridge-compliance-gate.py"
TEMPLATE_HOOK = REPO_ROOT / "groundtruth-kb" / "templates" / "hooks" / "bridge-compliance-gate.py"


def _load_gate(path: Path, module_name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_HOOKS = {
    "live": _load_gate(LIVE_HOOK, "bridge_compliance_gate_w4_live"),
    "template": _load_gate(TEMPLATE_HOOK, "bridge_compliance_gate_w4_template"),
}


@pytest.fixture(params=sorted(_HOOKS), ids=sorted(_HOOKS))
def gate(request: pytest.FixtureRequest) -> ModuleType:
    return _HOOKS[request.param]


# --- IP-3: heading-format misdetection -> ask --------------------------------


def test_compliance_gate_heading_ambiguity_asks(gate: ModuleType) -> None:
    """IP-3 (false-positive removed): an implementation proposal whose
    Specification Links heading is a near-miss form (a trailing parenthetical)
    is surfaced as an ask checkpoint, not a hard deny -- the author wrote the
    section and can confirm or correct the heading.
    """
    content = (
        "# Implementation Proposal\n\n"
        "## Specification Links (carried forward from prior revision)\n\n"
        "- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001\n"
        "- GOV-FILE-BRIDGE-AUTHORITY-001\n"
    )
    assert gate._specification_links_heading_misdetected(content) is True
    reason = gate._ask_reason_for_content("bridge/test-w4-heading-ambiguity-001.md", content)
    assert reason is not None
    assert "Specification Links heading was not recognized" in reason


def test_compliance_gate_absent_section_still_denies(gate: ModuleType, tmp_path: Path) -> None:
    """IP-3 (genuine-positive preserved): an implementation proposal with no
    Specification Links section at all -- not even a near-miss heading -- is
    still hard-denied. A genuinely absent section is not a misdetection.
    """
    content = "NEW\n\n# Implementation Proposal\n\nThis proposal changes behavior. It cites no governing rule.\n"
    reason = gate._deny_reason_for_content(
        cwd_path=tmp_path,
        file_path="bridge/test-w4-absent-section-001.md",
        content=content,
        run_pending_preflight=False,
    )
    assert reason is not None
    assert "Specification Links" in reason


# --- IP-5: per-line placeholder evaluation -----------------------------------


def test_compliance_gate_concrete_links_with_placeholder_word_passes(gate: ModuleType) -> None:
    """IP-5 (false-positive removed): a Specification Links section carrying
    genuine citation tokens is accepted even when a citation line's rationale
    prose contains a placeholder-vocabulary word.
    """
    content = (
        "# Implementation Proposal\n\n"
        "## Specification Links\n\n"
        "- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - governs spec linkage; "
        "none of the prior deliberations rejected this approach.\n"
        "- GOV-FILE-BRIDGE-AUTHORITY-001 - the bridge index is canonical workflow state.\n"
    )
    assert gate._has_concrete_spec_links(content) is True


def test_compliance_gate_placeholder_only_section_still_rejected(gate: ModuleType, tmp_path: Path) -> None:
    """IP-5 (genuine-positive preserved): a Specification Links section whose
    only content is a placeholder, with no genuine spec-link citation token,
    is still hard-denied.
    """
    content = "NEW\n\n# Implementation Proposal\n\n## Specification Links\n\n- TBD\n"
    assert gate._has_concrete_spec_links(content) is False
    reason = gate._deny_reason_for_content(
        cwd_path=tmp_path,
        file_path="bridge/test-w4-placeholder-only-001.md",
        content=content,
        run_pending_preflight=False,
    )
    assert reason is not None
    assert "Specification Links" in reason
