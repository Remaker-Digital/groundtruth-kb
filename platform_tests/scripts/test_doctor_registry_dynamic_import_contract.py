"""Regression coverage for the doctor registry's declared dynamic imports."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from check_artifact_decontamination import _import_requests  # noqa: E402

SOURCE = ROOT / "groundtruth-kb" / "src" / "groundtruth_kb" / "project" / "checks" / "__init__.py"
RATIONALE = (
    "Doctor modules are discovered from the package path and imported dynamically "
    "so decorator registration remains extensible."
)


def test_doctor_registry_declares_both_dynamic_imports() -> None:
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))

    requests, declared = _import_requests(tree)

    assert len(declared) == 2
    assert {item.function for item in declared} == {"get_registered_checks"}
    assert {item.reason for item in declared} == {RATIONALE}
    assert all(item.reason.strip() for item in declared)
    assert [request for request in requests if request.module == "<dynamic>"] == []
