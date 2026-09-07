"""W0.3 item 4: gate-message remedies.

(a) `scripts/_kb_attribution.py` missing/mismatched-session error states the
verbatim envelope-open remedy.
(b) `scripts/adr_dcl_clause_preflight.py` exit-5 output carries the per-clause
`Evidence required:` hint on the lifecycle-error / no-operative-file output
paths.

Authority: bridge/gtkb-w0-gate-false-positive-repair-001.md item 4 (GO at -002).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]


def test_kb_attribution_error_contains_envelope_open_remedy() -> None:
    # The _kb_attribution missing-session error must state the verbatim remedy
    # (open an envelope, then set the session-id env var) so agents are not
    # misdirected to add more env vars.
    src = (_ROOT / "scripts/_kb_attribution.py").read_text(encoding="utf-8")
    assert "gt session envelope open" in src
    assert "--harness-name" in src
    assert "SESSION_ID" in src


def test_adr_dcl_exit5_contains_evidence_hint() -> None:
    # No-operative-file path: exit 5 output must contain the Evidence hint.
    r = subprocess.run(
        [sys.executable, str(_ROOT / "scripts/adr_dcl_clause_preflight.py"), "--bridge-id", "gtkb-no-such-thread-xyz"],
        cwd=_ROOT,
        capture_output=True,
        text=True,
    )
    assert r.returncode == 5
    assert "Evidence required:" in r.stdout
