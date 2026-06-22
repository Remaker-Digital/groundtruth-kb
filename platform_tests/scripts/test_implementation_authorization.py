"""Tests for scripts/implementation_authorization.py (Slice 4 IP-1/IP-2/IP-4).

Per ``bridge/gtkb-self-diagnostic-leak-closure-slice-4-implementation-gate-hygiene-003.md``
(Codex GO at -004). Covers:

- IP-1: versioned bridge-file resolver hardening for implementation authorization.
- IP-2: named-packet cache at ``by-bridge/<bridge-id>.json``, ``activate`` and
  ``list`` subcommands, plus unique named-packet fallback when ``current.json``
  points at the wrong bridge.

Uses isolated tmp_path project roots; the only dependency on the live repo is
the script import path.
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "implementation_authorization.py"


@pytest.fixture(scope="module")
def auth_module():
    """Load implementation_authorization.py as a module without executing main().

    Registers in sys.modules before exec_module so the @dataclass(frozen=True)
    decorator can resolve cls.__module__ on Python 3.12+.
    """
    spec = importlib.util.spec_from_file_location("implementation_authorization", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["implementation_authorization"] = module
    spec.loader.exec_module(module)
    return module


def _ignore_retired_index_fixture(project_root: Path, blocks: list[str]) -> Path:
    """Keep obsolete chain fixture arguments without writing retired index state."""
    del blocks
    bridge_dir = project_root / "bridge"
    bridge_dir.mkdir(parents=True, exist_ok=True)
    return bridge_dir / "retired-index-fixture-not-written.md"


def _write_proposal(
    project_root: Path,
    slug: str,
    version: int = 1,
    *,
    status: str = "NEW",
    target_paths: list[str] | None = None,
    verification_heading: str = "Verification Plan",
    verification_body: str = "Fixture verification plan: derived from the linked specs above.",
) -> Path:
    """Write a minimal-compliant bridge proposal file."""
    if target_paths is None:
        target_paths = ["scripts/dummy.py"]
    suffix = "" if version == 1 else f"-{version:03d}"
    proposal_path = project_root / "bridge" / f"{slug}{suffix}.md"
    proposal_path.parent.mkdir(parents=True, exist_ok=True)
    target_paths_json = json.dumps(target_paths)
    body = (
        f"{status}\n\n"
        f"# Fixture proposal {slug} v{version}\n\n"
        f"target_paths: {target_paths_json}\n\n"
        f"## Specification Links\n\n"
        f"- GOV-FILE-BRIDGE-AUTHORITY-001 — bridge protocol.\n"
        f"- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — spec linkage.\n\n"
        f"## Requirement Sufficiency\n\n"
        f"Existing requirements sufficient.\n\n"
        f"## {verification_heading}\n\n"
        f"{verification_body}\n"
    )
    proposal_path.write_text(body, encoding="utf-8")
    return proposal_path


def _write_verdict(project_root: Path, slug: str, version: int, verdict: str = "GO") -> Path:
    """Write a verdict (GO/NO-GO/VERIFIED) file."""
    suffix = "" if version == 1 else f"-{version:03d}"
    path = project_root / "bridge" / f"{slug}{suffix}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{verdict}\n\nFixture {verdict} verdict for {slug} v{version}.\n", encoding="utf-8")
    return path


def _setup_simple_go_bridge(project_root: Path, slug: str = "fixture-bridge") -> tuple[str, Path, Path]:
    """Build a project root with a single GO'd bridge: NEW at -001, GO at -002."""
    proposal = _write_proposal(project_root, slug, version=1, target_paths=["scripts/dummy.py", ".gtkb-state/**"])
    verdict = _write_verdict(project_root, slug, version=2, verdict="GO")
    block = f"Document: {slug}\nGO: bridge/{slug}-002.md\nNEW: bridge/{slug}.md\n"
    _ignore_retired_index_fixture(project_root, [block])
    return slug, proposal, verdict


# ---------------------------------------------------------------------------
# IP-1: versioned bridge-file resolver hardening
# ---------------------------------------------------------------------------


def test_bridge_entry_uses_versioned_files_when_index_is_absent(auth_module, tmp_path):
    """bridge_entry reconstructs newest-first state from bridge/<slug>-NNN.md files."""
    slug, _, _ = _setup_simple_go_bridge(tmp_path, slug="real-bridge")

    entry = auth_module.bridge_entry(tmp_path, slug)

    assert entry.bridge_id == slug
    assert entry.versions == [
        ("GO", "bridge/real-bridge-002.md"),
        ("NEW", "bridge/real-bridge.md"),
    ]


def test_bridge_entry_raises_for_duplicate_version_files(auth_module, tmp_path):
    """bridge_entry fails closed when both v1 naming forms exist for one thread."""
    _write_proposal(tmp_path, "doc-a", version=1, target_paths=["scripts/foo.py"])
    duplicate = tmp_path / "bridge" / "doc-a-001.md"
    duplicate.write_text("NEW\n\nDuplicate v1 fixture.\n", encoding="utf-8")

    with pytest.raises(auth_module.AuthorizationError, match="Duplicate bridge version 001"):
        auth_module.bridge_entry(tmp_path, "doc-a")


def test_bridge_version_from_rel_path_accepts_v1_no_suffix_and_v2_plus_suffix(auth_module):
    """The resolver accepts both v1 (no suffix) and v2+ (-NNN.md) forms."""
    version = auth_module._bridge_version_from_rel_path
    assert version("bridge/foo.md", "foo") == 1
    assert version("bridge/foo-022.md", "foo") == 22
    assert (
        version("bridge/gtkb-single-harness-bridge-dispatcher-001.md", "gtkb-single-harness-bridge-dispatcher-001") == 1
    )
    assert (
        version(
            "bridge/gtkb-single-harness-bridge-dispatcher-001-022.md",
            "gtkb-single-harness-bridge-dispatcher-001",
        )
        == 22
    )
    assert version("bridge/bar-001.md", "foo") is None
    assert version("bridge/foo-abc.md", "foo") is None


def test_bridge_entry_succeeds_for_well_formed_bridge(auth_module, tmp_path):
    """Baseline: bridge_entry returns the entry when all status lines match."""
    slug, _, _ = _setup_simple_go_bridge(tmp_path)
    entry = auth_module.bridge_entry(tmp_path, slug)
    assert entry.bridge_id == slug
    assert entry.latest_status == "GO"


def test_bridge_entry_records_deferred_status(auth_module, tmp_path):
    """DEFERRED is a versioned lifecycle status, not a line to skip."""
    slug = "deferred-bridge"
    _write_proposal(tmp_path, slug, version=1, target_paths=["scripts/foo.py"])
    _write_verdict(tmp_path, slug, version=2, verdict="GO")
    _write_verdict(tmp_path, slug, version=3, verdict="DEFERRED")
    _ignore_retired_index_fixture(
        tmp_path,
        [f"Document: {slug}\nDEFERRED: bridge/{slug}-003.md\nGO: bridge/{slug}-002.md\nNEW: bridge/{slug}.md\n"],
    )

    entry = auth_module.bridge_entry(tmp_path, slug)

    assert entry.latest_status == "DEFERRED"
    assert entry.versions[0] == ("DEFERRED", f"bridge/{slug}-003.md")


def test_bridge_entry_raises_for_malformed_deferred_file(auth_module, tmp_path):
    """Per-file status validation applies to DEFERRED chains too."""
    slug = "deferred-bridge"
    _write_proposal(tmp_path, slug, version=1, target_paths=["scripts/foo.py"])
    _write_verdict(tmp_path, slug, version=2, verdict="GO")
    bad = tmp_path / "bridge" / f"{slug}-003.md"
    bad.write_text("# Missing status token\n", encoding="utf-8")

    with pytest.raises(auth_module.AuthorizationError, match="unrecognized status line"):
        auth_module.bridge_entry(tmp_path, slug)


def test_create_packet_fails_when_latest_status_is_deferred(auth_module, tmp_path):
    """Latest DEFERRED above older GO is parked state, not implementation authority."""
    slug = "deferred-bridge"
    _write_proposal(tmp_path, slug, version=1, target_paths=["scripts/foo.py"])
    _write_verdict(tmp_path, slug, version=2, verdict="GO")
    _write_verdict(tmp_path, slug, version=3, verdict="DEFERRED")
    _ignore_retired_index_fixture(
        tmp_path,
        [f"Document: {slug}\nDEFERRED: bridge/{slug}-003.md\nGO: bridge/{slug}-002.md\nNEW: bridge/{slug}.md\n"],
    )

    with pytest.raises(auth_module.AuthorizationError, match="DEFERRED"):
        auth_module.create_authorization_packet(tmp_path, slug)


# ---------------------------------------------------------------------------
# IP-2: named-packet cache + activate + list
# ---------------------------------------------------------------------------


def _make_groundtruth_toml(tmp_path: Path) -> None:
    """Create a minimal groundtruth.toml so groundtruth_db_path resolves."""
    (tmp_path / "groundtruth.toml").write_text('[groundtruth]\ndb_path = "groundtruth.db"\n', encoding="utf-8")


