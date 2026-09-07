"""The pre-commit hook carries no retired commit predicate.

Owner direction, 2026-09-07 (canon v8.92). The protected-commit authorization
gate demanded PAUTH evidence, GO packets under the forbidden ``.gtkb-state``,
or committed bridge material - none of which exists under sections 3, 6 and
17 - so its invocation was removed from ``.githooks/pre-commit``. This test
keeps it out, and keeps the gates that still have a live predicate in.

It is also the compatibility evidence the protected-artifact inventory
registry requires for a change to ``.githooks/**`` (route
``compatibility_tests``).
"""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PRE_COMMIT_HOOK = PROJECT_ROOT / ".githooks" / "pre-commit"

RETIRED_GATE = "check_protected_commit_authorization.py"
LIVE_GATES = (
    "scan_secrets.py",
    "check_dev_environment_inventory_drift.py",
    "check_ruff_format.py",
)


def _invocations(text: str, script: str) -> list[str]:
    """Return non-comment lines that invoke ``script``."""
    return [line for line in text.splitlines() if script in line and not line.lstrip().startswith("#")]


def test_pre_commit_does_not_invoke_the_retired_protected_commit_gate() -> None:
    text = PRE_COMMIT_HOOK.read_text(encoding="utf-8")
    assert _invocations(text, RETIRED_GATE) == [], (
        f"{RETIRED_GATE} is retired: project authorization is a field on the project row "
        "and gates dispatch, not commits (canon section 3)."
    )


def test_pre_commit_keeps_the_gates_with_a_live_predicate() -> None:
    text = PRE_COMMIT_HOOK.read_text(encoding="utf-8")
    for script in LIVE_GATES:
        assert _invocations(text, script), f"{script} must still run at pre-commit"
