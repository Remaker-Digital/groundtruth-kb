"""Tests for the orphan bridge-verdict file audit."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "audit_orphan_verdict_files.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("audit_orphan_verdict_files", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["audit_orphan_verdict_files"] = module
    spec.loader.exec_module(module)
    return module


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_flags_timestamped_verdict_shaped_orphan(tmp_path: Path) -> None:
    module = _load_module()
    bridge_dir = tmp_path / "bridge"
    _write(bridge_dir / "gtkb-sweep-commit-pycache-prefix-001-VERDICT-20260616T160700.md", "GO\n")

    audit = module.build_audit(tmp_path)

    assert audit["orphan_count"] == 1
    assert audit["orphans"][0]["first_line_status"] == "GO"
    assert audit["orphans"][0]["path"].endswith("gtkb-sweep-commit-pycache-prefix-001-VERDICT-20260616T160700.md")


def test_canonical_numbered_verdict_not_flagged(tmp_path: Path) -> None:
    module = _load_module()
    bridge_dir = tmp_path / "bridge"
    _write(bridge_dir / "gtkb-example-thread-002.md", "GO\n")

    audit = module.build_audit(tmp_path)

    assert audit["orphans"] == []
    assert audit["orphan_count"] == 0


def test_non_verdict_noncanonical_file_not_flagged(tmp_path: Path) -> None:
    module = _load_module()
    bridge_dir = tmp_path / "bridge"
    _write(bridge_dir / "gtkb-example-thread-draft.md", "NEW\n")

    audit = module.build_audit(tmp_path)

    assert audit["orphans"] == []


def test_flags_heading_first_lo_verdict_file(tmp_path: Path) -> None:
    module = _load_module()
    bridge_dir = tmp_path / "bridge"
    _write(
        bridge_dir / "gtkb-example-thread-001.lo-verdict.md",
        "# Loyal Opposition Review\n\nVerdict: GO\n",
    )

    audit = module.build_audit(tmp_path)

    assert audit["orphan_count"] == 1
    assert audit["orphans"][0]["first_line_status"] == "GO"
    assert audit["orphans"][0]["path"].endswith("gtkb-example-thread-001.lo-verdict.md")
    assert ".lo-verdict.md" in audit["orphans"][0]["reason"]


def test_flags_lo_verdict_section_followed_by_status(tmp_path: Path) -> None:
    module = _load_module()
    bridge_dir = tmp_path / "bridge"
    _write(
        bridge_dir / "gtkb-example-thread-001.lo-verdict.md",
        "## Loyal Opposition Verdict: gtkb-example-thread\n\n## Verdict\n\nNO-GO\n",
    )

    audit = module.build_audit(tmp_path)

    assert audit["orphan_count"] == 1
    assert audit["orphans"][0]["first_line_status"] == "NO-GO"


def test_non_verdict_bridge_markdown_with_verdict_line_not_flagged(tmp_path: Path) -> None:
    module = _load_module()
    bridge_dir = tmp_path / "bridge"
    _write(bridge_dir / "gtkb-example-thread-notes.md", "# Notes\n\nVerdict: GO\n")

    audit = module.build_audit(tmp_path)

    assert audit["orphans"] == []


def test_lo_verdict_without_verdict_content_not_flagged(tmp_path: Path) -> None:
    module = _load_module()
    bridge_dir = tmp_path / "bridge"
    _write(bridge_dir / "gtkb-example-thread-001.lo-verdict.md", "# Notes\n\nNo verdict here.\n")

    audit = module.build_audit(tmp_path)

    assert audit["orphans"] == []


def test_canonical_slug_containing_digits_not_flagged(tmp_path: Path) -> None:
    module = _load_module()
    bridge_dir = tmp_path / "bridge"
    _write(bridge_dir / "gtkb-retirement-001-013.md", "VERIFIED\n")

    audit = module.build_audit(tmp_path)

    assert audit["orphans"] == []


def test_no_orphans_reports_empty_and_exit_zero(tmp_path: Path, capsys) -> None:
    module = _load_module()
    bridge_dir = tmp_path / "bridge"
    _write(bridge_dir / "gtkb-clean-thread-001.md", "NEW\n")
    _write(bridge_dir / "gtkb-clean-thread-002.md", "VERIFIED\n")

    exit_code = module.main(["--project-root", str(tmp_path)])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "## Orphan Verdict Files" in output
    assert "No non-canonical verdict-shaped orphan bridge files found." in output


def test_json_output_lists_orphans(tmp_path: Path, capsys) -> None:
    module = _load_module()
    bridge_dir = tmp_path / "bridge"
    _write(bridge_dir / "gtkb-thread-001-VERDICT-20260616T160700.md", "NO-GO\n")

    exit_code = module.main(["--project-root", str(tmp_path), "--json"])
    output = capsys.readouterr().out
    parsed = json.loads(output)

    assert exit_code == 1
    assert parsed["orphan_count"] == 1
    assert parsed["orphans"] == [
        {
            "path": (bridge_dir / "gtkb-thread-001-VERDICT-20260616T160700.md").resolve().as_posix(),
            "first_line_status": "NO-GO",
            "reason": "verdict-shaped file name is not canonical <slug>-NNN.md",
        }
    ]
