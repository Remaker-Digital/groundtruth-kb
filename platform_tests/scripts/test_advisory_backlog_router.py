"""Spec-derived tests for scripts/advisory_backlog_router.py (Slice 1 IPs 1-4).

Per ``bridge/gtkb-self-diagnostic-leak-closure-slice-1-advisory-router-009.md``
REVISED-4 (Codex GO at -010). Each test maps to a verifiable behavior of the
router service.

Uses ``tmp_path``-rooted fixture projects with fresh ``groundtruth.db`` files
so tests are deterministic and independent of live state.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "advisory_backlog_router.py"


@pytest.fixture(scope="module")
def router():
    """Load ``advisory_backlog_router.py`` as a module without executing main().

    Registers the module in ``sys.modules`` before ``exec_module`` so Python
    3.14's stricter ``@dataclass`` lookup (which reads
    ``sys.modules.get(cls.__module__).__dict__``) finds the module dict.
    """
    spec = importlib.util.spec_from_file_location("advisory_backlog_router", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["advisory_backlog_router"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def fake_project(tmp_path):
    """Build a minimal project tree (dropbox + bridge/INDEX.md) for one test."""
    dropbox = tmp_path / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX"
    dropbox.mkdir(parents=True)
    bridge = tmp_path / "bridge"
    bridge.mkdir()
    (bridge / "INDEX.md").write_text("# Bridge Index\n", encoding="utf-8")
    return tmp_path


@pytest.fixture()
def db_factory(tmp_path):
    """Return a callable yielding a KnowledgeDB rooted at the project's groundtruth.db."""
    from groundtruth_kb.db import KnowledgeDB  # imported lazily so test collection stays cheap

    db_path = tmp_path / "groundtruth.db"

    def factory():
        return KnowledgeDB(str(db_path))

    return factory


def _write_insights(dropbox: Path, name: str, body: str) -> Path:
    path = dropbox / name
    path.write_text(body, encoding="utf-8")
    return path


def _basic_advisory(date_str: str = "2026-05-10", severity: str | None = "P1") -> str:
    severity_line = f"Severity: {severity}\n" if severity is not None else ""
    return (
        "# Sample LO Advisory Title\n"
        "\n"
        f"Date: {date_str}\n"
        "Author: Codex, Loyal Opposition\n"
        "Role: Loyal Opposition\n"
        "Audience: Prime Builder\n"
        "\n"
        "## Claim\n"
        "\n"
        "This is the first prose paragraph of the advisory. It explains the "
        "issue the router should route into the backlog.\n"
        "\n"
        "## Finding F1\n"
        f"\n{severity_line}\n"
        "### Observation\n"
        "\n"
        "Observation body here.\n"
    )


# 1.
def test_router_creates_wi_for_new_advisory(router, fake_project, db_factory):
    dropbox = fake_project / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX"
    _write_insights(dropbox, "INSIGHTS-2026-05-10-13-26-SAMPLE-A.md", _basic_advisory())
    result = router.run(project_root=fake_project, source="dropbox", since=None, dry_run=False, db_factory=db_factory)
    assert result.scanned == 1
    assert len(result.created) == 1
    assert result.created[0]["id"].startswith("WI-")
    assert result.created[0]["source"] == "dropbox"
    assert result.created[0]["source_key"] == "INSIGHTS-2026-05-10-13-26-SAMPLE-A.md"
    assert result.errors == []


# 2.
def test_router_idempotent_on_rerun(router, fake_project, db_factory):
    dropbox = fake_project / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX"
    _write_insights(dropbox, "INSIGHTS-2026-05-10-13-26-SAMPLE-B.md", _basic_advisory())
    first = router.run(project_root=fake_project, source="dropbox", since=None, dry_run=False, db_factory=db_factory)
    second = router.run(project_root=fake_project, source="dropbox", since=None, dry_run=False, db_factory=db_factory)
    assert len(first.created) == 1
    assert len(second.created) == 0
    assert len(second.skipped_existing) == 1
    assert second.skipped_existing[0]["matched_wi"] == first.created[0]["id"]


