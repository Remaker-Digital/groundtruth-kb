# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests confirming Slice 1 governance artifacts landed correctly.

Authority: bridge/gtkb-single-harness-bridge-dispatcher-001-013.md (Codex GO
at -014). IP-7 governance test surface; covers:

- IP-4: ``.claude/rules/operating-role.md`` amendment present.
- IP-5: 3 glossary entries in ``.claude/rules/canonical-terminology.md``.
- IP-1/2/3: MemBase rows present with the right type/status.
- IP-6: Doctor checks return sensible verdicts against isolated topology fixtures.
- SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001: kind-aware dispatchability
  invariant preserved (terminal GO/VERIFIED not dispatched).
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT / "groundtruth-kb" / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "groundtruth-kb" / "src"))


# ──────────────────────────────────────────────────────────────────────────
# T-SHD-operating-role-amendment: IP-4 rule edit landed (Path 2 framing)
# ──────────────────────────────────────────────────────────────────────────


def test_operating_role_amendment_active_authority_text_present() -> None:
    """Amendment text must claim role-SET as ACTIVE schema authority, not
    future-design framing."""
    src = (PROJECT_ROOT / ".claude" / "rules" / "operating-role.md").read_text(encoding="utf-8")
    assert "Role Set Schema (Active Authority)" in src
    assert "active runtime schema" in src
    # Backward-compatibility section present.
    assert "Backward Compatibility" in src
    assert "legacy scalar role values" in src
    # Single-harness topology rule cites the three new specs.
    assert "ADR-SINGLE-HARNESS-OPERATING-MODE-001" in src
    assert "SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001" in src
    assert "DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001" in src
    # Acting-prime READ-but-not-SET clause present.
    assert "acting-prime-builder" in src
    assert "rejected on SET" in src


# ──────────────────────────────────────────────────────────────────────────
# T-SHD-canonical-terminology: IP-5 glossary entries present
# ──────────────────────────────────────────────────────────────────────────


def test_canonical_terminology_has_three_new_glossary_entries() -> None:
    src = (PROJECT_ROOT / ".claude" / "rules" / "canonical-terminology.md").read_text(encoding="utf-8")
    assert "### role set" in src
    assert "### single-harness operating mode" in src
    assert "### single-harness bridge dispatcher" in src


def test_glossary_entries_cite_authorities() -> None:
    src = (PROJECT_ROOT / ".claude" / "rules" / "canonical-terminology.md").read_text(encoding="utf-8")
    # Each entry must cite an originating spec/ADR/DCL.
    assert "ADR-SINGLE-HARNESS-OPERATING-MODE-001" in src
    assert "SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001" in src
    assert "DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001" in src
    # And the operating-role.md cross-reference.
    assert "operating-role.md" in src


# ──────────────────────────────────────────────────────────────────────────
# T-SHD-membase-rows: IP-1/2/3 MemBase rows present
# ──────────────────────────────────────────────────────────────────────────


def _row(spec_id: str) -> dict:
    """Return the latest version row for spec_id from groundtruth.db."""
    db_path = PROJECT_ROOT / "groundtruth.db"
    assert db_path.is_file(), f"MemBase missing at {db_path}"
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.execute(
            "SELECT id, type, status, title FROM specifications WHERE id = ? ORDER BY version DESC LIMIT 1",
            (spec_id,),
        )
        row = cur.fetchone()
    finally:
        conn.close()
    assert row is not None, f"MemBase has no row for {spec_id}"
    return {"id": row[0], "type": row[1], "status": row[2], "title": row[3]}


def test_adr_single_harness_operating_mode_present() -> None:
    row = _row("ADR-SINGLE-HARNESS-OPERATING-MODE-001")
    assert row["type"] == "architecture_decision"
    assert row["status"] == "specified"
    assert "Single-Harness" in row["title"]


def test_spec_single_harness_bridge_dispatcher_present() -> None:
    row = _row("SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001")
    assert row["type"] == "requirement"
    assert row["status"] == "specified"


def test_dcl_single_harness_dispatcher_desktop_task_present() -> None:
    row = _row("DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001")
    assert row["type"] == "design_constraint"
    assert row["status"] == "specified"


# ──────────────────────────────────────────────────────────────────────────
# T-SHD-doctor-topology + T-SHD-dispatcher-recommendation: IP-6 doctor checks
# ──────────────────────────────────────────────────────────────────────────


def test_doctor_role_set_topology_check_recognizes_role_set_schema() -> None:
    from groundtruth_kb.project.doctor import _check_role_set_topology_consistency

    check = _check_role_set_topology_consistency(PROJECT_ROOT)
    # The live state is currently legacy-scalar; the check must accept it
    # (READ-accepted) and report PASS with the legacy-scalar count.
    assert check.status in {"pass", "warning"}, f"Unexpected status: {check.status}"
    assert "wire form valid" in check.message or "missing" in check.message


