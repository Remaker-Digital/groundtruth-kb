"""Tests for the configurable retention cap in .claude/hooks/assertion-check.py
(Slice 4 IP-3 / IP-4).

Per ``bridge/gtkb-self-diagnostic-leak-closure-slice-4-implementation-gate-hygiene-003.md``
(Codex GO at -004). Covers:

- Default fallback to 50 when config/governance/assertion-runs-retention.toml is absent.
- Cap honored when the config specifies a different value.
- Fallback to default plus log line when the config is malformed.

The hook script lives at .claude/hooks/assertion-check.py; we load it via
importlib so PROJECT_DIR resolves to our fixture tmp_path.
"""

from __future__ import annotations

import importlib.util
import os
import sqlite3
import sys
import types
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK_PATH = REPO_ROOT / ".claude" / "hooks" / "assertion-check.py"


def _load_hook_module(project_dir: Path) -> types.ModuleType:
    """Load assertion-check.py with CLAUDE_PROJECT_DIR set to project_dir.

    Resets the env var on import so PROJECT_DIR captures the fixture root,
    not the live repo root. Returns the loaded module.
    """
    orig_env = os.environ.get("CLAUDE_PROJECT_DIR")
    os.environ["CLAUDE_PROJECT_DIR"] = str(project_dir)
    try:
        spec = importlib.util.spec_from_file_location("_assertion_check_under_test", HOOK_PATH)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        sys.modules["_assertion_check_under_test"] = module
        spec.loader.exec_module(module)
        return module
    finally:
        if orig_env is None:
            os.environ.pop("CLAUDE_PROJECT_DIR", None)
        else:
            os.environ["CLAUDE_PROJECT_DIR"] = orig_env


class _FakeDB:
    """Minimal stand-in for KnowledgeDB exposing _get_conn(), which is the only
    method `_prune_assertion_runs()` calls."""

    def __init__(self, db_path: Path) -> None:
        self._conn = sqlite3.connect(str(db_path))

    def _get_conn(self) -> sqlite3.Connection:
        return self._conn

    def close(self) -> None:
        self._conn.close()


def _seed_assertion_runs(db_path: Path, *, runs_per_spec: dict[str, int]) -> None:
    """Create assertion_runs with `runs_per_spec[spec_id]` rows per spec, each
    with an ascending run_at timestamp."""
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute(
            "CREATE TABLE assertion_runs ("
            " rowid INTEGER PRIMARY KEY,"
            " spec_id TEXT,"
            " spec_version INTEGER,"
            " run_at TEXT,"
            " overall_passed INTEGER,"
            " results TEXT,"
            " triggered_by TEXT"
            ")"
        )
        for spec_id, count in runs_per_spec.items():
            for i in range(count):
                run_at = f"2026-05-{(i % 28) + 1:02d}T{(i % 24):02d}:00:00Z"
                conn.execute(
                    "INSERT INTO assertion_runs (spec_id, spec_version, run_at, overall_passed, results, triggered_by) "
                    "VALUES (?, 1, ?, 1, '[]', 'fixture')",
                    (spec_id, run_at),
                )
        conn.commit()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# _read_retention_cap
# ---------------------------------------------------------------------------


def test_read_retention_cap_defaults_to_50_when_config_missing(tmp_path):
    """Config file absent -> returns (50, [])."""
    module = _load_hook_module(tmp_path)
    cap, log_lines = module._read_retention_cap(tmp_path)
    assert cap == 50
    assert log_lines == []


def test_read_retention_cap_honors_configured_value(tmp_path):
    """Valid config with `default_runs_per_spec = 17` -> returns (17, [])."""
    cfg = tmp_path / "config" / "governance" / "assertion-runs-retention.toml"
    cfg.parent.mkdir(parents=True, exist_ok=True)
    cfg.write_text("default_runs_per_spec = 17\n", encoding="utf-8")
    module = _load_hook_module(tmp_path)
    cap, log_lines = module._read_retention_cap(tmp_path)
    assert cap == 17
    assert log_lines == []


def test_read_retention_cap_falls_back_on_malformed_config(tmp_path):
    """Malformed TOML -> returns (50, [<log line containing 'fallback'>])."""
    cfg = tmp_path / "config" / "governance" / "assertion-runs-retention.toml"
    cfg.parent.mkdir(parents=True, exist_ok=True)
    cfg.write_text("this is not valid TOML = =\n", encoding="utf-8")
    module = _load_hook_module(tmp_path)
    cap, log_lines = module._read_retention_cap(tmp_path)
    assert cap == 50
    assert any("fallback to default 50" in line for line in log_lines)