# 3.
@pytest.mark.parametrize(
    "severity,expected_priority",
    [("P0", "high"), ("P1", "high"), ("P2", "medium"), ("P3", "low"), ("P4", "low")],
)
def test_router_parses_severity_from_header(router, fake_project, db_factory, severity, expected_priority):
    dropbox = fake_project / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX"
    filename = f"INSIGHTS-2026-05-10-13-26-{severity}.md"
    _write_insights(dropbox, filename, _basic_advisory(severity=severity))
    result = router.run(project_root=fake_project, source="dropbox", since=None, dry_run=True, db_factory=db_factory)
    assert result.scanned == 1
    assert result.created[0]["priority"] == expected_priority


# 4.
def test_router_defaults_priority_when_severity_missing(router, fake_project, db_factory):
    dropbox = fake_project / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX"
    _write_insights(
        dropbox,
        "INSIGHTS-2026-05-10-13-26-NO-SEVERITY.md",
        _basic_advisory(severity=None),
    )
    result = router.run(project_root=fake_project, source="dropbox", since=None, dry_run=True, db_factory=db_factory)
    assert result.scanned == 1
    assert result.created[0]["priority"] == "low"


# 5.
def test_router_skips_advisories_already_in_bridge_threads(router, fake_project, db_factory):
    """When a WI's ``related_bridge_threads`` references the advisory's source key, skip."""
    dropbox = fake_project / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX"
    _write_insights(dropbox, "INSIGHTS-2026-05-10-13-26-SAMPLE-C.md", _basic_advisory())

    # Pre-populate a work_item that references the advisory filename via related_deliberation_ids.
    db = db_factory()
    db.insert_work_item(
        id="WI-9999",
        title="Pre-existing manual routing",
        origin="hygiene",
        component="backlog",
        resolution_status="open",
        changed_by="test/manual",
        change_reason="pre-populate for idempotency test",
        source_spec_id="GOV-STANDING-BACKLOG-001",
        related_deliberation_ids="INSIGHTS-2026-05-10-13-26-SAMPLE-C.md",
    )

    result = router.run(project_root=fake_project, source="dropbox", since=None, dry_run=False, db_factory=db_factory)
    assert result.scanned == 1
    assert len(result.created) == 0
    assert len(result.skipped_existing) == 1
    assert result.skipped_existing[0]["matched_wi"] == "WI-9999"


# 6.
def test_router_dry_run_does_not_mutate(router, fake_project, db_factory):
    dropbox = fake_project / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX"
    _write_insights(dropbox, "INSIGHTS-2026-05-10-13-26-SAMPLE-D.md", _basic_advisory())
    result = router.run(project_root=fake_project, source="dropbox", since=None, dry_run=True, db_factory=db_factory)
    assert result.scanned == 1
    assert len(result.created) == 1
    assert result.created[0]["id"] == "<dry-run>"
    # Confirm the table did not gain a row.
    db = db_factory()
    rows = db._get_conn().execute("SELECT COUNT(*) FROM work_items").fetchone()
    assert rows[0] == 0
    # And the last-scan file was NOT written.
    last_scan = fake_project / ".gtkb-state" / "advisory-router" / "last-scan.json"
    assert not last_scan.exists()


# 7.
def test_router_handles_malformed_advisory(router, fake_project, db_factory, monkeypatch):
    """A failure mid-loop becomes an entry in ``result.errors``, not a hard crash."""
    dropbox = fake_project / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX"
    _write_insights(dropbox, "INSIGHTS-2026-05-10-13-26-BAD.md", _basic_advisory())

    # Force insert_wi_for_advisory to raise, simulating a malformed/uninsertable advisory.
    def _boom(db, advisory):
        raise RuntimeError("simulated insert failure")

    monkeypatch.setattr(router, "insert_wi_for_advisory", _boom)

    result = router.run(project_root=fake_project, source="dropbox", since=None, dry_run=False, db_factory=db_factory)
    assert result.scanned == 1
    assert len(result.errors) == 1
    assert "simulated insert failure" in result.errors[0]["error"]
    assert result.errors[0]["source_key"] == "INSIGHTS-2026-05-10-13-26-BAD.md"
    # And no rows were created in result.created.
    assert result.created == []