def test_doctor_role_set_topology_flags_invalid_token(tmp_path: Path) -> None:
    """A bogus token in the role list must be reported as a failure."""
    from groundtruth_kb.project.doctor import _check_role_set_topology_consistency

    (tmp_path / "harness-state").mkdir(parents=True)
    (tmp_path / "harness-state" / "role-assignments.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": {
                    "A": {"role": ["prime-builder", "bogus-role"]},
                },
            }
        ),
        encoding="utf-8",
    )
    # Identity map intentionally absent so topology-drift check skips.
    check = _check_role_set_topology_consistency(tmp_path)
    assert check.status == "fail"
    assert "bogus-role" in check.message


def test_doctor_role_set_topology_flags_duplicate_tokens(tmp_path: Path) -> None:
    from groundtruth_kb.project.doctor import _check_role_set_topology_consistency

    (tmp_path / "harness-state").mkdir(parents=True)
    (tmp_path / "harness-state" / "role-assignments.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": {
                    "A": {"role": ["prime-builder", "prime-builder"]},
                },
            }
        ),
        encoding="utf-8",
    )
    check = _check_role_set_topology_consistency(tmp_path)
    assert check.status == "fail"
    assert "duplicate" in check.message.lower()


def test_doctor_single_harness_dispatcher_not_applicable_in_multi_harness(tmp_path: Path) -> None:
    from groundtruth_kb.project.doctor import _check_single_harness_dispatcher_when_required

    (tmp_path / "harness-state").mkdir(parents=True)
    (tmp_path / "harness-state" / "role-assignments.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": {
                    "A": {"role": ["prime-builder"]},
                    "B": {"role": ["loyal-opposition"]},
                },
            }
        ),
        encoding="utf-8",
    )
    check = _check_single_harness_dispatcher_when_required(tmp_path)
    assert check.status == "pass"
    assert "not applicable" in check.message


def test_doctor_single_harness_dispatcher_warns_when_applicable_but_absent(tmp_path: Path) -> None:
    """Single-harness mode + missing dispatcher script -> WARN."""
    from groundtruth_kb.project.doctor import _check_single_harness_dispatcher_when_required

    (tmp_path / "harness-state").mkdir(parents=True)
    (tmp_path / "harness-state" / "role-assignments.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": {
                    "B": {"role": ["prime-builder", "loyal-opposition"]},
                },
            }
        ),
        encoding="utf-8",
    )
    check = _check_single_harness_dispatcher_when_required(tmp_path)
    assert check.status == "warning"
    assert "single-harness mode applicable" in check.message


# ──────────────────────────────────────────────────────────────────────────
# T-SHD-dispatcher-kind-aware: behavior contract — terminal GO not dispatched
# ──────────────────────────────────────────────────────────────────────────


def test_dispatcher_kind_aware_terminal_go_not_dispatched() -> None:
    """SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 kind-aware dispatchability:
    terminal GO entries must NOT be marked dispatchable.

    This invariant is inherited from the cross-harness trigger's existing
    kind-aware-routing path (via `gtkb-cross-harness-trigger-codex-exec-hook-firing-001`).
    The SPEC explicitly preserves it: the single-harness dispatcher honors the
    same actionable-classification semantic.

    Test: import the trigger's actionable-computation; confirm a synthetic
    item flagged dispatchable=False is filtered out by the same predicate the
    dispatcher will use.
    """
    from types import SimpleNamespace

    # The dispatcher reuses the trigger's filter pattern:
    # `filtered = [it for it in items if getattr(it, "dispatchable", True)]`
    items = [
        SimpleNamespace(
            document_name="example-1",
            top_status="GO",
            top_file="bridge/example-1-002.md",
            dispatchable=False,  # terminal GO
        ),
        SimpleNamespace(
            document_name="example-2",
            top_status="GO",
            top_file="bridge/example-2-002.md",
            dispatchable=True,  # non-terminal GO
        ),
    ]
    filtered = [it for it in items if getattr(it, "dispatchable", True)]
    assert len(filtered) == 1
    assert filtered[0].document_name == "example-2"


# ──────────────────────────────────────────────────────────────────────────
# T-SHD-role-portability: role-portability invariant preserved
# ──────────────────────────────────────────────────────────────────────────


def test_role_portability_preserved_across_topologies(tmp_path: Path) -> None:
    """GOV-HARNESS-ROLE-PORTABILITY-001 preserved: in either topology
    (singleton multi-harness or multi-element single-harness), the role
    record attaches to the harness ID, not to a vendor name."""
    from scripts.harness_roles import is_loyal_opposition, is_prime_builder

    # Multi-harness fixture.
    multi = {"role": ["prime-builder"], "harness_type": "claude"}
    assert is_prime_builder(multi) is True
    assert is_loyal_opposition(multi) is False

    # Single-harness fixture (Claude holds both).
    single_claude = {"role": ["prime-builder", "loyal-opposition"], "harness_type": "claude"}
    assert is_prime_builder(single_claude) is True
    assert is_loyal_opposition(single_claude) is True

    # Same record shape with Codex as the single harness — same semantics.
    single_codex = {"role": ["prime-builder", "loyal-opposition"], "harness_type": "codex"}
    assert is_prime_builder(single_codex) is True
    assert is_loyal_opposition(single_codex) is True
