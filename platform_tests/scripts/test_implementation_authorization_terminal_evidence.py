"""Terminal-evidence packet classification tests for WI-5694 cycle 1.

Per ``bridge/gtkb-wi5694-terminal-evidence-packet-validator-001.md``
(GO at -002). Covers the four owner-mandated regression cases T1-T4 from
DELIB-202667723.

Uses isolated tmp_path project roots and fixture bridge chains; the only
dependency on the live repo is the script import path.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "implementation_authorization.py"


@pytest.fixture(scope="module")
def auth_module():
    """Load implementation_authorization.py as a module without executing main()."""
    spec = importlib.util.spec_from_file_location("implementation_authorization_terminal_evidence", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["implementation_authorization_terminal_evidence"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(autouse=True)
def _select_fixture_worker_documents(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GTKB_HARNESS_NAME", "fixture")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_packet(
    bridge_id: str,
    expires_at: str,
    finalized_at: str,
    session_id: str = "session-test",
    go_file: str = "bridge/test-packet-001.md",
    packet_hash_val: str | None = None,
    target_path_globs: list[str] | None = None,
    with_impl_start: bool = True,
    hash_fn: Any = None,
) -> dict[str, Any]:
    """Build a schema-v3 implementation-start packet fixture."""
    packet: dict[str, Any] = {
        "bridge_id": bridge_id,
        "created_at": "2026-01-01T00:00:00Z",
        "expires_at": expires_at,
        "go_file": go_file,
        "latest_status": "GO",
        "proposal_file": "bridge/test-packet-001.md",
        "schema_version": 3,
        "target_path_globs": target_path_globs or [],
        "spec_links": [],
    }
    if with_impl_start:
        packet["implementation_start"] = {
            "bridge_id": bridge_id,
            "finalized_at": finalized_at,
            "schema_version": 1,
            "session_id": session_id,
            "target_path_globs": target_path_globs or [],
        }
    if packet_hash_val is None and hash_fn is not None:
        packet_hash_val = hash_fn(packet)
    if packet_hash_val:
        packet["packet_hash"] = packet_hash_val
    return packet


def _write_packet(project_root: Path, packet: dict[str, Any]) -> None:
    """Write a packet to the named-cache directory."""
    by_bridge = project_root / ".gtkb-state" / "implementation-authorizations" / "by-bridge"
    by_bridge.mkdir(parents=True, exist_ok=True)
    bridge_id = packet["bridge_id"]
    path = by_bridge / f"{bridge_id}.json"
    path.write_text(json.dumps(packet, indent=2), encoding="utf-8")


def _write_bridge_file(
    project_root: Path,
    slug: str,
    version: int,
    *,
    status: str = "NEW",
    responds_to: str | None = None,
) -> None:
    """Write a bridge file with proper metadata."""
    bridge_dir = project_root / "bridge"
    bridge_dir.mkdir(parents=True, exist_ok=True)
    path = bridge_dir / f"{slug}-{version:03d}.md"

    author = "prime-builder/fixture" if version == 1 else "loyal-opposition/fixture"

    lines = [
        status,
        f"author_identity: {author}",
        f"Document: {slug}",
        f"Version: {version:03d}",
    ]
    if responds_to is not None:
        lines.append(f"Responds to: {responds_to}")
    lines.append("")
    lines.append("# Test Bridge File")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _setup_bridge_chain(project_root: Path, slug: str) -> None:
    """Write a standard proposal + GO bridge chain."""
    _write_bridge_file(project_root, slug, 1, status="NEW")
    _write_bridge_file(
        project_root,
        slug,
        2,
        status="GO",
        responds_to=f"bridge/{slug}-001.md",
    )


# ---------------------------------------------------------------------------
# T1: Expired-but-live-at-implementation ACCEPT
# ---------------------------------------------------------------------------


def test_t1_expired_live_at_implementation_accept(auth_module, tmp_path):
    """DELIB-202667723 case 1: expired-but-live-at-implementation -> evidence-valid."""
    slug = "test-packet"
    _setup_bridge_chain(tmp_path, slug)

    now = datetime.now(UTC)
    past = now - timedelta(hours=2)
    earlier = now - timedelta(hours=3)

    packet = _make_packet(
        bridge_id=slug,
        expires_at=past.isoformat().replace("+00:00", "Z"),
        finalized_at=earlier.isoformat().replace("+00:00", "Z"),
        session_id="session-t1",
        go_file=f"bridge/{slug}-002.md",
        hash_fn=auth_module.packet_hash,
    )
    _write_packet(tmp_path, packet)

    result = auth_module.assess_packet_terminal_evidence(tmp_path, slug)

    assert result["evidence_valid"] is True, f"Expected evidence_valid=True, got {result}"
    assert result["expired"] is True
    assert result["live_at_implementation"] is True
    assert result["contested"] is False
    assert result["active_valid"] is False

    rows = auth_module.list_named_packets(tmp_path)
    assert len(rows) == 1
    row = rows[0]
    assert row["valid"] is False
    assert row["evidence_valid"] is True
    assert row["expired"] is True

    compact = auth_module.list_named_packets_compact(tmp_path)
    assert compact["valid_count"] == 0
    assert compact["evidence_valid_count"] == 1
    assert any(p.get("evidence_only") for p in compact["packets"])


# ---------------------------------------------------------------------------
# T2: Expired-before-implementation REJECT
# ---------------------------------------------------------------------------


def test_t2a_finalized_after_expires_reject(auth_module, tmp_path):
    """DELIB-202667723 case 2a: finalized_at > expires_at -> evidence_valid=False."""
    slug = "test-packet-t2a"
    _setup_bridge_chain(tmp_path, slug)

    now = datetime.now(UTC)
    expires = now - timedelta(hours=3)
    finalized = now - timedelta(hours=1)

    packet = _make_packet(
        bridge_id=slug,
        expires_at=expires.isoformat().replace("+00:00", "Z"),
        finalized_at=finalized.isoformat().replace("+00:00", "Z"),
        session_id="session-t2a",
        go_file=f"bridge/{slug}-002.md",
        hash_fn=auth_module.packet_hash,
    )
    _write_packet(tmp_path, packet)

    result = auth_module.assess_packet_terminal_evidence(tmp_path, slug)

    assert result["evidence_valid"] is False
    assert result["live_at_implementation"] is False
    assert any("not live at implementation" in r.lower() for r in result["reasons"])


def test_t2b_no_implementation_start_reject(auth_module, tmp_path):
    """DELIB-202667723 case 2b: no implementation_start block -> evidence_valid=False."""
    slug = "test-packet-t2b"
    _setup_bridge_chain(tmp_path, slug)

    now = datetime.now(UTC)
    future = now + timedelta(hours=4)

    packet = _make_packet(
        bridge_id=slug,
        expires_at=future.isoformat().replace("+00:00", "Z"),
        finalized_at="2026-01-01T00:00:00Z",
        session_id="session-t2b",
        go_file=f"bridge/{slug}-002.md",
        with_impl_start=False,
        hash_fn=auth_module.packet_hash,
    )
    _write_packet(tmp_path, packet)

    result = auth_module.assess_packet_terminal_evidence(tmp_path, slug)

    assert result["evidence_valid"] is False
    assert result["live_at_implementation"] is False
    assert any("no implementation_start" in r.lower() for r in result["reasons"])


# ---------------------------------------------------------------------------
# T3: Contested REJECT
# ---------------------------------------------------------------------------


def test_t3_contested_reject(auth_module, tmp_path, monkeypatch):
    """DELIB-202667723 case 3: competing claim -> evidence_valid=False, contested=True."""
    slug = "test-packet-t3"
    _setup_bridge_chain(tmp_path, slug)

    def competing_holder(bridge_id: str, **kwargs) -> dict[str, Any] | None:
        return {"session_id": "competing-session", "bridge_id": bridge_id}

    monkeypatch.setattr(
        auth_module.bridge_work_intent_registry,
        "current_holder",
        competing_holder,
    )

    now = datetime.now(UTC)
    future = now + timedelta(hours=4)
    earlier = now - timedelta(hours=1)

    packet = _make_packet(
        bridge_id=slug,
        expires_at=future.isoformat().replace("+00:00", "Z"),
        finalized_at=earlier.isoformat().replace("+00:00", "Z"),
        session_id="packet-session",
        go_file=f"bridge/{slug}-002.md",
        hash_fn=auth_module.packet_hash,
    )
    _write_packet(tmp_path, packet)

    result = auth_module.assess_packet_terminal_evidence(tmp_path, slug)

    assert result["evidence_valid"] is False
    assert result["contested"] is True
    assert any("contested" in r.lower() for r in result["reasons"])


def test_t3_uncontested_accept(auth_module, tmp_path):
    """Same fixture minus competing claim -> evidence_valid=True."""
    slug = "test-packet-t3u"
    _setup_bridge_chain(tmp_path, slug)

    now = datetime.now(UTC)
    future = now + timedelta(hours=4)
    earlier = now - timedelta(hours=1)

    packet = _make_packet(
        bridge_id=slug,
        expires_at=future.isoformat().replace("+00:00", "Z"),
        finalized_at=earlier.isoformat().replace("+00:00", "Z"),
        session_id="packet-session",
        go_file=f"bridge/{slug}-002.md",
        hash_fn=auth_module.packet_hash,
    )
    _write_packet(tmp_path, packet)

    result = auth_module.assess_packet_terminal_evidence(tmp_path, slug)

    assert result["evidence_valid"] is True
    assert result["contested"] is False


def test_t3_registry_error_fails_closed(auth_module, tmp_path, monkeypatch):
    """DELIB-202667723 E5: registry read error -> evidence_valid=False."""
    slug = "test-packet-t3err"
    _setup_bridge_chain(tmp_path, slug)

    def registry_unavailable(*_args, **_kwargs):
        raise auth_module.bridge_work_intent_registry.WorkIntentRegistryError("fixture registry unavailable")

    monkeypatch.setattr(
        auth_module.bridge_work_intent_registry,
        "current_holder",
        registry_unavailable,
    )

    now = datetime.now(UTC)
    future = now + timedelta(hours=4)
    earlier = now - timedelta(hours=1)

    packet = _make_packet(
        bridge_id=slug,
        expires_at=future.isoformat().replace("+00:00", "Z"),
        finalized_at=earlier.isoformat().replace("+00:00", "Z"),
        session_id="packet-session",
        go_file=f"bridge/{slug}-002.md",
        hash_fn=auth_module.packet_hash,
    )
    _write_packet(tmp_path, packet)

    result = auth_module.assess_packet_terminal_evidence(tmp_path, slug)

    assert result["evidence_valid"] is False
    assert any("registry" in r.lower() or "unavailable" in r.lower() for r in result["reasons"])


# ---------------------------------------------------------------------------
# T4: Live-packet behavior unchanged
# ---------------------------------------------------------------------------


def test_t4a_unexpired_packet_passes_load(auth_module, tmp_path, monkeypatch):
    """T4a: unexpired packet passes load_named_packet/validate_targets."""
    slug = "test-packet-t4a"
    _setup_bridge_chain(tmp_path, slug)

    monkeypatch.setattr(
        auth_module.bridge_work_intent_registry,
        "current_claimed_bridge_id",
        lambda session_id, project_root=None: None,
    )

    now = datetime.now(UTC)
    future = now + timedelta(hours=4)
    earlier = now - timedelta(hours=1)

    packet = _make_packet(
        bridge_id=slug,
        expires_at=future.isoformat().replace("+00:00", "Z"),
        finalized_at=earlier.isoformat().replace("+00:00", "Z"),
        session_id="session-t4a",
        go_file=f"bridge/{slug}-002.md",
        target_path_globs=["test.py"],
        hash_fn=auth_module.packet_hash,
    )
    _write_packet(tmp_path, packet)

    loaded = auth_module.load_named_packet(tmp_path, slug)
    assert loaded["bridge_id"] == slug

    val_result = auth_module.validate_targets(tmp_path, ["test.py"], session_id="session-t4a")
    assert "packet" in val_result and "targets" in val_result


def test_t4b_expired_packet_rejected_on_active_path(auth_module, tmp_path):
    """T4b: expired packet is still rejected on active-authority path."""
    slug = "test-packet-t4b"
    _setup_bridge_chain(tmp_path, slug)

    now = datetime.now(UTC)
    past = now - timedelta(hours=2)
    earlier = now - timedelta(hours=3)

    packet = _make_packet(
        bridge_id=slug,
        expires_at=past.isoformat().replace("+00:00", "Z"),
        finalized_at=earlier.isoformat().replace("+00:00", "Z"),
        session_id="session-t4b",
        go_file=f"bridge/{slug}-002.md",
        target_path_globs=["test.py"],
        hash_fn=auth_module.packet_hash,
    )
    _write_packet(tmp_path, packet)

    with pytest.raises(auth_module.AuthorizationError, match="expired"):
        auth_module.load_named_packet(tmp_path, slug)

    rows = auth_module.list_named_packets(tmp_path)
    row = rows[0]
    assert row["valid"] is False
    assert "expired" in row["error"].lower()


def test_t4c_default_expiry_unchanged(auth_module):
    """T4c: DEFAULT_EXPIRY_MINUTES remains 120."""
    assert auth_module.DEFAULT_EXPIRY_MINUTES == 120


def test_t4d_list_valid_semantics_unchanged(auth_module, tmp_path):
    """T4d: list valid semantics unchanged with evidence fields."""
    slug = "test-packet-t4d"
    _setup_bridge_chain(tmp_path, slug)

    now = datetime.now(UTC)
    future = now + timedelta(hours=4)
    earlier = now - timedelta(hours=1)

    packet = _make_packet(
        bridge_id=slug,
        expires_at=future.isoformat().replace("+00:00", "Z"),
        finalized_at=earlier.isoformat().replace("+00:00", "Z"),
        session_id="session-t4d",
        go_file=f"bridge/{slug}-002.md",
        target_path_globs=["test.py"],
        hash_fn=auth_module.packet_hash,
    )
    _write_packet(tmp_path, packet)

    rows = auth_module.list_named_packets(tmp_path)
    row = rows[0]
    assert row["valid"] is True
    assert row["evidence_valid"] is True
    assert "path" in row
    assert "bridge_id" in row
    assert "expires_at" in row
    assert "target_path_globs" in row
    assert "error" in row

    compact = auth_module.list_named_packets_compact(tmp_path)
    assert compact["valid_count"] == 1
    valid_packet = compact["packets"][0]
    assert valid_packet["valid"] is True
    assert "evidence_valid" in valid_packet
    assert "evidence_error" in valid_packet
    assert "expired" in valid_packet
