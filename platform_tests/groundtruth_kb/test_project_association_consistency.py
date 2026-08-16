"""Project label/membership association must never diverge silently.

Work item: WI-6445.
Governing: DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001,
DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001, GOV-STANDING-BACKLOG-001,
GOV-FILE-BRIDGE-AUTHORITY-001.

``--project-name`` sets a label; only ``--project`` binds membership. They are
separate stores, and reporting ``project_membership: null`` with no reason let
that divergence accumulate invisibly: a live measurement found 4 items by label
versus 25 by membership for the same project and filters.

These tests assert the corrected contract: a create that carries only the label
either produces a membership or produces a NON-SILENT diagnostic, and a create
carrying ``--project`` produces a membership.
"""

from __future__ import annotations

from pathlib import Path

from groundtruth_kb.config import GTConfig
from groundtruth_kb.db import KnowledgeDB


def _config(tmp_path: Path) -> GTConfig:
    db_path = tmp_path / "groundtruth.db"
    chroma_path = tmp_path / "chroma"
    config = GTConfig(db_path=db_path, project_root=tmp_path, chroma_path=chroma_path)
    db = KnowledgeDB(db_path=db_path, chroma_path=chroma_path)
    db.insert_project("Real Project", "test", "test setup", id="PROJECT-REAL")
    db.close()
    return config


def _classify(config: GTConfig, result: dict, project_name: str | None, project_id: str | None):
    from groundtruth_kb.cli import _classify_project_membership

    return _classify_project_membership(config, result, project_name, project_id)


class TestMembershipReasonIsAlwaysReported:
    """No success path may report a null membership without a reason."""

    def test_membership_created_reports_created_and_no_warning(self, tmp_path: Path) -> None:
        config = _config(tmp_path)
        result = {"work_item_id": "WI-1", "project_membership": {"id": "PM-1"}}
        reason, warning = _classify(config, result, "PROJECT-REAL", "PROJECT-REAL")
        assert reason == "created"
        assert warning is None

    def test_label_naming_a_real_project_warns_and_names_the_fix(self, tmp_path: Path) -> None:
        """The divergence case measured on WI-6445 must not be silent."""
        config = _config(tmp_path)
        result = {"work_item_id": "WI-2", "project_membership": None}
        reason, warning = _classify(config, result, "PROJECT-REAL", None)
        assert reason == "label_only_no_membership"
        assert warning is not None, "a label naming a real project must not bind silently"
        assert "PROJECT-REAL" in warning
        assert "--project" in warning, "the warning must name the flag that binds membership"

    def test_label_naming_an_unknown_project_is_also_reported(self, tmp_path: Path) -> None:
        config = _config(tmp_path)
        result = {"work_item_id": "WI-3", "project_membership": None}
        reason, warning = _classify(config, result, "PROJECT-DOES-NOT-EXIST", None)
        assert reason == "label_only_unknown_project"
        assert warning is not None

    def test_no_label_and_no_project_is_not_requested(self, tmp_path: Path) -> None:
        """Absence of association is legitimate and must not emit noise."""
        config = _config(tmp_path)
        result = {"work_item_id": "WI-4", "project_membership": None}
        reason, warning = _classify(config, result, None, None)
        assert reason == "not_requested"
        assert warning is None

    def test_explicit_project_without_membership_is_flagged(self, tmp_path: Path) -> None:
        """--project was supplied but nothing was bound: the loudest failure."""
        config = _config(tmp_path)
        result = {"work_item_id": "WI-5", "project_membership": None}
        reason, warning = _classify(config, result, None, "PROJECT-REAL")
        assert reason == "requested_but_not_created"
        assert warning is not None

    def test_every_null_membership_path_yields_a_nonempty_reason(self, tmp_path: Path) -> None:
        """The invariant, stated directly: null membership always carries a reason."""
        config = _config(tmp_path)
        cases = [
            (None, None),
            ("PROJECT-REAL", None),
            ("PROJECT-DOES-NOT-EXIST", None),
            (None, "PROJECT-REAL"),
        ]
        for project_name, project_id in cases:
            result = {"work_item_id": "WI-X", "project_membership": None}
            reason, _ = _classify(config, result, project_name, project_id)
            assert reason, f"null membership reported with no reason for {project_name=} {project_id=}"

    def test_resolution_failure_does_not_raise(self, tmp_path: Path) -> None:
        """Classification is diagnostic; it must never fail the create."""
        config = GTConfig(
            db_path=tmp_path / "missing.db",
            project_root=tmp_path,
            chroma_path=tmp_path / "chroma",
        )
        result = {"work_item_id": "WI-6", "project_membership": None}
        reason, warning = _classify(config, result, "PROJECT-REAL", None)
        assert reason in {"label_only_unknown_project", "label_only_no_membership"}
        assert warning is not None
