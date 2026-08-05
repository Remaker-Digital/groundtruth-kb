from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
HELPER = REPO_ROOT / "scripts" / "harness_skill_effectiveness.py"


def _load():
    spec = importlib.util.spec_from_file_location("harness_skill_effectiveness", HELPER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_h = _load()


def _write_skill(root: Path, rel_path: str) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("---\nname: fixture\ndescription: Fixture.\n---\n\n# Fixture\n", encoding="utf-8")


def _write_profiles(root: Path) -> None:
    (root / "config" / "agent-control").mkdir(parents=True, exist_ok=True)
    skills_by_activity = {
        "ops": ["bridge"],
        "deliberation": ["decision-capture"],
        "build": ["bridge", "bridge-propose"],
        "test": ["verify"],
        "spec": ["spec-intake"],
        "project": ["projects"],
    }
    eligibility = {
        "ops": "interactive_primary",
        "deliberation": "interactive_only",
        "build": "headless_eligible",
        "test": "headless_eligible",
        "spec": "headless_eligible",
        "project": "interactive_only",
    }
    lines = ["schema_version = 1", ""]
    for activity, skills in skills_by_activity.items():
        lines.append(f"[activities.{activity}]")
        lines.append("version = 1")
        lines.append(f'headless_eligibility = "{eligibility[activity]}"')
        lines.append("skills = [" + ", ".join(f'"{skill}"' for skill in skills) + "]")
        lines.append('terminology = ["fixture"]')
        lines.append(f"[activities.{activity}.history_state]")
        lines.append('sources = ["fixture"]')
        lines.append(f"[activities.{activity}.classification]")
        lines.append('skills = "activity_only"')
        lines.append('terminology = "activity_only"')
        lines.append('history_state = "explicit_query"')
        lines.append('direction = "activity_only"')
        lines.append(f"[activities.{activity}.direction]")
        lines.append('stance = "fixture"')
        lines.append('guardrails = ["fixture"]')
        lines.append('manipulates = ["fixture"]')
        lines.append("")
    (root / "config" / "agent-control" / "activity-disposition-profiles.toml").write_text(
        "\n".join(lines), encoding="utf-8"
    )


def _write_harness_registry(root: Path) -> None:
    (root / "harness-state").mkdir(parents=True, exist_ok=True)
    (root / "harness-state" / "harness-registry.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": [
                    {"id": "A", "harness_name": "codex", "status": "active", "role": ["prime-builder"]},
                    {"id": "B", "harness_name": "claude", "status": "active", "role": ["loyal-opposition"]},
                    {"id": "C", "harness_name": "antigravity", "status": "active", "role": ["loyal-opposition"]},
                ],
            }
        ),
        encoding="utf-8",
    )


