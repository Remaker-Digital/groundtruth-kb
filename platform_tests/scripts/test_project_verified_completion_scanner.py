"""Tests for scripts/project_verified_completion_scanner.py (IP-1 of WI-3316).

Bridge thread gtkb-project-verified-completion-auq-trigger. Uses isolated
tmp_path project roots; the only dependency on the live repo is the script
import path.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest
from groundtruth_kb.db import KnowledgeDB

REPO_ROOT = Path(__file__).resolve().parents[2]
SCANNER_PATH = REPO_ROOT / "scripts" / "project_verified_completion_scanner.py"


@pytest.fixture(scope="module")
def scanner():
    spec = importlib.util.spec_from_file_location("project_verified_completion_scanner", SCANNER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["project_verified_completion_scanner"] = module
    spec.loader.exec_module(module)
    return module


def _seed(project_root: Path, *, wi_statuses: dict[str, bool]) -> None:
    """Seed a project root with one active authorization (PAUTH-X) over the WIs
    in ``wi_statuses``. Each WI maps to whether its bridge thread is VERIFIED."""
    bridge = project_root / "bridge"
    bridge.mkdir(parents=True, exist_ok=True)
    index_lines = ["# Bridge Index", ""]
    for index, (wi, verified) in enumerate(sorted(wi_statuses.items())):
        slug = f"gtkb-thread-{index}"
        top_status = "VERIFIED" if verified else "GO"
        (bridge / f"{slug}-001.md").write_text(
            f"# Proposal {slug}\n\nWork Item: {wi}\n", encoding="utf-8"
        )
        index_lines += [f"Document: {slug}", f"{top_status}: bridge/{slug}-001.md", ""]
    (bridge / "INDEX.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")

    db = KnowledgeDB(project_root / "groundtruth.db")
    try:
        db.insert_deliberation(
            "DELIB-SEED",
            "owner_conversation",
            "Owner approved",
            "Owner approved PROJECT-X authorization PAUTH-X.",
            "{}",
            "test",
            "seed",
            outcome="owner_decision",
        )
        db.insert_project("Scanner Project", "test", "seed", id="PROJECT-X", status="active")
        for wi in wi_statuses:
            db.insert_work_item(wi, f"Work item {wi}", "new", "backlog", "open", "test", "seed")
        db.insert_spec(
            id="SPEC-SEED",
            title="Seed spec",
            status="verified",
            changed_by="test",
            change_reason="seed",
        )
        db.insert_project_authorization(
            "PROJECT-X",
            "Scanner authorization",
            "DELIB-SEED",
            "Bounded scope.",
            "test",
            "seed",
            id="PAUTH-X",
            status="active",
            included_work_item_ids=list(wi_statuses),
            included_spec_ids=["SPEC-SEED"],
        )
    finally:
        db.close()


def test_scanner_marks_all_verified_authorization_completion_ready(scanner, tmp_path):
    _seed(tmp_path, wi_statuses={"WI-8001": True, "WI-8002": True})
    ready = scanner.completion_ready(tmp_path)
    assert [r.authorization_id for r in ready] == ["PAUTH-X"]
    assert ready[0].completion_ready is True
    assert set(ready[0].verified_work_item_ids) == {"WI-8001", "WI-8002"}
    assert ready[0].unverified_work_item_ids == []


def test_scanner_skips_authorization_with_one_non_verified_wi(scanner, tmp_path):
    _seed(tmp_path, wi_statuses={"WI-8001": True, "WI-8002": False})
    assert scanner.completion_ready(tmp_path) == []
    full = scanner.scan(tmp_path)
    auth = next(r for r in full if r.authorization_id == "PAUTH-X")
    assert auth.completion_ready is False
    assert auth.unverified_work_item_ids == ["WI-8002"]
    assert auth.verified_work_item_ids == ["WI-8001"]


def test_scanner_makes_no_db_writes(scanner, tmp_path):
    _seed(tmp_path, wi_statuses={"WI-8001": True})
    db_path = tmp_path / "groundtruth.db"
    probe = KnowledgeDB(db_path)
    try:
        before_version = probe.get_project_authorization("PAUTH-X")["version"]
        before_rows = probe._get_conn().execute("SELECT COUNT(*) FROM project_authorizations").fetchone()[0]
    finally:
        probe.close()

    scanner.scan(tmp_path)
    scanner.completion_ready(tmp_path)

    probe = KnowledgeDB(db_path)
    try:
        after_version = probe.get_project_authorization("PAUTH-X")["version"]
        after_rows = probe._get_conn().execute("SELECT COUNT(*) FROM project_authorizations").fetchone()[0]
    finally:
        probe.close()
    assert after_version == before_version
    assert after_rows == before_rows
