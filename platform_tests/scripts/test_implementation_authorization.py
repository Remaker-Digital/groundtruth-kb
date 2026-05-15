"""Tests for scripts/implementation_authorization.py (Slice 4 IP-1/IP-2/IP-4).

Per ``bridge/gtkb-self-diagnostic-leak-closure-slice-4-implementation-gate-hygiene-003.md``
(Codex GO at -004). Covers:

- IP-1: filename-vs-document boundary-based parser hardening (per-bridge strict
  check in ``bridge_entry``; ``parse_bridge_index`` silently skips misattributed).
- IP-2: named-packet cache at ``by-bridge/<bridge-id>.json``, ``activate`` and
  ``list`` subcommands, legacy ``current.json``-only workflow preservation.

Uses isolated tmp_path project roots; the only dependency on the live repo is
the script import path.
"""

from __future__ import annotations

import importlib.util
import json
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


def _write_index(project_root: Path, blocks: list[str]) -> Path:
    """Write a bridge/INDEX.md with header comments + the supplied per-document blocks."""
    index_path = project_root / "bridge" / "INDEX.md"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    header = (
        "# Bridge Index\n\n"
        "<!-- header comment -->\n"
        "\n"
    )
    index_path.write_text(header + "\n\n".join(blocks) + "\n", encoding="utf-8")
    return index_path


