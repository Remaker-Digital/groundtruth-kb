"""Tests for WI-4527 GO-implementation claim auto-extension.

These cover the bounded, fail-soft ``maybe_auto_extend`` registry helper and the
invariant that the implementation-start gate's allow/deny verdict is unchanged
by the auto-extend side-effect.

Authority: ``bridge/gtkb-wi4527-go-claim-auto-extend-003.md`` (GO at ``-004``);
WI-4527; ``PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-2``.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import importlib.util
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
REGISTRY_PATH = SCRIPTS_DIR / "bridge_work_intent_registry.py"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _registry():
    return _load_module(REGISTRY_PATH, "bridge_work_intent_registry")


def _write_index(root: Path, statuses: dict[str, str]) -> None:
    bridge = root / "bridge"
    bridge.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    for slug, status in statuses.items():
        version = "002" if status == "GO" else "001"
        lines.extend([f"Document: {slug}", f"{status}: bridge/{slug}-{version}.md", ""])
    (bridge / "INDEX.md").write_text("\n".join(lines), encoding="utf-8")


def _write_prime_marker(root: Path) -> None:
    """Provide owner-declared interactive Prime evidence for go_implementation claims.

    WI-4534 Slice A made ``go_implementation`` claims Prime-only; these tests
    acquire such a claim, so each must present positive Prime evidence via the
    hermetic in-``project_root`` interactive marker. See the equivalent helper in
    ``test_go_impl_claim_timebox.py``.
    """
    import json

    marker_dir = root / ".claude" / "session"
    marker_dir.mkdir(parents=True, exist_ok=True)
    (marker_dir / "active-session-role.json").write_text(
        json.dumps({"role": "prime-builder", "session_id": "marker-session"}), encoding="utf-8"
    )


# --- Registry-level behavior -------------------------------------------------


def test_auto_extend_when_deadline_near(tmp_path: Path, monkeypatch) -> None:
    """Auto-extend fires for an active holder near the deadline (WI-4527 root cause)."""
    registry = _registry()
    base = datetime(2026, 6, 13, 0, 0, tzinfo=UTC)
    now = {"value": base}
    monkeypatch.setattr(registry, "now_utc", lambda: now["value"])
    _write_index(tmp_path, {"go-thread": "GO"})
    _write_prime_marker(tmp_path)

    assert registry.acquire("go-thread", "session-a", project_root=tmp_path)
    # Advance to within the auto-extend threshold of the 00:30 deadline (5 min left).
    now["value"] = base + timedelta(minutes=25)

    result = registry.maybe_auto_extend("go-thread", "session-a", project_root=tmp_path)

    assert result is not None
    assert result["implementation_deadline"] == "2026-06-13T01:00:00Z"
    assert result["extensions_used"] == 1
    holder = registry.current_holder("go-thread", project_root=tmp_path)
    assert holder["implementation_deadline"] == "2026-06-13T01:00:00Z"


def test_no_extend_when_deadline_far(tmp_path: Path, monkeypatch) -> None:
    """No-op when the deadline is NOT near (no per-edit runaway)."""
    registry = _registry()
    base = datetime(2026, 6, 13, 0, 0, tzinfo=UTC)
    monkeypatch.setattr(registry, "now_utc", lambda: base)
    _write_index(tmp_path, {"go-thread": "GO"})
    _write_prime_marker(tmp_path)

    assert registry.acquire("go-thread", "session-a", project_root=tmp_path)
    # now == base: 30 min remaining, above the 10 min threshold.
    result = registry.maybe_auto_extend("go-thread", "session-a", project_root=tmp_path)

    assert result is None
    holder = registry.current_holder("go-thread", project_root=tmp_path)
    assert holder["implementation_deadline"] == "2026-06-13T00:30:00Z"
    assert holder["extensions_used"] == 0


def test_no_extend_for_non_holder(tmp_path: Path, monkeypatch) -> None:
    """No-op (no raise) for a non-holder session — no unauthorized extension."""
    registry = _registry()
    base = datetime(2026, 6, 13, 0, 0, tzinfo=UTC)
    now = {"value": base}
    monkeypatch.setattr(registry, "now_utc", lambda: now["value"])
    _write_index(tmp_path, {"go-thread": "GO"})
    _write_prime_marker(tmp_path)

    assert registry.acquire("go-thread", "session-a", project_root=tmp_path)
    now["value"] = base + timedelta(minutes=25)

    result = registry.maybe_auto_extend("go-thread", "session-b", project_root=tmp_path)

    assert result is None
    holder = registry.current_holder("go-thread", project_root=tmp_path)
    assert holder["session_id"] == "session-a"
    assert holder["implementation_deadline"] == "2026-06-13T00:30:00Z"
    assert holder["extensions_used"] == 0


def test_no_extend_for_draft_claim(tmp_path: Path, monkeypatch) -> None:
    """No-op for a draft (non-GO-implementation) claim."""
    registry = _registry()
    base = datetime(2026, 6, 13, 0, 0, tzinfo=UTC)
    monkeypatch.setattr(registry, "now_utc", lambda: base)
    _write_index(tmp_path, {"draft-thread": "NEW"})

    assert registry.acquire("draft-thread", "session-a", project_root=tmp_path)
    before = registry.current_holder("draft-thread", project_root=tmp_path)
    assert before["claim_kind"] == registry.CLAIM_KIND_DRAFT

    result = registry.maybe_auto_extend("draft-thread", "session-a", project_root=tmp_path)

    assert result is None
    after = registry.current_holder("draft-thread", project_root=tmp_path)
    assert after["ttl_expires_at"] == before["ttl_expires_at"]
    assert after["extensions_used"] == 0


def test_auto_extend_fail_soft_at_cap(tmp_path: Path, monkeypatch) -> None:
    """Fail-soft at the 2 h cap (GOV bound preserved): returns None, no raise."""
    registry = _registry()
    base = datetime(2026, 6, 13, 0, 0, tzinfo=UTC)
    now = {"value": base}
    monkeypatch.setattr(registry, "now_utc", lambda: now["value"])
    _write_index(tmp_path, {"go-thread": "GO"})
    _write_prime_marker(tmp_path)

    assert registry.acquire("go-thread", "session-a", project_root=tmp_path)
    # Drive the deadline to the 02:00 cap via explicit extends (00:30 -> 02:00).
    for _ in range(3):
        registry.extend("go-thread", "session-a", project_root=tmp_path)
    capped_holder = registry.current_holder("go-thread", project_root=tmp_path)
    assert capped_holder["implementation_deadline"] == "2026-06-13T02:00:00Z"

    # Near the (now-capped) deadline, a further auto-extend must fail soft.
    now["value"] = base + timedelta(hours=1, minutes=55)
    result = registry.maybe_auto_extend("go-thread", "session-a", project_root=tmp_path)

    assert result is None
    status = registry.claim_status("go-thread", project_root=tmp_path)
    assert status["extension_capped"] is True
    assert status["implementation_deadline"] == "2026-06-13T02:00:00Z"


def test_repeated_auto_extend_bounded_by_max_hold(tmp_path: Path, monkeypatch) -> None:
    """Repeated near-deadline auto-extends never push past acquired_at + MAX_HOLD."""
    registry = _registry()
    base = datetime(2026, 6, 13, 0, 0, tzinfo=UTC)
    now = {"value": base}
    monkeypatch.setattr(registry, "now_utc", lambda: now["value"])
    _write_index(tmp_path, {"go-thread": "GO"})
    _write_prime_marker(tmp_path)

    assert registry.acquire("go-thread", "session-a", project_root=tmp_path)
    cap = base + timedelta(seconds=registry.GO_IMPLEMENTATION_MAX_HOLD_SECONDS)

    for _ in range(6):
        holder = registry.current_holder("go-thread", project_root=tmp_path)
        deadline = datetime.fromisoformat(holder["implementation_deadline"].replace("Z", "+00:00"))
        # Step to within the threshold of the current deadline and auto-extend.
        now["value"] = deadline - timedelta(minutes=5)
        registry.maybe_auto_extend("go-thread", "session-a", project_root=tmp_path)
        current = registry.current_holder("go-thread", project_root=tmp_path)
        current_deadline = datetime.fromisoformat(current["implementation_deadline"].replace("Z", "+00:00"))
        assert current_deadline <= cap

    # Final state is pinned exactly at the cap.
    final = registry.current_holder("go-thread", project_root=tmp_path)
    assert final["implementation_deadline"] == "2026-06-13T02:00:00Z"


# --- Gate-verdict invariant --------------------------------------------------


def test_gate_verdict_unchanged_when_auto_extend_raises(monkeypatch) -> None:
    """PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001: the impl-start gate's
    allow/deny verdict on an authorized edit is identical whether the auto-extend
    side-effect raises or succeeds (the error is swallowed; the edit is allowed).
    """
    import scripts.bridge_work_intent_registry as registry_pkg
    import scripts.implementation_start_gate as gate

    # Force the gate down the authorized path with a protected, mutating target.
    monkeypatch.setattr(gate, "changed_paths", lambda payload: (["scripts/foo.py"], True))
    monkeypatch.setattr(gate, "is_protected_path", lambda path: True)
    monkeypatch.setattr(gate, "resolve_work_intent_session_id", lambda payload: "sess")
    monkeypatch.setattr(
        gate, "validate_targets", lambda root, protected, session_id=None: {"packet": {"bridge_id": "thread"}}
    )
    monkeypatch.setattr(gate, "work_intent_claim_block_reason", lambda root, bridge_id, session_id: None)

    # Baseline: auto-extend succeeds (returns a record) -> allow.
    monkeypatch.setattr(registry_pkg, "maybe_auto_extend", lambda *a, **k: {"ok": True})
    allow_baseline = gate.gate_decision({})

    # Side-effect raises -> still allow; verdict must be byte-identical.
    def _raise(*_a, **_k):
        raise RuntimeError("boom")

    monkeypatch.setattr(registry_pkg, "maybe_auto_extend", _raise)
    allow_when_raises = gate.gate_decision({})

    assert allow_baseline == {}
    assert allow_when_raises == {}
    assert allow_when_raises == allow_baseline