def _seed_owner_sufficiency_deliberation(
    tmp_path: Path,
    *,
    deliberation_id: str = "DELIB-OWNER-SUFFICIENCY",
    source_type: str = "owner_conversation",
    outcome: str = "owner_decision",
    work_item_id: str | None = "WI-OWNER-SUFFICIENCY",
    related_work_item_id: str | None = None,
    content: str | None = None,
) -> str:
    """Seed the minimal MemBase deliberation surface used by the gate."""
    _make_groundtruth_toml(tmp_path)
    db_path = tmp_path / "groundtruth.db"
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """CREATE TABLE current_deliberations (
                id TEXT PRIMARY KEY,
                source_type TEXT NOT NULL,
                outcome TEXT,
                work_item_id TEXT,
                title TEXT,
                summary TEXT,
                content TEXT
            )"""
        )
        conn.execute(
            """CREATE TABLE deliberation_work_items (
                deliberation_id TEXT NOT NULL,
                work_item_id TEXT NOT NULL,
                role TEXT DEFAULT 'related'
            )"""
        )
        conn.execute(
            """INSERT INTO current_deliberations
               (id, source_type, outcome, work_item_id, title, summary, content)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                deliberation_id,
                source_type,
                outcome,
                work_item_id,
                "Owner clarification",
                "Existing requirements are sufficient.",
                content
                or (
                    "Mike stated: Existing requirements are sufficient. "
                    "This applies to bridge fixture-bridge and preserves all other gates."
                ),
            ),
        )
        if related_work_item_id:
            conn.execute(
                "INSERT INTO deliberation_work_items (deliberation_id, work_item_id) VALUES (?, ?)",
                (deliberation_id, related_work_item_id),
            )
        conn.commit()
    finally:
        conn.close()
    return deliberation_id


def _seed_project_authorization(
    tmp_path: Path,
    *,
    project_status: str = "active",
    allowed_mutation_classes: list[str] | None = None,
    auth_id: str = "PAUTH-FIXTURE",
    project_id: str = "PROJECT-FIXTURE",
) -> str:
    """Seed the minimal project-authorization surface used by the gate."""
    _make_groundtruth_toml(tmp_path)
    db_path = tmp_path / "groundtruth.db"
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """CREATE TABLE current_projects (
                id TEXT PRIMARY KEY,
                status TEXT NOT NULL
            )"""
        )
        conn.execute(
            """CREATE TABLE current_project_authorizations (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                status TEXT NOT NULL,
                authorization_name TEXT,
                owner_decision_deliberation_id TEXT,
                scope_summary TEXT,
                expires_at TEXT,
                allowed_mutation_classes TEXT,
                forbidden_operations TEXT,
                included_work_item_ids TEXT,
                excluded_work_item_ids TEXT,
                included_spec_ids TEXT,
                excluded_spec_ids TEXT
            )"""
        )
        conn.execute(
            "INSERT INTO current_projects (id, status) VALUES (?, ?)",
            (project_id, project_status),
        )
        conn.execute(
            """INSERT INTO current_project_authorizations
               (id, project_id, status, authorization_name, owner_decision_deliberation_id,
                scope_summary, expires_at, allowed_mutation_classes, forbidden_operations,
                included_work_item_ids, excluded_work_item_ids, included_spec_ids, excluded_spec_ids)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                auth_id,
                project_id,
                "active",
                "Fixture PAUTH",
                "DELIB-FIXTURE",
                "Fixture implementation authority.",
                None,
                json.dumps(allowed_mutation_classes or []),
                json.dumps([]),
                json.dumps([]),
                json.dumps([]),
                json.dumps([]),
                json.dumps([]),
            ),
        )
        conn.commit()
    finally:
        conn.close()
    return auth_id


def _add_project_authorization_metadata(
    proposal_path: Path,
    *,
    auth_id: str = "PAUTH-FIXTURE",
    project_id: str = "PROJECT-FIXTURE",
) -> None:
    proposal_path.write_text(
        proposal_path.read_text(encoding="utf-8") + f"\nProject Authorization: {auth_id}\nProject: {project_id}\n",
        encoding="utf-8",
    )


def _begin_packet(auth_module, tmp_path: Path, slug: str) -> dict[str, Any]:
    """Wrapper: create + write both current.json and named packet."""
    packet = auth_module.create_authorization_packet(tmp_path, slug)
    auth_module.write_packet(tmp_path, packet)
    auth_module.write_named_packet(tmp_path, packet, slug)
    return packet


def _write_prime_marker(tmp_path: Path, session_id: str) -> None:
    marker_dir = tmp_path / ".claude" / "session"
    marker_dir.mkdir(parents=True, exist_ok=True)
    (marker_dir / f"role-{session_id}.json").write_text(
        json.dumps({"role": "prime-builder", "session_id": session_id}),
        encoding="utf-8",
    )


def _claim_bridge(auth_module, tmp_path: Path, slug: str, session_id: str = "session-1") -> None:
    _write_prime_marker(tmp_path, session_id)
    assert auth_module.bridge_work_intent_registry.acquire(slug, session_id, project_root=tmp_path)


def test_begin_writes_both_current_and_named_packet(auth_module, tmp_path):
    """write_packet + write_named_packet write identical packet content to both
    locations.
    """
    _make_groundtruth_toml(tmp_path)
    slug, _, _ = _setup_simple_go_bridge(tmp_path)
    packet = _begin_packet(auth_module, tmp_path, slug)

    current_path = auth_module.packet_path(tmp_path)
    named_path = auth_module.packet_path_for_bridge(tmp_path, slug)
    assert current_path.is_file()
    assert named_path.is_file()
    assert current_path.read_text(encoding="utf-8") == named_path.read_text(encoding="utf-8")
    assert packet["bridge_id"] == slug


def test_begin_cli_refuses_without_work_intent_claim(auth_module, tmp_path, capsys):
    _make_groundtruth_toml(tmp_path)
    slug, _, _ = _setup_simple_go_bridge(tmp_path)

    rc = auth_module.main(
        [
            "--project-root",
            str(tmp_path),
            "begin",
            "--bridge-id",
            slug,
            "--session-id",
            "session-1",
            "--no-write",
        ]
    )

    assert rc == 2
    output = json.loads(capsys.readouterr().out)
    assert output["authorized"] is False
    assert "No active work-intent claim" in output["error"]
    assert not auth_module.packet_path(tmp_path).exists()


def test_begin_cli_refuses_claim_held_by_other_session(auth_module, tmp_path, capsys):
    _make_groundtruth_toml(tmp_path)
    slug, _, _ = _setup_simple_go_bridge(tmp_path)
    _claim_bridge(auth_module, tmp_path, slug, session_id="other-session")

    rc = auth_module.main(
        [
            "--project-root",
            str(tmp_path),
            "begin",
            "--bridge-id",
            slug,
            "--session-id",
            "session-1",
            "--no-write",
        ]
    )

    assert rc == 2
    output = json.loads(capsys.readouterr().out)
    assert "claimed by session 'other-session'" in output["error"]
    assert not auth_module.packet_path(tmp_path).exists()


def test_begin_cli_succeeds_when_work_intent_claim_held(auth_module, tmp_path, capsys):
    _make_groundtruth_toml(tmp_path)
    slug, _, _ = _setup_simple_go_bridge(tmp_path)
    _claim_bridge(auth_module, tmp_path, slug, session_id="session-1")

    rc = auth_module.main(
        [
            "--project-root",
            str(tmp_path),
            "begin",
            "--bridge-id",
            slug,
            "--session-id",
            "session-1",
            "--no-write",
        ]
    )

    assert rc == 0
    packet = json.loads(capsys.readouterr().out)
    assert packet["bridge_id"] == slug
    assert not auth_module.packet_path(tmp_path).exists()


def test_project_authorization_accepts_active_project_without_retirement_class(auth_module, tmp_path):
    """Baseline: ordinary active-project PAUTH validation remains unchanged."""
    slug = "project-auth-active"
    proposal = _write_proposal(tmp_path, slug, version=1, target_paths=["scripts/dummy.py"])
    _add_project_authorization_metadata(proposal)
    _write_verdict(tmp_path, slug, version=2, verdict="GO")
    _seed_project_authorization(tmp_path, project_status="active", allowed_mutation_classes=["source"])

    packet = auth_module.create_authorization_packet(tmp_path, slug)

    assert packet["project_authorization"]["id"] == "PAUTH-FIXTURE"
    assert packet["project_authorization"]["project_id"] == "PROJECT-FIXTURE"


def test_project_authorization_accepts_retired_project_for_retirement_reconciliation(auth_module, tmp_path):
    """Retired-project reconciliation PAUTHs can mint implementation packets."""
    slug = "project-auth-retired-reconciliation"
    proposal = _write_proposal(tmp_path, slug, version=1, target_paths=["scripts/dummy.py"])
    _add_project_authorization_metadata(proposal)
    _write_verdict(tmp_path, slug, version=2, verdict="GO")
    _seed_project_authorization(
        tmp_path,
        project_status="retired",
        allowed_mutation_classes=["project_retirement_reconciliation"],
    )

    packet = auth_module.create_authorization_packet(tmp_path, slug)

    assert packet["project_authorization"]["id"] == "PAUTH-FIXTURE"
    assert packet["project_authorization"]["project_id"] == "PROJECT-FIXTURE"


def test_project_authorization_rejects_retired_project_without_retirement_reconciliation(auth_module, tmp_path):
    """Retired projects still fail closed unless the PAUTH explicitly allows reconciliation."""
    slug = "project-auth-retired-denied"
    proposal = _write_proposal(tmp_path, slug, version=1, target_paths=["scripts/dummy.py"])
    _add_project_authorization_metadata(proposal)
    _write_verdict(tmp_path, slug, version=2, verdict="GO")
    _seed_project_authorization(tmp_path, project_status="retired", allowed_mutation_classes=["source"])

    with pytest.raises(auth_module.AuthorizationError, match="not attached to an active project"):
        auth_module.create_authorization_packet(tmp_path, slug)


