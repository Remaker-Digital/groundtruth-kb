"""
Knowledge Database — Re-export shim for Agent Red.

This module re-exports the groundtruth_kb package's KnowledgeDB and related
symbols so that existing AR scripts using ``from db import KnowledgeDB`` continue
to work unchanged. The actual implementation lives in the groundtruth-kb package
(installed via requirements-local.txt as an editable dependency).

AR-specific behavior:
  - DB_PATH defaults to tools/knowledge-db/knowledge.db
  - TransportEvidenceGate is auto-wired from groundtruth.toml for all
    KnowledgeDB() callers (preserves default governance enforcement)

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from pathlib import Path

# AR-specific paths
_CONFIG_PATH = Path(__file__).resolve().parent / "groundtruth.toml"
DB_PATH = Path(__file__).resolve().parent / "knowledge.db"

# Patch the package-level default so KnowledgeDB() uses AR's path
import groundtruth_kb.db as _gt_db

_gt_db.DB_PATH = DB_PATH

# Re-export core symbols used by 30+ AR scripts
from groundtruth_kb.db import (  # noqa: E402
    SCHEMA_SQL,
    get_depth,
    get_parent_id,
    spec_sort_key,
)
from groundtruth_kb.db import KnowledgeDB as _KnowledgeDB  # noqa: E402

# Re-export transport gate error for scripts that catch it
from groundtruth_kb.gates_transport import TransportEvidenceGateError  # noqa: E402

# ---------------------------------------------------------------------------
# Build the default gate registry from groundtruth.toml so that KnowledgeDB()
# callers get transport-gate enforcement without passing gate_registry= explicitly.
# This preserves the behavioral contract of the old monolithic db.py.
# ---------------------------------------------------------------------------
from groundtruth_kb.config import GTConfig  # noqa: E402
from groundtruth_kb.gates import GateRegistry  # noqa: E402

_config = GTConfig.load(config_path=_CONFIG_PATH)
_default_registry = GateRegistry.from_config(
    _config.governance_gates,
    include_builtins=True,
    gate_config=_config.gate_config,
    project_root=_config.project_root,
)


class KnowledgeDB(_KnowledgeDB):
    """AR-aware KnowledgeDB with default transport gate enforcement.

    When no gate_registry is provided, automatically uses the registry
    built from tools/knowledge-db/groundtruth.toml. This preserves the
    governance behavior of the old monolithic db.py for all unchanged callers.
    """

    def __init__(
        self,
        db_path: str | Path | None = None,
        gate_registry: GateRegistry | None = None,
        check_same_thread: bool = True,
    ):
        if gate_registry is None:
            gate_registry = _default_registry
        super().__init__(db_path=db_path, gate_registry=gate_registry, check_same_thread=check_same_thread)


__all__ = [
    "DB_PATH",
    "SCHEMA_SQL",
    "KnowledgeDB",
    "TransportEvidenceGateError",
    "get_depth",
    "get_parent_id",
    "spec_sort_key",
]
