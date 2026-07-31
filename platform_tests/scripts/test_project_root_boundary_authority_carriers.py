from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RULE_PATH = REPO_ROOT / ".claude" / "rules" / "project-root-boundary.md"
UPGRADE_RECIPE_PATH = REPO_ROOT / "groundtruth-kb" / "templates" / "project" / "upgrade-rehearsal-recipe.md"
TERMINOLOGY_PATH = REPO_ROOT / "groundtruth-kb" / "templates" / "rules" / "canonical-terminology.md"


EXCEPTION_CARRIERS = {
    "Sandbox Output Exception": (
        "DCL-PROJECT-ROOT-BOUNDARY-SANDBOX-OUTPUT-EXCEPTION-001",
        "DELIB-S325-PROJECT-ROOT-BOUNDARY-SANDBOX-EXCEPTION-CHOICE",
    ),
    "DB-Snapshot Output Exception": (
        "DCL-PROJECT-ROOT-BOUNDARY-DB-SNAPSHOT-OUTPUT-EXCEPTION-001",
        "DELIB-FAB03-ROOT-BOUNDARY-EXCEPTION-20260611",
    ),
    "External Harness Executable Resolution Exception": (
        "DCL-PROJECT-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXEC-EXCEPTION-001",
        "DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION",
    ),
}


def _exception_section(rule_text: str, heading: str) -> str:
    _, section = rule_text.split(f"## {heading}", maxsplit=1)
    return section.split("\n## ", maxsplit=1)[0]


def test_root_boundary_exceptions_use_dcls_as_authority() -> None:
    rule_text = RULE_PATH.read_text(encoding="utf-8")

    for heading, (carrier, provenance) in EXCEPTION_CARRIERS.items():
        section = _exception_section(rule_text, heading)

        assert f"Authority: `{carrier}`" in section
        assert f"Provenance: `{provenance}`" in section
        assert "Source:" not in section


def test_adopter_templates_cite_the_canonical_carrier_pattern() -> None:
    upgrade_recipe = UPGRADE_RECIPE_PATH.read_text(encoding="utf-8")
    terminology = TERMINOLOGY_PATH.read_text(encoding="utf-8")

    assert "DCL-PROJECT-ROOT-BOUNDARY-SANDBOX-OUTPUT-EXCEPTION-001" in upgrade_recipe
    assert "DELIB-S324-PROJECT-ROOT-BOUNDARY-SANDBOX-EXCEPTION-CHOICE" in upgrade_recipe
    assert "provenance" in upgrade_recipe
    for carrier, _ in EXCEPTION_CARRIERS.values():
        assert carrier in terminology