def test_activate_restores_named_packet_to_current_json(auth_module, tmp_path):
    """activate copies the named packet back to current.json after current.json
    has been overwritten by another bridge.
    """
    _make_groundtruth_toml(tmp_path)
    slug_a, _, _ = _setup_simple_go_bridge(tmp_path, slug="bridge-a")
    _begin_packet(auth_module, tmp_path, slug_a)
    # Set up a second bridge
    _write_proposal(tmp_path, "bridge-b", version=1, target_paths=["scripts/b.py"])
    _write_verdict(tmp_path, "bridge-b", version=2, verdict="GO")
    block_b = "Document: bridge-b\nGO: bridge/bridge-b-002.md\nNEW: bridge/bridge-b.md\n"
    block_a = f"Document: {slug_a}\nGO: bridge/{slug_a}-002.md\nNEW: bridge/{slug_a}.md\n"
    _ignore_retired_index_fixture(tmp_path, [block_b, block_a])
    # Overwrite current.json with bridge-b's packet
    _begin_packet(auth_module, tmp_path, "bridge-b")
    assert json.loads(auth_module.packet_path(tmp_path).read_text(encoding="utf-8"))["bridge_id"] == "bridge-b"

    # Activate bridge-a; current.json should now reflect bridge-a's packet
    auth_module.activate_packet(tmp_path, slug_a)
    assert json.loads(auth_module.packet_path(tmp_path).read_text(encoding="utf-8"))["bridge_id"] == slug_a


def test_activate_fails_when_named_packet_expired(auth_module, tmp_path):
    """An expired named packet causes activate to raise without touching current.json."""
    _make_groundtruth_toml(tmp_path)
    slug, _, _ = _setup_simple_go_bridge(tmp_path)
    packet = auth_module.create_authorization_packet(tmp_path, slug)
    # Backdate expiration before computing hash
    packet["expires_at"] = "2026-01-01T00:00:00Z"
    packet["packet_hash"] = auth_module.packet_hash(packet)
    auth_module.write_named_packet(tmp_path, packet, slug)

    with pytest.raises(auth_module.AuthorizationError, match="expired"):
        auth_module.activate_packet(tmp_path, slug)


def test_activate_fails_when_bridge_status_drifted(auth_module, tmp_path):
    """If the bridge's latest INDEX status drifts off GO, activate raises."""
    _make_groundtruth_toml(tmp_path)
    slug, _, _ = _setup_simple_go_bridge(tmp_path)
    _begin_packet(auth_module, tmp_path, slug)

    # Now drift the INDEX: add NEW: -003.md so latest_status is no longer GO
    _write_proposal(tmp_path, slug, version=3, target_paths=["scripts/dummy.py"])
    block = f"Document: {slug}\nNEW: bridge/{slug}-003.md\nGO: bridge/{slug}-002.md\nNEW: bridge/{slug}.md\n"
    _ignore_retired_index_fixture(tmp_path, [block])

    with pytest.raises(auth_module.AuthorizationError, match="awaiting Loyal Opposition review"):
        auth_module.activate_packet(tmp_path, slug)


def test_validate_packet_fails_with_pending_new_after_go(auth_module, tmp_path):
    """IP-C chain walk: chain [GO, NEW] -> fail with 'awaiting Loyal Opposition review'."""
    _make_groundtruth_toml(tmp_path)
    slug, _, _ = _setup_simple_go_bridge(tmp_path)
    _begin_packet(auth_module, tmp_path, slug)
    _write_proposal(tmp_path, slug, version=3, target_paths=["scripts/dummy.py"])
    block = f"Document: {slug}\nNEW: bridge/{slug}-003.md\nGO: bridge/{slug}-002.md\nNEW: bridge/{slug}.md\n"
    _ignore_retired_index_fixture(tmp_path, [block])
    with pytest.raises(auth_module.AuthorizationError, match="awaiting Loyal Opposition review"):
        auth_module.activate_packet(tmp_path, slug)


def test_validate_packet_fails_with_newer_go_after_pinned_go(auth_module, tmp_path):
    """A newer GO after the packet's pinned go_file -> fail with 'Newer GO exists'.

    Repurposed from test_validate_packet_fails_with_revised_anywhere_in_chain:
    per WI-3333 Bug 3, a post-GO REVISED is a revised post-implementation
    report, not a superseding proposal, so it is no longer an automatic
    failure. The chain here additionally carries a genuine newer GO at -004,
    which is still rejected because the packet pins the -002 go_file.
    """
    _make_groundtruth_toml(tmp_path)
    slug, _, _ = _setup_simple_go_bridge(tmp_path)
    _begin_packet(auth_module, tmp_path, slug)
    _write_proposal(tmp_path, slug, version=3, target_paths=["scripts/dummy.py"])
    _write_verdict(tmp_path, slug, version=4, verdict="GO")
    block = (
        f"Document: {slug}\n"
        f"GO: bridge/{slug}-004.md\n"
        f"REVISED: bridge/{slug}-003.md\n"
        f"GO: bridge/{slug}-002.md\n"
        f"NEW: bridge/{slug}.md\n"
    )
    _ignore_retired_index_fixture(tmp_path, [block])
    with pytest.raises(auth_module.AuthorizationError, match="Newer GO exists"):
        auth_module.activate_packet(tmp_path, slug)


def test_validate_packet_fails_with_verified_after_go(auth_module, tmp_path):
    """IP-C chain walk: chain [GO, NEW, VERIFIED] -> fail with 'VERIFIED (terminal'."""
    _make_groundtruth_toml(tmp_path)
    slug, _, _ = _setup_simple_go_bridge(tmp_path)
    _begin_packet(auth_module, tmp_path, slug)
    _write_proposal(tmp_path, slug, version=3, target_paths=["scripts/dummy.py"])
    _write_verdict(tmp_path, slug, version=4, verdict="VERIFIED")
    block = (
        f"Document: {slug}\n"
        f"VERIFIED: bridge/{slug}-004.md\n"
        f"NEW: bridge/{slug}-003.md\n"
        f"GO: bridge/{slug}-002.md\n"
        f"NEW: bridge/{slug}.md\n"
    )
    _ignore_retired_index_fixture(tmp_path, [block])
    with pytest.raises(auth_module.AuthorizationError, match="VERIFIED \\(terminal"):
        auth_module.activate_packet(tmp_path, slug)


def test_validate_packet_fails_with_deferred_after_go(auth_module, tmp_path):
    """A packet issued under GO fails validation after owner-parking as DEFERRED."""
    _make_groundtruth_toml(tmp_path)
    slug, _, _ = _setup_simple_go_bridge(tmp_path)
    _begin_packet(auth_module, tmp_path, slug)
    _write_verdict(tmp_path, slug, version=3, verdict="DEFERRED")
    block = f"Document: {slug}\nDEFERRED: bridge/{slug}-003.md\nGO: bridge/{slug}-002.md\nNEW: bridge/{slug}.md\n"
    _ignore_retired_index_fixture(tmp_path, [block])

    with pytest.raises(auth_module.AuthorizationError, match="DEFERRED"):
        auth_module.load_packet(tmp_path)


def test_validate_packet_succeeds_with_no_go_after_post_impl(auth_module, tmp_path):
    """IP-C chain walk: chain [GO, NEW, NO-GO] (Friction C corrective) -> packet validates."""
    _make_groundtruth_toml(tmp_path)
    slug, _, _ = _setup_simple_go_bridge(tmp_path)
    _begin_packet(auth_module, tmp_path, slug)
    _write_proposal(tmp_path, slug, version=3, target_paths=["scripts/dummy.py"])
    _write_verdict(tmp_path, slug, version=4, verdict="NO-GO")
    block = (
        f"Document: {slug}\n"
        f"NO-GO: bridge/{slug}-004.md\n"
        f"NEW: bridge/{slug}-003.md\n"
        f"GO: bridge/{slug}-002.md\n"
        f"NEW: bridge/{slug}.md\n"
    )
    _ignore_retired_index_fixture(tmp_path, [block])
    packet = auth_module.activate_packet(tmp_path, slug)
    assert packet["bridge_id"] == slug


def test_list_enumerates_named_packets(auth_module, tmp_path):
    """list returns one row per named packet with bridge_id, expires_at, globs, valid."""
    _make_groundtruth_toml(tmp_path)
    _write_proposal(tmp_path, "bridge-a", version=1)
    _write_verdict(tmp_path, "bridge-a", version=2, verdict="GO")
    _write_proposal(tmp_path, "bridge-b", version=1)
    _write_verdict(tmp_path, "bridge-b", version=2, verdict="GO")
    _ignore_retired_index_fixture(
        tmp_path,
        [
            "Document: bridge-a\nGO: bridge/bridge-a-002.md\nNEW: bridge/bridge-a.md\n",
            "Document: bridge-b\nGO: bridge/bridge-b-002.md\nNEW: bridge/bridge-b.md\n",
        ],
    )
    _begin_packet(auth_module, tmp_path, "bridge-a")
    _begin_packet(auth_module, tmp_path, "bridge-b")

    rows = auth_module.list_named_packets(tmp_path)
    bridge_ids = sorted(r["bridge_id"] for r in rows)
    assert bridge_ids == ["bridge-a", "bridge-b"]
    assert all(r["valid"] for r in rows)
    assert all(r["error"] is None for r in rows)


def test_list_returns_empty_when_by_bridge_dir_absent(auth_module, tmp_path):
    """No named packets ever written -> list returns []."""
    rows = auth_module.list_named_packets(tmp_path)
    assert rows == []


