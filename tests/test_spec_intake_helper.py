# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for the /gtkb-spec-intake skill helper.

Covers helper contract: G4 (``outcome='deferred'`` on capture),
F1 (``changed_by='prime-builder/spec-intake-skill'`` on all four
persisted rows), confirm-before-mutate ergonomics, and reject-reason
fail-fast at the helper boundary.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

from groundtruth_kb import get_templates_dir, intake
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.gates import GateRegistry

_HELPER_PATH = Path(get_templates_dir()) / "skills" / "spec-intake" / "helpers" / "spec_intake.py"


def _load_helper() -> ModuleType:
    """Import ``spec_intake`` from the template tree into a stable module name.

    The helper lives under ``templates/skills/...`` and is not on the
    default Python path. We import it by file path so the same module
    reference is reused across tests.
    """
    module_name = "gtkb_test_spec_intake_helper"
    cached = sys.modules.get(module_name)
    if cached is not None:
        return cached
    spec = importlib.util.spec_from_file_location(module_name, _HELPER_PATH)
    assert spec is not None and spec.loader is not None, f"cannot load helper from {_HELPER_PATH}"
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def helper_db(tmp_path: Path) -> KnowledgeDB:
    """Fresh KnowledgeDB with builtin gates for helper tests."""
    db_path = tmp_path / "helper.db"
    registry = GateRegistry.from_config([], include_builtins=True)
    return KnowledgeDB(db_path=db_path, gate_registry=registry)


# ── Capture tests ─────────────────────────────────────────────────────


def test_capture_candidate_returns_deliberation_id(helper_db: KnowledgeDB) -> None:
    """Happy path: helper returns a dict containing ``deliberation_id``."""
    helper = _load_helper()
    result = helper.capture_candidate(
        helper_db,
        "The system must log all API errors",
        proposed_title="API error logging",
        proposed_section="observability",
    )
    assert isinstance(result, dict)
    assert "deliberation_id" in result
    assert result["deliberation_id"].startswith("INTAKE-")


def test_capture_candidate_writes_deferred_outcome(helper_db: KnowledgeDB) -> None:
    """G4 guard: persisted deliberation has ``outcome='deferred'``.

    The skill must never promote capture to any other outcome. This
    guard fails loudly if a future refactor changes the capture
    outcome.
    """
    helper = _load_helper()
    result = helper.capture_candidate(
        helper_db,
        "The system must validate user input",
        proposed_title="Input validation",
        proposed_section="security",
    )
    row = helper_db.get_deliberation(result["deliberation_id"])
    assert row is not None
    assert row["outcome"] == "deferred"


def test_capture_candidate_writes_owner_conversation_source_type(
    helper_db: KnowledgeDB,
) -> None:
    """Persisted deliberation has ``source_type='owner_conversation'``."""
    helper = _load_helper()
    result = helper.capture_candidate(
        helper_db,
        "The system must log errors",
        proposed_title="Error logging",
        proposed_section="observability",
    )
    row = helper_db.get_deliberation(result["deliberation_id"])
    assert row is not None
    assert row["source_type"] == "owner_conversation"


def test_capture_candidate_writes_skill_changed_by(helper_db: KnowledgeDB) -> None:
    """F1 guard: persisted deliberation has skill-specific ``changed_by``."""
    helper = _load_helper()
    result = helper.capture_candidate(
        helper_db,
        "The system must enforce rate limits",
        proposed_title="Rate limiting",
        proposed_section="api",
    )
    row = helper_db.get_deliberation(result["deliberation_id"])
    assert row is not None
    assert row["changed_by"] == "prime-builder/spec-intake-skill"


