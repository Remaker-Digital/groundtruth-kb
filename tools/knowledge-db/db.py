"""
Knowledge Database — Re-export shim for Agent Red.

This module re-exports the groundtruth_kb package's KnowledgeDB and related
symbols so that existing AR scripts using ``from db import KnowledgeDB`` continue
to work unchanged. The actual implementation lives in the groundtruth-kb package
(installed via requirements-local.txt as an editable dependency).

AR-specific behavior:
  - DB_PATH defaults to tools/knowledge-db/knowledge.db
  - TransportEvidenceGate is loaded via groundtruth.toml gate plugin config

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from pathlib import Path

# AR-specific DB path — set BEFORE importing KnowledgeDB so the module default
# is correct for scripts that call KnowledgeDB() with no arguments.
DB_PATH = Path(__file__).resolve().parent / "knowledge.db"

# Patch the package-level default so KnowledgeDB() uses AR's path
import groundtruth_kb.db as _gt_db

_gt_db.DB_PATH = DB_PATH

# Re-export core symbols used by 30+ AR scripts
from groundtruth_kb.db import (  # noqa: E402
    SCHEMA_SQL,
    KnowledgeDB,
    get_depth,
    get_parent_id,
    spec_sort_key,
)

# Re-export transport gate error for scripts that catch it
from groundtruth_kb.gates_transport import TransportEvidenceGateError  # noqa: E402

__all__ = [
    "DB_PATH",
    "SCHEMA_SQL",
    "KnowledgeDB",
    "TransportEvidenceGateError",
    "get_depth",
    "get_parent_id",
    "spec_sort_key",
]