def test_clear_active_packet_if_terminal_deletes_current_only(auth_module, tmp_path):
    _make_groundtruth_toml(tmp_path)
    slug, _, _ = _setup_simple_go_bridge(tmp_path)
    _begin_packet(auth_module, tmp_path, slug)
    _write_proposal(tmp_path, slug, version=3, status="NEW", target_paths=["scripts/dummy.py"])
    _write_verdict(tmp_path, slug, version=4, verdict="VERIFIED")

    current_path = auth_module.packet_path(tmp_path)
    named_path = auth_module.packet_path_for_bridge(tmp_path, slug)
    result = auth_module.clear_active_packet_if_terminal(tmp_path)

    assert result == {"cleared": True, "bridge_id": slug, "reason": "thread VERIFIED"}
    assert not current_path.exists()
    assert named_path.exists()


@pytest.mark.parametrize(
    ("latest_status", "writer"),
    [
        ("GO", None),
        (
            "NEW",
            lambda root, slug: _write_proposal(root, slug, version=3, status="NEW", target_paths=["scripts/dummy.py"]),
        ),
        (
            "REVISED",
            lambda root, slug: _write_proposal(
                root, slug, version=3, status="REVISED", target_paths=["scripts/dummy.py"]
            ),
        ),
        ("NO-GO", lambda root, slug: _write_verdict(root, slug, version=3, verdict="NO-GO")),
    ],
)
def test_clear_active_packet_if_terminal_preserves_in_flight_packets(auth_module, tmp_path, latest_status, writer):
    _make_groundtruth_toml(tmp_path)
    slug, _, _ = _setup_simple_go_bridge(tmp_path, slug=f"in-flight-{latest_status.lower()}")
    _begin_packet(auth_module, tmp_path, slug)
    if writer is not None:
        writer(tmp_path, slug)

    current_path = auth_module.packet_path(tmp_path)
    result = auth_module.clear_active_packet_if_terminal(tmp_path)

    assert result["cleared"] is False
    assert result["bridge_id"] == slug
    if latest_status == "GO":
        assert result["reason"] == "thread not VERIFIED (state=latest_is_go)"
    else:
        assert result["reason"].startswith("thread not VERIFIED")
    assert current_path.exists()


def test_clear_active_packet_if_terminal_noops_without_current(auth_module, tmp_path):
    result = auth_module.clear_active_packet_if_terminal(tmp_path)

    assert result == {"cleared": False, "bridge_id": None, "reason": "no active packet"}


def test_wrap_clear_impl_start_packet_script_emits_summary(auth_module, tmp_path):
    _make_groundtruth_toml(tmp_path)
    slug, _, _ = _setup_simple_go_bridge(tmp_path, slug="wrap-clear")
    _begin_packet(auth_module, tmp_path, slug)
    _write_proposal(tmp_path, slug, version=3, status="NEW", target_paths=["scripts/dummy.py"])
    _write_verdict(tmp_path, slug, version=4, verdict="VERIFIED")

    completed = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "wrap_clear_impl_start_packet.py"),
            "--project-root",
            str(tmp_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    prefix, payload = completed.stdout.strip().split(" ", 1)
    assert prefix == "implementation_start_packet_clear"
    assert json.loads(payload) == {"cleared": True, "bridge_id": slug, "reason": "thread VERIFIED"}
    assert not auth_module.packet_path(tmp_path).exists()


# ---------------------------------------------------------------------------
# F2-001 / WI-4452 regression: current.json plus named-packet fallback
# ---------------------------------------------------------------------------


def test_legacy_current_json_only_workflow_still_works(auth_module, tmp_path):
    """A session that calls begin without using activate/list still authorizes
    against current.json exactly as before Slice 4 IP-2.
    """
    _make_groundtruth_toml(tmp_path)
    slug, _, _ = _setup_simple_go_bridge(tmp_path)
    _begin_packet(auth_module, tmp_path, slug)
    target = tmp_path / "scripts" / "dummy.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.touch()
    result = auth_module.validate_targets(tmp_path, ["scripts/dummy.py"])
    assert result["packet"]["bridge_id"] == slug
    assert result["targets"] == ["scripts/dummy.py"]


def test_validate_targets_falls_back_to_unique_named_packet_after_current_clobber(auth_module, tmp_path):
    """WI-4452: bridge A remains authorized after bridge B overwrites current.json."""
    _make_groundtruth_toml(tmp_path)
    _write_proposal(tmp_path, "bridge-a", version=1, target_paths=["scripts/a.py"])
    _write_verdict(tmp_path, "bridge-a", version=2, verdict="GO")
    _write_proposal(tmp_path, "bridge-b", version=1, target_paths=["scripts/b.py"])
    _write_verdict(tmp_path, "bridge-b", version=2, verdict="GO")
    _ignore_retired_index_fixture(
        tmp_path,
        [
            "Document: bridge-a\nGO: bridge/bridge-a-002.md\nNEW: bridge/bridge-a.md\n",
            "Document: bridge-b\nGO: bridge/bridge-b-002.md\nNEW: bridge/bridge-b.md\n",
        ],
    )
    _begin_packet(auth_module, tmp_path, "bridge-a")
    _begin_packet(auth_module, tmp_path, "bridge-b")
    current_path = auth_module.packet_path(tmp_path)
    assert json.loads(current_path.read_text(encoding="utf-8"))["bridge_id"] == "bridge-b"

    result_a = auth_module.validate_targets(tmp_path, ["scripts/a.py"])
    assert result_a["packet"]["bridge_id"] == "bridge-a"
    assert result_a["targets"] == ["scripts/a.py"]
    assert json.loads(current_path.read_text(encoding="utf-8"))["bridge_id"] == "bridge-b"

    result_b = auth_module.validate_targets(tmp_path, ["scripts/b.py"])
    assert result_b["packet"]["bridge_id"] == "bridge-b"
    assert result_b["targets"] == ["scripts/b.py"]


def test_validate_targets_session_aware_prefers_claimed_bridge_packet(auth_module, tmp_path):
    """WI-4443: when a session holds a work-intent claim, validate_targets prefers
    that session's OWN by-bridge packet over the global current.json pointer.

    Both bridge-a and bridge-b authorize the SAME target and current.json points
    to bridge-b. A session that claims bridge-a must resolve to bridge-a's packet
    (session-aware), while the same call with no session_id falls back to the
    global pointer (bridge-b) -- proving the session lookup is what disambiguates
    the concurrent-implementer thrash WI-4443 fixes.
    """
    _make_groundtruth_toml(tmp_path)
    _write_proposal(tmp_path, "bridge-a", version=1, target_paths=["scripts/shared.py"])
    _write_verdict(tmp_path, "bridge-a", version=2, verdict="GO")
    _write_proposal(tmp_path, "bridge-b", version=1, target_paths=["scripts/shared.py"])
    _write_verdict(tmp_path, "bridge-b", version=2, verdict="GO")
    _ignore_retired_index_fixture(
        tmp_path,
        [
            "Document: bridge-a\nGO: bridge/bridge-a-002.md\nNEW: bridge/bridge-a.md\n",
            "Document: bridge-b\nGO: bridge/bridge-b-002.md\nNEW: bridge/bridge-b.md\n",
        ],
    )
    _begin_packet(auth_module, tmp_path, "bridge-a")
    _begin_packet(auth_module, tmp_path, "bridge-b")
    current_path = auth_module.packet_path(tmp_path)
    assert json.loads(current_path.read_text(encoding="utf-8"))["bridge_id"] == "bridge-b"

    # Session A holds the bridge-a claim -> session-aware resolution returns bridge-a.
    _claim_bridge(auth_module, tmp_path, "bridge-a", session_id="session-A")
    result_session = auth_module.validate_targets(tmp_path, ["scripts/shared.py"], session_id="session-A")
    assert result_session["packet"]["bridge_id"] == "bridge-a"
    # The read does not mutate the global pointer.
    assert json.loads(current_path.read_text(encoding="utf-8"))["bridge_id"] == "bridge-b"

    # No session_id -> legacy path resolves the global current.json pointer (bridge-b).
    result_no_session = auth_module.validate_targets(tmp_path, ["scripts/shared.py"])
    assert result_no_session["packet"]["bridge_id"] == "bridge-b"

    # A session that holds NO claim also falls through to the global pointer.
    result_other = auth_module.validate_targets(tmp_path, ["scripts/shared.py"], session_id="session-unknown")
    assert result_other["packet"]["bridge_id"] == "bridge-b"


def test_packet_path_for_bridge_rejects_path_traversal_bridge_id(auth_module, tmp_path):
    """bridge_id with path separators or traversal segments is refused."""
    with pytest.raises(auth_module.AuthorizationError):
        auth_module.packet_path_for_bridge(tmp_path, "../escape")
    with pytest.raises(auth_module.AuthorizationError):
        auth_module.packet_path_for_bridge(tmp_path, "foo/bar")
    with pytest.raises(auth_module.AuthorizationError):
        auth_module.packet_path_for_bridge(tmp_path, "")


# ---------------------------------------------------------------------------
# WI GTKB-IMPL-AUTH-VERIFICATION-HEADING-GATE-ALIGNMENT:
# has_spec_derived_verification heading-token recognition (bridge thread
# gtkb-impl-auth-verification-heading-gate-alignment).
# ---------------------------------------------------------------------------


def test_has_spec_derived_verification_accepts_legacy_headings(auth_module):
    """All four legacy exact headings remain recognized (regression-safe)."""
    for heading in (
        "Specification-Derived Verification",
        "Specification-Derived Verification Plan",
        "Spec-Derived Test Plan",
        "Verification Plan",
    ):
        markdown = f"## {heading}\n\nDerived from the linked specs.\n"
        assert auth_module.has_spec_derived_verification(markdown), heading


def test_has_spec_derived_verification_accepts_test_plan_spec_to_test_heading(auth_module):
    """A 'Test Plan (spec-to-test mapping)' heading with command evidence is
    recognized -- the S351 case the begin gate previously rejected."""
    markdown = (
        "## Test Plan (spec-to-test mapping)\n\nRun `python -m pytest platform_tests/scripts/test_x.py -q` to verify.\n"
    )
    assert auth_module.has_spec_derived_verification(markdown)


def test_has_spec_derived_verification_accepts_spec_to_test_mapping_heading(auth_module):
    """A 'Spec-to-Test Mapping' heading is recognized via the spec-to-test token."""
    markdown = "## Spec-to-Test Mapping\n\nEach linked spec maps to a test below.\n"
    assert auth_module.has_spec_derived_verification(markdown)


def test_has_spec_derived_verification_accepts_h2_plan_with_generic_h3_evidence(auth_module):
    """A qualifying h2 verification section includes generic h3 evidence."""
    markdown = "## Verification Plan\n\n### Evidence\n\nRun `python -m pytest platform_tests/scripts/test_x.py -q`.\n"
    assert auth_module.has_spec_derived_verification(markdown)


def test_has_spec_derived_verification_accepts_h2_spec_plan_with_generic_h3_body(auth_module):
    """A spec-derived h2 plan is recognized when its body sits under h3."""
    markdown = "## Spec-Derived Verification Plan\n\n### Evidence\n\nDerived from the linked specifications.\n"
    assert auth_module.has_spec_derived_verification(markdown)


def test_has_spec_derived_verification_rejects_bare_test_plan_without_evidence(auth_module):
    """A bare 'Test Plan' heading with no test-command evidence is rejected
    (governance floor preserved)."""
    markdown = "## Test Plan\n\nWe will think carefully about correctness.\n"
    assert not auth_module.has_spec_derived_verification(markdown)


def test_has_spec_derived_verification_rejects_h2_test_plan_h3_without_evidence(auth_module):
    """Nested h3 parsing does not widen bare Test Plan acceptance."""
    markdown = "## Test Plan\n\n### Evidence\n\nWe will think carefully about correctness.\n"
    assert not auth_module.has_spec_derived_verification(markdown)


def test_has_spec_derived_verification_rejects_missing_verification_section(auth_module):
    """A proposal with no verification section returns False."""
    markdown = "## Specification Links\n\n- GOV-FILE-BRIDGE-AUTHORITY-001\n"
    assert not auth_module.has_spec_derived_verification(markdown)


def test_section_body_exact_match_preserved(auth_module):
    """section_body keeps exact, first-match, case-insensitive heading semantics
    after the _iter_sections refactor."""
    markdown = "## Verification Plan\n\nfirst body\n\n## Other\n\nother body\n\n## Verification Plan\n\nsecond body\n"
    assert auth_module.section_body(markdown, "Verification Plan") == "first body"
    assert auth_module.section_body(markdown, "verification plan") == "first body"
    assert auth_module.section_body(markdown, "Test Plan (spec-to-test mapping)") == ""


def test_create_authorization_packet_accepts_test_plan_spec_to_test_heading(auth_module, tmp_path):
    """Integration: a GO'd proposal whose verification heading is
    'Test Plan (spec-to-test mapping)' yields a valid authorization packet
    rather than raising -- reproduces and closes the S351 friction."""
    slug = "fixture-bridge"
    _write_proposal(
        tmp_path,
        slug,
        version=1,
        target_paths=["scripts/dummy.py", ".gtkb-state/**"],
        verification_heading="Test Plan (spec-to-test mapping)",
        verification_body="Run `python -m pytest platform_tests/scripts/test_dummy.py -q`.",
    )
    _write_verdict(tmp_path, slug, version=2, verdict="GO")
    _ignore_retired_index_fixture(
        tmp_path,
        [f"Document: {slug}\nGO: bridge/{slug}-002.md\nNEW: bridge/{slug}.md\n"],
    )
    packet = auth_module.create_authorization_packet(tmp_path, slug)
    assert packet["bridge_id"] == slug


# ---------------------------------------------------------------------------
# WI-3410: Requirement Sufficiency natural-phrase tolerance
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "phrase",
    [
        "Existing requirements sufficient",
        "Existing requirements are sufficient",
        "Requirements remain sufficient",
        "Requirements are sufficient for this scope",
        "Existing requirements are sufficient for this scoped governance correction",
        "Existing owner direction and WI-4213 are sufficient to formalize the active-status capability gate",
    ],
)
def test_requirement_sufficiency_state_accepts_wi3410_variants(auth_module, phrase):
    """WI-3410: approved natural sufficient-state phrasings are accepted."""
    markdown = f"## Requirement Sufficiency\n\n{phrase}.\n"
    assert auth_module.requirement_sufficiency_state(markdown) == "sufficient"


