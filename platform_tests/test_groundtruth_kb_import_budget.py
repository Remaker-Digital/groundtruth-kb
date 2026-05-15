# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Import-budget regression tests for groundtruth_kb (WI-3319).

Bridge thread: gtkb-hook-import-latency-chromadb-lazy.

These tests lock in the lazy-chromadb fix: importing `groundtruth_kb` must not
eagerly import `chromadb` (which carries a ~6s opentelemetry/grpc import chain),
so PreToolUse hooks and the `gt` CLI stay fast. They are deterministic — no
wall-clock thresholds, which would themselves be flaky.
"""

from __future__ import annotations

import builtins
import os
import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
_GROUNDTRUTH_SRC = _REPO_ROOT / "groundtruth-kb" / "src"


def _subprocess_env() -> dict[str, str]:
    env = dict(os.environ)
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(_GROUNDTRUTH_SRC) + (os.pathsep + existing if existing else "")
    return env


def test_chromadb_not_eagerly_imported() -> None:
    """`import groundtruth_kb` must not pull chromadb into sys.modules.

    Derives from DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 and the
    gtkb-hook-import-latency-chromadb-lazy problem statement.
    """
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys, groundtruth_kb; "
            "leaked = sorted(m for m in sys.modules if m == 'chromadb' or m.startswith('chromadb.')); "
            "assert not leaked, leaked",
        ],
        capture_output=True,
        text=True,
        env=_subprocess_env(),
        timeout=60,
    )
    assert result.returncode == 0, (
        f"importing groundtruth_kb eagerly imported chromadb.\n"
        f"stdout={result.stdout}\nstderr={result.stderr}"
    )


def test_has_chromadb_is_eager_bool() -> None:
    """HAS_CHROMADB stays an eagerly-resolved bool (not None-until-first-use).

    Consumers (cli.py, operating_state.py, project/chroma.py) and several test
    suites read this module attribute at import time; find_spec keeps it eager.
    """
    from groundtruth_kb.db import HAS_CHROMADB

    assert isinstance(HAS_CHROMADB, bool)


def test_lazy_chromadb_loads_on_demand() -> None:
    """When chromadb is installed, _load_chromadb() imports it on demand."""
    from groundtruth_kb import db

    if not db.HAS_CHROMADB:
        pytest.skip("chromadb is not installed in this environment")

    module = db._load_chromadb()
    assert module is not None
    assert "chromadb" in sys.modules


def test_lazy_chromadb_import_failure_degrades_gracefully(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """A failed lazy import degrades to HAS_CHROMADB=False + SQLite fallback.

    Derives from DELIB-0699: ChromaDB is optional/rebuildable and its failures
    must not make canonical SQLite behavior appear failed. Simulates find_spec
    succeeding while the real `import chromadb` raises ImportError.
    """
    from groundtruth_kb import db as db_module

    monkeypatch.setattr(db_module, "HAS_CHROMADB", True)
    monkeypatch.setattr(db_module, "chromadb", None)

    real_import = builtins.__import__

    def _failing_import(name: str, *args: object, **kwargs: object) -> object:
        if name == "chromadb" or name.startswith("chromadb."):
            raise ImportError("simulated chromadb import failure")
        return real_import(name, *args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(builtins, "__import__", _failing_import)

    assert db_module._load_chromadb() is None
    assert db_module.HAS_CHROMADB is False

    # The SQLite LIKE fallback path must still answer without raising.
    kb = db_module.KnowledgeDB(str(tmp_path / "import-budget.db"))
    results = kb.search_deliberations("anything")
    assert isinstance(results, list)
