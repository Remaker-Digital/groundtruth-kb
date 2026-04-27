"""Tests for Wave 2 Slice 5 _backlog_split.py.

Per ``bridge/gtkb-isolation-016-phase8-wave2-slice5-005.md`` (REVISED-2)
and ``-006`` (Codex GO with 5 implementation conditions).

All tests use ``work_list_path=`` parameter override (per Codex Slice 5
``-002`` non-blocking note 4) to point at fixture files. No
monkeypatching of module constants; no live-root walks.

The F1 regression test (``test_run_classifies_gtkb_isolation_016_as_unclassified_not_framework``)
is the minimum required by Codex ``-004`` F1: the classifier must NOT
silently land the live ``GTKB-ISOLATION-016`` row in framework_rows.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from rehearse import _backlog_split  # noqa: E402


def _build_manifest(legacy_root: Path) -> dict[str, Any]:
    return {
        "target_root": str((legacy_root / "applications" / "Agent_Red").as_posix()),
        "legacy_root": str(legacy_root.as_posix()),
        "applications_namespace": str((legacy_root / "applications").as_posix()),
        "output_dir": "C:/temp/agent-red-rehearsal",
        "git_strategy": "clone_with_history_filter",
        "excluded_paths": [],
    }


def _write_work_list(
    path: Path,
    actionable_rows: str,
    *,
    include_completed_section: bool = False,
) -> None:
    """Write a fixture work_list.md with a Next Actionable Items table.

    If ``include_completed_section=True``, append a Completed section
    that contains rows that should NOT be classified (per Codex -002
    non-blocking note 3).
    """
    content = (
        "# Active Work List\n\n"
        "## Next Actionable Items\n\n"
        "| # | ID | Status | Blocks / blocked by | Next step |\n"
        "|---|---|---|---|---|\n"
        f"{actionable_rows}\n"
    )
    if include_completed_section:
        content += (
            "\n**Completed in S308 (2026-04-25), removed from active table:**\n\n"
            "- Some completed item that should NOT appear in classifier output.\n"
            "| 99 | `GTKB-COMPLETED-001` | done | n/a | n/a |\n"
        )
    path.write_text(content, encoding="utf-8")


def test_run_dry_run_returns_skipped(tmp_path: Path) -> None:
    manifest = _build_manifest(tmp_path)
    result = _backlog_split.run(
        manifest,
        tmp_path / "out",
        dry_run=True,
        work_list_path=tmp_path / "work_list.md",
    )
    assert result["status"] == "skipped"


# ----- F1 regression guard (REQUIRED by Codex -004) -----


def test_run_classifies_gtkb_isolation_016_as_unclassified_not_framework(
    tmp_path: Path,
) -> None:
    """F1 regression: GTKB-ISOLATION-016 must NOT silently land in framework_rows.

    Per Codex bridge/gtkb-isolation-016-phase8-wave2-slice5-004.md F1
    + GO -006 condition 1: GTKB-* prefix combined with Agent Red
    migration content is conflicted; classifier must surface it as
    unclassified with the conflict signal.
    """
    work_list_path = tmp_path / "work_list.md"
    _write_work_list(
        work_list_path,
        "| 2 | `GTKB-ISOLATION-016` | actionable now | n/a | "
        "Execute non-destructive Agent Red migration rehearsal from legacy "
        "mixed root into selected child application root. |",
    )
    manifest = _build_manifest(tmp_path)

    result = _backlog_split.run(
        manifest,
        tmp_path / "out",
        dry_run=False,
        work_list_path=work_list_path,
    )
    assert result["status"] == "ok"
    bs = json.loads((tmp_path / "out" / "backlog_split" / "backlog_split.json").read_text(encoding="utf-8"))

    framework_ids = [r["id"] for r in bs["framework_rows"]]
    adopter_ids = [r["id"] for r in bs["adopter_rows"]]
    unclassified_ids = [r["id"] for r in bs["unclassified_rows"]]

    assert "GTKB-ISOLATION-016" not in framework_ids, (
        "F1 regression: GTKB-ISOLATION-016 silently auto-classified as framework"
    )
    assert "GTKB-ISOLATION-016" not in adopter_ids
    assert "GTKB-ISOLATION-016" in unclassified_ids
    conflict_entry = next(r for r in bs["unclassified_rows"] if r["id"] == "GTKB-ISOLATION-016")
    assert conflict_entry["classification_signal"] == "gtkb_prefix_with_adopter_content"
    assert any("gtkb_prefix_with_adopter_content_conflicts" in w for w in result["warnings"])


# ----- Complementary classifier tests -----


def test_run_classifies_clean_gtkb_row_as_framework(tmp_path: Path) -> None:
    """GTKB-* row with no adopter content → framework."""
    work_list_path = tmp_path / "work_list.md"
    _write_work_list(
        work_list_path,
        "| 1 | `GTKB-FRAMEWORK-WORK` | scoping | n/a | Generic framework refactor unrelated to any adopter. |",
    )
    manifest = _build_manifest(tmp_path)
    result = _backlog_split.run(
        manifest,
        tmp_path / "out",
        dry_run=False,
        work_list_path=work_list_path,
    )
    bs = json.loads((tmp_path / "out" / "backlog_split" / "backlog_split.json").read_text(encoding="utf-8"))
    framework_ids = [r["id"] for r in bs["framework_rows"]]
    assert "GTKB-FRAMEWORK-WORK" in framework_ids
    assert result["status"] == "ok"


def test_run_classifies_ar_prefix_as_adopter(tmp_path: Path) -> None:
    work_list_path = tmp_path / "work_list.md"
    _write_work_list(
        work_list_path,
        "| 1 | `AR-DASHBOARD-001` | actionable | n/a | Build adopter dashboard. |",
    )
    manifest = _build_manifest(tmp_path)
    _backlog_split.run(
        manifest,
        tmp_path / "out",
        dry_run=False,
        work_list_path=work_list_path,
    )
    bs = json.loads((tmp_path / "out" / "backlog_split" / "backlog_split.json").read_text(encoding="utf-8"))
    adopter_ids = [r["id"] for r in bs["adopter_rows"]]
    assert "AR-DASHBOARD-001" in adopter_ids
    ar_entry = next(r for r in bs["adopter_rows"] if r["id"] == "AR-DASHBOARD-001")
    assert ar_entry["classification_signal"] == "ar_prefix"


def test_run_unknown_prefix_to_unclassified(tmp_path: Path) -> None:
    work_list_path = tmp_path / "work_list.md"
    _write_work_list(
        work_list_path,
        "| 1 | `MYPROJECT-001` | actionable | n/a | Unknown project work. |",
    )
    manifest = _build_manifest(tmp_path)
    result = _backlog_split.run(
        manifest,
        tmp_path / "out",
        dry_run=False,
        work_list_path=work_list_path,
    )
    bs = json.loads((tmp_path / "out" / "backlog_split" / "backlog_split.json").read_text(encoding="utf-8"))
    unclassified_ids = [r["id"] for r in bs["unclassified_rows"]]
    assert "MYPROJECT-001" in unclassified_ids
    entry = next(r for r in bs["unclassified_rows"] if r["id"] == "MYPROJECT-001")
    assert entry["classification_signal"] == "unknown_prefix"
    assert any("unknown_prefix_rows" in w for w in result["warnings"])


def test_run_adopter_content_marker_case_insensitive(tmp_path: Path) -> None:
    """'Agent RED Migration' (mixed case) matches the marker."""
    work_list_path = tmp_path / "work_list.md"
    _write_work_list(
        work_list_path,
        "| 1 | `GTKB-MIXED-CASE` | actionable | n/a | Run Agent RED Migration tooling test. |",
    )
    manifest = _build_manifest(tmp_path)
    _backlog_split.run(
        manifest,
        tmp_path / "out",
        dry_run=False,
        work_list_path=work_list_path,
    )
    bs = json.loads((tmp_path / "out" / "backlog_split" / "backlog_split.json").read_text(encoding="utf-8"))
    unclassified_ids = [r["id"] for r in bs["unclassified_rows"]]
    framework_ids = [r["id"] for r in bs["framework_rows"]]
    assert "GTKB-MIXED-CASE" in unclassified_ids
    assert "GTKB-MIXED-CASE" not in framework_ids


def test_run_scans_blocks_blocked_by_for_adopter_content(tmp_path: Path) -> None:
    """Per Codex -006 non-blocking: blocks_blocked_by also scanned."""
    work_list_path = tmp_path / "work_list.md"
    _write_work_list(
        work_list_path,
        "| 1 | `GTKB-BLOCKED-CASE` | actionable | "
        "Blocked on Agent Red migration completion | "
        "Generic step unrelated to migration text. |",
    )
    manifest = _build_manifest(tmp_path)
    _backlog_split.run(
        manifest,
        tmp_path / "out",
        dry_run=False,
        work_list_path=work_list_path,
    )
    bs = json.loads((tmp_path / "out" / "backlog_split" / "backlog_split.json").read_text(encoding="utf-8"))
    unclassified_ids = [r["id"] for r in bs["unclassified_rows"]]
    framework_ids = [r["id"] for r in bs["framework_rows"]]
    assert "GTKB-BLOCKED-CASE" in unclassified_ids
    assert "GTKB-BLOCKED-CASE" not in framework_ids


# ----- Scoping: Next Actionable Items only -----


def test_run_does_not_classify_completed_section(tmp_path: Path) -> None:
    """Per Codex -002 non-blocking note 3: only Next Actionable Items table."""
    work_list_path = tmp_path / "work_list.md"
    _write_work_list(
        work_list_path,
        "| 1 | `GTKB-ACTIVE` | actionable | n/a | Active work. |",
        include_completed_section=True,
    )
    manifest = _build_manifest(tmp_path)
    _backlog_split.run(
        manifest,
        tmp_path / "out",
        dry_run=False,
        work_list_path=work_list_path,
    )
    bs = json.loads((tmp_path / "out" / "backlog_split" / "backlog_split.json").read_text(encoding="utf-8"))
    all_ids = (
        [r["id"] for r in bs["framework_rows"]]
        + [r["id"] for r in bs["adopter_rows"]]
        + [r["id"] for r in bs["unclassified_rows"]]
    )
    assert "GTKB-ACTIVE" in all_ids
    assert "GTKB-COMPLETED-001" not in all_ids, "Completed section row leaked into classification"


# ----- Error paths -----


def test_run_returns_error_when_work_list_missing(tmp_path: Path) -> None:
    manifest = _build_manifest(tmp_path)
    result = _backlog_split.run(
        manifest,
        tmp_path / "out",
        dry_run=False,
        work_list_path=tmp_path / "nonexistent.md",
    )
    assert result["status"] == "error"
    assert any("work_list_missing" in w for w in result["warnings"])


def test_run_returns_error_when_no_actionable_section(tmp_path: Path) -> None:
    work_list_path = tmp_path / "work_list.md"
    work_list_path.write_text(
        "# Active Work List\n\n## Some Other Section\n\nNo table here.\n",
        encoding="utf-8",
    )
    manifest = _build_manifest(tmp_path)
    result = _backlog_split.run(
        manifest,
        tmp_path / "out",
        dry_run=False,
        work_list_path=work_list_path,
    )
    assert result["status"] == "error"
    assert any("not_found_or_empty" in w for w in result["warnings"])


def test_run_returns_error_when_table_has_no_rows(tmp_path: Path) -> None:
    work_list_path = tmp_path / "work_list.md"
    work_list_path.write_text(
        "# Active Work List\n\n## Next Actionable Items\n\n"
        "| # | ID | Status | Blocks | Next step |\n"
        "|---|---|---|---|---|\n",
        encoding="utf-8",
    )
    manifest = _build_manifest(tmp_path)
    result = _backlog_split.run(
        manifest,
        tmp_path / "out",
        dry_run=False,
        work_list_path=work_list_path,
    )
    assert result["status"] == "error"
    assert any("no_rows_parsed" in w for w in result["warnings"])


# ----- result.json artifact -----


def test_run_writes_result_json_on_ok_path(tmp_path: Path) -> None:
    work_list_path = tmp_path / "work_list.md"
    _write_work_list(
        work_list_path,
        "| 1 | `AR-FOO` | actionable | n/a | Adopter work. |",
    )
    manifest = _build_manifest(tmp_path)
    result = _backlog_split.run(
        manifest,
        tmp_path / "out",
        dry_run=False,
        work_list_path=work_list_path,
    )
    result_path = tmp_path / "out" / "backlog_split" / "result.json"
    assert result_path.exists()
    on_disk = json.loads(result_path.read_text(encoding="utf-8"))
    assert on_disk == result
    assert str(result_path) in on_disk["output_files"]


def test_run_writes_result_json_on_error_path(tmp_path: Path) -> None:
    manifest = _build_manifest(tmp_path)
    result = _backlog_split.run(
        manifest,
        tmp_path / "out",
        dry_run=False,
        work_list_path=tmp_path / "missing.md",
    )
    assert result["status"] == "error"
    result_path = tmp_path / "out" / "backlog_split" / "result.json"
    assert result_path.exists()
