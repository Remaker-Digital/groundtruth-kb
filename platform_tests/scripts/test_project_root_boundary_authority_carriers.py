from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RULE_PATH = REPO_ROOT / ".claude" / "rules" / "project-root-boundary.md"
BASELINE_RULE_PATH = REPO_ROOT / ".harness-baseline-configuration" / "rules" / "project-root-boundary.md"


EXCEPTION_CARRIERS = {
    "Sandbox Output Exception": (
        "DCL-PROJECT-ROOT-BOUNDARY-SANDBOX-OUTPUT-EXCEPTION-001",
        "DELIB-S325-PROJECT-ROOT-BOUNDARY-SANDBOX-EXCEPTION-CHOICE",
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
    """The baseline rule every harness and initialized application receives carries the exception authorities.

    The rehearsal recipe template retired with the legacy upgrade wrapper (O-7 R18) and the terminology rule is
    retrieval guidance only; the projected boundary rule is the adopter-facing carrier.
    """
    baseline = BASELINE_RULE_PATH.read_text(encoding="utf-8")
    for heading, (carrier, provenance) in EXCEPTION_CARRIERS.items():
        section = _exception_section(baseline, heading)
        assert f"Authority: `{carrier}`" in section
        assert f"Provenance: `{provenance}`" in section