def _write_capability_registry(root: Path) -> None:
    (root / "config" / "agent-control").mkdir(parents=True, exist_ok=True)
    (root / "config" / "agent-control" / "gtkb-harness-capability-registry.toml").write_text(
        """
schema_version = 1
registry_id = "fixture"
purpose = "fixture"

[[capabilities]]
id = "skill.bridge"
kind = "skill"
canonical_name = "gtkb-bridge"
canonical_source = ".claude/skills/bridge/SKILL.md"
required_for_roles = ["prime-builder", "loyal-opposition"]
parity_class = "required"

[capabilities.claude]
surface = ".claude/skills/bridge/SKILL.md"
status = "native"

[capabilities.codex]
surface = ".codex/skills/bridge/SKILL.md"
status = "adapter"

[capabilities.antigravity]
surface = ".agent/skills/bridge/SKILL.md"
status = "adapter"

[[capabilities]]
id = "skill.bridge-propose"
kind = "skill"
canonical_name = "gtkb-bridge-propose"
canonical_source = ".claude/skills/bridge-propose/SKILL.md"
required_for_roles = ["prime-builder"]
parity_class = "required"

[capabilities.claude]
surface = ".claude/skills/bridge-propose/SKILL.md"
status = "native"

[capabilities.codex]
surface = ".codex/skills/bridge-propose/SKILL.md"
status = "fallback"
fallback = "Fixture fallback surface."

[capabilities.antigravity]
surface = ".agent/skills/bridge-propose/SKILL.md"
status = "adapter"

[[capabilities]]
id = "skill.decision-capture"
kind = "skill"
canonical_name = "gtkb-decision-capture"
canonical_source = ".claude/skills/decision-capture/SKILL.md"
required_for_roles = ["prime-builder", "loyal-opposition"]
parity_class = "required"

[capabilities.claude]
surface = ".claude/skills/decision-capture/SKILL.md"
status = "native"

[capabilities.codex]
surface = ".codex/skills/decision-capture/SKILL.md"
status = "adapter"

[capabilities.antigravity]
surface = ".agent/skills/decision-capture/SKILL.md"
status = "adapter"

[[capabilities]]
id = "skill.verify"
kind = "skill"
canonical_name = "gtkb-verify"
canonical_source = ".claude/skills/verify/SKILL.md"
required_for_roles = ["loyal-opposition"]
parity_class = "required"

[capabilities.claude]
surface = ".claude/skills/verify/SKILL.md"
status = "native"

[capabilities.codex]
surface = ".codex/skills/verify/SKILL.md"
status = "adapter"

[capabilities.antigravity]
surface = ".agent/skills/verify/SKILL.md"
status = "adapter"

[[capabilities]]
id = "skill.spec-intake"
kind = "skill"
canonical_name = "gtkb-spec-intake"
canonical_source = ".claude/skills/spec-intake/SKILL.md"
required_for_roles = ["prime-builder"]
parity_class = "required"

[capabilities.claude]
surface = ".claude/skills/spec-intake/SKILL.md"
status = "native"

[capabilities.codex]
surface = ".codex/skills/spec-intake/SKILL.md"
status = "adapter"

[capabilities.antigravity]
surface = ".agent/skills/spec-intake/SKILL.md"
status = "adapter"

[[capabilities]]
id = "skill.projects"
kind = "skill"
canonical_name = "projects"
canonical_source = ".claude/skills/projects/SKILL.md"
required_for_roles = ["prime-builder"]
parity_class = "required"

[capabilities.claude]
surface = ".claude/skills/projects/SKILL.md"
status = "native"

[capabilities.codex]
surface = ".codex/skills/projects/SKILL.md"
status = "adapter"

[capabilities.antigravity]
status = "unsupported"
reason = "Fixture unsupported surface."

[[parity_waivers]]
capability_id = "skill.projects"
harness = "antigravity"
reason_class = "harness-surface-difference"
rationale = "Fixture Antigravity does not expose project management during optimized startup."
owner_approval_ref = "DELIB-FIXTURE"
review_trigger = "fixture review"

[harnesses.antigravity]
skill_adapter_manifest = ".agent/skills/MANIFEST.json"
""".lstrip(),
        encoding="utf-8",
    )


