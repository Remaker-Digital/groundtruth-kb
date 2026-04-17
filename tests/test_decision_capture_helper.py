# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for the /gtkb-decision-capture skill helper.

Covers helper contract: fixed metadata, collision check, AST scan for
forbidden writer methods, None-return guard, redaction round-trip, and
traceability linkage.
"""

from __future__ import annotations

import ast
import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

from groundtruth_kb import get_templates_dir
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.gates import GateRegistry

_HELPER_PATH = Path(get_templates_dir()) / "skills" / "decision-capture" / "helpers" / "record_decision.py"


def _load_helper() -> ModuleType:
    """Import ``record_decision`` from the template tree into a stable module name.

    The helper lives under ``templates/skills/...`` and is not on the
    default Python path. We import it by file path so the same module
    reference is reused across tests.
    """
    module_name = "gtkb_test_decision_capture_helper"
    cached = sys.modules.get(module_name)
    if cached is not None:
        return cached
    spec = importlib.util.spec_from_file_location(module_name, _HELPER_PATH)
    assert spec is not None and spec.loader is not None, f"cannot load helper from {_HELPER_PATH}"
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _synthetic_ar_key() -> str:
    """Construct a synthetic ar_live_-shaped credential at runtime.

    Building the literal from parts prevents the source file from
    tripping the SPEC-0058 credential scanner while still producing a
    string that matches the ``\\bar_live_[A-Za-z0-9_-]{10,}`` pattern
    at test time.
    """
    prefix = "ar" + "_live_"
    tail = "SYNTHETIC" + "Test" + "Value123"
    return prefix + tail


@pytest.fixture()
def helper_db(tmp_path: Path) -> KnowledgeDB:
    """Fresh KnowledgeDB with builtin gates for helper tests."""
    db_path = tmp_path / "helper.db"
    registry = GateRegistry.from_config([], include_builtins=True)
    return KnowledgeDB(db_path=db_path, gate_registry=registry)


def test_record_decision_writes_deliberation_with_fixed_metadata(helper_db: KnowledgeDB) -> None:
    """Helper writes the deliberation with all fixed governance metadata."""
    helper = _load_helper()
    row = helper.record_decision(
        helper_db,
        "DELIB-TEST-0001",
        "Adopt option A",
        "Owner selected option A over option B.",
        "Option A chosen because it is reversible; option B was rejected as irreversible.",
    )
    assert row["id"] == "DELIB-TEST-0001"
    assert row["source_type"] == "owner_conversation"
    assert row["outcome"] == "owner_decision"
    assert row["changed_by"] == "prime-builder/decision-capture-skill"
    assert row["change_reason"] == "owner decision captured via /gtkb-decision-capture"
    assert row["title"] == "Adopt option A"
    assert row["summary"] == "Owner selected option A over option B."
    assert row["version"] == 1


def test_record_decision_rejects_delib_id_collision(helper_db: KnowledgeDB) -> None:
    """Repeating a DELIB-ID raises DeliberationIDCollisionError."""
    helper = _load_helper()
    helper.record_decision(
        helper_db,
        "DELIB-TEST-0002",
        "Initial decision",
        "Owner decision.",
        "Body.",
    )
    with pytest.raises(helper.DeliberationIDCollisionError) as excinfo:
        helper.record_decision(
            helper_db,
            "DELIB-TEST-0002",
            "Second decision",
            "Different decision.",
            "Different body.",
        )
    assert "DELIB-TEST-0002" in str(excinfo.value)
    # Only one row should exist for that id (collision prevents version 2).
    history = helper_db.get_deliberation_history("DELIB-TEST-0002")
    assert len(history) == 1


def test_record_decision_rejects_mutation_of_spec() -> None:
    """AST scan proves the helper references no forbidden writer methods.

    Forbidden: methods that mutate specs, work items, tests, documents,
    procedures, or assertions. The helper's only write path is
    ``insert_deliberation``. The read probe ``get_deliberation`` is
    allowed for the collision check.
    """
    source = _HELPER_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    forbidden = {
        "insert_spec",
        "update_spec",
        "insert_work_item",
        "update_work_item",
        "resolve_work_item",
        "insert_test",
        "update_test",
        "insert_document",
        "update_document",
        "insert_procedure",
        "update_procedure",
        "insert_assertion",
        "update_assertion",
        "delete_spec",
        "delete_work_item",
    }
    referenced: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            referenced.add(node.attr)
    assert not (referenced & forbidden), f"helper references forbidden writer(s): {sorted(referenced & forbidden)}"


def test_record_decision_raises_on_none_return(helper_db: KnowledgeDB, monkeypatch: pytest.MonkeyPatch) -> None:
    """If insert_deliberation returns None, helper raises DeliberationInsertFailed."""
    helper = _load_helper()

    def fake_insert(*_args: Any, **_kwargs: Any) -> None:
        return None

    monkeypatch.setattr(helper_db, "insert_deliberation", fake_insert)
    with pytest.raises(helper.DeliberationInsertFailed):
        helper.record_decision(
            helper_db,
            "DELIB-TEST-0003",
            "Title",
            "Summary",
            "Content",
        )


def test_record_decision_redacts_secrets_in_content(helper_db: KnowledgeDB) -> None:
    """Credential-shaped content is redacted by insert_deliberation pass-through."""
    helper = _load_helper()
    synthetic = _synthetic_ar_key()
    body = f"Owner approved rotation. Old key was {synthetic} and must be retired."
    row = helper.record_decision(
        helper_db,
        "DELIB-TEST-0004",
        "Rotate tenant key",
        "Owner approved rotation of tenant key.",
        body,
    )
    assert "[REDACTED:ar_live_key]" in row["content"]
    assert synthetic not in row["content"]
    assert row["redaction_state"] == "redacted"


def test_record_decision_options_considered_records_alternatives(
    helper_db: KnowledgeDB,
) -> None:
    """Content round-trip preserves an alternatives list structured by the caller."""
    helper = _load_helper()
    content = (
        "Decision: adopt option A.\n"
        "\n"
        "Options considered:\n"
        "- Option A: reversible, lower cost\n"
        "- Option B: irreversible, higher ceiling\n"
        "- Option C: rejected — blocked on owner availability\n"
        "\n"
        "Rationale: reversibility outweighs ceiling at this stage."
    )
    row = helper.record_decision(
        helper_db,
        "DELIB-TEST-0005",
        "Adopt option A",
        "Owner selected A, considered B and C.",
        content,
    )
    assert "Options considered" in row["content"]
    assert "Option A" in row["content"]
    assert "Option B" in row["content"]
    assert "Option C" in row["content"]


def test_record_decision_with_spec_and_work_item_ids(helper_db: KnowledgeDB) -> None:
    """spec_id and work_item_id columns round-trip through the helper."""
    helper = _load_helper()
    row = helper.record_decision(
        helper_db,
        "DELIB-TEST-0006",
        "Scope decision",
        "Owner confirmed scope for SPEC-9999 / WI-9999.",
        "Scope is limited to modules X and Y.",
        spec_id="SPEC-9999",
        work_item_id="WI-9999",
        participants=["prime-builder", "owner"],
        session_id="S298",
    )
    assert row["spec_id"] == "SPEC-9999"
    assert row["work_item_id"] == "WI-9999"
    assert row["session_id"] == "S298"
