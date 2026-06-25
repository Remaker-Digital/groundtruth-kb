# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""WI-4831: SessionStart governance hook emits a ``[Shell]`` invocation hint.

Verifies ``GOV-SESSION-SELF-INITIALIZATION-001`` (startup token-reduction clause):
the SessionStart ``additionalContext`` carries a directive shell-invocation hint so
agents do not rediscover, each fresh session, that ``gt`` is invoked via PowerShell
(the Claude Bash-tool PATH lacks it) and that the canonical project venv
``groundtruth-kb/.venv`` imports ``groundtruth_kb`` without ``PYTHONPATH``.

Spec-derived per ``DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001``; bridge thread
``gtkb-wi4831-startup-shell-hint-line`` (GO at -002).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HOOK = Path(__file__).resolve().parents[2] / "groundtruth-kb" / "templates" / "hooks" / "session-start-governance.py"


def _run_hook(cwd: Path) -> str:
    """Invoke the hook as a subprocess with a minimal payload; return stdout."""
    payload = json.dumps({"cwd": str(cwd)})
    result = subprocess.run(
        [sys.executable, str(HOOK)],
        input=payload,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return result.stdout


def _additional_context(stdout: str) -> str:
    """Extract hookSpecificOutput.additionalContext from the emitted JSON."""
    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        ctx = obj.get("hookSpecificOutput", {}).get("additionalContext")
        if ctx:
            return ctx
    return ""


def test_shell_hint_present_in_startup_context(tmp_path: Path) -> None:
    ctx = _additional_context(_run_hook(tmp_path))
    assert "[Shell]" in ctx, f"missing [Shell] hint; got: {ctx!r}"
    assert "PowerShell" in ctx, f"hint must name PowerShell; got: {ctx!r}"
    # Canonical project venv (LO residual-risk correction on -002): imports
    # groundtruth_kb without PYTHONPATH; NOT the root .venv + PYTHONPATH workaround.
    assert "groundtruth-kb/.venv" in ctx, f"hint must name canonical venv; got: {ctx!r}"


def test_shell_hint_appended_not_replacing_governance_line(tmp_path: Path) -> None:
    """The existing governance line is preserved; the hint is appended."""
    ctx = _additional_context(_run_hook(tmp_path))
    assert "[Governance]" in ctx, f"governance line must remain; got: {ctx!r}"
    assert "[Shell]" in ctx