def test_requirement_sufficiency_state_is_case_and_whitespace_tolerant(auth_module):
    """WI-3410: matching tolerates case and ordinary markdown line wrapping."""
    markdown = "## Requirement Sufficiency\n\nexisting requirements\nare sufficient.\n"
    assert auth_module.requirement_sufficiency_state(markdown) == "sufficient"


def test_requirement_sufficiency_gap_takes_precedence(auth_module):
    """WI-3410: an explicit requirements-gap declaration still blocks."""
    markdown = (
        "## Requirement Sufficiency\n\n"
        "Existing requirements are sufficient, but new or revised requirement "
        "required before implementation.\n"
    )
    assert auth_module.requirement_sufficiency_state(markdown) == "gap"


def test_requirement_sufficiency_future_scoped_gap_is_sufficient(auth_module):
    """Ensure that future-scoped gap sentences match as sufficient."""
    markdown = (
        "## Requirement Sufficiency\n\n"
        "Existing requirements sufficient for umbrella decomposition. "
        "New or revised requirements may be required by specific child WIs "
        "before source implementation; those decisions belong in the child proposals, "
        "not this umbrella.\n"
    )
    assert auth_module.requirement_sufficiency_state(markdown) == "sufficient"


def test_requirement_sufficiency_state_rejects_unapproved_phrase(auth_module):
    """WI-3410 + HYG-046: an unapproved phrase is not accepted as sufficient; a
    present-but-unrecognized section returns the distinct 'unrecognized' state."""
    markdown = "## Requirement Sufficiency\n\nThis probably fits existing requirements.\n"
    assert auth_module.requirement_sufficiency_state(markdown) == "unrecognized"


def test_create_authorization_packet_accepts_requirement_sufficiency_are_sufficient(auth_module, tmp_path):
    """WI-3410 integration: a GO'd proposal using 'are sufficient' authorizes."""
    slug = "fixture-bridge"
    proposal_path = _write_proposal(tmp_path, slug, version=1, target_paths=["scripts/dummy.py"])
    proposal_path.write_text(
        proposal_path.read_text(encoding="utf-8").replace(
            "Existing requirements sufficient.",
            "Existing requirements are sufficient.",
        ),
        encoding="utf-8",
    )
    _write_verdict(tmp_path, slug, version=2, verdict="GO")
    _ignore_retired_index_fixture(tmp_path, [f"Document: {slug}\nGO: bridge/{slug}-002.md\nNEW: bridge/{slug}.md\n"])
    packet = auth_module.create_authorization_packet(tmp_path, slug)
    assert packet["requirement_sufficiency"] == "sufficient"


def test_create_authorization_packet_accepts_owner_direction_work_item_sufficiency(auth_module, tmp_path):
    """WI-4213 integration: approved owner-direction/work-item phrasing authorizes."""
    slug = "fixture-bridge"
    proposal_path = _write_proposal(tmp_path, slug, version=1, target_paths=["scripts/dummy.py"])
    proposal_path.write_text(
        proposal_path.read_text(encoding="utf-8").replace(
            "Existing requirements sufficient.",
            "Existing owner direction and WI-4213 are sufficient to formalize the active-status capability gate.",
        ),
        encoding="utf-8",
    )
    _write_verdict(tmp_path, slug, version=2, verdict="GO")
    _ignore_retired_index_fixture(tmp_path, [f"Document: {slug}\nGO: bridge/{slug}-002.md\nNEW: bridge/{slug}.md\n"])
    packet = auth_module.create_authorization_packet(tmp_path, slug)
    assert packet["requirement_sufficiency"] == "sufficient"


# ---------------------------------------------------------------------------
# WI-4241: owner-decision deliberation fallback for Requirement Sufficiency
# ---------------------------------------------------------------------------


def test_owner_sufficiency_deliberation_allows_missing_proposal_phrase(auth_module, tmp_path):
    """WI-4241: explicit owner evidence can satisfy only the missing phrase gate."""
    slug = "fixture-bridge"
    proposal_path = _write_proposal(tmp_path, slug, version=1, target_paths=["scripts/dummy.py"])
    proposal_path.write_text(
        proposal_path.read_text(encoding="utf-8").replace(
            "Existing requirements sufficient.",
            "This proposal has complete requirements coverage, but no bounded phrase.",
        )
        + "\nWork Item: WI-OWNER-SUFFICIENCY\n",
        encoding="utf-8",
    )
    _write_verdict(tmp_path, slug, version=2, verdict="GO")
    _ignore_retired_index_fixture(tmp_path, [f"Document: {slug}\nGO: bridge/{slug}-002.md\nNEW: bridge/{slug}.md\n"])
    delib_id = _seed_owner_sufficiency_deliberation(tmp_path)

    packet = auth_module.create_authorization_packet(
        tmp_path,
        slug,
        owner_sufficiency_deliberation_id=delib_id,
    )

    assert packet["requirement_sufficiency"] == "owner_deliberation"
    assert packet["requirement_sufficiency_evidence"] == {
        "mode": "owner_deliberation",
        "deliberation_id": delib_id,
        "source_type": "owner_conversation",
        "outcome": "owner_decision",
        "work_item_id": "WI-OWNER-SUFFICIENCY",
        "matched_basis": "bridge_id",
    }


