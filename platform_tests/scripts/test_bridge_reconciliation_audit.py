"""Tests for scripts/bridge_reconciliation_audit.py."""

from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from pathlib import Path
from types import ModuleType

from click.testing import CliRunner
from groundtruth_kb.cli import main as cli_main
from groundtruth_kb.db import KnowledgeDB

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "bridge_reconciliation_audit.py"
WRAPPER_PATH = REPO_ROOT / "scripts" / "bridge_backlog_terminal_reconciliation.py"


def _load_module(path: Path = SCRIPT_PATH, name: str = "bridge_reconciliation_audit_for_test") -> ModuleType:
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
    shutil.copy(SCRIPT_PATH, scripts_dir / "bridge_reconciliation_audit.py")
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


def _write_index(root: Path, statuses: dict[str, str], *, omit_files: set[str] | None = None) -> Path:
    bridge_dir = root / "bridge"
    bridge_dir.mkdir(parents=True, exist_ok=True)
    omit = omit_files or set()
    lines = ["# Bridge Index", ""]
    for slug, status in statuses.items():
        version = "002" if status == "VERIFIED" else "001"
        path = bridge_dir / f"{slug}-{version}.md"
        if slug not in omit:
            path.write_text(f"{status}\n\n# {slug}\n", encoding="utf-8")
        lines.extend([f"Document: {slug}", f"{status}: bridge/{slug}-{version}.md", ""])
    index = bridge_dir / "INDEX.md"
    index.write_text("\n".join(lines), encoding="utf-8")
    return index


def _append_bridge_text(root: Path, slug: str, text: str, *, version: str = "002") -> None:
    path = root / "bridge" / f"{slug}-{version}.md"
    path.write_text(path.read_text(encoding="utf-8") + f"\n{text}\n", encoding="utf-8")


def _insert_work_item(
    db: KnowledgeDB,
    item_id: str,
    related: object,
    *,
    resolution_status: str = "open",
    stage: str = "backlogged",
    completion_evidence: str | None = None,
) -> None:
    db.insert_work_item(
        item_id,
        f"{item_id} title",
        "new",
        "platform",
        resolution_status,
        "test",
        "seed",
        stage=stage,
        related_bridge_threads=json.dumps(related) if not isinstance(related, str) else related,
        completion_evidence=completion_evidence,
    )


def _classes(result: dict[str, object]) -> set[str]:
    return {issue["class"] for issue in result["issues"]}  # type: ignore[index]


def test_audit_reports_all_six_reconciliation_buckets(tmp_path: Path) -> None:
    module = _load_module()
    _write_index(
        tmp_path,
        {
            "missing-file": "VERIFIED",
            "thread-a": "VERIFIED",
            "thread-b": "VERIFIED",
            "thread-c": "VERIFIED",
        },
        omit_files={"missing-file"},
    )
    _append_bridge_text(tmp_path, "thread-a", "Work Item: WI-1001")
    _append_bridge_text(tmp_path, "thread-c", "Work Item: WI-9999")
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        _insert_work_item(db, "WI-1001", ["thread-a"])
        _insert_work_item(db, "WI-1002", ["missing-related"])
        _insert_work_item(db, "WI-1003", [], resolution_status="resolved", stage="resolved")
    finally:
        db.close()

    result = module.run_audit(project_root=tmp_path)

    assert _classes(result) == {
        "bridge_index_drift",
        "missing_or_incorrect_related_bridge_threads",
        "stale_backlog_status",
        "terminal_backlog_without_evidence",
        "verified_bridge_missing_terminal_backlog_state",
        "verified_bridge_without_backlog_match",
    }
    assert result["counts_by_class"]["bridge_index_drift"] >= 1
    assert result["counts_by_class"]["stale_backlog_status"] == 1


def test_audit_is_read_only_against_membase(tmp_path: Path) -> None:
    module = _load_module()
    _write_index(tmp_path, {"thread-a": "VERIFIED"})
    _append_bridge_text(tmp_path, "thread-a", "Work Item: WI-2001")
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        _insert_work_item(db, "WI-2001", ["thread-a"])
        before = db.get_work_item_history("WI-2001")
    finally:
        db.close()

    result = module.run_audit(project_root=tmp_path)

    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        after = db.get_work_item_history("WI-2001")
        current = db.get_work_item("WI-2001")
    finally:
        db.close()
    assert result["counts_by_class"]["stale_backlog_status"] == 1
    assert len(after) == len(before)
    assert current is not None
    assert current["resolution_status"] == "open"


def test_terminal_wrapper_delegates_to_shared_audit(tmp_path: Path, capsys) -> None:
    wrapper = _load_module(WRAPPER_PATH, "bridge_backlog_terminal_reconciliation_for_test")
    _write_index(tmp_path, {"thread-a": "VERIFIED"})
    rc = wrapper.main(["--project-root", str(tmp_path), "--json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert rc == 0
    assert payload["source_authority"]["mutation"] == "none; read-only audit"


def test_gt_bridge_reconcile_audit_json_cli(tmp_path: Path) -> None:
    config = _write_config(tmp_path)
    _write_index(tmp_path, {"thread-a": "VERIFIED"})
    _append_bridge_text(tmp_path, "thread-a", "Work Item: WI-3001")
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        _insert_work_item(db, "WI-3001", ["thread-a"])
    finally:
        db.close()

    result = CliRunner().invoke(cli_main, ["--config", str(config), "bridge", "reconcile", "audit", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["counts_by_class"]["stale_backlog_status"] == 1
    assert payload["source_authority"]["backlog"] == "fresh MemBase current_work_items"
