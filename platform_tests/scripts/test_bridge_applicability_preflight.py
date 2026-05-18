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
    assert "config/governance/sample.toml" in harvested, (
        f"repo-rooted path mention not harvested: {sorted(harvested)}"
    )
