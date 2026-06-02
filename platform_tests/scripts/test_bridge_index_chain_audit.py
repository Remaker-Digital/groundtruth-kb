"""Tests for scripts/bridge_index_chain_audit.py."""

from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from pathlib import Path
from types import ModuleType

from click.testing import CliRunner
from groundtruth_kb.cli import main as cli_main

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "bridge_index_chain_audit.py"


def _load_module(path: Path = SCRIPT_PATH, name: str = "bridge_index_chain_audit_for_test") -> ModuleType:
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _write_config(root: Path) -> Path:
    scripts_dir = root / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(SCRIPT_PATH, scripts_dir / "bridge_index_chain_audit.py")
    config = root / "groundtruth.toml"
    config.write_text(
        "\n".join(
            [
                "[groundtruth]",
                'db_path = "./groundtruth.db"',
                'project_root = "."',
                'app_title = "test"',
                'brand_mark = "GT"',
                'brand_color = "#2563eb"',
            ]
        ),
        encoding="utf-8",
    )
    return config


def _bridge_file(
    root: Path,
    slug: str,
    version: int,
    status: str,
    *,
    document: str | None = None,
    responds_to: str | None = None,
) -> None:
    bridge_dir = root / "bridge"
    bridge_dir.mkdir(parents=True, exist_ok=True)
    lines = [status, "", f"Document: {document or slug}", f"Version: {version:03d}"]
    if responds_to:
        lines.append(f"Responds to: {responds_to}")
    (bridge_dir / f"{slug}-{version:03d}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_index(root: Path, lines: list[str]) -> Path:
    bridge_dir = root / "bridge"
    bridge_dir.mkdir(parents=True, exist_ok=True)
    index = bridge_dir / "INDEX.md"
    index.write_text("# Bridge Index\n\n" + "\n".join(lines) + "\n", encoding="utf-8")
    return index


def test_index_chain_audit_reports_requested_deviation_types(tmp_path: Path) -> None:
    module = _load_module()
    _bridge_file(tmp_path, "status-mismatch", 1, "NO-GO")
    _bridge_file(tmp_path, "duplicate-version", 2, "GO", responds_to="bridge/duplicate-version-001.md")
    _bridge_file(tmp_path, "skipped", 1, "NEW")
    _bridge_file(tmp_path, "skipped", 3, "VERIFIED", responds_to="bridge/skipped-002.md")
    _bridge_file(tmp_path, "responds-mismatch", 1, "NEW")
    _bridge_file(tmp_path, "responds-mismatch", 2, "GO", responds_to="bridge/other-thread-001.md")
    _bridge_file(tmp_path, "latest", 1, "NEW")
    _bridge_file(tmp_path, "latest", 2, "GO", responds_to="bridge/latest-001.md")
    _bridge_file(tmp_path, "latest", 3, "VERIFIED")
    _bridge_file(tmp_path, "orphan", 1, "NEW")
    _write_index(
        tmp_path,
        [
            "Document: missing-file",
            "NEW: bridge/missing-file-001.md",
            "",
            "Document: status-mismatch",
            "GO: bridge/status-mismatch-001.md",
            "",
            "Document: duplicate-version",
            "GO: bridge/duplicate-version-002.md",
            "GO: bridge/duplicate-version-002.md",
            "",
            "Document: skipped",
            "VERIFIED: bridge/skipped-003.md",
            "NEW: bridge/skipped-001.md",
            "",
            "Document: responds-mismatch",
            "GO: bridge/responds-mismatch-002.md",
            "NEW: bridge/responds-mismatch-001.md",
            "",
            "Document: latest",
            "GO: bridge/latest-002.md",
            "NEW: bridge/latest-001.md",
            "",
        ],
    )

    result = module.run_audit(project_root=tmp_path)
    issue_types = {issue["type"] for issue in result["issues"]}

    assert {
        "index_references_missing_file",
        "index_status_body_mismatch",
        "duplicate_index_version",
        "duplicate_index_path",
        "missing_intermediate_versions",
        "responds_to_mismatch",
        "latest_index_omits_highest_file",
        "versioned_bridge_file_unindexed",
    }.issubset(issue_types)
    assert all(issue["candidate_repair_actions"] for issue in result["issues"])


def test_index_chain_audit_is_read_only(tmp_path: Path) -> None:
    module = _load_module()
    _bridge_file(tmp_path, "thread-a", 1, "NEW")
    index = _write_index(tmp_path, ["Document: thread-a", "NEW: bridge/thread-a-001.md", ""])
    file_path = tmp_path / "bridge" / "thread-a-001.md"
    before_index = index.read_text(encoding="utf-8")
    before_file = file_path.read_text(encoding="utf-8")

    result = module.run_audit(project_root=tmp_path)

    assert result["source_authority"]["mutation"] == "none; read-only audit"
    assert index.read_text(encoding="utf-8") == before_index
    assert file_path.read_text(encoding="utf-8") == before_file


def test_gt_bridge_reconcile_index_chain_json_cli(tmp_path: Path) -> None:
    config = _write_config(tmp_path)
    _bridge_file(tmp_path, "thread-a", 1, "NEW")
    _bridge_file(tmp_path, "thread-a", 2, "GO", responds_to="bridge/thread-a-001.md")
    _write_index(tmp_path, ["Document: thread-a", "GO: bridge/thread-a-002.md", "NEW: bridge/thread-a-001.md", ""])

    result = CliRunner().invoke(cli_main, ["--config", str(config), "bridge", "reconcile", "index-chain", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["source_authority"]["bridge"] == "fresh bridge/INDEX.md plus on-disk bridge files"
    assert payload["issue_count"] == 0
