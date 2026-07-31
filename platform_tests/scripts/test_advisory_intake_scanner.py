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
    (tmp_path / "bridge").mkdir()
    (tmp_path / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX").mkdir(parents=True)
    return tmp_path


@pytest.fixture()
def db_factory(tmp_path: Path):
    from groundtruth_kb.db import KnowledgeDB

    db_path = tmp_path / "groundtruth.db"

    def factory():
        return KnowledgeDB(str(db_path))

    return factory


def _advisory_body(
    *,
    title: str = "Test Advisory",
    classification: str = "adopt",
    has_gate: bool = True,
    date_str: str = "2026-07-07",
    priority: str = "P1",
) -> str:
    lines = [
        f"# {title}",
        "",
        f"Date: {date_str}",
        f"Severity: {priority}",
        "",
        "## Classification",
        f"Recommended disposition: {classification}.",
    ]
    if has_gate:
        lines.extend(
            [
                "",
                "## Required Prime Builder Owner-Grilling Gate",
                "1. Implementation implied: Yes",
                "2. Grill-the-owner questions: None",
                "3. Required durable owner decisions: None",
            ]
        )
    return "\n".join(lines) + "\n"


def _write_bridge_entry(
    project_root: Path,
    slug: str,
    *,
    version: int = 1,
    status: str = "ADVISORY",
    **body_kwargs,
) -> Path:
    path = project_root / "bridge" / f"{slug}-{version:03d}.md"
    path.write_text(f"{status}\n\n{_advisory_body(**body_kwargs)}", encoding="utf-8")
    return path


def _write_legacy_dropbox(project_root: Path, name: str, **body_kwargs) -> Path:
    path = project_root / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX" / name
    path.write_text(_advisory_body(**body_kwargs), encoding="utf-8")
    return path


def test_scanner_selects_only_live_bridge_advisories(scanner, fake_project: Path, db_factory) -> None:
    _write_bridge_entry(
        fake_project,
        "gtkb-live-adopt",
        title="Live Adopt Advisory",
        classification="adopt",
        date_str="2026-07-06",
        priority="P1",
    )
    _write_bridge_entry(
        fake_project,
        "gtkb-live-adapt",
        title="Live Adapt Advisory",
        classification="adapt",
        date_str="2026-07-07",
        priority="P2",
    )
    _write_bridge_entry(fake_project, "gtkb-reject", classification="reject")
    _write_bridge_entry(fake_project, "gtkb-missing-gate", classification="adopt", has_gate=False)
    _write_bridge_entry(fake_project, "gtkb-superseded", classification="adopt")
    _write_bridge_entry(fake_project, "gtkb-superseded", version=2, status="NEW")

    results = scanner.scan_intake_advisories(fake_project, db_factory=db_factory)

    assert [result.source_key for result in results] == ["gtkb-live-adopt", "gtkb-live-adapt"]
    assert all(result.source == "bridge" for result in results)
    assert all(result.has_grilling_gate is True for result in results)


def test_scanner_rejects_legacy_and_unnumbered_inputs(scanner, fake_project: Path, db_factory) -> None:
    _write_legacy_dropbox(
        fake_project,
        "INSIGHTS-2026-07-07-LEGACY.md",
        classification="adopt",
        has_gate=True,
    )
    (fake_project / "bridge" / "unnumbered-advisory.md").write_text(
        f"ADVISORY\n\n{_advisory_body(classification='adapt')}",
        encoding="utf-8",
    )
    _write_bridge_entry(fake_project, "gtkb-canonical", classification="adopt")

    results = scanner.scan_intake_advisories(fake_project, db_factory=db_factory)

    assert [result.source_key for result in results] == ["gtkb-canonical"]


def test_scanner_filters_advisories_already_linked_in_membase(scanner, fake_project: Path, db_factory) -> None:
    _write_bridge_entry(fake_project, "gtkb-already-promoted", classification="adopt")
    _write_bridge_entry(fake_project, "gtkb-still-live", classification="adapt")
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
        related_deliberation_ids="gtkb-already-promoted",
    )

    results = scanner.scan_intake_advisories(fake_project, db_factory=db_factory)

    assert [result.source_key for result in results] == ["gtkb-still-live"]


def test_scanner_preserves_summary_fields(scanner, fake_project: Path, db_factory) -> None:
    _write_bridge_entry(
        fake_project,
        "gtkb-fields",
        title="My Custom Title",
        classification="adapt",
        date_str="2026-07-07",
        priority="P1",
    )

    results = scanner.scan_intake_advisories(fake_project, db_factory=db_factory)

    assert len(results) == 1
    advisory = results[0]
    assert advisory.source_key == "gtkb-fields"
    assert advisory.source == "bridge"
    assert advisory.relative_path == "bridge/gtkb-fields-001.md"
    assert advisory.title == "My Custom Title"
    assert advisory.classification == "adapt"
    assert advisory.priority == "high"
    assert advisory.advisory_date == "2026-07-07"
    assert advisory.has_grilling_gate is True


def test_scanner_sorts_presentation_order(scanner, fake_project: Path, db_factory) -> None:
    _write_bridge_entry(fake_project, "gtkb-date-10", date_str="2026-07-10", priority="P1")
    _write_bridge_entry(fake_project, "gtkb-date-05", date_str="2026-07-05", priority="P3")
    _write_bridge_entry(fake_project, "gtkb-date-08-low", date_str="2026-07-08", priority="P3")
    _write_bridge_entry(fake_project, "gtkb-date-08-high", date_str="2026-07-08", priority="P1")
    _write_bridge_entry(fake_project, "gtkb-date-09-y", date_str="2026-07-09", priority="P1")
    _write_bridge_entry(fake_project, "gtkb-date-09-x", date_str="2026-07-09", priority="P1")

    results = scanner.scan_intake_advisories(fake_project, db_factory=db_factory)

    assert [result.source_key for result in results] == [
        "gtkb-date-05",
        "gtkb-date-08-high",
        "gtkb-date-08-low",
        "gtkb-date-09-x",
        "gtkb-date-09-y",
        "gtkb-date-10",
    ]


def test_cli_defaults_to_bridge_and_rejects_legacy_source_option(
    scanner,
    fake_project: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _write_bridge_entry(fake_project, "gtkb-cli", classification="adopt")
    _write_legacy_dropbox(fake_project, "INSIGHTS-2026-07-07-CLI.md", classification="adapt")

    assert scanner.main(["--project-root", str(fake_project), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["scanned_count"] == 1
    assert [item["source_key"] for item in payload["intake_ready"]] == ["gtkb-cli"]

    with pytest.raises(SystemExit) as exc_info:
        scanner.main(["--project-root", str(fake_project), "--source", "dropbox"])
    assert exc_info.value.code == 2