def test_owner_sufficiency_deliberation_can_match_work_item_relation(auth_module, tmp_path):
    """WI-4241: applicability may come from a related work-item link."""
    slug = "fixture-bridge"
    proposal_path = _write_proposal(tmp_path, slug, version=1, target_paths=["scripts/dummy.py"])
    proposal_path.write_text(
        proposal_path.read_text(encoding="utf-8").replace(
            "Existing requirements sufficient.",
            "This proposal has complete requirements coverage, but no bounded phrase.",
        )
        + "\nWork Item: WI-RELATED\n",
        encoding="utf-8",
    )
    _write_verdict(tmp_path, slug, version=2, verdict="GO")
    _ignore_retired_index_fixture(tmp_path, [f"Document: {slug}\nGO: bridge/{slug}-002.md\nNEW: bridge/{slug}.md\n"])
    delib_id = _seed_owner_sufficiency_deliberation(
        tmp_path,
        work_item_id=None,
        related_work_item_id="WI-RELATED",
        content="Mike stated: Existing requirements are sufficient.",
    )

    packet = auth_module.create_authorization_packet(
        tmp_path,
        slug,
        owner_sufficiency_deliberation_id=delib_id,
    )

    assert packet["requirement_sufficiency"] == "owner_deliberation"
    assert packet["requirement_sufficiency_evidence"]["matched_basis"] == "work_item_id"


def test_missing_requirement_sufficiency_still_blocks_without_owner_evidence(auth_module, tmp_path):
    slug = "fixture-bridge"
    proposal_path = _write_proposal(tmp_path, slug, version=1, target_paths=["scripts/dummy.py"])
    proposal_path.write_text(
        proposal_path.read_text(encoding="utf-8").replace(
            "Existing requirements sufficient.",
            "This proposal has complete requirements coverage, but no bounded phrase.",
        ),
        encoding="utf-8",
    )
    _write_verdict(tmp_path, slug, version=2, verdict="GO")
    _ignore_retired_index_fixture(tmp_path, [f"Document: {slug}\nGO: bridge/{slug}-002.md\nNEW: bridge/{slug}.md\n"])

    with pytest.raises(auth_module.AuthorizationError, match="phrasing is unrecognized"):
        auth_module.create_authorization_packet(tmp_path, slug)


def test_owner_sufficiency_deliberation_rejects_non_owner_source(auth_module, tmp_path):
    slug = "fixture-bridge"
    proposal_path = _write_proposal(tmp_path, slug, version=1, target_paths=["scripts/dummy.py"])
    proposal_path.write_text(
        proposal_path.read_text(encoding="utf-8").replace(
            "Existing requirements sufficient.",
            "This proposal has complete requirements coverage, but no bounded phrase.",
        ),
        encoding="utf-8",
    )
    _write_verdict(tmp_path, slug, version=2, verdict="GO")
    _ignore_retired_index_fixture(tmp_path, [f"Document: {slug}\nGO: bridge/{slug}-002.md\nNEW: bridge/{slug}.md\n"])
    delib_id = _seed_owner_sufficiency_deliberation(tmp_path, source_type="report")

    with pytest.raises(auth_module.AuthorizationError, match="not owner_conversation"):
        auth_module.create_authorization_packet(
            tmp_path,
            slug,
            owner_sufficiency_deliberation_id=delib_id,
        )


def test_owner_sufficiency_deliberation_rejects_non_decision_outcome(auth_module, tmp_path):
    slug = "fixture-bridge"
    proposal_path = _write_proposal(tmp_path, slug, version=1, target_paths=["scripts/dummy.py"])
    proposal_path.write_text(
        proposal_path.read_text(encoding="utf-8").replace(
            "Existing requirements sufficient.",
            "This proposal has complete requirements coverage, but no bounded phrase.",
        ),
        encoding="utf-8",
    )
    _write_verdict(tmp_path, slug, version=2, verdict="GO")
    _ignore_retired_index_fixture(tmp_path, [f"Document: {slug}\nGO: bridge/{slug}-002.md\nNEW: bridge/{slug}.md\n"])
    delib_id = _seed_owner_sufficiency_deliberation(tmp_path, outcome="deferred")

    with pytest.raises(auth_module.AuthorizationError, match="not an owner_decision"):
        auth_module.create_authorization_packet(
            tmp_path,
            slug,
            owner_sufficiency_deliberation_id=delib_id,
        )


def test_owner_sufficiency_deliberation_rejects_non_applicable_evidence(auth_module, tmp_path):
    slug = "fixture-bridge"
    proposal_path = _write_proposal(tmp_path, slug, version=1, target_paths=["scripts/dummy.py"])
    proposal_path.write_text(
        proposal_path.read_text(encoding="utf-8").replace(
            "Existing requirements sufficient.",
            "This proposal has complete requirements coverage, but no bounded phrase.",
        )
        + "\nWork Item: WI-THIS-WORK\n",
        encoding="utf-8",
    )
    _write_verdict(tmp_path, slug, version=2, verdict="GO")
    _ignore_retired_index_fixture(tmp_path, [f"Document: {slug}\nGO: bridge/{slug}-002.md\nNEW: bridge/{slug}.md\n"])
    delib_id = _seed_owner_sufficiency_deliberation(
        tmp_path,
        work_item_id="WI-OTHER",
        content="Mike stated: Existing requirements are sufficient for another bridge.",
    )

    with pytest.raises(auth_module.AuthorizationError, match="does not apply"):
        auth_module.create_authorization_packet(
            tmp_path,
            slug,
            owner_sufficiency_deliberation_id=delib_id,
        )


def test_owner_sufficiency_deliberation_does_not_override_explicit_gap(auth_module, tmp_path):
    slug = "fixture-bridge"
    proposal_path = _write_proposal(tmp_path, slug, version=1, target_paths=["scripts/dummy.py"])
    proposal_path.write_text(
        proposal_path.read_text(encoding="utf-8").replace(
            "Existing requirements sufficient.",
            "New or revised requirement required before implementation.",
        ),
        encoding="utf-8",
    )
    _write_verdict(tmp_path, slug, version=2, verdict="GO")
    _ignore_retired_index_fixture(tmp_path, [f"Document: {slug}\nGO: bridge/{slug}-002.md\nNEW: bridge/{slug}.md\n"])
    delib_id = _seed_owner_sufficiency_deliberation(tmp_path)

    with pytest.raises(auth_module.AuthorizationError, match="new or revised requirements"):
        auth_module.create_authorization_packet(
            tmp_path,
            slug,
            owner_sufficiency_deliberation_id=delib_id,
        )


def test_begin_cli_passes_owner_sufficiency_deliberation_id(auth_module, tmp_path, capsys):
    slug = "fixture-bridge"
    proposal_path = _write_proposal(tmp_path, slug, version=1, target_paths=["scripts/dummy.py"])
    proposal_path.write_text(
        proposal_path.read_text(encoding="utf-8").replace(
            "Existing requirements sufficient.",
            "This proposal has complete requirements coverage, but no bounded phrase.",
        ),
        encoding="utf-8",
    )
    _write_verdict(tmp_path, slug, version=2, verdict="GO")
    _ignore_retired_index_fixture(tmp_path, [f"Document: {slug}\nGO: bridge/{slug}-002.md\nNEW: bridge/{slug}.md\n"])
    delib_id = _seed_owner_sufficiency_deliberation(tmp_path)
    _claim_bridge(auth_module, tmp_path, slug, session_id="session-1")

    rc = auth_module.main(
        [
            "--project-root",
            str(tmp_path),
            "begin",
            "--bridge-id",
            slug,
            "--session-id",
            "session-1",
            "--owner-sufficiency-deliberation-id",
            delib_id,
            "--no-write",
        ]
    )

    assert rc == 0
    packet = json.loads(capsys.readouterr().out)
    assert packet["requirement_sufficiency"] == "owner_deliberation"
    assert not auth_module.packet_path(tmp_path).exists()


# ---------------------------------------------------------------------------
# WI-3333 Bug 1: `## target_paths` heading recognition in extract_target_paths
# ---------------------------------------------------------------------------


def test_extract_target_paths_accepts_target_paths_heading(auth_module):
    """T1 -- a `## target_paths` heading section with one backtick path per
    bullet yields the extracted paths."""
    md = "# Proposal\n\n## target_paths\n\n- `scripts/a.py`\n- `tests/b.py`\n"
    assert auth_module.extract_target_paths(md) == ["scripts/a.py", "tests/b.py"]


def test_extract_target_paths_target_paths_heading_first_span_only(auth_module):
    """T2 -- `## target_paths` bullets with a path plus a parenthetical
    backtick annotation yield only the first span (the path)."""
    md = "## target_paths\n\n- `scripts/a.py` (new module)\n- `tests/b.py` (`pytest` suite)\n"
    assert auth_module.extract_target_paths(md) == ["scripts/a.py", "tests/b.py"]


