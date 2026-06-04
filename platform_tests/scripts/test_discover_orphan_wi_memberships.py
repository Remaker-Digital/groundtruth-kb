"""Regression tests for scripts/discover_orphan_wi_memberships.py.

Per gtkb-orphan-wi-membership-discovery-slice-1-003 IP-2 + the verification
plan, this test file covers:

1. test_classifier_all_classes - table-driven classifier-correctness test.
2. test_recoverable_via_source_spec_extracts_project - source-spec linkage path.
3. test_unrecoverable_class_requires_owner_decision - unrecoverable preservation.
4. test_inventory_artifact_schema_compliance - JSON schema check.
5. test_review_packet_schema_compliance - markdown sections check.

These tests use synthetic fixtures rather than the live MemBase to keep the
test deterministic. The discovery script's live-MemBase behavior is verified
by the post-implementation report's apply-time discovery run.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


# Load the discovery module directly from the scripts/ path so the tests do
# not require packaging the script as an installed module.
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_SCRIPT_PATH = _REPO_ROOT / "scripts" / "discover_orphan_wi_memberships.py"


@pytest.fixture(scope="module")
def discover_module():
    """Import discover_orphan_wi_memberships as a module."""
    spec = importlib.util.spec_from_file_location(
        "discover_orphan_wi_memberships", _SCRIPT_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["discover_orphan_wi_memberships"] = module
    spec.loader.exec_module(module)
    return module


def _fixture_project_index() -> list[tuple[str, str]]:
    """Synthetic project index covering all classification paths."""
    return [
        # Longer ids first (matches the script's ordering)
        ("PROJECT-GTKB-RELIABILITY-FIXES", "GTKB-RELIABILITY-FIXES"),
        ("PROJECT-GTKB-PUSH-GATE", "PROJECT-GTKB-PUSH-GATE"),
        ("PROJECT-GTKB-GOV-CODE-QUALITY-BASELINE", "GTKB-GOV-CODE-QUALITY-BASELINE"),
    ]


# ---------------------------------------------------------------------------
# IP-2 test 1: classifier all-classes
# ---------------------------------------------------------------------------


def test_classifier_all_classes(discover_module):
    """The classifier returns the right class for each known pattern."""
    spec_to_project = {"SPEC-XYZ-001": "PROJECT-GTKB-RELIABILITY-FIXES"}
    bridge_to_project = {"gtkb-foo-bar": "PROJECT-GTKB-PUSH-GATE"}
    project_index = _fixture_project_index()

    cases = [
        # (wi_dict, expected_class)
        (
            {
                "id": "WI-1001",
                "title": "Some title",
                "source_spec_id": "SPEC-XYZ-001",
                "change_reason": "...",
            },
            "recoverable_via_source_spec",
        ),
        (
            {
                "id": "WI-2002",
                "title": "Some title",
                "source_spec_id": None,
                "change_reason": "implemented via bridge/gtkb-foo-bar-005.md",
            },
            "recoverable_via_bridge_thread",
        ),
        (
            {
                "id": "WI-GTKB-GOV-CODE-QUALITY-BASELINE-SLICE-2",
                "title": "Code quality slice 2",
                "source_spec_id": None,
                "change_reason": "",
            },
            "recoverable_via_id_match",
        ),
        (
            {
                "id": "WI-9999",
                "title": "GTKB-RELIABILITY-FIXES additional defect-fix work",
                "source_spec_id": None,
                "change_reason": "",
            },
            "recoverable_via_title_match",
        ),
        (
            {
                "id": "WI-7777",
                "title": "Something totally unrelated",
                "source_spec_id": None,
                "change_reason": "no provenance",
            },
            "unrecoverable",
        ),
    ]

    for wi, expected_class in cases:
        result = discover_module._classify_orphan(
            wi, spec_to_project, bridge_to_project, project_index
        )
        assert result["recoverability_class"] == expected_class, (
            f"WI {wi['id']} expected {expected_class}, got {result['recoverability_class']}"
        )
        # confidence_score must match the class's canonical value
        expected_confidence = discover_module.CONFIDENCE_BY_CLASS[expected_class]
        assert result["confidence_score"] == expected_confidence


# ---------------------------------------------------------------------------
# IP-2 test 2: source-spec recoverability extracts project
# ---------------------------------------------------------------------------


def test_recoverable_via_source_spec_extracts_project(discover_module):
    """The source_spec path resolves to the project_artifact_links project_id."""
    spec_to_project = {"SPEC-INTAKE-1262c1": "PROJECT-GTKB-GOV-CODE-QUALITY-BASELINE"}
    project_index = _fixture_project_index()

    wi = {
        "id": "WI-AUTO-SPEC-INTAKE-1262C1",
        "title": "Implement SPEC-INTAKE-1262c1: grill-me-for-clarification owner clarification interview skill",
        "source_spec_id": "SPEC-INTAKE-1262c1",
        "change_reason": "auto-created from spec intake",
    }

    result = discover_module._classify_orphan(wi, spec_to_project, {}, project_index)
    assert result["recoverability_class"] == "recoverable_via_source_spec"
    assert result["candidate_project_id"] == "PROJECT-GTKB-GOV-CODE-QUALITY-BASELINE"
    assert "source_spec_id=SPEC-INTAKE-1262c1" in result["evidence_path"]


# ---------------------------------------------------------------------------
# IP-2 test 3: unrecoverable class preservation
# ---------------------------------------------------------------------------


def test_unrecoverable_class_requires_owner_decision(discover_module):
    """An unrecoverable orphan is NOT silently bucketed into a recoverable class."""
    # No source_spec, no bridge thread, no id match, no title match.
    wi = {
        "id": "WI-NO-PROVENANCE-001",
        "title": "Untracked legacy item with no metadata",
        "source_spec_id": None,
        "change_reason": "auto-imported from legacy system",
    }
    result = discover_module._classify_orphan(wi, {}, {}, _fixture_project_index())
    assert result["recoverability_class"] == "unrecoverable"
    assert result["candidate_project_id"] is None
    assert result["confidence_score"] == 0.00


# ---------------------------------------------------------------------------
# IP-2 test 4: inventory artifact schema compliance
# ---------------------------------------------------------------------------


def test_inventory_artifact_schema_compliance(discover_module, tmp_path, monkeypatch):
    """The JSON inventory artifact has all required stable fields."""
    # Build an inventory dict via the public path with minimal mock DB shape.
    inventory = {
        "run_id": "test-run-001",
        "generated_at": "2026-05-28T15:00:00Z",
        "total_open_wi_count": 3,
        "orphan_count": 2,
        "orphan_count_by_class": {cls: 0 for cls in discover_module.RECOVERABILITY_CLASSES},
        "orphans": [
            {
                "id": "WI-1001",
                "title": "test orphan 1",
                "priority": "P1",
                "origin": "hygiene",
                "recoverability_class": "recoverable_via_source_spec",
                "candidate_project_id": "PROJECT-X",
                "confidence_score": 0.95,
                "evidence_path": "source_spec_id=SPEC-X",
                "root_cause_changed_by": "claude-prime-builder",
            },
            {
                "id": "WI-1002",
                "title": "test orphan 2",
                "priority": None,
                "origin": "defect",
                "recoverability_class": "unrecoverable",
                "candidate_project_id": None,
                "confidence_score": 0.00,
                "evidence_path": "no heuristic yielded a candidate project",
                "root_cause_changed_by": "<unknown>",
            },
        ],
    }
    inventory["orphan_count_by_class"]["recoverable_via_source_spec"] = 1
    inventory["orphan_count_by_class"]["unrecoverable"] = 1

    paths = discover_module.emit_outputs(inventory, tmp_path / "out")
    assert paths["report"].exists()

    import json

    loaded = json.loads(paths["report"].read_text(encoding="utf-8"))

    # Required top-level fields
    for field in [
        "run_id",
        "generated_at",
        "total_open_wi_count",
        "orphan_count",
        "orphan_count_by_class",
        "orphans",
    ]:
        assert field in loaded, f"missing top-level field {field}"

    # Required per-WI fields
    required_orphan_fields = {
        "id",
        "title",
        "priority",
        "origin",
        "recoverability_class",
        "candidate_project_id",
        "confidence_score",
        "evidence_path",
        "root_cause_changed_by",
    }
    for rec in loaded["orphans"]:
        missing = required_orphan_fields - set(rec.keys())
        assert not missing, f"orphan {rec.get('id')} missing fields: {missing}"

    # Class taxonomy is complete in the orphan_count_by_class dict
    for cls in discover_module.RECOVERABILITY_CLASSES:
        assert cls in loaded["orphan_count_by_class"]


# ---------------------------------------------------------------------------
# IP-2 test 5: review packet schema compliance
# ---------------------------------------------------------------------------


def test_review_packet_schema_compliance(discover_module, tmp_path):
    """The markdown review packet has all four required sections."""
    inventory = {
        "run_id": "test-run-002",
        "generated_at": "2026-05-28T15:00:00Z",
        "total_open_wi_count": 1,
        "orphan_count": 1,
        "orphan_count_by_class": {cls: 0 for cls in discover_module.RECOVERABILITY_CLASSES},
        "orphans": [
            {
                "id": "WI-2001",
                "title": "test orphan",
                "priority": "P2",
                "origin": "new",
                "recoverability_class": "unrecoverable",
                "candidate_project_id": None,
                "confidence_score": 0.00,
                "evidence_path": "no heuristic yielded a candidate project",
                "root_cause_changed_by": "codex-prime-builder",
            },
        ],
    }
    inventory["orphan_count_by_class"]["unrecoverable"] = 1
    paths = discover_module.emit_outputs(inventory, tmp_path / "out")
    summary_text = paths["summary"].read_text(encoding="utf-8")

    # Required sections
    for section_heading in [
        "## Orphan Count By Class",
        "## Top 10 Orphans By Confidence",
        "## Root Cause Attribution Table",
        "## Unrecoverable Orphans",
    ]:
        assert section_heading in summary_text, f"missing section: {section_heading}"

    # Resolution options listed in the unrecoverable section
    assert "Assign to an existing project" in summary_text
    assert "Create a new project" in summary_text
    assert "Retire" in summary_text
    assert "Defer" in summary_text


# ---------------------------------------------------------------------------
# Regression test for NO-GO-008 P1-001: root-cause attribution must use the
# version=1 immutable creator row, not the mutable latest changed_by field.
# ---------------------------------------------------------------------------


def test_root_cause_attribution_uses_version_1_creator(discover_module, tmp_path):
    """Later non-creation updates MUST NOT overwrite root-cause attribution.

    Regression test for bridge/gtkb-orphan-wi-membership-discovery-slice-1-008
    P1-001. Builds a synthetic multi-version WI fixture in a tmp_path sqlite
    DB via KnowledgeDB, runs build_inventory, asserts that
    root_cause_changed_by equals the version=1 changed_by, not the latest
    mutable changed_by.

    Reproduces the WI-3330-shaped pattern Codex cited in NO-GO-008 evidence
    (advisory-router create -> Codex backfill -> Claude migration) and proves
    the corrected logic returns the creator, not either later author.
    """
    import sys as _sys
    from pathlib import Path as _Path

    # Ensure groundtruth_kb is importable from the script's perspective.
    _repo_root = _Path(__file__).resolve().parents[2]
    _kb_src = _repo_root / "groundtruth-kb" / "src"
    if str(_kb_src) not in _sys.path:
        _sys.path.insert(0, str(_kb_src))
    from groundtruth_kb.db import KnowledgeDB

    db_path = tmp_path / "regression.db"
    db = KnowledgeDB(db_path)
    conn = db._get_conn()  # noqa: SLF001 - direct access for fixture construction

    # Insert one orphan WI with three versions to simulate the WI-3330 pattern:
    #   v1 changed_by='advisory-backlog-router/1.0'  (THE CREATOR)
    #   v2 changed_by='prime-builder/codex/A'        (later approval backfill)
    #   v3 changed_by='prime-builder/claude/B'       (later priority migration)
    # No active membership row -> orphan.
    for version, author, when in [
        (1, "advisory-backlog-router/1.0", "2026-04-15T10:00:00+00:00"),
        (2, "prime-builder/codex/A", "2026-05-10T12:00:00+00:00"),
        (3, "prime-builder/claude/B", "2026-05-27T14:00:00+00:00"),
    ]:
        conn.execute(
            """INSERT INTO work_items (
                id, version, title, description, priority, origin, component,
                resolution_status, changed_by, changed_at, change_reason
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                "WI-TEST-REGRESSION-9001",
                version,
                "Regression-test orphan WI for v1 creator attribution",
                "Multi-version fixture proving root_cause uses v1 not latest",
                "P3",
                "hygiene",
                "test_fixture",
                "open",
                author,
                when,
                f"v{version} insert by regression fixture",
            ),
        )
    conn.commit()

    inventory = discover_module.build_inventory(db, run_id="regression-v1-creator-001")

    assert inventory["orphan_count"] == 1, (
        f"Expected exactly 1 orphan, got {inventory['orphan_count']}: "
        f"orphans={inventory['orphans']}"
    )
    rec = inventory["orphans"][0]
    assert rec["id"] == "WI-TEST-REGRESSION-9001"
    assert rec["root_cause_changed_by"] == "advisory-backlog-router/1.0", (
        f"Root-cause MUST be v1 creator (advisory-backlog-router/1.0), "
        f"got {rec['root_cause_changed_by']}. Latest-author was "
        f"{rec.get('latest_mutator_changed_by')}; the test proves a "
        f"latest-author-based fallback would have produced "
        f"'prime-builder/claude/B' (incorrect)."
    )
    assert rec["latest_mutator_changed_by"] == "prime-builder/claude/B", (
        f"Diagnostic latest_mutator field should expose the most recent "
        f"mutation author, got {rec.get('latest_mutator_changed_by')}"
    )
