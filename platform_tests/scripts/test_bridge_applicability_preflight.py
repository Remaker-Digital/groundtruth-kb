"""Tests for mechanical bridge applicability preflight.

Governing decisions: DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001,
DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001,
ADR-ISOLATION-APPLICATION-PLACEMENT-001.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "bridge_applicability_preflight.py"

spec = importlib.util.spec_from_file_location("bridge_applicability_preflight", SCRIPT_PATH)
assert spec is not None
preflight = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["bridge_applicability_preflight"] = preflight
spec.loader.exec_module(preflight)


def _write_bridge(root: Path, bridge_id: str, content: str) -> None:
    bridge = root / "bridge"
    bridge.mkdir()
    (bridge / f"{bridge_id}-001.md").write_text(content, encoding="utf-8")
    (bridge / "INDEX.md").write_text(
        f"# Bridge Index\n\nDocument: {bridge_id}\nNEW: bridge/{bridge_id}-001.md\n",
        encoding="utf-8",
    )


def _write_config(path: Path) -> None:
    path.write_text(
        """
[[rules]]
spec_id = "ADR-ISOLATION-APPLICATION-PLACEMENT-001"
severity = "blocking"
rationale = "Application placement must honor the root boundary."
applies_when_paths_match = ["applications/**"]

[[rules]]
spec_id = "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"
severity = "advisory"
rationale = "Concrete requirements should be durable."
applies_when_content_matches = ["requirement"]
""",
        encoding="utf-8",
    )


def test_preflight_flags_missing_required_cross_cutting_spec(tmp_path: Path) -> None:
    bridge_id = "application-move"
    _write_bridge(
        tmp_path,
        bridge_id,
        """
# Proposal

target_paths: ["applications/Agent_Red/src/app.py"]

## Specification Links

- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
""",
    )
    config = tmp_path / "spec-applicability.toml"
    _write_config(config)

    packet = preflight.build_packet(
        bridge_id=bridge_id,
        index_path=tmp_path / "bridge" / "INDEX.md",
        config_path=config,
        db_path=tmp_path / "missing.db",
    )

    assert packet["preflight_passed"] is False
    assert packet["missing_required_specs"] == ["ADR-ISOLATION-APPLICATION-PLACEMENT-001"]
    assert packet["missing_advisory_specs"] == []
    assert packet["packet_hash"].startswith("sha256:")


def test_preflight_passes_when_required_spec_is_cited(tmp_path: Path) -> None:
    bridge_id = "application-move"
    _write_bridge(
        tmp_path,
        bridge_id,
        """
# Proposal

target_paths: ["applications/Agent_Red/src/app.py"]

## Specification Links

- ADR-ISOLATION-APPLICATION-PLACEMENT-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
""",
    )
    config = tmp_path / "spec-applicability.toml"
    _write_config(config)

    packet = preflight.build_packet(
        bridge_id=bridge_id,
        index_path=tmp_path / "bridge" / "INDEX.md",
        config_path=config,
        db_path=tmp_path / "missing.db",
    )

    assert packet["preflight_passed"] is True
    assert packet["missing_required_specs"] == []
    assert packet["missing_advisory_specs"] == []


def test_preflight_content_file_uses_pending_content(tmp_path: Path) -> None:
    bridge_id = "application-move"
    _write_bridge(
        tmp_path,
        bridge_id,
        """
# Proposal

target_paths: ["applications/Agent_Red/src/app.py"]

## Specification Links

- ADR-ISOLATION-APPLICATION-PLACEMENT-001
""",
    )
    pending = tmp_path / "pending.md"
    pending.write_text(
        """
# Proposal

target_paths: ["applications/Agent_Red/src/app.py"]

## Specification Links

- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
""",
        encoding="utf-8",
    )
    config = tmp_path / "spec-applicability.toml"
    _write_config(config)

    packet = preflight.build_packet(
        bridge_id=bridge_id,
        index_path=tmp_path / "bridge" / "INDEX.md",
        config_path=config,
        db_path=tmp_path / "missing.db",
        content_file=pending,
    )

    assert packet["content_source"]["mode"] == "pending_content"
    assert packet["operative_version"]["path"] == f"bridge/{bridge_id}-001.md"
    assert packet["preflight_passed"] is False
    assert packet["missing_required_specs"] == ["ADR-ISOLATION-APPLICATION-PLACEMENT-001"]


def test_preflight_content_file_passes_for_pending_compliant_content(tmp_path: Path) -> None:
    bridge_id = "application-move"
    _write_bridge(
        tmp_path,
        bridge_id,
        """
# Proposal

target_paths: ["applications/Agent_Red/src/app.py"]

## Specification Links

- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
""",
    )
    pending = tmp_path / "pending.md"
    pending.write_text(
        """
# Proposal

target_paths: ["applications/Agent_Red/src/app.py"]

## Specification Links

- ADR-ISOLATION-APPLICATION-PLACEMENT-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
""",
        encoding="utf-8",
    )
    config = tmp_path / "spec-applicability.toml"
    _write_config(config)

    packet = preflight.build_packet(
        bridge_id=bridge_id,
        index_path=tmp_path / "bridge" / "INDEX.md",
        config_path=config,
        db_path=tmp_path / "missing.db",
        content_file=pending,
    )

    assert packet["content_source"]["mode"] == "pending_content"
    assert packet["preflight_passed"] is True
    assert packet["missing_required_specs"] == []
    assert packet["missing_advisory_specs"] == []


def test_withdrawn_status_is_parsed_as_terminal_operative_version(tmp_path: Path) -> None:
    bridge_id = "retired-thread"
    bridge = tmp_path / "bridge"
    bridge.mkdir()
    (bridge / f"{bridge_id}-001.md").write_text(
        """
# Old Review

## Specification Links

- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
""",
        encoding="utf-8",
    )
    (bridge / f"{bridge_id}-002.md").write_text(
        """
# Supersession Notice

## Specification Links

- ADR-ISOLATION-APPLICATION-PLACEMENT-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
""",
        encoding="utf-8",
    )
    (bridge / "INDEX.md").write_text(
        "\n".join(
            [
                "# Bridge Index",
                "",
                f"Document: {bridge_id}",
                f"WITHDRAWN: bridge/{bridge_id}-002.md",
                f"NEW: bridge/{bridge_id}-001.md",
                "",
            ]
        ),
        encoding="utf-8",
    )
    config = tmp_path / "spec-applicability.toml"
    _write_config(config)

    packet = preflight.build_packet(
        bridge_id=bridge_id,
        index_path=bridge / "INDEX.md",
        config_path=config,
        db_path=tmp_path / "missing.db",
    )

    assert packet["operative_version"]["status"] == "WITHDRAWN"
    assert packet["operative_version"]["path"] == f"bridge/{bridge_id}-002.md"
    assert packet["preflight_passed"] is True


def test_markdown_output_contains_hook_readable_clean_fields(tmp_path: Path) -> None:
    bridge_id = "application-move"
    _write_bridge(
        tmp_path,
        bridge_id,
        """
# Proposal

target_paths: ["applications/Agent_Red/src/app.py"]

## Specification Links

