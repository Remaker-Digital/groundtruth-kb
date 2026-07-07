"""Tests for the WI-4754 command-surface roadmap disposition helper."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT / "scripts"))
import command_surface_disposition as helper  # noqa: E402

_CONFIG = _REPO_ROOT / "config" / "agent-control" / "command-surface.toml"


def test_config_covers_every_preserved_cs2_plus_slice() -> None:
    disposition = helper.load_disposition(_CONFIG)
    assert tuple(item.id for item in disposition.slices) == helper.EXPECTED_SLICE_IDS
    assert disposition.roadmap_id == "GTKB-COMMAND-SURFACE"
    assert disposition.work_item == "WI-4754"


def test_every_slice_has_terminal_disposition_and_harness_parity_text() -> None:
    disposition = helper.load_disposition(_CONFIG)
    for item in disposition.slices:
        assert item.disposition in helper.ALLOWED_DISPOSITIONS
        assert item.rationale
        assert item.harness_parity_disposition


def test_surviving_child_work_is_bridge_and_pauth_gated() -> None:
    disposition = helper.load_disposition(_CONFIG)
    surviving = [item for item in disposition.slices if item.survives_as_child_work]
    assert {item.id for item in surviving} == {"CS-2", "CS-3", "CS-4", "CS-5+"}
    for item in surviving:
        assert item.child_slice
        assert item.required_target_paths
        assert item.required_specs
        assert item.pauth_needed is True
        assert item.bridge_proposal_needed is True


def test_init_and_wrap_are_preserved_as_covered_behaviors() -> None:
    disposition = helper.load_disposition(_CONFIG)
    cs3 = next(item for item in disposition.slices if item.id == "CS-3")
    covered = "\n".join(cs3.covered_behaviors)
    assert "::init" in covered
    assert "::wrap" in covered
    assert "generic dispatcher" in covered


def test_markdown_report_lists_child_target_paths_and_bridge_requirements() -> None:
    disposition = helper.load_disposition(_CONFIG)
    report = helper.render_markdown(disposition)
    assert "## Surviving Child Work" in report
    assert "fresh bridge proposal" in report
    assert "GTKB-COMMAND-SURFACE-CS-2-DISPATCHER-HOOK" in report
    assert "`.claude/hooks/command-dispatcher.py`" in report
    assert "`DCL-CROSS-HARNESS-ENFORCEMENT-001`" in report


def test_main_emits_json(capsys: pytest.CaptureFixture[str]) -> None:
    rc = helper.main(["--project-root", str(_REPO_ROOT), "--format", "json"])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["work_item"] == "WI-4754"
    assert len(payload["slices"]) == len(helper.EXPECTED_SLICE_IDS)


def test_main_writes_markdown_output(tmp_path: Path) -> None:
    output = tmp_path / "report.md"
    rc = helper.main(["--project-root", str(_REPO_ROOT), "--output", str(output)])
    assert rc == 0
    text = output.read_text(encoding="utf-8")
    assert text.startswith("# Command-Surface Roadmap Disposition")
    assert "CS-7" in text


def test_loader_rejects_missing_slice(tmp_path: Path) -> None:
    bad_config = tmp_path / "command-surface.toml"
    bad_config.write_text(
        """
schema_version = 1
roadmap_id = "GTKB-COMMAND-SURFACE"
source_bridge = "bridge/gtkb-command-surface-003.md"
verified_architecture_bridge = "bridge/gtkb-command-surface-006.md"
project = "PROJECT-HARNESS-PARITY-PHASE-2"
work_item = "WI-4754"
project_authorization = "PAUTH"

[[slices]]
id = "CS-2"
title = "only one"
disposition = "retire"
child_slice = ""
rationale = "x"
harness_parity_disposition = "x"
required_target_paths = []
required_specs = []
pauth_needed = false
bridge_proposal_needed = false
""",
        encoding="utf-8",
    )
    with pytest.raises(helper.DispositionConfigError, match="missing required"):
        helper.load_disposition(bad_config)
