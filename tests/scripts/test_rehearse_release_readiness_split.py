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

from datetime import UTC

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
    """Duck-typed KB for tests. Tracks which methods get called.

    Supports the filter kwargs the lane actually uses (per Codex Slice
    6 ``-006`` F1 fix): ``list_specs(type=...)``,
    ``list_deliberations(outcome=...)``. Other filter kwargs are
    ignored (returns full list). Mirrors KnowledgeDB's filter
    semantics for the kwargs the lane uses.
    """

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
        self.list_specs_called_types: list[str | None] = []
        self.list_work_items_called = False
        self.list_deliberations_called_outcomes: list[str | None] = []
        self.search_deliberations_called = False

    def list_documents(self, **kwargs: Any) -> list[dict[str, Any]]:
        self.list_documents_called = True
        return list(self._documents)

    def list_specs(self, *, type: str | None = None, **kwargs: Any) -> list[dict[str, Any]]:
        self.list_specs_called_types.append(type)
        if type is None:
            return list(self._specs)
        return [s for s in self._specs if s.get("type") == type]

    def list_work_items(self, **kwargs: Any) -> list[dict[str, Any]]:
        self.list_work_items_called = True
        return list(self._work_items)

    def list_deliberations(self, *, outcome: str | None = None, **kwargs: Any) -> list[dict[str, Any]]:
        self.list_deliberations_called_outcomes.append(outcome)
        if outcome is None:
            return list(self._deliberations)
        return [d for d in self._deliberations if d.get("outcome") == outcome]

    @property
    def list_deliberations_called(self) -> bool:
        return len(self.list_deliberations_called_outcomes) > 0

    @property
    def list_specs_called(self) -> bool:
        return len(self.list_specs_called_types) > 0

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
                "type": "governance",
                "title": "Generic release-readiness governance spec",
                "description": "References Agent Red migration tooling for release.",
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
                "type": "governance",
                "title": "Generic framework release-readiness spec",
                "description": "Pure framework deployment concern, no adopter mention.",
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
    fake_kb = _FakeKB(
        work_items=[
            {
                "id": "AR-WI-001",
                "title": "Adopter release blocker work item",
                "resolution_status": "open",
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
    adopter_ids = [w["id"] for w in artifact["adopter_work_items"]]
    assert "AR-WI-001" in adopter_ids


# ---------- F2 fix: real KB ID-shape classification (Codex -006 F2) ----------


def test_run_gov_spec_with_agent_red_content_classifies_as_adopter(
    tmp_path: Path,
) -> None:
    """Real-shaped ID family: GOV-* spec with Agent Red content →
    adopter via artifact_content_agent_red signal."""
    ledger = tmp_path / "ledger.md"
    _write_ledger(ledger)
    manifest = _build_manifest(tmp_path)
    fake_kb = _FakeKB(
        specs=[
            {
                "id": "GOV-RELEASE-READINESS-GOVERNED-TESTING-001",
                "type": "governance",
                "title": "Agent Red release readiness governed testing",
                "description": "Production release blocker tracking for Agent Red.",
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
    adopter_ids = [s["id"] for s in artifact["adopter_specs"]]
    assert "GOV-RELEASE-READINESS-GOVERNED-TESTING-001" in adopter_ids
    entry = next(s for s in artifact["adopter_specs"] if s["id"] == "GOV-RELEASE-READINESS-GOVERNED-TESTING-001")
    assert entry["classification_signal"] == "artifact_content_agent_red"


def test_run_gov_spec_with_framework_content_classifies_as_framework(
    tmp_path: Path,
) -> None:
    """GOV-* spec with framework keyword → framework via artifact_content_framework."""
    ledger = tmp_path / "ledger.md"
    _write_ledger(ledger)
    manifest = _build_manifest(tmp_path)
    fake_kb = _FakeKB(
        specs=[
            {
                "id": "GOV-UPSTREAM-RELEASE-001",
                "type": "governance",
                "title": "Upstream release management",
                "description": "groundtruth-kb upstream package release deployment.",
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
    assert "GOV-UPSTREAM-RELEASE-001" in framework_ids


def test_run_pb_spec_with_mixed_content_classifies_as_unclassified(
    tmp_path: Path,
) -> None:
    """Real-ID + both adopter AND framework content → unclassified
    with mixed_content_signals."""
    ledger = tmp_path / "ledger.md"
    _write_ledger(ledger)
    manifest = _build_manifest(tmp_path)
    fake_kb = _FakeKB(
        specs=[
            {
                "id": "PB-MIXED-RELEASE-001",
                "type": "protected_behavior",
                "title": "Release readiness protected behavior",
                "description": "Agent Red release with groundtruth-kb upstream coordination.",
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
    unclassified_ids = [s["id"] for s in artifact["unclassified_specs"]]
    assert "PB-MIXED-RELEASE-001" in unclassified_ids
    entry = next(s for s in artifact["unclassified_specs"] if s["id"] == "PB-MIXED-RELEASE-001")
    assert entry["classification_signal"] == "mixed_content_signals"


def test_run_delib_owner_decision_with_agent_red_content_classifies_as_adopter(
    tmp_path: Path,
) -> None:
    """DELIB-* + outcome=owner_decision + Agent Red content → adopter."""
    ledger = tmp_path / "ledger.md"
    _write_ledger(ledger)
    manifest = _build_manifest(tmp_path)
    fake_kb = _FakeKB(
        deliberations=[
            {
                "id": "DELIB-0834",
                "outcome": "owner_decision",
                "title": "Agent Red release decision",
                "summary": "Release deployment to staging for Agent Red.",
                "content": "Decision content here.",
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
    adopter_ids = [d["id"] for d in artifact["adopter_deliberations"]]
    assert "DELIB-0834" in adopter_ids


# ---------- F1 fix: source filters (Codex -006 F1) ----------


def test_run_filters_out_non_release_relevant_specs(tmp_path: Path) -> None:
    """Specs without release-readiness keyword are filtered out."""
    ledger = tmp_path / "ledger.md"
    _write_ledger(ledger)
    manifest = _build_manifest(tmp_path)
    fake_kb = _FakeKB(
        specs=[
            {
                "id": "GOV-UNRELATED-FOO-001",
                "type": "governance",
                "title": "Some unrelated governance spec",
                "description": "Has nothing to do with that subject.",
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
    all_spec_ids = (
        [s["id"] for s in artifact["framework_specs"]]
        + [s["id"] for s in artifact["adopter_specs"]]
        + [s["id"] for s in artifact["unclassified_specs"]]
    )
    assert "GOV-UNRELATED-FOO-001" not in all_spec_ids, "F1 regression: non-release-relevant spec leaked through filter"


def test_run_includes_recently_closed_work_items(tmp_path: Path) -> None:
    """Per Codex Slice 6 ``-008`` NO-GO: 'open + recently closed' contract.

    A resolved WI with ``changed_at`` within
    ``_RECENT_CLOSURE_WINDOW_DAYS`` MUST be included as recent context
    for release-readiness inventory.
    """
    from datetime import datetime, timedelta

    ledger = tmp_path / "ledger.md"
    _write_ledger(ledger)
    manifest = _build_manifest(tmp_path)
    recent_iso = (datetime.now(tz=UTC) - timedelta(days=30)).isoformat()
    fake_kb = _FakeKB(
        work_items=[
            {
                "id": "WI-3168",
                "title": "Recently resolved Agent Red release blocker",
                "description": "Release deployment work, recently resolved.",
                "resolution_status": "resolved",
                "changed_at": recent_iso,
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
    all_wi_ids = (
        [w["id"] for w in artifact["framework_work_items"]]
        + [w["id"] for w in artifact["adopter_work_items"]]
        + [w["id"] for w in artifact["unclassified_work_items"]]
    )
    assert "WI-3168" in all_wi_ids, "Slice 6 -008 contract: recently-closed WI must be included as context"


def test_run_filters_out_old_resolved_work_items(tmp_path: Path) -> None:
    """Resolved WIs with ``changed_at`` outside the recency window are
    excluded (they're historical, not 'recently closed')."""
    from datetime import datetime, timedelta

    ledger = tmp_path / "ledger.md"
    _write_ledger(ledger)
    manifest = _build_manifest(tmp_path)
    old_iso = (datetime.now(tz=UTC) - timedelta(days=200)).isoformat()
    fake_kb = _FakeKB(
        work_items=[
            {
                "id": "WI-OLD-001",
                "title": "Old resolved Agent Red release blocker",
                "description": "Release deployment work, resolved long ago.",
                "resolution_status": "resolved",
                "changed_at": old_iso,
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
    all_wi_ids = (
        [w["id"] for w in artifact["framework_work_items"]]
        + [w["id"] for w in artifact["adopter_work_items"]]
        + [w["id"] for w in artifact["unclassified_work_items"]]
    )
    assert "WI-OLD-001" not in all_wi_ids, "Slice 6 -008: old resolved WIs (outside recency window) must be excluded"


def test_run_excludes_resolved_wi_with_malformed_changed_at(tmp_path: Path) -> None:
    """Defensive: resolved WIs with malformed/missing changed_at are
    excluded (conservative — don't flood split with undated records)."""
    ledger = tmp_path / "ledger.md"
    _write_ledger(ledger)
    manifest = _build_manifest(tmp_path)
    fake_kb = _FakeKB(
        work_items=[
            {
                "id": "WI-NODATE-001",
                "title": "Resolved Agent Red release WI with no timestamp",
                "description": "Release deployment work without changed_at.",
                "resolution_status": "resolved",
                # changed_at intentionally missing
            },
            {
                "id": "WI-BADDATE-001",
                "title": "Resolved Agent Red release WI with bad timestamp",
                "description": "Release deployment work with invalid date.",
                "resolution_status": "resolved",
                "changed_at": "not-a-real-date",
            },
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
    all_wi_ids = (
        [w["id"] for w in artifact["framework_work_items"]]
        + [w["id"] for w in artifact["adopter_work_items"]]
        + [w["id"] for w in artifact["unclassified_work_items"]]
    )
    assert "WI-NODATE-001" not in all_wi_ids
    assert "WI-BADDATE-001" not in all_wi_ids


def test_is_recently_changed_helper_handles_iso_with_z_suffix() -> None:
    """Helper accepts ISO-8601 with Z (Zulu) suffix as well as +00:00."""
    from datetime import datetime

    now = datetime(2026, 4, 27, tzinfo=UTC)
    recent_z = "2026-03-28T12:00:00Z"  # ~30 days before now
    old_z = "2025-09-01T12:00:00Z"  # >200 days before now
    assert _release_readiness_split._is_recently_changed(recent_z, now=now) is True
    assert _release_readiness_split._is_recently_changed(old_z, now=now) is False
    assert _release_readiness_split._is_recently_changed(None, now=now) is False
    assert _release_readiness_split._is_recently_changed("", now=now) is False
    assert _release_readiness_split._is_recently_changed("garbage", now=now) is False


def test_run_filters_specs_by_type(tmp_path: Path) -> None:
    """Only relevant spec types queried; irrelevant types filtered at DB layer."""
    ledger = tmp_path / "ledger.md"
    _write_ledger(ledger)
    manifest = _build_manifest(tmp_path)
    fake_kb = _FakeKB(
        specs=[
            {
                "id": "SPEC-RELEASE-NOTE-001",
                "type": "release_note",  # NOT in _RELEVANT_SPEC_TYPES
                "title": "Release note for v1.0",
                "description": "Some release note content.",
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
    queried_types = [t for t in fake_kb.list_specs_called_types if t is not None]
    assert "release_note" not in queried_types
    assert "governance" in queried_types
    artifact = json.loads(
        (tmp_path / "out" / "release_readiness_split" / "release_readiness_split.json").read_text(encoding="utf-8")
    )
    all_spec_ids = (
        [s["id"] for s in artifact["framework_specs"]]
        + [s["id"] for s in artifact["adopter_specs"]]
        + [s["id"] for s in artifact["unclassified_specs"]]
    )
    assert "SPEC-RELEASE-NOTE-001" not in all_spec_ids


def test_run_includes_owner_decision_deliberations_without_release_keyword(
    tmp_path: Path,
) -> None:
    """list_deliberations(outcome='owner_decision') always included
    (owner decisions are policy-bearing regardless of subject)."""
    ledger = tmp_path / "ledger.md"
    _write_ledger(ledger)
    manifest = _build_manifest(tmp_path)
    fake_kb = _FakeKB(
        deliberations=[
            {
                "id": "DELIB-0900",
                "outcome": "owner_decision",
                "title": "Owner decision on something unrelated",
                "summary": "Generic content.",
                "content": "More content.",
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
    all_delib_ids = (
        [d["id"] for d in artifact["framework_deliberations"]]
        + [d["id"] for d in artifact["adopter_deliberations"]]
        + [d["id"] for d in artifact["unclassified_deliberations"]]
    )
    assert "DELIB-0900" in all_delib_ids


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