- ADR-ISOLATION-APPLICATION-PLACEMENT-001
""",
    )
    config = tmp_path / "spec-applicability.toml"
    _write_config(config)

    packet = preflight.build_packet(
        bridge_id=bridge_id,
        index_path=tmp_path / "bridge" / "INDEX.md",
        config_path=config,
        db_path=tmp_path / "missing.db",
    )
    markdown = preflight.format_markdown(packet)

    assert "## Applicability Preflight" in markdown
    assert "packet_hash: `sha256:" in markdown
    assert "missing_required_specs: []" in markdown


# W4 IP-1 (gtkb-s358-w4-enforcement-calibration, WI-3368): the content-scan
# pass of extract_target_paths is anchored to an enumerated repo-directory set
# so prose word/word tokens are not harvested as repository paths.


def test_preflight_prose_slash_not_harvested() -> None:
    """W4 IP-1 (false-positive removed): prose ``word/word`` tokens (GO/NO-GO,
    and/or, read/write) are not harvested as repository paths -- the anchored
    PATH_TOKEN_RE requires an enumerated repo-directory prefix.
    """
    content = (
        "# Proposal\n\n"
        "This proposal discusses GO/NO-GO discipline, prime-builder/loyal-opposition\n"
        "roles, read/write semantics, and and/or phrasing.\n"
    )
    harvested = preflight.extract_target_paths(content)
    assert harvested == set(), f"prose word/word tokens were harvested as paths: {sorted(harvested)}"


def test_preflight_declared_and_rooted_paths_still_harvested() -> None:
    """W4 IP-1 (genuine-positive preserved): declared ``target_paths`` entries
    and repo-rooted path mentions in prose are still harvested, so every
    genuine path-keyed applicability rule still triggers (relevance closure
    preserved per DCL-SPEC-RELEVANCE-CLOSURE-001).
    """
    content = (
        "# Proposal\n\n"
        'target_paths: ["scripts/foo.py"]\n\n'
        "The change also touches config/governance/sample.toml as described.\n"
    )
    harvested = preflight.extract_target_paths(content)
    assert "scripts/foo.py" in harvested, f"declared target_paths entry not harvested: {sorted(harvested)}"
    assert "config/governance/sample.toml" in harvested, f"repo-rooted path mention not harvested: {sorted(harvested)}"


# WI-4542: SPEC_LINK_HEADING_RE was `$`-anchored immediately after the optional
# ` links?`/` references?` suffix, so a trailing qualifier (e.g.
# `## Specification Links (carried forward)`) failed to match and
# extract_spec_links returned an empty set -- the pre-filing gate then
# hard-blocked the Write with a misleading missing_required_specs list. The fix
# tolerates separator-introduced qualifiers and adds an advisory diagnostic that
# distinguishes an unrecognized heading from a genuinely-empty section, WITHOUT
# changing preflight_passed.


def test_extract_spec_links_tolerates_trailing_qualifier_headings() -> None:
    """WI-4542: separator-introduced trailing qualifiers (parenthetical, colon,
    en-dash, em-dash, hyphen) on the spec-links heading are tolerated and the
    cited spec id is harvested (the unfixed regex returned an empty set).
    """
    for heading in (
        "## Specification Links (carried forward)",
        "## Specification References (updated)",
        "## Specification Links: carried forward",
        "## Specification Links — inherited",  # em-dash
        "## Specification Links – inherited",  # en-dash
        "## Specification Links - inherited",  # hyphen
    ):
        content = f"# Proposal\n\n{heading}\n\n- ADR-ISOLATION-APPLICATION-PLACEMENT-001\n"
        harvested = preflight.extract_spec_links(content)
        assert "ADR-ISOLATION-APPLICATION-PLACEMENT-001" in harvested, (
            f"qualifier heading not harvested: {heading!r} -> {sorted(harvested)}"
        )


def test_extract_spec_links_preserves_canonical_and_bare_headings() -> None:
    """WI-4542: the widening preserves prior behavior -- canonical, bare, and
    prefixed `specification` headings still match exactly as before.
    """
    for heading in (
        "## Specification Links",
        "## Specification",
        "## Relevant Specification Links",
        "## Governing Specification References",
    ):
        content = f"# Proposal\n\n{heading}\n\n- GOV-FILE-BRIDGE-AUTHORITY-001\n"
        assert "GOV-FILE-BRIDGE-AUTHORITY-001" in preflight.extract_spec_links(content), heading


def test_extract_spec_links_does_not_over_harvest_unrelated_heading() -> None:
    """WI-4542 no-over-harvest guard: a heading that starts with 'Specification'
    but is not a links section (bare trailing words, no separator) is NOT
    treated as the spec-links section, so spec-shaped tokens under it are not
    harvested.
    """
    content = "# Proposal\n\n## Specification Format Guide\n\n- GOV-FILE-BRIDGE-AUTHORITY-001\n"
    assert preflight.extract_spec_links(content) == set()


def test_classify_spec_links_section_distinguishes_statuses() -> None:
    """WI-4542 advisory diagnostic: classify distinguishes harvested /
    section_empty / heading_unrecognized (with the offending heading) /
    no_section.
    """
    harvested = preflight.classify_spec_links_section(
        "# P\n\n## Specification Links\n\n- GOV-FILE-BRIDGE-AUTHORITY-001\n"
    )
    assert harvested["status"] == "harvested"
    assert harvested["candidate_heading"] is None

    empty = preflight.classify_spec_links_section("# P\n\n## Specification Links\n\n(none yet)\n")
    assert empty["status"] == "section_empty"

    unrecognized = preflight.classify_spec_links_section(
        "# P\n\n## Carried-Forward Specification Links\n\n- GOV-FILE-BRIDGE-AUTHORITY-001\n"
    )
    assert unrecognized["status"] == "heading_unrecognized"
    assert unrecognized["candidate_heading"] == "## Carried-Forward Specification Links"

    absent = preflight.classify_spec_links_section("# P\n\nNo spec links section here.\n")
    assert absent["status"] == "no_section"


def test_preflight_passes_with_carried_forward_qualifier_heading(tmp_path: Path) -> None:
    """WI-4542 end-to-end: a required cross-cutting spec cited under
    `## Specification Links (carried forward)` now passes the gate (the bug
    previously hard-blocked it with a misleading missing_required_specs).
    """
    bridge_id = "application-move"
    _write_bridge(
        tmp_path,
        bridge_id,
        """
