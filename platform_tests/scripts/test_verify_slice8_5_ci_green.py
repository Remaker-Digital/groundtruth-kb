"""Tests for the Slice 8.5 CI-green evidence verifier."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "verify_slice8_5_ci_green.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("verify_slice8_5_ci_green", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["verify_slice8_5_ci_green"] = module
    spec.loader.exec_module(module)
    return module


def _valid_text(module) -> str:
    rows = "\n".join(
        f"| {workflow} | {module.REPOSITORY} | {module.BRANCH} | {module.EVENT} | "
        f"{module.HEAD_SHA} | {run_id} | https://github.com/{module.REPOSITORY}/actions/runs/{run_id} | "
        f"{module.CONCLUSION} | {module.DELIB_ID} |"
        for workflow, run_id in module.REQUIRED_RUNS.items()
    )
    return f"""
| Blocker | Outcome | Evidence |
|---|---|---|
| B6 - CI-green evidence | GREEN | Evidence cites {module.DELIB_ID}. |

### Slice 8.5 CI-green evidence (transient exception)

| Workflow | Repository | Branch | Event | Head SHA | Run ID | URL | Conclusion | Authority |
|---|---|---|---|---|---|---|---|---|
{rows}

### Tag authorization gate

v0.7.0-rc1 remains unauthorized pending canonical migration and canonical CI.
"""


def test_verify_text_accepts_exact_evidence() -> None:
    module = _load_module()

    assert module.verify_text(_valid_text(module)) == []


def test_verify_text_rejects_missing_workflow() -> None:
    module = _load_module()
    text = _valid_text(module).replace(
        f"| Python Tests | {module.REPOSITORY}",
        f"| Missing Python Tests | {module.REPOSITORY}",
    )

    errors = module.verify_text(text)

    assert any("missing workflow evidence row: Python Tests" in error for error in errors)
    assert any("unexpected workflow evidence row" in error for error in errors)


def test_verify_text_rejects_wrong_head_sha() -> None:
    module = _load_module()
    text = _valid_text(module).replace(module.HEAD_SHA, "0" * 40, 1)

    errors = module.verify_text(text)

    assert any("expected Head SHA" in error for error in errors)


def test_verify_text_rejects_duplicate_workflow() -> None:
    module = _load_module()
    valid = _valid_text(module)
    duplicate = (
        f"| Lint | {module.REPOSITORY} | {module.BRANCH} | {module.EVENT} | "
        f"{module.HEAD_SHA} | {module.REQUIRED_RUNS['Lint']} | "
        f"https://github.com/{module.REPOSITORY}/actions/runs/{module.REQUIRED_RUNS['Lint']} | "
        f"{module.CONCLUSION} | {module.DELIB_ID} |"
    )
    text = valid.replace("### Tag authorization gate", f"{duplicate}\n\n### Tag authorization gate")

    errors = module.verify_text(text)

    assert any("duplicate workflow evidence rows for Lint" in error for error in errors)


def test_verify_text_rejects_deferred_b6_row() -> None:
    module = _load_module()
    text = _valid_text(module).replace(
        "| B6 - CI-green evidence | GREEN |",
        "| B6 - CI-green evidence | **DEFERRED to Slice 8.5** |",
    )

    errors = module.verify_text(text)

    assert any("still records deferred state" in error for error in errors)


def test_verify_text_rejects_missing_tag_gate() -> None:
    module = _load_module()
    text = _valid_text(module).replace("v0.7.0-rc1 remains unauthorized", "v0.7.0-rc1 authorized")

    errors = module.verify_text(text)

    assert any("missing tag-gate phrase" in error for error in errors)
