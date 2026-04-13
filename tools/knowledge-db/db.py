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

KnowledgeDB API surface (forwarded from groundtruth_kb.db.KnowledgeDB):
  Specs:      insert_spec, update_spec, get_spec, list_specs, count_specs
  Tests:      insert_test, update_test, get_test, list_tests, get_tests_for_spec
  Work items: insert_work_item, update_work_item, list_work_items, get_open_work_items, work_item
  Test plans: insert_test_plan, update_test_plan, test_plan, insert_test_plan_phase
  Procedures: insert_procedure, update_procedure, procedure
  Documents:  insert_document, update_document
  Testable:   insert_testable_element, testable_element, testable_elements
  Assertions: run_all_assertions, validate_dcl_constraints
  ADR/DCL:    ADR-* specs use type=architecture_decision, DCL-* use type=design_constraint
  Transport:  _TRANSPORT_GATED_SPECS, TransportEvidenceGateError,
              _validate_transport_test_pass, _validate_transport_spec_verification
  Backlog:    insert_backlog_snapshot, backlog_snapshot
  Coverage:   insert_test_coverage
  Prompts:    insert_session_prompt, get_next_session_prompt, consume_session_prompt
  Config:     insert_environment_config, environment_config
  Scores:     insert_quality_score
  Summaries:  get_summary

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from pathlib import Path

# AR-specific paths
_CONFIG_PATH = Path(__file__).resolve().parent / "groundtruth.toml"
DB_PATH = Path(__file__).resolve().parent.parent.parent / "groundtruth.db"

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


# ---------------------------------------------------------------------------
# Transport governance symbols for assertion hooks.
# Extracted from the loaded gate registry so that `.claude/hooks/assertion-check.py`
# can import `from db import _TRANSPORT_GATED_SPECS, _resolve_test_file`.
# ---------------------------------------------------------------------------
_TRANSPORT_GATED_SPECS: frozenset[str] = frozenset()
for _gate in _default_registry._gates:
    if hasattr(_gate, '_spec_ids'):
        _TRANSPORT_GATED_SPECS = _gate._spec_ids
        break


def _resolve_test_file(test_file: str | None) -> Path | None:
    """Resolve a test_file path relative to the project root."""
    if not test_file:
        return None
    p = _config.project_root / test_file
    return p if p.exists() else None


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
        chroma_path: str | Path | None = None,
    ):
        if gate_registry is None:
            gate_registry = _default_registry
        # Default chroma_path from groundtruth.toml config if not explicitly provided
        if chroma_path is None and _config.chroma_path is not None:
            chroma_path = _config.chroma_path
        super().__init__(
            db_path=db_path,
            gate_registry=gate_registry,
            check_same_thread=check_same_thread,
            chroma_path=chroma_path,
        )


__all__ = [
    "DB_PATH",
    "SCHEMA_SQL",
    "KnowledgeDB",
    "TransportEvidenceGateError",
    "_TRANSPORT_GATED_SPECS",
    "_resolve_test_file",
    "get_depth",
    "get_parent_id",
    "spec_sort_key",
]