# Proposal

target_paths: ["applications/Agent_Red/src/app.py"]

## Specification Links (carried forward)

- ADR-ISOLATION-APPLICATION-PLACEMENT-001
""",
    )
    config = tmp_path / "spec-applicability.toml"
    _write_config(config)
    packet = preflight.build_packet(
        bridge_id=bridge_id,
        index_path=tmp_path / "bridge" / "INDEX.md",
        config_path=config,
        db_path=tmp_path / "missing.db",
    )
    assert packet["preflight_passed"] is True
    assert packet["missing_required_specs"] == []
    assert packet["warnings"]["spec_links_section"]["status"] == "harvested"


def test_preflight_unrecognized_heading_surfaces_diagnostic_without_relaxing_gate(tmp_path: Path) -> None:
    """WI-4542: a prefix-form spec-links heading the STRICT regex rejects keeps
    the gate FAILING (harvesting stays strict) AND surfaces the advisory
    heading_unrecognized diagnostic -- proving the diagnostic does not weaken
    enforcement.
    """
    bridge_id = "application-move"
    _write_bridge(
        tmp_path,
        bridge_id,
        """
# Proposal

target_paths: ["applications/Agent_Red/src/app.py"]

## Carried-Forward Specification Links

- ADR-ISOLATION-APPLICATION-PLACEMENT-001
""",
    )
    config = tmp_path / "spec-applicability.toml"
    _write_config(config)
    packet = preflight.build_packet(
        bridge_id=bridge_id,
        index_path=tmp_path / "bridge" / "INDEX.md",
        config_path=config,
        db_path=tmp_path / "missing.db",
    )
    assert packet["preflight_passed"] is False
    assert packet["missing_required_specs"] == ["ADR-ISOLATION-APPLICATION-PLACEMENT-001"]
    diag = packet["warnings"]["spec_links_section"]
    assert diag["status"] == "heading_unrecognized"
    assert diag["candidate_heading"] == "## Carried-Forward Specification Links"