def test_read_retention_cap_rejects_non_positive_value(tmp_path):
    """`default_runs_per_spec = 0` -> falls back to 50 plus log line."""
    cfg = tmp_path / "config" / "governance" / "assertion-runs-retention.toml"
    cfg.parent.mkdir(parents=True, exist_ok=True)
    cfg.write_text("default_runs_per_spec = 0\n", encoding="utf-8")
    module = _load_hook_module(tmp_path)
    cap, log_lines = module._read_retention_cap(tmp_path)
    assert cap == 50
    assert any("invalid" in line for line in log_lines)


# ---------------------------------------------------------------------------
# _prune_assertion_runs end-to-end
# ---------------------------------------------------------------------------


def test_prune_defaults_to_50_runs_when_config_missing(tmp_path):
    """100 rows per spec, no config -> 50 rows retained per spec."""
    db_path = tmp_path / "groundtruth.db"
    _seed_assertion_runs(db_path, runs_per_spec={"SPEC-A": 100})
    module = _load_hook_module(tmp_path)
    fake = _FakeDB(db_path)
    try:
        lines = module._prune_assertion_runs(fake)
        # After prune, assertion_runs should have exactly 50 rows for SPEC-A
        conn = sqlite3.connect(str(db_path))
        try:
            count = conn.execute("SELECT COUNT(*) FROM assertion_runs WHERE spec_id = ?", ("SPEC-A",)).fetchone()[0]
        finally:
            conn.close()
        assert count == 50
        assert any("pruned" in line and "cap=50" in line for line in lines)
    finally:
        fake.close()


def test_prune_respects_configured_runs_per_spec(tmp_path):
    """Config sets cap=10 -> 10 rows retained per spec from 100."""
    cfg = tmp_path / "config" / "governance" / "assertion-runs-retention.toml"
    cfg.parent.mkdir(parents=True, exist_ok=True)
    cfg.write_text("default_runs_per_spec = 10\n", encoding="utf-8")
    db_path = tmp_path / "groundtruth.db"
    _seed_assertion_runs(db_path, runs_per_spec={"SPEC-A": 100})
    module = _load_hook_module(tmp_path)
    fake = _FakeDB(db_path)
    try:
        lines = module._prune_assertion_runs(fake)
        conn = sqlite3.connect(str(db_path))
        try:
            count = conn.execute("SELECT COUNT(*) FROM assertion_runs WHERE spec_id = ?", ("SPEC-A",)).fetchone()[0]
        finally:
            conn.close()
        assert count == 10
        assert any("pruned" in line and "cap=10" in line for line in lines)
    finally:
        fake.close()


def test_prune_fallback_logs_invalid_config_and_uses_default(tmp_path):
    """Malformed config -> prune still runs with cap=50, fallback line in log."""
    cfg = tmp_path / "config" / "governance" / "assertion-runs-retention.toml"
    cfg.parent.mkdir(parents=True, exist_ok=True)
    cfg.write_text("this is not valid TOML = =\n", encoding="utf-8")
    db_path = tmp_path / "groundtruth.db"
    _seed_assertion_runs(db_path, runs_per_spec={"SPEC-A": 100})
    module = _load_hook_module(tmp_path)
    fake = _FakeDB(db_path)
    try:
        lines = module._prune_assertion_runs(fake)
        conn = sqlite3.connect(str(db_path))
        try:
            count = conn.execute("SELECT COUNT(*) FROM assertion_runs WHERE spec_id = ?", ("SPEC-A",)).fetchone()[0]
        finally:
            conn.close()
        assert count == 50
        assert any("fallback" in line for line in lines)
        assert any("pruned" in line and "cap=50" in line for line in lines)
    finally:
        fake.close()


def test_prune_no_op_when_table_already_within_cap(tmp_path):
    """If rows-per-spec is already <= cap, no rows are deleted and no 'pruned' log."""
    db_path = tmp_path / "groundtruth.db"
    _seed_assertion_runs(db_path, runs_per_spec={"SPEC-A": 3})
    module = _load_hook_module(tmp_path)
    fake = _FakeDB(db_path)
    try:
        lines = module._prune_assertion_runs(fake)
        conn = sqlite3.connect(str(db_path))
        try:
            count = conn.execute("SELECT COUNT(*) FROM assertion_runs WHERE spec_id = ?", ("SPEC-A",)).fetchone()[0]
        finally:
            conn.close()
        assert count == 3
        assert not any("pruned" in line for line in lines)
    finally:
        fake.close()
