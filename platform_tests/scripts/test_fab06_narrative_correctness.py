"""FAB-06 (WI-4418) HYG-031/037/017: always-loaded narrative correctness.

Asserts the CLAUDE.md Governance Index is the deterministic render of the
canonical MemBase GOV rows (GOV-08: the DB wins), that GOV-06 carries the DB
meaning and GOV-18 is the SPEC-1662 alias, that the Knowledge Database Access
section points at the groundtruth_kb API (not the tools/knowledge-db shim), and
that AGENTS.md no longer frames Agent Red as "not part of GT-KB".
Authority: GOV-08, GOV-AGENT-RED-GTKB-CONFORMANCE-001, DELIB-FAB06-REMEDIATION-20260610.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]


def _read(rel: str) -> str:
    return (_ROOT / rel).read_text(encoding="utf-8")


def _generator_rows() -> list[str]:
    result = subprocess.run(
        [sys.executable, str(_ROOT / "scripts" / "generate_governance_index.py")],
        capture_output=True,
        text=True,
        cwd=str(_ROOT),
    )
    assert result.returncode == 0, result.stderr
    return [ln for ln in result.stdout.splitlines() if ln.startswith("| ") and "| ID |" not in ln and "|---" not in ln]


def test_gov_index_matches_generator_output():
    rows = _generator_rows()
    assert rows, "generator produced no GOV rows"
    claude = _read("CLAUDE.md")
    missing = [ln for ln in rows if ln not in claude]
    assert not missing, f"generated GOV-index rows missing from CLAUDE.md: {missing[:3]}"


def test_gov06_canonical_meaning():
    assert "GOV-06 | Spec-first correction cycle" in _read("CLAUDE.md")


def test_gov18_is_spec1662_alias():
    assert "SPEC-1662" in _read("CLAUDE.md")


def test_kb_access_repointed_off_shim():
    claude = _read("CLAUDE.md")
    assert "tools/knowledge-db/db.py" not in claude
    assert "groundtruth_kb" in claude


def test_agents_reference_adopter_framing():
    agents = _read("AGENTS.md")
    for forbidden in ("not part of GroundTruth", "not part of GT-KB", "not GT-KB files"):
        assert forbidden not in agents, f"AGENTS.md still contains {forbidden!r}"
