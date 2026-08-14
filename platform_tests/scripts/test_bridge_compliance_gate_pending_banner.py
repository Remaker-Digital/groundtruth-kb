"""Pending-proposal banner names the right thread, or none (WI-6216 D1).

Landed by bridge/gtkb-wi6216-tool-and-gate-defect-corpus-slice-1 (GO at -006).

The banner misdirected implementers ten times in a single session, each time
citing an unrelated thread while a live implementation-start packet authorized
the exact path being edited. These tests pin the four sub-repairs: live-packet
suppression, recency preference, root-anchored matching, and parked-thread aging.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import time
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
HOOK_PATH = PROJECT_ROOT / ".claude" / "hooks" / "bridge-compliance-gate.py"


def _load_hook():
    """Import the hook module by path; it is guarded by __main__ so this is safe."""
    spec = importlib.util.spec_from_file_location("bridge_compliance_gate_under_test", HOOK_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


gate = _load_hook()


def _bridge_file(root: Path, slug: str, version: int, age_days: float = 0.0) -> Path:
    bridge = root / "bridge"
    bridge.mkdir(parents=True, exist_ok=True)
    path = bridge / f"{slug}-{version:03d}.md"
    path.write_text("NO-GO\n\n# fixture\n", encoding="utf-8")
    if age_days:
        stamp = time.time() - (age_days * 86400)
        import os

        os.utime(path, (stamp, stamp))
    return path


def _packet(root: Path, slug: str, globs: list[str], *, expired: bool = False) -> Path:
    packet_dir = root / ".gtkb-state" / "implementation-authorizations" / "by-bridge"
    packet_dir.mkdir(parents=True, exist_ok=True)
    import datetime as dt

    offset = -1 if expired else 1
    expires = dt.datetime.now(dt.UTC) + dt.timedelta(hours=offset)
    path = packet_dir / f"{slug}.json"
    path.write_text(
        json.dumps(
            {
                "bridge_id": slug,
                "expires_at": expires.isoformat().replace("+00:00", "Z"),
                "latest_status": "GO",
                "target_path_globs": globs,
            }
        ),
        encoding="utf-8",
    )
    return path


@pytest.fixture
def records(monkeypatch):
    """Install a settable pending-proposal record set."""
    holder: dict[str, list] = {"records": []}
    monkeypatch.setattr(gate, "_pending_proposal_target_records", lambda _root: holder["records"])
    return holder


# --- (c) root-anchored matching -------------------------------------------------


def test_suffix_collision_does_not_claim_the_path(records, tmp_path):
    """The prior endswith() let an unrelated target claim a path by suffix."""
    records["records"] = [{"document": "unrelated-thread", "status": "NO-GO", "target_paths": ["parity.py"]}]
    _bridge_file(tmp_path, "unrelated-thread", 1)
    assert gate._pending_proposal_ask_reason(tmp_path, "scripts/check_harness_parity.py") is None


def test_exact_target_claims_the_path(records, tmp_path):
    records["records"] = [{"document": "owning-thread", "status": "NEW", "target_paths": ["scripts/impl.py"]}]
    _bridge_file(tmp_path, "owning-thread", 1)
    reason = gate._pending_proposal_ask_reason(tmp_path, "scripts/impl.py")
    assert reason is not None and "owning-thread" in reason


def test_glob_target_claims_the_path(records, tmp_path):
    records["records"] = [{"document": "glob-thread", "status": "NEW", "target_paths": ["scripts/*.py"]}]
    _bridge_file(tmp_path, "glob-thread", 1)
    assert gate._pending_proposal_ask_reason(tmp_path, "scripts/impl.py") is not None


def test_directory_prefix_claims_children(records, tmp_path):
    records["records"] = [{"document": "dir-thread", "status": "NEW", "target_paths": ["scripts"]}]
    _bridge_file(tmp_path, "dir-thread", 1)
    assert gate._pending_proposal_ask_reason(tmp_path, "scripts/nested/impl.py") is not None


# --- (a) live-packet suppression ------------------------------------------------


def test_live_packet_suppresses_the_banner(records, tmp_path):
    """The reproduced defect: authorized edit, unrelated thread banners anyway."""
    records["records"] = [{"document": "parked-thread", "status": "NO-GO", "target_paths": ["scripts/impl.py"]}]
    _bridge_file(tmp_path, "parked-thread", 1)
    _packet(tmp_path, "authorized-thread", ["scripts/impl.py"])
    assert gate._pending_proposal_ask_reason(tmp_path, "scripts/impl.py") is None


def test_expired_packet_does_not_suppress(records, tmp_path):
    records["records"] = [{"document": "parked-thread", "status": "NO-GO", "target_paths": ["scripts/impl.py"]}]
    _bridge_file(tmp_path, "parked-thread", 1)
    _packet(tmp_path, "stale-thread", ["scripts/impl.py"], expired=True)
    assert gate._pending_proposal_ask_reason(tmp_path, "scripts/impl.py") is not None


def test_packet_for_a_different_path_does_not_suppress(records, tmp_path):
    records["records"] = [{"document": "parked-thread", "status": "NEW", "target_paths": ["scripts/impl.py"]}]
    _bridge_file(tmp_path, "parked-thread", 1)
    _packet(tmp_path, "other-thread", ["docs/*.md"])
    assert gate._pending_proposal_ask_reason(tmp_path, "scripts/impl.py") is not None


# --- (b) recency preference -----------------------------------------------------


def test_most_recently_active_thread_is_named(records, tmp_path):
    records["records"] = [
        {"document": "older-thread", "status": "NEW", "target_paths": ["scripts/impl.py"]},
        {"document": "newer-thread", "status": "NEW", "target_paths": ["scripts/impl.py"]},
    ]
    _bridge_file(tmp_path, "older-thread", 1, age_days=10)
    _bridge_file(tmp_path, "newer-thread", 1)
    reason = gate._pending_proposal_ask_reason(tmp_path, "scripts/impl.py")
    assert "newer-thread" in reason
    assert "older-thread" not in reason


# --- (d) parked-thread aging ----------------------------------------------------


def test_long_parked_no_go_does_not_claim(records, tmp_path):
    records["records"] = [{"document": "ancient-thread", "status": "NO-GO", "target_paths": ["scripts/impl.py"]}]
    _bridge_file(tmp_path, "ancient-thread", 1, age_days=45)
    assert gate._pending_proposal_ask_reason(tmp_path, "scripts/impl.py") is None


def test_recent_no_go_still_claims(records, tmp_path):
    """Aging must not silence a live NO-GO; only long-parked ones."""
    records["records"] = [{"document": "recent-thread", "status": "NO-GO", "target_paths": ["scripts/impl.py"]}]
    _bridge_file(tmp_path, "recent-thread", 1, age_days=2)
    reason = gate._pending_proposal_ask_reason(tmp_path, "scripts/impl.py")
    assert reason is not None and "recent-thread" in reason


def test_long_parked_new_is_not_aged_out(records, tmp_path):
    """NEW/REVISED are live review work; aging applies to NO-GO only."""
    records["records"] = [{"document": "old-new-thread", "status": "NEW", "target_paths": ["scripts/impl.py"]}]
    _bridge_file(tmp_path, "old-new-thread", 1, age_days=60)
    assert gate._pending_proposal_ask_reason(tmp_path, "scripts/impl.py") is not None
