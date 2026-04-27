"""Tests for Wave 2 Slice 6 _release_readiness_split.py.

Per ``bridge/gtkb-isolation-016-phase8-wave2-slice6-003.md`` (REVISED-1)
and ``-004`` (Codex GO with 6 implementation conditions).

All tests use ``release_readiness_path=`` and ``kb=`` parameter
overrides per Slice 5 ``-002`` non-blocking note 4 fixture-root
pattern. No monkeypatching of module constants; no live-root walks.

Critical regression guards required by Codex:
- F1 (``-002``): release-gate surfaces classify as adopter, NOT framework
- F2 (``-002``): GTKB-* + Agent Red content → unclassified, NOT adopter
- ``-002`` non-blocking: list_deliberations called, search_deliberations NOT called
- ``-004`` condition 3: DOC-release-readiness-recovery test minimum
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from rehearse import _release_readiness_split  # noqa: E402


def _build_manifest(legacy_root: Path) -> dict[str, Any]:
    return {
        "target_root": str((legacy_root / "applications" / "Agent_Red").as_posix()),
        "legacy_root": str(legacy_root.as_posix()),
        "applications_namespace": str((legacy_root / "applications").as_posix()),
        "output_dir": "C:/temp/agent-red-rehearsal",
        "git_strategy": "clone_with_history_filter",
        "excluded_paths": [],
    }


class _FakeKB:
    """Duck-typed KB for tests. Tracks which methods get called."""

    def __init__(
        self,
        documents: list[dict[str, Any]] | None = None,
        specs: list[dict[str, Any]] | None = None,
        work_items: list[dict[str, Any]] | None = None,
        deliberations: list[dict[str, Any]] | None = None,
    ) -> None:
        self._documents = documents or []
        self._specs = specs or []
        self._work_items = work_items or []
        self._deliberations = deliberations or []
        self.list_documents_called = False
        self.list_specs_called = False
        self.list_work_items_called = False
        self.list_deliberations_called = False
        self.search_deliberations_called = False

    def list_documents(self, **kwargs: Any) -> list[dict[str, Any]]:
        self.list_documents_called = True
        return list(self._documents)

    def list_specs(self, **kwargs: Any) -> list[dict[str, Any]]:
        self.list_specs_called = True
        return list(self._specs)

    def list_work_items(self, **kwargs: Any) -> list[dict[str, Any]]:
        self.list_work_items_called = True
        return list(self._work_items)

    def list_deliberations(self, **kwargs: Any) -> list[dict[str, Any]]:
        self.list_deliberations_called = True
        return list(self._deliberations)

    def search_deliberations(self, *args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        # Tracking only — should NOT be called by the lane.
        self.search_deliberations_called = True
        return []


def _write_ledger(path: Path) -> None:
    """Minimal release-readiness.md fixture with a couple of H2 sections."""
    path.write_text(
        "# Release Readiness Recovery\n\n"
        "Last updated: 2026-04-21\n\n"
        "## Current State\n\n"
        "Some content describing current state of the Agent Red release.\n\n"
        "## Completed Recovery Work\n\n"
        "Bullet list of completed items.\n\n"
        "## Remaining Release Blockers\n\n"
        "More content.\n",
        encoding="utf-8",
    )


# ---------- T1: dry-run ----------


def test_run_dry_run_returns_skipped(tmp_path: Path) -> None:
    manifest = _build_manifest(tmp_path)
    result = _release_readiness_split.run(
        manifest,
        tmp_path / "out",
        dry_run=True,
        release_readiness_path=tmp_path / "ledger.md",
        kb=_FakeKB(),
    )
    assert result["status"] == "skipped"
    assert result["output_files"] == []


# ---------- T2-T4: ledger classification ----------


def test_run_classifies_release_readiness_md_as_adopter(tmp_path: Path) -> None:
    """Ledger → adopter with explicit_adopter_ledger signal."""
    ledger = tmp_path / "ledger.md"
    _write_ledger(ledger)
    manifest = _build_manifest(tmp_path)
    _release_readiness_split.run(
        manifest,
        tmp_path / "out",
        dry_run=False,
        release_readiness_path=ledger,
        kb=_FakeKB(),
    )
    artifact = json.loads(
        (tmp_path / "out" / "release_readiness_split" / "release_readiness_split.json").read_text(encoding="utf-8")
    )
    rec = artifact["memory_release_readiness_md"]
    assert rec["classification"] == "adopter"
    assert rec["classification_signal"] == "explicit_adopter_ledger"
    assert rec["exists"] is True


def test_run_extracts_section_headers_not_full_content(tmp_path: Path) -> None:
    """Section headers populated; full content NOT embedded."""
    ledger = tmp_path / "ledger.md"
    _write_ledger(ledger)
    manifest = _build_manifest(tmp_path)
    _release_readiness_split.run(
        manifest,
        tmp_path / "out",
        dry_run=False,
        release_readiness_path=ledger,
        kb=_FakeKB(),
    )
    artifact = json.loads(
        (tmp_path / "out" / "release_readiness_split" / "release_readiness_split.json").read_text(encoding="utf-8")
    )
    rec = artifact["memory_release_readiness_md"]
    assert rec["section_headers"] == [
        "Current State",
        "Completed Recovery Work",
        "Remaining Release Blockers",
    ]
    # Full content not present in record
    assert "content" not in rec
    assert "Some content describing" not in json.dumps(rec)


def test_run_warns_when_release_readiness_md_missing(tmp_path: Path) -> None:
    """Missing ledger → warning, not error."""
    manifest = _build_manifest(tmp_path)
    result = _release_readiness_split.run(
        manifest,
        tmp_path / "out",
        dry_run=False,
        release_readiness_path=tmp_path / "missing.md",
        kb=_FakeKB(),
    )
    assert result["status"] == "ok"
    assert any("release_readiness_md_missing" in w for w in result["warnings"])


# ---------- T5: DOC classification (Codex -004 condition 3) ----------


def test_run_classifies_doc_release_readiness_recovery_as_adopter(
    tmp_path: Path,
) -> None:
    """Per Codex -004 condition 3 minimum: DOC-release-readiness-recovery → adopter
    via known_adopter ID allowlist (NOT via the GTKB-/AR- prefix helper)."""
    ledger = tmp_path / "ledger.md"
    _write_ledger(ledger)
    manifest = _build_manifest(tmp_path)
    fake_kb = _FakeKB(
        documents=[
            {
                "id": "DOC-release-readiness-recovery",
                "title": "Agent Red Release Readiness Recovery",
                "category": "release",
                "status": "active",
            }
        ]
    )
    _release_readiness_split.run(
        manifest,
        tmp_path / "out",
        dry_run=False,
        release_readiness_path=ledger,
        kb=fake_kb,
    )
    artifact = json.loads(
        (tmp_path / "out" / "release_readiness_split" / "release_readiness_split.json").read_text(encoding="utf-8")
    )
    docs = artifact["documents"]
    assert len(docs) == 1
    assert docs[0]["id"] == "DOC-release-readiness-recovery"
    assert docs[0]["classification"] == "adopter"
    assert docs[0]["classification_signal"] == "doc_id_known_adopter"


def test_run_doc_release_management_generic_classifies_as_framework(
    tmp_path: Path,
) -> None:
    """doc-release-management without Agent Red mention → framework."""
    ledger = tmp_path / "ledger.md"
    _write_ledger(ledger)
    manifest = _build_manifest(tmp_path)
    fake_kb = _FakeKB(
        documents=[
            {
                "id": "doc-release-management",
                "title": "Release Management",
                "content": "Generic release management procedures.",
            }
        ]
    )
    _release_readiness_split.run(
        manifest,
        tmp_path / "out",
        dry_run=False,
        release_readiness_path=ledger,
        kb=fake_kb,
    )
    artifact = json.loads(
        (tmp_path / "out" / "release_readiness_split" / "release_readiness_split.json").read_text(encoding="utf-8")
    )
    docs = artifact["documents"]
    assert docs[0]["classification"] == "framework"
    assert docs[0]["classification_signal"] == "doc_release_management_generic"


# ---------- T6: list_deliberations vs search_deliberations (Codex -002 guard) ----------


def test_run_uses_list_deliberations_not_search_deliberations(tmp_path: Path) -> None:
    """Codex Slice 5 -002 explicit prescription: lane MUST use uncapped
    list_deliberations(), NOT capped search_deliberations()."""
    ledger = tmp_path / "ledger.md"
    _write_ledger(ledger)
    manifest = _build_manifest(tmp_path)
    fake_kb = _FakeKB()
    _release_readiness_split.run(
        manifest,
        tmp_path / "out",
        dry_run=False,
        release_readiness_path=ledger,
        kb=fake_kb,
    )
    assert fake_kb.list_deliberations_called is True
    assert fake_kb.search_deliberations_called is False, (
        "Codex -002: search_deliberations is capped; lane must NOT use it"
    )


# ---------- T7-T8: release-gate surfaces (F1 regression guards) ----------


def test_release_gate_surfaces_classified_as_adopter_not_framework(
    tmp_path: Path,
) -> None:
    """F1 regression guard: release-gate surfaces classify as adopter
    (per isolation inventory: application release gates, not GT-KB
    product gates), NOT framework as the original Slice 6 -001 proposed.
    """
    ledger = tmp_path / "ledger.md"
    _write_ledger(ledger)
    manifest = _build_manifest(tmp_path)
    _release_readiness_split.run(
        manifest,
        tmp_path / "out",
        dry_run=False,
        release_readiness_path=ledger,
        kb=_FakeKB(),
    )
    artifact = json.loads(
        (tmp_path / "out" / "release_readiness_split" / "release_readiness_split.json").read_text(encoding="utf-8")
    )
    surfaces = artifact["release_gate_surfaces"]
    assert len(surfaces) == 3
    for surface in surfaces:
        assert surface["classification"] == "adopter", (
            f"F1 regression: {surface['path']} classified as "
            f"{surface['classification']!r} — must be 'adopter' per isolation inventory"
        )
        assert surface["classification_signal"] == "application_release_gate_surface"


def test_release_gate_surfaces_include_mechanism_origin(tmp_path: Path) -> None:
    """Per Codex -004 condition 1: mechanism_origin separates ownership
    from provenance."""
    ledger = tmp_path / "ledger.md"
    _write_ledger(ledger)
    manifest = _build_manifest(tmp_path)
    _release_readiness_split.run(
        manifest,
        tmp_path / "out",
        dry_run=False,
        release_readiness_path=ledger,
        kb=_FakeKB(),
    )
    artifact = json.loads(
        (tmp_path / "out" / "release_readiness_split" / "release_readiness_split.json").read_text(encoding="utf-8")
    )
    surfaces = artifact["release_gate_surfaces"]
    for surface in surfaces:
        assert "mechanism_origin" in surface
        assert surface["mechanism_origin"] == "agent_red_local"


# ---------- T9-T11: spec / WI classification (F2 regression guard) ----------


def test_run_gtkb_spec_with_agent_red_content_routes_to_unclassified(
    tmp_path: Path,
) -> None:
    """F2 regression: GTKB-* spec mentioning Agent Red → unclassified,
    NOT silently adopter. Per Codex -002 F2 + Slice 5 -004 F1 lesson."""
    ledger = tmp_path / "ledger.md"
    _write_ledger(ledger)
    manifest = _build_manifest(tmp_path)
    fake_kb = _FakeKB(
        specs=[
            {
                "id": "GTKB-MIXED-001",
                "summary": "Generic spec",
                "content": "References Agent Red migration tooling.",
            }
        ]
    )
    _release_readiness_split.run(
        manifest,
        tmp_path / "out",
        dry_run=False,
        release_readiness_path=ledger,
        kb=fake_kb,
    )
    artifact = json.loads(
        (tmp_path / "out" / "release_readiness_split" / "release_readiness_split.json").read_text(encoding="utf-8")
    )
    framework_ids = [s["id"] for s in artifact["framework_specs"]]
    adopter_ids = [s["id"] for s in artifact["adopter_specs"]]
    unclassified_ids = [s["id"] for s in artifact["unclassified_specs"]]
    assert "GTKB-MIXED-001" not in framework_ids
    assert "GTKB-MIXED-001" not in adopter_ids
    assert "GTKB-MIXED-001" in unclassified_ids
    entry = next(s for s in artifact["unclassified_specs"] if s["id"] == "GTKB-MIXED-001")
    assert entry["classification_signal"] == "gtkb_prefix_with_adopter_content"


def test_run_clean_gtkb_spec_classifies_as_framework(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.md"
    _write_ledger(ledger)
    manifest = _build_manifest(tmp_path)
    fake_kb = _FakeKB(
        specs=[
            {
                "id": "GTKB-FRAMEWORK-001",
                "summary": "Generic framework spec",
                "content": "Pure framework concern, no adopter mention.",
            }
        ]
    )
    _release_readiness_split.run(
        manifest,
        tmp_path / "out",
        dry_run=False,
        release_readiness_path=ledger,
        kb=fake_kb,
    )
    artifact = json.loads(
        (tmp_path / "out" / "release_readiness_split" / "release_readiness_split.json").read_text(encoding="utf-8")
    )
    framework_ids = [s["id"] for s in artifact["framework_specs"]]
    assert "GTKB-FRAMEWORK-001" in framework_ids


def test_run_ar_prefix_work_item_classifies_as_adopter(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.md"
    _write_ledger(ledger)
    manifest = _build_manifest(tmp_path)
    fake_kb = _FakeKB(work_items=[{"id": "AR-WI-001", "title": "Adopter work item"}])
    _release_readiness_split.run(
        manifest,
        tmp_path / "out",
        dry_run=False,
        release_readiness_path=ledger,
        kb=fake_kb,
    )
    artifact = json.loads(
        (tmp_path / "out" / "release_readiness_split" / "release_readiness_split.json").read_text(encoding="utf-8")
    )
    adopter_ids = [w["id"] for w in artifact["adopter_work_items"]]
    assert "AR-WI-001" in adopter_ids


# ---------- T12-T14: artifact structure + result.json ----------


def test_run_writes_release_readiness_split_json(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.md"
    _write_ledger(ledger)
    manifest = _build_manifest(tmp_path)
    _release_readiness_split.run(
        manifest,
        tmp_path / "out",
        dry_run=False,
        release_readiness_path=ledger,
        kb=_FakeKB(),
    )
    artifact_path = tmp_path / "out" / "release_readiness_split" / "release_readiness_split.json"
    assert artifact_path.exists()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert "summary" in artifact
    assert "memory_release_readiness_md" in artifact
    assert "documents" in artifact
    assert "release_gate_surfaces" in artifact
    assert "framework_specs" in artifact
    assert "adopter_specs" in artifact
    assert "unclassified_specs" in artifact


def test_run_writes_result_json_on_ok_path(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.md"
    _write_ledger(ledger)
    manifest = _build_manifest(tmp_path)
    result = _release_readiness_split.run(
        manifest,
        tmp_path / "out",
        dry_run=False,
        release_readiness_path=ledger,
        kb=_FakeKB(),
    )
    result_path = tmp_path / "out" / "release_readiness_split" / "result.json"
    assert result_path.exists()
    on_disk = json.loads(result_path.read_text(encoding="utf-8"))
    assert on_disk == result
    assert str(result_path) in on_disk["output_files"]


def test_run_writes_result_json_on_error_path(tmp_path: Path) -> None:
    """KB query failure → status='error' + result.json still written."""

    class _FailingKB:
        def list_documents(self, **kwargs: Any) -> list[dict[str, Any]]:
            raise RuntimeError("kb_synthetic_failure")

        def list_specs(self, **kwargs: Any) -> list[dict[str, Any]]:
            return []

        def list_work_items(self, **kwargs: Any) -> list[dict[str, Any]]:
            return []

        def list_deliberations(self, **kwargs: Any) -> list[dict[str, Any]]:
            return []

    ledger = tmp_path / "ledger.md"
    _write_ledger(ledger)
    manifest = _build_manifest(tmp_path)
    result = _release_readiness_split.run(
        manifest,
        tmp_path / "out",
        dry_run=False,
        release_readiness_path=ledger,
        kb=_FailingKB(),
    )
    assert result["status"] == "error"
    result_path = tmp_path / "out" / "release_readiness_split" / "result.json"
    assert result_path.exists()


# ---------- T15: kb param testability ----------


def test_run_accepts_duck_typed_kb(tmp_path: Path) -> None:
    """kb=duck object with required methods works without real KnowledgeDB."""
    ledger = tmp_path / "ledger.md"
    _write_ledger(ledger)
    manifest = _build_manifest(tmp_path)
    fake_kb = _FakeKB()
    result = _release_readiness_split.run(
        manifest,
        tmp_path / "out",
        dry_run=False,
        release_readiness_path=ledger,
        kb=fake_kb,
    )
    assert result["status"] == "ok"
    assert fake_kb.list_documents_called
    assert fake_kb.list_specs_called
    assert fake_kb.list_work_items_called
    assert fake_kb.list_deliberations_called
