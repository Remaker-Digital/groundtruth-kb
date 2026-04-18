# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""CLI tests for ``gt project classify-tree``.

Proposal §3.4 — the new CLI subcommand must:

- Run without requiring ``groundtruth.toml`` in the target tree.
- Exit 0 on success.
- Write a deterministic report with the documented header block.
- Flag at least one ``legacy-exception`` row (fixture includes ``groundtruth.db``).
"""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from groundtruth_kb.cli import main


def _make_fixture(tmp_path: Path) -> Path:
    """Create a fixture tree with deliberate file types to exercise classification."""
    (tmp_path / "groundtruth.db").write_bytes(b"fake sqlite")
    (tmp_path / "requirements-local.txt").write_text(
        "groundtruth-kb[web,search] @ git+https://example.com/x.git@v0.2.1\n", encoding="utf-8"
    )
    (tmp_path / "requirements-test.txt").write_text(
        "groundtruth-kb[search] @ git+https://example.com/x.git@v0.2.1\n", encoding="utf-8"
    )
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("# main\n", encoding="utf-8")
    (tmp_path / "memory").mkdir()
    (tmp_path / "memory" / "notes.md").write_text("# memory notes\n", encoding="utf-8")
    (tmp_path / "bridge").mkdir()
    (tmp_path / "bridge" / "example-001.md").write_text("# bridge\n", encoding="utf-8")
    return tmp_path


def test_classify_tree_runs_without_groundtruth_toml(tmp_path: Path) -> None:
    """CLI exits 0 even though the target tree has no groundtruth.toml."""
    fixture_root = tmp_path / "fixture"
    fixture_root.mkdir()
    fixture = _make_fixture(fixture_root)

    output = tmp_path / "report.md"
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "project",
            "classify-tree",
            "--dir",
            str(fixture),
            "--output",
            str(output),
        ],
    )
    assert result.exit_code == 0, f"stdout={result.stdout} exception={result.exception}"
    assert output.exists(), "report file was not written"

    # No groundtruth.toml in fixture — command still succeeded.
    assert not (fixture / "groundtruth.toml").exists()


def test_classify_tree_report_contains_header_block(tmp_path: Path) -> None:
    """The generated Markdown report contains the documented header fields."""
    fixture = _make_fixture(tmp_path)
    output = tmp_path / "report.md"
    runner = CliRunner()
    result = runner.invoke(main, ["project", "classify-tree", "--dir", str(fixture), "--output", str(output)])
    assert result.exit_code == 0
    content = output.read_text(encoding="utf-8")
    assert "# Agent Red Classification Report" in content
    assert "- Generated:" in content
    assert "- GT-KB version:" in content
    assert "- GT-KB HEAD:" in content
    assert "- Target tree:" in content
    assert "- Target HEAD:" in content
    assert "- Total paths classified:" in content
    assert "- Owner-decision-pending rows:" in content
    # Table header.
    assert "| path | ownership | upgrade_policy | divergence_policy | notes | owner_decision_pending |" in content


def test_classify_tree_reports_legacy_exception_row(tmp_path: Path) -> None:
    """Fixture includes groundtruth.db → report contains at least one legacy-exception row."""
    fixture = _make_fixture(tmp_path)
    output = tmp_path / "report.md"
    runner = CliRunner()
    result = runner.invoke(main, ["project", "classify-tree", "--dir", str(fixture), "--output", str(output)])
    assert result.exit_code == 0
    content = output.read_text(encoding="utf-8")
    assert "legacy-exception" in content
    # Specifically: groundtruth.db must appear as legacy-exception.
    assert "| groundtruth.db | legacy-exception" in content


def test_classify_tree_flags_requirements_files_as_owner_decision_pending(tmp_path: Path) -> None:
    """GO C3: requirements-local.txt + requirements-test.txt appear as owner-decision-pending."""
    fixture = _make_fixture(tmp_path)
    output = tmp_path / "report.md"
    runner = CliRunner()
    result = runner.invoke(main, ["project", "classify-tree", "--dir", str(fixture), "--output", str(output)])
    assert result.exit_code == 0
    content = output.read_text(encoding="utf-8")
    # Both rows must appear as legacy-exception with YES in last column.
    assert "| requirements-local.txt | legacy-exception" in content
    assert "| requirements-test.txt | legacy-exception" in content
    # Extract the two lines and confirm "YES" is at end.
    lines = [
        ln for ln in content.splitlines() if "| requirements-local.txt |" in ln or "| requirements-test.txt |" in ln
    ]
    assert len(lines) == 2
    for ln in lines:
        assert ln.rstrip().endswith("YES |"), f"row missing YES marker: {ln!r}"


def test_classify_tree_owner_decision_pending_count_is_positive(tmp_path: Path) -> None:
    """Report header shows owner-decision-pending count > 0 for our fixture."""
    fixture = _make_fixture(tmp_path)
    output = tmp_path / "report.md"
    runner = CliRunner()
    result = runner.invoke(main, ["project", "classify-tree", "--dir", str(fixture), "--output", str(output)])
    assert result.exit_code == 0
    content = output.read_text(encoding="utf-8")
    for line in content.splitlines():
        if line.startswith("- Owner-decision-pending rows:"):
            count = int(line.split(":")[1].strip())
            assert count >= 3, f"expected at least 3 owner-decision-pending rows; got {count}"
            return
    raise AssertionError("owner-decision-pending count line not found")


def test_classify_tree_json_format(tmp_path: Path) -> None:
    """JSON format produces valid JSON with the same structure as markdown."""
    fixture = _make_fixture(tmp_path)
    output = tmp_path / "report.json"
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "project",
            "classify-tree",
            "--dir",
            str(fixture),
            "--output",
            str(output),
            "--format",
            "json",
        ],
    )
    assert result.exit_code == 0
    data = json.loads(output.read_text(encoding="utf-8"))
    assert "rows" in data
    assert "owner_decision_pending_rows" in data
    assert data["owner_decision_pending_rows"] >= 3
    # Each row has required fields.
    for row in data["rows"]:
        assert "path" in row
        assert "ownership" in row
        assert "upgrade_policy" in row
        assert "owner_decision_pending" in row