def test_extract_target_paths_inline_json_unchanged(auth_module):
    """T3 -- the inline `target_paths:` JSON metadata line is unchanged."""
    md = 'target_paths: ["scripts/a.py", "tests/b.py"]\n\n## Summary\n\nx\n'
    assert auth_module.extract_target_paths(md) == ["scripts/a.py", "tests/b.py"]


def test_extract_target_paths_files_expected_to_change_unchanged(auth_module):
    """T4 -- `## Files Expected To Change` multi-span bullets yield all spans."""
    md = "## Files Expected To Change\n\n- `scripts/a.py` and `scripts/c.py`\n- `tests/b.py`\n"
    assert auth_module.extract_target_paths(md) == [
        "scripts/a.py",
        "scripts/c.py",
        "tests/b.py",
    ]


def test_extract_target_paths_raises_when_all_forms_absent(auth_module):
    """T5 -- none of the three forms present -> AuthorizationError."""
    md = "# Proposal\n\n## Summary\n\nNo target paths anywhere.\n"
    with pytest.raises(auth_module.AuthorizationError, match="missing concrete target_paths"):
        auth_module.extract_target_paths(md)


def test_extract_target_paths_inline_json_precedence(auth_module):
    """T6 -- when both inline JSON and a `## target_paths` heading are present,
    the inline JSON form wins."""
    md = 'target_paths: ["scripts/inline.py"]\n\n## target_paths\n\n- `scripts/heading.py`\n'
    assert auth_module.extract_target_paths(md) == ["scripts/inline.py"]


# ---------------------------------------------------------------------------
# WI-3333 Bug 2: per-bullet Specification Links placeholder check
# ---------------------------------------------------------------------------


def test_extract_spec_links_substantive_word_in_cited_bullet_not_flagged(auth_module):
    """T7 -- a bullet citing a backticked spec is not flagged as placeholder
    even when its prose contains an ordinary placeholder-shaped word."""
    md = (
        "## Specification Links\n\n"
        "- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge authority; covers the pending-review state.\n"
    )
    assert auth_module.extract_spec_links(md) == ["GOV-FILE-BRIDGE-AUTHORITY-001"]


def test_extract_spec_links_placeholder_only_bullet_still_flagged(auth_module):
    """T8 -- a bullet with no concrete citation that matches PLACEHOLDER_RE
    still raises."""
    md = (
        "## Specification Links\n\n"
        "- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge authority.\n"
        "- TODO: add the remaining specs.\n"
    )
    with pytest.raises(auth_module.AuthorizationError, match="placeholder text"):
        auth_module.extract_spec_links(md)


def test_extract_spec_links_bare_placeholder_word_bullet_still_flagged(auth_module):
    """T9 -- a bullet that is a bare placeholder token still raises."""
    md = "## Specification Links\n\n- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge authority.\n- TBD\n"
    with pytest.raises(auth_module.AuthorizationError, match="placeholder text"):
        auth_module.extract_spec_links(md)


def test_extract_spec_links_id_token_bullet_with_placeholder_word_not_flagged(auth_module):
    """T10 -- a bullet citing a bare uppercase artifact-ID token (no backticks)
    is not flagged even when its prose contains a placeholder-shaped word."""
    md = "## Specification Links\n\n- GOV-FILE-BRIDGE-AUTHORITY-001 - resolves the pending verification gap.\n"
    assert auth_module.extract_spec_links(md)


def test_extract_spec_links_normal_section_returns_links(auth_module):
    """T11 -- a normal section with real citations returns the links."""
    md = (
        "## Specification Links\n\n"
        "- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge authority.\n"
        "- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - testing gate.\n"
    )
    assert auth_module.extract_spec_links(md) == [
        "GOV-FILE-BRIDGE-AUTHORITY-001",
        "DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001",
    ]


def test_create_authorization_packet_accepts_target_paths_heading_proposal(auth_module, tmp_path):
    """T12 -- end-to-end: a GO'd proposal using the `## target_paths` heading
    form (not the inline JSON) yields a valid authorization packet."""
    slug = "fixture-bridge"
    proposal = tmp_path / "bridge" / f"{slug}.md"
    proposal.parent.mkdir(parents=True, exist_ok=True)
    proposal.write_text(
        "NEW\n\n"
        f"# Fixture proposal {slug}\n\n"
        "## target_paths\n\n"
        "- `scripts/dummy.py`\n"
        "- `.gtkb-state/**` (state dir)\n\n"
        "## Specification Links\n\n"
        "- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.\n"
        "- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.\n\n"
        "## Requirement Sufficiency\n\nExisting requirements sufficient.\n\n"
        "## Verification Plan\n\n"
        "Run `python -m pytest platform_tests/scripts/test_dummy.py -q`.\n",
        encoding="utf-8",
    )
    _write_verdict(tmp_path, slug, version=2, verdict="GO")
    _ignore_retired_index_fixture(tmp_path, [f"Document: {slug}\nGO: bridge/{slug}-002.md\nNEW: bridge/{slug}.md\n"])
    packet = auth_module.create_authorization_packet(tmp_path, slug)
    assert packet["bridge_id"] == slug
    assert packet["target_path_globs"] == ["scripts/dummy.py", ".gtkb-state/**"]


# ---------------------------------------------------------------------------
# WI-3333 Bug 3: post-GO authorization-resume symmetry
# ---------------------------------------------------------------------------


def test_approved_files_for_go_authorizes_post_go_no_go(auth_module):
    """T13 -- chain NEW/NO-GO/REVISED/GO/NEW/NO-GO (latest is a post-GO NO-GO)
    -> authorized; returns the proposal under the GO and the GO file."""
    entry = auth_module.BridgeEntry(
        bridge_id="x",
        versions=[
            ("NO-GO", "bridge/x-006.md"),
            ("NEW", "bridge/x-005.md"),
            ("GO", "bridge/x-004.md"),
            ("REVISED", "bridge/x-003.md"),
            ("NO-GO", "bridge/x-002.md"),
            ("NEW", "bridge/x-001.md"),
        ],
    )
    assert auth_module.approved_files_for_go(entry) == ("bridge/x-003.md", "bridge/x-004.md")


def test_approved_files_for_go_raises_on_post_go_new_awaiting_review(auth_module):
    """T14 -- latest is a post-GO NEW report awaiting review -> raises."""
    entry = auth_module.BridgeEntry(
        bridge_id="x",
        versions=[
            ("NEW", "bridge/x-005.md"),
            ("GO", "bridge/x-004.md"),
            ("NEW", "bridge/x-001.md"),
        ],
    )
    with pytest.raises(auth_module.AuthorizationError, match="awaiting Loyal Opposition review"):
        auth_module.approved_files_for_go(entry)


def test_approved_files_for_go_raises_on_post_go_revised_awaiting_review(auth_module):
    """T15 -- latest is a post-GO REVISED report awaiting review -> raises."""
    entry = auth_module.BridgeEntry(
        bridge_id="x",
        versions=[
            ("REVISED", "bridge/x-007.md"),
            ("NO-GO", "bridge/x-006.md"),
            ("NEW", "bridge/x-005.md"),
            ("GO", "bridge/x-004.md"),
            ("NEW", "bridge/x-001.md"),
        ],
    )
    with pytest.raises(auth_module.AuthorizationError, match="awaiting Loyal Opposition review"):
        auth_module.approved_files_for_go(entry)


def test_approved_files_for_go_raises_on_post_go_verified(auth_module):
    """T16 -- latest is a post-GO VERIFIED (terminal) -> raises."""
    entry = auth_module.BridgeEntry(
        bridge_id="x",
        versions=[
            ("VERIFIED", "bridge/x-006.md"),
            ("NEW", "bridge/x-005.md"),
            ("GO", "bridge/x-004.md"),
            ("NEW", "bridge/x-001.md"),
        ],
    )
    with pytest.raises(auth_module.AuthorizationError, match="VERIFIED \\(terminal"):
        auth_module.approved_files_for_go(entry)


def test_approved_files_for_go_raises_on_latest_deferred(auth_module):
    """Latest DEFERRED is non-actionable even when an older GO exists."""
    entry = auth_module.BridgeEntry(
        bridge_id="x",
        versions=[
            ("DEFERRED", "bridge/x-006.md"),
            ("GO", "bridge/x-004.md"),
            ("NEW", "bridge/x-001.md"),
        ],
    )
    with pytest.raises(auth_module.AuthorizationError, match="DEFERRED"):
        auth_module.approved_files_for_go(entry)


def test_approved_files_for_go_raises_when_no_go_in_chain(auth_module):
    """T17 -- a chain with no GO anywhere -> raises."""
    entry = auth_module.BridgeEntry(
        bridge_id="x",
        versions=[("NO-GO", "bridge/x-002.md"), ("NEW", "bridge/x-001.md")],
    )
    with pytest.raises(auth_module.AuthorizationError, match="requires a GO in the bridge chain"):
        auth_module.approved_files_for_go(entry)


def test_approved_files_for_go_latest_is_go_unchanged(auth_module):
    """T18 -- latest IS the GO (today's happy path) -> unchanged behavior."""
    entry = auth_module.BridgeEntry(
        bridge_id="x",
        versions=[("GO", "bridge/x-002.md"), ("NEW", "bridge/x-001.md")],
    )
    assert auth_module.approved_files_for_go(entry) == ("bridge/x-001.md", "bridge/x-002.md")