def _write_fixture(root: Path) -> None:
    _write_profiles(root)
    _write_harness_registry(root)
    _write_capability_registry(root)
    for rel_path in (
        ".claude/skills/bridge/SKILL.md",
        ".claude/skills/bridge-propose/SKILL.md",
        ".claude/skills/decision-capture/SKILL.md",
        ".claude/skills/verify/SKILL.md",
        ".claude/skills/spec-intake/SKILL.md",
        ".claude/skills/projects/SKILL.md",
        ".codex/skills/bridge/SKILL.md",
        ".codex/skills/bridge-propose/SKILL.md",
        ".codex/skills/decision-capture/SKILL.md",
        ".codex/skills/verify/SKILL.md",
        ".codex/skills/spec-intake/SKILL.md",
        ".codex/skills/projects/SKILL.md",
        ".agent/skills/bridge/SKILL.md",
        ".agent/skills/bridge-propose/SKILL.md",
        ".agent/skills/decision-capture/SKILL.md",
        ".agent/skills/verify/SKILL.md",
        ".agent/skills/spec-intake/SKILL.md",
    ):
        _write_skill(root, rel_path)
    (root / ".agent" / "skills").mkdir(parents=True, exist_ok=True)
    (root / ".agent" / "skills" / "MANIFEST.json").write_text(
        json.dumps(
            {
                "adapters": [
                    {
                        "capability_id": "skill.bridge",
                        "adapter_relative_path": ".agent/skills/bridge/SKILL.md",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )


def _row(report, harness: str, activity: str):
    matches = [row for row in report.rows if row.harness == harness and row.activity == activity]
    assert len(matches) == 1
    return matches[0]


def test_evaluate_maps_activity_skills_to_harness_skill_evidence(tmp_path: Path) -> None:
    _write_fixture(tmp_path)

    report = _h.evaluate(tmp_path, generated_at="2026-07-06T05-20-00Z")

    codex_build = _row(report, "codex", "build")
    assert codex_build.status == _h.STATUS_WEAK
    assert codex_build.weak_skills == ("bridge-propose",)
    assert "Fixture fallback surface" in codex_build.evidence[1].disposition

    claude_build = _row(report, "claude", "build")
    assert claude_build.status == _h.STATUS_COVERED
    assert all(item.status == _h.STATUS_COVERED for item in claude_build.evidence)


def test_missing_skill_projection_is_reported_as_gap(tmp_path: Path) -> None:
    _write_fixture(tmp_path)
    (tmp_path / ".codex" / "skills" / "verify" / "SKILL.md").unlink()

    report = _h.evaluate(tmp_path, generated_at="2026-07-06T05-20-00Z")
    codex_test = _row(report, "codex", "test")

    assert codex_test.status == _h.STATUS_MISSING
    assert codex_test.missing_skills == ("verify",)
    assert codex_test.follow_on_disposition.startswith("Follow-on:")


def test_typed_waiver_is_distinct_from_missing_projection(tmp_path: Path) -> None:
    _write_fixture(tmp_path)

    report = _h.evaluate(tmp_path, generated_at="2026-07-06T05-20-00Z")
    antigravity_project = _row(report, "antigravity", "project")

    assert antigravity_project.status == _h.STATUS_TYPED_WAIVED
    assert antigravity_project.typed_waivers == ("DELIB-FIXTURE",)
    assert antigravity_project.evidence[0].status == _h.STATUS_TYPED_WAIVED


def test_manifest_projection_can_supply_missing_harness_subtable(tmp_path: Path) -> None:
    _write_fixture(tmp_path)
    registry = tmp_path / "config" / "agent-control" / "gtkb-harness-capability-registry.toml"
    text = registry.read_text(encoding="utf-8")
    text = text.replace(
        """
[capabilities.antigravity]
surface = ".agent/skills/bridge/SKILL.md"
status = "adapter"
""",
        "",
    )
    registry.write_text(text, encoding="utf-8")

    report = _h.evaluate(tmp_path, generated_at="2026-07-06T05-20-00Z")
    antigravity_ops = _row(report, "antigravity", "ops")

    assert antigravity_ops.status == _h.STATUS_COVERED
    assert antigravity_ops.evidence[0].evidence == "generated skill manifest"


def test_markdown_report_includes_summary_gaps_weak_rows_and_waivers(tmp_path: Path) -> None:
    _write_fixture(tmp_path)
    (tmp_path / ".codex" / "skills" / "verify" / "SKILL.md").unlink()
    report = _h.evaluate(tmp_path, generated_at="2026-07-06T05-20-00Z")

    markdown = _h.render_markdown_report(report)

    assert "# Harness Equivalence Phase 3 Skill Effectiveness Audit" in markdown
    assert "| `missing` | 1 |" in markdown
    assert "| `weakly-evidenced` | 1 |" in markdown
    assert "## Gaps" in markdown
    assert "`codex` / `test`" in markdown
    assert "## Typed Waivers" in markdown
    assert "DELIB-FIXTURE" in markdown


def test_write_report_is_limited_to_dropbox_prefix(tmp_path: Path) -> None:
    report_path = (
        tmp_path
        / "independent-progress-assessments"
        / "CODEX-INSIGHT-DROPBOX"
        / "HARNESS-EQUIVALENCE-PHASE-3-SKILL-EFFECTIVENESS-2026-07-06T05-20-00Z.md"
    )

    written = _h.write_report("report\n", report_path, project_root=tmp_path)

    assert written == report_path.resolve()
    assert written.read_text(encoding="utf-8") == "report\n"


def test_write_report_rejects_wrong_location_or_prefix(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="CODEX-INSIGHT-DROPBOX"):
        _h.write_report("report\n", tmp_path / "bridge" / "report.md", project_root=tmp_path)

    bad_prefix = tmp_path / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX" / "OTHER.md"
    with pytest.raises(ValueError, match="HARNESS-EQUIVALENCE-PHASE-3-SKILL-EFFECTIVENESS-"):
        _h.write_report("report\n", bad_prefix, project_root=tmp_path)
