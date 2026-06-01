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

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ACTIVE_HOOK = REPO_ROOT / ".claude" / "hooks" / "bridge-compliance-gate.py"

# Body-status-token rule (GTKB-GOV-PROPOSAL-STANDARDS Slice 1): the rule blocks a
# heading-first first line only for VERSIONED bridge files (bridge/<slug>-NNN.md).
# These calibration fixtures isolate the Specification Links section-scanner, so
# they use NON-VERSIONED bridge paths (no -NNN suffix): the body-status-token rule
# exempts them, while _is_bridge_markdown_file still routes them through the
# spec-links logic under test. (Leading a fixture with NEW instead would subject it
# to the pending-applicability-preflight, which hard-denies a minimal fixture whose
# fake bridge id is absent from bridge/INDEX.md.) The versioned-heading-first BLOCK
# behavior is covered by test_bridge_compliance_gate_body_status_token.py.


def _run_hook(file_path: str, content: str) -> dict:
    """Run the live bridge-compliance gate on a Write payload and return the
    parsed hook output ({} for pass)."""
    payload = json.dumps(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {"file_path": file_path, "content": content},
            "session_id": "test",
            "cwd": str(REPO_ROOT),
        }
    )
    result = subprocess.run(
        ["python", str(ACTIVE_HOOK)],
        input=payload,
        capture_output=True,
        text=True,
        timeout=15,
        cwd=str(REPO_ROOT),
    )
    assert result.returncode == 0, f"hook exited non-zero: {result.stderr}"
    return json.loads(result.stdout) if result.stdout.strip() else {}


def _decision(output: dict) -> str | None:
    return output.get("hookSpecificOutput", {}).get("permissionDecision")


# --- IP-3: heading-format misdetection -> ask --------------------------------


def test_compliance_gate_heading_ambiguity_asks() -> None:
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
    output = _run_hook("bridge/test-w4-heading-ambiguity.md", content)
    assert _decision(output) == "ask", f"heading-format ambiguity must ask, not deny/pass; got {output}"


def test_compliance_gate_absent_section_still_denies() -> None:
    """IP-3 (genuine-positive preserved): an implementation proposal with no
    Specification Links section at all -- not even a near-miss heading -- is
    still hard-denied. A genuinely absent section is not a misdetection.
    """
    content = "# Implementation Proposal\n\nThis proposal changes behavior. It cites no governing rule.\n"
    output = _run_hook("bridge/test-w4-absent-section.md", content)
    assert _decision(output) == "deny", f"a genuinely absent section must still deny; got {output}"
    assert "Specification Links" in output.get("hookSpecificOutput", {}).get("permissionDecisionReason", "")


# --- IP-5: per-line placeholder evaluation -----------------------------------


def test_compliance_gate_concrete_links_with_placeholder_word_passes() -> None:
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
    output = _run_hook("bridge/test-w4-placeholder-word.md", content)
    assert _decision(output) != "deny", (
        f"a section with genuine citations must not be denied for a placeholder word in rationale; got {output}"
    )


def test_compliance_gate_placeholder_only_section_still_rejected() -> None:
    """IP-5 (genuine-positive preserved): a Specification Links section whose
    only content is a placeholder, with no genuine spec-link citation token,
    is still hard-denied.
    """
    content = "# Implementation Proposal\n\n## Specification Links\n\n- TBD\n"
    output = _run_hook("bridge/test-w4-placeholder-only.md", content)
    assert _decision(output) == "deny", f"a placeholder-only section must still deny; got {output}"
