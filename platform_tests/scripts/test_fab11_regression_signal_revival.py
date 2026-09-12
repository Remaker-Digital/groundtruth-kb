from __future__ import annotations

# ruff: noqa: E402, I001

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
GTKB_SRC = PROJECT_ROOT / "groundtruth-kb" / "src"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(GTKB_SRC) not in sys.path:
    sys.path.insert(0, str(GTKB_SRC))

from groundtruth_kb.db import KnowledgeDB  # noqa: E402
from scripts import (  # noqa: E402
    fab11_assertion_corpus_remediation as assertion_fix,
)


def _db(tmp_path: Path) -> tuple[Path, KnowledgeDB]:
    db_path = tmp_path / "groundtruth.db"
    return db_path, KnowledgeDB(db_path=db_path)


def test_assertion_corpus_rewrites_critical_and_retires_history(tmp_path: Path) -> None:
    db_path, db = _db(tmp_path)
    try:
        (tmp_path / "applications" / "Agent_Red" / "src").mkdir(parents=True)
        (tmp_path / "applications" / "Agent_Red" / "src" / "app.py").write_text("hello\n", encoding="utf-8")

        db.insert_spec(
            "SPEC-CRIT",
            "Critical spec",
            "verified",
            "test",
            "seed",
            assertions=[{"type": "grep", "file": "src/app.py", "pattern": "hello"}],
        )
        db.insert_assertion_run(
            "SPEC-CRIT",
            1,
            False,
            [{"type": "grep", "passed": False, "detail": "File not found: src/app.py"}],
            "test",
        )
        db.insert_spec(
            "SPEC-OLD",
            "Old app history",
            "specified",
            "test",
            "seed",
            assertions=[{"type": "file_exists", "file": "admin/old.py"}],
        )
        db.insert_assertion_run(
            "SPEC-OLD",
            1,
            False,
            [{"type": "file_exists", "passed": False, "detail": "File not found: admin/old.py"}],
            "test",
        )
    finally:
        db.close()

    result = assertion_fix.apply_actions(db_path, tmp_path)

    assert result["rewritten"] == 1
    assert result["retired"] == 1
    db = KnowledgeDB(db_path=db_path)
    try:
        critical = db.get_spec("SPEC-CRIT")
        old = db.get_spec("SPEC-OLD")
    finally:
        db.close()
    assert critical["assertions_parsed"][0]["file"] == "applications/Agent_Red/src/app.py"
    assert old["status"] == "retired"
    assert old["assertions_parsed"] == []
    assert "fab11-app-scoped-history" in old["tags_parsed"]


def test_assertion_rewrite_preserves_json_path_expression() -> None:
    rewritten, changed = assertion_fix.rewrite_assertions(
        [{"type": "json_path", "file": "src/config.json", "path": "src/not-a-file"}],
        ("src/config.json",),
    )

    assert changed == 1
    assert rewritten[0]["file"] == "applications/Agent_Red/src/config.json"
    assert rewritten[0]["path"] == "src/not-a-file"