# 8.
def test_router_writes_last_scan_timestamp(router, fake_project, db_factory):
    dropbox = fake_project / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX"
    _write_insights(dropbox, "INSIGHTS-2026-05-10-13-26-SAMPLE-E.md", _basic_advisory())
    router.run(project_root=fake_project, source="dropbox", since=None, dry_run=False, db_factory=db_factory)
    last_scan = fake_project / ".gtkb-state" / "advisory-router" / "last-scan.json"
    assert last_scan.is_file()
    payload = json.loads(last_scan.read_text(encoding="utf-8"))
    assert "last_scan_started_at" in payload
    assert "last_scan_finished_at" in payload
    assert payload["dry_run"] is False
    assert payload["scanned"] == 1
    assert payload["created_count"] == 1
    assert payload["source"] == "dropbox"


# 9.
def test_router_uses_hygiene_origin(router, fake_project, db_factory):
    dropbox = fake_project / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX"
    _write_insights(dropbox, "INSIGHTS-2026-05-10-13-26-SAMPLE-F.md", _basic_advisory())
    router.run(project_root=fake_project, source="dropbox", since=None, dry_run=False, db_factory=db_factory)
    db = db_factory()
    row = (
        db._get_conn()
        .execute(
            "SELECT origin FROM current_work_items WHERE related_deliberation_ids LIKE ?",
            ("%INSIGHTS-2026-05-10-13-26-SAMPLE-F.md%",),
        )
        .fetchone()
    )
    assert row is not None
    assert row[0] == "hygiene"


# 10.
def test_router_sets_source_spec_id(router, fake_project, db_factory):
    dropbox = fake_project / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX"
    _write_insights(dropbox, "INSIGHTS-2026-05-10-13-26-SAMPLE-G.md", _basic_advisory())
    router.run(project_root=fake_project, source="dropbox", since=None, dry_run=False, db_factory=db_factory)
    db = db_factory()
    row = (
        db._get_conn()
        .execute(
            "SELECT source_spec_id FROM current_work_items WHERE related_deliberation_ids LIKE ?",
            ("%INSIGHTS-2026-05-10-13-26-SAMPLE-G.md%",),
        )
        .fetchone()
    )
    assert row is not None
    assert row[0] == "GOV-STANDING-BACKLOG-001"


# 11.
def test_canonical_glossary_contains_advisory_router_entry():
    """IP-4 glossary edit lands the ``advisory-router`` entry in canonical-terminology.md.

    Runs against the LIVE project glossary, not a fixture; this test fails until
    the IP-4 narrative-artifact-approval-packet workflow is executed. Verification
    plan §4 requires this assertion.
    """
    glossary = PROJECT_ROOT / ".claude" / "rules" / "canonical-terminology.md"
    body = glossary.read_text(encoding="utf-8-sig")
    assert "### advisory-router" in body, (
        "Slice 1 IP-4 requires a ### advisory-router entry in "
        ".claude/rules/canonical-terminology.md, landed via the narrative-artifact "
        "approval-packet workflow per .claude/hooks/narrative-artifact-approval-gate.py"
    )
    assert "scripts/advisory_backlog_router.py" in body, (
        "advisory-router glossary entry should include an Implementation pointer to scripts/advisory_backlog_router.py"
    )


def test_router_compact_mode(router, fake_project, db_factory):
    dropbox = fake_project / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX"
    _write_insights(dropbox, "INSIGHTS-2026-05-10-13-26-COMPACT.md", _basic_advisory())
    result = router.run(project_root=fake_project, source="dropbox", since=None, dry_run=True, db_factory=db_factory)

    # 1. Non-compact format check
    normal_json = json.loads(result.as_json(compact=False))
    assert "created" in normal_json
    assert "skipped_existing" in normal_json
    assert "created_count" not in normal_json
    assert "skipped_existing_count" not in normal_json

    # 2. Compact format check
    compact_json = json.loads(result.as_json(compact=True))
    assert "created" not in compact_json
    assert "skipped_existing" not in compact_json
    assert compact_json["created_count"] == 1
    assert compact_json["skipped_existing_count"] == 0