def test_capture_candidate_raises_on_malformed_result(
    helper_db: KnowledgeDB,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """If ``intake.capture_requirement`` returns None, helper raises."""
    helper = _load_helper()

    def fake_capture(*_args: Any, **_kwargs: Any) -> None:
        return None

    monkeypatch.setattr(intake, "capture_requirement", fake_capture)
    with pytest.raises(helper.SpecIntakeCaptureFailed):
        helper.capture_candidate(
            helper_db,
            "Some requirement",
            proposed_title="X",
            proposed_section="core",
        )


# ── Confirm tests ─────────────────────────────────────────────────────


def test_confirm_candidate_creates_spec(helper_db: KnowledgeDB) -> None:
    """Happy path: confirm creates a KB spec at ``status='specified'``."""
    helper = _load_helper()
    cap = helper.capture_candidate(
        helper_db,
        "The system must log all errors",
        proposed_title="Error logging",
        proposed_section="observability",
    )
    result = helper.confirm_candidate(helper_db, cap["deliberation_id"])
    assert "spec" in result
    assert result["spec"]["status"] == "specified"


def test_confirm_candidate_writes_skill_changed_by_on_spec(
    helper_db: KnowledgeDB,
) -> None:
    """F1 guard: created spec records skill-specific ``changed_by``."""
    helper = _load_helper()
    cap = helper.capture_candidate(
        helper_db,
        "The system must verify credentials",
        proposed_title="Credential verification",
        proposed_section="security",
    )
    result = helper.confirm_candidate(helper_db, cap["deliberation_id"])
    spec_id = result["confirmed_spec_id"]
    spec_row = helper_db.get_spec(spec_id)
    assert spec_row is not None
    assert spec_row["changed_by"] == "prime-builder/spec-intake-skill"


def test_confirm_candidate_writes_skill_changed_by_on_deliberation(
    helper_db: KnowledgeDB,
) -> None:
    """F1 guard: confirmation-version deliberation records skill ``changed_by`` and ``owner_decision`` outcome."""
    helper = _load_helper()
    cap = helper.capture_candidate(
        helper_db,
        "The system must throttle requests",
        proposed_title="Request throttling",
        proposed_section="api",
    )
    helper.confirm_candidate(helper_db, cap["deliberation_id"])
    # The confirmation is the latest version of the same deliberation ID.
    confirmed = helper_db.get_deliberation(cap["deliberation_id"])
    assert confirmed is not None
    assert confirmed["outcome"] == "owner_decision"
    assert confirmed["changed_by"] == "prime-builder/spec-intake-skill"


def test_confirm_candidate_raises_on_unknown_id(helper_db: KnowledgeDB) -> None:
    """Confirming an unknown DELIB-ID raises ``SpecIntakeConfirmFailed``."""
    helper = _load_helper()
    with pytest.raises(helper.SpecIntakeConfirmFailed):
        helper.confirm_candidate(helper_db, "INTAKE-does-not-exist")


# ── Reject tests ──────────────────────────────────────────────────────


def test_reject_candidate_requires_reason(helper_db: KnowledgeDB) -> None:
    """Empty-string reason raises ``SpecIntakeRejectFailed`` at helper boundary.

    The guard runs BEFORE any call to ``intake.reject_intake`` so the
    library is not reached with a would-fail-anyway argument.
    """
    helper = _load_helper()
    cap = helper.capture_candidate(
        helper_db,
        "An idea to reject",
        proposed_title="Rejectable idea",
        proposed_section="core",
    )
    with pytest.raises(helper.SpecIntakeRejectFailed):
        helper.reject_candidate(helper_db, cap["deliberation_id"], "")
    with pytest.raises(helper.SpecIntakeRejectFailed):
        helper.reject_candidate(helper_db, cap["deliberation_id"], "   ")


def test_reject_candidate_writes_skill_changed_by(helper_db: KnowledgeDB) -> None:
    """F1 guard: rejection-version deliberation records skill ``changed_by`` and ``no_go`` outcome."""
    helper = _load_helper()
    cap = helper.capture_candidate(
        helper_db,
        "An exploratory idea",
        proposed_title="Exploratory idea",
        proposed_section="core",
    )
    helper.reject_candidate(helper_db, cap["deliberation_id"], "Out of scope for this release")
    rejected = helper_db.get_deliberation(cap["deliberation_id"])
    assert rejected is not None
    assert rejected["outcome"] == "no_go"
    assert rejected["changed_by"] == "prime-builder/spec-intake-skill"
