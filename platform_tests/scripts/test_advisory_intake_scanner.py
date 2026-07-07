"""Unit tests for scripts/advisory_intake_scanner.py."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
GTKB_SRC = PROJECT_ROOT / "groundtruth-kb" / "src"
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "advisory_intake_scanner.py"
for path in (PROJECT_ROOT, GTKB_SRC):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


@pytest.fixture(scope="module")
def scanner():
    spec = importlib.util.spec_from_file_location("advisory_intake_scanner", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["advisory_intake_scanner"] = module
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


def _write_advisory_file(
    path: Path,
    *,
    title: str = "Test Advisory",
    classification: str = "adopt",
    has_gate: bool = True,
    date_str: str = "2026-07-07",
    priority: str = "high",
    is_bridge: bool = False,
) -> None:
    content_lines = []
    if is_bridge:
        content_lines.append("ADVISORY\n")
        content_lines.append(f"Date: {date_str}\n")

    content_lines.append("Mode: advisory report\n")
    content_lines.append(f"# {title}\n")
    content_lines.append(f"Date: {date_str}\n")
    content_lines.append("## Classification\n")
    content_lines.append(f"We recommend to {classification} this design.\n")
    content_lines.append(f"Severity: {priority}\n")

    if has_gate:
        content_lines.append("\n## Required Prime Builder Owner-Grilling Gate\n")
        content_lines.append("1. Implementation implied: Yes\n")
        content_lines.append("2. Grill-the-owner questions: None\n")
        content_lines.append("3. Required durable owner decisions: None\n")

    path.write_text("\n".join(content_lines), encoding="utf-8")


def _append_candidate_status(
    project_root: Path,
    source_key: str,
    status: str,
) -> None:
    store = project_root / ".gtkb-state" / "advisory-candidates" / "candidates.jsonl"
    store.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "event": status,
        "status": status,
        "source": "dropbox",
        "source_key": source_key,
        "relative_path": f"independent-progress-assessments/CODEX-INSIGHT-DROPBOX/{source_key}",
        "proposed_title": f"Route LO advisory: {source_key}",
        "priority": "high",
    }
    with store.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")


def test_scanner_selects_intake_ready_advisories(scanner, fake_project: Path, db_factory) -> None:
    dropbox = fake_project / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX"

    # 1. Valid: adopt with gate
    _write_advisory_file(dropbox / "INSIGHTS-2026-07-07-A.md", classification="adopt", has_gate=True)
    # 2. Valid: adapt with gate
    _write_advisory_file(dropbox / "INSIGHTS-2026-07-07-B.md", classification="adapt", has_gate=True)
    # 3. Invalid: reject (even if it has a gate, not adopt/adapt)
    _write_advisory_file(dropbox / "INSIGHTS-2026-07-07-C.md", classification="reject", has_gate=True)
    # 4. Invalid: adopt but no gate
    _write_advisory_file(dropbox / "INSIGHTS-2026-07-07-D.md", classification="adopt", has_gate=False)

    results = scanner.scan_intake_advisories(fake_project, source="dropbox", db_factory=db_factory)

    assert len(results) == 2
    keys = [r.source_key for r in results]
    assert "INSIGHTS-2026-07-07-A.md" in keys
    assert "INSIGHTS-2026-07-07-B.md" in keys
    assert "INSIGHTS-2026-07-07-C.md" not in keys
    assert "INSIGHTS-2026-07-07-D.md" not in keys


def test_scanner_selects_live_bridge_advisory_threads(scanner, fake_project: Path, db_factory) -> None:
    bridge = fake_project / "bridge"

    _write_advisory_file(
        bridge / "gtkb-live-adopt-001.md",
        title="Live Adopt Advisory",
        classification="adopt",
        has_gate=True,
        date_str="2026-07-06",
        priority="P1",
        is_bridge=True,
    )
    _write_advisory_file(
        bridge / "gtkb-live-adapt-001.md",
        title="Live Adapt Advisory",
        classification="adapt",
        has_gate=True,
        date_str="2026-07-07",
        priority="P2",
        is_bridge=True,
    )
    _write_advisory_file(
        bridge / "gtkb-reject-001.md",
        classification="reject",
        has_gate=True,
        is_bridge=True,
    )
    _write_advisory_file(
        bridge / "gtkb-missing-gate-001.md",
        classification="adopt",
        has_gate=False,
        is_bridge=True,
    )
    _write_advisory_file(
        bridge / "gtkb-superseded-001.md",
        classification="adopt",
        has_gate=True,
        is_bridge=True,
    )
    (bridge / "gtkb-superseded-002.md").write_text(
        "NEW\n\nDocument: gtkb-superseded\nVersion: 002\n",
        encoding="utf-8",
    )

    results = scanner.scan_intake_advisories(fake_project, source="bridge", db_factory=db_factory)

    keys = [r.source_key for r in results]
    assert keys == ["gtkb-live-adopt", "gtkb-live-adapt"]
    assert all(r.source == "bridge" for r in results)
    assert all(r.has_grilling_gate is True for r in results)


def test_scanner_filters_non_live_advisories(scanner, fake_project: Path, db_factory) -> None:
    dropbox = fake_project / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX"

    # Ready but will be marked as promoted in candidate store
    _write_advisory_file(dropbox / "INSIGHTS-2026-07-07-PROM.md", classification="adopt", has_gate=True)
    _append_candidate_status(fake_project, "INSIGHTS-2026-07-07-PROM.md", "promoted")

    # Ready but will be marked as rejected in candidate store
    _write_advisory_file(dropbox / "INSIGHTS-2026-07-07-REJ.md", classification="adopt", has_gate=True)
    _append_candidate_status(fake_project, "INSIGHTS-2026-07-07-REJ.md", "rejected")

    # Ready and is only staged in candidate store (should be live)
    _write_advisory_file(dropbox / "INSIGHTS-2026-07-07-STAGED.md", classification="adopt", has_gate=True)
    _append_candidate_status(fake_project, "INSIGHTS-2026-07-07-STAGED.md", "staged")

    # Ready and is not in candidate store at all (should be live)
    _write_advisory_file(dropbox / "INSIGHTS-2026-07-07-NEW.md", classification="adopt", has_gate=True)

    # Ready but already has work item row in DB
    _write_advisory_file(dropbox / "INSIGHTS-2026-07-07-DB.md", classification="adopt", has_gate=True)
    db = db_factory()
    db.insert_work_item(
        id="WI-9999",
        title="Promoted advisory in DB",
        origin="hygiene",
        component="backlog",
        resolution_status="open",
        changed_by="test",
        change_reason="promote advisory",
        source_spec_id="GOV-STANDING-BACKLOG-001",
        related_deliberation_ids="INSIGHTS-2026-07-07-DB.md",
    )

    results = scanner.scan_intake_advisories(fake_project, source="dropbox", db_factory=db_factory)

    keys = [r.source_key for r in results]
    assert "INSIGHTS-2026-07-07-PROM.md" not in keys
    assert "INSIGHTS-2026-07-07-REJ.md" not in keys
    assert "INSIGHTS-2026-07-07-DB.md" not in keys
    assert "INSIGHTS-2026-07-07-STAGED.md" in keys
    assert "INSIGHTS-2026-07-07-NEW.md" in keys


def test_scanner_preserves_summary_fields(scanner, fake_project: Path, db_factory) -> None:
    dropbox = fake_project / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX"
    _write_advisory_file(
        dropbox / "INSIGHTS-2026-07-07-FIELDS.md",
        title="My Custom Title",
        classification="adapt",
        has_gate=True,
        date_str="2026-07-07",
        priority="P1",
    )

    results = scanner.scan_intake_advisories(fake_project, source="dropbox", db_factory=db_factory)

    assert len(results) == 1
    adv = results[0]
    assert adv.source_key == "INSIGHTS-2026-07-07-FIELDS.md"
    assert adv.source == "dropbox"
    assert adv.relative_path == "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-07-07-FIELDS.md"
    assert adv.title == "My Custom Title"
    assert adv.classification == "adapt"
    assert adv.priority == "high"  # mapped from P1
    assert adv.advisory_date == "2026-07-07"
    assert adv.has_grilling_gate is True


def test_scanner_sorts_presentation_order(scanner, fake_project: Path, db_factory) -> None:
    dropbox = fake_project / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX"

    # Oldest date should come first
    _write_advisory_file(dropbox / "INSIGHTS-2026-07-10-A.md", date_str="2026-07-10", priority="P1")
    _write_advisory_file(dropbox / "INSIGHTS-2026-07-05-A.md", date_str="2026-07-05", priority="P3")  # P3 = low
    # Equal date: High priority (P1) comes before Low priority (P3)
    _write_advisory_file(dropbox / "INSIGHTS-2026-07-08-LOW.md", date_str="2026-07-08", priority="P3")
    _write_advisory_file(dropbox / "INSIGHTS-2026-07-08-HIGH.md", date_str="2026-07-08", priority="P1")
    # Equal date and priority: alphabetical sort by source_key
    _write_advisory_file(dropbox / "INSIGHTS-2026-07-09-Y.md", date_str="2026-07-09", priority="P1")
    _write_advisory_file(dropbox / "INSIGHTS-2026-07-09-X.md", date_str="2026-07-09", priority="P1")

    results = scanner.scan_intake_advisories(fake_project, source="dropbox", db_factory=db_factory)

    keys = [r.source_key for r in results]
    expected_order = [
        "INSIGHTS-2026-07-05-A.md",  # 2026-07-05
        "INSIGHTS-2026-07-08-HIGH.md",  # 2026-07-08 High
        "INSIGHTS-2026-07-08-LOW.md",  # 2026-07-08 Low
        "INSIGHTS-2026-07-09-X.md",  # 2026-07-09 High (X < Y)
        "INSIGHTS-2026-07-09-Y.md",  # 2026-07-09 High
        "INSIGHTS-2026-07-10-A.md",  # 2026-07-10
    ]
    assert keys == expected_order
