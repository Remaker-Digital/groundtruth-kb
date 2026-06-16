"""Tests for scripts/check_skill_health.py (Slice 0 skill-health checker).

Spec-derived per bridge gtkb-skill-modernization-slice-0-skill-health-checker
(Codex GO at -002); WI-3451; GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 +
ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 + DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import check_skill_health as chk  # noqa: E402

_PY_FENCE = "```python"
_FENCE_CLOSE = "```"


def _make_skill(tmp_path: Path, rel: str, body: str) -> Path:
    path = tmp_path / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


# --- detection unit tests (pure scan_text) ----------------------------------


def test_detects_inline_db_mutation() -> None:
    text = f"## Step 3\n{_PY_FENCE}\nwi = db.insert_work_item(id='WI-1')\n{_FENCE_CLOSE}\n"
    findings = chk.scan_text(text, ".claude/skills/x/SKILL.md")
    assert any(f.finding_type == "db_mutation" for f in findings)


def test_detects_sql_mutation_snippet() -> None:
    text = "Run: INSERT INTO work_items (id) VALUES ('WI-1');\n"
    findings = chk.scan_text(text, "x")
    assert any(f.finding_type == "db_mutation" for f in findings)


def test_detects_fenced_python_block() -> None:
    text = f"intro\n{_PY_FENCE}\nprint(1)\n{_FENCE_CLOSE}\n"
    findings = chk.scan_text(text, "x")
    assert any(f.finding_type == "fenced_python" for f in findings)


def test_detects_direct_bridge_write_instruction() -> None:
    text = "Then edit bridge/gtkb-some-topic-001.md manually.\n"
    findings = chk.scan_text(text, "x")
    assert any(f.finding_type == "bridge_direct_write" for f in findings)


def test_bridge_write_suppressed_by_governed_helper() -> None:
    text = "File the entry via bridge-propose, which updates bridge/gtkb-some-topic-001.md for you.\n"
    findings = chk.scan_text(text, "x")
    assert not any(f.finding_type == "bridge_direct_write" for f in findings)


def test_clean_skill_passes() -> None:
    text = "Run `gt backlog add --title ...` to capture the work item.\nNo code blocks here.\n"
    findings = chk.scan_text(text, "x")
    assert findings == []


# --- run() + report + read-only behavior ------------------------------------


def test_emits_structured_report(tmp_path: Path) -> None:
    _make_skill(
        tmp_path,
        ".claude/skills/dirty/SKILL.md",
        f"{_PY_FENCE}\ndb.insert_test(id='T')\n{_FENCE_CLOSE}\n",
    )
    report = chk.run([".claude/skills"], "run-test", "2026-05-29T00:00:00+00:00", tmp_path)
    out_dir = chk.write_run_outputs("run-test", report, tmp_path)

    report_json = out_dir / "report.json"
    assert report_json.is_file()
    assert (out_dir / "summary.md").is_file()

    data = json.loads(report_json.read_text(encoding="utf-8"))
    for field in ("run_id", "generated_at", "skills_scanned", "findings_by_type", "findings"):
        assert field in data
    assert data["findings"], "expected at least one finding for the dirty fixture"
    for finding in data["findings"]:
        for field in ("skill_path", "finding_type", "line", "snippet"):
            assert field in finding


def test_checker_is_read_only(tmp_path: Path) -> None:
    skill = _make_skill(
        tmp_path,
        ".claude/skills/x/SKILL.md",
        f"{_PY_FENCE}\ndb.insert_work_item(id='W')\n{_FENCE_CLOSE}\n",
    )
    before_bytes = skill.read_bytes()
    before_mtime = skill.stat().st_mtime_ns

    chk.run([".claude/skills"], "run-ro", "2026-05-29T00:00:00+00:00", tmp_path)

    assert skill.read_bytes() == before_bytes
    assert skill.stat().st_mtime_ns == before_mtime
    # The read-only checker must not create a database in the scanned tree.
    assert not (tmp_path / "groundtruth.db").exists()


# --- exit-code contract (warn-only advisory phase) --------------------------


def test_warn_only_exit_zero(tmp_path: Path) -> None:
    _make_skill(
        tmp_path,
        ".claude/skills/x/SKILL.md",
        f"{_PY_FENCE}\ndb.insert_work_item(id='W')\n{_FENCE_CLOSE}\n",
    )
    report = chk.run([".claude/skills"], "run-x", "2026-05-29T00:00:00+00:00", tmp_path)
    assert report.findings
    assert chk.exit_code_for(report, warn_only=True) == 0
    assert chk.exit_code_for(report, warn_only=False) == 1


def test_clean_tree_exit_zero(tmp_path: Path) -> None:
    _make_skill(tmp_path, ".claude/skills/clean/SKILL.md", "Use `gt backlog add` to capture work.\n")
    report = chk.run([".claude/skills"], "run-clean", "2026-05-29T00:00:00+00:00", tmp_path)
    assert report.findings == []
    assert chk.exit_code_for(report, warn_only=False) == 0
