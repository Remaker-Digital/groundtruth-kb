"""The opportunity-radar baseline teaches informative, owner-directed follow-up.

The separate projector suites qualify derivation for every declared harness.
These checks read the authored baseline, not a stale local projection/registry.
"""

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / ".agents/skills/gtkb-lo-opportunity-radar/SKILL.md"


def test_skill_file_exists_with_valid_frontmatter():
    text = SKILL.read_text(encoding="utf-8")
    frontmatter = yaml.safe_load(text.split("---", 2)[1])
    assert frontmatter["name"] == "gtkb-lo-opportunity-radar"
    assert frontmatter["description"]


def test_skill_body_declares_five_passes():
    text = SKILL.read_text(encoding="utf-8")
    for name in (
        "Defect pass",
        "Token-savings pass",
        "Deterministic-service pass",
        "Surface-eligibility pass",
        "Routing pass",
    ):
        assert name in text


def test_routing_is_informational_without_candidate_promotion():
    text = SKILL.read_text(encoding="utf-8")
    assert "native ADVISORY" in text
    assert "owner selects" in text
    assert "separate NEW" in text
    assert "advisory-router" not in text and "advisory_backlog_router" not in text


def test_radar_keeps_current_canonical_requirement_and_material_owner_choice():
    text = SKILL.read_text(encoding="utf-8")
    assert "SPEC-LO-OPPORTUNITY-RADAR-001" in text
    assert "GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001" in text
    assert "unresolved" in text and "material owner choice" in text
    assert "Required Prime Builder Owner-Grilling Gate" not in text
