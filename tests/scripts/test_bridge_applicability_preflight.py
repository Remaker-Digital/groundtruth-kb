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