def test_validate_packet_accepts_post_go_no_go_after_revised_report(auth_module, tmp_path):
    """T19 -- chain GO/NEW/NO-GO/REVISED/NO-GO: the latest is a NO-GO'd
    post-impl report and the pinned GO still authorizes resume; the
    intervening (non-latest) REVISED report is not a blocker."""
    _make_groundtruth_toml(tmp_path)
    slug, _, _ = _setup_simple_go_bridge(tmp_path)
    _begin_packet(auth_module, tmp_path, slug)
    for version, status in ((3, "NEW"), (4, "NO-GO"), (5, "REVISED"), (6, "NO-GO")):
        _write_verdict(tmp_path, slug, version=version, verdict=status)
    block = (
        f"Document: {slug}\n"
        f"NO-GO: bridge/{slug}-006.md\n"
        f"REVISED: bridge/{slug}-005.md\n"
        f"NO-GO: bridge/{slug}-004.md\n"
        f"NEW: bridge/{slug}-003.md\n"
        f"GO: bridge/{slug}-002.md\n"
        f"NEW: bridge/{slug}.md\n"
    )
    _ignore_retired_index_fixture(tmp_path, [block])
    packet = auth_module.activate_packet(tmp_path, slug)
    assert packet["bridge_id"] == slug


def test_validate_packet_raises_on_post_go_revised_report_awaiting_review(auth_module, tmp_path):
    """T20 -- the latest version is a post-GO REVISED report awaiting Loyal
    Opposition review -> _validate_packet raises."""
    _make_groundtruth_toml(tmp_path)
    slug, _, _ = _setup_simple_go_bridge(tmp_path)
    _begin_packet(auth_module, tmp_path, slug)
    for version, status in ((3, "NEW"), (4, "NO-GO"), (5, "REVISED")):
        _write_verdict(tmp_path, slug, version=version, verdict=status)
    block = (
        f"Document: {slug}\n"
        f"REVISED: bridge/{slug}-005.md\n"
        f"NO-GO: bridge/{slug}-004.md\n"
        f"NEW: bridge/{slug}-003.md\n"
        f"GO: bridge/{slug}-002.md\n"
        f"NEW: bridge/{slug}.md\n"
    )
    _ignore_retired_index_fixture(tmp_path, [block])
    with pytest.raises(auth_module.AuthorizationError, match="awaiting Loyal Opposition review"):
        auth_module.activate_packet(tmp_path, slug)


def test_create_authorization_packet_raises_on_latest_deferred_above_go(auth_module, tmp_path):
    """Latest DEFERRED above older GO must fail closed at packet creation."""
    _make_groundtruth_toml(tmp_path)
    slug, _, _ = _setup_simple_go_bridge(tmp_path)
    _write_verdict(tmp_path, slug, version=3, verdict="DEFERRED")
    block = f"Document: {slug}\nDEFERRED: bridge/{slug}-003.md\nGO: bridge/{slug}-002.md\nNEW: bridge/{slug}.md\n"
    _ignore_retired_index_fixture(tmp_path, [block])

    with pytest.raises(auth_module.AuthorizationError, match="DEFERRED"):
        auth_module.create_authorization_packet(tmp_path, slug)


def test_validate_packet_raises_when_bridge_becomes_latest_deferred(auth_module, tmp_path):
    """A previously valid packet cannot stay valid after latest DEFERRED."""
    _make_groundtruth_toml(tmp_path)
    slug, _, _ = _setup_simple_go_bridge(tmp_path)
    _begin_packet(auth_module, tmp_path, slug)
    _write_verdict(tmp_path, slug, version=3, verdict="DEFERRED")
    block = f"Document: {slug}\nDEFERRED: bridge/{slug}-003.md\nGO: bridge/{slug}-002.md\nNEW: bridge/{slug}.md\n"
    _ignore_retired_index_fixture(tmp_path, [block])

    with pytest.raises(auth_module.AuthorizationError, match="DEFERRED"):
        auth_module.activate_packet(tmp_path, slug)


def test_begin_creates_packet_for_post_go_no_go_thread(auth_module, tmp_path):
    """T21 -- end-to-end: create_authorization_packet succeeds for a thread
    whose latest status is a post-implementation-report NO-GO (the WI-3333
    Bug 3 keystone case that previously failed at begin)."""
    slug = "fixture-bridge"
    _write_proposal(tmp_path, slug, version=1, target_paths=["scripts/dummy.py", ".gtkb-state/**"])
    _write_verdict(tmp_path, slug, version=2, verdict="GO")
    _write_verdict(tmp_path, slug, version=3, verdict="NEW")
    _write_verdict(tmp_path, slug, version=4, verdict="NO-GO")
    _ignore_retired_index_fixture(
        tmp_path,
        [
            f"Document: {slug}\n"
            f"NO-GO: bridge/{slug}-004.md\n"
            f"NEW: bridge/{slug}-003.md\n"
            f"GO: bridge/{slug}-002.md\n"
            f"NEW: bridge/{slug}.md\n"
        ],
    )
    packet = auth_module.create_authorization_packet(tmp_path, slug)
    assert packet["bridge_id"] == slug
    assert packet["go_file"] == f"bridge/{slug}-002.md"
    assert packet["proposal_file"] == f"bridge/{slug}.md"


# ---------------------------------------------------------------------------
# WI-3353 IP-4: worktree-safe project_root_from_arg
# ---------------------------------------------------------------------------


def _build_worktree_project(tmp_path: Path) -> tuple[Path, Path]:
    """Build a synthetic GT-KB canonical checkout with a linked worktree under
    .claude/worktrees/test-wt. Returns (canonical_root, worktree_root). The
    worktree carries its own committed groundtruth.toml. Requires git.
    """
    ident = [
        "-c",
        "user.email=test@example.com",
        "-c",
        "user.name=test",
        "-c",
        "commit.gpgsign=false",
    ]
    canonical = tmp_path / "canonical"
    canonical.mkdir()
    (canonical / "groundtruth.toml").write_text("# synthetic GT-KB root\n", encoding="utf-8")
    subprocess.run(["git", "init"], cwd=canonical, check=True, capture_output=True)
    subprocess.run(["git", *ident, "add", "groundtruth.toml"], cwd=canonical, check=True, capture_output=True)
    subprocess.run(["git", *ident, "commit", "-m", "init"], cwd=canonical, check=True, capture_output=True)
    worktree = canonical / ".claude" / "worktrees" / "test-wt"
    worktree.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", *ident, "worktree", "add", "--detach", str(worktree)],
        cwd=canonical,
        check=True,
        capture_output=True,
    )
    return canonical, worktree


def test_project_root_from_arg_resolves_canonical_from_worktree(
    auth_module, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """WI-3353 IP-4: project_root_from_arg() with no --project-root resolves the
    canonical root when invoked from inside a linked worktree, so the
    implementation-start authorization packet is not scoped to the worktree's
    own scripts/ copy. An explicit --project-root still takes precedence."""
    if shutil.which("git") is None:
        pytest.skip("git not available on this system")
    canonical, worktree = _build_worktree_project(tmp_path)
    monkeypatch.delenv("GTKB_PROJECT_ROOT", raising=False)
    monkeypatch.chdir(worktree)
    assert auth_module.project_root_from_arg().resolve() == canonical.resolve()
    assert auth_module.project_root_from_arg(None).resolve() == canonical.resolve()
    # An explicit --project-root argument still wins.
    explicit = tmp_path / "explicit-root"
    explicit.mkdir()
    assert auth_module.project_root_from_arg(str(explicit)).resolve() == explicit.resolve()


# ---------------------------------------------------------------------------
# WI-4532: packet TTL shrink + gate-level liveness-coupling proof
# ---------------------------------------------------------------------------


def test_default_expiry_minutes_tracks_claim_max_hold(auth_module):
    """WI-4532: the impl-start packet TTL must not outlive the work-intent claim's
    2-hour hard cap, so an orphaned packet self-expires within the claim window
    instead of lingering for the former 8 hours. Fails closed if anyone re-widens
    DEFAULT_EXPIRY_MINUTES past the claim cap.
    """
    max_hold_minutes = auth_module.bridge_work_intent_registry.GO_IMPLEMENTATION_MAX_HOLD_SECONDS // 60
    assert max_hold_minutes >= auth_module.DEFAULT_EXPIRY_MINUTES
    assert auth_module.DEFAULT_EXPIRY_MINUTES == 120


def test_gate_rejects_orphaned_packet_via_work_intent_claim_check(auth_module, tmp_path):
    """WI-4532: the liveness coupling the owner asked for already exists at the gate.

    For a bridge with NO live work-intent claim (the orphaned-packet condition),
    work_intent_claim_block_reason returns a denial, so an orphaned packet cannot
    authorize a mutation regardless of its TTL window. This is the behavior the
    withdrawn broad _validate_packet orphan check would have duplicated (and which
    broke 14 verified tests); proving it here documents why the narrow design is
    sufficient.
    """
    slug = "orphan-liveness-bridge"
    # No claim acquired -> current_holder(slug) is None -> orphaned condition.
    reason = auth_module.work_intent_claim_block_reason(tmp_path, slug, "session-1")
    assert reason is not None
    assert "no active work-intent claim" in reason.lower()

    # Positive control: a live claim by the same session removes the block.
    auth_module.bridge_work_intent_registry.acquire(slug, "session-1", project_root=tmp_path)
    assert auth_module.work_intent_claim_block_reason(tmp_path, slug, "session-1") is None

    # Cross-scope denial preserved: a claim held by a DIFFERENT session still blocks
    # the caller -- the gate's liveness coupling is session-specific.
    other = "orphan-liveness-bridge-2"
    auth_module.bridge_work_intent_registry.acquire(other, "session-2", project_root=tmp_path)
    cross = auth_module.work_intent_claim_block_reason(tmp_path, other, "session-1")
    assert cross is not None
    assert "session-2" in cross
