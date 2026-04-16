"""
GroundTruth KB — Specification-driven governance toolkit for AI engineering teams.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from pathlib import Path

from groundtruth_kb.assertion_schema import validate_assertion, validate_assertion_list
from groundtruth_kb.assertions import format_summary, run_all_assertions, run_single_assertion
from groundtruth_kb.config import GTConfig, GTConfigError
from groundtruth_kb.db import KnowledgeDB, get_depth, get_parent_id, spec_sort_key
from groundtruth_kb.gates import GateRegistry, GovernanceGate, GovernanceGateError

__version__ = "0.5.0"


def get_templates_dir() -> Path:
    """Return the path to the process templates directory.

    In a wheel install, templates are at groundtruth_kb/templates/.
    In an editable install, they are at the repo root templates/.
    """
    # Wheel install: templates bundled inside the package
    pkg_path = Path(__file__).parent / "templates"
    if pkg_path.is_dir():
        return pkg_path
    # Editable install: templates at repo root
    repo_root = Path(__file__).parent.parent.parent
    repo_path = repo_root / "templates"
    if repo_path.is_dir():
        return repo_path
    return pkg_path  # fallback (will show missing-dir error to caller)


__all__ = [
    "GTConfig",
    "GTConfigError",
    "KnowledgeDB",
    "GateRegistry",
    "GovernanceGate",
    "GovernanceGateError",
    "format_summary",
    "run_all_assertions",
    "run_single_assertion",
    "validate_assertion",
    "validate_assertion_list",
    "spec_sort_key",
    "get_depth",
    "get_parent_id",
    "get_templates_dir",
    "__version__",
]