def _write_proposal(project_root: Path, slug: str, version: int = 1, *, target_paths: list[str] | None = None) -> Path:
    """Write a minimal-compliant bridge proposal file."""
    if target_paths is None:
        target_paths = ["scripts/dummy.py"]
    suffix = "" if version == 1 else f"-{version:03d}"
    proposal_path = project_root / "bridge" / f"{slug}{suffix}.md"
    proposal_path.parent.mkdir(parents=True, exist_ok=True)
    target_paths_json = json.dumps(target_paths)
    body = (
        f"# Fixture proposal {slug} v{version}\n\n"
        f"target_paths: {target_paths_json}\n\n"
        f"## Specification Links\n\n"
        f"- GOV-FILE-BRIDGE-AUTHORITY-001 — bridge protocol.\n"
        f"- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — spec linkage.\n\n"
        f"## Requirement Sufficiency\n\n"
        f"Existing requirements sufficient.\n\n"
        f"## Verification Plan\n\n"
        f"Fixture verification plan: derived from the linked specs above.\n"
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
    block = (
        f"Document: {slug}\n"
        f"GO: bridge/{slug}-002.md\n"
        f"NEW: bridge/{slug}.md\n"
    )
    _write_index(project_root, [block])
    return slug, proposal, verdict


# ---------------------------------------------------------------------------
# IP-1: parser hardening
# ---------------------------------------------------------------------------


def test_parse_bridge_index_skips_misattributed_status_line(auth_module, tmp_path):
    """parse_bridge_index silently skips status lines whose filename does not
    match the enclosing Document name; per-bridge enforcement is in bridge_entry.
    """
    _setup_simple_go_bridge(tmp_path, slug="real-bridge")
    # Insert a bad block that mixes filenames
    bad_block = (
        "Document: doc-a\n"
        "NEW: bridge/doc-b-001.md\n"  # misattributed: filename is for doc-b
    )
    good_block = (
        "Document: real-bridge\n"
        "GO: bridge/real-bridge-002.md\n"
        "NEW: bridge/real-bridge.md\n"
    )
    _write_index(tmp_path, [bad_block, good_block])

    entries = auth_module.parse_bridge_index(tmp_path)
    # real-bridge present, doc-a has no valid versions so it's absent
    assert "real-bridge" in entries
    assert "doc-a" not in entries


def test_bridge_entry_raises_for_misattributed_status_under_queried_bridge(auth_module, tmp_path):
    """bridge_entry enforces per-bridge consistency: querying a bridge whose
    Document section has a misattributed status line raises.
    """
    _write_proposal(tmp_path, "doc-a", version=1, target_paths=["scripts/foo.py"])
    _write_verdict(tmp_path, "doc-a", version=2, verdict="GO")
    bad_block = (
        "Document: doc-a\n"
        "GO: bridge/doc-a-002.md\n"
        "NEW: bridge/some-other-doc-001.md\n"  # misattributed
    )
    _write_index(tmp_path, [bad_block])

    with pytest.raises(auth_module.AuthorizationError, match="does not match enclosing Document"):
        auth_module.bridge_entry(tmp_path, "doc-a")


def test_filename_matches_doc_accepts_v1_no_suffix_and_v2_plus_suffix(auth_module):
    """The boundary-based matcher accepts both v1 (no suffix) and v2+ (-NNN.md)
    forms, including for doc_ids that themselves end in -NNN.
    """
    matches = auth_module._filename_matches_doc
    # v1, no suffix
    assert matches("bridge/foo.md", "foo")
    # v2+ with suffix
    assert matches("bridge/foo-022.md", "foo")
    # doc_id ending in -001 (real-world case)
    assert matches("bridge/gtkb-single-harness-bridge-dispatcher-001.md", "gtkb-single-harness-bridge-dispatcher-001")
    assert matches("bridge/gtkb-single-harness-bridge-dispatcher-001-022.md", "gtkb-single-harness-bridge-dispatcher-001")
    # Mismatch: filename does not start with bridge/<doc_id>
    assert not matches("bridge/bar-001.md", "foo")
    # Mismatch: suffix not matching expected pattern
    assert not matches("bridge/foo-abc.md", "foo")


def test_bridge_entry_succeeds_for_well_formed_bridge(auth_module, tmp_path):
    """Baseline: bridge_entry returns the entry when all status lines match."""
    slug, _, _ = _setup_simple_go_bridge(tmp_path)
    entry = auth_module.bridge_entry(tmp_path, slug)
    assert entry.bridge_id == slug
    assert entry.latest_status == "GO"


# ---------------------------------------------------------------------------
# IP-2: named-packet cache + activate + list
# ---------------------------------------------------------------------------


def _make_groundtruth_toml(tmp_path: Path) -> None:
    """Create a minimal groundtruth.toml so groundtruth_db_path resolves."""
    (tmp_path / "groundtruth.toml").write_text(
        "[groundtruth]\ndb_path = \"groundtruth.db\"\n", encoding="utf-8"
    )


def _begin_packet(auth_module, tmp_path: Path, slug: str) -> dict[str, Any]:
    """Wrapper: create + write both current.json and named packet."""
    packet = auth_module.create_authorization_packet(tmp_path, slug)
    auth_module.write_packet(tmp_path, packet)
    auth_module.write_named_packet(tmp_path, packet, slug)
    return packet


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
    block_b = (
        "Document: bridge-b\n"
        "GO: bridge/bridge-b-002.md\n"
        "NEW: bridge/bridge-b.md\n"
    )
    block_a = (
        f"Document: {slug_a}\n"
        f"GO: bridge/{slug_a}-002.md\n"
        f"NEW: bridge/{slug_a}.md\n"
    )
    _write_index(tmp_path, [block_b, block_a])
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
    block = (
        f"Document: {slug}\n"
        f"NEW: bridge/{slug}-003.md\n"
        f"GO: bridge/{slug}-002.md\n"
        f"NEW: bridge/{slug}.md\n"
    )
    _write_index(tmp_path, [block])

    with pytest.raises(auth_module.AuthorizationError, match="awaiting Loyal Opposition review"):
        auth_module.activate_packet(tmp_path, slug)


def test_validate_packet_fails_with_pending_new_after_go(auth_module, tmp_path):
    """IP-C chain walk: chain [GO, NEW] -> fail with 'awaiting Loyal Opposition review'."""
    _make_groundtruth_toml(tmp_path)
    slug, _, _ = _setup_simple_go_bridge(tmp_path)
    _begin_packet(auth_module, tmp_path, slug)
    _write_proposal(tmp_path, slug, version=3, target_paths=["scripts/dummy.py"])
    block = (
        f"Document: {slug}\n"
        f"NEW: bridge/{slug}-003.md\n"
        f"GO: bridge/{slug}-002.md\n"
        f"NEW: bridge/{slug}.md\n"
    )
    _write_index(tmp_path, [block])
    with pytest.raises(auth_module.AuthorizationError, match="awaiting Loyal Opposition review"):
        auth_module.activate_packet(tmp_path, slug)


def test_validate_packet_fails_with_revised_anywhere_in_chain(auth_module, tmp_path):
    """IP-C chain walk: any REVISED in post-GO range -> fail with 'superseded by REVISED'."""
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
    _write_index(tmp_path, [block])
    with pytest.raises(auth_module.AuthorizationError, match="superseded by REVISED"):
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
    _write_index(tmp_path, [block])
    with pytest.raises(auth_module.AuthorizationError, match="VERIFIED \\(terminal"):
        auth_module.activate_packet(tmp_path, slug)


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
    _write_index(tmp_path, [block])
    packet = auth_module.activate_packet(tmp_path, slug)
    assert packet["bridge_id"] == slug


def test_list_enumerates_named_packets(auth_module, tmp_path):
    """list returns one row per named packet with bridge_id, expires_at, globs, valid."""
    _make_groundtruth_toml(tmp_path)
    _write_proposal(tmp_path, "bridge-a", version=1)
    _write_verdict(tmp_path, "bridge-a", version=2, verdict="GO")
    _write_proposal(tmp_path, "bridge-b", version=1)
    _write_verdict(tmp_path, "bridge-b", version=2, verdict="GO")
    _write_index(tmp_path, [
        "Document: bridge-a\nGO: bridge/bridge-a-002.md\nNEW: bridge/bridge-a.md\n",
        "Document: bridge-b\nGO: bridge/bridge-b-002.md\nNEW: bridge/bridge-b.md\n",
    ])
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


# ---------------------------------------------------------------------------
# F2-001 regression: legacy current.json-only workflow preserved
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


def test_packet_path_for_bridge_rejects_path_traversal_bridge_id(auth_module, tmp_path):
    """bridge_id with path separators or traversal segments is refused."""
    with pytest.raises(auth_module.AuthorizationError):
        auth_module.packet_path_for_bridge(tmp_path, "../escape")
    with pytest.raises(auth_module.AuthorizationError):
        auth_module.packet_path_for_bridge(tmp_path, "foo/bar")
    with pytest.raises(auth_module.AuthorizationError):
        auth_module.packet_path_for_bridge(tmp_path, "")
