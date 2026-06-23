"""Stage 3 tests for scripts/advisory_backlog_router.py.

WI-4469 redirects advisory intake from automatic OPEN work_items rows to an
append-only approval-staging surface. These tests use tmp_path-rooted fixture
projects so the live candidate store and live groundtruth.db are untouched.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
GTKB_SRC = PROJECT_ROOT / "groundtruth-kb" / "src"
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "advisory_backlog_router.py"
for path in (PROJECT_ROOT, GTKB_SRC):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


@pytest.fixture(scope="module")
def router():
    spec = importlib.util.spec_from_file_location("advisory_backlog_router", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["advisory_backlog_router"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def fake_project(tmp_path: Path) -> Path:
    dropbox = tmp_path / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX"
    dropbox.mkdir(parents=True)
    bridge = tmp_path / "bridge"
    bridge.mkdir()
    (bridge / "INDEX.md").write_text("# Bridge Index\n", encoding="utf-8")
    return tmp_path


@pytest.fixture()
def db_factory(tmp_path: Path):
    from groundtruth_kb.db import KnowledgeDB

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
        "This is the first prose paragraph of the advisory. It explains the issue the router should stage.\n"
        "\n"
        "## Finding F1\n"
        f"\n{severity_line}\n"
        "### Observation\n"
        "\n"
        "Observation body here.\n"
    )


def _candidate_events(project_root: Path) -> list[dict]:
    store = project_root / ".gtkb-state" / "advisory-candidates" / "candidates.jsonl"
    if not store.exists():
        return []
    return [json.loads(line) for line in store.read_text(encoding="utf-8").splitlines() if line.strip()]


def _work_item_count(db) -> int:
    return db._get_conn().execute("SELECT COUNT(*) FROM work_items").fetchone()[0]


def test_router_stages_candidates_creates_no_work_items(router, fake_project: Path, db_factory) -> None:
    dropbox = fake_project / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX"
    _write_insights(dropbox, "INSIGHTS-2026-05-10-13-26-SAMPLE-A.md", _basic_advisory())

    result = router.run(project_root=fake_project, source="dropbox", since=None, dry_run=False, db_factory=db_factory)

    assert result.scanned == 1
    assert len(result.staged) == 1
    assert result.errors == []
    assert _work_item_count(db_factory()) == 0
    events = _candidate_events(fake_project)
    assert len(events) == 1
    assert events[0]["status"] == "staged"
    assert events[0]["source_key"] == "INSIGHTS-2026-05-10-13-26-SAMPLE-A.md"
    assert events[0]["proposed_title"] == "Route LO advisory: INSIGHTS-2026-05-10-13-26-SAMPLE-A.md"
    assert events[0]["source_spec_id"] == "GOV-STANDING-BACKLOG-001"


def test_router_idempotent_on_rerun(router, fake_project: Path, db_factory) -> None:
    dropbox = fake_project / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX"
    _write_insights(dropbox, "INSIGHTS-2026-05-10-13-26-SAMPLE-B.md", _basic_advisory())

    first = router.run(project_root=fake_project, source="dropbox", since=None, dry_run=False, db_factory=db_factory)
    second = router.run(project_root=fake_project, source="dropbox", since=None, dry_run=False, db_factory=db_factory)

    assert len(first.staged) == 1
    assert len(second.staged) == 0
    assert len(second.skipped_existing) == 1
    assert second.skipped_existing[0]["matched_in"] == "candidate_store"
    assert second.skipped_existing[0]["matched_status"] == "staged"
    assert len(_candidate_events(fake_project)) == 1


@pytest.mark.parametrize(
    ("severity", "expected_priority", "expected_token"),
    [("P0", "high", "P0"), ("P1", "high", "P1"), ("P2", "medium", "P2"), ("P3", "low", "P3")],
)
def test_router_parses_severity_for_staged_candidate(
    router,
    fake_project: Path,
    db_factory,
    severity: str,
    expected_priority: str,
    expected_token: str,
) -> None:
    dropbox = fake_project / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX"
    _write_insights(dropbox, f"INSIGHTS-2026-05-10-13-26-{severity}.md", _basic_advisory(severity=severity))

    result = router.run(project_root=fake_project, source="dropbox", since=None, dry_run=False, db_factory=db_factory)

    assert result.staged[0]["priority"] == expected_priority
    event = _candidate_events(fake_project)[0]
    assert event["severity_token"] == expected_token
    assert event["priority"] == expected_priority


def test_router_dry_run_does_not_mutate_db_or_candidate_store(router, fake_project: Path, db_factory) -> None:
    dropbox = fake_project / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX"
    _write_insights(dropbox, "INSIGHTS-2026-05-10-13-26-DRY.md", _basic_advisory())

    result = router.run(project_root=fake_project, source="dropbox", since=None, dry_run=True, db_factory=db_factory)

    assert result.scanned == 1
    assert len(result.staged) == 1
    assert result.staged[0]["status"] == "staged"
    assert _work_item_count(db_factory()) == 0
    assert _candidate_events(fake_project) == []
    assert not (fake_project / ".gtkb-state" / "advisory-router" / "last-scan.json").exists()


def test_already_promoted_source_key_not_restaged(router, fake_project: Path, db_factory) -> None:
    source_key = "INSIGHTS-2026-05-10-13-26-PROMOTED.md"
    dropbox = fake_project / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX"
    _write_insights(dropbox, source_key, _basic_advisory())
    db = db_factory()
    db.insert_work_item(
        id="WI-9999",
        title="Pre-existing promoted advisory",
        origin="hygiene",
        component="backlog",
        resolution_status="open",
        changed_by="test",
        change_reason="seed promoted advisory",
        source_spec_id="GOV-STANDING-BACKLOG-001",
        related_deliberation_ids=source_key,
    )

    result = router.run(project_root=fake_project, source="dropbox", since=None, dry_run=False, db_factory=db_factory)

    assert result.staged == []
    assert result.skipped_existing[0]["matched_in"] == "work_items"
    assert result.skipped_existing[0]["matched_wi"] == "WI-9999"
    assert _candidate_events(fake_project) == []


def test_router_writes_last_scan_with_staged_count(router, fake_project: Path, db_factory) -> None:
    dropbox = fake_project / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX"
    _write_insights(dropbox, "INSIGHTS-2026-05-10-13-26-LAST-SCAN.md", _basic_advisory())

    router.run(project_root=fake_project, source="dropbox", since=None, dry_run=False, db_factory=db_factory)

    last_scan = fake_project / ".gtkb-state" / "advisory-router" / "last-scan.json"
    payload = json.loads(last_scan.read_text(encoding="utf-8"))
    assert payload["dry_run"] is False
    assert payload["scanned"] == 1
    assert payload["staged_count"] == 1
    assert payload["skipped_existing_count"] == 0


def test_router_compact_mode_reports_staged_count(router, fake_project: Path, db_factory) -> None:
    dropbox = fake_project / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX"
    _write_insights(dropbox, "INSIGHTS-2026-05-10-13-26-COMPACT.md", _basic_advisory())
    result = router.run(project_root=fake_project, source="dropbox", since=None, dry_run=True, db_factory=db_factory)

    normal_json = json.loads(result.as_json(compact=False))
    assert "staged" in normal_json
    assert "staged_count" not in normal_json

    compact_json = json.loads(result.as_json(compact=True))
    assert "staged" not in compact_json
    assert compact_json["staged_count"] == 1
    assert compact_json["skipped_expired_count"] == 0


def test_router_compact_mode_suppresses_skipped_existing_items(router, fake_project: Path, db_factory) -> None:
    dropbox = fake_project / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX"
    _write_insights(dropbox, "INSIGHTS-2026-05-10-13-26-COMPACT-SKIPPED.md", _basic_advisory())

    router.run(project_root=fake_project, source="dropbox", since=None, dry_run=False, db_factory=db_factory)
    result = router.run(project_root=fake_project, source="dropbox", since=None, dry_run=False, db_factory=db_factory)

    normal_json = json.loads(result.as_json(compact=False))
    assert "skipped_existing" in normal_json
    assert len(normal_json["skipped_existing"]) == 1
    assert "skipped_existing_count" not in normal_json

    compact_json = json.loads(result.as_json(compact=True))
    assert "skipped_existing" not in compact_json
    assert compact_json["skipped_existing_count"] == 1
    assert compact_json["staged_count"] == 0


def test_router_retention_policy_skips_expired_advisories(router, fake_project: Path, db_factory) -> None:
    dropbox = fake_project / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX"
    _write_insights(dropbox, "INSIGHTS-2026-03-01-13-26-OLD.md", _basic_advisory(date_str="2026-03-01"))
    _write_insights(dropbox, "INSIGHTS-2026-05-10-13-26-NEW.md", _basic_advisory(date_str="2026-05-10"))

    result = router.run(
        project_root=fake_project,
        source="dropbox",
        since=None,
        dry_run=False,
        db_factory=db_factory,
        retention_policy=router.RetentionPolicy(max_advisory_age_days=60),
        now=router.date(2026, 6, 12),
    )

    assert result.scanned == 2
    assert [row["source_key"] for row in result.skipped_expired] == ["INSIGHTS-2026-03-01-13-26-OLD.md"]
    assert [row["source_key"] for row in result.staged] == ["INSIGHTS-2026-05-10-13-26-NEW.md"]
    events = _candidate_events(fake_project)
    assert [row["source_key"] for row in events] == ["INSIGHTS-2026-05-10-13-26-NEW.md"]
