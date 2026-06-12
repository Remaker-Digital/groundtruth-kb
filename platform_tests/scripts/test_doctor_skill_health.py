# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for the skill health check and doctor integration."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "check_skill_health.py"
SRC_ROOT = REPO_ROOT / "groundtruth-kb" / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


def test_doctor_check_skill_health_clean(tmp_path: Path) -> None:
    from groundtruth_kb.project import doctor

    # Setup scripts dir and copy check_skill_health.py
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    shutil.copy(str(SCRIPT_PATH), str(scripts_dir / "check_skill_health.py"))

    # Create empty skill directories to ensure 0 findings
    skills_dir = tmp_path / ".claude" / "skills"
    skills_dir.mkdir(parents=True)

    check = doctor._check_skill_health(tmp_path)

    assert check.name == "Skill health"
    assert check.status == "pass"
    assert "No skill health findings found" in check.message


def test_doctor_check_skill_health_warnings(tmp_path: Path) -> None:
    from groundtruth_kb.project import doctor

    # Setup scripts dir and copy check_skill_health.py
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    shutil.copy(str(SCRIPT_PATH), str(scripts_dir / "check_skill_health.py"))

    # Create a skill directory with a failing SKILL.md (fenced python block)
    skill_dir = tmp_path / ".claude" / "skills" / "bad-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("```python\nprint('hello')\n```", encoding="utf-8")

    check = doctor._check_skill_health(tmp_path)

    assert check.name == "Skill health"
    assert check.status == "warning"
    assert "1 skill health finding(s) found" in check.message
