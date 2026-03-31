"""
GroundTruth KB — Specification-driven governance toolkit for AI engineering teams.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from groundtruth_kb.assertions import format_summary, run_all_assertions, run_single_assertion
from groundtruth_kb.config import GTConfig
from groundtruth_kb.db import KnowledgeDB, get_depth, get_parent_id, spec_sort_key
from groundtruth_kb.gates import GateRegistry, GovernanceGate, GovernanceGateError

__version__ = "0.1.0"

__all__ = [
    "GTConfig",
    "KnowledgeDB",
    "GateRegistry",
    "GovernanceGate",
    "GovernanceGateError",
    "format_summary",
    "run_all_assertions",
    "run_single_assertion",
    "spec_sort_key",
    "get_depth",
    "get_parent_id",
    "__version__",
]
