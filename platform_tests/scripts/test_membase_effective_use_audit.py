from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

from groundtruth_kb.membase_effective_use_audit import (
    AuditResult,
    parse_bridge_index,
    run_audit,
    write_audit_report,
)


class FakeDB:
    def __init__(self, specs: list[dict[str, str]]) -> None:
        self._specs = specs

    def list_specs(self) -> list[dict[str, str]]:
        return self._specs

    def get_spec(self, spec_id: str) -> dict[str, str] | None:
        for spec in self._specs:
            if spec.get("id") == spec_id:
                return spec
        return None


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_parse_bridge_index_captures_latest_status_and_versions(tmp_path: Path) -> None:
    index = tmp_path / "bridge" / "INDEX.md"
    _write(
        index,
        "\n".join(
            [
                "Document: gtkb-example",
                "VERIFIED: bridge/gtkb-example-002.md",
                "NEW: bridge/gtkb-example-001.md",
                "",
            ]
        ),
    )

    entries = parse_bridge_index(index)

    assert len(entries) == 1
    assert entries[0].document == "gtkb-example"
    assert entries[0].latest_status == "VERIFIED"
    assert entries[0].latest_path == "bridge/gtkb-example-002.md"
    assert entries[0].version_paths == ("bridge/gtkb-example-002.md", "bridge/gtkb-example-001.md")


def test_run_audit_flags_verified_bridge_citing_unverified_spec(tmp_path: Path) -> None:
    _write(tmp_path / "bridge" / "INDEX.md", "Document: gtkb-example\nVERIFIED: bridge/gtkb-example-001.md\n")
    _write(tmp_path / "bridge" / "gtkb-example-001.md", "Specification Links\n- SPEC-EXAMPLE-001\n")
    db = FakeDB([{"id": "SPEC-EXAMPLE-001", "status": "specified", "changed_at": "2026-05-01T00:00:00+00:00"}])

    result = run_audit(tmp_path, db=db, now=datetime(2026, 6, 1, tzinfo=UTC))

    assert result.bridge_entries_scanned == 1
    assert result.findings[0].lens == "verified_state_mismatch"
    assert result.findings[0].subject == "SPEC-EXAMPLE-001"
    assert result.findings[0].references == ("bridge/gtkb-example-001.md",)


def test_run_audit_ignores_verified_bridge_citing_verified_spec(tmp_path: Path) -> None:
    _write(tmp_path / "bridge" / "INDEX.md", "Document: gtkb-example\nVERIFIED: bridge/gtkb-example-001.md\n")
    _write(tmp_path / "bridge" / "gtkb-example-001.md", "Specification Links\n- SPEC-EXAMPLE-001\n")
    db = FakeDB([{"id": "SPEC-EXAMPLE-001", "status": "verified", "changed_at": "2026-05-01T00:00:00+00:00"}])

    result = run_audit(tmp_path, db=db, now=datetime(2026, 6, 1, tzinfo=UTC))

    assert result.findings == ()


def test_run_audit_flags_memory_duplication_of_three_spec_sentences(tmp_path: Path) -> None:
    _write(tmp_path / "bridge" / "INDEX.md", "")
    _write(
        tmp_path / "memory" / "MEMORY.md",
        "First durable sentence. Second durable sentence. Third durable sentence.",
    )
    db = FakeDB(
        [
            {
                "id": "SPEC-DUPLICATE-001",
                "status": "verified",
                "changed_at": "2026-05-01T00:00:00+00:00",
                "description": "First durable sentence. Second durable sentence. Third durable sentence.",
            }
        ]
    )

    result = run_audit(tmp_path, db=db, now=datetime(2026, 6, 1, tzinfo=UTC))

    assert [finding.lens for finding in result.findings] == ["duplicated_canonical_content"]
    assert result.findings[0].subject == "SPEC-DUPLICATE-001"


def test_run_audit_flags_deliberation_draft_candidates(tmp_path: Path) -> None:
    _write(tmp_path / "bridge" / "INDEX.md", "")
    _write(tmp_path / "memory" / "MEMORY.md", "draft delib: owner said this should become durable.")

    result = run_audit(tmp_path, db=FakeDB([]), now=datetime(2026, 6, 1, tzinfo=UTC))

    assert [finding.lens for finding in result.findings] == ["delib_draft_candidate"]
    assert result.findings[0].subject == "MEMORY.md"


def test_run_audit_applies_age_filter_to_specs(tmp_path: Path) -> None:
    _write(tmp_path / "bridge" / "INDEX.md", "Document: gtkb-example\nVERIFIED: bridge/gtkb-example-001.md\n")
    _write(tmp_path / "bridge" / "gtkb-example-001.md", "Specification Links\n- SPEC-OLD-001\n")
    old_timestamp = (datetime(2026, 6, 1, tzinfo=UTC) - timedelta(days=200)).isoformat()
    db = FakeDB([{"id": "SPEC-OLD-001", "status": "specified", "changed_at": old_timestamp}])

    result = run_audit(tmp_path, db=db, age_threshold_days=183, now=datetime(2026, 6, 1, tzinfo=UTC))

    assert result.specs_scanned == 0
    assert result.findings == ()


def test_write_audit_report_writes_markdown(tmp_path: Path) -> None:
    result = AuditResult(
        generated_at="2026-06-01T00:00:00+00:00",
        project_root=str(tmp_path),
        bridge_entries_scanned=1,
        specs_scanned=2,
        memory_files_scanned=3,
    )

    out_path = write_audit_report(result, tmp_path / "reports" / "audit.md")

    assert out_path == tmp_path / "reports" / "audit.md"
    assert "# MemBase Effective Use Audit" in out_path.read_text(encoding="utf-8")
