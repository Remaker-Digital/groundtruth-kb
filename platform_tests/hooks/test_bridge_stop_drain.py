# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for .claude/hooks/bridge-stop-drain.py -- role-aware bridge
active-session auto-drain.

WI-3359 -- bridge/gtkb-bridge-active-session-autodrain-005.md (Codex GO at -006).

Specification coverage (``drain_decision`` is the documented testable core,
deliberately kept pure of stdin parsing so tests can drive it directly):

- ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 -- the drain closes the
  owner-out-of-loop dispatch gap by blocking turn-end when role-actionable
  bridge work is pending.
- DCL-SMART-POLLER-AUTO-TRIGGER-001 -- actionable bridge state triggers the
  drain automatically (no owner prompt).
- GOV-HARNESS-ROLE-PORTABILITY-001 -- actionability is role-bound; the drain
  resolves the session's durable operating role before selecting actionable
  statuses (Prime drains GO/NO-GO; LO drains NEW/REVISED).
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 -- this suite derives from
  the linked specs and executes against the implementation.

harness_roles and groundtruth_kb are imported by ``drain_decision`` from the
real checkout (they are code, not fixture data); the fixture project roots
supply only the data files the drain reads -- harness-state/*.json,
bridge/INDEX.md, memory/pending-owner-decisions.md, and the stop-drain state
directory.
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import ModuleType

_REPO_ROOT = Path(__file__).resolve().parents[2]
_HOOK_PATH = _REPO_ROOT / ".claude" / "hooks" / "bridge-stop-drain.py"

# drain_decision imports harness_roles (scripts/) and groundtruth_kb
# (groundtruth-kb/src/) from the real checkout. Put both on sys.path so the
# in-process tests can satisfy those imports against project code while the
# fixture project roots remain the source of the *data* the drain reads.
for _rel in ("scripts", "groundtruth-kb/src"):
    _candidate = _REPO_ROOT / _rel
    if _candidate.is_dir() and str(_candidate) not in sys.path:
        sys.path.insert(0, str(_candidate))


def _load_hook() -> ModuleType:
    """Load .claude/hooks/bridge-stop-drain.py as a module. The hyphenated
    filename cannot be imported by name, so importlib loads it by path."""
    assert _HOOK_PATH.is_file(), f"Expected hook at {_HOOK_PATH}"
    module_name = "bridge_stop_drain_under_test"
    if module_name in sys.modules:
        return sys.modules[module_name]
    spec = importlib.util.spec_from_file_location(module_name, _HOOK_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _make_project(root: Path, *, claude_role: str, codex_role: str) -> Path:
    """Create a fixture GT-KB project root with harness-state identity + role
    maps and an empty bridge/ dir. The identity map mirrors the live project
    (claude=B, codex=A); the role map is parameterised per test."""
    (root / "bridge").mkdir(parents=True, exist_ok=True)
    harness_state = root / "harness-state"
    harness_state.mkdir(exist_ok=True)
    (harness_state / "harness-identities.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": {"claude": {"id": "B"}, "codex": {"id": "A"}},
            }
        ),
        encoding="utf-8",
    )
    (harness_state / "role-assignments.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": {
                    "B": {"role": claude_role, "harness_type": "claude"},
                    "A": {"role": codex_role, "harness_type": "codex"},
                },
            }
        ),
        encoding="utf-8",
    )
    return root


def _write_index(root: Path, docs: list[tuple[str, str, int]]) -> None:
    """Write bridge/INDEX.md plus the referenced bridge files for each
    (document_name, top_status, top_version) tuple.

    compute_actionable_pending excludes documents whose top file is missing
    (LC6), so every referenced file is created on disk.
    """
    bridge = root / "bridge"
    blocks: list[str] = []
    for name, status, version in docs:
        (bridge / f"{name}-001.md").write_text("# stub\n", encoding="utf-8")
        block = [f"Document: {name}"]
        if version == 1:
            block.append(f"{status}: bridge/{name}-001.md")
        else:
            (bridge / f"{name}-{version:03d}.md").write_text("# stub\n", encoding="utf-8")
            block.append(f"{status}: bridge/{name}-{version:03d}.md")
            block.append(f"NEW: bridge/{name}-001.md")
        blocks.append("\n".join(block))
    (bridge / "INDEX.md").write_text("\n\n".join(blocks) + "\n", encoding="utf-8")


def _drain_state(root: Path, session_id: str) -> dict:
    """Read the per-session stop-drain state file written by drain_decision."""
    path = root / ".gtkb-state" / "bridge-poller" / "stop-drain" / f"{session_id}.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def _write_pending_decision(root: Path, *, status: str, asked_at: datetime) -> None:
    """Write memory/pending-owner-decisions.md with a single decision block in
    the format _owner_decision_pending parses (- id / status / asked_at)."""
    memory = root / "memory"
    memory.mkdir(parents=True, exist_ok=True)
    asked = asked_at.isoformat().replace("+00:00", "Z")
    (memory / "pending-owner-decisions.md").write_text(
        "# Pending owner decisions\n\n"
        "- id: DECISION-9001\n"
        f"  status: {status}\n"
        f"  asked_at: {asked}\n",
        encoding="utf-8",
    )


def _install_heartbeat_stub(root: Path) -> Path:
    """Install a stub scripts/active_session_heartbeat.py in the fixture root
    that records its argv to a marker file. _rearm_heartbeat invokes the
    project-root copy of this script by path (not by import), so a fixture
    copy is enough to observe the re-arm."""
    scripts = root / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    (scripts / "active_session_heartbeat.py").write_text(
        "import sys\n"
        "from pathlib import Path\n"
        "marker = Path(__file__).resolve().parents[1] / '.heartbeat-rearm-marker'\n"
        "marker.write_text(' '.join(sys.argv[1:]), encoding='utf-8')\n",
        encoding="utf-8",
    )
    return root / ".heartbeat-rearm-marker"


def _write_transcript(
    root: Path, *, last_user_text: str, trailing_tool_result: bool = False
) -> Path:
    """Write a minimal Claude Code JSONL transcript whose last real owner
    message is ``last_user_text``. When ``trailing_tool_result`` is set a
    tool-result-only user event (an agent-loop continuation) is appended after
    it, so a test can prove _last_user_message_text skips tool_result
    continuations and still finds the real owner message."""
    events: list[dict] = [
        {"type": "user", "message": {"role": "user", "content": "an earlier prompt"}},
        {"type": "assistant", "message": {"role": "assistant", "content": "an earlier reply"}},
        {"type": "user", "message": {"role": "user", "content": last_user_text}},
        {"type": "assistant", "message": {"role": "assistant", "content": "ok"}},
    ]
    if trailing_tool_result:
        events.append(
            {
                "type": "user",
                "message": {
                    "role": "user",
                    "content": [{"type": "tool_result", "content": "tool output"}],
                },
            }
        )
    transcript = root / "transcript.jsonl"
    transcript.write_text(
        "\n".join(json.dumps(e) for e in events) + "\n", encoding="utf-8"
    )
    return transcript


# --- Role-aware actionability (GOV-HARNESS-ROLE-PORTABILITY-001) ------------


def test_codex_as_lo_drains_new_revised(tmp_path: Path) -> None:
    """Codex holding the loyal-opposition role drains NEW/REVISED threads."""
    hook = _load_hook()
    root = _make_project(tmp_path, claude_role="prime-builder", codex_role="loyal-opposition")
    _write_index(root, [("alpha", "NEW", 1), ("beta", "REVISED", 2)])
    out = hook.drain_decision(root, "codex", "s1")
    assert out.get("decision") == "block"
    assert "NEW: alpha" in out["reason"]
    assert "REVISED: beta" in out["reason"]
    assert _drain_state(root, "s1")["last_result"] == "blocked_drain"


def test_codex_as_lo_ignores_go_no_go(tmp_path: Path) -> None:
    """Codex-as-LO drains ONLY NEW/REVISED: GO/NO-GO are Prime-actionable, so a
    LO session with only GO/NO-GO pending does not block its stop."""
    hook = _load_hook()
    root = _make_project(tmp_path, claude_role="prime-builder", codex_role="loyal-opposition")
    _write_index(root, [("alpha", "GO", 2), ("beta", "NO-GO", 2)])
    assert hook.drain_decision(root, "codex", "s1") == {}


def test_codex_as_prime_drains_go_no_go(tmp_path: Path) -> None:
    """Codex holding the prime-builder role drains GO/NO-GO threads -- proving
    actionability follows the role, not the vendor."""
    hook = _load_hook()
    root = _make_project(tmp_path, claude_role="loyal-opposition", codex_role="prime-builder")
    _write_index(root, [("alpha", "GO", 2), ("beta", "NO-GO", 2)])
    out = hook.drain_decision(root, "codex", "s1")
    assert out.get("decision") == "block"
    assert "GO: alpha" in out["reason"]
    assert "NO-GO: beta" in out["reason"]


def test_codex_as_prime_ignores_new_revised(tmp_path: Path) -> None:
    """Codex-as-Prime drains ONLY GO/NO-GO: NEW/REVISED are LO-actionable."""
    hook = _load_hook()
    root = _make_project(tmp_path, claude_role="loyal-opposition", codex_role="prime-builder")
    _write_index(root, [("alpha", "NEW", 1), ("beta", "REVISED", 2)])
    assert hook.drain_decision(root, "codex", "s1") == {}


def test_claude_as_prime_drains_go_no_go(tmp_path: Path) -> None:
    """Claude holding the prime-builder role drains GO/NO-GO threads."""
    hook = _load_hook()
    root = _make_project(tmp_path, claude_role="prime-builder", codex_role="loyal-opposition")
    _write_index(root, [("alpha", "GO", 2)])
    out = hook.drain_decision(root, "claude", "s1")
    assert out.get("decision") == "block"
    assert "GO: alpha" in out["reason"]


# --- Signature-change gate -------------------------------------------------


def test_unchanged_signature_does_not_reblock(tmp_path: Path) -> None:
    """A second Stop with the SAME role-actionable signature does not re-block;
    the signature gate releases the session so it can actually idle."""
    hook = _load_hook()
    root = _make_project(tmp_path, claude_role="prime-builder", codex_role="loyal-opposition")
    _write_index(root, [("alpha", "GO", 2)])
    first = hook.drain_decision(root, "claude", "s1")
    assert first.get("decision") == "block"
    second = hook.drain_decision(root, "claude", "s1")
    assert second == {}
    assert _drain_state(root, "s1")["last_result"] == "unchanged_no_reblock"


def test_unchanged_signature_does_not_reblock_lo(tmp_path: Path) -> None:
    """The signature gate releases a loyal-opposition session too: a second
    Stop with the same NEW/REVISED signature does not re-block."""
    hook = _load_hook()
    root = _make_project(tmp_path, claude_role="prime-builder", codex_role="loyal-opposition")
    _write_index(root, [("alpha", "NEW", 1)])
    assert hook.drain_decision(root, "codex", "s1").get("decision") == "block"
    assert hook.drain_decision(root, "codex", "s1") == {}
    assert _drain_state(root, "s1")["last_result"] == "unchanged_no_reblock"


# --- Circuit breaker -------------------------------------------------------


def test_circuit_breaker_bounds_consecutive_blocks(tmp_path: Path) -> None:
    """Consecutive drain-blocks are capped at CIRCUIT_BREAKER_CAP. Each call
    presents a fresh signature (one more actionable doc) so the signature gate
    never short-circuits -- only the circuit breaker can stop the escalation."""
    hook = _load_hook()
    cap = hook.CIRCUIT_BREAKER_CAP
    root = _make_project(tmp_path, claude_role="prime-builder", codex_role="loyal-opposition")
    docs: list[tuple[str, str, int]] = []
    for i in range(cap):
        docs.append((f"doc{i}", "GO", 2))
        _write_index(root, docs)
        out = hook.drain_decision(root, "claude", "s1")
        assert out.get("decision") == "block", f"call {i + 1} of {cap} should block"
    # The (cap+1)-th call: consecutive_blocks has reached the cap; the breaker
    # trips and releases the session even though new actionable work exists.
    docs.append((f"doc{cap}", "GO", 2))
    _write_index(root, docs)
    out = hook.drain_decision(root, "claude", "s1")
    assert out == {}
    assert _drain_state(root, "s1")["last_result"] == "circuit_breaker_tripped"


# --- Owner-decision deference ----------------------------------------------


def test_owner_decision_deference_suppresses_drain(tmp_path: Path) -> None:
    """A recent unresolved owner decision suppresses the drain so the session
    does not pile drain context onto the owner-decision path."""
    hook = _load_hook()
    root = _make_project(tmp_path, claude_role="prime-builder", codex_role="loyal-opposition")
    _write_index(root, [("alpha", "GO", 2)])  # actionable Prime work exists
    _write_pending_decision(root, status="pending", asked_at=datetime.now(UTC))
    out = hook.drain_decision(root, "claude", "s1")
    assert out == {}
    assert _drain_state(root, "s1")["last_result"] == "deferred_owner_decision"


def test_resolved_owner_decision_does_not_suppress_drain(tmp_path: Path) -> None:
    """A resolved owner decision is not deferred-to: the drain proceeds."""
    hook = _load_hook()
    root = _make_project(tmp_path, claude_role="prime-builder", codex_role="loyal-opposition")
    _write_index(root, [("alpha", "GO", 2)])
    _write_pending_decision(root, status="resolved", asked_at=datetime.now(UTC))
    assert hook.drain_decision(root, "claude", "s1").get("decision") == "block"


def test_stale_owner_decision_still_suppresses_drain(tmp_path: Path) -> None:
    """WI-3363 IP-1: an unresolved owner decision suppresses the drain
    regardless of age. The removed 30-minute recency window previously let the
    drain fire over an older-but-still-pending decision; it no longer does."""
    hook = _load_hook()
    root = _make_project(tmp_path, claude_role="prime-builder", codex_role="loyal-opposition")
    _write_index(root, [("alpha", "GO", 2)])
    stale = datetime.now(UTC) - timedelta(hours=6)
    _write_pending_decision(root, status="pending", asked_at=stale)
    out = hook.drain_decision(root, "claude", "s1")
    assert out == {}
    assert _drain_state(root, "s1")["last_result"] == "deferred_owner_decision"


# --- Wrap-up-command deference (WI-3363 IP-2; GOV-SESSION-LIFECYCLE-* ) -----


def test_wrapup_command_defers_drain(tmp_path: Path) -> None:
    """A turn ending on a wrap-up command defers the drain: the hook returns
    the empty allow-stop result so an owner-invoked wrap-up is not blocked
    (GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001 / PB-SESSION-WRAP-UP-
    PROACTIVE-001 / DCL-SESSION-WRAP-UP-AUTOMATION-SAFETY-001)."""
    hook = _load_hook()
    root = _make_project(tmp_path, claude_role="prime-builder", codex_role="loyal-opposition")
    _write_index(root, [("alpha", "GO", 2)])  # actionable Prime work exists
    transcript = _write_transcript(root, last_user_text="wrap up")
    out = hook.drain_decision(root, "claude", "s1", str(transcript))
    assert out == {}
    assert _drain_state(root, "s1")["last_result"] == "deferred_wrap_up_command"


def test_non_wrapup_message_does_not_defer_drain(tmp_path: Path) -> None:
    """A turn ending on an ordinary (non-wrap-up) owner message does not defer:
    the drain proceeds and blocks on the pending actionable work."""
    hook = _load_hook()
    root = _make_project(tmp_path, claude_role="prime-builder", codex_role="loyal-opposition")
    _write_index(root, [("alpha", "GO", 2)])
    transcript = _write_transcript(root, last_user_text="implement the next thread")
    out = hook.drain_decision(root, "claude", "s1", str(transcript))
    assert out.get("decision") == "block"


def test_wrapup_command_normalization_tolerance(tmp_path: Path) -> None:
    """The wrap-up match tolerates the documented normalization: case, trailing
    punctuation, and an optional leading or trailing "please"."""
    hook = _load_hook()
    variants = ("Wrap Up.", "please wrap up", "session wrap-up please", "  end this session!  ")
    for i, variant in enumerate(variants):
        root = _make_project(
            tmp_path / f"v{i}", claude_role="prime-builder", codex_role="loyal-opposition"
        )
        _write_index(root, [("alpha", "GO", 2)])
        transcript = _write_transcript(root, last_user_text=variant)
        out = hook.drain_decision(root, "claude", "s1", str(transcript))
        assert out == {}, f"variant {variant!r} should defer the drain"


def test_wrapup_check_skips_tool_result_continuation(tmp_path: Path) -> None:
    """The wrap-up check identifies the last *real* owner message: a trailing
    tool_result continuation (also type=='user') is skipped, so a wrap-up
    command followed by tool-result events still defers."""
    hook = _load_hook()
    root = _make_project(tmp_path, claude_role="prime-builder", codex_role="loyal-opposition")
    _write_index(root, [("alpha", "GO", 2)])
    transcript = _write_transcript(
        root, last_user_text="wrap up this session", trailing_tool_result=True
    )
    assert hook.drain_decision(root, "claude", "s1", str(transcript)) == {}


def test_wrapup_check_inert_when_transcript_absent(tmp_path: Path) -> None:
    """The wrap-up check fails open: with no transcript path -- or an
    explicitly-missing one -- the drain proceeds through its other gates
    exactly as before (it blocks on the pending actionable work)."""
    hook = _load_hook()
    root = _make_project(tmp_path, claude_role="prime-builder", codex_role="loyal-opposition")
    _write_index(root, [("alpha", "GO", 2)])
    assert hook.drain_decision(root, "claude", "s1").get("decision") == "block"
    missing = str(root / "no-such-transcript.jsonl")
    assert hook.drain_decision(root, "claude", "s2", missing).get("decision") == "block"


def test_wrapup_command_set_matches_canonical() -> None:
    """Drift guard: the hook's local WRAPUP_TRIGGER_COMMANDS copy is byte-equal
    to the canonical tuple in scripts/session_self_initialization.py, so the
    copy cannot silently diverge from the owner-facing wrap-up command set."""
    import session_self_initialization

    hook = _load_hook()
    assert hook.WRAPUP_TRIGGER_COMMANDS == session_self_initialization.WRAPUP_TRIGGER_COMMANDS


# --- Heartbeat re-arm (Risk R3: stale-lock dispatch race) ------------------


def test_drain_rearms_active_session_heartbeat_before_blocking(tmp_path: Path) -> None:
    """On the drain path the hook re-arms the active-session heartbeat so the
    session-stop heartbeat (which runs earlier in the Stop array) cannot leave
    a stale-lock window for a cross-harness dispatch race against the draining
    session (proposal Risk R3)."""
    hook = _load_hook()
    root = _make_project(tmp_path, claude_role="prime-builder", codex_role="loyal-opposition")
    marker = _install_heartbeat_stub(root)
    _write_index(root, [("alpha", "GO", 2)])
    out = hook.drain_decision(root, "claude", "s1")
    assert out.get("decision") == "block"
    assert marker.is_file(), "drain must re-arm the active-session heartbeat"
    assert "--mode tool-use" in marker.read_text(encoding="utf-8")


# --- Shared detection surface (no-drift) -----------------------------------


def test_both_surfaces_use_shared_compute_actionable_pending() -> None:
    """No new detection helper was extracted: bridge-stop-drain.py and the
    AXIS-2 UserPromptSubmit Prime surface both call
    groundtruth_kb.bridge.notify.compute_actionable_pending, so the two
    surfaces cannot drift apart."""
    axis2 = (_REPO_ROOT / ".claude" / "hooks" / "bridge-axis-2-surface.py").read_text(
        encoding="utf-8"
    )
    drain = _HOOK_PATH.read_text(encoding="utf-8")
    assert "compute_actionable_pending" in axis2
    assert "compute_actionable_pending" in drain


# --- CLI surface (Stop-hook end-to-end) ------------------------------------


def test_main_cli_surface_emits_block_and_exits_zero(tmp_path: Path) -> None:
    """End-to-end Stop-hook surface: main() parses --harness, reads the Stop
    event JSON from stdin, emits the drain decision to stdout, and exits 0."""
    root = _make_project(tmp_path, claude_role="prime-builder", codex_role="loyal-opposition")
    _write_index(root, [("alpha", "GO", 2)])
    env = dict(os.environ)
    env["CLAUDE_PROJECT_DIR"] = str(root)
    env.pop("GTKB_NO_BRIDGE_STOP_DRAIN", None)
    # main() bootstraps PROJECT_ROOT/scripts + PROJECT_ROOT/groundtruth-kb/src;
    # the fixture root has neither, so PYTHONPATH carries the real checkout's
    # code while CLAUDE_PROJECT_DIR points the *data* reads at the fixture.
    env["PYTHONPATH"] = os.pathsep.join(
        [str(_REPO_ROOT / "scripts"), str(_REPO_ROOT / "groundtruth-kb" / "src")]
    )
    proc = subprocess.run(
        [sys.executable, str(_HOOK_PATH), "--harness", "claude"],
        input=json.dumps({"session_id": "cli-smoke"}),
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
    )
    assert proc.returncode == 0, proc.stderr
    out = json.loads(proc.stdout)
    assert out.get("decision") == "block"
    assert "GO: alpha" in out["reason"]


# --- Registration (Stop-array placement) -----------------------------------


def test_bridge_stop_drain_registered_last_in_both_stop_arrays() -> None:
    """bridge-stop-drain.py must be the LAST Stop hook in both .claude/settings.json
    and .codex/hooks.json so it observes every prior Stop hook's INDEX
    side-effects before deciding whether to drain."""
    claude_cfg = json.loads(
        (_REPO_ROOT / ".claude" / "settings.json").read_text(encoding="utf-8")
    )
    claude_stop = claude_cfg["hooks"]["Stop"][0]["hooks"]
    assert "bridge-stop-drain.py" in claude_stop[-1]["command"]
    assert "--harness claude" in claude_stop[-1]["command"]

    codex_cfg = json.loads(
        (_REPO_ROOT / ".codex" / "hooks.json").read_text(encoding="utf-8")
    )
    codex_stop = codex_cfg["hooks"]["Stop"][0]["hooks"]
    assert "bridge-stop-drain.py" in codex_stop[-1]["command"]
    assert "--harness codex" in codex_stop[-1]["command"]
